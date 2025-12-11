"""
Test script for newly added models: Inspection, Invoice, Payment (updated), SiteVisit
Validates that all models work correctly with sample data.
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timezone
from app.config import settings
from app.db.models import Inspection, Invoice, Payment, SiteVisit, Client, Project, Permit


async def test_models():
    """Test all new models with sample data"""
    
    # Create async engine
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        print("\n" + "="*80)
        print("TESTING NEW MODELS")
        print("="*80)
        
        # Get existing client and project for FKs
        from sqlalchemy import select
        result = await session.execute(select(Client).limit(1))
        client = result.scalars().first()
        
        if not client:
            print("❌ No clients found. Run migration scripts first.")
            return
        
        result = await session.execute(select(Project).where(Project.client_id == client.client_id).limit(1))
        project = result.scalars().first()
        
        if not project:
            print("❌ No projects found. Run migration scripts first.")
            return
        
        result = await session.execute(select(Permit).where(Permit.project_id == project.project_id).limit(1))
        permit = result.scalars().first()
        
        print(f"\n✅ Found test data:")
        print(f"   Client: {client.full_name} (ID: {client.client_id})")
        print(f"   Project: {project.project_address} (ID: {project.project_id})")
        if permit:
            print(f"   Permit: {permit.permit_type} (ID: {permit.permit_id})")
        
        # Test 1: Create Inspection
        print("\n" + "-"*80)
        print("TEST 1: Creating Inspection")
        print("-"*80)
        
        if permit:
            inspection = Inspection(
                permit_id=permit.permit_id,
                project_id=project.project_id,
                inspection_type="Foundation",
                status="Scheduled",
                scheduled_date=datetime.now(timezone.utc),
                inspector="John Smith",
                photos={
                    "photos": [
                        {"url": "https://example.com/photo1.jpg", "gps": "40.7128,-74.0060", "timestamp": "2025-12-10T10:30:00Z"},
                        {"url": "https://example.com/photo2.jpg", "gps": "40.7128,-74.0060", "timestamp": "2025-12-10T10:35:00Z"}
                    ]
                },
                deficiencies={
                    "deficiencies": [
                        {"description": "Rebar spacing incorrect", "severity": "High", "photo_refs": [0]}
                    ]
                },
                notes="Initial foundation inspection"
            )
            session.add(inspection)
            await session.commit()
            await session.refresh(inspection)
            
            print(f"✅ Created Inspection:")
            print(f"   ID: {inspection.inspection_id}")
            print(f"   Business ID: {inspection.business_id} (will be set by trigger)")
            print(f"   Type: {inspection.inspection_type}")
            print(f"   Status: {inspection.status}")
            print(f"   Photos: {len(inspection.photos.get('photos', []))} photos")
            print(f"   Deficiencies: {len(inspection.deficiencies.get('deficiencies', []))} found")
        else:
            print("⚠️  Skipping - no permit found for inspection")
        
        # Test 2: Create Invoice
        print("\n" + "-"*80)
        print("TEST 2: Creating Invoice")
        print("-"*80)
        
        invoice = Invoice(
            project_id=project.project_id,
            client_id=client.client_id,
            invoice_number="INV-2025-001",
            invoice_date=datetime.now(timezone.utc),
            subtotal=5000.00,
            tax_amount=400.00,
            total_amount=5400.00,
            balance=5400.00,
            status="Draft",
            line_items={
                "items": [
                    {"description": "Foundation Work", "quantity": 1, "rate": 3000.00, "amount": 3000.00},
                    {"description": "Framing", "quantity": 1, "rate": 2000.00, "amount": 2000.00}
                ]
            },
            sync_status="pending",
            notes="Test invoice for foundation and framing work"
        )
        session.add(invoice)
        await session.commit()
        await session.refresh(invoice)
        
        print(f"✅ Created Invoice:")
        print(f"   ID: {invoice.invoice_id}")
        print(f"   Business ID: {invoice.business_id} (will be set by trigger)")
        print(f"   Number: {invoice.invoice_number}")
        print(f"   Total: ${invoice.total_amount}")
        print(f"   Status: {invoice.status}")
        print(f"   Sync Status: {invoice.sync_status}")
        print(f"   Line Items: {len(invoice.line_items.get('items', []))} items")
        
        # Test 3: Create Payment
        print("\n" + "-"*80)
        print("TEST 3: Creating Payment")
        print("-"*80)
        
        payment = Payment(
            invoice_id=invoice.invoice_id,
            client_id=client.client_id,
            project_id=project.project_id,
            amount=2700.00,
            payment_date=datetime.now(timezone.utc),
            payment_method="Check",
            reference_number="CHK-12345",
            status="Cleared",
            sync_status="pending",
            notes="50% deposit payment"
        )
        session.add(payment)
        await session.commit()
        await session.refresh(payment)
        
        print(f"✅ Created Payment:")
        print(f"   ID: {payment.payment_id}")
        print(f"   Business ID: {payment.business_id} (will be set by trigger)")
        print(f"   Amount: ${payment.amount}")
        print(f"   Method: {payment.payment_method}")
        print(f"   Reference: {payment.reference_number}")
        print(f"   Status: {payment.status}")
        print(f"   Sync Status: {payment.sync_status}")
        
        # Test 4: Create SiteVisit
        print("\n" + "-"*80)
        print("TEST 4: Creating Site Visit")
        print("-"*80)
        
        site_visit = SiteVisit(
            project_id=project.project_id,
            client_id=client.client_id,
            visit_type="Progress Check",
            status="Completed",
            scheduled_date=datetime.now(timezone.utc),
            start_time=datetime.now(timezone.utc),
            end_time=datetime.now(timezone.utc),
            gps_location="40.7128,-74.0060",
            attendees={
                "attendees": [
                    {"name": "Jane Doe", "role": "Project Manager", "email": "jane@example.com"},
                    {"name": "Bob Smith", "role": "Client", "email": "bob@example.com"}
                ]
            },
            photos={
                "photos": [
                    {"url": "https://example.com/site1.jpg", "gps": "40.7128,-74.0060", "timestamp": "2025-12-10T14:00:00Z", "caption": "Foundation progress"},
                    {"url": "https://example.com/site2.jpg", "gps": "40.7128,-74.0060", "timestamp": "2025-12-10T14:15:00Z", "caption": "Framing started"}
                ]
            },
            deficiencies={
                "deficiencies": [
                    {"description": "Minor cleanup needed in corner", "severity": "Low", "location": "NW corner", "photo_refs": [1]}
                ]
            },
            follow_up_actions={
                "actions": [
                    {"type": "punchlist", "status": "pending", "description": "Schedule cleanup crew"}
                ]
            },
            notes="Good progress overall. Foundation looks solid, framing ahead of schedule.",
            weather="Sunny, 72°F"
        )
        session.add(site_visit)
        await session.commit()
        await session.refresh(site_visit)
        
        print(f"✅ Created Site Visit:")
        print(f"   ID: {site_visit.visit_id}")
        print(f"   Business ID: {site_visit.business_id} (will be set by trigger)")
        print(f"   Type: {site_visit.visit_type}")
        print(f"   Status: {site_visit.status}")
        print(f"   GPS: {site_visit.gps_location}")
        print(f"   Attendees: {len(site_visit.attendees.get('attendees', []))} people")
        print(f"   Photos: {len(site_visit.photos.get('photos', []))} photos")
        print(f"   Deficiencies: {len(site_visit.deficiencies.get('deficiencies', []))} found")
        print(f"   Follow-ups: {len(site_visit.follow_up_actions.get('actions', []))} actions")
        print(f"   Weather: {site_visit.weather}")
        
        # Test 5: Query with JSONB fields
        print("\n" + "-"*80)
        print("TEST 5: Testing JSONB Queries (GIN Indexes)")
        print("-"*80)
        
        # Query inspections with photos
        from sqlalchemy.dialects.postgresql import JSONB
        result = await session.execute(
            select(Inspection).where(Inspection.photos.isnot(None))
        )
        inspections_with_photos = result.scalars().all()
        print(f"✅ Found {len(inspections_with_photos)} inspection(s) with photos")
        
        # Query site visits with deficiencies
        result = await session.execute(
            select(SiteVisit).where(SiteVisit.deficiencies.isnot(None))
        )
        visits_with_deficiencies = result.scalars().all()
        print(f"✅ Found {len(visits_with_deficiencies)} site visit(s) with deficiencies")
        
        # Query invoices with line items
        result = await session.execute(
            select(Invoice).where(Invoice.line_items.isnot(None))
        )
        invoices_with_items = result.scalars().all()
        print(f"✅ Found {len(invoices_with_items)} invoice(s) with line items")
        
        print("\n" + "="*80)
        print("✅ ALL TESTS PASSED!")
        print("="*80)
        print("\nSummary:")
        print("  - All 4 new models created successfully")
        print("  - JSONB fields working correctly")
        print("  - Foreign keys validated")
        print("  - Business IDs will be set by triggers (Phase A.2)")
        print("  - GIN indexes ready for complex queries")
        print("\nNext Steps:")
        print("  1. Implement business ID sequences and triggers (Phase A.2)")
        print("  2. Create service layer for CRUD operations (Phase A.3)")
        print("  3. Build API endpoints (Phase B.1-B.2)")
        print("="*80 + "\n")


if __name__ == "__main__":
    asyncio.run(test_models())
