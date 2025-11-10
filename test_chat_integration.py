"""
Test chat queries to verify context enhancements and payments integration
"""

import asyncio
import sys
sys.path.insert(0, '.')

from app.services.openai_service import openai_service
from app.services.google_service import GoogleService
from app.services.quickbooks_service import quickbooks_service
from app.utils.context_builder import build_context
from app.memory.memory_manager import memory_manager


async def test_chat_query(query: str, session_id: str = "test_session"):
    """Test a single chat query"""
    print(f"\n{'='*60}")
    print(f"🗣️  Query: {query}")
    print(f"{'='*60}")
    
    try:
        # Initialize services
        google_service = GoogleService()
        google_service.initialize()
        
        # Build context
        session_memory = memory_manager.get_all(session_id)
        context = await build_context(query, google_service, quickbooks_service, session_memory)
        
        print(f"\n📊 Context loaded: {context.get('contexts_loaded', [])}")
        
        # Check if payments data was loaded
        if 'payments' in context:
            print(f"💰 Payments loaded: {len(context['payments'])} records")
        
        # Check if projects data was loaded
        if 'all_projects' in context:
            print(f"📁 Projects loaded: {len(context['all_projects'])} records")
            if context['all_projects']:
                project = context['all_projects'][0]
                # Check for enhanced fields
                has_cost = bool(project.get('Project Cost (Materials + Labor)'))
                has_type = bool(project.get('Project Type'))
                has_start = bool(project.get('Start Date'))
                has_county = bool(project.get('County'))
                print(f"   Enhanced fields: Cost={has_cost}, Type={has_type}, Start={has_start}, County={has_county}")
        
        # Check if permits data was loaded
        if 'all_permits' in context:
            print(f"📋 Permits loaded: {len(context['all_permits'])} records")
            if context['all_permits']:
                permit = context['all_permits'][0]
                has_project_id = bool(permit.get('Project ID'))
                has_app_date = bool(permit.get('Application Date'))
                has_appr_date = bool(permit.get('Approval Date'))
                print(f"   Enhanced fields: ProjectID={has_project_id}, AppDate={has_app_date}, ApprDate={has_appr_date}")
        
        print(f"\n✅ Query processed successfully")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Test various chat queries"""
    print("\n" + "="*60)
    print("🧪 CHAT INTEGRATION TESTS")
    print("="*60)
    
    test_queries = [
        "What's the project cost for Temple?",
        "Show me all payments",
        "Has Javier paid his invoice?",
        "When was the permit for 47 Main applied?",
        "Sync payments from QuickBooks",
        "Get payment history for client",
    ]
    
    results = []
    for query in test_queries:
        result = await test_chat_query(query)
        results.append((query, result))
        await asyncio.sleep(0.5)  # Brief pause between tests
    
    # Summary
    print("\n" + "="*60)
    print("📊 CHAT TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for query, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {query}")
    
    print(f"\n📈 Results: {passed}/{total} queries processed successfully")
    
    if passed == total:
        print("\n🎉 All chat integration tests passed!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
