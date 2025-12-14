"""
QuickBooks Sync Service

Handles synchronization of QuickBooks data to local cache tables.
Implements delta sync using qb_last_modified timestamps to minimize API calls.
Includes circuit breaker pattern for API resilience.
"""

import logging
from datetime import datetime, timezone
from typing import List, Dict, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.services.quickbooks_service import quickbooks_service
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
    """
    
    def __init__(self):
        self.qb_service = quickbooks_service
    
    async def sync_customers(self, db: AsyncSession, since: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Sync customers from QuickBooks to quickbooks_customers_cache.
        
        Args:
            db: Database session
            since: Only fetch customers modified after this timestamp (for delta sync)
            
        Returns:
            Dict with sync metrics (records_synced, duration_ms, errors)
        """
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
            
            # Build QuickBooks query with delta filter
            query = "SELECT * FROM Customer"
            if since:
                # Format datetime for QuickBooks API (ISO 8601)
                since_str = since.strftime('%Y-%m-%dT%H:%M:%S-00:00')
                query += f" WHERE Metadata.LastUpdatedTime > '{since_str}'"
                logger.info(f"[SYNC] Delta query: fetching customers modified after {since_str}")
            
            query += " MAXRESULTS 1000"
            
            # Fetch customers from QuickBooks with circuit breaker protection
            try:
                customers = await qb_circuit_breaker.call(
                    self.qb_service.query,
                    query
                )
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
                return {"records_synced": 0, "duration_ms": 0, "errors": 0}
            
            logger.info(f"[SYNC] Fetched {len(customers)} customers from QuickBooks")
            
            # Process each customer
            for customer in customers:
                try:
                    qb_customer_id = customer.get('Id')
                    
                    # Extract customer data
                    customer_data = {
                        'qb_customer_id': qb_customer_id,
                        'display_name': customer.get('DisplayName'),
                        'company_name': customer.get('CompanyName'),
                        'given_name': customer.get('GivenName'),
                        'family_name': customer.get('FamilyName'),
                        'email': customer.get('PrimaryEmailAddr', {}).get('Address') if customer.get('PrimaryEmailAddr') else None,
                        'phone': customer.get('PrimaryPhone', {}).get('FreeFormNumber') if customer.get('PrimaryPhone') else None,
                        'qb_data': customer,  # Store full QB object as JSONB
                        'qb_last_modified': customer.get('MetaData', {}).get('LastUpdatedTime'),
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
                "errors": errors
            }
            
        except Exception as e:
            logger.error(f"Customer sync failed: {e}", exc_info=True)
            await db.rollback()
            
            # Update sync status with error
            duration_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
            await self._update_sync_status(db, 'customers', start_time, duration_ms, records_synced, errors + 1, str(e))
            
            raise
    
    async def sync_invoices(self, db: AsyncSession, since: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Sync invoices from QuickBooks to quickbooks_invoices_cache.
        
        Args:
            db: Database session
            since: Only fetch invoices modified after this timestamp
            
        Returns:
            Dict with sync metrics
        """
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
                return {"records_synced": 0, "duration_ms": 0, "errors": 0}
            
            logger.info(f"[SYNC] Fetched {len(invoices)} invoices from QuickBooks")
            
            # Process each invoice
            for invoice in invoices:
                try:
                    qb_invoice_id = invoice.get('Id')
                    
                    invoice_data = {
                        'qb_invoice_id': qb_invoice_id,
                        'customer_id': invoice.get('CustomerRef', {}).get('value'),
                        'doc_number': invoice.get('DocNumber'),
                        'total_amount': invoice.get('TotalAmt'),
                        'balance': invoice.get('Balance'),
                        'due_date': invoice.get('DueDate'),
                        'qb_data': invoice,
                        'qb_last_modified': invoice.get('MetaData', {}).get('LastUpdatedTime'),
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
            
            return {
                "records_synced": records_synced,
                "duration_ms": duration_ms,
                "errors": errors
            }
            
        except Exception as e:
            logger.error(f"Invoice sync failed: {e}", exc_info=True)
            await db.rollback()
            
            duration_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
            await self._update_sync_status(db, 'invoices', start_time, duration_ms, records_synced, errors + 1, str(e))
            
            raise
    
    async def sync_payments(self, db: AsyncSession, since: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Sync payments from QuickBooks to quickbooks_payments_cache.
        
        Args:
            db: Database session
            since: Only fetch payments modified after this timestamp
            
        Returns:
            Dict with sync metrics
        """
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
                return {"records_synced": 0, "duration_ms": 0, "errors": 0}
            
            logger.info(f"[SYNC] Fetched {len(payments)} payments from QuickBooks")
            
            # Process each payment
            for payment in payments:
                try:
                    qb_payment_id = payment.get('Id')
                    
                    # Extract linked invoice if present
                    invoice_id = None
                    if payment.get('Line'):
                        for line in payment['Line']:
                            if line.get('LinkedTxn'):
                                for linked_txn in line['LinkedTxn']:
                                    if linked_txn.get('TxnType') == 'Invoice':
                                        invoice_id = linked_txn.get('TxnId')
                                        break
                    
                    payment_data = {
                        'qb_payment_id': qb_payment_id,
                        'customer_id': payment.get('CustomerRef', {}).get('value'),
                        'invoice_id': invoice_id,
                        'amount': payment.get('TotalAmt'),
                        'payment_date': payment.get('TxnDate'),
                        'payment_method': payment.get('PaymentMethodRef', {}).get('name'),
                        'reference_number': payment.get('PaymentRefNum'),
                        'qb_data': payment,
                        'qb_last_modified': payment.get('MetaData', {}).get('LastUpdatedTime'),
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
            
            return {
                "records_synced": records_synced,
                "duration_ms": duration_ms,
                "errors": errors
            }
            
        except Exception as e:
            logger.error(f"Payment sync failed: {e}", exc_info=True)
            await db.rollback()
            
            duration_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
            await self._update_sync_status(db, 'payments', start_time, duration_ms, records_synced, errors + 1, str(e))
            
            raise
    
    async def sync_all(self, db: AsyncSession, force_full_sync: bool = False) -> Dict[str, Any]:
        """
        Sync all entity types (customers, invoices, payments).
        
        Args:
            db: Database session
            force_full_sync: If True, ignores last_sync_at and syncs everything
            
        Returns:
            Dict with combined metrics from all syncs
        """
        logger.info(f"[SYNC] Starting full sync (force_full: {force_full_sync})")
        
        results = {
            "customers": None,
            "invoices": None,
            "payments": None,
            "total_records": 0,
            "total_duration_ms": 0,
            "total_errors": 0
        }
        
        try:
            # Sync customers first (invoices/payments reference customers)
            since = None if force_full_sync else await self._get_last_sync(db, 'customers')
            results["customers"] = await self.sync_customers(db, since=since)
            
            # Sync invoices
            since = None if force_full_sync else await self._get_last_sync(db, 'invoices')
            results["invoices"] = await self.sync_invoices(db, since=since)
            
            # Sync payments
            since = None if force_full_sync else await self._get_last_sync(db, 'payments')
            results["payments"] = await self.sync_payments(db, since=since)
            
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


# Singleton instance
qb_sync_service = QuickBooksSyncService()
