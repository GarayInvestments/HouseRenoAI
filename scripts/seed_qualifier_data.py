"""
Seed initial qualifier compliance data for Phase Q.1

Creates:
- 2 Licensed Businesses (House Renovators, 2States Carolinas LLC)
- 2 Qualifiers (Steve Garay, Daniela Molina Rodriguez)
- 2 Active relationships with proper date bounds

Run after Phase Q.1 migration: python scripts/seed_qualifier_data.py
"""

import asyncio
import sys
from datetime import date, datetime
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.db.session import AsyncSessionLocal


async def seed_qualifier_data():
    """Seed initial qualifier compliance data"""
    
    async with AsyncSessionLocal() as session:
        print("🌱 Seeding qualifier compliance data...\n")
        
        # 1. Create Licensed Businesses
        print("📋 Creating Licensed Businesses...")
        
        # House Renovators LLC
        hr_result = await session.execute(text("""
            INSERT INTO licensed_businesses (
                business_name,
                legal_name,
                license_number,
                license_type,
                license_status,
                license_issue_date,
                active
            ) VALUES (
                'House Renovators',
                'House Renovators LLC',
                '85538',
                'Unlimited',
                'active',
                '2010-01-01',
                true
            )
            RETURNING id, business_id;
        """))
        hr_data = hr_result.fetchone()
        hr_id = hr_data[0]
        hr_business_id = hr_data[1]
        print(f"  ✅ House Renovators LLC created: {hr_business_id} (License: 85538)")
        
        # 2 States Carolinas LLC
        states_result = await session.execute(text("""
            INSERT INTO licensed_businesses (
                business_name,
                legal_name,
                license_number,
                license_type,
                license_status,
                license_issue_date,
                active
            ) VALUES (
                '2States Carolinas LLC',
                '2States Carolinas LLC',
                '107618',
                'Unlimited',
                'active',
                '2018-01-01',
                true
            )
            RETURNING id, business_id;
        """))
        states_data = states_result.fetchone()
        states_id = states_data[0]
        states_business_id = states_data[1]
        print(f"  ✅ 2States Carolinas LLC created: {states_business_id} (License: 107618)\n")
        
        # 2. Get user IDs for Steve and Daniela
        print("👥 Looking up user accounts...")
        
        steve_result = await session.execute(text("""
            SELECT id FROM users WHERE email ILIKE '%steve%' OR full_name ILIKE '%steve%garay%' LIMIT 1;
        """))
        steve_user = steve_result.fetchone()
        
        daniela_result = await session.execute(text("""
            SELECT id FROM users WHERE email ILIKE '%daniela%' OR full_name ILIKE '%daniela%' LIMIT 1;
        """))
        daniela_user = daniela_result.fetchone()
        
        if not steve_user:
            print("  ⚠️  Steve Garay user not found - creating placeholder...")
            steve_result = await session.execute(text("""
                INSERT INTO users (email, full_name, role, is_active)
                VALUES ('steve@houserenovators.com', 'Steve Garay', 'admin', true)
                RETURNING id;
            """))
            steve_user_id = steve_result.fetchone()[0]
        else:
            steve_user_id = steve_user[0]
            print(f"  ✅ Found Steve Garay user: {steve_user_id}")
        
        if not daniela_user:
            print("  ⚠️  Daniela user not found - creating placeholder...")
            daniela_result = await session.execute(text("""
                INSERT INTO users (email, full_name, role, is_active)
                VALUES ('daniela@houserenovators.com', 'Daniela Molina Rodriguez', 'admin', true)
                RETURNING id;
            """))
            daniela_user_id = daniela_result.fetchone()[0]
        else:
            daniela_user_id = daniela_user[0]
            print(f"  ✅ Found Daniela Molina Rodriguez user: {daniela_user_id}\n")
        
        # 3. Create Qualifiers
        print("🎓 Creating Qualifiers...")
        
        # Steve Garay
        steve_qual_result = await session.execute(text("""
            INSERT INTO qualifiers (
                user_id,
                full_name,
                qualifier_id_number,
                license_type,
                license_status,
                license_issue_date,
                max_licenses_allowed
            ) VALUES (
                :user_id,
                'Steve Garay',
                '59510',
                'Unlimited',
                'active',
                '2008-01-01',
                2
            )
            RETURNING id, qualifier_id;
        """), {"user_id": steve_user_id})
        steve_qual_data = steve_qual_result.fetchone()
        steve_qual_id = steve_qual_data[0]
        steve_qual_business_id = steve_qual_data[1]
        print(f"  ✅ Steve Garay qualifier created: {steve_qual_business_id} (Qualifier ID: 59510)")
        
        # Daniela Molina Rodriguez
        daniela_qual_result = await session.execute(text("""
            INSERT INTO qualifiers (
                user_id,
                full_name,
                qualifier_id_number,
                license_type,
                license_status,
                license_issue_date,
                max_licenses_allowed
            ) VALUES (
                :user_id,
                'Daniela Molina Rodriguez',
                '102579',
                'Unlimited',
                'active',
                '2015-01-01',
                2
            )
            RETURNING id, qualifier_id;
        """), {"user_id": daniela_user_id})
        daniela_qual_data = daniela_qual_result.fetchone()
        daniela_qual_id = daniela_qual_data[0]
        daniela_qual_business_id = daniela_qual_data[1]
        print(f"  ✅ Daniela Molina Rodriguez qualifier created: {daniela_qual_business_id} (Qualifier ID: 102579)\n")
        
        # 4. Update users.is_qualifier flag
        print("🔧 Updating user qualifier flags...")
        await session.execute(text("""
            UPDATE users SET is_qualifier = true WHERE id IN (:steve_id, :daniela_id);
        """), {"steve_id": steve_user_id, "daniela_id": daniela_user_id})
        print("  ✅ User qualifier flags set\n")
        
        # 5. Create Licensed Business Qualifier relationships
        print("🔗 Creating Licensed Business ↔ Qualifier relationships...")
        
        # Steve → House Renovators (primary, since 2010)
        await session.execute(text("""
            INSERT INTO licensed_business_qualifiers (
                licensed_business_id,
                qualifier_id,
                relationship_type,
                start_date,
                end_date
            ) VALUES (
                :business_id,
                :qualifier_id,
                'qualification',
                '2010-01-01',
                NULL
            );
        """), {"business_id": hr_id, "qualifier_id": steve_qual_id})
        print(f"  ✅ Steve Garay → House Renovators (since 2010, active)")
        
        # Daniela → 2States Carolinas (primary, since 2018)
        await session.execute(text("""
            INSERT INTO licensed_business_qualifiers (
                licensed_business_id,
                qualifier_id,
                relationship_type,
                start_date,
                end_date
            ) VALUES (
                :business_id,
                :qualifier_id,
                'qualification',
                '2018-01-01',
                NULL
            );
        """), {"business_id": states_id, "qualifier_id": daniela_qual_id})
        print(f"  ✅ Daniela Molina Rodriguez → 2States Carolinas LLC (since 2018, active)\n")
        
        # 6. Update denormalized qualifying_user_id (for UI convenience)
        print("🎨 Updating denormalized UI fields...")
        await session.execute(text("""
            UPDATE licensed_businesses 
            SET qualifying_user_id = :steve_id 
            WHERE id = :hr_id;
        """), {"steve_id": steve_user_id, "hr_id": hr_id})
        
        await session.execute(text("""
            UPDATE licensed_businesses 
            SET qualifying_user_id = :daniela_id 
            WHERE id = :states_id;
        """), {"daniela_id": daniela_user_id, "states_id": states_id})
        print("  ✅ UI convenience fields updated\n")
        
        # Commit transaction
        await session.commit()
        
        # 7. Verify capacity enforcement
        print("✅ Testing capacity enforcement trigger...")
        try:
            # Try to add a 3rd business to Steve (should fail)
            await session.execute(text("""
                INSERT INTO licensed_businesses (business_name, legal_name, license_number, license_type, license_status)
                VALUES ('Test Business', 'Test LLC', '99999', 'Limited', 'active')
                RETURNING id;
            """))
            test_business = (await session.execute(text("SELECT id FROM licensed_businesses WHERE license_number = '99999'"))).fetchone()
            
            if test_business:
                await session.execute(text("""
                    INSERT INTO licensed_business_qualifiers (
                        licensed_business_id,
                        qualifier_id,
                        relationship_type,
                        start_date
                    ) VALUES (
                        :business_id,
                        :qualifier_id,
                        'qualification',
                        CURRENT_DATE
                    );
                """), {"business_id": test_business[0], "qualifier_id": steve_qual_id})
                
                print("  ⚠️  WARNING: Capacity trigger did NOT block 3rd business assignment!")
        except Exception as e:
            if "capacity exceeded" in str(e).lower():
                print(f"  ✅ Capacity trigger working: {str(e)}")
            else:
                print(f"  ⚠️  Unexpected error: {e}")
        
        await session.rollback()  # Roll back test transaction
        
        print("\n" + "="*80)
        print("🎉 Qualifier compliance data seeded successfully!")
        print("="*80)
        print("\n📊 Summary:")
        print(f"  • Licensed Businesses: 2 (House Renovators, 2States Carolinas LLC)")
        print(f"  • Qualifiers: 2 (Steve Garay, Daniela Molina Rodriguez)")
        print(f"  • Active Relationships: 2")
        print(f"  • Capacity Available: Steve (1/2), Daniela (1/2)")
        print("\n📋 Next Steps:")
        print("  1. Run: python scripts/backfill_project_qualifiers.py")
        print("  2. Verify: Check projects have licensed_business_id and qualifier_id")
        print("  3. Test: Try creating oversight actions, test cutoff enforcement")


if __name__ == "__main__":
    asyncio.run(seed_qualifier_data())
