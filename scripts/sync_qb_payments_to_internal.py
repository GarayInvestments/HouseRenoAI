"""
Sync QuickBooks payments from cache to internal database.

Follows best practices from DATA_MIGRATION_BEST_PRACTICES.md:
- Dry-run mode (default)
- Incremental testing (--limit parameter)
- ORM-based inserts (no SQL syntax issues)
- Explicit type conversions
- Defensive JSONB parsing
- ASCII-only output

Usage:
    python scripts/sync_qb_payments_to_internal.py --limit 1   # Test with 1 payment
    python scripts/sync_qb_payments_to_internal.py --limit 3   # Test with 3 payments
    python scripts/sync_qb_payments_to_internal.py             # Dry-run all
    python scripts/sync_qb_payments_to_internal.py --commit    # Apply changes
"""

import asyncio
import sys
from datetime import datetime
from decimal import Decimal
from uuid import UUID
from sqlalchemy import select, text
from sqlalchemy.orm import selectinload

# Validate imports
try:
    from app.db.session import AsyncSessionLocal
    from app.db.models import Payment, Client, Invoice
except ImportError as e:
    print(f"[ERROR] Import failed: {e}")
    print("Make sure PYTHONPATH is set: $env:PYTHONPATH = \"C:\\Users\\Steve Garay\\Desktop\\HouseRenovators-api\"")
    sys.exit(1)


async def validate_before_sync():
    """Pre-flight validation checks."""
    print("[*] Running pre-flight validation...\n")
    
    async with AsyncSessionLocal() as session:
        # 1. Check source data
        result = await session.execute(
            text("SELECT COUNT(*) FROM quickbooks_payments_cache WHERE is_active = true")
        )
        qb_count = result.scalar()
        print(f"[OK] QB payments in cache: {qb_count}")
        
        # 2. Check linked clients
        result = await session.execute(
            text("SELECT COUNT(*) FROM clients WHERE qb_customer_id IS NOT NULL")
        )
        linked_clients = result.scalar()
        print(f"[OK] Clients with QB IDs: {linked_clients}")
        
        # 3. Check linked invoices
        result = await session.execute(
            text("SELECT COUNT(*) FROM invoices WHERE qb_invoice_id IS NOT NULL")
        )
        linked_invoices = result.scalar()
        print(f"[OK] Invoices with QB IDs: {linked_invoices}")
        
        # 4. Check payment status enum
        result = await session.execute(
            text("SELECT unnest(enum_range(NULL::payment_status_enum))")
        )
        enum_values = [row[0] for row in result]
        print(f"[OK] Payment status enum values: {enum_values}")
        
        # 5. Sample QB payment structure
        result = await session.execute(
            text("SELECT qb_data FROM quickbooks_payments_cache WHERE is_active = true LIMIT 1")
        )
        sample = result.scalar()
        if sample:
            print(f"\n[OK] Sample QB payment structure:")
            print(f"  - TxnDate: {sample.get('TxnDate')} (type: {type(sample.get('TxnDate')).__name__})")
            print(f"  - TotalAmt: {sample.get('TotalAmt')} (type: {type(sample.get('TotalAmt')).__name__})")
            print(f"  - CustomerRef: {sample.get('CustomerRef', {}).get('value')}")
            line = sample.get('Line', [{}])[0] if sample.get('Line') else {}
            linked_txn = (line.get('LinkedTxn') or [{}])[0] if line.get('LinkedTxn') else {}
            print(f"  - LinkedTxn TxnId: {linked_txn.get('TxnId')}")
            print(f"  - PaymentMethodRef: {sample.get('PaymentMethodRef', {}).get('name')}")
    
    print("\n[OK] Validation complete\n")


def map_payment_method(qb_method: str) -> str:
    """Map QB payment method to internal format."""
    method_map = {
        'Cash': 'CASH',
        'Check': 'CHECK',
        'Credit Card': 'CREDIT_CARD',
        'ACH': 'ACH',
        'Wire': 'WIRE',
        'Venmo': 'VENMO',
        'Zelle': 'ZELLE',
    }
    return method_map.get(qb_method, 'OTHER')


def map_payment_status(qb_data: dict) -> str:
    """Determine payment status from QB data."""
    # QB payments are always posted when synced
    # Enum values: PENDING, POSTED, FAILED, REFUNDED
    # Check if there's a void or deleted status
    private_note = (qb_data.get('PrivateNote') or '').upper()
    if 'VOID' in private_note or 'DELETED' in private_note:
        return 'REFUNDED'  # Closest match for voided payments
    return 'POSTED'  # QB synced payments are posted


async def sync_qb_payments(dry_run: bool = True, limit: int = None):
    """
    Sync QB payments from cache to internal database.
    
    Args:
        dry_run: If True, show what would be done without committing (default: True)
        limit: Process only first N payments (for testing)
    
    Returns:
        dict: Stats about sync operation
    """
    stats = {'created': 0, 'updated': 0, 'skipped': 0, 'errors': 0}
    
    async with AsyncSessionLocal() as session:
        # Fetch QB payments from cache
        query = text("""
            SELECT qb_data 
            FROM quickbooks_payments_cache 
            WHERE is_active = true
            ORDER BY (qb_data->>'TxnDate')::date DESC
        """)
        
        result = await session.execute(query)
        qb_payments = [row[0] for row in result.fetchall()]
        
        # Apply limit for testing
        if limit:
            qb_payments = qb_payments[:limit]
            print(f"[*] Limited to first {limit} payments for testing\n")
        
        print(f"[*] Processing {len(qb_payments)} QB payments...\n")
        
        # Pre-load clients by QB customer ID for efficient lookup
        clients_result = await session.execute(
            select(Client).where(Client.qb_customer_id.isnot(None))
        )
        clients_by_qb_id = {
            client.qb_customer_id: client 
            for client in clients_result.scalars().all()
        }
        
        # Pre-load invoices by QB invoice ID for efficient lookup
        invoices_result = await session.execute(
            select(Invoice).where(Invoice.qb_invoice_id.isnot(None))
        )
        invoices_by_qb_id = {
            invoice.qb_invoice_id: invoice 
            for invoice in invoices_result.scalars().all()
        }
        
        print(f"[*] Loaded {len(clients_by_qb_id)} clients and {len(invoices_by_qb_id)} invoices for matching\n")
        
        for qb_payment in qb_payments:
            try:
                # Extract QB payment ID
                qb_payment_id = str(qb_payment.get('Id', ''))
                
                # Check if payment already exists
                existing_result = await session.execute(
                    select(Payment).where(Payment.qb_payment_id == qb_payment_id)
                )
                existing = existing_result.scalar_one_or_none()
                
                if existing:
                    print(f"[*] Payment {qb_payment_id} already exists, skipping")
                    stats['skipped'] += 1
                    continue
                
                # Find client via CustomerRef
                customer_ref = qb_payment.get('CustomerRef') or {}
                qb_customer_id = str(customer_ref.get('value', ''))
                client = clients_by_qb_id.get(qb_customer_id)
                
                if not client:
                    print(f"[WARNING] Payment {qb_payment_id}: No client found for QB customer ID {qb_customer_id}")
                    stats['skipped'] += 1
                    continue
                
                # Find linked invoice via Line->LinkedTxn
                line = (qb_payment.get('Line') or [{}])[0] if qb_payment.get('Line') else {}
                linked_txn = (line.get('LinkedTxn') or [{}])[0] if line.get('LinkedTxn') else {}
                qb_invoice_id = str(linked_txn.get('TxnId', ''))
                
                invoice = None
                project_id = None
                if qb_invoice_id:
                    invoice = invoices_by_qb_id.get(qb_invoice_id)
                    if invoice:
                        project_id = invoice.project_id
                
                # Parse payment data with explicit type conversions
                payment_date_str = qb_payment.get('TxnDate')
                payment_date = datetime.fromisoformat(payment_date_str) if payment_date_str else None
                
                total_amt = qb_payment.get('TotalAmt')
                amount = Decimal(str(total_amt)) if total_amt is not None else None
                
                payment_method_ref = qb_payment.get('PaymentMethodRef') or {}
                payment_method = map_payment_method(payment_method_ref.get('name', ''))
                
                status = map_payment_status(qb_payment)
                
                # Extract reference number (check number or transaction ID)
                ref_number = qb_payment.get('PaymentRefNum', '')
                check_number = ref_number if payment_method == 'CHECK' else None
                transaction_id = ref_number if payment_method != 'CHECK' else None
                
                # Extract notes
                notes = qb_payment.get('PrivateNote', '')
                
                # Create Payment object
                new_payment = Payment(
                    client_id=UUID(str(client.client_id)),
                    project_id=UUID(str(project_id)) if project_id else None,
                    invoice_id=UUID(str(invoice.invoice_id)) if invoice else None,
                    amount=amount,
                    payment_date=payment_date,
                    payment_method=payment_method,
                    status=status,
                    check_number=check_number,
                    transaction_id=transaction_id,
                    qb_payment_id=qb_payment_id,
                    reference_number=ref_number,
                    notes=notes,
                    extra=qb_payment,  # Store full QB data
                    sync_status='SYNCED',
                    last_sync_attempt=datetime.now()
                )
                
                session.add(new_payment)
                stats['created'] += 1
                
                # Display what we're creating
                print(f"[Payment] QB ID: {qb_payment_id}")
                print(f"  Client: {client.full_name}")
                print(f"  Amount: ${amount}")
                print(f"  Date: {payment_date.strftime('%Y-%m-%d') if payment_date else 'N/A'}")
                print(f"  Method: {payment_method}")
                print(f"  Invoice: {invoice.invoice_number if invoice else 'None'}")
                print(f"  Project: {project_id if project_id else 'Not linked'}")
                print(f"  [OK] Ready to create\n")
                
            except Exception as e:
                print(f"[ERROR] Processing payment {qb_payment.get('Id')}: {e}")
                stats['errors'] += 1
                continue
        
        # Summary
        print("\n" + "="*80)
        print("SYNC SUMMARY")
        print("="*80)
        print(f"Total processed: {len(qb_payments)}")
        print(f"Created: {stats['created']}")
        print(f"Updated: {stats['updated']}")
        print(f"Skipped: {stats['skipped']}")
        print(f"Errors: {stats['errors']}")
        print("="*80 + "\n")
        
        # Dry-run or commit
        if dry_run:
            print("[DRY RUN] No changes made. Run with --commit to apply changes.")
            await session.rollback()
        else:
            await session.commit()
            print(f"[OK] Committed {stats['created']} payments to database")
        
        return stats


async def main():
    """Main entry point with CLI argument parsing."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Sync QuickBooks payments from cache to internal database',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/sync_qb_payments_to_internal.py --limit 1   # Test with 1 payment
  python scripts/sync_qb_payments_to_internal.py --limit 3   # Test with 3 payments
  python scripts/sync_qb_payments_to_internal.py             # Dry-run all payments
  python scripts/sync_qb_payments_to_internal.py --commit    # Apply changes to database
        """
    )
    parser.add_argument(
        '--commit',
        action='store_true',
        help='Actually commit changes to database (default: dry-run)'
    )
    parser.add_argument(
        '--limit',
        type=int,
        help='Process only first N payments (for testing)'
    )
    
    args = parser.parse_args()
    
    # Run validation
    await validate_before_sync()
    
    # Run sync
    await sync_qb_payments(dry_run=not args.commit, limit=args.limit)


if __name__ == '__main__':
    asyncio.run(main())
