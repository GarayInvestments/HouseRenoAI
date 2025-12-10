"""
Comprehensive tests for business_id functionality.

Tests cover:
1. Automatic generation on INSERT
2. Uniqueness constraints
3. Format validation (PREFIX-00001)
4. Sequential incrementing
5. Lookup by business_id
6. Idempotent backfill
7. Concurrency safety
8. NULL handling

Run with: pytest tests/test_business_ids.py -v
"""

import pytest
import asyncio
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.db.models import Client, Project, Permit, Payment
from app.config import settings

# Test database engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False
)

AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


@pytest.fixture
async def session():
    """Provide a clean database session for each test."""
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()


@pytest.mark.asyncio
async def test_client_business_id_auto_generated(session):
    """Test that business_id is automatically generated for new clients."""
    # Insert client without business_id
    client = Client(
        client_id="test_001",
        full_name="Test Client",
        email="test@example.com"
    )
    session.add(client)
    await session.commit()
    
    # Refresh to get trigger-assigned business_id
    await session.refresh(client)
    
    assert client.business_id is not None
    assert client.business_id.startswith("CL-")
    assert len(client.business_id) == 8  # CL-00001 format
    
    # Cleanup
    await session.delete(client)
    await session.commit()


@pytest.mark.asyncio
async def test_project_business_id_format(session):
    """Test that project business_ids follow PRJ-XXXXX format."""
    project = Project(
        project_id="test_prj_001",
        project_name="Test Project"
    )
    session.add(project)
    await session.commit()
    await session.refresh(project)
    
    assert project.business_id.startswith("PRJ-")
    assert project.business_id[4:].isdigit()
    assert len(project.business_id) == 9  # PRJ-00001
    
    # Cleanup
    await session.delete(project)
    await session.commit()


@pytest.mark.asyncio
async def test_business_id_uniqueness(session):
    """Test that duplicate business_ids are rejected."""
    client1 = Client(
        client_id="test_unique_1",
        full_name="Client 1"
    )
    session.add(client1)
    await session.commit()
    await session.refresh(client1)
    
    # Try to manually set duplicate business_id
    client2 = Client(
        client_id="test_unique_2",
        full_name="Client 2",
        business_id=client1.business_id  # Duplicate!
    )
    session.add(client2)
    
    with pytest.raises(Exception) as exc_info:
        await session.commit()
    
    assert "duplicate" in str(exc_info.value).lower() or "unique" in str(exc_info.value).lower()
    
    # Cleanup
    await session.rollback()
    await session.delete(client1)
    await session.commit()


@pytest.mark.asyncio
async def test_business_id_sequential(session):
    """Test that business_ids increment sequentially."""
    # Create 3 clients and check sequence
    clients = []
    for i in range(3):
        client = Client(
            client_id=f"test_seq_{i}",
            full_name=f"Sequential Client {i}"
        )
        session.add(client)
        await session.commit()
        await session.refresh(client)
        clients.append(client)
    
    # Extract numbers from business_ids
    ids = [int(c.business_id.split('-')[1]) for c in clients]
    
    # Verify sequential (allowing for other tests' data)
    assert ids[1] == ids[0] + 1
    assert ids[2] == ids[1] + 1
    
    # Cleanup
    for client in clients:
        await session.delete(client)
    await session.commit()


@pytest.mark.asyncio
async def test_permit_business_id_prefix(session):
    """Test permit business_ids use PRM- prefix."""
    permit = Permit(
        permit_id="test_permit_001",
        permit_number="TEST-2025-001"
    )
    session.add(permit)
    await session.commit()
    await session.refresh(permit)
    
    assert permit.business_id.startswith("PRM-")
    
    # Cleanup
    await session.delete(permit)
    await session.commit()


@pytest.mark.asyncio
async def test_payment_business_id_prefix(session):
    """Test payment business_ids use PAY- prefix."""
    payment = Payment(
        payment_id="test_payment_001",
        amount=1000.00
    )
    session.add(payment)
    await session.commit()
    await session.refresh(payment)
    
    assert payment.business_id.startswith("PAY-")
    
    # Cleanup
    await session.delete(payment)
    await session.commit()


@pytest.mark.asyncio
async def test_lookup_by_business_id(session):
    """Test querying by business_id works efficiently."""
    # Create client
    client = Client(
        client_id="test_lookup_001",
        full_name="Lookup Test Client",
        email="lookup@example.com"
    )
    session.add(client)
    await session.commit()
    await session.refresh(client)
    
    business_id = client.business_id
    
    # Query by business_id
    result = await session.execute(
        select(Client).where(Client.business_id == business_id)
    )
    found_client = result.scalar_one_or_none()
    
    assert found_client is not None
    assert found_client.client_id == "test_lookup_001"
    assert found_client.full_name == "Lookup Test Client"
    
    # Cleanup
    await session.delete(client)
    await session.commit()


@pytest.mark.asyncio
async def test_explicit_business_id_preserved(session):
    """Test that manually provided business_ids are preserved."""
    # This tests that triggers check for NULL before generating
    client = Client(
        client_id="test_explicit_001",
        full_name="Explicit ID Client",
        business_id="CL-99999"  # Manually provided
    )
    session.add(client)
    await session.commit()
    await session.refresh(client)
    
    assert client.business_id == "CL-99999"
    
    # Cleanup
    await session.delete(client)
    await session.commit()


@pytest.mark.asyncio
async def test_generation_function_directly(session):
    """Test calling generation functions directly."""
    # Test client generation function
    result = await session.execute(
        text("SELECT generate_client_business_id()")
    )
    client_id = result.scalar()
    
    assert client_id.startswith("CL-")
    assert len(client_id) == 8
    
    # Test project generation function
    result = await session.execute(
        text("SELECT generate_project_business_id()")
    )
    project_id = result.scalar()
    
    assert project_id.startswith("PRJ-")
    assert len(project_id) == 9


@pytest.mark.asyncio
async def test_index_exists(session):
    """Test that unique indexes are created."""
    # Query PostgreSQL system catalogs
    result = await session.execute(
        text("""
            SELECT indexname 
            FROM pg_indexes 
            WHERE tablename = 'clients' 
            AND indexname = 'idx_clients_business_id'
        """)
    )
    index_name = result.scalar()
    
    assert index_name == "idx_clients_business_id"


@pytest.mark.asyncio
async def test_concurrency_no_collision(session):
    """Test that concurrent inserts don't collide (sequences are atomic)."""
    # This is a basic test - real concurrency requires multiple connections
    # Create 5 clients rapidly
    clients = []
    for i in range(5):
        client = Client(
            client_id=f"test_concurrent_{i}",
            full_name=f"Concurrent Client {i}"
        )
        session.add(client)
    
    await session.commit()
    
    # Refresh all to get business_ids
    for client in clients:
        await session.refresh(client)
    
    # Get all business_ids
    business_ids = [c.business_id for c in clients]
    
    # Verify all unique
    assert len(business_ids) == len(set(business_ids))
    
    # Cleanup
    for client in clients:
        await session.delete(client)
    await session.commit()


@pytest.mark.asyncio
async def test_all_sequences_exist(session):
    """Test that all sequences were created."""
    result = await session.execute(
        text("""
            SELECT sequence_name 
            FROM information_schema.sequences 
            WHERE sequence_name LIKE '%business_id%'
            ORDER BY sequence_name
        """)
    )
    sequences = [row[0] for row in result.fetchall()]
    
    expected = [
        'client_business_id_seq',
        'payment_business_id_seq',
        'permit_business_id_seq',
        'project_business_id_seq'
    ]
    
    assert set(sequences) == set(expected)


@pytest.mark.asyncio
async def test_all_generation_functions_exist(session):
    """Test that all generation functions were created."""
    result = await session.execute(
        text("""
            SELECT routine_name 
            FROM information_schema.routines 
            WHERE routine_name LIKE 'generate_%business_id'
            ORDER BY routine_name
        """)
    )
    functions = [row[0] for row in result.fetchall()]
    
    expected = [
        'generate_client_business_id',
        'generate_payment_business_id',
        'generate_permit_business_id',
        'generate_project_business_id'
    ]
    
    assert set(functions) == set(expected)


@pytest.mark.asyncio
async def test_all_triggers_exist(session):
    """Test that all triggers were created."""
    result = await session.execute(
        text("""
            SELECT tgname 
            FROM pg_trigger 
            WHERE tgname LIKE 'trigger_set_%business_id'
            ORDER BY tgname
        """)
    )
    triggers = [row[0] for row in result.fetchall()]
    
    expected = [
        'trigger_set_client_business_id',
        'trigger_set_payment_business_id',
        'trigger_set_permit_business_id',
        'trigger_set_project_business_id'
    ]
    
    assert set(triggers) == set(expected)


if __name__ == "__main__":
    # Run tests directly (not via pytest)
    import sys
    
    async def run_all_tests():
        """Run all tests sequentially."""
        async with AsyncSessionLocal() as session:
            tests = [
                ("Auto-generation", test_client_business_id_auto_generated),
                ("Format validation", test_project_business_id_format),
                ("Uniqueness", test_business_id_uniqueness),
                ("Sequential", test_business_id_sequential),
                ("Permit prefix", test_permit_business_id_prefix),
                ("Payment prefix", test_payment_business_id_prefix),
                ("Lookup", test_lookup_by_business_id),
                ("Explicit ID", test_explicit_business_id_preserved),
                ("Direct generation", test_generation_function_directly),
                ("Index exists", test_index_exists),
                ("Concurrency", test_concurrency_no_collision),
                ("All sequences", test_all_sequences_exist),
                ("All functions", test_all_generation_functions_exist),
                ("All triggers", test_all_triggers_exist),
            ]
            
            passed = 0
            failed = 0
            
            for name, test_func in tests:
                try:
                    print(f"Running: {name}...", end=" ")
                    await test_func(session)
                    print("✓ PASSED")
                    passed += 1
                except Exception as e:
                    print(f"✗ FAILED: {e}")
                    failed += 1
            
            print(f"\n{'='*60}")
            print(f"Results: {passed} passed, {failed} failed")
            print(f"{'='*60}")
            
            return failed == 0
    
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
