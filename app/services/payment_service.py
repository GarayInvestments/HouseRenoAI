"""
Payment Service - Business logic for payment management.

Handles payment recording, invoice application, and QuickBooks sync.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
from decimal import Decimal
import logging

from app.db.models import Payment, Invoice

logger = logging.getLogger(__name__)


class PaymentService:
    """Service for managing payments and invoice applications."""
    
    @staticmethod
    async def get_payments(
        db: AsyncSession,
        invoice_id: Optional[str] = None,
        payment_method: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Payment]:
        """
        Get payments with optional filtering.
        
        Args:
            db: Database session
            invoice_id: Filter by invoice UUID
            payment_method: Filter by payment method
            skip: Number of records to skip
            limit: Maximum records to return
            
        Returns:
            List of Payment objects
        """
        query = select(Payment).order_by(Payment.payment_date.desc())
        
        if invoice_id:
            query = query.where(Payment.invoice_id == invoice_id)
        if payment_method:
            query = query.where(Payment.payment_method == payment_method)
            
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        payments = result.scalars().all()
        
        logger.info(f"Retrieved {len(payments)} payments")
        return payments
    
    @staticmethod
    async def get_by_id(db: AsyncSession, payment_id: str) -> Optional[Payment]:
        """Get payment by UUID."""
        result = await db.execute(
            select(Payment).where(Payment.payment_id == payment_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_business_id(db: AsyncSession, business_id: str) -> Optional[Payment]:
        """Get payment by business ID (e.g., PAY-00001)."""
        result = await db.execute(
            select(Payment).where(Payment.business_id == business_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def record_payment(
        db: AsyncSession,
        invoice_id: str,
        amount: Decimal,
        payment_date: datetime,
        payment_method: str,
        reference_number: Optional[str] = None,
        notes: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None
    ) -> Payment:
        """
        Record a new payment.
        
        Args:
            db: Database session
            invoice_id: Invoice UUID to apply payment to
            amount: Payment amount
            payment_date: When payment was received
            payment_method: Method (e.g., "Check", "Credit Card", "ACH")
            reference_number: Check number, transaction ID, etc.
            notes: Additional notes
            extra: Additional metadata
            
        Returns:
            Created Payment object with auto-generated business_id
        """
        # Verify invoice exists
        invoice_result = await db.execute(
            select(Invoice).where(Invoice.invoice_id == invoice_id)
        )
        invoice = invoice_result.scalar_one_or_none()
        if not invoice:
            raise ValueError(f"Invoice not found: {invoice_id}")
        
        payment = Payment(
            invoice_id=invoice_id,
            amount=amount,
            payment_date=payment_date,
            payment_method=payment_method,
            reference_number=reference_number,
            notes=notes,
            sync_status="pending",
            extra=extra or {}
        )
        
        db.add(payment)
        await db.flush()
        await db.refresh(payment)
        
        logger.info(f"Recorded payment {payment.business_id} for invoice {invoice.business_id}")
        return payment
    
    @staticmethod
    async def apply_to_invoice(
        db: AsyncSession,
        payment_id: str,
        invoice_id: str
    ) -> Dict[str, Any]:
        """
        Apply payment to invoice and update balances.
        
        Args:
            db: Database session
            payment_id: Payment UUID
            invoice_id: Invoice UUID
            
        Returns:
            Result with updated invoice and payment info
        """
        payment = await PaymentService.get_by_id(db, payment_id)
        if not payment:
            raise ValueError(f"Payment not found: {payment_id}")
        
        invoice = await db.execute(
            select(Invoice).where(Invoice.invoice_id == invoice_id)
        )
        invoice = invoice.scalar_one_or_none()
        if not invoice:
            raise ValueError(f"Invoice not found: {invoice_id}")
        
        # Update invoice balances
        invoice.amount_paid += payment.amount
        invoice.balance_due = invoice.total_amount - invoice.amount_paid
        
        # Update invoice status
        if invoice.balance_due <= Decimal("0.00"):
            invoice.status = "Paid"
        elif invoice.amount_paid > Decimal("0.00"):
            invoice.status = "Partially Paid"
        
        invoice.updated_at = datetime.now(timezone.utc)
        
        # Update payment reference
        payment.invoice_id = invoice_id
        payment.updated_at = datetime.now(timezone.utc)
        
        await db.flush()
        await db.refresh(payment)
        await db.refresh(invoice)
        
        logger.info(f"Applied payment {payment.business_id} to invoice {invoice.business_id}")
        
        return {
            "payment_id": payment.payment_id,
            "payment_business_id": payment.business_id,
            "invoice_id": invoice.invoice_id,
            "invoice_business_id": invoice.business_id,
            "amount_applied": float(payment.amount),
            "new_balance": float(invoice.balance_due),
            "invoice_status": invoice.status
        }
    
    @staticmethod
    async def sync_to_quickbooks(
        db: AsyncSession,
        payment_id: str
    ) -> Dict[str, Any]:
        """
        Sync payment to QuickBooks (stub for Phase B).
        
        Args:
            db: Database session
            payment_id: Payment UUID
            
        Returns:
            Sync result (stub implementation)
        """
        payment = await PaymentService.get_by_id(db, payment_id)
        if not payment:
            raise ValueError(f"Payment not found: {payment_id}")
        
        # TODO: Implement actual QB sync logic in Phase B
        logger.info(f"QB sync stub called for payment {payment.business_id}")
        
        payment.sync_status = "pending"
        payment.last_sync_attempt = datetime.now(timezone.utc)
        await db.flush()
        
        return {
            "status": "stub",
            "message": "QuickBooks sync coming in Phase B",
            "payment_id": payment_id,
            "business_id": payment.business_id
        }


# Global service instance
payment_service = PaymentService()
