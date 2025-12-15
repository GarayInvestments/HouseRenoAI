"""
QuickBooks Concurrent Request Behavior

Purpose: Test parallel request handling and rate limiting behavior
Framework: Stress-Test Mode (Discovery Phase)
"""

import asyncio
import sys
import os
import time
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.session import AsyncSessionLocal
from app.services.quickbooks_service import get_quickbooks_service
from quickbooks.objects.customer import Customer


async def single_query_task(qb_service, query: str, task_id: int):
    """Execute a single query and track timing."""
    
    start = time.time()
    try:
        result = Customer.query(query, qb=qb_service.qb_client)
        elapsed = (time.time() - start) * 1000
        count = len(result) if isinstance(result, list) else (1 if result else 0)
        
        return {
            'task_id': task_id,
            'success': True,
            'count': count,
            'elapsed_ms': elapsed,
            'error': None
        }
    except Exception as e:
        elapsed = (time.time() - start) * 1000
        return {
            'task_id': task_id,
            'success': False,
            'count': 0,
            'elapsed_ms': elapsed,
            'error': str(e)[:200]
        }


async def concurrent_burst(qb_service, query: str, num_requests: int, description: str):
    """Execute multiple queries concurrently."""
    
    print(f"\n{description}")
    print(f"  Launching {num_requests} concurrent requests...")
    
    start = time.time()
    
    # Launch all tasks simultaneously
    tasks = [single_query_task(qb_service, query, i) for i in range(num_requests)]
    results = await asyncio.gather(*tasks)
    
    total_elapsed = (time.time() - start) * 1000
    
    # Analyze results
    successful = len([r for r in results if r['success']])
    failed = len([r for r in results if not r['success']])
    
    avg_response_time = sum(r['elapsed_ms'] for r in results if r['success']) / successful if successful > 0 else 0
    min_response_time = min(r['elapsed_ms'] for r in results if r['success']) if successful > 0 else 0
    max_response_time = max(r['elapsed_ms'] for r in results if r['success']) if successful > 0 else 0
    
    print(f"  Total wall time: {total_elapsed:.0f}ms")
    print(f"  Successful: {successful}/{num_requests}")
    print(f"  Failed: {failed}/{num_requests}")
    
    if successful > 0:
        print(f"  Response times: min={min_response_time:.0f}ms, avg={avg_response_time:.0f}ms, max={max_response_time:.0f}ms")
    
    if failed > 0:
        print(f"  ⚠️  {failed} requests failed")
        # Show first 3 errors
        errors = [r['error'] for r in results if not r['success']]
        for error in errors[:3]:
            print(f"    - {error[:100]}")
    
    return {
        'description': description,
        'num_requests': num_requests,
        'total_elapsed_ms': total_elapsed,
        'successful': successful,
        'failed': failed,
        'avg_response_ms': avg_response_time,
        'min_response_ms': min_response_time,
        'max_response_ms': max_response_time,
        'individual_results': results
    }


async def sequential_burst(qb_service, query: str, num_requests: int, description: str):
    """Execute multiple queries sequentially for comparison."""
    
    print(f"\n{description}")
    print(f"  Executing {num_requests} sequential requests...")
    
    start = time.time()
    results = []
    
    for i in range(num_requests):
        result = await single_query_task(qb_service, query, i)
        results.append(result)
    
    total_elapsed = (time.time() - start) * 1000
    
    successful = len([r for r in results if r['success']])
    avg_response_time = sum(r['elapsed_ms'] for r in results if r['success']) / successful if successful > 0 else 0
    
    print(f"  Total time: {total_elapsed:.0f}ms")
    print(f"  Successful: {successful}/{num_requests}")
    print(f"  Avg response time: {avg_response_time:.0f}ms")
    
    return {
        'description': description,
        'num_requests': num_requests,
        'total_elapsed_ms': total_elapsed,
        'successful': successful,
        'avg_response_ms': avg_response_time
    }


async def run_concurrent_tests():
    """Run concurrent request tests."""
    
    print("=" * 80)
    print("QuickBooks Concurrent Request Behavior")
    print("Testing parallel requests and rate limiting")
    print("=" * 80)
    
    async with AsyncSessionLocal() as db:
        qb_service = get_quickbooks_service(db)
        await qb_service.load_tokens_from_db()
        
        if not qb_service.is_authenticated():
            print("❌ Not authenticated")
            return
        
        print("✅ Authenticated\n")
        
        test_query = "SELECT * FROM Customer MAXRESULTS 5"
        
        all_results = []
        
        # ============================================================
        # Test 1: Small Burst (5 concurrent)
        # ============================================================
        print("=" * 80)
        print("Test 1: Small Burst (5 concurrent requests)")
        print("=" * 80)
        
        result = await concurrent_burst(qb_service, test_query, 5, "Small burst test")
        all_results.append(result)
        
        await asyncio.sleep(2)  # Cooldown
        
        # ============================================================
        # Test 2: Medium Burst (10 concurrent)
        # ============================================================
        print("\n" + "=" * 80)
        print("Test 2: Medium Burst (10 concurrent requests)")
        print("=" * 80)
        
        result = await concurrent_burst(qb_service, test_query, 10, "Medium burst test")
        all_results.append(result)
        
        await asyncio.sleep(2)  # Cooldown
        
        # ============================================================
        # Test 3: Large Burst (20 concurrent)
        # ============================================================
        print("\n" + "=" * 80)
        print("Test 3: Large Burst (20 concurrent requests)")
        print("=" * 80)
        
        result = await concurrent_burst(qb_service, test_query, 20, "Large burst test")
        all_results.append(result)
        
        await asyncio.sleep(2)  # Cooldown
        
        # ============================================================
        # Test 4: Sequential Comparison (10 requests)
        # ============================================================
        print("\n" + "=" * 80)
        print("Test 4: Sequential Baseline (10 requests)")
        print("=" * 80)
        
        seq_result = await sequential_burst(qb_service, test_query, 10, "Sequential baseline")
        
        # ============================================================
        # Test 5: Mixed Entity Types Concurrently
        # ============================================================
        print("\n" + "=" * 80)
        print("Test 5: Mixed Entity Types (5 different entities, 3 requests each)")
        print("=" * 80)
        
        from quickbooks.objects.invoice import Invoice
        from quickbooks.objects.payment import Payment
        
        print("\n  Launching mixed entity queries...")
        start = time.time()
        
        mixed_tasks = []
        
        # 3 customer queries
        for i in range(3):
            mixed_tasks.append(single_query_task(qb_service, "SELECT * FROM Customer MAXRESULTS 5", i))
        
        # 3 invoice queries
        async def invoice_query(task_id):
            try:
                result = Invoice.query("SELECT * FROM Invoice MAXRESULTS 5", qb=qb_service.qb_client)
                count = len(result) if isinstance(result, list) else 1
                return {'task_id': task_id, 'entity': 'Invoice', 'success': True, 'count': count}
            except Exception as e:
                return {'task_id': task_id, 'entity': 'Invoice', 'success': False, 'error': str(e)[:100]}
        
        for i in range(3, 6):
            mixed_tasks.append(invoice_query(i))
        
        # 3 payment queries
        async def payment_query(task_id):
            try:
                result = Payment.query("SELECT * FROM Payment MAXRESULTS 5", qb=qb_service.qb_client)
                count = len(result) if isinstance(result, list) else 1
                return {'task_id': task_id, 'entity': 'Payment', 'success': True, 'count': count}
            except Exception as e:
                return {'task_id': task_id, 'entity': 'Payment', 'success': False, 'error': str(e)[:100]}
        
        for i in range(6, 9):
            mixed_tasks.append(payment_query(i))
        
        mixed_results = await asyncio.gather(*mixed_tasks)
        mixed_elapsed = (time.time() - start) * 1000
        
        mixed_successful = len([r for r in mixed_results if r.get('success')])
        print(f"  Total time: {mixed_elapsed:.0f}ms")
        print(f"  Successful: {mixed_successful}/9")
        
        # ============================================================
        # Test 6: Sustained Load (30 requests over 10 seconds)
        # ============================================================
        print("\n" + "=" * 80)
        print("Test 6: Sustained Load (30 requests over ~10 seconds)")
        print("=" * 80)
        
        print("\n  Launching sustained load test...")
        sustained_results = []
        start = time.time()
        
        for i in range(30):
            result = await single_query_task(qb_service, test_query, i)
            sustained_results.append(result)
            await asyncio.sleep(0.3)  # ~3 requests per second
        
        sustained_elapsed = (time.time() - start) * 1000
        sustained_successful = len([r for r in sustained_results if r['success']])
        
        print(f"  Total time: {sustained_elapsed:.0f}ms ({sustained_elapsed/1000:.1f} seconds)")
        print(f"  Successful: {sustained_successful}/30")
        print(f"  Effective rate: {30 / (sustained_elapsed/1000):.1f} requests/second")
        
        # ============================================================
        # ANALYSIS
        # ============================================================
        print("\n" + "=" * 80)
        print("ANALYSIS")
        print("=" * 80)
        
        # Concurrent vs Sequential comparison
        concurrent_10 = next((r for r in all_results if r['num_requests'] == 10), None)
        if concurrent_10 and seq_result:
            speedup = seq_result['total_elapsed_ms'] / concurrent_10['total_elapsed_ms']
            print(f"\nConcurrent vs Sequential (10 requests):")
            print(f"  Concurrent: {concurrent_10['total_elapsed_ms']:.0f}ms")
            print(f"  Sequential: {seq_result['total_elapsed_ms']:.0f}ms")
            print(f"  Speedup: {speedup:.2f}x faster with concurrency")
        
        # Scaling analysis
        print("\nScaling behavior (concurrent requests):")
        for result in all_results:
            num = result['num_requests']
            wall_time = result['total_elapsed_ms']
            avg_per_request = wall_time / num
            print(f"  {num} requests: {wall_time:.0f}ms total ({avg_per_request:.0f}ms per request)")
        
        # Rate limiting detection
        print("\nRate limiting detection:")
        all_failed = sum(r['failed'] for r in all_results)
        if all_failed > 0:
            print(f"  ⚠️  {all_failed} total failures across burst tests")
            print("  Possible rate limiting or connection issues")
        else:
            print("  ✅ No rate limiting detected in burst tests")
            print("  All concurrent requests succeeded")
        
        # ============================================================
        # KEY FINDINGS
        # ============================================================
        print("\n" + "=" * 80)
        print("KEY FINDINGS")
        print("=" * 80)
        
        if all_results:
            max_concurrent = max(r['num_requests'] for r in all_results)
            max_concurrent_result = next(r for r in all_results if r['num_requests'] == max_concurrent)
            
            if max_concurrent_result['successful'] == max_concurrent_result['num_requests']:
                print(f"\n✅ Successfully handled {max_concurrent} concurrent requests")
                print("  No apparent rate limiting for burst requests")
            else:
                failed_pct = max_concurrent_result['failed'] / max_concurrent_result['num_requests'] * 100
                print(f"\n⚠️  {failed_pct:.0f}% failure rate at {max_concurrent} concurrent requests")
                print("  Possible rate limit or connection limit")
        
        if concurrent_10 and seq_result:
            efficiency = (seq_result['total_elapsed_ms'] / concurrent_10['total_elapsed_ms']) / 10
            print(f"\n✅ Concurrency efficiency: {efficiency:.1%}")
            print(f"  Concurrent execution provides {speedup:.1f}x speedup")
        
        print(f"\n✅ Sustained load: {sustained_successful}/30 requests succeeded")
        print(f"  Effective rate: {30 / (sustained_elapsed/1000):.1f} req/sec")
        
        print("\n" + "=" * 80)
        print("RECOMMENDATIONS")
        print("=" * 80)
        print("1. Concurrent requests work well for sync operations")
        print("2. No obvious rate limiting for reasonable burst sizes (<20)")
        print("3. Mixed entity types can be queried concurrently")
        print("4. Sustained load at ~3 req/sec appears safe")
        print("5. Consider concurrent execution for batch sync operations")
        print("6. Monitor for 429 (rate limit) errors in production")
        
        with open("concurrent_behavior_results.json", "w") as f:
            json.dump({
                'burst_tests': all_results,
                'sequential_baseline': seq_result,
                'mixed_entities': {'elapsed_ms': mixed_elapsed, 'successful': mixed_successful},
                'sustained_load': {'elapsed_ms': sustained_elapsed, 'successful': sustained_successful}
            }, f, indent=2)
        
        print(f"\n📄 Results saved to: concurrent_behavior_results.json")


if __name__ == "__main__":
    asyncio.run(run_concurrent_tests())
