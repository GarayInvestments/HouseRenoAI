"""
Test fixtures for AI handler tests.
Provides mock services for Google Sheets, QuickBooks, and memory manager.
"""
import pytest
from unittest.mock import MagicMock, AsyncMock


@pytest.fixture
def mock_google_service():
    """Mock Google Sheets service with common responses"""
    mock = AsyncMock()
    mock.update_project_status.return_value = True
    mock.update_permit_status.return_value = True
    mock.update_client_field.return_value = True
    mock.add_column_to_sheet.return_value = True
    
    # Mock data getters
    mock.get_projects_data.return_value = [
        {"Project ID": "P123", "Status": "Active", "Client": "Test Client"}
    ]
    mock.get_permits_data.return_value = [
        {"Permit ID": "PM456", "Permit Status": "Approved"}
    ]
    mock.get_clients_data.return_value = [
        {"Client ID": "C789", "Full Name": "Test Client"}
    ]
    
    return mock


@pytest.fixture
def mock_quickbooks_service():
    """Mock QuickBooks service with common responses"""
    mock = AsyncMock()
    mock.is_authenticated.return_value = True
    mock.create_invoice.return_value = {
        "Id": "123",
        "DocNumber": "123",
        "CustomerRef": {"name": "Test Customer", "value": "1"}
    }
    mock.update_invoice.return_value = {
        "Id": "123",
        "DocNumber": "TTD-123",
        "SyncToken": "1"
    }
    mock.get_invoice_by_id.return_value = {
        "Id": "123",
        "DocNumber": "OLD-123",
        "SyncToken": "0",
        "Line": [{"Amount": 1000}],
        "CustomerRef": {"value": "1"}
    }
    mock.get_customers.return_value = [
        {"Id": "1", "DisplayName": "Test Customer"}
    ]
    mock.get_invoices.return_value = [
        {"Id": "123", "DocNumber": "123", "TotalAmt": 1000}
    ]
    
    return mock


@pytest.fixture
def mock_memory_manager():
    """Mock memory manager for session storage"""
    mock = MagicMock()
    mock.get_all.return_value = {}
    mock.get.return_value = None
    mock.set.return_value = None
    
    return mock
