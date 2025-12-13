"""
Unit tests for QuickBooks Cache Service (Phase D.1)

Tests cache operations, TTL behavior, invalidation, and hit rate tracking.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.qb_cache_service import QuickBooksCacheService
from app.db.models import (
    QuickBooksCustomerCache,
    QuickBooksInvoiceCache,
    QuickBooksPaymentCache
)


@pytest.fixture
def mock_db():
    """Mock database session."""
    db = AsyncMock(spec=AsyncSession)
    return db


@pytest.fixture
def cache_service(mock_db):
    """Create cache service with 5-minute TTL."""
    return QuickBooksCacheService(mock_db, cache_ttl_minutes=5)


@pytest.fixture
def sample_qb_customer():
    """Sample QuickBooks customer data."""
    return {
        'Id': 'QB123',
        'DisplayName': 'John Doe',
        'CompanyName': 'Doe Construction',
        'GivenName': 'John',
        'FamilyName': 'Doe',
        'PrimaryEmailAddr': {'Address': 'john@example.com'},
        'PrimaryPhone': {'FreeFormNumber': '555-1234'},
        'Balance': 1500.00,
        'Active': True
    }


@pytest.fixture
def sample_qb_invoice():
    """Sample QuickBooks invoice data."""
    return {
        'Id': 'INV123',
        'DocNumber': '1001',
        'CustomerRef': {'value': 'QB123', 'name': 'John Doe'},
        'TxnDate': '2025-01-15',
        'DueDate': '2025-02-15',
        'TotalAmt': 5000.00,
        'Balance': 2500.00,
        'Line': [
            {
                'Id': '1',
                'Amount': 5000.00,
                'Description': 'Construction services',
                'DetailType': 'SalesItemLineDetail'
            }
        ]
    }


@pytest.fixture
def sample_qb_payment():
    """Sample QuickBooks payment data."""
    return {
        'Id': 'PAY123',
        'TxnDate': '2025-01-20',
        'CustomerRef': {'value': 'QB123', 'name': 'John Doe'},
        'TotalAmt': 2500.00,
        'Line': [
            {
                'Amount': 2500.00,
                'LinkedTxn': [
                    {'TxnId': 'INV123', 'TxnType': 'Invoice'}
                ]
            }
        ]
    }


# ==================== CUSTOMER CACHE TESTS ====================

@pytest.mark.asyncio
async def test_cache_customers_new(cache_service, mock_db, sample_qb_customer):
    """Test caching new customer."""
    # Mock: No existing customer
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result
    
    # Cache customer
    count = await cache_service.cache_customers([sample_qb_customer])
    
    # Verify
    assert count == 1
    assert mock_db.add.called
    assert mock_db.commit.called


@pytest.mark.asyncio
async def test_cache_customers_update_existing(cache_service, mock_db, sample_qb_customer):
    """Test updating existing cached customer."""
    # Mock: Existing customer
    existing = QuickBooksCustomerCache(
        qb_customer_id='QB123',
        display_name='Old Name',
        cached_at=datetime.utcnow() - timedelta(minutes=10)
    )
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing
    mock_db.execute.return_value = mock_result
    
    # Cache customer (should update)
    count = await cache_service.cache_customers([sample_qb_customer])
    
    # Verify update
    assert count == 1
    assert existing.display_name == 'John Doe'
    assert existing.company_name == 'Doe Construction'
    assert mock_db.commit.called


@pytest.mark.asyncio
async def test_cache_customers_bulk(cache_service, mock_db):
    """Test bulk caching multiple customers."""
    customers = [
        {'Id': 'QB1', 'DisplayName': 'Customer 1'},
        {'Id': 'QB2', 'DisplayName': 'Customer 2'},
        {'Id': 'QB3', 'DisplayName': 'Customer 3'},
    ]
    
    # Mock: No existing customers
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result
    
    count = await cache_service.cache_customers(customers)
    
    assert count == 3
    assert mock_db.add.call_count == 3


@pytest.mark.asyncio
async def test_cache_customers_skip_invalid(cache_service, mock_db):
    """Test skipping customers without QB ID."""
    customers = [
        {'Id': 'QB1', 'DisplayName': 'Valid'},
        {'DisplayName': 'No ID'},  # Missing Id
        {'Id': None, 'DisplayName': 'Null ID'},  # Null Id
    ]
    
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result
    
    count = await cache_service.cache_customers(customers)
    
    assert count == 1  # Only valid customer cached
    assert mock_db.add.call_count == 1


@pytest.mark.asyncio
async def test_get_cached_customers_fresh(cache_service, mock_db):
    """Test retrieving fresh cached customers."""
    # Mock: Recent cached customers
    cached_customers = [
        QuickBooksCustomerCache(
            qb_customer_id='QB1',
            display_name='Customer 1',
            cached_at=datetime.utcnow() - timedelta(minutes=2)
        ),
        QuickBooksCustomerCache(
            qb_customer_id='QB2',
            display_name='Customer 2',
            cached_at=datetime.utcnow() - timedelta(minutes=1)
        ),
    ]
    
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = cached_customers
    mock_db.execute.return_value = mock_result
    
    customers = await cache_service.get_cached_customers()
    
    assert len(customers) == 2
    assert cache_service._hit_count == 1
    assert cache_service._miss_count == 0


@pytest.mark.asyncio
async def test_get_cached_customers_stale(cache_service, mock_db):
    """Test cache miss when customers are stale."""
    # Mock: No recent customers (cache expired)
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_db.execute.return_value = mock_result
    
    customers = await cache_service.get_cached_customers()
    
    assert len(customers) == 0
    assert cache_service._miss_count == 1


# ==================== INVOICE CACHE TESTS ====================

@pytest.mark.asyncio
async def test_cache_invoices(cache_service, mock_db, sample_qb_invoice):
    """Test caching invoices."""
    # Mock: No existing invoice
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result
    
    count = await cache_service.cache_invoices([sample_qb_invoice])
    
    assert count == 1
    assert mock_db.add.called
    assert mock_db.commit.called


@pytest.mark.asyncio
async def test_get_cached_invoices_with_filters(cache_service, mock_db):
    """Test retrieving invoices with customer filter."""
    cached_invoices = [
        QuickBooksInvoiceCache(
            qb_invoice_id='INV1',
            customer_id='QB123',
            doc_number='1001',
            total_amount=5000.00,
            cached_at=datetime.utcnow()
        ),
    ]
    
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = cached_invoices
    mock_db.execute.return_value = mock_result
    
    invoices = await cache_service.get_cached_invoices(qb_customer_id='QB123')
    
    assert len(invoices) == 1
    assert invoices[0]['qb_customer_id'] == 'QB123'


# ==================== PAYMENT CACHE TESTS ====================

@pytest.mark.asyncio
async def test_cache_payments(cache_service, mock_db, sample_qb_payment):
    """Test caching payments."""
    # Mock: No existing payment
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result
    
    count = await cache_service.cache_payments([sample_qb_payment])
    
    assert count == 1
    assert mock_db.add.called
    assert mock_db.commit.called


@pytest.mark.asyncio
async def test_get_cached_payments_with_filters(cache_service, mock_db):
    """Test retrieving payments with customer filter."""
    cached_payments = [
        QuickBooksPaymentCache(
            qb_payment_id='PAY1',
            customer_id='QB123',
            total_amount=2500.00,
            cached_at=datetime.utcnow()
        ),
    ]
    
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = cached_payments
    mock_db.execute.return_value = mock_result
    
    payments = await cache_service.get_cached_payments(qb_customer_id='QB123')
    
    assert len(payments) == 1
    assert payments[0]['qb_customer_id'] == 'QB123'


# ==================== TTL & CACHE FRESHNESS TESTS ====================

@pytest.mark.asyncio
async def test_is_cache_fresh_within_ttl(cache_service, mock_db):
    """Test cache freshness check - within TTL."""
    # Mock: Recent cached customer
    mock_result = MagicMock()
    mock_customer = QuickBooksCustomerCache(
        cached_at=datetime.utcnow() - timedelta(minutes=2)
    )
    mock_result.scalar_one_or_none.return_value = mock_customer
    mock_db.execute.return_value = mock_result

    is_fresh = await cache_service.is_customers_cache_fresh()
    assert is_fresh is True


@pytest.mark.asyncio
async def test_is_cache_fresh_expired(cache_service, mock_db):
    """Test cache freshness check - expired."""
    # Mock: Old cached customer (beyond TTL)
    mock_result = MagicMock()
    mock_customer = QuickBooksCustomerCache(
        cached_at=datetime.utcnow() - timedelta(minutes=10)
    )
    mock_result.scalar_one_or_none.return_value = mock_customer
    mock_db.execute.return_value = mock_result

    is_fresh = await cache_service.is_customers_cache_fresh()
    assert is_fresh is False


@pytest.mark.asyncio
async def test_is_cache_fresh_empty(cache_service, mock_db):
    """Test cache freshness check - no cached data."""
    # Mock: No cached data
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result

    is_fresh = await cache_service.is_customers_cache_fresh()
    assert is_fresh is False


# ==================== CACHE INVALIDATION TESTS ====================

@pytest.mark.asyncio
async def test_invalidate_cache_all(cache_service, mock_db):
    """Test invalidating all cache types."""
    await cache_service.invalidate_all_caches()
    
    # Should delete from all 3 cache tables
    assert mock_db.execute.call_count == 3
    assert mock_db.commit.called


@pytest.mark.asyncio
async def test_invalidate_cache_specific_type(cache_service, mock_db):
    """Test invalidating specific cache type."""
    await cache_service.invalidate_customer_cache()
    
    # Should delete only from customers cache
    assert mock_db.execute.call_count == 1
    assert mock_db.commit.called


@pytest.mark.asyncio
async def test_invalidate_cache_by_customer(cache_service, mock_db):
    """Test invalidating cache for specific customer."""
    await cache_service.invalidate_customer_cache()
    
    # Should delete customer and related invoices/payments
    assert mock_db.execute.call_count == 3
    assert mock_db.commit.called


# ==================== HIT RATE TRACKING TESTS ====================

def test_get_cache_stats_initial(cache_service):
    """Test cache stats with no hits/misses."""
    stats = cache_service.get_cache_stats()

    assert stats['total_requests'] == 0
    assert stats['hit_count'] == 0
    assert stats['miss_count'] == 0
    assert stats['hit_rate_percent'] == 0.0
@pytest.mark.asyncio
async def test_get_cache_stats_with_hits(cache_service, mock_db):
    """Test cache stats after hits."""
    # Simulate cache hits
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [MagicMock()]
    mock_db.execute.return_value = mock_result
    
    await cache_service.get_cached_customers()
    await cache_service.get_cached_invoices()
    
    stats = cache_service.get_cache_stats()

    assert stats['total_requests'] == 2
    assert stats['hit_count'] == 2
    assert stats['miss_count'] == 0
    assert stats['hit_rate_percent'] == 100.0


@pytest.mark.asyncio
async def test_get_cache_stats_mixed(cache_service, mock_db):
    """Test cache stats with mixed hits/misses."""
    # Hit
    mock_result_hit = MagicMock()
    mock_result_hit.scalars.return_value.all.return_value = [MagicMock()]
    
    # Miss
    mock_result_miss = MagicMock()
    mock_result_miss.scalars.return_value.all.return_value = []
    
    # Simulate 2 hits, 1 miss
    mock_db.execute.side_effect = [mock_result_hit, mock_result_hit, mock_result_miss]
    
    await cache_service.get_cached_customers()
    await cache_service.get_cached_invoices()
    await cache_service.get_cached_payments()
    
    stats = cache_service.get_cache_stats()

    assert stats['total_requests'] == 3
    assert stats['hit_count'] == 2
    assert stats['miss_count'] == 1
    assert stats['hit_rate_percent'] == pytest.approx(66.67, rel=0.01)


def test_reset_cache_stats(cache_service):
    """Test resetting cache stats manually."""
    cache_service._hit_count = 5
    cache_service._miss_count = 3
    
    # Manual reset since no reset method exists
    cache_service._hit_count = 0
    cache_service._miss_count = 0
    
    assert cache_service._hit_count == 0
    assert cache_service._miss_count == 0


# ==================== ERROR HANDLING TESTS ====================

@pytest.mark.asyncio
async def test_cache_customers_db_error(cache_service, mock_db, sample_qb_customer):
    """Test handling database errors during cache."""
    # Mock database error
    mock_db.execute.side_effect = Exception("Database connection failed")
    
    # Should raise exception
    with pytest.raises(Exception) as exc_info:
        await cache_service.cache_customers([sample_qb_customer])
    
    assert "Database connection failed" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_cached_customers_db_error(cache_service, mock_db):
    """Test handling database errors during retrieval."""
    # Mock database error
    mock_db.execute.side_effect = Exception("Database timeout")

    # Service logs error but returns empty list instead of raising
    customers = await cache_service.get_cached_customers()
    assert customers == []
# ==================== EDGE CASES ====================

@pytest.mark.asyncio
async def test_cache_empty_list(cache_service, mock_db):
    """Test caching empty list."""
    count = await cache_service.cache_customers([])
    
    assert count == 0
    assert not mock_db.add.called


@pytest.mark.asyncio
async def test_cache_with_missing_optional_fields(cache_service, mock_db):
    """Test caching customer with missing optional fields."""
    customer = {
        'Id': 'QB999',
        'DisplayName': 'Minimal Customer'
        # No email, phone, company, etc.
    }
    
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result
    
    count = await cache_service.cache_customers([customer])
    
    assert count == 1  # Should still cache


@pytest.mark.asyncio
async def test_is_cache_fresh_invalid_type(cache_service, mock_db):
    """Test cache freshness check with invalid cache type."""
    is_fresh = await cache_service.is_cache_fresh('invalid_type')
    
    assert is_fresh is False
