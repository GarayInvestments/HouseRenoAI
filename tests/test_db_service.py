"""
Unit tests for DB service.

Purpose: Test database operations with in-memory SQLite for speed.
Usage: pytest tests/test_db_service.py -v
"""

import pytest
import asyncio
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select

from app.db.models import Base, Client, Project, Permit, Payment
from app.services.db_service import DBService


@pytest.fixture(scope="function")
async def test_engine():
    """Create test engine with in-memory SQLite."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
    )
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    await engine.dispose()


@pytest.fixture(scope="function")
async def test_session(test_engine):
    """Create test session."""
    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with async_session() as session:
        yield session


@pytest.fixture(scope="function")
async def db_service_test(test_engine):
    """Create DB service for testing."""
    # Override session factory to use test engine
    from app.db import session as session_module
    
    original_sessionmaker = session_module.AsyncSessionLocal
    
    session_module.AsyncSessionLocal = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    service = DBService()
    await service.initialize()
    
    yield service
    
    # Restore original
    session_module.AsyncSessionLocal = original_sessionmaker


class TestClientOperations:
    """Test client CRUD operations."""
    
    @pytest.mark.asyncio
    async def test_upsert_client_creates_new(self, db_service_test):
        """Test creating a new client."""
        row_data = {
            "Client ID": "12345678",
            "Full Name": "John Doe",
            "Email": "john@example.com",
            "Phone": "555-1234",
            "Address": "123 Main St",
            "Status": "Active"
        }
        
        client_id = await db_service_test.upsert_client_from_sheet_row(row_data)
        assert client_id == "12345678"
        
        # Verify it was created
        client = await db_service_test.get_client_by_id(client_id)
        assert client is not None
        assert client["Full Name"] == "John Doe"
        assert client["Email"] == "john@example.com"
    
    @pytest.mark.asyncio
    async def test_upsert_client_updates_existing(self, db_service_test):
        """Test updating an existing client."""
        # Create initial client
        row_data = {
            "Client ID": "12345678",
            "Full Name": "John Doe",
            "Email": "john@example.com"
        }
        await db_service_test.upsert_client_from_sheet_row(row_data)
        
        # Update with new data
        updated_data = {
            "Client ID": "12345678",
            "Full Name": "John Doe Updated",
            "Email": "john.updated@example.com",
            "Phone": "555-9999"
        }
        await db_service_test.upsert_client_from_sheet_row(updated_data)
        
        # Verify update
        client = await db_service_test.get_client_by_id("12345678")
        assert client["Full Name"] == "John Doe Updated"
        assert client["Email"] == "john.updated@example.com"
        assert client["Phone"] == "555-9999"
    
    @pytest.mark.asyncio
    async def test_get_clients_data(self, db_service_test):
        """Test retrieving all clients."""
        # Create multiple clients
        clients = [
            {"Client ID": "11111111", "Full Name": "Alice", "Email": "alice@example.com"},
            {"Client ID": "22222222", "Full Name": "Bob", "Email": "bob@example.com"},
            {"Client ID": "33333333", "Full Name": "Charlie", "Email": "charlie@example.com"},
        ]
        
        for client_data in clients:
            await db_service_test.upsert_client_from_sheet_row(client_data)
        
        # Retrieve all
        all_clients = await db_service_test.get_clients_data()
        assert len(all_clients) == 3
        
        names = [c["Full Name"] for c in all_clients]
        assert "Alice" in names
        assert "Bob" in names
        assert "Charlie" in names
    
    @pytest.mark.asyncio
    async def test_get_clients_data_with_limit(self, db_service_test):
        """Test retrieving clients with limit."""
        # Create 5 clients
        for i in range(5):
            await db_service_test.upsert_client_from_sheet_row({
                "Client ID": f"client_{i}",
                "Full Name": f"Client {i}",
                "Email": f"client{i}@example.com"
            })
        
        # Get only 2
        limited = await db_service_test.get_clients_data(limit=2)
        assert len(limited) == 2


class TestProjectOperations:
    """Test project CRUD operations."""
    
    @pytest.mark.asyncio
    async def test_upsert_project(self, db_service_test):
        """Test creating a project."""
        row_data = {
            "Project ID": "proj123",
            "Client ID": "client123",
            "Project Name": "Kitchen Remodel",
            "Address": "456 Oak St",
            "Status": "Active",
            "Budget": "50000.00"
        }
        
        project_id = await db_service_test.upsert_project_from_sheet_row(row_data)
        assert project_id == "proj123"
        
        project = await db_service_test.get_project_by_id(project_id)
        assert project["Project Name"] == "Kitchen Remodel"
        assert project["Budget"] == 50000.0
    
    @pytest.mark.asyncio
    async def test_get_projects_data(self, db_service_test):
        """Test retrieving all projects."""
        projects = [
            {"Project ID": "p1", "Project Name": "Project 1", "Status": "Active"},
            {"Project ID": "p2", "Project Name": "Project 2", "Status": "Complete"},
        ]
        
        for proj in projects:
            await db_service_test.upsert_project_from_sheet_row(proj)
        
        all_projects = await db_service_test.get_projects_data()
        assert len(all_projects) == 2


class TestPermitOperations:
    """Test permit CRUD operations."""
    
    @pytest.mark.asyncio
    async def test_upsert_permit(self, db_service_test):
        """Test creating a permit."""
        row_data = {
            "Permit ID": "permit123",
            "Project ID": "proj123",
            "Permit Number": "BP-2025-001",
            "Permit Type": "Building",
            "Status": "Pending"
        }
        
        permit_id = await db_service_test.upsert_permit_from_sheet_row(row_data)
        assert permit_id == "permit123"
        
        permit = await db_service_test.get_permit_by_id(permit_id)
        assert permit["Permit Number"] == "BP-2025-001"
        assert permit["Status"] == "Pending"


class TestCaching:
    """Test TTL caching functionality."""
    
    @pytest.mark.asyncio
    async def test_cache_hit(self, db_service_test):
        """Test that cache returns same data."""
        row_data = {"Client ID": "cache123", "Full Name": "Cached Client", "Email": "cached@example.com"}
        await db_service_test.upsert_client_from_sheet_row(row_data)
        
        # First call - cache miss
        client1 = await db_service_test.get_client_by_id("cache123")
        
        # Second call - should hit cache
        client2 = await db_service_test.get_client_by_id("cache123")
        
        assert client1 == client2
    
    @pytest.mark.asyncio
    async def test_cache_invalidation(self, db_service_test):
        """Test that cache is invalidated on update."""
        row_data = {"Client ID": "cache456", "Full Name": "Original", "Email": "original@example.com"}
        await db_service_test.upsert_client_from_sheet_row(row_data)
        
        # Get client (cache it)
        client1 = await db_service_test.get_client_by_id("cache456")
        assert client1["Full Name"] == "Original"
        
        # Update client (should invalidate cache)
        updated_data = {"Client ID": "cache456", "Full Name": "Updated", "Email": "updated@example.com"}
        await db_service_test.upsert_client_from_sheet_row(updated_data)
        
        # Get again (should fetch fresh data)
        client2 = await db_service_test.get_client_by_id("cache456")
        assert client2["Full Name"] == "Updated"


class TestHelperMethods:
    """Test helper methods."""
    
    def test_generate_id(self):
        """Test ID generation."""
        service = DBService()
        
        id1 = service._generate_id("test123")
        id2 = service._generate_id("test123")
        id3 = service._generate_id("different")
        
        # Same input = same ID
        assert id1 == id2
        
        # Different input = different ID
        assert id1 != id3
        
        # ID is 8 characters
        assert len(id1) == 8
    
    def test_parse_numeric(self):
        """Test numeric parsing."""
        service = DBService()
        
        assert service._parse_numeric("100.50") == 100.5
        assert service._parse_numeric("$1,234.56") == 1234.56
        assert service._parse_numeric("") is None
        assert service._parse_numeric(None) is None
        assert service._parse_numeric("invalid") is None
    
    def test_parse_date(self):
        """Test date parsing."""
        service = DBService()
        
        # ISO format
        result = service._parse_date("2025-12-10T10:30:00")
        assert result is not None
        assert isinstance(result, datetime)
        
        # Empty/None
        assert service._parse_date("") is None
        assert service._parse_date(None) is None
