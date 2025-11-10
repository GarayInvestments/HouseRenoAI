from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict, Any, Optional
import logging
import uuid
from datetime import datetime

import app.services.google_service as google_service_module
import app.services.quickbooks_service as quickbooks_service_module
from app.routes.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()

def get_google_service():
    """Helper function to get Google service with proper error handling"""
    if not google_service_module.google_service:
        raise HTTPException(status_code=503, detail="Google service not initialized")
    return google_service_module.google_service

def get_quickbooks_service():
    """Helper function to get QuickBooks service with proper error handling"""
    if not quickbooks_service_module.quickbooks_service:
        raise HTTPException(status_code=503, detail="QuickBooks service not initialized")
    return quickbooks_service_module.quickbooks_service

@router.get("/")
async def get_all_payments(current_user: dict = Depends(get_current_user)):
    """
    Get all payments from Google Sheets.
    
    Returns list of payment records with client and invoice information.
    """
    try:
        google_service = get_google_service()
        payments = await google_service.get_sheet_data('Payments')
        logger.info(f"Retrieved {len(payments)} payments for user {current_user.get('email')}")
        return {
            "status": "success",
            "count": len(payments),
            "payments": payments
        }
    except Exception as e:
        logger.error(f"Failed to get payments: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve payments: {str(e)}")

@router.get("/{payment_id}")
async def get_payment(payment_id: str, current_user: dict = Depends(get_current_user)):
    """
    Get a specific payment by Payment ID.
    
    Args:
        payment_id: The Payment ID to retrieve
    
    Returns:
        Payment record with details
    """
    try:
        google_service = get_google_service()
        payments = await google_service.get_sheet_data('Payments')
        
        payment = next((p for p in payments if p.get('Payment ID') == payment_id), None)
        if not payment:
            raise HTTPException(status_code=404, detail=f"Payment {payment_id} not found")
        
        logger.info(f"Retrieved payment {payment_id} for user {current_user.get('email')}")
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
async def get_client_payments(client_id: str, current_user: dict = Depends(get_current_user)):
    """
    Get all payments for a specific client.
    
    Args:
        client_id: The Client ID to get payments for
    
    Returns:
        List of payment records for the client
    """
    try:
        google_service = get_google_service()
        payments = await google_service.get_sheet_data('Payments')
        
        client_payments = [p for p in payments if p.get('Client ID') == client_id]
        
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
    current_user: dict = Depends(get_current_user)
):
    """
    Sync QuickBooks payments to Google Sheets.
    
    Args:
        days_back: How many days back to sync payments (default 90)
    
    Returns:
        Sync summary with counts of new/updated payments
    """
    try:
        google_service = get_google_service()
        qb_service = get_quickbooks_service()
        
        logger.info(f"Starting payment sync (days_back={days_back}) by user {current_user.get('email')}")
        
        result = await qb_service.sync_payments_to_sheets(google_service, days_back)
        
        logger.info(f"Payment sync complete: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Payment sync failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Payment sync failed: {str(e)}")

@router.post("/")
async def record_payment(
    payment_data: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """
    Record a manual payment (non-QuickBooks).
    
    Request body:
        {
            "client_id": "abc12345",
            "amount": 4000,
            "payment_date": "2025-11-08",  # optional, defaults to today
            "payment_method": "Zelle",     # required
            "status": "Completed",         # optional, defaults to "Completed"
            "invoice_id": "INV-001",       # optional
            "project_id": "P-001",         # optional
            "transaction_id": "zelle-123", # optional
            "notes": "Payment received"    # optional
        }
    
    Returns:
        Created payment record
    """
    try:
        google_service = get_google_service()
        
        # Validate required fields
        if not payment_data.get('client_id'):
            raise HTTPException(status_code=400, detail="client_id is required")
        if not payment_data.get('amount'):
            raise HTTPException(status_code=400, detail="amount is required")
        if not payment_data.get('payment_method'):
            raise HTTPException(status_code=400, detail="payment_method is required")
        
        # Generate Payment ID
        payment_id = f"PAY-{uuid.uuid4().hex[:8]}"
        
        # Build payment record
        payment = {
            'Payment ID': payment_id,
            'Invoice ID': payment_data.get('invoice_id', ''),
            'Project ID': payment_data.get('project_id', ''),
            'Client ID': payment_data.get('client_id', ''),
            'Amount': payment_data.get('amount', 0),
            'Payment Date': payment_data.get('payment_date', datetime.now().strftime('%Y-%m-%d')),
            'Payment Method': payment_data.get('payment_method', 'Other'),
            'Status': payment_data.get('status', 'Completed'),
            'QB Payment ID': '',  # Manual entry - no QB ID
            'Transaction ID': payment_data.get('transaction_id', ''),
            'Notes': payment_data.get('notes', f'Manual entry by {current_user.get("email")}')
        }
        
        # Validate payment method
        valid_methods = ['Zelle', 'Check', 'Cash', 'Credit Card', 'ACH', 'Other']
        if payment['Payment Method'] not in valid_methods:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid payment_method. Must be one of: {', '.join(valid_methods)}"
            )
        
        # Validate status
        valid_statuses = ['Pending', 'Completed', 'Failed', 'Refunded']
        if payment['Status'] not in valid_statuses:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            )
        
        # Append to Payments sheet
        await google_service.append_row('Payments', list(payment.values()))
        
        logger.info(f"Recorded manual payment: {payment_id} by user {current_user.get('email')}")
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
