"""
Modern QuickBooks service using PostgreSQL database for token storage.

Replaces Google Sheets token storage with database-backed secure storage.
Migrates from: app/services/quickbooks_service.py (Google Sheets)
To: Database table quickbooks_tokens with encryption support
"""
# IMPORTANT (QuickBooks queries):
# QuickBooks SQL is strict and non-standard.
# When writing or modifying QB queries, ALWAYS verify syntax
# against official Intuit QBO documentation.


import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, List
import urllib.parse
import httpx
from intuitlib.client import AuthClient
from intuitlib.enums import Scopes
from quickbooks import QuickBooks
from quickbooks.objects.customer import Customer
from quickbooks.objects.invoice import Invoice
from quickbooks.objects.estimate import Estimate
from quickbooks.objects.bill import Bill
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings
from app.db.models import QuickBooksToken

logger = logging.getLogger(__name__)


class QuickBooksService:
    """
    QuickBooks OAuth2 and API service with database token storage.
    
    Key improvements over legacy version:
    - Database token storage (no Google Sheets dependency)
    - Async token operations
    - Better error handling
    - Automatic token refresh with database update
    - Support for multiple environments (sandbox/production)
    
    Token lifecycle:
    1. OAuth flow → store tokens in database
    2. API calls → auto-refresh if expired
    3. Token refresh → update database
    4. Logout → revoke tokens in database
    """
    
    def __init__(self, db: Optional[AsyncSession] = None):
        """
        Initialize QuickBooks service.
        
        Args:
            db: Database session for token operations (optional for sync operations)
        """
        self.db = db
        
        # OAuth configuration
        self.client_id = settings.QB_CLIENT_ID
        self.client_secret = settings.QB_CLIENT_SECRET
        self.redirect_uri = settings.QB_REDIRECT_URI
        self.environment = settings.QB_ENVIRONMENT  # "sandbox" or "production"
        
        # OAuth URLs
        if self.environment == "production":
            self.base_url = "https://quickbooks.api.intuit.com"
            self.token_url = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"
        else:
            self.base_url = "https://sandbox-quickbooks.api.intuit.com"
            self.token_url = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"
        
        # Current token state (loaded from database)
        self.realm_id: Optional[str] = None
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.token_expires_at: Optional[datetime] = None
        self.company_name: Optional[str] = None
        
        # QuickBooks client (created after token load)
        self.qb_client: Optional[QuickBooks] = None
        
        logger.info(f"QuickBooks service initialized (environment: {self.environment})")
    
    # ==================== Database Token Operations ====================
    
    async def load_tokens_from_db(self) -> bool:
        """
        Load QuickBooks tokens from database.
        
        Returns:
            True if tokens loaded successfully, False otherwise
        """
        if not self.db:
            logger.warning("No database session provided for token loading")
            return False
        
        try:
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
            self.token_expires_at = token_record.access_token_expires_at
            self.company_name = None  # TODO: Add company_name field to model
            
            # Create QuickBooks client
            self._create_qb_client()
            
            logger.info(f"Loaded tokens from database for realm: {self.realm_id}")
            
            # Auto-refresh if expired
            if self.is_token_expired():
                logger.info("Token expired, refreshing...")
                await self.refresh_access_token()
            
            return True
            
        except Exception as e:
            logger.error(f"Error loading tokens from database: {e}", exc_info=True)
            return False
    
    async def save_tokens_to_db(
        self,
        realm_id: str,
        access_token: str,
        refresh_token: str,
        expires_in: int
    ) -> bool:
        """
        Save QuickBooks tokens to database.
        
        Args:
            realm_id: QuickBooks company ID
            access_token: OAuth access token
            refresh_token: OAuth refresh token
            expires_in: Token expiration time in seconds
        
        Returns:
            True if saved successfully, False otherwise
        """
        if not self.db:
            logger.warning("No database session provided for token saving")
            return False
        
        try:
            # Calculate expiration times
            now = datetime.utcnow()
            access_expires_at = now + timedelta(seconds=expires_in)
            refresh_expires_at = now + timedelta(days=100)  # QB refresh tokens last 100 days
            
            # Check if token already exists for this realm
            result = await self.db.execute(
                select(QuickBooksToken).where(QuickBooksToken.realm_id == realm_id)
            )
            existing_token = result.scalar_one_or_none()
            
            if existing_token:
                # Update existing token
                existing_token.access_token = access_token
                existing_token.refresh_token = refresh_token
                existing_token.access_token_expires_at = access_expires_at
                existing_token.refresh_token_expires_at = refresh_expires_at
                existing_token.environment = self.environment
                existing_token.is_active = True
                logger.info(f"Updated existing tokens for realm: {realm_id}")
            else:
                # Create new token record
                new_token = QuickBooksToken(
                    realm_id=realm_id,
                    access_token=access_token,
                    refresh_token=refresh_token,
                    access_token_expires_at=access_expires_at,
                    refresh_token_expires_at=refresh_expires_at,
                    environment=self.environment,
                    is_active=True
                )
                self.db.add(new_token)
                logger.info(f"Created new tokens for realm: {realm_id}")
            
            await self.db.commit()
            
            # Update instance state
            self.realm_id = realm_id
            self.access_token = access_token
            self.refresh_token = refresh_token
            self.token_expires_at = access_expires_at
            self.company_name = None  # TODO: Add company_name field
            
            # Create QuickBooks client
            self._create_qb_client()
            
            logger.info(f"Saved tokens to database for realm: {realm_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving tokens to database: {e}", exc_info=True)
            await self.db.rollback()
            return False
    
    async def revoke_tokens(self) -> bool:
        """
        Revoke QuickBooks tokens (mark as inactive in database).
        
        Returns:
            True if revoked successfully, False otherwise
        """
        if not self.db or not self.realm_id:
            return False
        
        try:
            # Mark all tokens for this realm as inactive
            await self.db.execute(
                select(QuickBooksToken).where(QuickBooksToken.realm_id == self.realm_id)
            )
            tokens = await self.db.execute(
                select(QuickBooksToken).where(QuickBooksToken.realm_id == self.realm_id)
            )
            for token in tokens.scalars():
                token.is_active = False
            
            await self.db.commit()
            
            # Clear instance state
            self.realm_id = None
            self.access_token = None
            self.refresh_token = None
            self.token_expires_at = None
            self.company_name = None
            self.qb_client = None
            
            logger.info("QuickBooks tokens revoked")
            return True
            
        except Exception as e:
            logger.error(f"Error revoking tokens: {e}", exc_info=True)
            await self.db.rollback()
            return False
    
    # ==================== Token Management ====================
    
    def is_token_expired(self) -> bool:
        """Check if access token is expired"""
        if not self.token_expires_at:
            return True
        
        # Use timezone-aware datetime for comparison
        now = datetime.now(timezone.utc)
        # Add 5-minute buffer
        return now >= (self.token_expires_at - timedelta(minutes=5))
    
    def is_authenticated(self) -> bool:
        """Check if service has valid tokens"""
        return (
            self.realm_id is not None
            and self.access_token is not None
            and self.refresh_token is not None
            and not self.is_token_expired()
        )
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current QuickBooks connection status.
        
        Returns:
            Dictionary with authentication status, realm ID, environment, and token expiration
        """
        return {
            "authenticated": self.is_authenticated(),
            "realm_id": self.realm_id,
            "environment": self.environment,
            "token_expires_at": self.token_expires_at.isoformat() if self.token_expires_at else None
        }
    
    def _create_qb_client(self):
        """Create QuickBooks API client with current tokens"""
        if self.realm_id and self.access_token:
            # Create AuthClient for environment detection
            from intuitlib.enums import Scopes
            auth_client = AuthClient(
                client_id=self.client_id,
                client_secret=self.client_secret,
                redirect_uri=self.redirect_uri,
                environment='sandbox' if self.environment == 'sandbox' else 'production'
            )
            
            self.qb_client = QuickBooks(
                auth_client=auth_client,
                refresh_token=self.refresh_token,
                company_id=self.realm_id,
                minorversion=65
            )
            if self.qb_client:
                self.qb_client.access_token = self.access_token
    
    async def refresh_access_token(self) -> bool:
        """
        Refresh QuickBooks access token using refresh token.
        
        Returns:
            True if refreshed successfully, False otherwise
        """
        if not self.refresh_token or not self.db:
            logger.error("Cannot refresh: missing refresh token or database session")
            return False
        
        try:
            # Create auth client
            auth_client = AuthClient(
                client_id=self.client_id,
                client_secret=self.client_secret,
                redirect_uri=self.redirect_uri,
                environment=self.environment
            )
            
            # Refresh token
            auth_client.refresh(refresh_token=self.refresh_token)
            
            # Save new tokens
            await self.save_tokens_to_db(
                realm_id=self.realm_id,
                access_token=auth_client.access_token,
                refresh_token=auth_client.refresh_token,
                expires_in=auth_client.expires_in
            )
            
            logger.info("QuickBooks access token refreshed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error refreshing access token: {e}", exc_info=True)
            return False
    
    # ==================== OAuth Flow ====================
    
    def get_authorization_url(self, state: Optional[str] = None) -> str:
        """
        Get OAuth authorization URL for user consent.
        
        Args:
            state: Optional state parameter for CSRF protection
        
        Returns:
            Authorization URL
        """
        auth_client = AuthClient(
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.redirect_uri,
            environment=self.environment,
            state_token=state
        )
        
        scopes = [
            Scopes.ACCOUNTING,
        ]
        
        return auth_client.get_authorization_url(scopes)
    
    async def handle_callback(
        self,
        authorization_code: str,
        realm_id: str,
        state: Optional[str] = None
    ) -> bool:
        """
        Handle OAuth callback and exchange code for tokens.
        
        Args:
            authorization_code: Authorization code from callback
            realm_id: QuickBooks company ID
            state: State parameter for CSRF validation
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create auth client
            auth_client = AuthClient(
                client_id=self.client_id,
                client_secret=self.client_secret,
                redirect_uri=self.redirect_uri,
                environment=self.environment,
                state_token=state
            )
            
            # Exchange code for tokens
            auth_client.get_bearer_token(authorization_code, realm_id=realm_id)
            
            # Save tokens to database
            await self.save_tokens_to_db(
                realm_id=realm_id,
                access_token=auth_client.access_token,
                refresh_token=auth_client.refresh_token,
                expires_in=auth_client.expires_in
            )
            
            logger.info(f"OAuth callback handled successfully for realm: {realm_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error handling OAuth callback: {e}", exc_info=True)
            return False
    
    # ==================== QuickBooks API Operations ====================
    
    async def _ensure_authenticated(self):
        """Ensure service is authenticated before API calls"""
        if not self.qb_client:
            # Try to load tokens
            await self.load_tokens_from_db()
        
        if not self.is_authenticated():
            raise Exception("QuickBooks not authenticated. Please connect first.")
        
        # Auto-refresh if needed
        if self.is_token_expired():
            await self.refresh_access_token()
    
    async def get_customers(self) -> List[Customer]:
        """Get all customers from QuickBooks"""
        await self._ensure_authenticated()
        return Customer.all(qb=self.qb_client)
    
    async def get_invoices(self, customer_id: Optional[str] = None) -> List[Invoice]:
        """Get invoices from QuickBooks"""
        await self._ensure_authenticated()
        
        if customer_id:
            query = f"SELECT * FROM Invoice WHERE CustomerRef = '{customer_id}'"
            return Invoice.query(query, qb=self.qb_client)
        else:
            return Invoice.all(qb=self.qb_client)
    
    async def get_estimates(self, customer_id: Optional[str] = None) -> List[Estimate]:
        """Get estimates from QuickBooks"""
        await self._ensure_authenticated()
        
        if customer_id:
            query = f"SELECT * FROM Estimate WHERE CustomerRef = '{customer_id}'"
            return Estimate.query(query, qb=self.qb_client)
        else:
            return Estimate.all(qb=self.qb_client)
    
    async def query(self, query_string: str, entity_class=None):
        """Execute a raw QuickBooks query with hybrid SDK/HTTP routing.
        
        Strategy (based on stress test findings - see docs/audits/QUICKBOOKS_SDK_VS_HTTP_ANALYSIS.md):
        - Block known-unsupported patterns (CustomerTypeRef)
        - Use HTTP for COUNT queries (SDK bug returns 0)
        - Use SDK for all other queries (3.6x faster)
        
        Args:
            query_string: SQL-like query string (e.g., "SELECT * FROM Payment WHERE...")
            entity_class: Optional entity class to query with SDK
        
        Returns:
            List of entity dictionaries or COUNT result dict
        """
        await self._ensure_authenticated()
        
        # Guardrail: Block known-unsupported patterns
        if "CustomerTypeRef" in query_string:
            raise ValueError(
                "CustomerTypeRef is not queryable in QuickBooks API. "
                "Fetch all customers with 'SELECT * FROM Customer' and post-filter in Python: "
                "[c for c in customers if c.get('CustomerTypeRef', {}).get('value') == '698682']"
            )
        
        # Route COUNT queries to HTTP (SDK bug - returns 0)
        if "COUNT(*)" in query_string.upper():
            logger.info("[QB QUERY] Routing COUNT query to HTTP (SDK bug)")
            return await self._http_query(query_string)
        
        # Route all other queries to SDK (3.6x faster)
        logger.info("[QB QUERY] Routing query to SDK (3.6x faster than HTTP)")
        return await self._sdk_query(query_string, entity_class)
    
    async def _sdk_query(self, query_string: str, entity_class=None):
        """Execute query using QuickBooks SDK (faster, but COUNT broken).
        
        Performance: 289ms average (3.6x faster than HTTP)
        Limitation: COUNT(*) returns 0 (use HTTP instead)
        """
        # Determine entity class from query if not provided
        if entity_class is None:
            query_upper = query_string.upper()
            if "FROM CUSTOMER" in query_upper:
                entity_class = Customer
            elif "FROM INVOICE" in query_upper:
                entity_class = Invoice
            elif "FROM ESTIMATE" in query_upper:
                entity_class = Estimate
            elif "FROM BILL" in query_upper:
                entity_class = Bill
            else:
                # Fallback to HTTP if entity unknown
                logger.warning(f"Unknown entity in query, falling back to HTTP: {query_string}")
                return await self._http_query(query_string)
        
        try:
            results = entity_class.query(query_string, qb=self.qb_client)
            
            # Convert SDK objects to dictionaries
            if results:
                dict_results = [r.to_dict() if hasattr(r, 'to_dict') else r for r in results]
                logger.info(f"[METRICS] SDK query returned {len(dict_results)} entities")
                return dict_results
            else:
                logger.info("[METRICS] SDK query returned 0 entities")
                return []
        except Exception as e:
            logger.error(f"SDK query failed, falling back to HTTP: {e}")
            return await self._http_query(query_string)
    
    async def _http_query(self, query_string: str):
        """Execute query using direct HTTP (required for COUNT, fallback for SDK failures).
        
        Performance: 1034ms average (slower than SDK)
        Use cases: COUNT queries, SDK failures, unknown entities
        """
        base_url = self.qb_client.api_url_v3
        encoded_query = urllib.parse.quote(query_string)
        url = f"{base_url}/company/{self.realm_id}/query?query={encoded_query}&minorversion=75"
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
            "Content-Type": "text/plain"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=30.0)
            
            if response.status_code != 200:
                error_msg = f"Query failed: HTTP {response.status_code} - {response.text[:200]}"
                logger.error(error_msg)
                raise Exception(error_msg)
            
            data = response.json()
            
            # Check for Fault
            if "Fault" in data:
                fault = data["Fault"]
                error_msg = f"QB Query Fault: {fault}"
                logger.error(error_msg)
                raise Exception(error_msg)
            
            # Extract QueryResponse
            query_response = data.get("QueryResponse", {})
            
            # Handle COUNT queries
            if "totalCount" in query_response:
                logger.info(f"[METRICS] HTTP COUNT query returned: {query_response['totalCount']}")
                return {"totalCount": query_response["totalCount"]}
            
            # Handle entity queries - return the entity array
            # QB returns Customer, Invoice, Payment, etc. as the key
            for key in query_response:
                if key not in ["startPosition", "maxResults", "totalCount"]:
                    entities = query_response[key]
                    # Ensure it's always a list
                    if not isinstance(entities, list):
                        entities = [entities]
                    logger.info(f"[METRICS] HTTP query returned {len(entities)} {key} entities")
                    return entities
            
            # Empty result
            logger.info("[METRICS] HTTP query returned 0 entities")
            return []
    
    async def create_invoice(self, invoice_data: Dict[str, Any]) -> Optional[Invoice]:
        """Create invoice in QuickBooks"""
        await self._ensure_authenticated()
        
        try:
            invoice = Invoice()
            # Set invoice fields from invoice_data
            # ... (invoice creation logic)
            invoice.save(qb=self.qb_client)
            return invoice
        except Exception as e:
            logger.error(f"Error creating invoice: {e}", exc_info=True)
            return None


# Module-level service instance (for backward compatibility)
# Initialize with database session when needed
quickbooks_service = QuickBooksService()


def get_quickbooks_service(db: AsyncSession) -> QuickBooksService:
    """
    Get QuickBooks service instance with database session.
    
    Use this in FastAPI routes with Depends(get_db).
    """
    return QuickBooksService(db=db)
