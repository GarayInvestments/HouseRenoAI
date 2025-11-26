"""Check what CustomerType entities exist in QuickBooks"""
import asyncio
from app.services.quickbooks_service import quickbooks_service

async def main():
    print("Querying CustomerType entities from QuickBooks...\n")
    
    query = "SELECT * FROM CustomerType"
    try:
        response = await quickbooks_service._make_request("GET", "query", params={"query": query})
        types = response.get("QueryResponse", {}).get("CustomerType", [])
        
        if not types:
            print("❌ No CustomerType entities found!")
            print("\n💡 You may need to create 'GC Compliance' CustomerType in QuickBooks first.")
            return
        
        print(f"✅ Found {len(types)} CustomerType entities:\n")
        gc_found = False
        for t in types:
            type_id = t.get("Id")
            type_name = t.get("Name")
            active = t.get("Active", True)
            status = "✅" if active else "❌"
            print(f"  {status} {type_name}: ID = {type_id}")
            if type_name == "GC Compliance":
                gc_found = True
                print(f"     👆 This is the GC Compliance type!")
        
        if not gc_found:
            print(f"\n❌ 'GC Compliance' CustomerType not found in QuickBooks")
            print("   You need to create it first or use a different type name.")
        
    except Exception as e:
        print(f"❌ Error querying CustomerTypes: {e}")

if __name__ == "__main__":
    asyncio.run(main())
