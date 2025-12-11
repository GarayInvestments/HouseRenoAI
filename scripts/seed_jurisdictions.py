"""
Seed Jurisdiction Data (Phase A.4)

This script seeds the jurisdictions table with Minnesota jurisdictions
commonly used by House Renovators AI Portal.

Run this script after all migrations are applied.

Usage:
    python scripts/seed_jurisdictions.py
"""

import asyncio
import sys
import os
import json
from datetime import datetime, timezone

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text


# Minnesota jurisdictions commonly served
JURISDICTIONS = [
    {
        "name": "City of Burnsville",
        "state": "MN",
        "requirements": {
            "permit_validity_months": 6,
            "inspection_sequence": {
                "Footing": [],
                "Foundation": ["Footing"],
                "Framing": ["Foundation"],
                "Rough Plumbing": ["Framing"],
                "Rough Electrical": ["Framing"],
                "Rough Mechanical": ["Framing"],
                "Insulation": ["Rough Plumbing", "Rough Electrical", "Rough Mechanical"],
                "Final": ["Insulation"]
            },
            "required_documents": {
                "Framing": ["structural_plans"],
                "Rough Electrical": ["electrical_plans"],
                "Final": ["certificate_of_occupancy_application"]
            },
            "fees": {
                "residential_building_permit_base": 150.00,
                "residential_inspection_base": 50.00,
                "commercial_building_permit_base": 300.00,
                "commercial_inspection_base": 75.00
            },
            "contact": {
                "phone": "952-895-4400",
                "email": "permits@burnsvillemn.gov",
                "address": "100 Civic Center Pkwy, Burnsville, MN 55337"
            }
        }
    },
    {
        "name": "City of Minneapolis",
        "state": "MN",
        "requirements": {
            "permit_validity_months": 12,
            "inspection_sequence": {
                "Footing": [],
                "Foundation": ["Footing"],
                "Framing": ["Foundation"],
                "Rough-In": ["Framing"],
                "Insulation": ["Rough-In"],
                "Final": ["Insulation"]
            },
            "required_documents": {
                "Framing": ["structural_plans", "energy_calcs"],
                "Final": ["as_built_plans"]
            },
            "fees": {
                "residential_building_permit_base": 200.00,
                "residential_inspection_base": 60.00,
                "commercial_building_permit_base": 400.00,
                "commercial_inspection_base": 100.00
            },
            "contact": {
                "phone": "612-673-3000",
                "email": "inspections@minneapolismn.gov",
                "address": "250 S 4th St, Minneapolis, MN 55415"
            }
        }
    },
    {
        "name": "City of St. Paul",
        "state": "MN",
        "requirements": {
            "permit_validity_months": 12,
            "inspection_sequence": {
                "Footing": [],
                "Foundation": ["Footing"],
                "Framing": ["Foundation"],
                "Rough Plumbing": ["Framing"],
                "Rough Electrical": ["Framing"],
                "Rough Mechanical": ["Framing"],
                "Insulation": ["Rough Plumbing", "Rough Electrical", "Rough Mechanical"],
                "Final": ["Insulation"]
            },
            "required_documents": {
                "Framing": ["structural_plans", "energy_calcs"],
                "Rough Electrical": ["electrical_plans"],
                "Final": ["truth_in_housing_evaluation"]
            },
            "fees": {
                "residential_building_permit_base": 175.00,
                "residential_inspection_base": 55.00,
                "commercial_building_permit_base": 350.00,
                "commercial_inspection_base": 90.00
            },
            "contact": {
                "phone": "651-266-8989",
                "email": "dsi@ci.stpaul.mn.us",
                "address": "375 Jackson St, Suite 220, St. Paul, MN 55101"
            }
        }
    },
    {
        "name": "City of Bloomington",
        "state": "MN",
        "requirements": {
            "permit_validity_months": 6,
            "inspection_sequence": {
                "Footing": [],
                "Foundation": ["Footing"],
                "Framing": ["Foundation"],
                "Rough-In": ["Framing"],
                "Final": ["Rough-In"]
            },
            "required_documents": {
                "Framing": ["structural_plans"]
            },
            "fees": {
                "residential_building_permit_base": 160.00,
                "residential_inspection_base": 50.00,
                "commercial_building_permit_base": 320.00,
                "commercial_inspection_base": 80.00
            },
            "contact": {
                "phone": "952-563-8920",
                "email": "inspections@bloomingtonmn.gov",
                "address": "1800 W Old Shakopee Rd, Bloomington, MN 55431"
            }
        }
    },
    {
        "name": "City of Edina",
        "state": "MN",
        "requirements": {
            "permit_validity_months": 6,
            "inspection_sequence": {
                "Footing": [],
                "Foundation": ["Footing"],
                "Framing": ["Foundation"],
                "Rough Plumbing": ["Framing"],
                "Rough Electrical": ["Framing"],
                "Insulation": ["Rough Plumbing", "Rough Electrical"],
                "Final": ["Insulation"]
            },
            "required_documents": {
                "Framing": ["structural_plans", "truss_plans"],
                "Final": ["as_built_plans"]
            },
            "fees": {
                "residential_building_permit_base": 180.00,
                "residential_inspection_base": 60.00,
                "commercial_building_permit_base": 360.00,
                "commercial_inspection_base": 95.00
            },
            "contact": {
                "phone": "952-927-8861",
                "email": "permits@edinamn.gov",
                "address": "4801 W 50th St, Edina, MN 55424"
            }
        }
    },
    {
        "name": "Hennepin County",
        "state": "MN",
        "requirements": {
            "permit_validity_months": 6,
            "inspection_sequence": {
                "Footing": [],
                "Foundation": ["Footing"],
                "Framing": ["Foundation"],
                "Final": ["Framing"]
            },
            "required_documents": {
                "Framing": ["structural_plans"]
            },
            "fees": {
                "residential_building_permit_base": 150.00,
                "residential_inspection_base": 50.00,
                "commercial_building_permit_base": 300.00,
                "commercial_inspection_base": 75.00
            },
            "contact": {
                "phone": "612-348-3000",
                "email": "permits@hennepin.us",
                "address": "A-600 Government Center, Minneapolis, MN 55487"
            }
        }
    }
]


async def seed_jurisdictions():
    """Seed jurisdictions table with Minnesota jurisdictions"""
    
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        try:
            print("=" * 80)
            print("SEED JURISDICTIONS - PHASE A.4")
            print("=" * 80)
            print()
            
            # Check if jurisdictions table exists
            check_table = text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'jurisdictions'
                );
            """)
            
            result = await session.execute(check_table)
            table_exists = result.scalar()
            
            if not table_exists:
                print("❌ ERROR: jurisdictions table does not exist!")
                print("   Run migrations first: alembic upgrade head")
                return
            
            print("✅ jurisdictions table found")
            print()
            
            # Check existing jurisdictions
            check_existing = text("""
                SELECT name, state FROM jurisdictions ORDER BY name;
            """)
            result = await session.execute(check_existing)
            existing = result.fetchall()
            
            if existing:
                print(f"📋 Found {len(existing)} existing jurisdictions:")
                for jurisdiction in existing:
                    print(f"   - {jurisdiction[0]}, {jurisdiction[1]}")
                print()
                
                response = input("⚠️  Clear existing jurisdictions and reseed? (yes/no): ")
                if response.lower() == 'yes':
                    delete_all = text("DELETE FROM jurisdictions;")
                    await session.execute(delete_all)
                    await session.commit()
                    print("✅ Cleared existing jurisdictions")
                    print()
                else:
                    print("❌ Seeding cancelled")
                    return
            
            # Insert jurisdictions
            print(f"📝 Seeding {len(JURISDICTIONS)} jurisdictions...")
            print()
            
            for idx, jurisdiction in enumerate(JURISDICTIONS, 1):
                insert_query = text("""
                    INSERT INTO jurisdictions (name, state, requirements, created_at, updated_at)
                    VALUES (:name, :state, :requirements, :created_at, :updated_at)
                    RETURNING id, name, state;
                """)
                
                result = await session.execute(
                    insert_query,
                    {
                        "name": jurisdiction["name"],
                        "state": jurisdiction["state"],
                        "requirements": json.dumps(jurisdiction["requirements"]),
                        "created_at": datetime.now(timezone.utc),
                        "updated_at": datetime.now(timezone.utc)
                    }
                )
                
                inserted = result.fetchone()
                
                print(f"{idx}. ✅ {inserted[1]}, {inserted[2]}")
                print(f"     - Permit validity: {jurisdiction['requirements']['permit_validity_months']} months")
                print(f"     - Inspection types: {len(jurisdiction['requirements']['inspection_sequence'])}")
                print(f"     - Contact: {jurisdiction['requirements']['contact']['phone']}")
                print()
            
            await session.commit()
            
            print("=" * 80)
            print("✅ JURISDICTION SEEDING COMPLETE!")
            print("=" * 80)
            print()
            print(f"Seeded {len(JURISDICTIONS)} jurisdictions for Minnesota")
            print()
            print("Next steps:")
            print("  1. Verify jurisdictions: SELECT name, state FROM jurisdictions;")
            print("  2. Test AI precheck with jurisdiction rules")
            print("  3. Move to Phase B: API & Business Flows")
            
        except Exception as e:
            print(f"❌ ERROR: {e}")
            await session.rollback()
            raise
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_jurisdictions())
