"""
API routes for invoice management.
"""

from fastapi import APIRouter, HTTPException, Query, status
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel
import logging

from app.services.db_service import db_service

logger = logging.getLogger(__name__)
router = APIRouter()


# ==================== REQUEST/RESPONSE MODELS ====================

class InvoiceLineItem(BaseModel):
    description: str
    quantity: float
    rate: float
    amount: float


class InvoiceCreate(BaseModel):
    """Request model for creating an invoice."""
    project_id: str
    client_id: Optional[str] = None
    invoice_number: Optional[str] = None
    invoice_date: datetime
    due_date: datetime
    line_items: List[InvoiceLineItem]
    tax_amount: Optional[float] = 0
    notes: Optional[str] = None
    status: Optional[str] = "Draft"


class InvoiceUpdate(BaseModel):
    """Request model for updating an invoice."""
    invoice_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    status: Optional[str] = None
    line_items: Optional[List[InvoiceLineItem]] = None
    tax_amount: Optional[float] = None
    notes: Optional[str] = None


# ==================== ROUTES ====================

@router.get("/")
async def get_all_invoices():
    """Get all invoices with client and permit information"""
    try:
        invoices = await db_service.get_invoices_with_relations()
        logger.info(f"Retrieved {len(invoices)} invoices from database")
        return invoices
    except Exception as e:
        logger.error(f"Failed to get invoices: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{invoice_id}")
async def get_invoice(invoice_id: str):
    """Get a specific invoice by ID"""
    try:
        invoice = await db_service.get_invoice_by_id(invoice_id)
        if not invoice:
            raise HTTPException(status_code=404, detail=f"Invoice {invoice_id} not found")
        return invoice
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get invoice {invoice_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_invoice(invoice_data: InvoiceCreate):
    """Create a new invoice"""
    try:
        invoice_dict = invoice_data.model_dump(exclude_none=True)
        
        # Calculate totals
        subtotal = sum(item.amount for item in invoice_data.line_items)
        total = subtotal + (invoice_data.tax_amount or 0)
        
        invoice_dict['subtotal'] = subtotal
        invoice_dict['total_amount'] = total
        invoice_dict['balance_due'] = total
        invoice_dict['amount_paid'] = 0
        
        new_invoice = await db_service.create_invoice(invoice_dict)
        return new_invoice
    except Exception as e:
        logger.error(f"Failed to create invoice: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{invoice_id}")
async def update_invoice(invoice_id: str, invoice_data: InvoiceUpdate):
    """Update an existing invoice"""
    try:
        update_dict = invoice_data.model_dump(exclude_none=True)
        
        if not update_dict:
            raise HTTPException(status_code=400, detail="No updates provided")
        
        # Recalculate totals if line items changed
        if 'line_items' in update_dict:
            subtotal = sum(item['amount'] for item in update_dict['line_items'])
            tax = update_dict.get('tax_amount', 0)
            update_dict['subtotal'] = subtotal
            update_dict['total_amount'] = subtotal + tax
        
        updated_invoice = await db_service.update_invoice(invoice_id, update_dict)
        return updated_invoice
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to update invoice {invoice_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{invoice_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_invoice(invoice_id: str):
    """Delete an invoice"""
    try:
        deleted = await db_service.delete_invoice(invoice_id)
        if not deleted:
            raise HTTPException(status_code=404, detail=f"Invoice {invoice_id} not found")
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete invoice {invoice_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/project/{project_id}")
async def get_invoices_by_project(project_id: str):
    """Get all invoices for a specific project"""
    try:
        invoices = await db_service.get_invoices_by_project(project_id)
        return invoices
    except Exception as e:
        logger.error(f"Failed to get invoices for project {project_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
