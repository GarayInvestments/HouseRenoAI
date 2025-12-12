"""
Test QuickBooks Cache Performance (Phase D.1)

Measures API call reduction and response time improvements
from PostgreSQL caching implementation.

Expected Results:
- First call: ~2-3s (API call + cache population)
- Subsequent calls within 5 min: ~50-100ms (cache hit)
- API call reduction: ~90%
"""

import asyncio
import time
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_cache_performance():
    """Test QuickBooks cache performance improvements."""
    from app.services.quickbooks_service import quickbooks_service
    from app.db.database import get_db
    
    logger.info("=" * 80)
    logger.info("PHASE D.1: QuickBooks Cache Performance Test")
    logger.info("=" * 80)
    
    # Set up database session
    db = await anext(get_db())
    quickbooks_service.set_db_session(db)
    
    # Load tokens
    await quickbooks_service.load_tokens()
    
    if not quickbooks_service.is_authenticated():
        logger.error("❌ QuickBooks not authenticated - cannot test cache")
        return
    
    logger.info("✅ QuickBooks authenticated\n")
    
    # Test 1: First call (cache miss)
    logger.info("TEST 1: First Call (Cache Miss - API Call Expected)")
    logger.info("-" * 80)
    start_time = time.time()
    customers_1 = await quickbooks_service.get_customers()
    elapsed_1 = time.time() - start_time
    logger.info(f"⏱️  First call: {elapsed_1:.2f}s")
    logger.info(f"📊 Customers fetched: {len(customers_1)}")
    logger.info("")
    
    # Test 2: Second call (cache hit)
    logger.info("TEST 2: Second Call (Cache Hit Expected - No API Call)")
    logger.info("-" * 80)
    start_time = time.time()
    customers_2 = await quickbooks_service.get_customers()
    elapsed_2 = time.time() - start_time
    logger.info(f"⏱️  Second call: {elapsed_2:.2f}s")
    logger.info(f"📊 Customers fetched: {len(customers_2)}")
    
    # Calculate speedup
    if elapsed_1 > 0:
        speedup = elapsed_1 / elapsed_2 if elapsed_2 > 0 else float('inf')
        logger.info(f"🚀 Speedup: {speedup:.1f}x faster")
    logger.info("")
    
    # Test 3: Invoice caching
    logger.info("TEST 3: Invoice Caching")
    logger.info("-" * 80)
    start_time = time.time()
    invoices_1 = await quickbooks_service.get_invoices()
    elapsed_3 = time.time() - start_time
    logger.info(f"⏱️  First call: {elapsed_3:.2f}s")
    logger.info(f"📊 Invoices fetched: {len(invoices_1)}")
    
    start_time = time.time()
    invoices_2 = await quickbooks_service.get_invoices()
    elapsed_4 = time.time() - start_time
    logger.info(f"⏱️  Second call: {elapsed_4:.2f}s")
    logger.info(f"📊 Invoices fetched: {len(invoices_2)}")
    
    if elapsed_3 > 0:
        speedup = elapsed_3 / elapsed_4 if elapsed_4 > 0 else float('inf')
        logger.info(f"🚀 Speedup: {speedup:.1f}x faster")
    logger.info("")
    
    # Test 4: Payment caching
    logger.info("TEST 4: Payment Caching")
    logger.info("-" * 80)
    start_time = time.time()
    payments_1 = await quickbooks_service.get_payments()
    elapsed_5 = time.time() - start_time
    logger.info(f"⏱️  First call: {elapsed_5:.2f}s")
    logger.info(f"📊 Payments fetched: {len(payments_1)}")
    
    start_time = time.time()
    payments_2 = await quickbooks_service.get_payments()
    elapsed_6 = time.time() - start_time
    logger.info(f"⏱️  Second call: {elapsed_6:.2f}s")
    logger.info(f"📊 Payments fetched: {len(payments_2)}")
    
    if elapsed_5 > 0:
        speedup = elapsed_5 / elapsed_6 if elapsed_6 > 0 else float('inf')
        logger.info(f"🚀 Speedup: {speedup:.1f}x faster")
    logger.info("")
    
    # Get cache statistics
    if quickbooks_service.cache_service:
        stats = quickbooks_service.cache_service.get_cache_stats()
        logger.info("CACHE STATISTICS")
        logger.info("-" * 80)
        logger.info(f"✅ Cache hits: {stats['hit_count']}")
        logger.info(f"❌ Cache misses: {stats['miss_count']}")
        logger.info(f"📊 Total requests: {stats['total_requests']}")
        logger.info(f"🎯 Hit rate: {stats['hit_rate_percent']}%")
        logger.info("")
    
    # Summary
    logger.info("=" * 80)
    logger.info("PHASE D.1 RESULTS SUMMARY")
    logger.info("=" * 80)
    
    total_api_time = elapsed_1 + elapsed_3 + elapsed_5
    total_cache_time = elapsed_2 + elapsed_4 + elapsed_6
    
    if total_api_time > 0:
        overall_speedup = total_api_time / total_cache_time if total_cache_time > 0 else float('inf')
        time_saved = total_api_time - total_cache_time
        reduction_percent = (time_saved / total_api_time) * 100
        
        logger.info(f"⏱️  Total API time (3 calls): {total_api_time:.2f}s")
        logger.info(f"⏱️  Total cache time (3 calls): {total_cache_time:.2f}s")
        logger.info(f"💾 Time saved: {time_saved:.2f}s")
        logger.info(f"📉 Response time reduction: {reduction_percent:.1f}%")
        logger.info(f"🚀 Overall speedup: {overall_speedup:.1f}x faster")
        
        # Estimate API call reduction
        logger.info("")
        logger.info("ESTIMATED API CALL REDUCTION:")
        logger.info(f"- Without cache: 6 API calls (customers x2, invoices x2, payments x2)")
        logger.info(f"- With cache: 3 API calls (first calls only)")
        logger.info(f"- API reduction: 50% (for 2 consecutive calls)")
        logger.info(f"- Over 10 calls in 5-min window: 90% reduction (9/10 from cache)")
    
    logger.info("=" * 80)
    logger.info("✅ Phase D.1 cache performance test complete!")
    logger.info("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_cache_performance())
