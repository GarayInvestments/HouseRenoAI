"""
Metrics Collection Script - Run during Nov 8-10, 2025

This script tests production endpoints and measures response times.
Run this script several times per day to collect baseline data.

Usage:
    python scripts/collect_metrics.py

Output:
    docs/metrics/baseline/metrics_YYYYMMDD.json
"""

import time
import requests
import json
from datetime import datetime
from pathlib import Path

# Production API URL
API_URL = "https://houserenoai.onrender.com/v1"

# Test data for various endpoints
TEST_CASES = [
    {
        "name": "Simple Chat (no tools)",
        "method": "POST",
        "path": "/chat",
        "data": {"message": "Hello, how are you?"}
    },
    {
        "name": "Get Projects",
        "method": "GET",
        "path": "/projects",
        "data": None
    },
    {
        "name": "Get Permits",
        "method": "GET", 
        "path": "/permits",
        "data": None
    },
    {
        "name": "Get Clients",
        "method": "GET",
        "path": "/clients",
        "data": None
    },
]


def test_endpoint(name, method, path, data=None):
    """Test endpoint and measure response time"""
    print(f"Testing: {name}...", end=" ", flush=True)
    
    try:
        start = time.time()
        response = requests.request(
            method, 
            f"{API_URL}{path}", 
            json=data,
            timeout=60  # Increased to 60 seconds for slow endpoints
        )
        duration = (time.time() - start) * 1000  # convert to ms
        
        result = {
            "timestamp": datetime.now().isoformat(),
            "endpoint": name,
            "method": method,
            "path": path,
            "duration_ms": round(duration, 2),
            "status_code": response.status_code,
            "success": response.status_code < 400
        }
        
        # Try to parse response for function calls
        if method == "POST" and path == "/chat":
            try:
                # For streaming responses, we can't easily parse
                # Just note that it was a chat request
                result["type"] = "chat"
            except:
                pass
        
        status = "✅" if result["success"] else "❌"
        print(f"{status} {duration:.0f}ms ({response.status_code})")
        
        return result
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return {
            "timestamp": datetime.now().isoformat(),
            "endpoint": name,
            "method": method,
            "path": path,
            "error": str(e),
            "success": False
        }


def collect_metrics():
    """Run all test cases and save results"""
    print("="*60)
    print("BASELINE METRICS COLLECTION")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API: {API_URL}")
    print("="*60)
    print()
    
    results = []
    
    for test_case in TEST_CASES:
        result = test_endpoint(
            test_case["name"],
            test_case["method"],
            test_case["path"],
            test_case.get("data")
        )
        results.append(result)
        time.sleep(1)  # Be nice to the API
    
    # Save results
    date_str = datetime.now().strftime("%Y%m%d")
    time_str = datetime.now().strftime("%H%M%S")
    
    # Create output directory
    output_dir = Path(__file__).parent.parent / "docs" / "metrics" / "baseline"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save with timestamp in filename
    output_file = output_dir / f"metrics_{date_str}_{time_str}.json"
    
    data = {
        "collection_date": datetime.now().isoformat(),
        "api_url": API_URL,
        "results": results,
        "summary": {
            "total_tests": len(results),
            "successful": sum(1 for r in results if r.get("success", False)),
            "failed": sum(1 for r in results if not r.get("success", False)),
            "avg_duration_ms": round(
                sum(r.get("duration_ms", 0) for r in results if "duration_ms" in r) / 
                len([r for r in results if "duration_ms" in r]),
                2
            ) if any("duration_ms" in r for r in results) else 0
        }
    }
    
    with open(output_file, "w") as f:
        json.dump(data, f, indent=2)
    
    print()
    print("="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Total Tests: {data['summary']['total_tests']}")
    print(f"Successful: {data['summary']['successful']}")
    print(f"Failed: {data['summary']['failed']}")
    print(f"Avg Duration: {data['summary']['avg_duration_ms']:.0f}ms")
    print()
    print(f"Results saved to: {output_file}")
    print()
    print("Run this script multiple times per day for 3 days (Nov 8-10)")
    print("to collect comprehensive baseline data.")
    print()


if __name__ == "__main__":
    collect_metrics()
