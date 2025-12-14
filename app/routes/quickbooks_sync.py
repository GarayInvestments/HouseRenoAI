"""
QuickBooks Sync API Endpoints

Provides manual sync triggers and cache data access.
"""

import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User
from app.db.session import get_db
from app.routes.auth_supabase import get_current_user
from app.services.quickbooks_sync_service import qb_sync_service
from app.utils.circuit_breaker import qb_circuit_breaker
from app.services.scheduler_service import scheduler_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/quickbooks/sync", tags=["quickbooks-sync"])


@router.post("/customers")
async def sync_customers(
    force_full: bool = Query(False, description="Force full sync (ignore last_sync_at)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Manually trigger customer sync from QuickBooks.
    
    - **force_full**: If true, syncs all customers regardless of last_sync_at
    - By default, performs delta sync (only changed records)
    """
    try:
        logger.info(f"[API] Manual customer sync triggered by {current_user.email} (force_full={force_full})")
        
        since = None if force_full else await qb_sync_service._get_last_sync(db, 'customers')
        result = await qb_sync_service.sync_customers(db, since=since)
        
        return {
            "success": True,
            "entity_type": "customers",
            "force_full": force_full,
            **result
        }
        
    except Exception as e:
        logger.error(f"Customer sync failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/invoices")
async def sync_invoices(
    force_full: bool = Query(False, description="Force full sync"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Manually trigger invoice sync from QuickBooks.
    """
    try:
        logger.info(f"[API] Manual invoice sync triggered by {current_user.email} (force_full={force_full})")
        
        since = None if force_full else await qb_sync_service._get_last_sync(db, 'invoices')
        result = await qb_sync_service.sync_invoices(db, since=since)
        
        return {
            "success": True,
            "entity_type": "invoices",
            "force_full": force_full,
            **result
        }
        
    except Exception as e:
        logger.error(f"Invoice sync failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/payments")
async def sync_payments(
    force_full: bool = Query(False, description="Force full sync"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Manually trigger payment sync from QuickBooks.
    """
    try:
        logger.info(f"[API] Manual payment sync triggered by {current_user.email} (force_full={force_full})")
        
        since = None if force_full else await qb_sync_service._get_last_sync(db, 'payments')
        result = await qb_sync_service.sync_payments(db, since=since)
        
        return {
            "success": True,
            "entity_type": "payments",
            "force_full": force_full,
            **result
        }
        
    except Exception as e:
        logger.error(f"Payment sync failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/all")
async def sync_all(
    force_full: bool = Query(False, description="Force full sync for all entities"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Manually trigger sync for all entity types (customers, invoices, payments).
    
    Syncs are performed in order: customers → invoices → payments
    """
    try:
        logger.info(f"[API] Manual full sync triggered by {current_user.email} (force_full={force_full})")
        
        result = await qb_sync_service.sync_all(db, force_full_sync=force_full)
        
        return {
            "success": True,
            "force_full": force_full,
            **result
        }
        
    except Exception as e:
        logger.error(f"Full sync failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_sync_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get sync status for all entity types.
    
    Returns last sync time, record counts, errors, and next scheduled sync.
    """
    try:
        result = await db.execute(
            text("""
                SELECT 
                    entity_type,
                    last_sync_at,
                    last_sync_duration_ms,
                    records_synced,
                    sync_errors,
                    last_error_message,
                    is_syncing,
                    next_sync_at,
                    updated_at
                FROM sync_status
                ORDER BY entity_type
            """)
        )
        
        rows = result.fetchall()
        
        status = []
        for row in rows:
            # Calculate time since last sync
            hours_since_sync = None
            if row.last_sync_at:
                delta = datetime.now() - row.last_sync_at.replace(tzinfo=None)
                hours_since_sync = delta.total_seconds() / 3600
            
            # Determine health status
            health = "unknown"
            if row.last_sync_at:
                if hours_since_sync < 4:
                    health = "healthy"  # Green
                elif hours_since_sync < 8:
                    health = "warning"  # Yellow
                else:
                    health = "stale"  # Red
            
            status.append({
                "entity_type": row.entity_type,
                "last_sync_at": row.last_sync_at.isoformat() if row.last_sync_at else None,
                "hours_since_sync": round(hours_since_sync, 1) if hours_since_sync else None,
                "last_sync_duration_ms": row.last_sync_duration_ms,
                "records_synced": row.records_synced,
                "sync_errors": row.sync_errors,
                "last_error_message": row.last_error_message,
                "is_syncing": row.is_syncing,
                "next_sync_at": row.next_sync_at.isoformat() if row.next_sync_at else None,
                "health": health,
                "updated_at": row.updated_at.isoformat() if row.updated_at else None
            })
        
        return {
            "sync_status": status,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get sync status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cache/customers")
async def get_cached_customers(
    limit: int = Query(100, description="Max records to return"),
    offset: int = Query(0, description="Offset for pagination"),
    active_only: bool = Query(True, description="Only return active customers"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get customers from local cache.
    
    Fast response (<200ms) - no QuickBooks API calls.
    """
    try:
        # Build query
        query = """
            SELECT 
                qb_customer_id, display_name, company_name, given_name, family_name,
                email, phone, qb_last_modified, is_active, cached_at
            FROM quickbooks_customers_cache
        """
        
        if active_only:
            query += " WHERE is_active = true"
        
        query += " ORDER BY display_name LIMIT :limit OFFSET :offset"
        
        # Execute
        result = await db.execute(
            text(query),
            {"limit": limit, "offset": offset}
        )
        
        customers = []
        for row in result.fetchall():
            customers.append({
                "qb_customer_id": row.qb_customer_id,
                "display_name": row.display_name,
                "company_name": row.company_name,
                "given_name": row.given_name,
                "family_name": row.family_name,
                "email": row.email,
                "phone": row.phone,
                "qb_last_modified": row.qb_last_modified,
                "is_active": row.is_active,
                "cached_at": row.cached_at.isoformat() if row.cached_at else None
            })
        
        # Get total count
        count_result = await db.execute(
            text("SELECT COUNT(*) as total FROM quickbooks_customers_cache" + 
                 (" WHERE is_active = true" if active_only else ""))
        )
        total = count_result.fetchone().total
        
        return {
            "customers": customers,
            "total": total,
            "limit": limit,
            "offset": offset,
            "source": "cache"
        }
        
    except Exception as e:
        logger.error(f"Failed to get cached customers: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cache/invoices")
async def get_cached_invoices(
    limit: int = Query(100, description="Max records to return"),
    offset: int = Query(0, description="Offset for pagination"),
    customer_id: Optional[str] = Query(None, description="Filter by QB customer ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get invoices from local cache.
    
    Fast response - no QuickBooks API calls.
    """
    try:
        # Build query
        query = """
            SELECT 
                qb_invoice_id, customer_id, doc_number, total_amount, balance,
                due_date, qb_last_modified, cached_at
            FROM quickbooks_invoices_cache
        """
        
        params = {"limit": limit, "offset": offset}
        
        if customer_id:
            query += " WHERE customer_id = :customer_id"
            params["customer_id"] = customer_id
        
        query += " ORDER BY due_date DESC LIMIT :limit OFFSET :offset"
        
        # Execute
        result = await db.execute(text(query), params)
        
        invoices = []
        for row in result.fetchall():
            invoices.append({
                "qb_invoice_id": row.qb_invoice_id,
                "customer_id": row.customer_id,
                "doc_number": row.doc_number,
                "total_amount": float(row.total_amount) if row.total_amount else 0.0,
                "balance": float(row.balance) if row.balance else 0.0,
                "due_date": row.due_date,
                "qb_last_modified": row.qb_last_modified,
                "cached_at": row.cached_at.isoformat() if row.cached_at else None
            })
        
        # Get total count
        count_query = "SELECT COUNT(*) as total FROM quickbooks_invoices_cache"
        if customer_id:
            count_query += " WHERE customer_id = :customer_id"
        
        count_result = await db.execute(text(count_query), {"customer_id": customer_id} if customer_id else {})
        total = count_result.fetchone().total
        
        return {
            "invoices": invoices,
            "total": total,
            "limit": limit,
            "offset": offset,
            "customer_id": customer_id,
            "source": "cache"
        }
        
    except Exception as e:
        logger.error(f"Failed to get cached invoices: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cache/payments")
async def get_cached_payments(
    limit: int = Query(100, description="Max records to return"),
    offset: int = Query(0, description="Offset for pagination"),
    customer_id: Optional[str] = Query(None, description="Filter by QB customer ID"),
    invoice_id: Optional[str] = Query(None, description="Filter by QB invoice ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get payments from local cache.
    
    Fast response - no QuickBooks API calls.
    """
    try:
        # Build query
        query = """
            SELECT 
                qb_payment_id, customer_id, invoice_id, amount, payment_date,
                payment_method, reference_number, qb_last_modified, cached_at
            FROM quickbooks_payments_cache
        """
        
        params = {"limit": limit, "offset": offset}
        where_clauses = []
        
        if customer_id:
            where_clauses.append("customer_id = :customer_id")
            params["customer_id"] = customer_id
        
        if invoice_id:
            where_clauses.append("invoice_id = :invoice_id")
            params["invoice_id"] = invoice_id
        
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)
        
        query += " ORDER BY payment_date DESC LIMIT :limit OFFSET :offset"
        
        # Execute
        result = await db.execute(text(query), params)
        
        payments = []
        for row in result.fetchall():
            payments.append({
                "qb_payment_id": row.qb_payment_id,
                "customer_id": row.customer_id,
                "invoice_id": row.invoice_id,
                "amount": float(row.amount) if row.amount else 0.0,
                "payment_date": row.payment_date,
                "payment_method": row.payment_method,
                "reference_number": row.reference_number,
                "qb_last_modified": row.qb_last_modified,
                "cached_at": row.cached_at.isoformat() if row.cached_at else None
            })
        
        # Get total count
        count_query = "SELECT COUNT(*) as total FROM quickbooks_payments_cache"
        if where_clauses:
            count_query += " WHERE " + " AND ".join(where_clauses)
        
        count_result = await db.execute(text(count_query), 
            {k: v for k, v in params.items() if k not in ['limit', 'offset']})
        total = count_result.fetchone().total
        
        return {
            "payments": payments,
            "total": total,
            "limit": limit,
            "offset": offset,
            "customer_id": customer_id,
            "invoice_id": invoice_id,
            "source": "cache"
        }
        
    except Exception as e:
        logger.error(f"Failed to get cached payments: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/circuit-breaker")
async def get_circuit_breaker_status(
    current_user: User = Depends(get_current_user)
):
    """
    Get current circuit breaker status.
    
    Shows circuit state, failure count, and time until retry.
    Useful for monitoring and debugging sync issues.
    """
    try:
        status = qb_circuit_breaker.get_status()
        return {
            "circuit_breaker": status,
            "explanation": {
                "closed": "Normal operation - requests pass through",
                "open": "Failing fast - no API calls attempted (cooling down)",
                "half_open": "Testing recovery - limited requests allowed"
            }
        }
    except Exception as e:
        logger.error(f"Failed to get circuit breaker status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/circuit-breaker/reset")
async def reset_circuit_breaker(
    current_user: User = Depends(get_current_user)
):
    """
    Manually reset circuit breaker to CLOSED state.
    
    Use this to force circuit closed after resolving QuickBooks API issues.
    Only for admin/debugging purposes.
    """
    try:
        old_status = qb_circuit_breaker.get_status()
        qb_circuit_breaker.reset()
        new_status = qb_circuit_breaker.get_status()
        
        logger.info(f"[ADMIN] Circuit breaker manually reset by {current_user.email}")
        
        return {
            "message": "Circuit breaker reset to CLOSED",
            "old_state": old_status["state"],
            "new_state": new_status["state"],
            "reset_by": current_user.email
        }
    except Exception as e:
        logger.error(f"Failed to reset circuit breaker: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/scheduler")
async def get_scheduler_status(
    current_user: User = Depends(get_current_user)
):
    """
    Get current scheduler status.
    
    Shows whether scheduler is running, next sync time, and schedule.
    """
    try:
        status = scheduler_service.get_status()
        return status
    except Exception as e:
        logger.error(f"Failed to get scheduler status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scheduler/trigger")
async def trigger_sync_now(
    current_user: User = Depends(get_current_user)
):
    """
    Manually trigger scheduled sync job immediately.
    
    Runs sync outside of normal schedule. Useful for testing or
    forcing immediate sync after known data changes.
    """
    try:
        logger.info(f"[ADMIN] Manual sync triggered by {current_user.email}")
        await scheduler_service.trigger_now()
        
        return {
            "message": "Sync job triggered successfully",
            "triggered_by": current_user.email,
            "note": "Check sync status endpoint for results"
        }
    except Exception as e:
        logger.error(f"Failed to trigger sync: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scheduler/pause")
async def pause_scheduler(
    current_user: User = Depends(get_current_user)
):
    """
    Pause the scheduler (jobs won't run but scheduler stays alive).
    
    Use this to temporarily disable automatic syncs without stopping scheduler.
    """
    try:
        await scheduler_service.pause()
        logger.info(f"[ADMIN] Scheduler paused by {current_user.email}")
        
        return {
            "message": "Scheduler paused",
            "paused_by": current_user.email,
            "status": scheduler_service.get_status()
        }
    except Exception as e:
        logger.error(f"Failed to pause scheduler: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scheduler/resume")
async def resume_scheduler(
    current_user: User = Depends(get_current_user)
):
    """
    Resume the scheduler after pause.
    """
    try:
        await scheduler_service.resume()
        logger.info(f"[ADMIN] Scheduler resumed by {current_user.email}")
        
        return {
            "message": "Scheduler resumed",
            "resumed_by": current_user.email,
            "status": scheduler_service.get_status()
        }
    except Exception as e:
        logger.error(f"Failed to resume scheduler: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


