"""
QuickBooks Online API Service

Handles OAuth2 authentication and API interactions with QuickBooks Online.
Supports customer, vendor, invoice, estimate, and bill management.
"""
import logging
import httpx
import base64
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from urllib.parse import urlencode

from app.config import settings

logger = logging.getLogger(__name__)

# Token storage sheet name
QB_TOKENS_SHEET = "QB_Tokens"


class QuickBooksService:
    """
    Service for interacting with QuickBooks Online API.
    
    Features:
    - OAuth2 authentication flow
    - Token management (access + refresh)
    - Customer, vendor, and invoice operations
    - Sync with Google Sheets data
    
    Note: Tokens are stored in memory. For production, consider
    storing in Google Sheets or a proper database.
    """
    
    def __init__(self):
        self.client_id = settings.QB_CLIENT_ID
        self.client_secret = settings.QB_CLIENT_SECRET
        self.redirect_uri = settings.QB_REDIRECT_URI
        self.environment = settings.QB_ENVIRONMENT
        
        # Set base URLs based on environment
        if self.environment == "production":
            self.base_url = "https://quickbooks.api.intuit.com/v3/company"
            self.auth_url = "https://appcenter.intuit.com/connect/oauth2"
            self.token_url = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"
        else:  # sandbox
            self.base_url = "https://sandbox-quickbooks.api.intuit.com/v3/company"
            self.auth_url = "https://appcenter.intuit.com/connect/oauth2"
            self.token_url = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"
        
        # Token storage (persisted in Google Sheets)
        self.realm_id: Optional[str] = None  # Company ID
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.token_expires_at: Optional[datetime] = None
        
        # Cache storage for QB data (5-minute TTL)
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._cache_ttl = timedelta(minutes=5)
        
        logger.info(f"QuickBooksService initialized ({self.environment} environment)")
        
        # Load tokens from Google Sheets on startup
        self._load_tokens_from_sheets()
    
    def _load_tokens_from_sheets(self) -> None:
        """Load QuickBooks tokens from Google Sheets."""
        try:
            from app.services.google_service import google_service
            
            if not google_service or not google_service.sheets_service:
                logger.warning("Google Sheets service not available for token loading")
                return
            
            # Try to read from QB_Tokens sheet
            result = google_service.sheets_service.spreadsheets().values().get(
                spreadsheetId=settings.SHEET_ID,
                range=f"{QB_TOKENS_SHEET}!A2:E2"
            ).execute()
            
            values = result.get('values', [])
            if values and len(values[0]) >= 4:
                row = values[0]
                self.realm_id = row[0] if len(row) > 0 else None
                self.access_token = row[1] if len(row) > 1 else None
                self.refresh_token = row[2] if len(row) > 2 else None
                expires_str = row[3] if len(row) > 3 else None
                
                if expires_str:
                    self.token_expires_at = datetime.fromisoformat(expires_str)
                
                logger.info(f"Loaded tokens from Google Sheets for realm: {self.realm_id}")
            else:
                logger.info("No tokens found in Google Sheets")
                
        except Exception as e:
            logger.warning(f"Could not load tokens from sheets (sheet may not exist yet): {e}")
    
    def _save_tokens_to_sheets(self) -> None:
        """Save QuickBooks tokens to Google Sheets."""
        try:
            from app.services.google_service import google_service
            
            if not google_service or not google_service.sheets_service:
                logger.warning("Google Sheets service not available for token saving")
                return
            
            # Prepare data
            expires_str = self.token_expires_at.isoformat() if self.token_expires_at else ""
            updated_at = datetime.now().isoformat()
            
            values = [[
                self.realm_id or "",
                self.access_token or "",
                self.refresh_token or "",
                expires_str,
                updated_at
            ]]
            
            # Try to update existing row, or create sheet if it doesn't exist
            try:
                google_service.sheets_service.spreadsheets().values().update(
                    spreadsheetId=settings.SHEET_ID,
                    range=f"{QB_TOKENS_SHEET}!A2:E2",
                    valueInputOption="RAW",
                    body={"values": values}
                ).execute()
                logger.info("Saved tokens to Google Sheets")
            except Exception as update_error:
                # Sheet might not exist, try to create it
                logger.info(f"Creating {QB_TOKENS_SHEET} sheet...")
                self._create_tokens_sheet()
                # Retry update
                google_service.sheets_service.spreadsheets().values().update(
                    spreadsheetId=settings.SHEET_ID,
                    range=f"{QB_TOKENS_SHEET}!A2:E2",
                    valueInputOption="RAW",
                    body={"values": values}
                ).execute()
                logger.info("Created sheet and saved tokens")
                
        except Exception as e:
            logger.error(f"Failed to save tokens to sheets: {e}")
    
    def _create_tokens_sheet(self) -> None:
        """Create the QB_Tokens sheet with headers."""
        try:
            from app.services.google_service import google_service
            
            # Add new sheet
            request_body = {
                "requests": [{
                    "addSheet": {
                        "properties": {
                            "title": QB_TOKENS_SHEET,
                            "gridProperties": {
                                "rowCount": 10,
                                "columnCount": 5
                            }
                        }
                    }
                }]
            }
            
            google_service.sheets_service.spreadsheets().batchUpdate(
                spreadsheetId=settings.SHEET_ID,
                body=request_body
            ).execute()
            
            # Add headers
            headers = [["Realm ID", "Access Token", "Refresh Token", "Expires At", "Updated At"]]
            google_service.sheets_service.spreadsheets().values().update(
                spreadsheetId=settings.SHEET_ID,
                range=f"{QB_TOKENS_SHEET}!A1:E1",
                valueInputOption="RAW",
                body={"values": headers}
            ).execute()
            
            logger.info(f"Created {QB_TOKENS_SHEET} sheet with headers")
            
        except Exception as e:
            logger.error(f"Failed to create tokens sheet: {e}")
    
    def _get_cache(self, key: str) -> Optional[Any]:
        """Get value from cache if still valid."""
        if key in self._cache:
            cached_data = self._cache[key]
            if datetime.now() < cached_data['expires_at']:
                logger.info(f"Cache HIT for {key} (expires in {(cached_data['expires_at'] - datetime.now()).seconds}s)")
                return cached_data['data']
            else:
                # Cache expired
                logger.info(f"Cache EXPIRED for {key}")
                del self._cache[key]
        
        logger.info(f"Cache MISS for {key}")
        return None
    
    def _set_cache(self, key: str, data: Any) -> None:
        """Store value in cache with TTL."""
        expires_at = datetime.now() + self._cache_ttl
        self._cache[key] = {
            'data': data,
            'expires_at': expires_at
        }
        logger.info(f"Cache SET for {key} (TTL: {self._cache_ttl.seconds}s)")
    
    def _invalidate_cache(self, key: Optional[str] = None) -> None:
        """Invalidate cache (specific key or all keys)."""
        if key:
            if key in self._cache:
                del self._cache[key]
                logger.info(f"Cache INVALIDATED for {key}")
        else:
            self._cache.clear()
            logger.info("Cache INVALIDATED (all keys)")
    
    def get_auth_url(self, state: str = "randomstate") -> str:
        """
        Generate QuickBooks OAuth2 authorization URL.
        
        Args:
            state: CSRF protection state parameter
        
        Returns:
            Authorization URL for user to visit
        
        Example:
            url = qb_service.get_auth_url()
            # Redirect user to this URL in browser
        """
        params = {
            "client_id": self.client_id,
            "scope": "com.intuit.quickbooks.accounting openid profile email phone address",
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "state": state
        }
        
        auth_url = f"{self.auth_url}?{urlencode(params)}"
        logger.info(f"Generated auth URL for state: {state}")
        return auth_url
    
    async def exchange_code_for_token(self, code: str, realm_id: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access and refresh tokens.
        
        Args:
            code: Authorization code from OAuth callback
            realm_id: Company ID (realmId) from callback
        
        Returns:
            Token response with access_token, refresh_token, expires_in
        
        Example:
            tokens = await qb_service.exchange_code_for_token("auth_code", "company_id")
        """
        try:
            # Create Basic auth header
            credentials = f"{self.client_id}:{self.client_secret}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()
            
            headers = {
                "Authorization": f"Basic {encoded_credentials}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            data = {
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": self.redirect_uri
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.token_url,
                    headers=headers,
                    data=data
                )
                response.raise_for_status()
                token_data = response.json()
            
            # Store tokens
            self.access_token = token_data["access_token"]
            self.refresh_token = token_data["refresh_token"]
            self.realm_id = realm_id
            self.token_expires_at = datetime.now() + timedelta(seconds=token_data["expires_in"])
            
            # Save tokens to Google Sheets for persistence
            self._save_tokens_to_sheets()
            
            logger.info(f"Successfully exchanged code for tokens. Realm ID: {realm_id}")
            
            return {
                "access_token": self.access_token,
                "refresh_token": self.refresh_token,
                "expires_in": token_data["expires_in"],
                "realm_id": self.realm_id,
                "token_type": token_data.get("token_type", "Bearer")
            }
            
        except Exception as e:
            logger.error(f"Failed to exchange code for token: {e}")
            raise
    
    async def refresh_access_token(self) -> Dict[str, Any]:
        """
        Refresh the access token using the refresh token.
        
        Returns:
            New token data
        
        Example:
            tokens = await qb_service.refresh_access_token()
        """
        if not self.refresh_token:
            raise ValueError("No refresh token available")
        
        try:
            credentials = f"{self.client_id}:{self.client_secret}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()
            
            headers = {
                "Authorization": f"Basic {encoded_credentials}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            data = {
                "grant_type": "refresh_token",
                "refresh_token": self.refresh_token
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.token_url,
                    headers=headers,
                    data=data
                )
                response.raise_for_status()
                token_data = response.json()
            
            # Update tokens
            self.access_token = token_data["access_token"]
            self.refresh_token = token_data["refresh_token"]
            self.token_expires_at = datetime.now() + timedelta(seconds=token_data["expires_in"])
            
            # Save refreshed tokens to Google Sheets
            self._save_tokens_to_sheets()
            
            logger.info("Successfully refreshed access token")
            
            return {
                "access_token": self.access_token,
                "refresh_token": self.refresh_token,
                "expires_in": token_data["expires_in"]
            }
            
        except Exception as e:
            logger.error(f"Failed to refresh token: {e}")
            raise
    
    async def _ensure_valid_token(self) -> None:
        """Ensure access token is valid, refresh if needed."""
        if not self.access_token:
            raise ValueError("Not authenticated. Please complete OAuth flow first.")
        
        # Refresh if token expires in less than 5 minutes
        if self.token_expires_at and datetime.now() >= self.token_expires_at - timedelta(minutes=5):
            logger.info("Token expiring soon, refreshing...")
            await self.refresh_access_token()
    
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make authenticated request to QuickBooks API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (e.g., "customer")
            data: Request body for POST/PUT
            params: Query parameters
        
        Returns:
            API response as dictionary
        """
        await self._ensure_valid_token()
        
        url = f"{self.base_url}/{self.realm_id}/{endpoint}"
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                if method.upper() == "GET":
                    response = await client.get(url, headers=headers, params=params)
                elif method.upper() == "POST":
                    response = await client.post(url, headers=headers, json=data)
                elif method.upper() == "PUT":
                    response = await client.put(url, headers=headers, json=data)
                elif method.upper() == "DELETE":
                    response = await client.delete(url, headers=headers, params=params)
                else:
                    raise ValueError(f"Unsupported method: {method}")
                
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPStatusError as e:
            logger.error(f"QuickBooks API error: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Request failed: {e}")
            raise
    
    # ==================== CUSTOMER OPERATIONS ====================
    
    async def get_customers(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """
        Retrieve all customers from QuickBooks with caching.
        
        Cache is invalidated after create/update operations.
        
        Args:
            active_only: Only return active customers
        
        Returns:
            List of customer records
        
        Example:
            customers = await qb_service.get_customers()
        """
        # Build cache key from filters
        cache_key = f"customers_{active_only}"
        
        # Check cache first
        cached = self._get_cache(cache_key)
        if cached is not None:
            return cached
        
        # Cache miss - fetch from API
        query = "SELECT * FROM Customer"
        if active_only:
            query += " WHERE Active = true"
        
        params = {"query": query}
        
        response = await self._make_request("GET", "query", params=params)
        customers = response.get("QueryResponse", {}).get("Customer", [])
        
        logger.info(f"Retrieved {len(customers)} customers from QB API")
        
        # Store in cache
        self._set_cache(cache_key, customers)
        
        return customers
    
    async def create_customer(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new customer in QuickBooks.
        
        Args:
            customer_data: Customer information
                Required: DisplayName
                Optional: CompanyName, GivenName, FamilyName, PrimaryPhone, 
                         PrimaryEmailAddr, BillAddr, etc.
        
        Returns:
            Created customer record
        
        Example:
            customer = await qb_service.create_customer({
                "DisplayName": "John Doe",
                "PrimaryEmailAddr": {"Address": "john@example.com"},
                "PrimaryPhone": {"FreeFormNumber": "(555) 123-4567"}
            })
        """
        response = await self._make_request("POST", "customer", data=customer_data)
        customer = response.get("Customer", {})
        
        # Invalidate customer cache after creation
        self._invalidate_cache()  # Clear all customer caches
        logger.info(f"Created customer: {customer.get('DisplayName')} - cache invalidated")
        
        return customer
    
    async def get_customer_by_id(self, customer_id: str) -> Dict[str, Any]:
        """Get a specific customer by QuickBooks ID."""
        response = await self._make_request("GET", f"customer/{customer_id}")
        return response.get("Customer", {})
    
    # ==================== INVOICE OPERATIONS ====================
    
    async def get_invoices(
        self, 
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        customer_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve invoices from QuickBooks with caching.
        
        Cache key includes filters to ensure correct data.
        Cache is invalidated after create/update/delete operations.
        
        Args:
            start_date: Filter by TxnDate >= start_date (YYYY-MM-DD)
            end_date: Filter by TxnDate <= end_date (YYYY-MM-DD)
            customer_id: Filter by specific customer
        
        Returns:
            List of invoice records
        
        Example:
            invoices = await qb_service.get_invoices(customer_id="123")
        """
        # Build cache key from filters
        cache_key = f"invoices_{start_date}_{end_date}_{customer_id}"
        
        # Check cache first
        cached = self._get_cache(cache_key)
        if cached is not None:
            return cached
        
        # Cache miss - fetch from API
        query = "SELECT * FROM Invoice"
        conditions = []
        
        if customer_id:
            conditions.append(f"CustomerRef = '{customer_id}'")
        if start_date:
            conditions.append(f"TxnDate >= '{start_date}'")
        if end_date:
            conditions.append(f"TxnDate <= '{end_date}'")
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDERBY TxnDate DESC"
        
        params = {"query": query}
        response = await self._make_request("GET", "query", params=params)
        invoices = response.get("QueryResponse", {}).get("Invoice", [])
        
        logger.info(f"Retrieved {len(invoices)} invoices from QB API")
        
        # Store in cache
        self._set_cache(cache_key, invoices)
        
        return invoices
        return invoices
    
    async def create_invoice(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new invoice in QuickBooks.
        
        Args:
            invoice_data: Invoice information
                Required: CustomerRef, Line (array of line items)
                Optional: TxnDate, DueDate, DocNumber, etc.
        
        Returns:
            Created invoice record
        
        Example:
            invoice = await qb_service.create_invoice({
                "CustomerRef": {"value": "123"},
                "Line": [{
                    "Amount": 1000.00,
                    "DetailType": "SalesItemLineDetail",
                    "SalesItemLineDetail": {
                        "ItemRef": {"value": "1"},  # Item/Service ID
                        "Qty": 1
                    },
                    "Description": "Renovation work"
                }]
            })
        """
        response = await self._make_request("POST", "invoice", data=invoice_data)
        invoice = response.get("Invoice", {})
        
        # Invalidate invoice cache after creation
        self._invalidate_cache()  # Clear all invoice caches
        logger.info(f"Created invoice: {invoice.get('DocNumber')} - cache invalidated")
        
        return invoice
    
    async def get_invoice_by_id(self, invoice_id: str) -> Dict[str, Any]:
        """Get a specific invoice by QuickBooks ID."""
        response = await self._make_request("GET", f"invoice/{invoice_id}")
        return response.get("Invoice", {})
    
    async def update_invoice(self, invoice_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing invoice in QuickBooks.
        
        Args:
            invoice_id: QuickBooks invoice ID
            updates: Fields to update (can include Amount, DueDate, Line items, etc.)
                Note: Must include the full invoice object with SyncToken for sparse updates
        
        Returns:
            Updated invoice record
            
        Example:
            # Get the existing invoice first to get SyncToken
            invoice = await qb_service.get_invoice_by_id("123")
            
            # Update specific fields
            updated = await qb_service.update_invoice("123", {
                **invoice,  # Include all existing fields
                "DueDate": "2025-12-31",
                "Line": [...updated line items...]
            })
        """
        # QuickBooks requires a sparse update with SyncToken
        # We need to get the existing invoice first if not provided
        if "SyncToken" not in updates or "Id" not in updates:
            existing_invoice = await self.get_invoice_by_id(invoice_id)
            updates["Id"] = invoice_id
            updates["SyncToken"] = existing_invoice.get("SyncToken")
        
        response = await self._make_request("POST", "invoice", data=updates, params={"operation": "update"})
        invoice = response.get("Invoice", {})
        
        # Invalidate invoice cache after update
        self._invalidate_cache()  # Clear all invoice caches
        logger.info(f"Updated invoice: {invoice.get('DocNumber')} - cache invalidated")
        
        return invoice
    
    # ==================== ESTIMATE OPERATIONS ====================
    
    async def create_estimate(self, estimate_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create an estimate in QuickBooks.
        
        Args:
            estimate_data: Estimate information (similar structure to invoice)
        
        Returns:
            Created estimate record
        """
        response = await self._make_request("POST", "estimate", data=estimate_data)
        estimate = response.get("Estimate", {})
        
        logger.info(f"Created estimate: {estimate.get('DocNumber')}")
        return estimate
    
    # ==================== BILL/VENDOR OPERATIONS ====================
    
    async def get_vendors(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """Retrieve all vendors from QuickBooks."""
        query = "SELECT * FROM Vendor"
        if active_only:
            query += " WHERE Active = true"
        
        params = {"query": query}
        response = await self._make_request("GET", "query", params=params)
        vendors = response.get("QueryResponse", {}).get("Vendor", [])
        
        logger.info(f"Retrieved {len(vendors)} vendors")
        return vendors
    
    async def create_bill(self, bill_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a bill in QuickBooks.
        
        Args:
            bill_data: Bill information
                Required: VendorRef, Line (array of line items)
        
        Returns:
            Created bill record
        """
        response = await self._make_request("POST", "bill", data=bill_data)
        bill = response.get("Bill", {})
        
        logger.info(f"Created bill: {bill.get('DocNumber')}")
        return bill
    
    # ==================== ITEMS/SERVICES ====================
    
    async def get_items(self, item_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieve items/services from QuickBooks.
        
        Args:
            item_type: Filter by type (Service, Inventory, NonInventory, etc.)
        
        Returns:
            List of item records
        """
        query = "SELECT * FROM Item"
        if item_type:
            query += f" WHERE Type = '{item_type}'"
        
        params = {"query": query}
        response = await self._make_request("GET", "query", params=params)
        items = response.get("QueryResponse", {}).get("Item", [])
        
        logger.info(f"Retrieved {len(items)} items")
        return items
    
    # ==================== COMPANY INFO ====================
    
    async def get_company_info(self) -> Dict[str, Any]:
        """Get company information from QuickBooks."""
        if not self.realm_id:
            raise ValueError("Realm ID not set. Please authenticate first.")
        response = await self._make_request("GET", f"companyinfo/{self.realm_id}")
        return response.get("CompanyInfo", {})
    
    # ==================== STATUS & HEALTH ====================
    
    def is_authenticated(self) -> bool:
        """
        Check if service has valid authentication.
        Lazy-loads tokens from Google Sheets if not in memory.
        """
        # If tokens not in memory, try to load from Sheets
        if not self.access_token or not self.realm_id:
            self._load_tokens_from_sheets()
        
        return bool(self.access_token and self.realm_id)
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current service status.
        Ensures tokens are loaded before reporting status.
        """
        # Ensure tokens loaded
        if not self.access_token or not self.realm_id:
            self._load_tokens_from_sheets()
        
        return {
            "authenticated": bool(self.access_token and self.realm_id),
            "realm_id": self.realm_id,
            "environment": self.environment,
            "token_expires_at": self.token_expires_at.isoformat() if self.token_expires_at else None
        }


# Global QuickBooks service instance
quickbooks_service = QuickBooksService()
