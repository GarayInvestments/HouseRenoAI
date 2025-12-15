"""
QuickBooks Stress-Test Suite Master Runner

Purpose: Execute all stress tests in sequence with proper cooldown periods
Framework: Stress-Test Mode (Discovery Phase)
"""

import asyncio
import subprocess
import time
import sys

def run_test_script(script_name: str, description: str):
    """Run a test script and capture results."""
    
    print("\n" + "=" * 80)
    print(f"RUNNING: {description}")
    print(f"Script: {script_name}")
    print("=" * 80)
    print()
    
    start = time.time()
    
    try:
        result = subprocess.run(
            [sys.executable, f"scripts/{script_name}"],
            capture_output=False,
            text=True,
            timeout=300  # 5 minute timeout per test
        )
        
        elapsed = time.time() - start
        
        if result.returncode == 0:
            print(f"\n✅ {description} completed successfully in {elapsed:.1f}s")
            return True
        else:
            print(f"\n❌ {description} failed with exit code {result.returncode}")
            return False
    
    except subprocess.TimeoutExpired:
        print(f"\n⏱️  {description} timed out after 5 minutes")
        return False
    except Exception as e:
        print(f"\n❌ {description} error: {e}")
        return False


def main():
    """Run all stress tests in sequence."""
    
    print("=" * 80)
    print("QuickBooks API Stress-Test Suite")
    print("Comprehensive Discovery Phase Testing")
    print("=" * 80)
    print()
    print("This suite will run 5 test scripts:")
    print("1. POST Method Deep Dive")
    print("2. Encoding & Special Characters")
    print("3. Error Response Patterns")
    print("4. Entity-Specific Quirks")
    print("5. Concurrent Request Behavior")
    print()
    print("Estimated total time: 10-15 minutes")
    print("=" * 80)
    
    input("\nPress Enter to start tests...")
    
    suite_start = time.time()
    results = {}
    
    # Test 1: POST Method Deep Dive
    results['post_method'] = run_test_script(
        "test_qb_post_method_deep_dive.py",
        "POST Method Deep Dive"
    )
    print("\nCooldown: 5 seconds...")
    time.sleep(5)
    
    # Test 2: Encoding Edge Cases
    results['encoding'] = run_test_script(
        "test_qb_encoding_edge_cases.py",
        "Encoding & Special Characters"
    )
    print("\nCooldown: 5 seconds...")
    time.sleep(5)
    
    # Test 3: Error Patterns
    results['error_patterns'] = run_test_script(
        "test_qb_error_patterns.py",
        "Error Response Patterns"
    )
    print("\nCooldown: 5 seconds...")
    time.sleep(5)
    
    # Test 4: Entity Quirks
    results['entity_quirks'] = run_test_script(
        "test_qb_entity_quirks.py",
        "Entity-Specific Quirks"
    )
    print("\nCooldown: 5 seconds...")
    time.sleep(5)
    
    # Test 5: Concurrent Requests
    results['concurrent'] = run_test_script(
        "test_qb_concurrent_requests.py",
        "Concurrent Request Behavior"
    )
    
    suite_elapsed = time.time() - suite_start
    
    # Summary
    print("\n" + "=" * 80)
    print("STRESS-TEST SUITE COMPLETE")
    print("=" * 80)
    
    total_tests = len(results)
    successful = len([r for r in results.values() if r])
    failed = total_tests - successful
    
    print(f"\nTotal test scripts: {total_tests}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Total time: {suite_elapsed/60:.1f} minutes")
    
    print("\nIndividual results:")
    status_emoji = {True: "✅", False: "❌"}
    for test_name, success in results.items():
        print(f"  {status_emoji[success]} {test_name}: {'PASSED' if success else 'FAILED'}")
    
    print("\n" + "=" * 80)
    print("GENERATED ARTIFACTS")
    print("=" * 80)
    print("\nResult files created:")
    print("  • post_method_deep_dive_results.json")
    print("  • encoding_edge_cases_results.json")
    print("  • error_patterns_results.json")
    print("  • entity_quirks_results.json")
    print("  • concurrent_behavior_results.json")
    
    print("\n" + "=" * 80)
    print("NEXT STEPS")
    print("=" * 80)
    print("\n1. Review all JSON result files for detailed findings")
    print("2. Update docs/audits/QUICKBOOKS_SDK_VS_HTTP_ANALYSIS.md with new discoveries")
    print("3. Identify any surprising behaviors that contradict earlier assumptions")
    print("4. Plan Phase 2 validation tests based on findings")
    print("5. Document production recommendations")
    
    if successful == total_tests:
        print("\n🎉 All tests completed successfully!")
        print("   Proceed to Phase 2: Validation over 24+ hours")
    else:
        print(f"\n⚠️  {failed} test(s) failed")
        print("   Review errors before proceeding to Phase 2")
    
    print()


if __name__ == "__main__":
    main()
