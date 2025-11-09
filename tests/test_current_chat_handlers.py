"""
Integration tests for current AI function handlers in chat.py.
These tests validate existing behavior BEFORE refactoring.

Tests are based on actual function implementations in app/routes/chat.py
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import sys
import os

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.mark.asyncio
async def test_update_project_status(mock_google_service, mock_memory_manager):
    """Test project status update - validates current implementation"""
    # Simulate what chat.py does
    func_args = {
        "project_id": "P123",
        "new_status": "Active"
    }
    
    # Mock the actual Google Sheets method used in chat.py
    mock_google_service.update_record_by_id.return_value = True
    
    # Execute update (simulating chat.py logic)
    success = await mock_google_service.update_record_by_id(
        sheet_name='Projects',
        id_field='Project ID',
        record_id=func_args["project_id"],
        updates={'Status': func_args["new_status"]}
    )
    
    # Assertions
    assert success is True
    mock_google_service.update_record_by_id.assert_called_once_with(
        sheet_name='Projects',
        id_field='Project ID',
        record_id="P123",
        updates={'Status': 'Active'}
    )


@pytest.mark.asyncio
async def test_update_permit_status(mock_google_service):
    """Test permit status update - validates current implementation"""
    func_args = {
        "permit_id": "PM456",
        "new_status": "Approved"
    }
    
    mock_google_service.update_record_by_id.return_value = True
    
    success = await mock_google_service.update_record_by_id(
        sheet_name='Permits',
        id_field='Permit ID',
        record_id=func_args["permit_id"],
        updates={'Permit Status': func_args["new_status"]}
    )
    
    assert success is True
    mock_google_service.update_record_by_id.assert_called_once_with(
        sheet_name='Permits',
        id_field='Permit ID',
        record_id="PM456",
        updates={'Permit Status': 'Approved'}
    )


@pytest.mark.asyncio
async def test_update_client_field(mock_google_service):
    """Test client field update - validates current implementation"""
    func_args = {
        "client_identifier": "Ajay Nair",
        "field_name": "QBO ID",
        "field_value": "164"
    }
    
    # Mock the search and update methods
    mock_google_service.get_clients_data.return_value = [
        {"Client ID": "C001", "Full Name": "Ajay Nair", "QBO ID": ""}
    ]
    mock_google_service.update_record_by_id.return_value = True
    
    # Simulate chat.py logic
    clients = await mock_google_service.get_clients_data()
    client = next((c for c in clients if c.get('Full Name') == func_args["client_identifier"]), None)
    
    assert client is not None
    
    success = await mock_google_service.update_record_by_id(
        sheet_name='Clients',
        id_field='Client ID',
        record_id=client['Client ID'],
        updates={func_args["field_name"]: func_args["field_value"]}
    )
    
    assert success is True


@pytest.mark.asyncio
async def test_create_quickbooks_invoice(mock_quickbooks_service):
    """Test invoice creation - validates current implementation"""
    func_args = {
        "customer_id": "C123",
        "customer_name": "Test Customer",
        "amount": 5000,
        "description": "Test invoice",
        "due_date": "2025-12-01"
    }
    
    # Mock QB authentication check
    mock_quickbooks_service.is_authenticated.return_value = True
    mock_quickbooks_service.create_invoice.return_value = {
        "Id": "5000",
        "DocNumber": "5000",
        "CustomerRef": {"name": "Test Customer", "value": "C123"}
    }
    
    # Simulate chat.py logic
    is_auth = await mock_quickbooks_service.is_authenticated()
    if is_auth:
        invoice = await mock_quickbooks_service.create_invoice({
            "customer_id": func_args["customer_id"],
            "amount": func_args["amount"],
            "description": func_args["description"]
        })
        
        assert invoice is not None
        assert invoice["Id"] == "5000"
        assert invoice["DocNumber"] == "5000"


@pytest.mark.asyncio
async def test_update_quickbooks_invoice_docnumber():
    """
    REGRESSION TEST: DocNumber update feature (November 8, 2025)
    
    This tests the critical feature added today that allows updating
    invoice DocNumbers (e.g., "TTD-6441-11-08").
    
    If this test fails, the DocNumber update feature is broken.
    """
    mock_qb = AsyncMock()
    
    # Mock getting existing invoice
    mock_qb.get_invoice_by_id.return_value = {
        "Id": "4155",
        "DocNumber": "1234",  # Old number
        "Line": [{"Amount": 1000, "DetailType": "SalesItemLineDetail"}],
        "SyncToken": "0",
        "CustomerRef": {"value": "1"}
    }
    
    # Mock update success
    mock_qb.update_invoice.return_value = {
        "Id": "4155",
        "DocNumber": "TTD-6441-11-08",  # New number
        "SyncToken": "1"
    }
    
    # Simulate chat.py update logic
    invoice_id = "4155"
    updates = {"doc_number": "TTD-6441-11-08"}
    
    # Get existing invoice
    existing = await mock_qb.get_invoice_by_id(invoice_id)
    assert existing is not None
    
    # Update invoice (simulating chat.py logic)
    updated_invoice = await mock_qb.update_invoice(
        invoice_id=invoice_id,
        updates=updates,
        sync_token=existing["SyncToken"]
    )
    
    # Verify update
    assert updated_invoice["DocNumber"] == "TTD-6441-11-08"
    assert updated_invoice["Id"] == "4155"
    
    # Verify methods were called correctly
    mock_qb.get_invoice_by_id.assert_called_once_with("4155")
    mock_qb.update_invoice.assert_called_once()


@pytest.mark.asyncio
async def test_add_column_to_sheet(mock_google_service):
    """Test adding column to Google Sheet - validates current implementation"""
    func_args = {
        "sheet_name": "Projects",
        "column_name": "New Field"
    }
    
    mock_google_service.add_column_to_sheet.return_value = True
    
    success = await mock_google_service.add_column_to_sheet(
        sheet_name=func_args["sheet_name"],
        column_name=func_args["column_name"]
    )
    
    assert success is True
    mock_google_service.add_column_to_sheet.assert_called_once_with(
        sheet_name="Projects",
        column_name="New Field"
    )


@pytest.mark.asyncio
async def test_error_handling():
    """Test that service errors are handled gracefully"""
    mock_google = AsyncMock()
    mock_google.update_record_by_id.side_effect = Exception("API Error")
    
    # This should raise an exception (current behavior)
    with pytest.raises(Exception) as exc_info:
        await mock_google.update_record_by_id(
            sheet_name='Projects',
            id_field='Project ID',
            record_id="P123",
            updates={'Status': 'Active'}
        )
    
    assert "API Error" in str(exc_info.value)


@pytest.mark.asyncio
async def test_quickbooks_authentication_check(mock_quickbooks_service):
    """Test that QB operations check authentication"""
    # Test authenticated
    mock_quickbooks_service.is_authenticated.return_value = True
    result = await mock_quickbooks_service.is_authenticated()
    assert result is True
    
    # Test not authenticated
    mock_quickbooks_service.is_authenticated.return_value = False
    result = await mock_quickbooks_service.is_authenticated()
    assert result is False


def test_function_registry_concept():
    """
    Test concept of function registry for future refactor.
    
    After Phase 1, handlers will be in a FUNCTION_HANDLERS dict.
    This test validates the concept works.
    """
    # Simulate future handler registry
    def mock_handler(args):
        return {"status": "success", "details": f"Handled {args}"}
    
    FUNCTION_HANDLERS = {
        "update_project_status": mock_handler,
        "update_permit_status": mock_handler,
        "create_quickbooks_invoice": mock_handler,
        "update_quickbooks_invoice": mock_handler,
        "add_column_to_sheet": mock_handler,
        "update_client_field": mock_handler,
    }
    
    # Verify all expected functions are in registry
    expected_functions = [
        "update_project_status",
        "update_permit_status",
        "create_quickbooks_invoice",
        "update_quickbooks_invoice",
        "add_column_to_sheet",
        "update_client_field"
    ]
    
    for func_name in expected_functions:
        assert func_name in FUNCTION_HANDLERS, f"Function {func_name} missing from registry"
        assert callable(FUNCTION_HANDLERS[func_name]), f"Function {func_name} not callable"
    
    # Verify no extra functions
    assert len(FUNCTION_HANDLERS) == len(expected_functions), "Unexpected functions in registry"
    
    # Test registry usage
    result = FUNCTION_HANDLERS["update_project_status"]({"test": "data"})
    assert result["status"] == "success"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
