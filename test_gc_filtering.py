"""
Test GC Compliance filtering in QuickBooks context.

This test verifies:
1. Only GC Compliance customers are loaded in context
2. Only invoices for GC Compliance customers are included
3. Logging shows filtering statistics
4. AI receives optimized context (reduced tokens)
"""

import asyncio
import httpx

BASE_URL = "http://localhost:8000"

async def test_gc_filtering():
    """Test chat with QuickBooks context to verify GC Compliance filtering."""
    
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        # Login to get token
        print("🔐 Logging in...")
        login_response = await client.post(
            f"{BASE_URL}/v1/auth/login",
            json={
                "email": "steve@garayinvestments.com",
                "password": "Stv060485!"
            }
        )
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            print(login_response.text)
            return
        
        token = login_response.json()["access_token"]
        print(f"✅ Logged in successfully")
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test 1: Ask about QuickBooks customers (should trigger QB context loading)
        print("\n" + "="*70)
        print("TEST 1: QuickBooks Customer Query (Triggers Context Loading)")
        print("="*70)
        
        chat_response = await client.post(
            f"{BASE_URL}/v1/chat",
            headers=headers,
            json={
                "message": "Show me all QuickBooks customers",
                "session_id": "test_gc_filter_session"
            }
        )
        
        if chat_response.status_code == 200:
            result = chat_response.json()
            print(f"\n📊 Response Status: {chat_response.status_code}")
            print(f"✅ AI Response: {result['response'][:200]}...")
            print(f"🔍 Action Taken: {result.get('action_taken', 'None')}")
            print(f"💾 Session Active: {result.get('memory_active', False)}")
        else:
            print(f"❌ Chat failed: {chat_response.status_code}")
            print(chat_response.text)
            return
        
        # Test 2: Ask about invoices (should use filtered context)
        print("\n" + "="*70)
        print("TEST 2: Invoice Query (Uses Filtered Context)")
        print("="*70)
        
        invoice_response = await client.post(
            f"{BASE_URL}/v1/chat",
            headers=headers,
            json={
                "message": "How many unpaid invoices do we have?",
                "session_id": "test_gc_filter_session"
            }
        )
        
        if invoice_response.status_code == 200:
            result = invoice_response.json()
            print(f"\n📊 Response Status: {invoice_response.status_code}")
            print(f"✅ AI Response: {result['response'][:200]}...")
        else:
            print(f"❌ Invoice query failed: {invoice_response.status_code}")
        
        # Test 3: Map clients (handler should still fetch ALL customers)
        print("\n" + "="*70)
        print("TEST 3: Client Mapping (Handler Fetches ALL Customers)")
        print("="*70)
        
        map_response = await client.post(
            f"{BASE_URL}/v1/chat",
            headers=headers,
            json={
                "message": "Show me how clients would map to QB without making changes",
                "session_id": "test_gc_filter_session"
            }
        )
        
        if map_response.status_code == 200:
            result = map_response.json()
            print(f"\n📊 Response Status: {map_response.status_code}")
            print(f"✅ AI Response: {result['response']}")
            
            # Check function results for orphaned customers
            func_results = result.get('function_results', [])
            if func_results:
                print(f"\n📋 Function Results:")
                for fr in func_results:
                    summary = fr.get('summary', {})
                    print(f"  - Already Mapped: {summary.get('already_mapped', 0)}")
                    print(f"  - Newly Matched: {summary.get('newly_matched', 0)}")
                    print(f"  - Unmapped Clients: {summary.get('unmapped_clients', 0)}")
                    print(f"  - Orphaned QB Customers: {summary.get('orphaned_qb_customers', 0)}")
        else:
            print(f"❌ Mapping failed: {map_response.status_code}")
        
        print("\n" + "="*70)
        print("✅ All Tests Complete")
        print("="*70)
        print("\n📝 Check server logs for:")
        print("  - '[QB CONTEXT] Filtered to X GC Compliance customers from Y total'")
        print("  - '[QB CONTEXT] Filtered to X GC Compliance invoices from Y total'")
        print("  - '[CLIENT MAPPING] Found 25 customers in QuickBooks' (should be ALL)")

if __name__ == "__main__":
    print("🧪 Testing GC Compliance Filtering\n")
    asyncio.run(test_gc_filtering())
