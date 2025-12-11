"""
Service Integration Tests - Test all Phase A.3 services

Tests CRUD operations, business ID generation, and service integration.
Run: pytest scripts/test_services.py -v
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta
from decimal import Decimal

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.services.permit_service import permit_service
from app.services.inspection_service import inspection_service
from app.services.invoice_service import invoice_service
from app.services.payment_service import payment_service
from app.services.site_visit_service import site_visit_service


async def test_all_services():
    """Run all service integration tests"""
    
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    print("\n" + "="*80)
    print("SERVICE INTEGRATION TESTS - PHASE A.3")
    print("="*80)
    
    async with async_session() as db:
        try:
            # Get existing data for testing
            from sqlalchemy import select, text
            from app.db.models import Project, Client
            
            # Get first project and client
            project_result = await db.execute(select(Project).limit(1))
            project = project_result.scalar_one()
            
            client_result = await db.execute(select(Client).limit(1))
            client = client_result.scalar_one()
            
            print(f"\nTest Data:")
            print(f"  Project: {project.business_id} - {project.project_name}")
            print(f"  Client: {client.business_id} - {client.full_name}")
            
            # Test 1: PermitService
            print("\n" + "-"*80)
            print("TEST 1: PermitService")
            print("-"*80)
            
            permit = await permit_service.create_permit(
                db=db,
                project_id=project.project_id,
                permit_type="Building",
                permit_number="TEST-PERMIT-001",
                status="Pending"
            )
            await db.commit()
            
            print(f"✅ Created permit: {permit.business_id}")
            assert permit.business_id.startswith("PER-"), "Business ID should start with PER-"
            assert permit.permit_type == "Building"
            
            # Update permit status
            updated_permit = await permit_service.update_status(
                db=db,
                permit_id=permit.permit_id,
                new_status="Approved",
                notes="Test approval"
            )
            await db.commit()
            
            print(f"✅ Updated permit status: Pending → Approved")
            assert updated_permit.status == "Approved"
            assert len(updated_permit.status_history) > 0
            
            # Get permits by project
            permits = await permit_service.get_permits(db=db, project_id=project.project_id)
            print(f"✅ Retrieved {len(permits)} permits for project")
            
            # Test 2: InspectionService
            print("\n" + "-"*80)
            print("TEST 2: InspectionService")
            print("-"*80)
            
            inspection = await inspection_service.create_inspection(
                db=db,
                permit_id=permit.permit_id,
                project_id=project.project_id,
                inspection_type="Framing",
                scheduled_date=datetime.now(timezone.utc) + timedelta(days=7)
            )
            await db.commit()
            
            print(f"✅ Created inspection: {inspection.business_id}")
            assert inspection.business_id.startswith("INS-"), "Business ID should start with INS-"
            assert inspection.status == "Scheduled"
            
            # Upload photos
            photos = [
                {"url": "https://example.com/photo1.jpg", "caption": "Test photo 1"},
                {"url": "https://example.com/photo2.jpg", "caption": "Test photo 2"}
            ]
            inspection_with_photos = await inspection_service.upload_photos(
                db=db,
                inspection_id=inspection.inspection_id,
                photos=photos
            )
            await db.commit()
            
            print(f"✅ Uploaded {len(photos)} photos to inspection")
            assert len(inspection_with_photos.photos) >= 2
            
            # Complete inspection
            completed = await inspection_service.complete_inspection(
                db=db,
                inspection_id=inspection.inspection_id,
                result="Passed",
                notes="All items checked"
            )
            await db.commit()
            
            print(f"✅ Completed inspection with result: {completed.result}")
            assert completed.status == "Completed"
            assert completed.result == "Passed"
            
            # Test 3: InvoiceService
            print("\n" + "-"*80)
            print("TEST 3: InvoiceService")
            print("-"*80)
            
            invoice = await invoice_service.create_invoice(
                db=db,
                project_id=project.project_id,
                client_id=client.client_id,
                invoice_number="TEST-INV-001",
                total_amount=Decimal("5000.00"),
                line_items=[
                    {"description": "Labor", "quantity": 40, "rate": 100},
                    {"description": "Materials", "quantity": 1, "rate": 1000}
                ],
                status="Draft"
            )
            await db.commit()
            
            print(f"✅ Created invoice: {invoice.business_id}")
            assert invoice.business_id.startswith("INV-"), "Business ID should start with INV-"
            assert invoice.total_amount == Decimal("5000.00")
            assert invoice.balance_due == Decimal("5000.00")
            
            # Test 4: PaymentService
            print("\n" + "-"*80)
            print("TEST 4: PaymentService")
            print("-"*80)
            
            payment = await payment_service.record_payment(
                db=db,
                invoice_id=invoice.invoice_id,
                amount=Decimal("2000.00"),
                payment_date=datetime.now(timezone.utc),
                payment_method="Check",
                reference_number="CHK-12345"
            )
            await db.commit()
            
            print(f"✅ Recorded payment: {payment.business_id}")
            assert payment.business_id.startswith("PAY-"), "Business ID should start with PAY-"
            assert payment.amount == Decimal("2000.00")
            
            # Apply payment to invoice
            result = await payment_service.apply_to_invoice(
                db=db,
                payment_id=payment.payment_id,
                invoice_id=invoice.invoice_id
            )
            await db.commit()
            
            print(f"✅ Applied payment to invoice")
            print(f"   Amount applied: ${result['amount_applied']}")
            print(f"   New balance: ${result['new_balance']}")
            print(f"   Invoice status: {result['invoice_status']}")
            
            # Verify invoice was updated
            updated_invoice = await invoice_service.get_by_id(db, invoice.invoice_id)
            assert updated_invoice.amount_paid == Decimal("2000.00")
            assert updated_invoice.balance_due == Decimal("3000.00")
            assert updated_invoice.status == "Partially Paid"
            
            # Test 5: SiteVisitService
            print("\n" + "-"*80)
            print("TEST 5: SiteVisitService")
            print("-"*80)
            
            site_visit = await site_visit_service.schedule_visit(
                db=db,
                project_id=project.project_id,
                client_id=client.client_id,
                visit_type="Progress Check",
                scheduled_time=datetime.now(timezone.utc) + timedelta(days=3),
                attendees=["John Smith", "Jane Doe"],
                purpose="Review framing progress"
            )
            await db.commit()
            
            print(f"✅ Scheduled site visit: {site_visit.business_id}")
            assert site_visit.business_id.startswith("SV-"), "Business ID should start with SV-"
            assert site_visit.status == "Scheduled"
            
            # Start visit
            started_visit = await site_visit_service.start_visit(
                db=db,
                visit_id=site_visit.visit_id,
                gps_location={"latitude": 34.0522, "longitude": -118.2437}
            )
            await db.commit()
            
            print(f"✅ Started site visit")
            assert started_visit.status == "In Progress"
            assert started_visit.gps_location is not None
            
            # Upload photos to visit
            visit_photos = [
                {"url": "https://example.com/visit1.jpg", "caption": "Before work"}
            ]
            visit_with_photos = await site_visit_service.upload_photos(
                db=db,
                visit_id=site_visit.visit_id,
                photos=visit_photos
            )
            await db.commit()
            
            print(f"✅ Uploaded photos to site visit")
            assert len(visit_with_photos.photos) >= 1
            
            # Create follow-up actions
            actions = [
                {
                    "description": "Order additional materials",
                    "priority": "high",
                    "assigned_to": "Foreman",
                    "due_date": (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
                },
                {
                    "description": "Schedule electrical inspection",
                    "priority": "medium",
                    "assigned_to": "Project Manager",
                    "due_date": (datetime.now(timezone.utc) + timedelta(days=5)).isoformat()
                }
            ]
            visit_with_actions = await site_visit_service.create_follow_up_actions(
                db=db,
                visit_id=site_visit.visit_id,
                actions=actions
            )
            await db.commit()
            
            print(f"✅ Created {len(actions)} follow-up actions")
            assert len(visit_with_actions.follow_up_actions) >= 2
            
            # Complete visit
            completed_visit = await site_visit_service.complete_visit(
                db=db,
                visit_id=site_visit.visit_id,
                summary="Framing complete, ready for inspection"
            )
            await db.commit()
            
            print(f"✅ Completed site visit")
            assert completed_visit.status == "Completed"
            assert completed_visit.summary is not None
            
            # Test 6: Business ID Queries
            print("\n" + "-"*80)
            print("TEST 6: Business ID Queries")
            print("-"*80)
            
            permit_by_bid = await permit_service.get_by_business_id(db, permit.business_id)
            print(f"✅ Retrieved permit by business ID: {permit_by_bid.business_id}")
            assert permit_by_bid.permit_id == permit.permit_id
            
            inspection_by_bid = await inspection_service.get_by_business_id(db, inspection.business_id)
            print(f"✅ Retrieved inspection by business ID: {inspection_by_bid.business_id}")
            assert inspection_by_bid.inspection_id == inspection.inspection_id
            
            invoice_by_bid = await invoice_service.get_by_business_id(db, invoice.business_id)
            print(f"✅ Retrieved invoice by business ID: {invoice_by_bid.business_id}")
            assert invoice_by_bid.invoice_id == invoice.invoice_id
            
            payment_by_bid = await payment_service.get_by_business_id(db, payment.business_id)
            print(f"✅ Retrieved payment by business ID: {payment_by_bid.business_id}")
            assert payment_by_bid.payment_id == payment.payment_id
            
            visit_by_bid = await site_visit_service.get_by_business_id(db, site_visit.business_id)
            print(f"✅ Retrieved site visit by business ID: {visit_by_bid.business_id}")
            assert visit_by_bid.visit_id == site_visit.visit_id
            
            # Summary
            print("\n" + "="*80)
            print("✅ ALL SERVICE TESTS PASSED!")
            print("="*80)
            print("\nCreated Test Records:")
            print(f"  Permit: {permit.business_id}")
            print(f"  Inspection: {inspection.business_id}")
            print(f"  Invoice: {invoice.business_id}")
            print(f"  Payment: {payment.business_id}")
            print(f"  Site Visit: {site_visit.business_id}")
            print("\nService Layer Features Verified:")
            print("  ✅ Business ID auto-generation")
            print("  ✅ CRUD operations for all entities")
            print("  ✅ Status tracking and history")
            print("  ✅ Photo uploads")
            print("  ✅ Payment application to invoices")
            print("  ✅ Follow-up action creation")
            print("  ✅ Business ID queries")
            print("\n  Phase A.3 Complete - Service Layer Ready!")
            print("="*80 + "\n")
            
        except Exception as e:
            print(f"\n❌ TEST FAILED: {e}")
            import traceback
            traceback.print_exc()
            raise


if __name__ == "__main__":
    asyncio.run(test_all_services())
