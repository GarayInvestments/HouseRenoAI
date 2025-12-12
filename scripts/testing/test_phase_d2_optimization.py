"""
Phase D.2 Performance Test: Context Size Optimization

Tests token reduction achieved through intelligent truncation.
Compares before (optimize=False) vs after (optimize=True).

Target: 40-50% token reduction while maintaining response quality.

Run: python scripts/testing/test_phase_d2_optimization.py
"""

import asyncio
import sys
import json
import logging
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.utils.context_builder import build_context
from app.services.quickbooks_service import quickbooks_service
from app.memory.memory_manager import memory_manager

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def count_tokens(text: str) -> int:
    """
    Rough token estimation using OpenAI's rule of thumb:
    ~4 characters = 1 token
    
    For more accurate counting, would use tiktoken library.
    """
    return len(text) // 4


def analyze_context_size(context: dict) -> dict:
    """
    Analyze token usage breakdown of context dict.
    """
    # Convert context to JSON string for token counting
    context_json = json.dumps(context, default=str)
    total_tokens = count_tokens(context_json)
    
    analysis = {
        "total_tokens": total_tokens,
        "breakdown": {}
    }
    
    # Analyze each major component
    components = ["projects", "permits", "clients", "payments"]
    for component in components:
        if component in context:
            component_json = json.dumps(context[component], default=str)
            component_tokens = count_tokens(component_json)
            
            # Check if summary available
            summary_key = f"{component}_summary"
            summary_data = context.get(summary_key, {})
            
            analysis["breakdown"][component] = {
                "count": len(context[component]),
                "tokens": component_tokens,
                "percentage": (component_tokens / total_tokens * 100) if total_tokens > 0 else 0,
                "summary": summary_data
            }
    
    # QuickBooks data
    if "quickbooks" in context:
        qb = context["quickbooks"]
        qb_json = json.dumps(qb, default=str)
        qb_tokens = count_tokens(qb_json)
        
        analysis["breakdown"]["quickbooks"] = {
            "customers": len(qb.get("customers", [])),
            "invoices": len(qb.get("invoices", [])),
            "tokens": qb_tokens,
            "percentage": (qb_tokens / total_tokens * 100) if total_tokens > 0 else 0
        }
    
    return analysis


async def test_query_comparison(query: str, description: str):
    """
    Test a query with and without optimization.
    Compare token reduction.
    """
    print(f"\n{'='*80}")
    print(f"Test: {description}")
    print(f"Query: '{query}'")
    print(f"{'='*80}")
    
    session_id = f"test_session_{datetime.now().timestamp()}"
    session_memory = memory_manager.get_all(session_id)
    
    # Test WITHOUT optimization (baseline)
    print(f"\n🔴 BEFORE Optimization (Phase D.1 only):")
    context_before = await build_context(
        message=query,
        qb_service=quickbooks_service,
        session_memory=session_memory,
        optimize=False
    )
    
    analysis_before = analyze_context_size(context_before)
    print(f"  Total Tokens: {analysis_before['total_tokens']:,}")
    
    for component, data in analysis_before["breakdown"].items():
        if component == "quickbooks":
            print(f"  • {component}: {data['tokens']:,} tokens ({data['percentage']:.1f}%) - "
                  f"{data['customers']} customers, {data['invoices']} invoices")
        else:
            print(f"  • {component}: {data['tokens']:,} tokens ({data['percentage']:.1f}%) - "
                  f"{data['count']} records")
    
    # Test WITH optimization (Phase D.2)
    print(f"\n🟢 AFTER Optimization (Phase D.2):")
    session_memory_opt = memory_manager.get_all(session_id)
    context_after = await build_context(
        message=query,
        qb_service=quickbooks_service,
        session_memory=session_memory_opt,
        optimize=True
    )
    
    analysis_after = analyze_context_size(context_after)
    print(f"  Total Tokens: {analysis_after['total_tokens']:,}")
    
    for component, data in analysis_after["breakdown"].items():
        summary = data.get("summary", {})
        filtered = summary.get("filtered", False)
        shown = summary.get("shown", data.get("count", 0))
        total = summary.get("total", shown)
        
        if component == "quickbooks":
            print(f"  • {component}: {data['tokens']:,} tokens ({data['percentage']:.1f}%) - "
                  f"{data['customers']} customers, {data['invoices']} invoices")
        else:
            filter_note = " (filtered)" if filtered else ""
            print(f"  • {component}: {data['tokens']:,} tokens ({data['percentage']:.1f}%) - "
                  f"{shown}/{total} records{filter_note}")
    
    # Calculate reduction
    token_reduction = analysis_before['total_tokens'] - analysis_after['total_tokens']
    reduction_pct = (token_reduction / analysis_before['total_tokens'] * 100) if analysis_before['total_tokens'] > 0 else 0
    
    print(f"\n📊 Optimization Results:")
    print(f"  • Before: {analysis_before['total_tokens']:,} tokens")
    print(f"  • After: {analysis_after['total_tokens']:,} tokens")
    print(f"  • Reduction: {token_reduction:,} tokens ({reduction_pct:.1f}%)")
    
    # Success indicator
    if reduction_pct >= 40:
        print(f"  • Status: ✅ TARGET ACHIEVED (≥40% reduction)")
    elif reduction_pct >= 30:
        print(f"  • Status: ⚠️ CLOSE TO TARGET (30-40% reduction)")
    else:
        print(f"  • Status: ❌ BELOW TARGET (<30% reduction)")
    
    return {
        "query": query,
        "description": description,
        "tokens_before": analysis_before['total_tokens'],
        "tokens_after": analysis_after['total_tokens'],
        "reduction_tokens": token_reduction,
        "reduction_pct": reduction_pct
    }


async def main():
    """Run comprehensive Phase D.2 optimization tests."""
    print("\n" + "="*80)
    print("PHASE D.2: Context Size Optimization Performance Test")
    print("="*80)
    print("\nTarget: 40-50% token reduction while maintaining AI response quality")
    print("Strategy: Query-relevant filtering + recent data priority")
    
    # Test queries representing different scenarios
    test_cases = [
        # Specific queries (high filtering potential)
        ("What's the status of the Temple project?", 
         "Specific project query (should filter heavily)"),
        
        ("Show me invoices for Temple Hills", 
         "Specific client + QB query (should filter to 1 client)"),
        
        ("List all payments for PRJ-00001", 
         "Specific project payments (should filter to 1 project)"),
        
        # General queries (moderate filtering)
        ("Show me all active projects", 
         "General projects query (should limit to recent)"),
        
        ("List all unpaid invoices", 
         "QB query (should show recent only)"),
        
        # Broad queries (minimal filtering)
        ("Give me a summary of all clients and projects", 
         "Broad summary query (limited filtering)"),
    ]
    
    results = []
    for query, description in test_cases:
        try:
            result = await test_query_comparison(query, description)
            results.append(result)
            await asyncio.sleep(1)  # Avoid rate limiting
        except Exception as e:
            print(f"\n❌ Error: {e}")
            logger.error(f"Error testing query '{query}': {e}", exc_info=True)
    
    # Overall Summary
    print("\n" + "="*80)
    print("PHASE D.2 SUMMARY")
    print("="*80)
    
    if results:
        avg_reduction_pct = sum(r["reduction_pct"] for r in results) / len(results)
        max_reduction_pct = max(r["reduction_pct"] for r in results)
        min_reduction_pct = min(r["reduction_pct"] for r in results)
        
        total_tokens_before = sum(r["tokens_before"] for r in results)
        total_tokens_after = sum(r["tokens_after"] for r in results)
        total_reduction = total_tokens_before - total_tokens_after
        total_reduction_pct = (total_reduction / total_tokens_before * 100) if total_tokens_before > 0 else 0
        
        print(f"\n📊 Overall Statistics:")
        print(f"  • Tests run: {len(results)}")
        print(f"  • Average reduction: {avg_reduction_pct:.1f}%")
        print(f"  • Max reduction: {max_reduction_pct:.1f}%")
        print(f"  • Min reduction: {min_reduction_pct:.1f}%")
        print(f"  • Total tokens before: {total_tokens_before:,}")
        print(f"  • Total tokens after: {total_tokens_after:,}")
        print(f"  • Total reduction: {total_reduction:,} tokens ({total_reduction_pct:.1f}%)")
        
        # Phase D.2 Success Evaluation
        print(f"\n🎯 Phase D.2 Target Evaluation:")
        if avg_reduction_pct >= 40:
            print(f"  ✅ SUCCESS: Average reduction {avg_reduction_pct:.1f}% meets target (≥40%)")
        elif avg_reduction_pct >= 35:
            print(f"  ⚠️ CLOSE: Average reduction {avg_reduction_pct:.1f}% slightly below target")
            print(f"     Recommendation: Fine-tune truncation thresholds")
        else:
            print(f"  ❌ NEEDS WORK: Average reduction {avg_reduction_pct:.1f}% below target")
            print(f"     Recommendation: Increase truncation aggressiveness")
        
        # Per-query breakdown
        print(f"\n📋 Per-Query Results:")
        for i, result in enumerate(results, 1):
            status = "✅" if result["reduction_pct"] >= 40 else "⚠️" if result["reduction_pct"] >= 30 else "❌"
            print(f"  {status} Test {i}: {result['reduction_pct']:.1f}% reduction")
            print(f"     '{result['query'][:60]}...'")
        
        # Next Steps
        print(f"\n🚀 Next Steps:")
        if avg_reduction_pct >= 40:
            print(f"  1. ✅ Phase D.2 target achieved")
            print(f"  2. Deploy optimization to production")
            print(f"  3. Monitor AI response quality")
            print(f"  4. Update documentation")
        else:
            print(f"  1. Fine-tune truncation parameters:")
            print(f"     - Reduce max_recent_projects (currently 10)")
            print(f"     - Reduce max_recent_permits (currently 15)")
            print(f"     - Reduce max_customers (currently 20)")
            print(f"  2. Re-run tests")
            print(f"  3. Validate response quality")


if __name__ == "__main__":
    asyncio.run(main())
