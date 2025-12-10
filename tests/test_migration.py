"""
Test migration script functionality.

Purpose: Validate migration script behavior in dry-run mode.
Usage: pytest tests/test_migration.py -v
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))


@pytest.fixture
def mock_google_service():
    """Mock Google Sheets service."""
    service = MagicMock()
    
    # Mock get methods
    service.get_clients_data = AsyncMock(return_value=[
        {"Client ID": "12345678", "Full Name": "Test Client", "Email": "test@example.com"},
        {"Client ID": "87654321", "Full Name": "Another Client", "Email": "another@example.com"},
    ])
    
    service.get_projects_data = AsyncMock(return_value=[
        {"Project ID": "proj1", "Client ID": "12345678", "Project Name": "Test Project", "Status": "Active"},
    ])
    
    service.get_permits_data = AsyncMock(return_value=[
        {"Permit ID": "permit1", "Project ID": "proj1", "Permit Number": "BP-001", "Status": "Pending"},
    ])
    
    service.get_payments_data = AsyncMock(return_value=[])
    
    return service


@pytest.fixture
def mock_db_service():
    """Mock DB service."""
    service = MagicMock()
    
    service.initialize = AsyncMock()
    service.upsert_client_from_sheet_row = AsyncMock(return_value="12345678")
    service.upsert_project_from_sheet_row = AsyncMock(return_value="proj1")
    service.upsert_permit_from_sheet_row = AsyncMock(return_value="permit1")
    
    return service


@pytest.mark.asyncio
async def test_migration_dry_run(mock_google_service, mock_db_service):
    """Test that dry-run mode doesn't modify database."""
    with patch('scripts.migrate_sheets_to_db.google_service', mock_google_service), \
         patch('scripts.migrate_sheets_to_db.db_service', mock_db_service):
        
        from scripts.migrate_sheets_to_db import SheetsMigration
        
        migration = SheetsMigration(dry_run=True)
        success = await migration.migrate_clients()
        
        assert success is True
        # Verify no DB writes in dry-run
        mock_db_service.upsert_client_from_sheet_row.assert_not_called()
        
        # Verify Sheets were read
        mock_google_service.get_clients_data.assert_called_once()


@pytest.mark.asyncio
async def test_migration_stats_tracking():
    """Test that migration tracks statistics correctly."""
    from scripts.migrate_sheets_to_db import MigrationStats
    
    stats = MigrationStats()
    stats.add_entity("clients")
    stats.set_sheets_count("clients", 10)
    
    for i in range(8):
        stats.record_success("clients")
    
    stats.record_error("clients")
    stats.record_skip("clients")
    
    assert stats.entities["clients"]["sheets_count"] == 10
    assert stats.entities["clients"]["migrated"] == 8
    assert stats.entities["clients"]["errors"] == 1
    assert stats.entities["clients"]["skipped"] == 1
    
    report = stats.generate_report()
    assert "MIGRATION REPORT" in report
    assert "CLIENTS:" in report
    assert "Migrated:    8" in report


@pytest.mark.asyncio
async def test_migration_handles_errors(mock_google_service):
    """Test that migration handles errors gracefully."""
    # Mock DB service that fails
    failing_db_service = MagicMock()
    failing_db_service.initialize = AsyncMock()
    failing_db_service.upsert_client_from_sheet_row = AsyncMock(
        side_effect=Exception("DB connection failed")
    )
    
    with patch('scripts.migrate_sheets_to_db.google_service', mock_google_service), \
         patch('scripts.migrate_sheets_to_db.db_service', failing_db_service):
        
        from scripts.migrate_sheets_to_db import SheetsMigration
        
        migration = SheetsMigration(dry_run=False)
        success = await migration.migrate_clients()
        
        # Should handle errors and continue
        assert migration.stats.entities["clients"]["errors"] > 0


@pytest.mark.asyncio
async def test_migration_validates_referential_integrity(mock_google_service, mock_db_service):
    """Test that migration validates client references in projects."""
    with patch('scripts.migrate_sheets_to_db.google_service', mock_google_service), \
         patch('scripts.migrate_sheets_to_db.db_service', mock_db_service):
        
        # Mock AsyncSessionLocal to return valid client IDs
        with patch('scripts.migrate_sheets_to_db.AsyncSessionLocal') as mock_session:
            mock_session_instance = AsyncMock()
            mock_session.return_value.__aenter__.return_value = mock_session_instance
            
            # Mock execute to return client IDs
            mock_result = MagicMock()
            mock_result.all.return_value = [("12345678",), ("87654321",)]
            mock_session_instance.execute = AsyncMock(return_value=mock_result)
            
            from scripts.migrate_sheets_to_db import SheetsMigration
            
            migration = SheetsMigration(dry_run=False)
            success = await migration.migrate_projects()
            
            # Should have checked for valid client IDs
            mock_session_instance.execute.assert_called()
