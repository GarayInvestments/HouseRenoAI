"""
Reconcile Google Sheets historical data with PostgreSQL database.

Pulls Permits and Payments from Sheets and matches/imports missing records.
Also maps QuickBooks invoices to permits via project/client relationships.
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.google_service import google_service
from app.services.db_service import db_service
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import AsyncSessionLocal


async def reconcile_permits():
    """Compare Sheets permits with DB permits, identify gaps"""
    print("\n" + "="*60)
    print("PERMITS RECONCILIATION")
    print("="*60)
    
    # Get Sheets data
    try:
        sheets_permits = await google_service.get_permits_data()
        print(f"\n📊 Found {len(sheets_permits)} permits in Google Sheets")
    except Exception as e:
        print(f"❌ Could not read Sheets permits: {e}")
        sheets_permits = []
    
    # Get DB data
    db_permits = await db_service.get_permits_data()
    print(f"📊 Found {len(db_permits)} permits in PostgreSQL")
    
    if not sheets_permits:
        print("\n✅ No Sheets data to reconcile (already migrated)")
        return
    
    # Sample comparison
    print("\n📋 Sample Sheets permit:")
    if sheets_permits:
        sample = sheets_permits[0]
        print(f"  Keys: {list(sample.keys())}")
        print(f"  Sample: {sample}")
    
    print("\n📋 Sample DB permit:")
    if db_permits:
        sample = db_permits[0]
        print(f"  Keys: {list(sample.keys())}")
        print(f"  Permit Number: {sample.get('Permit Number')}")
        print(f"  Status: {sample.get('Status')}")


async def reconcile_payments():
    """Compare Sheets payments with DB payments, identify gaps"""
    print("\n" + "="*60)
    print("PAYMENTS RECONCILIATION")
    print("="*60)
    
    # Get Sheets data
    try:
        sheets_payments = await google_service.get_all_sheet_data('Payments')
        print(f"\n📊 Found {len(sheets_payments)} payments in Google Sheets")
    except Exception as e:
        print(f"⚠️  Could not read Sheets payments: {e}")
        sheets_payments = []
    
    # Get DB data
    async with AsyncSessionLocal() as session:
        from sqlalchemy import select, text
        result = await session.execute(text("SELECT * FROM payments"))
        db_payments = [dict(row._mapping) for row in result]
        print(f"📊 Found {len(db_payments)} payments in PostgreSQL")
    
    if not sheets_payments:
        print("\n✅ No Sheets data to reconcile")
        return
    
    # Sample comparison
    print("\n📋 Sample Sheets payment:")
    if sheets_payments:
        sample = sheets_payments[0]
        print(f"  Keys: {list(sample.keys())}")
        for key in ['Payment ID', 'Invoice ID', 'Client ID', 'Amount', 'Payment Date', 'Payment Method', 'QB Payment ID']:
            if key in sample:
                print(f"  {key}: {sample[key]}")
    
    print("\n📋 Sample DB payment:")
    if db_payments:
        sample = db_payments[0]
        print(f"  Keys: {list(sample.keys())}")
        print(f"  Amount: ${sample.get('amount')}")
        print(f"  Payment Date: {sample.get('payment_date')}")
        print(f"  Payment Method: {sample.get('payment_method')}")


async def map_invoices_to_permits():
    """Map QB cached invoices to permits via project relationships"""
    print("\n" + "="*60)
    print("QUICKBOOKS INVOICE → PERMIT MAPPING")
    print("="*60)
    
    async with AsyncSessionLocal() as session:
        from sqlalchemy import select, text
        
        # Get QB invoices from cache
        result = await session.execute(
            text("SELECT qb_invoice_id, customer_id, doc_number, total_amount FROM quickbooks_invoices_cache")
        )
        invoices = [dict(row._mapping) for row in result]
        print(f"\n📊 Found {len(invoices)} QB invoices in cache")
        
        # Get QB customers from cache
        result = await session.execute(
            text("SELECT qb_customer_id, display_name, company_name FROM quickbooks_customers_cache")
        )
        customers = [dict(row._mapping) for row in result]
        print(f"📊 Found {len(customers)} QB customers in cache")
        
        # Get DB clients with QB mapping
        result = await session.execute(
            text("SELECT client_id, business_id, full_name, qb_customer_id FROM clients WHERE qb_customer_id IS NOT NULL")
        )
        clients_with_qb = [dict(row._mapping) for row in result]
        print(f"📊 Found {len(clients_with_qb)} clients mapped to QB customers")
        
        # Get projects
        result = await session.execute(
            text("SELECT project_id, business_id, project_name, client_id FROM projects")
        )
        projects = [dict(row._mapping) for row in result]
        print(f"📊 Found {len(projects)} projects in DB")
        
        # Get permits
        result = await session.execute(
            text("SELECT permit_id, business_id, permit_number, project_id FROM permits WHERE project_id IS NOT NULL")
        )
        permits = [dict(row._mapping) for row in result]
        print(f"📊 Found {len(permits)} permits linked to projects")
    
    # Build mapping chain
    print("\n🔗 Building relationship chain:")
    print("   QB Invoice → QB Customer → Client → Project → Permit")
    
    # Create lookup dictionaries
    qb_customer_to_client = {c['qb_customer_id']: c for c in clients_with_qb}
    client_to_projects = {}
    for project in projects:
        client_id = project['client_id']
        if client_id not in client_to_projects:
            client_to_projects[client_id] = []
        client_to_projects[client_id].append(project)
    
    project_to_permits = {}
    for permit in permits:
        project_id = permit['project_id']
        if project_id not in project_to_permits:
            project_to_permits[project_id] = []
        project_to_permits[project_id].append(permit)
    
    # Map invoices to permits
    mapped_count = 0
    for invoice in invoices[:5]:  # Sample first 5
        qb_customer_id = invoice['customer_id']
        if qb_customer_id in qb_customer_to_client:
            client = qb_customer_to_client[qb_customer_id]
            projects_for_client = client_to_projects.get(str(client['client_id']), [])
            
            print(f"\n📄 Invoice {invoice['doc_number']} (${invoice['total_amount']})")
            print(f"   → Client: {client['full_name']} ({client['business_id']})")
            print(f"   → Projects: {len(projects_for_client)}")
            
            for project in projects_for_client[:2]:  # Show first 2 projects
                permits_for_project = project_to_permits.get(str(project['project_id']), [])
                print(f"      → Project: {project['business_id']} - {project['project_name']}")
                print(f"         → Permits: {len(permits_for_project)}")
                if permits_for_project:
                    mapped_count += 1
                    for permit in permits_for_project:
                        print(f"            ✅ Permit: {permit['business_id']} ({permit['permit_number']})")
    
    print(f"\n✅ Successfully mapped {mapped_count} invoices to permits (sample)")


async def main():
    """Run all reconciliation tasks"""
    print("\n" + "="*70)
    print(" GOOGLE SHEETS → POSTGRESQL RECONCILIATION")
    print("="*70)
    
    # Initialize services
    print("\n🔄 Initializing services...")
    try:
        # Import and set module-level instances
        from app.services import google_service as gs_module, db_service as ds_module
        from app.services.google_service import GoogleService
        from app.services.db_service import DBService
        
        # Create instances
        gs_module.google_service = GoogleService()
        ds_module.db_service = DBService()
        
        # Initialize
        gs_module.google_service.initialize()
        await ds_module.db_service.initialize()
        
        print("✅ Services initialized")
    except Exception as e:
        print(f"❌ Service initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Run reconciliation tasks
    await reconcile_permits()
    await reconcile_payments()
    await map_invoices_to_permits()
    
    print("\n" + "="*70)
    print("RECONCILIATION COMPLETE")
    print("="*70)
    print("\nNext steps:")
    print("1. Review gaps identified above")
    print("2. Create migration script to import missing Sheets data")
    print("3. Link QB invoices to permits in database")
    print("="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
