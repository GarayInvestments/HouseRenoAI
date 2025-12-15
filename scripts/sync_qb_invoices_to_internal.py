"""
Sync QuickBooks Cache Invoices to Internal Database

Creates/updates internal invoices from QB cache, linking to clients and permits.
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime
from decimal import Decimal
import re
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import AsyncSessionLocal
from app.db.models import Client, Permit
from datetime import datetime
from decimal import Decimal
import re

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import AsyncSessionLocal
from app.db.models import Client, Permit
import json


def extract_permit_number(description: str) -> str:
    """
    Extract permit number from QB line item description.
    
    Patterns to match:
    - RES-ADD-25-000990
    - BP-25-35
    - PRRN202502429
    """
    if not description:
        return None
    
    patterns = [
        r'permit number ([A-Z]{2,4}-[A-Z]{3,4}-\d{2}-\d{6})',  # RES-ADD-25-000990
        r'permit\s+#?\s*([A-Z]{2,4}-[A-Z]{2,4}-\d{2}-\d{1,6})',  # BP-25-35
        r'permit\s+#?\s*(PRRN\d+)',  # PRRN202502429
        r'permit\s+#?\s*([A-Z]{2,4}-\d{2}-\d{4,6})',  # BC-25-0409
    ]
    
    for pattern in patterns:
        match = re.search(pattern, description, re.IGNORECASE)
        if match:
            return match.group(1)
    
    return None


def transform_qb_line_items(qb_lines: list) -> list:
    """Transform QB line items to internal format."""
    items = []
    
    for line in qb_lines:
        if line.get('DetailType') == 'SalesItemLineDetail':
            detail = line.get('SalesItemLineDetail') or {}
            item_ref = detail.get('ItemRef') or {}
            items.append({
                'description': line.get('Description', ''),
                'quantity': detail.get('Qty', 1),
                'unit_price': float(detail.get('UnitPrice', 0)),
                'amount': float(line.get('Amount', 0)),
                'item_name': item_ref.get('name', '')
            })
    
    return items


def map_qb_status(qb_status: str) -> str:
    """Map QB status to internal status enum (UPPERCASE)."""
    status_map = {
        'EmailSent': 'SENT',
        'Sent': 'SENT',
        'NeedToPrint': 'DRAFT',
        'Paid': 'PAID',
        'Pending': 'DRAFT',
    }
    return status_map.get(qb_status, 'DRAFT')


async def get_qb_cache_invoices(session: AsyncSession):
    """Fetch all QB cache invoices."""
    result = await session.execute(
        text("""
            SELECT 
                qb_invoice_id, customer_id, doc_number, total_amount, balance,
                due_date, qb_data, qb_last_modified
            FROM quickbooks_invoices_cache
            WHERE is_active = true
            ORDER BY due_date DESC
        """)
    )
    return result.fetchall()


async def find_client_by_qb_customer_id(session: AsyncSession, qb_customer_id: str):
    """Find internal client by QB customer ID."""
    result = await session.execute(
        select(Client).where(Client.qb_customer_id == qb_customer_id)
    )
    return result.scalar_one_or_none()


async def find_permit_by_number(session: AsyncSession, permit_number: str):
    """Find permit by permit number (case-insensitive)."""
    result = await session.execute(
        select(Permit).where(Permit.permit_number.ilike(f"%{permit_number}%"))
    )
    return result.scalar_one_or_none()


async def upsert_invoice(session: AsyncSession, invoice_data: dict):
    """Insert or update internal invoice using ORM."""
    from uuid import UUID
    from datetime import datetime
    from app.db.models import Invoice
    
    # Convert string UUIDs to UUID objects
    client_id = UUID(invoice_data['client_id']) if invoice_data['client_id'] else None
    project_id = UUID(invoice_data['project_id']) if invoice_data['project_id'] else None
    
    # Check if invoice exists
    result = await session.execute(
        select(Invoice).where(Invoice.qb_invoice_id == invoice_data['qb_invoice_id'])
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        # Update existing invoice
        existing.invoice_number = invoice_data['invoice_number']
        existing.client_id = client_id
        existing.project_id = project_id
        existing.invoice_date = invoice_data['invoice_date']
        existing.due_date = invoice_data['due_date']
        existing.subtotal = invoice_data['subtotal']
        existing.total_amount = invoice_data['total_amount']
        existing.balance_due = invoice_data['balance_due']
        existing.status = invoice_data['status']
        existing.line_items = invoice_data['line_items']
        existing.sync_status = invoice_data['sync_status']
        return 'updated'
    else:
        # Create new invoice
        new_invoice = Invoice(
            qb_invoice_id=invoice_data['qb_invoice_id'],
            invoice_number=invoice_data['invoice_number'],
            client_id=client_id,
            project_id=project_id,
            invoice_date=invoice_data['invoice_date'],
            due_date=invoice_data['due_date'],
            subtotal=invoice_data['subtotal'],
            total_amount=invoice_data['total_amount'],
            balance_due=invoice_data['balance_due'],
            status=invoice_data['status'],
            line_items=invoice_data['line_items'],
            sync_status=invoice_data['sync_status']
        )
        session.add(new_invoice)
        return 'created'


async def sync_qb_invoices():
    """Main function to sync QB invoices to internal database."""
    async with AsyncSessionLocal() as session:
        print("[*] Fetching QB cache invoices...")
        qb_invoices = await get_qb_cache_invoices(session)
        
        if limit:
            qb_invoices = qb_invoices[:limit]
            print(f"   Found {len(qb_invoices)} QB invoices (limited to {limit} for testing)")
        else:
            print(f"   Found {len(qb_invoices)} QB invoices")
        
        print("="*80)
        print("SYNCING INVOICES")
        print("="*80 + "\n")
        
        stats = {
            'created': 0,
            'updated': 0,
            'skipped_no_client': 0,
            'linked_to_permit': 0,
            'no_permit_link': 0
        }
        
        for qb_inv in qb_invoices:
            print(f"[Invoice] {qb_inv.doc_number} (QB ID: {qb_inv.qb_invoice_id})")
            
            # Parse QB data
            qb_data = qb_inv.qb_data or {}
            
            # Find linked client
            client = await find_client_by_qb_customer_id(session, qb_inv.customer_id)
            
            if not client:
                customer_name = qb_data.get('CustomerRef', {}).get('name', 'Unknown')
                print(f"   [WARNING] Skipped - No client linked to QB customer {customer_name} (ID: {qb_inv.customer_id})")
                stats['skipped_no_client'] += 1
                print()
                continue
            
            print(f"   [OK] Client: {client.full_name}")
            
            # Extract permit number from line items
            permit_number = None
            project_id = None
            
            for line in qb_data.get('Line', []):
                if line.get('DetailType') == 'SalesItemLineDetail':
                    description = line.get('Description', '')
                    permit_number = extract_permit_number(description)
                    if permit_number:
                        break
            
            if permit_number:
                permit = await find_permit_by_number(session, permit_number)
                if permit:
                    project_id = str(permit.project_id)
                    print(f"   [OK] Linked to permit: {permit.permit_number}")
                    stats['linked_to_permit'] += 1
                else:
                    print(f"   [WARNING] Permit not found: {permit_number}")
                    stats['no_permit_link'] += 1
            else:
                print(f"   [WARNING] No permit number found in description")
                stats['no_permit_link'] += 1
            
            # Transform line items
            line_items = transform_qb_line_items(qb_data.get('Line', []))
            
            # Map status
            status = map_qb_status(qb_data.get('EmailStatus', 'draft'))
            
            # Prepare invoice data
            from datetime import datetime
            
            # Parse dates from QB data
            invoice_date_str = qb_data.get('TxnDate')
            invoice_date = datetime.fromisoformat(invoice_date_str) if invoice_date_str else None
            
            invoice_data = {
                'qb_invoice_id': qb_inv.qb_invoice_id,
                'invoice_number': qb_inv.doc_number,
                'client_id': str(client.client_id),
                'project_id': project_id,
                'invoice_date': invoice_date,
                'due_date': qb_inv.due_date if qb_inv.due_date else None,
                'subtotal': float(qb_inv.total_amount) if qb_inv.total_amount else 0.0,
                'total_amount': float(qb_inv.total_amount) if qb_inv.total_amount else 0.0,
                'balance_due': float(qb_inv.balance) if qb_inv.balance else 0.0,
                'status': status,
                'line_items': json.dumps(line_items),
                'sync_status': 'synced'
            }
            
            # Upsert invoice
            action = await upsert_invoice(session, invoice_data)
            stats[action] += 1
            
            print(f"   [OK] {action.capitalize()}")
            print()
        
        # Commit or rollback based on dry_run flag
        if dry_run:
            await session.rollback()
            print("\n" + "="*80)
            print("DRY RUN COMPLETE (NO CHANGES MADE)")
            print("="*80)
            print(f"[*] Would create: {stats['created']}")
            print(f"[*] Would update: {stats['updated']}")
            print(f"[*] Would skip: {stats['skipped']}")
            print("\nRun with --commit flag to apply changes.")
        else:
            await session.commit()
            print("\n" + "="*80)
            print("SYNC COMPLETE")
            print("="*80)
            print(f"[OK] Created: {stats['created']}")
            print(f"[*] Updated: {stats['updated']}")
        print(f"🔗 Linked to permits: {stats['linked_to_permit']}")
        print(f"[WARNING] No permit link: {stats['no_permit_link']}")
        print(f"[ERROR] Skipped (no client): {stats['skipped_no_client']}")
        
        print("\n📊 Next Steps:")
        print("   1. Check database: SELECT COUNT(*) FROM invoices;")
        print("   2. Restart frontend to see unified invoice list")
        print("   3. Test invoice navigation with client/permit links")


if __name__ == "__main__":
    print("="*80)
    print("QUICKBOOKS TO INTERNAL DATABASE SYNC")
    print("="*80)
    print()
    
    asyncio.run(sync_qb_invoices())
