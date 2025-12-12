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
from app.utils.sanitizer import sanitize_log_message

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
        
        # Database session for token storage (optional - falls back to Sheets if not provided)
        self.db: Optional[Any] = None
        
        logger.info(f"QuickBooksService initialized ({self.environment} environment)")
        
        # Tokens will be loaded by startup event in main.py
        # Don't load here to avoid event loop conflicts
    
    def set_db_session(self, db: Any):
        """Set database session for token storage (enables database mode)"""
        self.db = db
        logger.info("Database session set for QuickBooks token storage")
    
    async def _load_tokens_from_db(self) -> bool:
        """
        Load QuickBooks tokens from PostgreSQL database.
        
        Returns:
            True if tokens loaded, False otherwise
        """
        if not self.db:
            return False
        
        try:
            from sqlalchemy import select
            from app.db.models import QuickBooksToken
            
            # Get the most recent active token
            result = await self.db.execute(
                select(QuickBooksToken)
                .where(QuickBooksToken.is_active == True)
                .order_by(QuickBooksToken.updated_at.desc())
                .limit(1)
            )
            token_record = result.scalar_one_or_none()
            
            if not token_record:
                logger.info("No QuickBooks tokens found in database")
                return False
            
            # Load token data
            self.realm_id = token_record.realm_id
            self.access_token = token_record.access_token
            self.refresh_token = token_record.refresh_token
            self.token_expires_at = token_record.access_token_expires_at.replace(tzinfo=None)  # Remove timezone for compatibility
            
            logger.info(f"Loaded tokens from database for realm: {self.realm_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading tokens from database: {e}", exc_info=True)
            return False
    
    async def _save_tokens_to_db(self) -> bool:
        """
        Save QuickBooks tokens to PostgreSQL database.
        
        Returns:
            True if saved, False otherwise
        """
        if not self.db:
            return False
        
        try:
            from sqlalchemy import select
            from app.db.models import QuickBooksToken
            
            # Calculate expiration times
            now = datetime.utcnow()
            access_expires_at = self.token_expires_at if self.token_expires_at else now + timedelta(hours=1)
            refresh_expires_at = now + timedelta(days=100)  # QB refresh tokens last 100 days
            
            # Deactivate old tokens for this realm
            if self.realm_id:
                old_tokens = await self.db.execute(
                    select(QuickBooksToken).where(QuickBooksToken.realm_id == self.realm_id)
                )
                for old_token in old_tokens.scalars():
                    old_token.is_active = False
            
            # Create new token record
            new_token = QuickBooksToken(
                realm_id=self.realm_id,
                access_token=self.access_token,
                refresh_token=self.refresh_token,
                access_token_expires_at=access_expires_at,
                refresh_token_expires_at=refresh_expires_at,
                environment=self.environment,
                is_active=True
            )
            
            self.db.add(new_token)
            await self.db.commit()
            
            logger.info(f"Saved tokens to database for realm: {self.realm_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving tokens to database: {e}", exc_info=True)
            if self.db:
                await self.db.rollback()
            return False
    
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
            
            # Save refreshed tokens to database
            if self.db:
                saved = await self._save_tokens_to_db()
                if saved:
                    logger.info("Tokens saved to database after refresh")
                else:
                    logger.error("Failed to save tokens to database after refresh")
            else:
                logger.warning("Database session not available - tokens not persisted")
            
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
            # Sanitize response to avoid leaking QB data or tokens
            logger.error(f"QuickBooks API error: {sanitize_log_message(e.response.text)}")
            raise
        except Exception as e:
            logger.error(f"Request failed: {e}")
            raise
    
    # ==================== CUSTOMER OPERATIONS ====================
    
    async def _get_customer_type_id(self, type_name: str) -> Optional[str]:
        """
        Get CustomerType ID by name.
        
        Args:
            type_name: Name of the CustomerType (e.g., "GC Compliance")
        
        Returns:
            CustomerType ID or None if not found
        """
        cache_key = f"customer_type_{type_name}"
        cached = self._get_cache(cache_key)
        if cached is not None:
            return cached
        
        query = f"SELECT * FROM CustomerType WHERE Name = '{type_name}'"
        try:
            response = await self._make_request("GET", "query", params={"query": query})
            types = response.get("QueryResponse", {}).get("CustomerType", [])
            
            if types:
                type_id = types[0].get("Id")
                self._set_cache(cache_key, type_id)
                logger.info(f"CustomerType '{type_name}' resolved to ID: {type_id}")
                return type_id
            else:
                logger.warning(f"CustomerType '{type_name}' not found in QuickBooks")
                return None
        except Exception as e:
            logger.error(f"Failed to query CustomerType: {e}")
            return None
    
    async def get_customers(self, active_only: bool = True, customer_type: Optional[str] = "GC Compliance") -> List[Dict[str, Any]]:
        """
        Retrieve all customers from QuickBooks with caching.
        
        Cache is invalidated after create/update operations.
        
        Args:
            active_only: Only return active customers
            customer_type: Filter by CustomerType name (default: "GC Compliance" for permit clients). Set to None for all customers.
        
        Returns:
            List of customer records
        
        Example:
            customers = await qb_service.get_customers()  # Returns only GC Compliance customers
            all_customers = await qb_service.get_customers(customer_type=None)  # Returns all customers
        """
        # Build cache key from filters
        cache_key = f"customers_{active_only}_{customer_type}"
        
        # Check cache first
        cached = self._get_cache(cache_key)
        if cached is not None:
            return cached
        
        # Resolve CustomerType name to ID if filtering
        customer_type_id = None
        if customer_type:
            customer_type_id = await self._get_customer_type_id(customer_type)
            if not customer_type_id:
                logger.warning(f"CustomerType '{customer_type}' not found - returning empty list")
                return []
        
        # Cache miss - fetch from API
        query = "SELECT * FROM Customer"
        if active_only:
            query += " WHERE Active = true"
        
        params = {"query": query}
        
        response = await self._make_request("GET", "query", params=params)
        customers = response.get("QueryResponse", {}).get("Customer", [])
        
        # Post-filter by CustomerType ID (QB API doesn't support WHERE on CustomerTypeRef)
        if customer_type_id:
            customers = [
                c for c in customers 
                if c.get('CustomerTypeRef', {}).get('value') == customer_type_id
            ]
            logger.info(f"Retrieved {len(customers)} customers (filtered to CustomerType: {customer_type} [ID: {customer_type_id}])")
        else:
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
        customer_id: Optional[str] = None,
        customer_type: Optional[str] = "GC Compliance"
    ) -> List[Dict[str, Any]]:
        """
        Retrieve invoices from QuickBooks with caching.
        
        Cache key includes filters to ensure correct data.
        Cache is invalidated after create/update/delete operations.
        
        Args:
            start_date: Filter by TxnDate >= start_date (YYYY-MM-DD)
            end_date: Filter by TxnDate <= end_date (YYYY-MM-DD)
            customer_id: Filter by specific customer
            customer_type: Filter by CustomerType (default: "GC Compliance" to show only permit clients)
                          Set to None to retrieve all invoices regardless of customer type
        
        Returns:
            List of invoice records
        
        Example:
            invoices = await qb_service.get_invoices(customer_id="123")
        """
        # Build cache key from filters
        cache_key = f"invoices_{start_date}_{end_date}_{customer_id}_{customer_type}"
        
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
        
        # Post-filter by CustomerType if specified
        if customer_type:
            # Get GC Compliance customer IDs for filtering
            gc_customers = await self.get_customers(customer_type=customer_type)
            gc_customer_ids = set(str(c.get('Id')) for c in gc_customers)
            
            # Filter invoices to only GC Compliance customers
            invoices = [
                inv for inv in invoices
                if str(inv.get('CustomerRef', {}).get('value', '')) in gc_customer_ids
            ]
            logger.info(f"Retrieved {len(invoices)} invoices (filtered to CustomerType: {customer_type})")
        else:
            logger.info(f"Retrieved {len(invoices)} invoices from QB API")
        
        # Store in cache
        self._set_cache(cache_key, invoices)
        
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
    
    # ==================== PAYMENT OPERATIONS ====================
    
    async def get_payments(
        self,
        customer_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve payments from QuickBooks with optional filters.
        
        Args:
            customer_id: Filter by QB customer ID
            start_date: Filter payments after this date (YYYY-MM-DD)
            end_date: Filter payments before this date (YYYY-MM-DD)
        
        Returns:
            List of payment records
        
        Example:
            payments = await qb_service.get_payments(start_date="2025-01-01")
        """
        self._check_authentication()
        
        # Build query
        query = "SELECT * FROM Payment"
        conditions = []
        
        if customer_id:
            conditions.append(f"CustomerRef = '{customer_id}'")
        if start_date:
            conditions.append(f"TxnDate >= '{start_date}'")
        if end_date:
            conditions.append(f"TxnDate <= '{end_date}'")
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " MAXRESULTS 1000"
        
        response = await self._make_request(
            method="GET",
            endpoint="/query",
            params={"query": query}
        )
        
        payments = response.get("QueryResponse", {}).get("Payment", [])
        logger.info(f"Retrieved {len(payments)} payments from QB API")
        
        return payments
    
    async def get_payment_by_id(self, payment_id: str) -> Dict[str, Any]:
        """
        Get a specific payment by QB Payment ID.
        
        Args:
            payment_id: QuickBooks Payment ID
        
        Returns:
            Payment record
        """
        self._check_authentication()
        
        response = await self._make_request(
            method="GET",
            endpoint=f"/payment/{payment_id}",
            params={"minorversion": "73"}
        )
        
        return response.get("Payment", {})
    
    async def sync_payments_to_sheets(
        self,
        google_service,
        days_back: int = 90
    ) -> Dict[str, Any]:
        """
        Sync QuickBooks payments to Google Sheets Payments tab.
        
        Args:
            google_service: Google Sheets service instance
            days_back: How many days back to sync (default 90)
        
        Returns:
            Sync summary with counts
        
        Example:
            result = await qb_service.sync_payments_to_sheets(google_service, days_back=30)
            # Returns: {"status": "success", "synced": 5, "new": 3, "updated": 2}
        """
        from datetime import datetime, timedelta
        import uuid
        
        start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        
        logger.info(f"Starting payment sync from {start_date}")
        
        # Get QB payments
        qb_payments = await self.get_payments(start_date=start_date)
        logger.info(f"Retrieved {len(qb_payments)} payments from QuickBooks")
        
        # Get existing payments from Sheets
        existing_payments = await google_service.get_sheet_data('Payments')
        existing_qb_ids = {p.get('QB Payment ID') for p in existing_payments if p.get('QB Payment ID')}
        
        logger.info(f"Found {len(existing_qb_ids)} existing payments in Sheets")
        
        synced_count = 0
        new_count = 0
        updated_count = 0
        errors = []
        
        for qb_payment in qb_payments:
            try:
                payment_id = qb_payment.get('Id')
                
                # Map QB payment to Sheets structure
                sheet_payment = await self._map_qb_payment_to_sheet(qb_payment, google_service)
                
                if payment_id in existing_qb_ids:
                    # Update existing - find row by QB Payment ID
                    row_index = None
                    for idx, p in enumerate(existing_payments):
                        if p.get('QB Payment ID') == payment_id:
                            row_index = idx + 2  # +2 for header row and 0-indexing
                            break
                    
                    if row_index:
                        # Update the row
                        values = [list(sheet_payment.values())]
                        await google_service.update_range(
                            sheet_name='Payments',
                            range_name=f'A{row_index}:K{row_index}',
                            values=values
                        )
                        updated_count += 1
                        logger.info(f"Updated payment: {payment_id}")
                else:
                    # Insert new payment
                    await google_service.append_row('Payments', list(sheet_payment.values()))
                    new_count += 1
                    logger.info(f"Added new payment: {payment_id}")
                
                synced_count += 1
                
            except Exception as e:
                error_msg = f"Error syncing payment {qb_payment.get('Id')}: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)
        
        result = {
            "status": "success" if not errors else "partial",
            "synced": synced_count,
            "new": new_count,
            "updated": updated_count,
            "errors": errors if errors else None
        }
        
        logger.info(f"Payment sync complete: {result}")
        return result
    
    async def _map_qb_payment_to_sheet(
        self,
        qb_payment: Dict[str, Any],
        google_service
    ) -> Dict[str, Any]:
        """
        Map QuickBooks Payment entity to Sheets Payments row.
        
        Args:
            qb_payment: QB Payment entity
            google_service: Google service for client lookup
        
        Returns:
            Dictionary with Sheets column values
        """
        import uuid
        
        # Extract QB fields
        qb_id = qb_payment.get('Id', '')
        customer_ref = qb_payment.get('CustomerRef', {}).get('value', '')
        total_amt = qb_payment.get('TotalAmt', 0)
        txn_date = qb_payment.get('TxnDate', '')
        payment_method_ref = qb_payment.get('PaymentMethodRef', {})
        payment_method = payment_method_ref.get('name', 'Unknown') if payment_method_ref else 'Unknown'
        
        # Extract linked invoice ID
        invoice_id = ''
        lines = qb_payment.get('Line', [])
        for line in lines:
            linked_txns = line.get('LinkedTxn', [])
            for txn in linked_txns:
                if txn.get('TxnType') == 'Invoice':
                    invoice_id = txn.get('TxnId', '')
                    break
            if invoice_id:
                break
        
        # Resolve Client ID from QB Customer ID
        # Look up in Clients sheet for matching QBO Client ID
        clients = await google_service.get_sheet_data('Clients')
        client_id = ''
        for client in clients:
            if str(client.get('QBO Client ID', '')).strip() == str(customer_ref).strip():
                client_id = client.get('Client ID', '')
                break
        
        # Generate Payment ID if this is a new payment
        payment_id = f"PAY-{uuid.uuid4().hex[:8]}"
        
        # Map payment method names
        method_mapping = {
            'Cash': 'Cash',
            'Check': 'Check',
            'Credit Card': 'Credit Card',
            'Bank Transfer': 'ACH',
            'Other': 'Other'
        }
        mapped_method = method_mapping.get(payment_method, 'Other')
        
        return {
            'Payment ID': payment_id,
            'Invoice ID': invoice_id,
            'Project ID': '',  # Will be filled later if we link invoice to project
            'Client ID': client_id,
            'Amount': total_amt,
            'Payment Date': txn_date,
            'Payment Method': mapped_method,
            'Status': 'Completed',  # QB payments are completed
            'QB Payment ID': qb_id,
            'Transaction ID': '',
            'Notes': f'Synced from QuickBooks on {datetime.now().strftime("%Y-%m-%d %H:%M")}'
        }
    
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
    
    # ==================== CUSTOMER TYPE SYNC ====================
    
    async def update_customer(
        self, 
        customer_id: str, 
        customer_data: Dict[str, Any],
        sync_token: str,
        existing_customer: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Update an existing customer in QuickBooks.
        
        IMPORTANT: QuickBooks requires name fields (GivenName, FamilyName, or DisplayName) 
        to be present in EVERY update, even when updating other fields like address.
        
        Args:
            customer_id: QuickBooks customer ID
            customer_data: Updated customer information (sparse - only fields to change)
            sync_token: Current SyncToken for optimistic locking
            existing_customer: Full existing customer record (optional but recommended)
        
        Returns:
            Updated customer record
        """
        # Start with base required fields
        update_data = {
            "Id": customer_id,
            "SyncToken": sync_token
        }
        
        # If we have the existing customer, merge in required name fields
        # (QuickBooks validation requires at least one name field present)
        if existing_customer:
            # Preserve existing name fields if not being updated
            name_fields = ['GivenName', 'FamilyName', 'MiddleName', 'DisplayName', 'Title', 'Suffix']
            for field in name_fields:
                if field in existing_customer and existing_customer[field]:
                    update_data[field] = existing_customer[field]
        
        # Apply user's updates (will override any existing fields copied above)
        update_data.update(customer_data)
        
        # Ensure at least DisplayName exists (QuickBooks requirement)
        if not any(update_data.get(field) for field in ['GivenName', 'FamilyName', 'DisplayName']):
            # If still no name, try to use DisplayName from existing
            if existing_customer and existing_customer.get('DisplayName'):
                update_data['DisplayName'] = existing_customer['DisplayName']
        
        response = await self._make_request("POST", "customer", data=update_data)
        customer = response.get("Customer", {})
        
        # Invalidate customer cache after update
        self._invalidate_cache()
        logger.info(f"Updated customer ID {customer_id}: {customer.get('DisplayName')} - cache invalidated")
        
        return customer
    
    async def sync_gc_customer_types_from_sheets(
        self,
        google_service,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Sync CustomerTypeRef to 'GC Compliance' for all clients in Google Sheets.
        
        Process:
        1. Get all clients from Google Sheets
        2. Get all QB customers
        3. Match by name or email
        4. Update QB customer with CustomerTypeRef = {"name": "GC Compliance"}
        5. Skip if already set correctly
        
        Args:
            google_service: Google Sheets service instance
            dry_run: If True, preview changes without updating
        
        Returns:
            Dictionary with sync results
        """
        try:
            logger.info(f"[QB TYPE SYNC] Starting CustomerTypeRef sync (dry_run={dry_run})")
            
            # Get all clients from Sheets
            clients_data = await google_service.get_clients_data()
            logger.info(f"[QB TYPE SYNC] Found {len(clients_data)} clients in Google Sheets")
            
            # Get ALL QB customers (no filter for sync operation)
            qb_customers = await self.get_customers(customer_type=None)
            logger.info(f"[QB TYPE SYNC] Found {len(qb_customers)} customers in QuickBooks")
            
            # Build lookup maps for efficient matching
            qb_by_name = {}
            qb_by_email = {}
            
            for customer in qb_customers:
                name = customer.get('DisplayName', '').strip().lower()
                email_obj = customer.get('PrimaryEmailAddr', {})
                email = email_obj.get('Address', '').strip().lower() if email_obj else ''
                
                if name:
                    qb_by_name[name] = customer
                if email:
                    qb_by_email[email] = customer
            
            # Process each Sheet client
            matched = []
            skipped = []
            updated = []
            not_found = []
            errors = []
            
            for client in clients_data:
                client_name = (client.get('Full Name') or client.get('Client Name', '')).strip()
                client_email = client.get('Email', '').strip()
                
                if not client_name:
                    continue
                
                # Try to find matching QB customer
                qb_customer = None
                match_method = None
                
                # Match by name (exact or without LLC variations)
                name_lower = client_name.lower()
                if name_lower in qb_by_name:
                    qb_customer = qb_by_name[name_lower]
                    match_method = "exact name"
                else:
                    # Try without LLC suffix
                    name_without_llc = name_lower.replace(' llc', '').replace(', llc', '').strip()
                    if name_without_llc in qb_by_name:
                        qb_customer = qb_by_name[name_without_llc]
                        match_method = "name (without LLC)"
                
                # Fallback to email
                if not qb_customer and client_email:
                    email_lower = client_email.lower()
                    if email_lower in qb_by_email:
                        qb_customer = qb_by_email[email_lower]
                        match_method = "email"
                
                if not qb_customer:
                    not_found.append({
                        "client_name": client_name,
                        "email": client_email
                    })
                    continue
                
                # Check current CustomerTypeRef
                current_type_ref = qb_customer.get('CustomerTypeRef', {})
                current_type_id = current_type_ref.get('value', '').strip()
                
                # Get GC Compliance type ID for comparison
                gc_type_id = await self._get_customer_type_id("GC Compliance")
                
                match_info = {
                    "client_name": client_name,
                    "qb_id": qb_customer.get('Id'),
                    "qb_name": qb_customer.get('DisplayName'),
                    "match_method": match_method,
                    "current_type_id": current_type_id,
                    "already_gc": current_type_id == gc_type_id
                }
                
                if current_type_id == gc_type_id:
                    skipped.append(match_info)
                    logger.debug(f"[QB TYPE SYNC] Skipping {client_name} - already GC Compliance (ID: {gc_type_id})")
                    continue
                
                matched.append(match_info)
                
                # Update if not dry run
                if not dry_run:
                    try:
                        # Get full customer record to ensure we have SyncToken
                        full_customer = await self.get_customer_by_id(qb_customer['Id'])
                        sync_token = full_customer.get('SyncToken')
                        
                        if not sync_token:
                            errors.append({
                                **match_info,
                                "error": "Missing SyncToken"
                            })
                            continue
                        
                        # Update with CustomerTypeRef (use ID, not name)
                        update_data = {
                            "CustomerTypeRef": {
                                "value": gc_type_id
                            }
                        }
                        
                        updated_customer = await self.update_customer(
                            customer_id=qb_customer['Id'],
                            customer_data=update_data,
                            sync_token=sync_token,
                            existing_customer=qb_customer
                        )
                        
                        updated.append({
                            **match_info,
                            "updated_type": updated_customer.get('CustomerTypeRef', {}).get('name', 'Unknown')
                        })
                        
                        logger.info(f"[QB TYPE SYNC] Updated {client_name} → GC Compliance")
                        
                    except Exception as e:
                        error_msg = str(e)
                        errors.append({
                            **match_info,
                            "error": error_msg
                        })
                        logger.error(f"[QB TYPE SYNC] Error updating {client_name}: {error_msg}")
            
            result = {
                "status": "success",
                "dry_run": dry_run,
                "total_clients": len(clients_data),
                "matched": len(matched),
                "skipped_already_set": len(skipped),
                "updated": len(updated),
                "not_found_in_qb": len(not_found),
                "errors": len(errors),
                "matched_details": matched[:20],  # First 20 for brevity
                "skipped_details": skipped[:10],
                "not_found_details": not_found,
                "error_details": errors
            }
            
            if dry_run:
                result["message"] = f"Dry run: {len(matched)} customers would be updated to GC Compliance"
            else:
                result["message"] = f"Updated {len(updated)} customers to GC Compliance"
            
            logger.info(f"[QB TYPE SYNC] Complete: {result['message']}")
            return result
            
        except Exception as e:
            logger.error(f"[QB TYPE SYNC] Error: {e}", exc_info=True)
            return {
                "status": "failed",
                "error": f"Sync failed: {str(e)}"
            }
    
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
        Tokens should be loaded by startup event in main.py.
        """
        return bool(self.access_token and self.realm_id)
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current service status.
        """
        return {
            "authenticated": bool(self.access_token and self.realm_id),
            "realm_id": self.realm_id,
            "environment": self.environment,
            "token_expires_at": self.token_expires_at.isoformat() if self.token_expires_at else None
        }


# Global QuickBooks service instance
quickbooks_service = QuickBooksService()
