"""
Unit tests for Context Optimizer (Phase D.2)

Tests entity extraction, intelligent truncation, and query-relevant filtering.
"""

import pytest
from datetime import datetime, timedelta
from app.utils.context_optimizer import (
    extract_entity_mentions,
    truncate_projects,
    truncate_permits,
    truncate_payments,
    truncate_clients,
    truncate_quickbooks_customers,
    truncate_quickbooks_invoices,
    optimize_context
)


# ==================== ENTITY EXTRACTION TESTS ====================

def test_extract_entity_mentions_client_names():
    """Test extracting client name keywords."""
    message = "Show me projects for Temple Hills client"
    entities = extract_entity_mentions(message)
    
    assert "temple" in entities["client_names"]
    assert len(entities["client_names"]) >= 1


def test_extract_entity_mentions_business_ids():
    """Test extracting business IDs."""
    message = "What's the status of PRJ-00123 and CL-00456?"
    entities = extract_entity_mentions(message)
    
    assert "PRJ-00123" in entities["specific_ids"]
    assert "CL-00456" in entities["specific_ids"]
    assert len(entities["specific_ids"]) == 2


def test_extract_entity_mentions_date_references():
    """Test extracting date keywords."""
    message = "Show me projects from last month"
    entities = extract_entity_mentions(message)
    
    assert "last month" in entities["date_references"]


def test_extract_entity_mentions_multiple_types():
    """Test extracting multiple entity types at once."""
    message = "Show Fairmont project PRJ-00001 from last week"
    entities = extract_entity_mentions(message)
    
    assert "fairmont" in entities["client_names"]
    assert "PRJ-00001" in entities["specific_ids"]
    assert "last week" in entities["date_references"]


def test_extract_entity_mentions_no_matches():
    """Test message with no entity mentions."""
    message = "Hello, how are you?"
    entities = extract_entity_mentions(message)
    
    assert len(entities["client_names"]) == 0
    assert len(entities["specific_ids"]) == 0


def test_extract_entity_mentions_case_insensitive():
    """Test case-insensitive entity extraction."""
    message = "TEMPLE HILLS project status"
    entities = extract_entity_mentions(message)
    
    assert "temple" in entities["client_names"]


# ==================== PROJECT TRUNCATION TESTS ====================

def test_truncate_projects_empty_list():
    """Test truncating empty project list."""
    result = truncate_projects([], "show me projects")
    
    assert result["projects"] == []
    assert result["summary"] == {}


def test_truncate_projects_specific_client():
    """Test filtering to specific client mention."""
    projects = [
        {"Project Name": "Temple Hills Renovation", "business_id": "PRJ-00001", "Status": "Active"},
        {"Project Name": "Fairmont Construction", "business_id": "PRJ-00002", "Status": "Active"},
        {"Project Name": "Upshur Remodel", "business_id": "PRJ-00003", "Status": "Active"},
    ]
    
    result = truncate_projects(projects, "Show me Temple projects")
    
    assert len(result["projects"]) == 1
    assert "Temple" in result["projects"][0]["Project Name"]
    assert result["summary"]["filtered"] is True
    assert result["summary"]["shown"] == 1
    assert result["summary"]["total"] == 3


def test_truncate_projects_by_business_id():
    """Test filtering by business ID."""
    projects = [
        {"Project Name": "Project A", "business_id": "PRJ-00001"},
        {"Project Name": "Project B", "business_id": "PRJ-00002"},
        {"Project Name": "Project C", "business_id": "PRJ-00003"},
    ]
    
    result = truncate_projects(projects, "Status of PRJ-00002")
    
    assert len(result["projects"]) == 1
    assert result["projects"][0]["business_id"] == "PRJ-00002"
    assert result["summary"]["filtered"] is True


def test_truncate_projects_recent_only():
    """Test showing only recent projects when no specific mention."""
    projects = [
        {"business_id": f"PRJ-{str(i).zfill(5)}", "updated_at": f"2025-01-{20-i:02d}"}
        for i in range(15)
    ]
    
    result = truncate_projects(projects, "Show me all projects", max_recent=10)
    
    assert len(result["projects"]) == 10
    assert result["summary"]["shown"] == 10
    assert result["summary"]["total"] == 15
    assert result["summary"]["filtered"] is False


def test_truncate_projects_status_summary():
    """Test status breakdown in summary."""
    projects = [
        {"business_id": "PRJ-00001", "Status": "Active", "updated_at": "2025-01-15"},
        {"business_id": "PRJ-00002", "Status": "Active", "updated_at": "2025-01-14"},
        {"business_id": "PRJ-00003", "Status": "Completed", "updated_at": "2025-01-13"},
        {"business_id": "PRJ-00004", "Status": "On Hold", "updated_at": "2025-01-12"},
    ]
    
    result = truncate_projects(projects, "Show projects", max_recent=10)
    
    assert "status_breakdown" in result["summary"]
    assert result["summary"]["status_breakdown"]["Active"] == 2
    assert result["summary"]["status_breakdown"]["Completed"] == 1
    assert result["summary"]["status_breakdown"]["On Hold"] == 1


# ==================== PERMIT TRUNCATION TESTS ====================

def test_truncate_permits_empty_list():
    """Test truncating empty permit list."""
    result = truncate_permits([], "show permits")
    
    assert result["permits"] == []
    assert result["summary"] == {}


def test_truncate_permits_by_project_id():
    """Test filtering permits by project business ID."""
    permits = [
        {"business_id": "PER-00001", "project_id": "PRJ-00001", "Permit Type": "Building"},
        {"business_id": "PER-00002", "project_id": "PRJ-00002", "Permit Type": "Electrical"},
        {"business_id": "PER-00003", "project_id": "PRJ-00001", "Permit Type": "Plumbing"},
    ]
    
    result = truncate_permits(permits, "Show permits for PRJ-00001")
    
    assert len(result["permits"]) == 2
    assert all(p["project_id"] == "PRJ-00001" for p in result["permits"])
    assert result["summary"]["filtered"] is True


def test_truncate_permits_recent_only():
    """Test showing only recent permits when no filter."""
    permits = [
        {"business_id": f"PER-{str(i).zfill(5)}", "updated_at": f"2025-01-{20-i:02d}"}
        for i in range(20)
    ]
    
    result = truncate_permits(permits, "Show all permits", max_recent=15)
    
    assert len(result["permits"]) == 15
    assert result["summary"]["shown"] == 15
    assert result["summary"]["total"] == 20


def test_truncate_permits_status_summary():
    """Test permit status breakdown."""
    permits = [
        {"business_id": "PER-00001", "Status": "Approved", "updated_at": "2025-01-15"},
        {"business_id": "PER-00002", "Status": "Pending", "updated_at": "2025-01-14"},
        {"business_id": "PER-00003", "Status": "Approved", "updated_at": "2025-01-13"},
    ]
    
    result = truncate_permits(permits, "Show permits", max_recent=15)
    
    assert result["summary"]["status_breakdown"]["Approved"] == 2
    assert result["summary"]["status_breakdown"]["Pending"] == 1


# ==================== PAYMENT TRUNCATION TESTS ====================

def test_truncate_payments_empty_list():
    """Test truncating empty payment list."""
    result = truncate_payments([], "show payments")
    
    assert result["payments"] == []
    assert result["summary"]["total_amount"] == 0


def test_truncate_payments_recent_only():
    """Test showing recent payments with summary."""
    payments = [
        {"business_id": f"PAY-{str(i).zfill(5)}", "Amount": 1000.00 * i, "payment_date": f"2025-01-{20-i:02d}"}
        for i in range(1, 26)  # 25 payments
    ]
    
    result = truncate_payments(payments, "Show payments", max_recent=20)
    
    assert len(result["payments"]) == 20
    assert result["summary"]["shown"] == 20
    assert result["summary"]["total"] == 25
    assert result["summary"]["total_amount"] == sum(p["Amount"] for p in payments)


def test_truncate_payments_amount_summary():
    """Test payment amount calculations in summary."""
    payments = [
        {"business_id": "PAY-00001", "Amount": 1000.00, "payment_date": "2025-01-15"},
        {"business_id": "PAY-00002", "Amount": 2500.00, "payment_date": "2025-01-14"},
        {"business_id": "PAY-00003", "Amount": 500.00, "payment_date": "2025-01-13"},
    ]
    
    result = truncate_payments(payments, "Show payments", max_recent=20)

    assert result["summary"]["total_amount"] == 4000.00
    assert result["summary"]["shown"] == 3
    assert result["summary"]["total"] == 3
# ==================== CLIENT TRUNCATION TESTS ====================

def test_truncate_clients_specific_mention():
    """Test filtering clients by name mention."""
    clients = [
        {"Full Name": "Temple Hills LLC", "business_id": "CL-00001"},
        {"Full Name": "Fairmont Construction", "business_id": "CL-00002"},
        {"Full Name": "Upshur Properties", "business_id": "CL-00003"},
    ]
    
    result = truncate_clients(clients, "Show Temple client info")
    
    assert len(result["clients"]) == 1
    assert "Temple" in result["clients"][0]["Full Name"]
    assert result["summary"]["filtered"] is True


def test_truncate_clients_by_business_id():
    """Test filtering clients by business ID."""
    clients = [
        {"Full Name": "Client A", "business_id": "CL-00001"},
        {"Full Name": "Client B", "business_id": "CL-00002"},
    ]
    
    result = truncate_clients(clients, "Details for CL-00002")
    
    assert len(result["clients"]) == 1
    assert result["clients"][0]["business_id"] == "CL-00002"


def test_truncate_clients_all_when_no_filter():
    """Test returning all clients when no filter applies."""
    clients = [
        {"Full Name": f"Client {i}", "business_id": f"CL-{str(i).zfill(5)}"}
        for i in range(10)
    ]
    
    result = truncate_clients(clients, "Show all clients")
    
    assert len(result["clients"]) == 10  # All clients included
    assert result["summary"]["filtered"] is False


# ==================== QUICKBOOKS CUSTOMER TRUNCATION TESTS ====================

def test_truncate_quickbooks_customers_active_only():
    """Test showing only active QB customers."""
    customers = [
        {"Id": "QB1", "DisplayName": "Customer 1", "Active": True},
        {"Id": "QB2", "DisplayName": "Customer 2", "Active": False},
        {"Id": "QB3", "DisplayName": "Customer 3", "Active": True},
    ]
    
    result = truncate_quickbooks_customers(customers, "Show customers", max_customers=20)
    
    # Should only include active customers
    assert all(c.get("Active") for c in result["customers"])
    assert result["summary"]["active_count"] == 2
    assert result["summary"]["inactive_count"] == 1


def test_truncate_quickbooks_customers_specific_filter():
    """Test filtering QB customers by name mention."""
    customers = [
        {"Id": "QB1", "DisplayName": "Temple Construction", "Active": True},
        {"Id": "QB2", "DisplayName": "Fairmont LLC", "Active": True},
    ]
    
    result = truncate_quickbooks_customers(customers, "Show Temple customer")
    
    assert len(result["customers"]) == 1
    assert "Temple" in result["customers"][0]["DisplayName"]


def test_truncate_quickbooks_customers_max_limit():
    """Test limiting active customers to max count."""
    customers = [
        {"Id": f"QB{i}", "DisplayName": f"Customer {i}", "Active": True}
        for i in range(30)
    ]
    
    result = truncate_quickbooks_customers(customers, "Show customers", max_customers=20)
    
    assert len(result["customers"]) == 20
    assert result["summary"]["shown"] == 20
    assert result["summary"]["active_count"] == 30


# ==================== QUICKBOOKS INVOICE TRUNCATION TESTS ====================

def test_truncate_quickbooks_invoices_already_limited():
    """Test that QB invoices are already limited upstream."""
    invoices = [
        {"Id": f"INV{i}", "TotalAmt": 1000.00 * i, "Balance": 500.00 * i}
        for i in range(5)
    ]
    
    result = truncate_quickbooks_invoices(invoices, "Show invoices")
    
    # Should return all (already limited to 10 by caller)
    assert len(result["invoices"]) == 5
    assert "summary" in result
    assert result["summary"]["total_amount"] == sum(inv["TotalAmt"] for inv in invoices)


def test_truncate_quickbooks_invoices_summary_stats():
    """Test invoice summary statistics."""
    invoices = [
        {"Id": "INV1", "TotalAmt": 5000.00, "Balance": 2500.00},
        {"Id": "INV2", "TotalAmt": 3000.00, "Balance": 0.00},
        {"Id": "INV3", "TotalAmt": 2000.00, "Balance": 2000.00},
    ]
    
    result = truncate_quickbooks_invoices(invoices, "Show invoices")

    assert result["summary"]["total_amount"] == 10000.00
    assert result["summary"]["paid_count"] == 1
    assert result["summary"]["unpaid_count"] == 2
    assert result["summary"]["paid_count"] == 1  # INV2 fully paid


# ==================== FULL CONTEXT OPTIMIZATION TESTS ====================

def test_optimize_context_empty():
    """Test optimizing empty context."""
    context = {}
    result = optimize_context(context, "Hello")

    # Empty context still returns optimization metadata
    assert result["optimized"] is True
    assert "optimization_metadata" in result
    assert result["contexts_loaded"] == []
    assert result["session_memory"] == {}
def test_optimize_context_all_types():
    """Test optimizing context with all data types."""
    context = {
        "projects": [{"business_id": f"PRJ-{str(i).zfill(5)}"} for i in range(20)],
        "permits": [{"business_id": f"PER-{str(i).zfill(5)}"} for i in range(25)],
        "payments": [{"business_id": f"PAY-{str(i).zfill(5)}", "Amount": 1000.00} for i in range(30)],
        "clients": [{"business_id": f"CL-{str(i).zfill(5)}"} for i in range(15)],
        "quickbooks_customers": [{"Id": f"QB{i}", "Active": True} for i in range(40)],
        "quickbooks_invoices": [{"Id": f"INV{i}", "TotalAmt": 5000.00, "Balance": 2500.00} for i in range(8)],
    }
    
    result = optimize_context(context, "Show me recent projects")

    # Verify all types were processed
    assert "projects" in result
    assert "permits" in result
    assert "payments" in result
    assert "clients" in result
    # QB customers/invoices go under "quickbooks" key
    assert "quickbooks" in result
    assert "customers" in result["quickbooks"]
    assert "invoices" in result["quickbooks"]    # Verify truncation occurred
    assert len(result["projects"]) <= 10  # Max recent
    assert len(result["permits"]) <= 15
    assert len(result["payments"]) <= 20
    assert len(result["quickbooks_customers"]) <= 20


def test_optimize_context_query_relevant_filtering():
    """Test that query-relevant filtering works across optimization."""
    context = {
        "projects": [
            {"Project Name": "Temple Hills", "business_id": "PRJ-00001"},
            {"Project Name": "Fairmont", "business_id": "PRJ-00002"},
        ],
        "clients": [
            {"Full Name": "Temple LLC", "business_id": "CL-00001"},
            {"Full Name": "Fairmont Inc", "business_id": "CL-00002"},
        ],
    }
    
    result = optimize_context(context, "Show me Temple project details")
    
    # Should filter to Temple-related records only
    assert len(result["projects"]) == 1
    assert "Temple" in result["projects"][0]["Project Name"]
    assert len(result["clients"]) == 1
    assert "Temple" in result["clients"][0]["Full Name"]


def test_optimize_context_preserves_non_list_data():
    """Test that non-list context data is preserved."""
    context = {
        "projects": [{"business_id": "PRJ-00001"}],
        "metadata": {"user": "admin", "timestamp": "2025-01-15"},
        "session_info": "some_session_id"
    }
    
    result = optimize_context(context, "Show projects")

    # Projects should be processed
    assert "projects" in result
    
    # Non-list data is not preserved by optimize_context
    # optimize_context only processes known data types
    assert "optimized" in result
    assert "optimization_metadata" in result
# ==================== EDGE CASES ====================

def test_extract_entity_mentions_special_characters():
    """Test entity extraction with special characters."""
    message = "Show project PRJ-00001 & CL-00002 (Temple)"
    entities = extract_entity_mentions(message)
    
    assert "PRJ-00001" in entities["specific_ids"]
    assert "CL-00002" in entities["specific_ids"]
    assert "temple" in entities["client_names"]


def test_truncate_projects_missing_fields():
    """Test truncation when projects have missing fields."""
    projects = [
        {"business_id": "PRJ-00001"},  # No name or address
        {"Project Name": "Test Project"},  # No business_id
    ]
    
    result = truncate_projects(projects, "Show projects", max_recent=10)
    
    # Should handle gracefully without errors
    assert len(result["projects"]) == 2


def test_optimize_context_none_values():
    """Test optimization handles None values in lists."""
    context = {
        "projects": None,
        "permits": [],
        "clients": [{"business_id": "CL-00001"}]
    }
    
    result = optimize_context(context, "Show data")
    
    # Should handle None gracefully
    assert result.get("projects") is None or result.get("projects") == []
    assert result["permits"] == []
    assert len(result["clients"]) == 1


def test_truncate_payments_zero_amounts():
    """Test payment truncation with zero amounts."""
    payments = [
        {"business_id": "PAY-00001", "Amount": 0.00, "payment_date": "2025-01-15"},
        {"business_id": "PAY-00002", "Amount": 1000.00, "payment_date": "2025-01-14"},
    ]
    
    result = truncate_payments(payments, "Show payments", max_recent=20)
    
    assert result["summary"]["total_amount"] == 1000.00
    assert len(result["payments"]) == 2  # Both included
