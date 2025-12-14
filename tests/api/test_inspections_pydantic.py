"""
Regression test for Pydantic validation in Inspections API

This test catches the specific failure mode from Phase F.2:
- Database returns photos/deficiencies as lists
- Pydantic response model must accept lists, not dicts
- Without this test, changing Optional[List[dict]] back to Optional[dict] 
  would not be caught until runtime 500 errors

Issue: Phase F.2 Inspections 500 Error (Dec 13, 2025)
Root cause: JSONB arrays returned as lists but Pydantic expected dicts
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from datetime import datetime
from uuid import uuid4

from app.main import app
from app.db.models import Inspection


@pytest.fixture
def mock_inspection_with_arrays():
    """
    Mock inspection with photos and deficiencies as LISTS (actual DB structure).
    
    This is the critical test case that would fail if someone changes:
        photos: Optional[List[dict]] → Optional[dict]
    """
    inspection_id = uuid4()
    permit_id = uuid4()
    project_id = uuid4()
    
    return Inspection(
        inspection_id=inspection_id,
        business_id="INSP-001",
        permit_id=permit_id,
        project_id=project_id,
        inspection_type="Final",
        status="Scheduled",
        scheduled_date=datetime(2025, 12, 15, 10, 0, 0),
        completed_date=None,
        inspector="John Doe",
        assigned_to=None,
        result=None,
        notes="Initial inspection",
        # CRITICAL: These are LISTS, not dicts
        photos=[
            {
                "url": "https://example.com/photo1.jpg",
                "timestamp": "2025-12-13T15:36:43.000Z",
                "uploaded_by": "test@example.com"
            }
        ],
        deficiencies=[],  # Empty list is also valid
        extra=None,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )


@pytest.fixture
def mock_auth_user():
    """Mock authenticated user for get_current_user dependency"""
    from app.db.models import User
    
    user = User(
        id=1,
        supabase_user_id=uuid4(),
        email="test@example.com",
        full_name="Test User",
        role="admin",
        is_active=True,
        is_email_verified=True,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    return user


@pytest.fixture
def client(mock_auth_user):
    """Test client with mocked authentication"""
    from app.routes.auth_supabase import get_current_user
    
    # Override auth dependency to bypass JWT validation
    app.dependency_overrides[get_current_user] = lambda: mock_auth_user
    
    client = TestClient(app)
    yield client
    
    # Clean up
    app.dependency_overrides.clear()


def test_inspections_list_pydantic_validation_with_arrays(client, mock_inspection_with_arrays):
    """
    REGRESSION TEST: Ensure photos/deficiencies as lists don't cause Pydantic validation errors.
    
    This test would FAIL if someone changes InspectionResponse to:
        photos: Optional[dict]  # ❌ WRONG
        deficiencies: Optional[dict]  # ❌ WRONG
    
    Expected behavior:
        photos: Optional[List[dict]]  # ✅ CORRECT
        deficiencies: Optional[List[dict]]  # ✅ CORRECT
    """
    
    # Mock the service layer to return our test inspection
    with patch('app.services.inspection_service.InspectionService.get_inspections') as mock_service:
        mock_service.return_value = [mock_inspection_with_arrays]
        
        # Call the endpoint
        response = client.get("/v1/inspections")
        
        # Assert no Pydantic validation error (would be 500)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        # Parse response
        data = response.json()
        
        # Verify structure matches InspectionListResponse
        assert "items" in data
        assert "total" in data
        assert isinstance(data["items"], list)
        assert len(data["items"]) == 1
        
        # Verify the critical fields are lists
        inspection = data["items"][0]
        assert isinstance(inspection["photos"], list), "photos must be a list"
        assert isinstance(inspection["deficiencies"], list), "deficiencies must be a list"
        
        # Verify photos list structure
        assert len(inspection["photos"]) == 1
        assert inspection["photos"][0]["url"] == "https://example.com/photo1.jpg"
        
        # Verify deficiencies is empty list (also valid)
        assert inspection["deficiencies"] == []


def test_inspections_list_empty_photos_deficiencies(client):
    """
    Test case: inspection with NULL photos/deficiencies.
    
    This ensures Optional[List[dict]] = None works correctly.
    """
    
    inspection_id = uuid4()
    mock_inspection_null = Inspection(
        inspection_id=inspection_id,
        business_id="INSP-002",
        permit_id=uuid4(),
        project_id=uuid4(),
        inspection_type="Rough",
        status="Completed",
        scheduled_date=datetime(2025, 12, 10, 9, 0, 0),
        completed_date=datetime(2025, 12, 10, 11, 30, 0),
        inspector="Jane Smith",
        assigned_to=None,
        result="Pass",
        notes=None,
        photos=None,  # NULL in database
        deficiencies=None,  # NULL in database
        extra=None,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    with patch('app.services.inspection_service.InspectionService.get_inspections') as mock_service:
        mock_service.return_value = [mock_inspection_null]
        
        response = client.get("/v1/inspections")
        
        assert response.status_code == 200
        data = response.json()
        
        inspection = data["items"][0]
        # None should be serialized as null in JSON
        assert inspection["photos"] is None
        assert inspection["deficiencies"] is None


def test_inspections_list_multiple_photos_deficiencies(client):
    """
    Test case: inspection with multiple photos and deficiencies.
    
    Ensures List[dict] handles multiple items correctly.
    """
    
    inspection_id = uuid4()
    mock_inspection_multi = Inspection(
        inspection_id=inspection_id,
        business_id="INSP-003",
        permit_id=uuid4(),
        project_id=uuid4(),
        inspection_type="Final",
        status="In Progress",
        scheduled_date=datetime(2025, 12, 14, 14, 0, 0),
        completed_date=None,
        inspector="Bob Wilson",
        assigned_to=uuid4(),
        result=None,
        notes="Found issues",
        photos=[
            {"url": "https://example.com/photo1.jpg", "timestamp": "2025-12-13T10:00:00Z"},
            {"url": "https://example.com/photo2.jpg", "timestamp": "2025-12-13T10:05:00Z"},
            {"url": "https://example.com/photo3.jpg", "timestamp": "2025-12-13T10:10:00Z"}
        ],
        deficiencies=[
            {"description": "Cracked foundation", "severity": "high"},
            {"description": "Missing handrail", "severity": "medium"}
        ],
        extra=None,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    with patch('app.services.inspection_service.InspectionService.get_inspections') as mock_service:
        mock_service.return_value = [mock_inspection_multi]
        
        response = client.get("/v1/inspections")
        
        assert response.status_code == 200
        data = response.json()
        
        inspection = data["items"][0]
        
        # Verify multiple items in lists
        assert isinstance(inspection["photos"], list)
        assert len(inspection["photos"]) == 3
        assert inspection["photos"][0]["url"] == "https://example.com/photo1.jpg"
        assert inspection["photos"][2]["url"] == "https://example.com/photo3.jpg"
        
        assert isinstance(inspection["deficiencies"], list)
        assert len(inspection["deficiencies"]) == 2
        assert inspection["deficiencies"][0]["description"] == "Cracked foundation"
        assert inspection["deficiencies"][1]["severity"] == "medium"


if __name__ == "__main__":
    # Run with: python -m pytest tests/api/test_inspections_pydantic.py -v
    pytest.main([__file__, "-v"])
