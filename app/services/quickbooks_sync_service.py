"""
QuickBooks Sync Service

Handles synchronization of QuickBooks data to local cache tables.
Implements delta sync using qb_last_modified timestamps to minimize API calls.
Includes circuit breaker pattern for API resilience.

IMPORTANT: QuickBooks Query vs GET behavior
-------------------------------------------
QBO has TWO read paths with different reliability:
1. Entity GET (Customer.get(id)) → Very reliable, always use when ID known
2. Query endpoint (QBO SQL) → Strict, limited, often returns 0 rows even when data exists

Query limitations:
- Invalid predicates fail SILENTLY (return empty results, not errors)
- Reference fields (CustomerTypeRef) are NOT filterable despite being present on objects
- One entity per query, no OR clauses, MAXRESULTS ≤ 1000
- GET-by-Id can succeed even when Query returns 0 rows

Strategy:
- When IDs are known: Use GET (authoritative)
- When discovering data: Use Query (best-effort only)
- Empty query results ≠ data does not exist (QB limitation, not our bug)
"""

import logging
import json
from datetime import datetime, timezone
from typing import List, Dict, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.services.quickbooks_service import get_quickbooks_service
from app.utils.circuit_breaker import qb_circuit_breaker, CircuitBreakerError

logger = logging.getLogger(__name__)


class QuickBooksSyncService:
    """
    Manages synchronization between QuickBooks and local cache tables.
    
    Features:
    - Delta sync: Only fetches records changed since last sync
    - Batch processing: Handles large datasets efficiently
    - Error tracking: Records sync failures per record
    - Metrics: Tracks sync duration and record counts
    - Filtering: Only syncs "GC Compliance" customers (CustomerTypeRef=698682)
    - Authoritative IDs: Uses QB IDs only, never name/amount matching
    """
    
    # QuickBooks CustomerType ID for "GC Compliance" customers
    GC_COMPLIANCE_CUSTOMER_TYPE = "698682"
    
    def __init__(self):
        self.qb_service = None  # Injected per-request with DB session
    
    async def sync_customers(self, db: AsyncSession, since: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Sync customers from QuickBooks to quickbooks_customers_cache.
        
        Args:
            db: Database session
            since: Only fetch customers modified after this timestamp (for delta sync)
            
        Returns:
            Dict with sync metrics (records_synced, duration_ms, errors)
        """        # Inject DB-aware QuickBooks service
        self.qb_service = get_quickbooks_service(db)
                # Inject DB-aware QuickBooks service
        self.qb_service = get_quickbooks_service(db)
        
        start_time = datetime.now(timezone.utc)
        records_synced = 0
        errors = 0
        
        try:
            logger.info(f"[SYNC] Starting customer sync (delta: {since is not None})")
            
            # Get last sync time from sync_status if not provided
            if since is None:
                result = await db.execute(
                    text("SELECT last_sync_at FROM sync_status WHERE entity_type = 'customers'")
                )
                row = result.fetchone()
                since = row.last_sync_at if row and row.last_sync_at else None
            
            # Build QuickBooks query
            # NOTE: CustomerTypeRef is NOT queryable - must fetch all and filter in Python
            query = "SELECT * FROM Customer"
            where_clauses = []
            
            if since:
                # Format datetime for QuickBooks API (ISO 8601)
                since_str = since.strftime('%Y-%m-%dT%H:%M:%S-00:00')
                where_clauses.append(f"Metadata.LastUpdatedTime > '{since_str}'")
                logger.info(f"[SYNC] Delta query: fetching customers modified after {since_str}")
            else:
                logger.info(f"[SYNC] Full sync: fetching all customers (will filter to GC Compliance in Python)")
            
            if where_clauses:
                query += " WHERE " + " AND ".join(where_clauses)
            query += " MAXRESULTS 1000"
            
            # Fetch customers from QuickBooks with circuit breaker protection
            try:
                all_customers = await qb_circuit_breaker.call(
                    self.qb_service.query,
                    query
                )
                logger.info(f"[SYNC] Query returned {len(all_customers)} total customers")
                
                # Filter to GC Compliance customers only (CustomerTypeRef not queryable in QB API)
                customers = [
                    c for c in all_customers 
                    if c.get('CustomerTypeRef', {}).get('value') == self.GC_COMPLIANCE_CUSTOMER_TYPE
                ]
                logger.info(f"[SYNC] Filtered to {len(customers)} GC Compliance customers (CustomerTypeRef={self.GC_COMPLIANCE_CUSTOMER_TYPE})")
            except CircuitBreakerError as e:
                # Circuit is open - fail fast without attempting API call
                logger.error(f"[SYNC] Circuit breaker blocked sync: {e}")
                duration_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
                await self._update_sync_status(db, 'customers', start_time, 0, duration_ms, 1)
                return {
                    "records_synced": 0, 
                    "duration_ms": duration_ms, 
                    "errors": 1,
                    "circuit_breaker_status": qb_circuit_breaker.get_status(),
                    "error": str(e)
                }
            
            if not customers:
                logger.info("[SYNC] No customers to sync")
                await self._update_sync_status(db, 'customers', start_time, 0, 0, 0)
                return {"records_synced": 0, "duration_ms": 0, "errors": 0, "created": 0, "updated": 0, "skipped": 0}
            
            logger.info(f"[SYNC] Fetched {len(customers)} customers from QuickBooks")
            
            # Process each customer
            for customer in customers:
                try:
                    qb_customer_id = customer.get('Id')
                    
                    # CRITICAL: Validate this is a GC Compliance customer
                    customer_type_ref = customer.get('CustomerTypeRef', {})
                    customer_type_id = customer_type_ref.get('value') if customer_type_ref else None
                    
                    if customer_type_id != self.GC_COMPLIANCE_CUSTOMER_TYPE:
                        logger.warning(f"[SYNC] Skipping customer {qb_customer_id}: not GC Compliance (type={customer_type_id})")
                        continue
                    
                    # QB ID is authoritative - never match by name
                    if not qb_customer_id:
                        logger.error(f"[SYNC] Skipping customer: missing QB ID")
                        errors += 1
                        continue
                    
                    # Extract customer data
                    # Parse QB timestamp string to datetime
                    qb_last_modified_str = customer.get('MetaData', {}).get('LastUpdatedTime')
                    qb_last_modified = datetime.fromisoformat(qb_last_modified_str.replace('Z', '+00:00')) if qb_last_modified_str else None
                    
                    customer_data = {
                        'qb_customer_id': qb_customer_id,
                        'display_name': customer.get('DisplayName'),
                        'company_name': customer.get('CompanyName'),
                        'given_name': customer.get('GivenName'),
                        'family_name': customer.get('FamilyName'),
                        'email': customer.get('PrimaryEmailAddr', {}).get('Address') if customer.get('PrimaryEmailAddr') else None,
                        'phone': customer.get('PrimaryPhone', {}).get('FreeFormNumber') if customer.get('PrimaryPhone') else None,
                        'qb_data': json.dumps(customer),  # JSON-encode for JSONB column
                        'qb_last_modified': qb_last_modified,
                        'is_active': customer.get('Active', True),
                        'sync_error': None,
                        'cached_at': datetime.now(timezone.utc)
                    }
                    
                    # Upsert into cache table
                    await db.execute(
                        text("""
                            INSERT INTO quickbooks_customers_cache 
                            (qb_customer_id, display_name, company_name, given_name, family_name, 
                             email, phone, qb_data, qb_last_modified, is_active, sync_error, cached_at)
                            VALUES 
                            (:qb_customer_id, :display_name, :company_name, :given_name, :family_name,
                             :email, :phone, :qb_data, :qb_last_modified, :is_active, :sync_error, :cached_at)
                            ON CONFLICT (qb_customer_id) DO UPDATE SET
                                display_name = EXCLUDED.display_name,
                                company_name = EXCLUDED.company_name,
                                given_name = EXCLUDED.given_name,
                                family_name = EXCLUDED.family_name,
                                email = EXCLUDED.email,
                                phone = EXCLUDED.phone,
                                qb_data = EXCLUDED.qb_data,
                                qb_last_modified = EXCLUDED.qb_last_modified,
                                is_active = EXCLUDED.is_active,
                                sync_error = NULL,
                                cached_at = EXCLUDED.cached_at
                        """),
                        customer_data
                    )
                    
                    records_synced += 1
                    
                except Exception as e:
                    logger.error(f"Failed to sync customer {qb_customer_id}: {e}")
                    errors += 1
                    
                    # Store error in cache
                    try:
                        await db.execute(
                            text("""
                                UPDATE quickbooks_customers_cache 
                                SET sync_error = :error 
                                WHERE qb_customer_id = :qb_customer_id
                            """),
                            {"error": str(e), "qb_customer_id": qb_customer_id}
                        )
                    except:
                        pass
            
            # Commit all changes
            await db.commit()
            
            # Calculate duration
            end_time = datetime.now(timezone.utc)
            duration_ms = int((end_time - start_time).total_seconds() * 1000)
            
            # Update sync status
            await self._update_sync_status(db, 'customers', start_time, duration_ms, records_synced, errors)
            
            logger.info(f"[SYNC] Customer sync complete: {records_synced} synced, {errors} errors, {duration_ms}ms")
            
            return {
                "records_synced": records_synced,
                "duration_ms": duration_ms,
                "errors": errors,
                "created": 0,  # TODO: Track created vs updated
                "updated": records_synced,
                "skipped": 0
            }
            
        except Exception as e:
            logger.error(f"Customer sync failed: {e}", exc_info=True)
            await db.rollback()
            
            # Update sync status with error
            duration_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
            await self._update_sync_status(db, 'customers', start_time, duration_ms, records_synced, errors + 1, str(e))
            
            raise
    
    async def sync_invoices(self, db: AsyncSession, since: Optional[datetime] = None, auto_promote: bool = True) -> Dict[str, Any]:
        """
        Sync invoices from QuickBooks to quickbooks_invoices_cache.
        
        Args:
            db: Database session
            since: Only fetch invoices modified after this timestamp
            auto_promote: If True, automatically promotes cached invoices to main invoices table
            
        Returns:
            Dict with sync metrics
        """
        # Inject DB-aware QuickBooks service
        self.qb_service = get_quickbooks_service(db)
        
        start_time = datetime.now(timezone.utc)
        records_synced = 0
        errors = 0
        
        try:
            logger.info(f"[SYNC] Starting invoice sync (delta: {since is not None})")
            
            # Get last sync time if not provided
            if since is None:
                result = await db.execute(
                    text("SELECT last_sync_at FROM sync_status WHERE entity_type = 'invoices'")
                )
                row = result.fetchone()
                since = row.last_sync_at if row and row.last_sync_at else None
            
            # Build query
            query = "SELECT * FROM Invoice"
            if since:
                since_str = since.strftime('%Y-%m-%dT%H:%M:%S-00:00')
                query += f" WHERE Metadata.LastUpdatedTime > '{since_str}'"
                logger.info(f"[SYNC] Delta query: fetching invoices modified after {since_str}")
            
            query += " MAXRESULTS 1000"
            
            # Fetch invoices with circuit breaker protection
            try:
                invoices = await qb_circuit_breaker.call(
                    self.qb_service.query,
                    query
                )
            except CircuitBreakerError as e:
                logger.error(f"[SYNC] Circuit breaker blocked invoice sync: {e}")
                duration_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
                await self._update_sync_status(db, 'invoices', start_time, 0, duration_ms, 1)
                return {
                    "records_synced": 0,
                    "duration_ms": duration_ms,
                    "errors": 1,
                    "circuit_breaker_status": qb_circuit_breaker.get_status(),
                    "error": str(e)
                }
            
            if not invoices:
                logger.info("[SYNC] No invoices to sync")
                await self._update_sync_status(db, 'invoices', start_time, 0, 0, 0)
                return {"records_synced": 0, "duration_ms": 0, "errors": 0, "created": 0, "updated": 0, "skipped": 0}
            
            logger.info(f"[SYNC] Fetched {len(invoices)} invoices from QuickBooks")
            
            # Get list of GC Compliance customer IDs from cache
            result = await db.execute(
                text("SELECT qb_customer_id FROM quickbooks_customers_cache WHERE is_active = true")
            )
            gc_customer_ids = {row.qb_customer_id for row in result.fetchall()}
            logger.info(f"[SYNC] Filtering invoices for {len(gc_customer_ids)} GC Compliance customers")
            
            # Process each invoice
            for invoice in invoices:
                try:
                    qb_invoice_id = invoice.get('Id')
                    customer_ref = invoice.get('CustomerRef', {})
                    customer_id = customer_ref.get('value') if customer_ref else None
                    
                    # CRITICAL: Only sync invoices for GC Compliance customers
                    if customer_id not in gc_customer_ids:
                        logger.debug(f"[SYNC] Skipping invoice {qb_invoice_id}: customer {customer_id} not in GC Compliance")
                        continue
                    
                    # QB ID is authoritative
                    if not qb_invoice_id:
                        logger.error(f"[SYNC] Skipping invoice: missing QB ID")
                        errors += 1
                        continue
                    
                    # Parse QB timestamp string to datetime
                    qb_last_modified_str = invoice.get('MetaData', {}).get('LastUpdatedTime')
                    qb_last_modified = datetime.fromisoformat(qb_last_modified_str.replace('Z', '+00:00')) if qb_last_modified_str else None
                    
                    # Parse date string to date object
                    due_date_str = invoice.get('DueDate')
                    due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date() if due_date_str else None
                    
                    invoice_data = {
                        'qb_invoice_id': qb_invoice_id,
                        'customer_id': invoice.get('CustomerRef', {}).get('value'),
                        'doc_number': invoice.get('DocNumber'),
                        'total_amount': invoice.get('TotalAmt'),
                        'balance': invoice.get('Balance'),
                        'due_date': due_date,
                        'qb_data': json.dumps(invoice),  # JSON-encode for JSONB column
                        'qb_last_modified': qb_last_modified,
                        'is_active': True,  # Invoices don't have Active field
                        'sync_error': None,
                        'cached_at': datetime.now(timezone.utc)
                    }
                    
                    # Upsert
                    await db.execute(
                        text("""
                            INSERT INTO quickbooks_invoices_cache 
                            (qb_invoice_id, customer_id, doc_number, total_amount, balance, 
                             due_date, qb_data, qb_last_modified, is_active, sync_error, cached_at)
                            VALUES 
                            (:qb_invoice_id, :customer_id, :doc_number, :total_amount, :balance,
                             :due_date, :qb_data, :qb_last_modified, :is_active, :sync_error, :cached_at)
                            ON CONFLICT (qb_invoice_id) DO UPDATE SET
                                customer_id = EXCLUDED.customer_id,
                                doc_number = EXCLUDED.doc_number,
                                total_amount = EXCLUDED.total_amount,
                                balance = EXCLUDED.balance,
                                due_date = EXCLUDED.due_date,
                                qb_data = EXCLUDED.qb_data,
                                qb_last_modified = EXCLUDED.qb_last_modified,
                                is_active = EXCLUDED.is_active,
                                sync_error = NULL,
                                cached_at = EXCLUDED.cached_at
                        """),
                        invoice_data
                    )
                    
                    records_synced += 1
                    
                except Exception as e:
                    logger.error(f"Failed to sync invoice {qb_invoice_id}: {e}")
                    errors += 1
                    
                    try:
                        await db.execute(
                            text("""
                                UPDATE quickbooks_invoices_cache 
                                SET sync_error = :error 
                                WHERE qb_invoice_id = :qb_invoice_id
                            """),
                            {"error": str(e), "qb_invoice_id": qb_invoice_id}
                        )
                    except:
                        pass
            
            await db.commit()
            
            end_time = datetime.now(timezone.utc)
            duration_ms = int((end_time - start_time).total_seconds() * 1000)
            
            await self._update_sync_status(db, 'invoices', start_time, duration_ms, records_synced, errors)
            
            logger.info(f"[SYNC] Invoice sync complete: {records_synced} synced, {errors} errors, {duration_ms}ms")
            
            # Auto-promote to main table if enabled
            promotion_result = None
            if auto_promote and records_synced > 0:
                logger.info(f"[SYNC] Auto-promoting {records_synced} invoices to main table")
                try:
                    promotion_result = await self.promote_invoices_to_database(db)
                except Exception as e:
                    logger.error(f"[SYNC] Auto-promotion failed (sync succeeded): {e}")
                    # Don't fail the sync if promotion fails
            
            return {
                "records_synced": records_synced,
                "duration_ms": duration_ms,
                "errors": errors,
                "created": 0,  # TODO: Track created vs updated
                "updated": records_synced,
                "skipped": 0,
                "promotion": promotion_result
            }
            
        except Exception as e:
            logger.error(f"Invoice sync failed: {e}", exc_info=True)
            await db.rollback()
            
            duration_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
            await self._update_sync_status(db, 'invoices', start_time, duration_ms, records_synced, errors + 1, str(e))
            
            raise
    
    async def sync_payments(self, db: AsyncSession, since: Optional[datetime] = None, auto_promote: bool = True) -> Dict[str, Any]:
        """
        Sync payments from QuickBooks to quickbooks_payments_cache.
        
        Args:
            db: Database session
            since: Only fetch payments modified after this timestamp
            auto_promote: If True, automatically promotes cached payments to main payments table
            
        Returns:
            Dict with sync metrics
        """
        # Inject DB-aware QuickBooks service
        self.qb_service = get_quickbooks_service(db)
        
        start_time = datetime.now(timezone.utc)
        records_synced = 0
        errors = 0
        
        try:
            logger.info(f"[SYNC] Starting payment sync (delta: {since is not None})")
            
            # Get last sync time if not provided
            if since is None:
                result = await db.execute(
                    text("SELECT last_sync_at FROM sync_status WHERE entity_type = 'payments'")
                )
                row = result.fetchone()
                since = row.last_sync_at if row and row.last_sync_at else None
            
            # Build query
            query = "SELECT * FROM Payment"
            if since:
                since_str = since.strftime('%Y-%m-%dT%H:%M:%S-00:00')
                query += f" WHERE Metadata.LastUpdatedTime > '{since_str}'"
                logger.info(f"[SYNC] Delta query: fetching payments modified after {since_str}")
            
            query += " MAXRESULTS 1000"
            
            # Fetch payments with circuit breaker protection
            try:
                payments = await qb_circuit_breaker.call(
                    self.qb_service.query,
                    query
                )
            except CircuitBreakerError as e:
                logger.error(f"[SYNC] Circuit breaker blocked payment sync: {e}")
                duration_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
                await self._update_sync_status(db, 'payments', start_time, 0, duration_ms, 1)
                return {
                    "records_synced": 0,
                    "duration_ms": duration_ms,
                    "errors": 1,
                    "circuit_breaker_status": qb_circuit_breaker.get_status(),
                    "error": str(e)
                }
            
            if not payments:
                logger.info("[SYNC] No payments to sync")
                await self._update_sync_status(db, 'payments', start_time, 0, 0, 0)
                return {"records_synced": 0, "duration_ms": 0, "errors": 0, "created": 0, "updated": 0, "skipped": 0}
            
            logger.info(f"[SYNC] Fetched {len(payments)} payments from QuickBooks")
            
            # Get list of GC Compliance invoice IDs from cache
            result = await db.execute(
                text("SELECT qb_invoice_id FROM quickbooks_invoices_cache")
            )
            gc_invoice_ids = {row.qb_invoice_id for row in result.fetchall()}
            logger.info(f"[SYNC] Filtering payments for {len(gc_invoice_ids)} GC Compliance invoices")
            
            # Process each payment
            for payment in payments:
                try:
                    qb_payment_id = payment.get('Id')
                    customer_ref = payment.get('CustomerRef', {})
                    customer_id = customer_ref.get('value') if customer_ref else None
                    
                    # Extract linked invoice IDs from payment lines
                    linked_invoice_ids = []
                    for line in payment.get('Line', []):
                        linked_txns = line.get('LinkedTxn', [])
                        for linked_txn in linked_txns:
                            if linked_txn.get('TxnType') == 'Invoice':
                                linked_invoice_ids.append(linked_txn.get('TxnId'))
                    
                    # CRITICAL: Only sync payments for GC Compliance invoices
                    has_gc_invoice = any(inv_id in gc_invoice_ids for inv_id in linked_invoice_ids)
                    if not has_gc_invoice:
                        logger.debug(f"[SYNC] Skipping payment {qb_payment_id}: no GC Compliance invoices linked")
                        continue
                    
                    # QB ID is authoritative
                    if not qb_payment_id:
                        logger.error(f"[SYNC] Skipping payment: missing QB ID")
                        errors += 1
                        continue
                    
                    # Extract linked invoice if present
                    invoice_id = None
                    if payment.get('Line'):
                        for line in payment['Line']:
                            if line.get('LinkedTxn'):
                                for linked_txn in line['LinkedTxn']:
                                    if linked_txn.get('TxnType') == 'Invoice':
                                        invoice_id = linked_txn.get('TxnId')
                                        break
                    
                    # Parse QB timestamp string to datetime
                    qb_last_modified_str = payment.get('MetaData', {}).get('LastUpdatedTime')
                    qb_last_modified = datetime.fromisoformat(qb_last_modified_str.replace('Z', '+00:00')) if qb_last_modified_str else None
                    
                    # Parse date string to date object
                    payment_date_str = payment.get('TxnDate')
                    payment_date = datetime.strptime(payment_date_str, '%Y-%m-%d').date() if payment_date_str else None
                    
                    payment_data = {
                        'qb_payment_id': qb_payment_id,
                        'customer_id': payment.get('CustomerRef', {}).get('value'),
                        'invoice_id': invoice_id,
                        'amount': payment.get('TotalAmt'),
                        'payment_date': payment_date,
                        'payment_method': payment.get('PaymentMethodRef', {}).get('name'),
                        'reference_number': payment.get('PaymentRefNum'),
                        'qb_data': json.dumps(payment),  # JSON-encode for JSONB column
                        'qb_last_modified': qb_last_modified,
                        'is_active': True,
                        'sync_error': None,
                        'cached_at': datetime.now(timezone.utc)
                    }
                    
                    # Upsert
                    await db.execute(
                        text("""
                            INSERT INTO quickbooks_payments_cache 
                            (qb_payment_id, customer_id, invoice_id, amount, payment_date, 
                             payment_method, reference_number, qb_data, qb_last_modified, 
                             is_active, sync_error, cached_at)
                            VALUES 
                            (:qb_payment_id, :customer_id, :invoice_id, :amount, :payment_date,
                             :payment_method, :reference_number, :qb_data, :qb_last_modified,
                             :is_active, :sync_error, :cached_at)
                            ON CONFLICT (qb_payment_id) DO UPDATE SET
                                customer_id = EXCLUDED.customer_id,
                                invoice_id = EXCLUDED.invoice_id,
                                amount = EXCLUDED.amount,
                                payment_date = EXCLUDED.payment_date,
                                payment_method = EXCLUDED.payment_method,
                                reference_number = EXCLUDED.reference_number,
                                qb_data = EXCLUDED.qb_data,
                                qb_last_modified = EXCLUDED.qb_last_modified,
                                is_active = EXCLUDED.is_active,
                                sync_error = NULL,
                                cached_at = EXCLUDED.cached_at
                        """),
                        payment_data
                    )
                    
                    records_synced += 1
                    
                except Exception as e:
                    logger.error(f"Failed to sync payment {qb_payment_id}: {e}")
                    errors += 1
                    
                    try:
                        await db.execute(
                            text("""
                                UPDATE quickbooks_payments_cache 
                                SET sync_error = :error 
                                WHERE qb_payment_id = :qb_payment_id
                            """),
                            {"error": str(e), "qb_payment_id": qb_payment_id}
                        )
                    except:
                        pass
            
            await db.commit()
            
            end_time = datetime.now(timezone.utc)
            duration_ms = int((end_time - start_time).total_seconds() * 1000)
            
            await self._update_sync_status(db, 'payments', start_time, duration_ms, records_synced, errors)
            
            logger.info(f"[SYNC] Payment sync complete: {records_synced} synced, {errors} errors, {duration_ms}ms")
            
            # Auto-promote to main table if enabled
            promotion_result = None
            if auto_promote and records_synced > 0:
                logger.info(f"[SYNC] Auto-promoting {records_synced} payments to main table")
                try:
                    promotion_result = await self.promote_payments_to_database(db)
                except Exception as e:
                    logger.error(f"[SYNC] Auto-promotion failed (sync succeeded): {e}")
                    # Don't fail the sync if promotion fails
            
            return {
                "records_synced": records_synced,
                "duration_ms": duration_ms,
                "errors": errors,
                "created": 0,  # TODO: Track created vs updated
                "updated": records_synced,
                "skipped": 0,
                "promotion": promotion_result  # Include promotion metrics
            }
            
        except Exception as e:
            logger.error(f"Payment sync failed: {e}", exc_info=True)
            await db.rollback()
            
            duration_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
            await self._update_sync_status(db, 'payments', start_time, duration_ms, records_synced, errors + 1, str(e))
            
            raise
    
    async def sync_all(self, db: AsyncSession, force_full_sync: bool = False) -> Dict[str, Any]:
        """
        Sync all entity types in mandatory order: Customers → Invoices → Payments.
        
        This order is CRITICAL to prevent orphan records:
        - Invoices reference customers
        - Payments reference invoices
        
        Only GC Compliance customers (CustomerTypeRef=698682) and their related data are synced.
        
        Args:
            db: Database session
            force_full_sync: If True, ignores last_sync_at and syncs everything
            
        Returns:
            Dict with combined metrics from all syncs
        """
        logger.info(f"[SYNC] Starting full GC Compliance sync (force_full: {force_full_sync})")
        
        results = {
            "customers": None,
            "invoices": None,
            "payments": None,
            "total_records": 0,
            "total_duration_ms": 0,
            "total_errors": 0
        }
        
        try:
            # Step 1: Sync customers (filtered by CustomerTypeRef=698682)
            logger.info("[SYNC] Step 1/3: Syncing GC Compliance customers...")
            since = None if force_full_sync else await self._get_last_sync(db, 'customers')
            results["customers"] = await self.sync_customers(db, since=since)
            logger.info(f"[SYNC] Step 1/3 complete: {results['customers']['records_synced']} customers synced")
            
            # Step 2: Sync invoices (only for GC Compliance customers)
            logger.info("[SYNC] Step 2/3: Syncing invoices for GC Compliance customers...")
            since = None if force_full_sync else await self._get_last_sync(db, 'invoices')
            results["invoices"] = await self.sync_invoices(db, since=since)
            logger.info(f"[SYNC] Step 2/3 complete: {results['invoices']['records_synced']} invoices synced")
            
            # Step 3: Sync payments (only for GC Compliance invoices)
            logger.info("[SYNC] Step 3/3: Syncing payments for GC Compliance invoices...")
            since = None if force_full_sync else await self._get_last_sync(db, 'payments')
            results["payments"] = await self.sync_payments(db, since=since)
            logger.info(f"[SYNC] Step 3/3 complete: {results['payments']['records_synced']} payments synced")
            
            # Calculate totals
            for entity_result in [results["customers"], results["invoices"], results["payments"]]:
                if entity_result:
                    results["total_records"] += entity_result["records_synced"]
                    results["total_duration_ms"] += entity_result["duration_ms"]
                    results["total_errors"] += entity_result["errors"]
            
            logger.info(f"[SYNC] Full sync complete: {results['total_records']} records, {results['total_duration_ms']}ms, {results['total_errors']} errors")
            
            return results
            
        except Exception as e:
            logger.error(f"Full sync failed: {e}", exc_info=True)
            raise
    
    async def _get_last_sync(self, db: AsyncSession, entity_type: str) -> Optional[datetime]:
        """Get last successful sync timestamp for an entity type."""
        result = await db.execute(
            text("SELECT last_sync_at FROM sync_status WHERE entity_type = :entity_type"),
            {"entity_type": entity_type}
        )
        row = result.fetchone()
        return row.last_sync_at if row and row.last_sync_at else None
    
    async def _update_sync_status(
        self, 
        db: AsyncSession, 
        entity_type: str, 
        sync_time: datetime,
        duration_ms: int,
        records_synced: int,
        errors: int,
        error_message: Optional[str] = None
    ):
        """Update sync_status table with sync results."""
        try:
            await db.execute(
                text("""
                    UPDATE sync_status SET
                        last_sync_at = :sync_time,
                        last_sync_duration_ms = :duration_ms,
                        records_synced = :records_synced,
                        sync_errors = :errors,
                        last_error_message = :error_message,
                        is_syncing = false,
                        updated_at = :updated_at
                    WHERE entity_type = :entity_type
                """),
                {
                    "entity_type": entity_type,
                    "sync_time": sync_time,
                    "duration_ms": duration_ms,
                    "records_synced": records_synced,
                    "errors": errors,
                    "error_message": error_message,
                    "updated_at": datetime.now(timezone.utc)
                }
            )
            await db.commit()
        except Exception as e:
            logger.error(f"Failed to update sync status: {e}")
            await db.rollback()
    
    async def create_customer_in_qb(self, db: AsyncSession, client_data: Dict[str, Any]) -> str:
        """
        Create a new customer in QuickBooks with GC Compliance type.
        
        App → QB Sync Rules:
        - Customer created in app MUST be created in QB first
        - CustomerTypeRef MUST be set to 698682 ("GC Compliance")
        - QB ID is stored and becomes authoritative identifier
        - No heuristic matching - only QB ID-based lookups
        
        Conflict Resolution:
        - Financial data (not applicable for customer creation)
        - Metadata: App provides initial values, QB stores authoritative record
        
        Args:
            db: Database session
            client_data: Dict with display_name, company_name, email, phone, etc.
            
        Returns:
            QuickBooks customer ID (authoritative identifier)
            
        Raises:
            Exception if QB creation fails
        """
        self.qb_service = get_quickbooks_service(db)
        
        logger.info(f"[APP→QB] Creating customer: {client_data.get('display_name')}")
        
        # Build QB Customer object with mandatory GC Compliance type
        qb_customer_data = {
            "DisplayName": client_data.get("display_name"),
            "CompanyName": client_data.get("company_name"),
            "GivenName": client_data.get("given_name"),
            "FamilyName": client_data.get("family_name"),
            "PrimaryEmailAddr": {"Address": client_data.get("email")} if client_data.get("email") else None,
            "PrimaryPhone": {"FreeFormNumber": client_data.get("phone")} if client_data.get("phone") else None,
            # CRITICAL: Assign "GC Compliance" customer type
            "CustomerTypeRef": {"value": self.GC_COMPLIANCE_CUSTOMER_TYPE}
        }
        
        # Create in QuickBooks
        qb_customer = await self.qb_service.create_customer(qb_customer_data)
        qb_customer_id = qb_customer.get("Id")
        
        logger.info(f"[APP→QB] Customer created: {qb_customer_id}")
        
        # Store in cache immediately
        await db.execute(
            text("""
                INSERT INTO quickbooks_customers_cache 
                (qb_customer_id, display_name, company_name, given_name, family_name, 
                 email, phone, qb_data, qb_last_modified, is_active, cached_at)
                VALUES 
                (:qb_customer_id, :display_name, :company_name, :given_name, :family_name,
                 :email, :phone, :qb_data, :qb_last_modified, true, :cached_at)
                ON CONFLICT (qb_customer_id) DO UPDATE SET
                    qb_data = EXCLUDED.qb_data,
                    qb_last_modified = EXCLUDED.qb_last_modified,
                    cached_at = EXCLUDED.cached_at
            """),
            {
                "qb_customer_id": qb_customer_id,
                "display_name": qb_customer.get("DisplayName"),
                "company_name": qb_customer.get("CompanyName"),
                "given_name": qb_customer.get("GivenName"),
                "family_name": qb_customer.get("FamilyName"),
                "email": qb_customer.get("PrimaryEmailAddr", {}).get("Address"),
                "phone": qb_customer.get("PrimaryPhone", {}).get("FreeFormNumber"),
                "qb_data": qb_customer,
                "qb_last_modified": qb_customer.get("MetaData", {}).get("LastUpdatedTime"),
                "cached_at": datetime.now(timezone.utc)
            }
        )
        await db.commit()
        
        return qb_customer_id
    
    async def promote_invoices_to_database(
        self,
        db: AsyncSession,
        qb_invoice_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Promote invoices from cache to main invoices table.
        
        Maps QB customer IDs to app client_ids using clients table.
        Creates business_id automatically via database trigger.
        
        Args:
            db: Database session
            qb_invoice_ids: Optional list of specific QB invoice IDs to promote.
                           If None, promotes all cached invoices.
        
        Returns:
            Dict with promotion metrics (promoted, skipped, errors)
        """
        start_time = datetime.now(timezone.utc)
        promoted = 0
        skipped = 0
        errors = 0
        
        try:
            logger.info(f"[PROMOTE] Starting invoice promotion from cache to main table")
            
            # Build query to get cached invoices
            if qb_invoice_ids:
                placeholders = ','.join([f':id_{i}' for i in range(len(qb_invoice_ids))])
                query = f"""
                    SELECT * FROM quickbooks_invoices_cache 
                    WHERE qb_invoice_id IN ({placeholders})
                """
                params = {f'id_{i}': qb_id for i, qb_id in enumerate(qb_invoice_ids)}
            else:
                query = "SELECT * FROM quickbooks_invoices_cache WHERE is_active = true"
                params = {}
            
            result = await db.execute(text(query), params)
            cached_invoices = result.fetchall()
            
            logger.info(f"[PROMOTE] Found {len(cached_invoices)} cached invoices to process")
            
            for cached_invoice in cached_invoices:
                try:
                    qb_invoice_id = cached_invoice.qb_invoice_id
                    qb_customer_id = cached_invoice.customer_id
                    
                    # Map QB customer ID to app client_id
                    client_result = await db.execute(
                        text("SELECT client_id FROM clients WHERE qb_customer_id = :qb_customer_id"),
                        {"qb_customer_id": qb_customer_id}
                    )
                    client_row = client_result.fetchone()
                    
                    if not client_row:
                        logger.warning(f"[PROMOTE] Skipping invoice {qb_invoice_id}: QB customer {qb_customer_id} not found in clients table")
                        skipped += 1
                        continue
                    
                    client_id = client_row.client_id
                    
                    # Get project_id from client
                    # WARNING: Using LIMIT 1 is a temporary fallback for single-project clients only.
                    # Production-safe approach requires:
                    # 1. QB custom field mapping (e.g., Class or Department)
                    # 2. DocNumber pattern matching (e.g., "PROJ-123-INV001")
                    # 3. Explicit client-project mapping table
                    # If client has multiple projects and no clear mapping → SKIP, do not guess
                    # TODO: Implement proper project resolution before multi-project clients
                    project_result = await db.execute(
                        text("SELECT project_id FROM projects WHERE client_id = :client_id LIMIT 1"),
                        {"client_id": client_id}
                    )
                    project_row = project_result.fetchone()
                    
                    if not project_row:
                        logger.warning(f"[PROMOTE] Skipping invoice {qb_invoice_id}: No project found for client {client_id}")
                        skipped += 1
                        continue
                    
                    project_id = project_row.project_id
                    
                    # Parse QB JSON data
                    qb_data = json.loads(cached_invoice.qb_data) if isinstance(cached_invoice.qb_data, str) else cached_invoice.qb_data
                    
                    # Extract invoice details from cache
                    total_amount = float(cached_invoice.total_amount or 0)
                    balance = float(cached_invoice.balance or 0)
                    
                    # Derive status from QB data
                    # If balance is 0, invoice is paid. Otherwise, it's open.
                    status = 'PAID' if balance == 0 else 'OPEN'
                    
                    # Extract additional QB fields with safe null handling
                    bill_email_obj = qb_data.get('BillEmail')
                    bill_email = bill_email_obj.get('Address') if bill_email_obj else None
                    
                    currency_ref = qb_data.get('CurrencyRef')
                    currency_code = currency_ref.get('value') if currency_ref else None
                    
                    sales_term_ref = qb_data.get('SalesTermRef')
                    payment_terms = sales_term_ref.get('name') if sales_term_ref else None
                    
                    customer_memo_obj = qb_data.get('CustomerMemo')
                    customer_memo = customer_memo_obj.get('value') if customer_memo_obj else None
                    
                    invoice_data = {
                        'qb_invoice_id': qb_invoice_id,
                        'project_id': project_id,
                        'client_id': client_id,
                        'invoice_number': qb_data.get('DocNumber'),
                        'invoice_date': datetime.fromisoformat(qb_data['TxnDate']) if qb_data.get('TxnDate') else None,
                        'due_date': datetime.fromisoformat(qb_data['DueDate']) if qb_data.get('DueDate') else None,
                        'subtotal': total_amount,  # QB API doesn't separate subtotal from total consistently
                        'total_amount': total_amount,
                        'amount_paid': total_amount - balance,  # Calculate paid amount from balance
                        'balance_due': balance,
                        'status': status,  # Derived from balance
                        'sync_status': 'synced',
                        'notes': f"Imported from QuickBooks (QB ID: {qb_invoice_id})",
                        # New QB-specific fields
                        'email_status': qb_data.get('EmailStatus'),
                        'print_status': qb_data.get('PrintStatus'),
                        'bill_email': bill_email,
                        'bill_address': json.dumps(qb_data.get('BillAddr')) if qb_data.get('BillAddr') else None,
                        'ship_address': json.dumps(qb_data.get('ShipAddr')) if qb_data.get('ShipAddr') else None,
                        'currency_code': currency_code,
                        'payment_terms': payment_terms,
                        'qb_metadata': json.dumps(qb_data.get('MetaData')) if qb_data.get('MetaData') else None,
                        'private_note': qb_data.get('PrivateNote'),
                        'customer_memo': customer_memo
                    }
                    
                    # Upsert into invoices table
                    # Note: amount_paid will be recalculated when payments are promoted
                    await db.execute(
                        text("""
                            INSERT INTO invoices 
                            (qb_invoice_id, project_id, client_id, invoice_number, invoice_date, due_date,
                             subtotal, total_amount, amount_paid, balance_due, status, sync_status, notes,
                             email_status, print_status, bill_email, bill_address, ship_address,
                             currency_code, payment_terms, qb_metadata, private_note, customer_memo)
                            VALUES 
                            (:qb_invoice_id, :project_id, :client_id, :invoice_number, :invoice_date, :due_date,
                             :subtotal, :total_amount, :amount_paid, :balance_due, :status, :sync_status, :notes,
                             :email_status, :print_status, :bill_email, :bill_address, :ship_address,
                             :currency_code, :payment_terms, :qb_metadata, :private_note, :customer_memo)
                            ON CONFLICT (qb_invoice_id) DO UPDATE SET
                                invoice_number = EXCLUDED.invoice_number,
                                invoice_date = EXCLUDED.invoice_date,
                                due_date = EXCLUDED.due_date,
                                subtotal = EXCLUDED.subtotal,
                                total_amount = EXCLUDED.total_amount,
                                amount_paid = EXCLUDED.amount_paid,
                                balance_due = EXCLUDED.balance_due,
                                status = EXCLUDED.status,
                                email_status = EXCLUDED.email_status,
                                print_status = EXCLUDED.print_status,
                                bill_email = EXCLUDED.bill_email,
                                bill_address = EXCLUDED.bill_address,
                                ship_address = EXCLUDED.ship_address,
                                currency_code = EXCLUDED.currency_code,
                                payment_terms = EXCLUDED.payment_terms,
                                qb_metadata = EXCLUDED.qb_metadata,
                                private_note = EXCLUDED.private_note,
                                customer_memo = EXCLUDED.customer_memo,
                                updated_at = CURRENT_TIMESTAMP
                        """),
                        invoice_data
                    )
                    
                    promoted += 1
                    logger.debug(f"[PROMOTE] Promoted invoice {qb_invoice_id}")
                    # Commit after each successful promotion to avoid transaction cascade failures
                    await db.commit()
                    
                except Exception as e:
                    logger.error(f"[PROMOTE] Failed to promote invoice {qb_invoice_id}: {e}")
                    errors += 1
                    # Rollback the failed transaction to allow subsequent invoices to process
                    await db.rollback()
            
            # Final commit (likely no-op since we commit after each success)
            
            duration_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
            logger.info(f"[PROMOTE] Invoice promotion complete: {promoted} promoted, {skipped} skipped, {errors} errors, {duration_ms}ms")
            
            return {
                "promoted": promoted,
                "skipped": skipped,
                "errors": errors,
                "duration_ms": duration_ms
            }
            
        except Exception as e:
            logger.error(f"[PROMOTE] Invoice promotion failed: {e}", exc_info=True)
            await db.rollback()
            raise
    
    async def promote_payments_to_database(
        self,
        db: AsyncSession,
        qb_payment_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Promote payments from cache to main payments table.
        
        Maps QB customer IDs to client_ids and QB invoice IDs to invoice_ids.
        Updates invoice.amount_paid and invoice.balance_due automatically.
        
        Args:
            db: Database session
            qb_payment_ids: Optional list of specific QB payment IDs to promote.
                           If None, promotes all cached payments.
        
        Returns:
            Dict with promotion metrics
        """
        start_time = datetime.now(timezone.utc)
        promoted = 0
        skipped = 0
        errors = 0
        
        try:
            logger.info(f"[PROMOTE] Starting payment promotion from cache to main table")
            
            # Build query
            if qb_payment_ids:
                placeholders = ','.join([f':id_{i}' for i in range(len(qb_payment_ids))])
                query = f"""
                    SELECT * FROM quickbooks_payments_cache 
                    WHERE qb_payment_id IN ({placeholders})
                """
                params = {f'id_{i}': qb_id for i, qb_id in enumerate(qb_payment_ids)}
            else:
                query = "SELECT * FROM quickbooks_payments_cache WHERE is_active = true"
                params = {}
            
            result = await db.execute(text(query), params)
            cached_payments = result.fetchall()
            
            logger.info(f"[PROMOTE] Found {len(cached_payments)} cached payments to process")
            
            for cached_payment in cached_payments:
                try:
                    qb_payment_id = cached_payment.qb_payment_id
                    qb_customer_id = cached_payment.customer_id
                    qb_invoice_id = cached_payment.invoice_id
                    
                    # Map QB customer ID to client_id
                    client_result = await db.execute(
                        text("SELECT client_id FROM clients WHERE qb_customer_id = :qb_customer_id"),
                        {"qb_customer_id": qb_customer_id}
                    )
                    client_row = client_result.fetchone()
                    
                    if not client_row:
                        logger.warning(f"[PROMOTE] Skipping payment {qb_payment_id}: QB customer {qb_customer_id} not found")
                        skipped += 1
                        continue
                    
                    client_id = client_row.client_id
                    
                    # Map QB invoice ID to invoice_id (if payment is linked to invoice)
                    invoice_id = None
                    project_id = None
                    if qb_invoice_id:
                        invoice_result = await db.execute(
                            text("SELECT invoice_id, project_id FROM invoices WHERE qb_invoice_id = :qb_invoice_id"),
                            {"qb_invoice_id": qb_invoice_id}
                        )
                        invoice_row = invoice_result.fetchone()
                        
                        if invoice_row:
                            invoice_id = invoice_row.invoice_id
                            project_id = invoice_row.project_id
                        else:
                            # CRITICAL: Payment references an invoice that hasn't been promoted yet or failed promotion
                            # This is an orphan payment - SKIP to prevent breaking invoice-level accounting
                            logger.warning(f"[PROMOTE] Skipping payment {qb_payment_id}: QB invoice {qb_invoice_id} not found in main invoices table (promote invoices first)")
                            skipped += 1
                            continue
                    else:
                        # Payment without invoice link (rare but valid in QB for prepayments/credits)
                        # Try to get project from client for these edge cases only
                        project_result = await db.execute(
                            text("SELECT project_id FROM projects WHERE client_id = :client_id LIMIT 1"),
                            {"client_id": client_id}
                        )
                        project_row = project_result.fetchone()
                        
                        if not project_row:
                            logger.warning(f"[PROMOTE] Skipping unlinked payment {qb_payment_id}: No project found for client {client_id}")
                            skipped += 1
                            continue
                        
                        project_id = project_row.project_id
                        logger.info(f"[PROMOTE] Payment {qb_payment_id} has no invoice link - treating as prepayment/credit")
                    
                    # Extract QB payment data
                    qb_data = cached_payment.qb_data or {}
                    
                    # Extract deposit account
                    deposit_ref = qb_data.get('DepositToAccountRef')
                    deposit_account = deposit_ref.get('value') if deposit_ref else None
                    
                    # Extract currency
                    currency_ref = qb_data.get('CurrencyRef')
                    currency_code = currency_ref.get('value') if currency_ref else None
                    
                    # Extract QB metadata
                    metadata = qb_data.get('MetaData')
                    qb_metadata = json.dumps(metadata) if metadata else None
                    
                    # Extract Line array for linked transactions
                    line_array = qb_data.get('Line', [])
                    linked_transactions = json.dumps(line_array) if line_array else None
                    
                    payment_data = {
                        'qb_payment_id': qb_payment_id,
                        'invoice_id': invoice_id,
                        'client_id': client_id,
                        'project_id': project_id,
                        'amount': float(cached_payment.amount) if cached_payment.amount else 0.0,
                        'payment_date': cached_payment.payment_date,
                        'payment_method': cached_payment.payment_method or 'Check',
                        'status': 'POSTED',  # POSTED = successfully received payment (valid enum: FAILED, PENDING, POSTED, REFUNDED)
                        'reference_number': cached_payment.reference_number,
                        'check_number': cached_payment.reference_number,  # Use reference_number as check_number
                        'sync_status': 'synced',
                        'notes': f"Imported from QuickBooks (QB ID: {qb_payment_id})",
                        # QuickBooks metadata fields
                        'deposit_account': deposit_account,
                        'currency_code': currency_code,
                        'total_amount': float(qb_data.get('TotalAmt', 0)) if qb_data.get('TotalAmt') else None,
                        'unapplied_amount': float(qb_data.get('UnappliedAmt', 0)) if qb_data.get('UnappliedAmt') is not None else None,
                        'process_payment': qb_data.get('ProcessPayment'),
                        'linked_transactions': linked_transactions,
                        'qb_metadata': qb_metadata,
                        'private_note': qb_data.get('PrivateNote')
                    }
                    
                    # Upsert into payments table
                    await db.execute(
                        text("""
                            INSERT INTO payments 
                            (qb_payment_id, invoice_id, client_id, project_id, amount, payment_date,
                             payment_method, status, reference_number, check_number, sync_status, notes,
                             deposit_account, currency_code, total_amount, unapplied_amount, process_payment,
                             linked_transactions, qb_metadata, private_note)
                            VALUES 
                            (:qb_payment_id, :invoice_id, :client_id, :project_id, :amount, :payment_date,
                             :payment_method, :status, :reference_number, :check_number, :sync_status, :notes,
                             :deposit_account, :currency_code, :total_amount, :unapplied_amount, :process_payment,
                             :linked_transactions, :qb_metadata, :private_note)
                            ON CONFLICT (qb_payment_id) DO UPDATE SET
                                amount = EXCLUDED.amount,
                                payment_date = EXCLUDED.payment_date,
                                payment_method = EXCLUDED.payment_method,
                                reference_number = EXCLUDED.reference_number,
                                deposit_account = EXCLUDED.deposit_account,
                                currency_code = EXCLUDED.currency_code,
                                total_amount = EXCLUDED.total_amount,
                                unapplied_amount = EXCLUDED.unapplied_amount,
                                process_payment = EXCLUDED.process_payment,
                                linked_transactions = EXCLUDED.linked_transactions,
                                qb_metadata = EXCLUDED.qb_metadata,
                                private_note = EXCLUDED.private_note,
                                updated_at = CURRENT_TIMESTAMP
                        """),
                        payment_data
                    )
                    
                    # Update invoice amount_paid and balance_due if payment is linked
                    if invoice_id:
                        await db.execute(
                            text("""
                                UPDATE invoices 
                                SET 
                                    amount_paid = COALESCE((
                                        SELECT SUM(amount) 
                                        FROM payments 
                                        WHERE invoice_id = :invoice_id AND status = 'POSTED'
                                    ), 0),
                                    balance_due = total_amount - COALESCE((
                                        SELECT SUM(amount) 
                                        FROM payments 
                                        WHERE invoice_id = :invoice_id AND status = 'POSTED'
                                    ), 0),
                                    updated_at = CURRENT_TIMESTAMP
                                WHERE invoice_id = :invoice_id
                            """),
                            {"invoice_id": invoice_id}
                        )
                    
                    promoted += 1
                    await db.commit()  # Commit after each success
                    logger.debug(f"[PROMOTE] Promoted payment {qb_payment_id}")
                    
                except Exception as e:
                    logger.error(f"[PROMOTE] Failed to promote payment {qb_payment_id}: {e}")
                    errors += 1
                    await db.rollback()  # Rollback to reset transaction
            
            duration_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
            logger.info(f"[PROMOTE] Payment promotion complete: {promoted} promoted, {skipped} skipped, {errors} errors, {duration_ms}ms")
            
            return {
                "promoted": promoted,
                "skipped": skipped,
                "errors": errors,
                "duration_ms": duration_ms
            }
            
        except Exception as e:
            logger.error(f"[PROMOTE] Payment promotion failed: {e}", exc_info=True)
            await db.rollback()
            raise


# Singleton instance
qb_sync_service = QuickBooksSyncService()
