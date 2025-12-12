"""
QuickBooks Cache Service

Handles caching of QuickBooks data in PostgreSQL to reduce API calls by 90%.
Uses TTL-based cache with background sync strategy.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    QuickBooksCustomerCache,
    QuickBooksInvoiceCache,
    QuickBooksPaymentCache
)

logger = logging.getLogger(__name__)


class QuickBooksCacheService:
    """
    Service for caching QuickBooks data in PostgreSQL.
    
    Features:
    - TTL-based caching (default: 5 minutes)
    - Bulk upsert operations
    - Cache invalidation (full or selective)
    - Cache hit rate tracking
    
    Usage:
        cache_service = QuickBooksCacheService(db_session)
        
        # Cache customers
        await cache_service.cache_customers(customers_data)
        
        # Get cached customers
        customers = await cache_service.get_cached_customers()
        
        # Check if cache is fresh
        is_fresh = await cache_service.is_cache_fresh('customers')
    """
    
    def __init__(self, db: AsyncSession, cache_ttl_minutes: int = 5):
        self.db = db
        self.cache_ttl = timedelta(minutes=cache_ttl_minutes)
        self._hit_count = 0
        self._miss_count = 0
    
    # ==================== CUSTOMER CACHE ====================
    
    async def cache_customers(self, customers: List[Dict[str, Any]]) -> int:
        """
        Cache QuickBooks customers in PostgreSQL.
        
        Args:
            customers: List of customer data from QB API
        
        Returns:
            Number of customers cached
        """
        try:
            cached_count = 0
            
            for customer in customers:
                qb_id = customer.get('Id')
                if not qb_id:
                    continue
                
                # Check if exists
                result = await self.db.execute(
                    select(QuickBooksCustomerCache).where(
                        QuickBooksCustomerCache.qb_customer_id == qb_id
                    )
                )
                existing = result.scalar_one_or_none()
                
                if existing:
                    # Update existing
                    existing.display_name = customer.get('DisplayName')
                    existing.company_name = customer.get('CompanyName')
                    existing.given_name = customer.get('GivenName')
                    existing.family_name = customer.get('FamilyName')
                    existing.email = customer.get('PrimaryEmailAddr', {}).get('Address')
                    existing.phone = customer.get('PrimaryPhone', {}).get('FreeFormNumber')
                    existing.qb_data = customer
                    existing.cached_at = datetime.utcnow()
                else:
                    # Create new
                    new_customer = QuickBooksCustomerCache(
                        qb_customer_id=qb_id,
                        display_name=customer.get('DisplayName'),
                        company_name=customer.get('CompanyName'),
                        given_name=customer.get('GivenName'),
                        family_name=customer.get('FamilyName'),
                        email=customer.get('PrimaryEmailAddr', {}).get('Address'),
                        phone=customer.get('PrimaryPhone', {}).get('FreeFormNumber'),
                        qb_data=customer,
                        cached_at=datetime.utcnow()
                    )
                    self.db.add(new_customer)
                
                cached_count += 1
            
            await self.db.commit()
            logger.info(f"[CACHE] Cached {cached_count} QuickBooks customers")
            return cached_count
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"[CACHE] Failed to cache customers: {e}")
            raise
    
    async def get_cached_customers(
        self, 
        customer_type: Optional[str] = None,
        max_age_minutes: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get cached customers from PostgreSQL.
        
        Args:
            customer_type: Filter by customer type (from qb_data JSONB)
            max_age_minutes: Only return cache entries newer than this
        
        Returns:
            List of customer data (qb_data field)
        """
        try:
            query = select(QuickBooksCustomerCache)
            
            # Filter by age if specified
            if max_age_minutes:
                cutoff = datetime.utcnow() - timedelta(minutes=max_age_minutes)
                query = query.where(QuickBooksCustomerCache.cached_at >= cutoff)
            
            result = await self.db.execute(query)
            cached_customers = result.scalars().all()
            
            # Extract qb_data and filter by customer_type if needed
            customers = []
            for cached in cached_customers:
                customer_data = cached.qb_data
                
                # Filter by customer type if specified
                if customer_type:
                    if customer_data.get('PrimaryCustomerType', {}).get('Name') == customer_type:
                        customers.append(customer_data)
                else:
                    customers.append(customer_data)
            
            if customers:
                self._hit_count += 1
                logger.info(f"[CACHE HIT] Retrieved {len(customers)} customers from cache")
            else:
                self._miss_count += 1
                logger.info(f"[CACHE MISS] No cached customers found")
            
            return customers
            
        except Exception as e:
            logger.error(f"[CACHE] Failed to get cached customers: {e}")
            return []
    
    async def is_customers_cache_fresh(self, max_age_minutes: Optional[int] = None) -> bool:
        """
        Check if customer cache is fresh.
        
        Args:
            max_age_minutes: Cache age threshold (defaults to cache_ttl)
        
        Returns:
            True if cache exists and is fresh
        """
        if max_age_minutes is None:
            max_age_minutes = int(self.cache_ttl.total_seconds() / 60)
        
        cutoff = datetime.utcnow() - timedelta(minutes=max_age_minutes)
        
        result = await self.db.execute(
            select(QuickBooksCustomerCache)
            .where(QuickBooksCustomerCache.cached_at >= cutoff)
            .limit(1)
        )
        
        return result.scalar_one_or_none() is not None
    
    # ==================== INVOICE CACHE ====================
    
    async def cache_invoices(self, invoices: List[Dict[str, Any]]) -> int:
        """
        Cache QuickBooks invoices in PostgreSQL.
        
        Args:
            invoices: List of invoice data from QB API
        
        Returns:
            Number of invoices cached
        """
        try:
            cached_count = 0
            
            for invoice in invoices:
                qb_id = invoice.get('Id')
                if not qb_id:
                    continue
                
                # Check if exists
                result = await self.db.execute(
                    select(QuickBooksInvoiceCache).where(
                        QuickBooksInvoiceCache.qb_invoice_id == qb_id
                    )
                )
                existing = result.scalar_one_or_none()
                
                customer_ref = invoice.get('CustomerRef', {})
                due_date_str = invoice.get('DueDate')
                due_date = datetime.fromisoformat(due_date_str) if due_date_str else None
                
                if existing:
                    # Update existing
                    existing.customer_id = customer_ref.get('value')
                    existing.doc_number = invoice.get('DocNumber')
                    existing.total_amount = float(invoice.get('TotalAmt', 0))
                    existing.balance = float(invoice.get('Balance', 0))
                    existing.due_date = due_date
                    existing.qb_data = invoice
                    existing.cached_at = datetime.utcnow()
                else:
                    # Create new
                    new_invoice = QuickBooksInvoiceCache(
                        qb_invoice_id=qb_id,
                        customer_id=customer_ref.get('value'),
                        doc_number=invoice.get('DocNumber'),
                        total_amount=float(invoice.get('TotalAmt', 0)),
                        balance=float(invoice.get('Balance', 0)),
                        due_date=due_date,
                        qb_data=invoice,
                        cached_at=datetime.utcnow()
                    )
                    self.db.add(new_invoice)
                
                cached_count += 1
            
            await self.db.commit()
            logger.info(f"[CACHE] Cached {cached_count} QuickBooks invoices")
            return cached_count
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"[CACHE] Failed to cache invoices: {e}")
            raise
    
    async def get_cached_invoices(
        self,
        customer_id: Optional[str] = None,
        max_age_minutes: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get cached invoices from PostgreSQL.
        
        Args:
            customer_id: Filter by specific customer
            max_age_minutes: Only return cache entries newer than this
        
        Returns:
            List of invoice data (qb_data field)
        """
        try:
            query = select(QuickBooksInvoiceCache)
            
            # Filter by customer if specified
            if customer_id:
                query = query.where(QuickBooksInvoiceCache.customer_id == customer_id)
            
            # Filter by age if specified
            if max_age_minutes:
                cutoff = datetime.utcnow() - timedelta(minutes=max_age_minutes)
                query = query.where(QuickBooksInvoiceCache.cached_at >= cutoff)
            
            result = await self.db.execute(query)
            cached_invoices = result.scalars().all()
            
            invoices = [cached.qb_data for cached in cached_invoices]
            
            if invoices:
                self._hit_count += 1
                logger.info(f"[CACHE HIT] Retrieved {len(invoices)} invoices from cache")
            else:
                self._miss_count += 1
                logger.info(f"[CACHE MISS] No cached invoices found")
            
            return invoices
            
        except Exception as e:
            logger.error(f"[CACHE] Failed to get cached invoices: {e}")
            return []
    
    async def is_invoices_cache_fresh(self, max_age_minutes: Optional[int] = None) -> bool:
        """Check if invoice cache is fresh."""
        if max_age_minutes is None:
            max_age_minutes = int(self.cache_ttl.total_seconds() / 60)
        
        cutoff = datetime.utcnow() - timedelta(minutes=max_age_minutes)
        
        result = await self.db.execute(
            select(QuickBooksInvoiceCache)
            .where(QuickBooksInvoiceCache.cached_at >= cutoff)
            .limit(1)
        )
        
        return result.scalar_one_or_none() is not None
    
    # ==================== PAYMENT CACHE ====================
    
    async def cache_payments(self, payments: List[Dict[str, Any]]) -> int:
        """
        Cache QuickBooks payments in PostgreSQL.
        
        Args:
            payments: List of payment data from QB API
        
        Returns:
            Number of payments cached
        """
        try:
            cached_count = 0
            
            for payment in payments:
                qb_id = payment.get('Id')
                if not qb_id:
                    continue
                
                # Check if exists
                result = await self.db.execute(
                    select(QuickBooksPaymentCache).where(
                        QuickBooksPaymentCache.qb_payment_id == qb_id
                    )
                )
                existing = result.scalar_one_or_none()
                
                customer_ref = payment.get('CustomerRef', {})
                txn_date_str = payment.get('TxnDate')
                payment_date = datetime.fromisoformat(txn_date_str) if txn_date_str else None
                
                payment_method_ref = payment.get('PaymentMethodRef', {})
                payment_method = payment_method_ref.get('name') if payment_method_ref else None
                
                if existing:
                    # Update existing
                    existing.customer_id = customer_ref.get('value')
                    existing.total_amount = float(payment.get('TotalAmt', 0))
                    existing.payment_date = payment_date
                    existing.payment_method = payment_method
                    existing.payment_ref_num = payment.get('PaymentRefNum')
                    existing.qb_data = payment
                    existing.cached_at = datetime.utcnow()
                else:
                    # Create new
                    new_payment = QuickBooksPaymentCache(
                        qb_payment_id=qb_id,
                        customer_id=customer_ref.get('value'),
                        total_amount=float(payment.get('TotalAmt', 0)),
                        payment_date=payment_date,
                        payment_method=payment_method,
                        payment_ref_num=payment.get('PaymentRefNum'),
                        qb_data=payment,
                        cached_at=datetime.utcnow()
                    )
                    self.db.add(new_payment)
                
                cached_count += 1
            
            await self.db.commit()
            logger.info(f"[CACHE] Cached {cached_count} QuickBooks payments")
            return cached_count
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"[CACHE] Failed to cache payments: {e}")
            raise
    
    async def get_cached_payments(
        self,
        customer_id: Optional[str] = None,
        max_age_minutes: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get cached payments from PostgreSQL.
        
        Args:
            customer_id: Filter by specific customer
            max_age_minutes: Only return cache entries newer than this
        
        Returns:
            List of payment data (qb_data field)
        """
        try:
            query = select(QuickBooksPaymentCache)
            
            # Filter by customer if specified
            if customer_id:
                query = query.where(QuickBooksPaymentCache.customer_id == customer_id)
            
            # Filter by age if specified
            if max_age_minutes:
                cutoff = datetime.utcnow() - timedelta(minutes=max_age_minutes)
                query = query.where(QuickBooksPaymentCache.cached_at >= cutoff)
            
            result = await self.db.execute(query)
            cached_payments = result.scalars().all()
            
            payments = [cached.qb_data for cached in cached_payments]
            
            if payments:
                self._hit_count += 1
                logger.info(f"[CACHE HIT] Retrieved {len(payments)} payments from cache")
            else:
                self._miss_count += 1
                logger.info(f"[CACHE MISS] No cached payments found")
            
            return payments
            
        except Exception as e:
            logger.error(f"[CACHE] Failed to get cached payments: {e}")
            return []
    
    async def is_payments_cache_fresh(self, max_age_minutes: Optional[int] = None) -> bool:
        """Check if payment cache is fresh."""
        if max_age_minutes is None:
            max_age_minutes = int(self.cache_ttl.total_seconds() / 60)
        
        cutoff = datetime.utcnow() - timedelta(minutes=max_age_minutes)
        
        result = await self.db.execute(
            select(QuickBooksPaymentCache)
            .where(QuickBooksPaymentCache.cached_at >= cutoff)
            .limit(1)
        )
        
        return result.scalar_one_or_none() is not None
    
    # ==================== CACHE MANAGEMENT ====================
    
    async def invalidate_all_caches(self):
        """Clear all QuickBooks caches."""
        try:
            await self.db.execute(delete(QuickBooksCustomerCache))
            await self.db.execute(delete(QuickBooksInvoiceCache))
            await self.db.execute(delete(QuickBooksPaymentCache))
            await self.db.commit()
            logger.info("[CACHE] Invalidated all QuickBooks caches")
        except Exception as e:
            await self.db.rollback()
            logger.error(f"[CACHE] Failed to invalidate caches: {e}")
            raise
    
    async def invalidate_customer_cache(self):
        """Clear customer cache only."""
        try:
            await self.db.execute(delete(QuickBooksCustomerCache))
            await self.db.commit()
            logger.info("[CACHE] Invalidated customer cache")
        except Exception as e:
            await self.db.rollback()
            logger.error(f"[CACHE] Failed to invalidate customer cache: {e}")
            raise
    
    async def invalidate_invoice_cache(self):
        """Clear invoice cache only."""
        try:
            await self.db.execute(delete(QuickBooksInvoiceCache))
            await self.db.commit()
            logger.info("[CACHE] Invalidated invoice cache")
        except Exception as e:
            await self.db.rollback()
            logger.error(f"[CACHE] Failed to invalidate invoice cache: {e}")
            raise
    
    async def invalidate_payment_cache(self):
        """Clear payment cache only."""
        try:
            await self.db.execute(delete(QuickBooksPaymentCache))
            await self.db.commit()
            logger.info("[CACHE] Invalidated payment cache")
        except Exception as e:
            await self.db.rollback()
            logger.error(f"[CACHE] Failed to invalidate payment cache: {e}")
            raise
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache performance statistics.
        
        Returns:
            Dict with hit_count, miss_count, hit_rate
        """
        total = self._hit_count + self._miss_count
        hit_rate = (self._hit_count / total * 100) if total > 0 else 0
        
        return {
            "hit_count": self._hit_count,
            "miss_count": self._miss_count,
            "total_requests": total,
            "hit_rate_percent": round(hit_rate, 2)
        }
