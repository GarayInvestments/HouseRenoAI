"""
QuickBooks Online API Routes

Handles OAuth2 flow and QuickBooks operations.
"""
import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import RedirectResponse

from app.services.quickbooks_service import quickbooks_service

logger = logging.getLogger(__name__)
router = APIRouter()


# ==================== OAUTH2 FLOW ====================

@router.get("/auth")
async def initiate_auth(state: str = Query(default="randomstate")):
    """
    Initiate QuickBooks OAuth2 flow.
    
    Redirects user to QuickBooks login page.
    After authorization, QuickBooks redirects back to /callback endpoint.
    
    Query Parameters:
        state: Optional CSRF protection state parameter
    
    Returns:
        Redirect to QuickBooks authorization page
    
    Example:
        GET /v1/quickbooks/auth
        GET /v1/quickbooks/auth?state=my-secure-state
    """
    try:
        auth_url = quickbooks_service.get_auth_url(state=state)
        logger.info(f"Redirecting to QuickBooks auth: {auth_url}")
        return RedirectResponse(url=auth_url)
    except Exception as e:
        logger.error(f"Failed to generate auth URL: {e}")
        raise HTTPException(status_code=500, detail=f"Auth initialization failed: {str(e)}")


@router.get("/callback")
async def oauth_callback(
    code: str = Query(..., description="Authorization code from QuickBooks"),
    realmId: str = Query(..., description="Company ID"),
    state: Optional[str] = Query(default=None)
):
    """
    OAuth2 callback endpoint.
    
    QuickBooks redirects here after user authorizes the app.
    Exchanges authorization code for access and refresh tokens.
    
    Query Parameters:
        code: Authorization code
        realmId: QuickBooks company ID
        state: State parameter (should match initial request)
    
    Returns:
        Token information and success status
    
    Example:
        GET /v1/quickbooks/callback?code=ABC123&realmId=123456789
    """
    try:
        logger.info(f"Received OAuth callback for realm: {realmId}")
        
        token_data = await quickbooks_service.exchange_code_for_token(code, realmId)
        
        return {
            "success": True,
            "message": "Successfully connected to QuickBooks",
            "realm_id": realmId,
            "token_expires_in": token_data.get("expires_in"),
            "redirect_to": "/quickbooks/status"  # Frontend can redirect here
        }
        
    except Exception as e:
        logger.error(f"OAuth callback failed: {e}")
        raise HTTPException(status_code=400, detail=f"OAuth callback failed: {str(e)}")


@router.post("/disconnect")
async def disconnect():
    """
    Disconnect from QuickBooks (clear tokens).
    
    Note: This only clears local tokens. User must revoke app access
    in QuickBooks settings for full disconnection.
    
    Returns:
        Success status
    """
    try:
        quickbooks_service.access_token = None
        quickbooks_service.refresh_token = None
        quickbooks_service.realm_id = None
        quickbooks_service.token_expires_at = None
        
        logger.info("Disconnected from QuickBooks")
        return {"success": True, "message": "Disconnected from QuickBooks"}
        
    except Exception as e:
        logger.error(f"Disconnect failed: {e}")
        raise HTTPException(status_code=500, detail=f"Disconnect failed: {str(e)}")


# ==================== STATUS & INFO ====================

@router.get("/status")
async def get_status():
    """
    Get QuickBooks connection status.
    
    Returns:
        Connection status, realm ID, token expiration
    
    Example Response:
        {
            "authenticated": true,
            "realm_id": "123456789",
            "environment": "sandbox",
            "token_expires_at": "2025-01-06T12:00:00"
        }
    """
    try:
        status = quickbooks_service.get_status()
        return status
    except Exception as e:
        logger.error(f"Failed to get status: {e}")
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")


@router.post("/refresh")
async def manual_refresh():
    """
    Manually refresh QuickBooks access token using refresh token.
    Use this after deployments if tokens are expired.
    
    Returns:
        Success status and new token expiration
    """
    try:
        if not quickbooks_service.refresh_token:
            raise HTTPException(
                status_code=400, 
                detail="No refresh token available. Please authenticate first at /v1/quickbooks/auth"
            )
        
        # Attempt to refresh
        result = await quickbooks_service.refresh_access_token()
        
        return {
            "success": True,
            "message": "Token refreshed successfully",
            "token_expires_in": result.get("expires_in"),
            "token_expires_at": quickbooks_service.token_expires_at.isoformat() if quickbooks_service.token_expires_at else None
        }
        
    except Exception as e:
        logger.error(f"Failed to refresh token: {e}")
        # If refresh fails, tokens are likely expired - need to re-auth
        raise HTTPException(
            status_code=401, 
            detail=f"Token refresh failed: {str(e)}. Refresh token may be expired. Please re-authenticate at /v1/quickbooks/auth"
        )


@router.get("/company")
async def get_company_info():
    """
    Get company information from QuickBooks.
    
    Returns:
        Company details (name, address, tax info, etc.)
    
    Requires:
        Active authentication
    
    Example Response:
        {
            "CompanyName": "House Renovators LLC",
            "LegalName": "House Renovators LLC",
            "CompanyAddr": {...},
            "Email": {...}
        }
    """
    try:
        if not quickbooks_service.is_authenticated():
            raise HTTPException(status_code=401, detail="Not authenticated with QuickBooks")
        
        company_info = await quickbooks_service.get_company_info()
        return company_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get company info: {e}")
        raise HTTPException(status_code=500, detail=f"Company info retrieval failed: {str(e)}")


# ==================== CUSTOMER OPERATIONS ====================

@router.get("/customers")
async def get_customers(
    active_only: bool = Query(default=True),
    customer_type: Optional[str] = Query(default="GC Compliance", description="Filter by CustomerType. Default: 'GC Compliance' for permit clients. Pass empty string '' or 'none' to disable filtering.")
):
    """
    Get all customers from QuickBooks.
    
    Query Parameters:
        active_only: Only return active customers (default: true)
        customer_type: Filter by CustomerType name (default: "GC Compliance" - permit clients only)
    
    Returns:
        List of customer records
    
    Example:
        GET /v1/quickbooks/customers  (returns only GC Compliance customers)
        GET /v1/quickbooks/customers?customer_type=  (returns all customers)
        GET /v1/quickbooks/customers?customer_type=GC%20Compliance
    """
    try:
        if not quickbooks_service.is_authenticated():
            raise HTTPException(status_code=401, detail="Not authenticated with QuickBooks")
        
        # Convert empty string to None for "no filter"
        filter_type = None if customer_type == "" else customer_type
        
        customers = await quickbooks_service.get_customers(
            active_only=active_only,
            customer_type=filter_type
        )
        
        return {
            "success": True,
            "count": len(customers),
            "customers": customers
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get customers: {e}")
        raise HTTPException(status_code=500, detail=f"Customer retrieval failed: {str(e)}")


@router.post("/customers")
async def create_customer(customer_data: Dict[str, Any]):
    """
    Create a new customer in QuickBooks.
    
    Request Body:
        {
            "DisplayName": "John Doe",  # Required
            "CompanyName": "Doe Construction",  # Optional
            "GivenName": "John",  # Optional
            "FamilyName": "Doe",  # Optional
            "PrimaryPhone": {"FreeFormNumber": "(555) 123-4567"},  # Optional
            "PrimaryEmailAddr": {"Address": "john@example.com"},  # Optional
            "BillAddr": {  # Optional
                "Line1": "123 Main St",
                "City": "Anytown",
                "CountrySubDivisionCode": "CA",
                "PostalCode": "12345"
            }
        }
    
    Returns:
        Created customer record
    
    Example:
        POST /v1/quickbooks/customers
        Body: {"DisplayName": "John Doe", "PrimaryPhone": {"FreeFormNumber": "555-1234"}}
    """
    try:
        if not quickbooks_service.is_authenticated():
            raise HTTPException(status_code=401, detail="Not authenticated with QuickBooks")
        
        if "DisplayName" not in customer_data:
            raise HTTPException(status_code=400, detail="DisplayName is required")
        
        customer = await quickbooks_service.create_customer(customer_data)
        
        return {
            "success": True,
            "message": "Customer created successfully",
            "customer": customer
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create customer: {e}")
        raise HTTPException(status_code=500, detail=f"Customer creation failed: {str(e)}")


@router.get("/customers/{customer_id}")
async def get_customer(customer_id: str):
    """
    Get a specific customer by QuickBooks ID.
    
    Path Parameters:
        customer_id: QuickBooks customer ID
    
    Returns:
        Customer record
    
    Example:
        GET /v1/quickbooks/customers/123
    """
    try:
        if not quickbooks_service.is_authenticated():
            raise HTTPException(status_code=401, detail="Not authenticated with QuickBooks")
        
        customer = await quickbooks_service.get_customer_by_id(customer_id)
        
        return {
            "success": True,
            "customer": customer
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get customer: {e}")
        raise HTTPException(status_code=404, detail=f"Customer not found: {str(e)}")


# ==================== INVOICE OPERATIONS ====================

@router.get("/invoices")
async def get_invoices(
    customer_id: Optional[str] = Query(default=None),
    start_date: Optional[str] = Query(default=None, description="YYYY-MM-DD format"),
    end_date: Optional[str] = Query(default=None, description="YYYY-MM-DD format")
):
    """
    Get invoices from QuickBooks.
    
    Query Parameters:
        customer_id: Filter by customer ID (optional)
        start_date: Filter by TxnDate >= start_date (YYYY-MM-DD) (optional)
        end_date: Filter by TxnDate <= end_date (YYYY-MM-DD) (optional)
    
    Returns:
        List of invoice records
    
    Example:
        GET /v1/quickbooks/invoices
        GET /v1/quickbooks/invoices?customer_id=123
        GET /v1/quickbooks/invoices?start_date=2025-01-01&end_date=2025-01-31
    """
    try:
        if not quickbooks_service.is_authenticated():
            raise HTTPException(status_code=401, detail="Not authenticated with QuickBooks")
        
        invoices = await quickbooks_service.get_invoices(
            customer_id=customer_id,
            start_date=start_date,
            end_date=end_date
        )
        
        return {
            "success": True,
            "count": len(invoices),
            "invoices": invoices
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get invoices: {e}")
        raise HTTPException(status_code=500, detail=f"Invoice retrieval failed: {str(e)}")


@router.post("/invoices")
async def create_invoice(invoice_data: Dict[str, Any]):
    """
    Create a new invoice in QuickBooks.
    
    Request Body:
        {
            "CustomerRef": {"value": "123"},  # Required: Customer ID
            "Line": [  # Required: Line items
                {
                    "Amount": 1000.00,
                    "DetailType": "SalesItemLineDetail",
                    "SalesItemLineDetail": {
                        "ItemRef": {"value": "1"},  # Item/Service ID
                        "Qty": 1
                    },
                    "Description": "Renovation work"
                }
            ],
            "TxnDate": "2025-01-06",  # Optional: Invoice date (YYYY-MM-DD)
            "DueDate": "2025-02-06",  # Optional: Due date (YYYY-MM-DD)
            "DocNumber": "INV-001"  # Optional: Invoice number
        }
    
    Returns:
        Created invoice record
    
    Example:
        POST /v1/quickbooks/invoices
        Body: {
            "CustomerRef": {"value": "123"},
            "Line": [{
                "Amount": 500.00,
                "DetailType": "SalesItemLineDetail",
                "SalesItemLineDetail": {"ItemRef": {"value": "1"}},
                "Description": "Labor"
            }]
        }
    """
    try:
        if not quickbooks_service.is_authenticated():
            raise HTTPException(status_code=401, detail="Not authenticated with QuickBooks")
        
        # Validate required fields
        if "CustomerRef" not in invoice_data:
            raise HTTPException(status_code=400, detail="CustomerRef is required")
        if "Line" not in invoice_data or not invoice_data["Line"]:
            raise HTTPException(status_code=400, detail="At least one Line item is required")
        
        invoice = await quickbooks_service.create_invoice(invoice_data)
        
        return {
            "success": True,
            "message": "Invoice created successfully",
            "invoice": invoice
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create invoice: {e}")
        raise HTTPException(status_code=500, detail=f"Invoice creation failed: {str(e)}")


@router.get("/invoices/{invoice_id}")
async def get_invoice(invoice_id: str):
    """
    Get a specific invoice by QuickBooks ID.
    
    Path Parameters:
        invoice_id: QuickBooks invoice ID
    
    Returns:
        Invoice record
    
    Example:
        GET /v1/quickbooks/invoices/123
    """
    try:
        if not quickbooks_service.is_authenticated():
            raise HTTPException(status_code=401, detail="Not authenticated with QuickBooks")
        
        invoice = await quickbooks_service.get_invoice_by_id(invoice_id)
        
        return {
            "success": True,
            "invoice": invoice
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get invoice: {e}")
        raise HTTPException(status_code=404, detail=f"Invoice not found: {str(e)}")


# ==================== ESTIMATE OPERATIONS ====================

@router.post("/estimates")
async def create_estimate(estimate_data: Dict[str, Any]):
    """
    Create an estimate in QuickBooks.
    
    Request Body: Similar to invoice structure
        {
            "CustomerRef": {"value": "123"},
            "Line": [{"Amount": 1000.00, ...}],
            "TxnDate": "2025-01-06"
        }
    
    Returns:
        Created estimate record
    """
    try:
        if not quickbooks_service.is_authenticated():
            raise HTTPException(status_code=401, detail="Not authenticated with QuickBooks")
        
        if "CustomerRef" not in estimate_data:
            raise HTTPException(status_code=400, detail="CustomerRef is required")
        if "Line" not in estimate_data or not estimate_data["Line"]:
            raise HTTPException(status_code=400, detail="At least one Line item is required")
        
        estimate = await quickbooks_service.create_estimate(estimate_data)
        
        return {
            "success": True,
            "message": "Estimate created successfully",
            "estimate": estimate
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create estimate: {e}")
        raise HTTPException(status_code=500, detail=f"Estimate creation failed: {str(e)}")


# ==================== VENDOR & BILL OPERATIONS ====================

@router.get("/vendors")
async def get_vendors(active_only: bool = Query(default=True)):
    """
    Get all vendors from QuickBooks.
    
    Query Parameters:
        active_only: Only return active vendors (default: true)
    
    Returns:
        List of vendor records
    """
    try:
        if not quickbooks_service.is_authenticated():
            raise HTTPException(status_code=401, detail="Not authenticated with QuickBooks")
        
        vendors = await quickbooks_service.get_vendors(active_only=active_only)
        
        return {
            "success": True,
            "count": len(vendors),
            "vendors": vendors
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get vendors: {e}")
        raise HTTPException(status_code=500, detail=f"Vendor retrieval failed: {str(e)}")


@router.post("/bills")
async def create_bill(bill_data: Dict[str, Any]):
    """
    Create a bill in QuickBooks.
    
    Request Body:
        {
            "VendorRef": {"value": "123"},  # Required: Vendor ID
            "Line": [  # Required: Line items
                {
                    "Amount": 500.00,
                    "DetailType": "AccountBasedExpenseLineDetail",
                    "AccountBasedExpenseLineDetail": {
                        "AccountRef": {"value": "1"}  # Expense account ID
                    },
                    "Description": "Materials"
                }
            ],
            "TxnDate": "2025-01-06",  # Optional
            "DueDate": "2025-02-06"  # Optional
        }
    
    Returns:
        Created bill record
    """
    try:
        if not quickbooks_service.is_authenticated():
            raise HTTPException(status_code=401, detail="Not authenticated with QuickBooks")
        
        if "VendorRef" not in bill_data:
            raise HTTPException(status_code=400, detail="VendorRef is required")
        if "Line" not in bill_data or not bill_data["Line"]:
            raise HTTPException(status_code=400, detail="At least one Line item is required")
        
        bill = await quickbooks_service.create_bill(bill_data)
        
        return {
            "success": True,
            "message": "Bill created successfully",
            "bill": bill
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create bill: {e}")
        raise HTTPException(status_code=500, detail=f"Bill creation failed: {str(e)}")


# ==================== ITEMS/SERVICES ====================

@router.get("/items")
async def get_items(item_type: Optional[str] = Query(default=None)):
    """
    Get items/services from QuickBooks.
    
    Query Parameters:
        item_type: Filter by type (Service, Inventory, NonInventory, etc.)
    
    Returns:
        List of item records
    
    Example:
        GET /v1/quickbooks/items
        GET /v1/quickbooks/items?item_type=Service
    """
    try:
        if not quickbooks_service.is_authenticated():
            raise HTTPException(status_code=401, detail="Not authenticated with QuickBooks")
        
        items = await quickbooks_service.get_items(item_type=item_type)
        
        return {
            "success": True,
            "count": len(items),
            "items": items
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get items: {e}")
        raise HTTPException(status_code=500, detail=f"Item retrieval failed: {str(e)}")


# ==================== CUSTOMER TYPE OPERATIONS ====================

@router.get("/customer-types")
async def get_customer_types():
    """
    Get all CustomerType entities from QuickBooks.
    
    Returns:
        List of CustomerType records with ID and Name
    
    Example:
        GET /v1/quickbooks/customer-types
    """
    try:
        if not quickbooks_service.is_authenticated():
            raise HTTPException(status_code=401, detail="Not authenticated with QuickBooks")
        
        query = "SELECT * FROM CustomerType"
        response = await quickbooks_service._make_request("GET", "query", params={"query": query})
        types = response.get("QueryResponse", {}).get("CustomerType", [])
        
        return {
            "success": True,
            "count": len(types),
            "customer_types": types
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get customer types: {e}")
        raise HTTPException(status_code=500, detail=f"Customer type retrieval failed: {str(e)}")


# ==================== SYNC OPERATIONS ====================

@router.post("/sync-types")
async def sync_customer_types(dry_run: bool = Query(default=False)):
    """
    Sync CustomerTypeRef for all Google Sheets clients to 'GC Compliance' in QuickBooks.
    
    Process:
    1. Gets all clients from Google Sheets
    2. Matches with QuickBooks customers by name/email
    3. Updates CustomerTypeRef to {"name": "GC Compliance"}
    4. Skips customers already set correctly
    
    Query Parameters:
        dry_run: If true, preview changes without updating (default: false)
    
    Returns:
        Sync results with matched, updated, skipped, and error counts
    
    Example:
        POST /v1/quickbooks/sync-types (executes updates)
        POST /v1/quickbooks/sync-types?dry_run=true (preview only)
    """
    try:
        if not quickbooks_service.is_authenticated():
            raise HTTPException(status_code=401, detail="Not authenticated with QuickBooks")
        
        # Get Google Sheets service
        from app.services.google_service import google_service
        
        if not google_service or not google_service.sheets_service:
            raise HTTPException(status_code=503, detail="Google Sheets service not initialized")
        
        # Execute sync
        result = await quickbooks_service.sync_gc_customer_types_from_sheets(
            google_service=google_service,
            dry_run=dry_run
        )
        
        if result.get("status") == "failed":
            raise HTTPException(status_code=500, detail=result.get("error", "Sync failed"))
        
        return {
            "success": True,
            **result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to sync customer types: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Customer type sync failed: {str(e)}")
