"""
Create permits from provided data table with intelligent field inference.

Handles:
- Permit type inference from permit number patterns
- UTC-aware datetime conversion
- Metadata preservation in extra field
- Responsibility role defaults
- Grouped permit batch tracking
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime, timezone
import re

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.session import AsyncSessionLocal
from app.db.models import Permit
from sqlalchemy import select


def infer_permit_type(permit_number: str) -> str:
    """
    Infer permit type from permit number pattern.
    
    Examples:
    - RES-ADD-* → Residential Addition
    - RES-ALT-* → Residential Alteration
    - PRB* → Building Permit
    - B-*, BC-*, BP-* → Building Permit
    - PRRN* → Plan Review
    - BU* → Building Permit
    """
    permit_upper = permit_number.upper()
    
    if permit_upper.startswith('RES-ADD'):
        return 'Residential Addition'
    elif permit_upper.startswith('RES-ALT'):
        return 'Residential Alteration'
    elif permit_upper.startswith('PRB') or permit_upper.startswith('BU'):
        return 'Building Permit'
    elif permit_upper.startswith('B-') or permit_upper.startswith('BC-') or permit_upper.startswith('BP-'):
        return 'Building Permit'
    elif permit_upper.startswith('PRRN'):
        return 'Plan Review'
    else:
        return 'Building Permit'  # Safe default


def detect_grouped_batch(permit_number: str, all_permits: list) -> str | None:
    """
    Detect if this permit is part of a grouped batch (e.g., multiple PRRN permits).
    
    Returns the batch identifier (first permit number) if part of a group, else None.
    """
    # Extract base pattern (e.g., PRRN202502429 → PRRN20250242)
    base_match = re.match(r'([A-Z]+\d+)\d$', permit_number)
    if not base_match:
        return None
    
    base_pattern = base_match.group(1)
    
    # Find all permits with similar pattern
    similar = [
        p['permit_number'] for p in all_permits 
        if p['permit_number'].startswith(base_pattern) and p['permit_number'] != permit_number
    ]
    
    if similar:
        # Return earliest permit number as batch ID
        all_in_batch = [permit_number] + similar
        return sorted(all_in_batch)[0]
    
    return None


async def create_permits():
    """Create permits from table data."""
    
    # Permit data from user table
    permits_data = [
        {
            "permit_number": "BC-25-0409",
            "project_id": "6e1ff79c-a63d-4f6d-bec4-4c56f3c89612",
            "client_id": "9f9990c1-e217-4dd4-a68b-f983a726113c",
            "status": "Approved",
            "application_date": "2025-05-21",
            "approval_date": "2025-05-21"
        },
        {
            "permit_number": "BP-25-35",
            "project_id": "dc546b0c-e9aa-44dc-bff7-ca1585c7632a",
            "client_id": "a9f0df2a-0f80-4030-94eb-e9097ad6f7b4",
            "status": "Closed",
            "application_date": "2025-05-05",
            "approval_date": "2025-05-06"
        },
        {
            "permit_number": "PRRN202502429",
            "project_id": "e3eaa00f-c370-4114-911c-b7633cc81927",
            "client_id": "493f8b53-ab37-4943-a18a-a68f36cc30a3",
            "status": "Under Review",
            "application_date": "2025-10-13",
            "approval_date": None
        },
        {
            "permit_number": "PRRN2025024230",
            "project_id": "e3eaa00f-c370-4114-911c-b7633cc81927",
            "client_id": "493f8b53-ab37-4943-a18a-a68f36cc30a3",
            "status": "Under Review",
            "application_date": "2025-10-13",
            "approval_date": None
        },
        {
            "permit_number": "PRRN2025024231",
            "project_id": "e3eaa00f-c370-4114-911c-b7633cc81927",
            "client_id": "493f8b53-ab37-4943-a18a-a68f36cc30a3",
            "status": "Under Review",
            "application_date": "2025-10-13",
            "approval_date": None
        },
        {
            "permit_number": "PRRN2025024232",
            "project_id": "e3eaa00f-c370-4114-911c-b7633cc81927",
            "client_id": "493f8b53-ab37-4943-a18a-a68f36cc30a3",
            "status": "Under Review",
            "application_date": "2025-10-13",
            "approval_date": None
        },
        {
            "permit_number": "PRRN202501103",
            "project_id": "ad857828-99ee-41ac-b79d-e516b3b092ea",
            "client_id": "c38f08e7-ad9e-407f-a9c9-76a1f95272fa",
            "status": "Approved",
            "application_date": "2025-05-23",
            "approval_date": "2025-06-02"
        },
        {
            "permit_number": "RES-ALT-25-001173",
            "project_id": "cca678d5-f28a-466b-b632-41990b9118e1",
            "client_id": "5b58597d-c1ab-4aee-8272-ebdc85316461",
            "status": "Closed",
            "application_date": "2025-08-01",
            "approval_date": "2025-08-01"
        },
        {
            "permit_number": "B-25-636",
            "project_id": "52195167-d5ee-4fd0-863b-7003eef8accb",
            "client_id": "493f8b53-ab37-4943-a18a-a68f36cc30a3",
            "status": "Approved",
            "application_date": "2025-10-22",
            "approval_date": "2025-10-22"
        },
        {
            "permit_number": "PRB2025-02843",
            "project_id": "284f0239-160d-4f9f-a66e-c87f55e025dd",
            "client_id": "493f8b53-ab37-4943-a18a-a68f36cc30a3",
            "status": "Approved",
            "application_date": "2025-10-17",
            "approval_date": "2025-11-04"
        },
        {
            "permit_number": "B01825",
            "project_id": "d3e0676c-ea61-4a89-90f2-ddfac4578068",
            "client_id": "569b9f27-def3-4881-aa2e-2e646823a9ff",
            "status": "Closed",
            "application_date": "2025-11-07",
            "approval_date": "2025-11-07"
        },
        {
            "permit_number": "RES-ADD-25-000990",
            "project_id": "93e74448-5097-4ff7-9110-b8e82ba76aa2",
            "client_id": "493f8b53-ab37-4943-a18a-a68f36cc30a3",
            "status": "Approved",
            "application_date": "2025-10-28",
            "approval_date": "2025-12-01"
        },
        {
            "permit_number": "RES-ADD-25-000964",
            "project_id": "12239f59-98f8-4778-ba4a-8d6efa48e139",
            "client_id": "493f8b53-ab37-4943-a18a-a68f36cc30a3",
            "status": "Approved",
            "application_date": "2025-09-25",
            "approval_date": "2025-11-19"
        },
        {
            "permit_number": "BU2025-03428",
            "project_id": "424fd588-6110-483d-a632-f9817d6da2ad",
            "client_id": "493f8b53-ab37-4943-a18a-a68f36cc30a3",
            "status": "Approved",
            "application_date": "2025-10-31",
            "approval_date": "2025-12-01"
        }
    ]
    
    async with AsyncSessionLocal() as db:
        created_count = 0
        skipped_count = 0
        
        for permit_data in permits_data:
            # Check if permit already exists
            result = await db.execute(
                select(Permit).where(Permit.permit_number == permit_data["permit_number"])
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                print(f"⚠️  Permit {permit_data['permit_number']} already exists, skipping")
                skipped_count += 1
                continue
            
            # Parse dates (UTC-aware)
            application_date = None
            if permit_data["application_date"]:
                application_date = datetime.strptime(permit_data["application_date"], "%Y-%m-%d").replace(tzinfo=timezone.utc)
            
            approval_date = None
            if permit_data.get("approval_date"):
                approval_date = datetime.strptime(permit_data["approval_date"], "%Y-%m-%d").replace(tzinfo=timezone.utc)
            
            # Infer permit type from permit number
            permit_type = infer_permit_type(permit_data["permit_number"])
            
            # Detect if part of grouped batch
            batch_id = detect_grouped_batch(permit_data["permit_number"], permits_data)
            
            # Build extra metadata
            extra = {
                "source": "initial_import",
                "import_date": datetime.now(timezone.utc).isoformat(),
                "inferred_permit_type": True
            }
            
            if batch_id:
                extra["grouped_permit_batch"] = batch_id
            
            # Create permit with full intelligence
            permit = Permit(
                permit_number=permit_data["permit_number"],
                project_id=permit_data["project_id"],
                client_id=permit_data["client_id"],
                permit_type=permit_type,
                status=permit_data["status"],
                application_date=application_date,
                approval_date=approval_date,
                responsibility_role="PRIMARY_LICENSE_HOLDER",  # Safe default, can be updated later
                extra=extra
            )
            
            db.add(permit)
            batch_note = f" [Batch: {batch_id}]" if batch_id else ""
            print(f"✅ Creating permit {permit_data['permit_number']} (Type: {permit_type}, Status: {permit_data['status']}){batch_note}")
            created_count += 1
        
        # Commit all permits
        await db.commit()
        
        print("\n" + "=" * 80)
        print(f"✅ Successfully created {created_count} permits")
        print(f"⚠️  Skipped {skipped_count} existing permits")
        print("=" * 80)


if __name__ == "__main__":
    asyncio.run(create_permits())
