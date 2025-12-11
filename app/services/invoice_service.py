"""
Invoice Service - Business logic for invoice management.

Handles invoice CRUD, QuickBooks sync, and payment tracking.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
from decimal import Decimal
import logging

from app.db.models import Invoice, Project

logger = logging.getLogger(__name__)


class InvoiceService:
    """Service for managing invoices and QuickBooks sync."""
    
    @staticmethod
    async def get_invoices(
        db: AsyncSession,
        project_id: Optional[str] = None,
        client_id: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Invoice]:
        """
        Get invoices with optional filtering.
        
        Args:
            db: Database session
            project_id: Filter by project UUID
            client_id: Filter by client UUID
            status: Filter by invoice status
            skip: Number of records to skip
            limit: Maximum records to return
            
        Returns:
            List of Invoice objects
        """
        query = select(Invoice).order_by(Invoice.created_at.desc())
        
        if project_id:
            query = query.where(Invoice.project_id == project_id)
        if client_id:
            query = query.where(Invoice.client_id == client_id)
        if status:
            query = query.where(Invoice.status == status)
            
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        invoices = result.scalars().all()
        
        logger.info(f"Retrieved {len(invoices)} invoices")
        return invoices
    
    @staticmethod
    async def get_by_id(db: AsyncSession, invoice_id: str) -> Optional[Invoice]:
        """Get invoice by UUID."""
        result = await db.execute(
            select(Invoice).where(Invoice.invoice_id == invoice_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_business_id(db: AsyncSession, business_id: str) -> Optional[Invoice]:
        """Get invoice by business ID (e.g., INV-00001)."""
        result = await db.execute(
            select(Invoice).where(Invoice.business_id == business_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def create_invoice(
        db: AsyncSession,
        project_id: str,
        client_id: str,
        invoice_number: str,
        total_amount: Decimal,
        line_items: Optional[List[Dict[str, Any]]] = None,
        status: str = "Draft",
        due_date: Optional[datetime] = None,
        extra: Optional[Dict[str, Any]] = None
    ) -> Invoice:
        """
        Create a new invoice.
        
        Args:
            db: Database session
            project_id: Project UUID
            client_id: Client UUID
            invoice_number: External invoice number
            total_amount: Total invoice amount
            line_items: List of line items with description, quantity, rate
            status: Initial status (default: "Draft")
            due_date: When payment is due
            extra: Additional metadata
            
        Returns:
            Created Invoice object with auto-generated business_id
        """
        # Verify project exists
        project_result = await db.execute(
            select(Project).where(Project.project_id == project_id)
        )
        project = project_result.scalar_one_or_none()
        if not project:
            raise ValueError(f"Project not found: {project_id}")
        
        invoice = Invoice(
            project_id=project_id,
            client_id=client_id,
            invoice_number=invoice_number,
            total_amount=total_amount,
            amount_paid=Decimal("0.00"),
            balance_due=total_amount,
            line_items=line_items or [],
            status=status,
            due_date=due_date,
            sync_status="pending",
            extra=extra or {}
        )
        
        db.add(invoice)
        await db.flush()
        await db.refresh(invoice)
        
        logger.info(f"Created invoice {invoice.business_id} for project {project.business_id}")
        return invoice
    
    @staticmethod
    async def update_status(
        db: AsyncSession,
        invoice_id: str,
        new_status: str
    ) -> Optional[Invoice]:
        """
        Update invoice status.
        
        Args:
            db: Database session
            invoice_id: Invoice UUID
            new_status: New status value
            
        Returns:
            Updated Invoice object or None if not found
        """
        invoice = await InvoiceService.get_by_id(db, invoice_id)
        if not invoice:
            return None
        
        old_status = invoice.status
        invoice.status = new_status
        invoice.updated_at = datetime.now(timezone.utc)
        
        await db.flush()
        await db.refresh(invoice)
        
        logger.info(f"Updated invoice {invoice.business_id} status: {old_status} → {new_status}")
        return invoice
    
    @staticmethod
    async def record_payment(
        db: AsyncSession,
        invoice_id: str,
        payment_amount: Decimal
    ) -> Optional[Invoice]:
        """
        Record a payment against an invoice.
        
        Args:
            db: Database session
            invoice_id: Invoice UUID
            payment_amount: Amount paid
            
        Returns:
            Updated Invoice object or None if not found
        """
        invoice = await InvoiceService.get_by_id(db, invoice_id)
        if not invoice:
            return None
        
        invoice.amount_paid += payment_amount
        invoice.balance_due = invoice.total_amount - invoice.amount_paid
        
        # Update status based on balance
        if invoice.balance_due <= Decimal("0.00"):
            invoice.status = "Paid"
        elif invoice.amount_paid > Decimal("0.00"):
            invoice.status = "Partially Paid"
        
        invoice.updated_at = datetime.now(timezone.utc)
        
        await db.flush()
        await db.refresh(invoice)
        
        logger.info(f"Recorded ${payment_amount} payment on invoice {invoice.business_id}")
        return invoice
    
    @staticmethod
    async def sync_to_quickbooks(
        db: AsyncSession,
        invoice_id: str
    ) -> Dict[str, Any]:
        """
        Sync invoice to QuickBooks (stub for Phase B).
        
        Args:
            db: Database session
            invoice_id: Invoice UUID
            
        Returns:
            Sync result (stub implementation)
        """
        invoice = await InvoiceService.get_by_id(db, invoice_id)
        if not invoice:
            raise ValueError(f"Invoice not found: {invoice_id}")
        
        # TODO: Implement actual QB sync logic in Phase B
        logger.info(f"QB sync stub called for invoice {invoice.business_id}")
        
        invoice.sync_status = "pending"
        invoice.last_sync_attempt = datetime.now(timezone.utc)
        await db.flush()
        
        return {
            "status": "stub",
            "message": "QuickBooks sync coming in Phase B",
            "invoice_id": invoice_id,
            "business_id": invoice.business_id
        }


# Global service instance
invoice_service = InvoiceService()
