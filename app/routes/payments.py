from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict, Any, Optional
import logging
import uuid
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

import app.services.quickbooks_service as quickbooks_service_module
from app.routes.auth_supabase import get_current_user
from app.services.db_service import db_service
from app.db.session import get_db
from app.db.models import User

logger = logging.getLogger(__name__)
router = APIRouter()

def get_quickbooks_service():
    """Helper function to get QuickBooks service with proper error handling"""
    if not quickbooks_service_module.quickbooks_service:
        raise HTTPException(status_code=503, detail="QuickBooks service not initialized")
    return quickbooks_service_module.quickbooks_service

@router.get("/")
async def get_all_payments(current_user: User = Depends(get_current_user)):
    """
    Get all payments from database.
    
    Returns list of payment records with client and invoice information.
    """
    try:
        payments = await db_service.get_payments_data()
        logger.info(f"Retrieved {len(payments)} payments for user {current_user.email}")
        return {
            "status": "success",
            "count": len(payments),
            "payments": payments
        }
    except Exception as e:
        logger.error(f"Failed to get payments: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve payments: {str(e)}")

@router.get("/{payment_id}")
async def get_payment(payment_id: str, current_user: User = Depends(get_current_user)):
    """
    Get a specific payment by Payment ID (UUID or business ID like PAY-00001).
    
    Args:
        payment_id: The Payment ID to retrieve (UUID or business ID)
    
    Returns:
        Payment record with details
    """
    try:
        # Try business_id first (PAY-00001 format)
        payment = await db_service.get_payment_by_business_id(payment_id)
        
        if not payment:
            raise HTTPException(status_code=404, detail=f"Payment {payment_id} not found")
        
        logger.info(f"Retrieved payment {payment_id} for user {current_user.email}")
        return {
            "status": "success",
            "payment": payment
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get payment {payment_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve payment: {str(e)}")

@router.get("/client/{client_id}")
async def get_client_payments(client_id: str, current_user: User = Depends(get_current_user)):
    """
    Get all payments for a specific client.
    
    Args:
        client_id: The Client ID to get payments for
    
    Returns:
        List of payment records for the client
    """
    try:
        all_payments = await db_service.get_payments_data()
        client_payments = [p for p in all_payments if p.get('Client ID') == client_id]
        
        logger.info(f"Retrieved {len(client_payments)} payments for client {client_id}")
        return {
            "status": "success",
            "client_id": client_id,
            "count": len(client_payments),
            "payments": client_payments
        }
    except Exception as e:
        logger.error(f"Failed to get payments for client {client_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve client payments: {str(e)}")

@router.post("/sync")
async def sync_quickbooks_payments(
    days_back: int = Query(default=90, description="Number of days back to sync"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Sync QuickBooks payments to database.
    
    Args:
        days_back: How many days back to sync payments (default 90)
    
    Returns:
        Sync summary with counts of new/updated payments
    """
    try:
        qb_service = get_quickbooks_service()
        
        logger.info(f"Starting payment sync (days_back={days_back}) by user {current_user.email}")
        
        # TODO: Implement sync_payments_to_database method in quickbooks_service
        # For now, return not implemented
        raise HTTPException(
            status_code=501,
            detail="QuickBooks payment sync to database not yet implemented. Use manual payment recording."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Payment sync failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Payment sync failed: {str(e)}")

@router.post("/")
async def record_payment(
    payment_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Record a manual payment (non-QuickBooks).
    
    Request body:
        {
            "client_id": "abc12345",
            "amount": 4000,
            "payment_date": "2025-11-08",  # optional, defaults to today
            "payment_method": "Check",     # required: Check, Credit Card, Wire, Cash, ACH
            "status": "Cleared",           # optional, defaults to "Cleared"
            "invoice_id": "invoice-uuid",  # optional
            "project_id": "project-uuid",  # optional
            "check_number": "1234",        # optional
            "transaction_id": "txn-123",   # optional
            "notes": "Payment received"    # optional
        }
    
    Returns:
        Created payment record
    """
    try:
        # Validate required fields
        if not payment_data.get('client_id'):
            raise HTTPException(status_code=400, detail="client_id is required")
        if not payment_data.get('amount'):
            raise HTTPException(status_code=400, detail="amount is required")
        if not payment_data.get('payment_method'):
            raise HTTPException(status_code=400, detail="payment_method is required")
        
        # Validate payment method
        valid_methods = ['Check', 'Credit Card', 'Wire', 'Cash', 'ACH']
        if payment_data.get('payment_method') not in valid_methods:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid payment_method. Must be one of: {', '.join(valid_methods)}"
            )
        
        # Validate status
        valid_statuses = ['Pending', 'Cleared', 'Failed', 'Refunded']
        status = payment_data.get('status', 'Cleared')
        if status not in valid_statuses:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            )
        
        # Create payment in database
        payment = await db_service.create_payment(
            client_id=payment_data['client_id'],
            amount=float(payment_data['amount']),
            payment_date=payment_data.get('payment_date'),
            payment_method=payment_data['payment_method'],
            status=status,
            invoice_id=payment_data.get('invoice_id'),
            project_id=payment_data.get('project_id'),
            check_number=payment_data.get('check_number'),
            transaction_id=payment_data.get('transaction_id'),
            notes=payment_data.get('notes', f'Manual entry by {current_user.email}')
        )
        
        logger.info(f"Recorded manual payment: {payment.get('Business ID')} by user {current_user.email}")
        return {
            "status": "success",
            "message": "Payment recorded successfully",
            "payment": payment
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to record payment: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to record payment: {str(e)}")

@router.get("/by-business-id/{business_id}")
async def get_payment_by_business_id(business_id: str):
    """
    Get a specific payment by business ID (e.g., PAY-00001)
    """
    try:
        from app.services.db_service import db_service
        
        payment = await db_service.get_payment_by_business_id(business_id)
        
        if not payment:
            raise HTTPException(status_code=404, detail=f"Payment with business ID {business_id} not found")
        
        return payment
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get payment by business ID {business_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve payment: {str(e)}")
