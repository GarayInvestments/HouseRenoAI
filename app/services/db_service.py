"""
Database service with backwards-compatible API matching GoogleService.

Purpose: Provide async database operations with same method signatures as GoogleService
to minimize changes in routes and handlers. Implements TTL caching for performance.

Validation: 
- Unit tests in tests/test_db_service.py
- Integration: Call methods and verify returned dict shapes match GoogleService
"""

import hashlib
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from sqlalchemy import select, update, delete, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert

from app.db.models import Client, Project, Permit, Payment, User, QuickBooksCustomerCache, QuickBooksInvoiceCache
from app.db.session import AsyncSessionLocal

logger = logging.getLogger(__name__)


class TTLCache:
    """Simple in-memory TTL cache for database queries."""
    
    def __init__(self, default_ttl_seconds: int = 120):
        self._cache: Dict[str, tuple[Any, datetime]] = {}
        self.default_ttl_seconds = default_ttl_seconds
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached value if not expired."""
        if key in self._cache:
            value, expiry = self._cache[key]
            if datetime.utcnow() < expiry:
                return value
            else:
                del self._cache[key]
        return None
    
    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None):
        """Set value with TTL."""
        ttl = ttl_seconds or self.default_ttl_seconds
        expiry = datetime.utcnow() + timedelta(seconds=ttl)
        self._cache[key] = (value, expiry)
    
    def clear(self):
        """Clear all cached values."""
        self._cache.clear()
    
    def invalidate(self, key: str):
        """Invalidate specific cache key."""
        if key in self._cache:
            del self._cache[key]


class DBService:
    """
    Database service providing backwards-compatible API with GoogleService.
    
    All methods return data in same shape as GoogleService for drop-in replacement.
    Uses async SQLAlchemy with connection pooling and TTL caching.
    """
    
    def __init__(self):
        self.cache = TTLCache(default_ttl_seconds=120)  # 2 minute default
        self._initialized = False
    
    async def initialize(self):
        """
        Initialize database service.
        
        In development: Creates tables if they don't exist.
        In production: Assumes Alembic migrations have been run.
        """
        if self._initialized:
            return
        
        try:
            # Test connection
            async with AsyncSessionLocal() as session:
                result = await session.execute(select(func.count()).select_from(Client))
                result.scalar()
            
            self._initialized = True
            logger.info("[DB_SERVICE] Database service initialized successfully")
        except Exception as e:
            logger.error(f"[DB_SERVICE] Failed to initialize: {e}", exc_info=True)
            raise
    
    # ==================== CLIENT METHODS ====================
    
    async def get_clients_data(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get all clients as list of dicts matching GoogleService format.
        
        Returns: List of dicts with keys: client_id, Full Name, Email, Phone, etc.
        Includes extra JSONB fields merged into main dict.
        """
        cache_key = f"clients_all_{limit}"
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached
        
        async with AsyncSessionLocal() as session:
            query = select(Client).order_by(Client.created_at.desc())
            if limit:
                query = query.limit(limit)
            
            result = await session.execute(query)
            clients = result.scalars().all()
            
            # Convert to dict format matching Sheets
            clients_data = []
            for client in clients:
                client_dict = {
                    "Client ID": client.client_id,
                    "Full Name": client.full_name or "Not provided",
                    "Email": client.email or "Not provided",
                    "Phone": client.phone or "Not provided",
                    "Address": client.address or "Not provided",
                    "City": client.city or "",
                    "State": client.state or "",
                    "Zip": client.zip_code or "",
                    "Status": client.status or "Active",
                    "Client Type": client.client_type or "Residential",
                    "QB Customer ID": client.qb_customer_id or "",
                    "QB Display Name": client.qb_display_name or "",
                    "QB Sync Status": client.qb_sync_status or "",
                    "Created At": client.created_at.isoformat() if client.created_at else "",
                    "Updated At": client.updated_at.isoformat() if client.updated_at else "",
                }
                
                # Merge extra JSONB fields
                if client.extra:
                    client_dict.update(client.extra)
                
                clients_data.append(client_dict)
            
            self.cache.set(cache_key, clients_data)
            logger.info(f"[DB_SERVICE] Retrieved {len(clients_data)} clients from DB")
            return clients_data
    
    async def get_client_by_id(self, client_id: str) -> Optional[Dict[str, Any]]:
        """Get single client by ID."""
        cache_key = f"client_{client_id}"
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached
        
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Client).where(Client.client_id == client_id)
            )
            client = result.scalar_one_or_none()
            
            if not client:
                return None
            
            client_dict = {
                "Client ID": client.client_id,
                "Full Name": client.full_name or "Not provided",
                "Email": client.email or "Not provided",
                "Phone": client.phone or "Not provided",
                "Address": client.address or "Not provided",
                "City": client.city or "",
                "State": client.state or "",
                "Zip": client.zip_code or "",
                "Status": client.status or "Active",
                "Client Type": client.client_type or "Residential",
                "QB Customer ID": client.qb_customer_id or "",
            }
            
            if client.extra:
                client_dict.update(client.extra)
            
            self.cache.set(cache_key, client_dict)
            return client_dict
    
    async def get_client_by_business_id(self, business_id: str) -> Optional[Dict[str, Any]]:
        """Get single client by business ID (e.g., CL-00001)."""
        cache_key = f"client_bid_{business_id}"
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached
        
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Client).where(Client.business_id == business_id)
            )
            client = result.scalar_one_or_none()
            
            if not client:
                return None
            
            client_dict = {
                "Client ID": client.client_id,
                "Business ID": client.business_id,
                "Full Name": client.full_name or "Not provided",
                "Email": client.email or "Not provided",
                "Phone": client.phone or "Not provided",
                "Address": client.address or "Not provided",
                "City": client.city or "",
                "State": client.state or "",
                "Zip": client.zip_code or "",
                "Status": client.status or "Active",
                "Client Type": client.client_type or "Residential",
                "QB Customer ID": client.qb_customer_id or "",
            }
            
            if client.extra:
                client_dict.update(client.extra)
            
            self.cache.set(cache_key, client_dict)
            return client_dict
    
    async def upsert_client_from_sheet_row(self, row_dict: Dict[str, Any]) -> str:
        """
        Insert or update client from sheet row data.
        
        Args:
            row_dict: Dict with keys from Sheets (Full Name, Email, etc.)
        
        Returns:
            client_id of created/updated client
        """
        client_id = row_dict.get("Client ID") or row_dict.get("client_id")
        
        # Generate ID if missing
        if not client_id:
            client_id = self._generate_id(row_dict.get("Full Name", "") + row_dict.get("Email", ""))
        
        # Separate typed fields from extra fields
        typed_fields = {
            "client_id": client_id,
            "full_name": row_dict.get("Full Name") or row_dict.get("Name"),
            "email": row_dict.get("Email"),
            "phone": row_dict.get("Phone"),
            "address": row_dict.get("Address"),
            "city": row_dict.get("City"),
            "state": row_dict.get("State"),
            "zip_code": row_dict.get("Zip") or row_dict.get("Zip Code"),
            "status": row_dict.get("Status"),
            "client_type": row_dict.get("Client Type"),
            "qb_customer_id": row_dict.get("QB Customer ID"),
            "qb_display_name": row_dict.get("QB Display Name"),
            "qb_sync_status": row_dict.get("QB Sync Status"),
        }
        
        # Extra fields go to JSONB
        extra_fields = {}
        known_keys = set(typed_fields.keys()) | {"Client ID", "Full Name", "Email", "Phone", "Address", "City", "State", "Zip", "Zip Code", "Status", "Client Type", "QB Customer ID", "QB Display Name", "QB Sync Status"}
        for key, value in row_dict.items():
            if key not in known_keys and value:
                extra_fields[key] = value
        
        if extra_fields:
            typed_fields["extra"] = extra_fields
        
        async with AsyncSessionLocal() as session:
            # Use INSERT ... ON CONFLICT UPDATE (upsert)
            stmt = insert(Client).values(**typed_fields)
            stmt = stmt.on_conflict_do_update(
                index_elements=["client_id"],
                set_={k: v for k, v in typed_fields.items() if k != "client_id"}
            )
            
            await session.execute(stmt)
            await session.commit()
        
        # Invalidate cache
        self.cache.invalidate(f"client_{client_id}")
        self.cache.invalidate("clients_all_None")
        
        logger.info(f"[DB_SERVICE] Upserted client {client_id}")
        return client_id
    
    # ==================== PROJECT METHODS ====================
    
    async def get_projects_data(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get all projects matching GoogleService format."""
        cache_key = f"projects_all_{limit}"
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached
        
        async with AsyncSessionLocal() as session:
            query = select(Project).order_by(Project.created_at.desc())
            if limit:
                query = query.limit(limit)
            
            result = await session.execute(query)
            projects = result.scalars().all()
            
            projects_data = []
            for project in projects:
                project_dict = {
                    "Project ID": project.project_id,
                    "Client ID": project.client_id or "",
                    "Project Name": project.project_name or "Unnamed Project",
                    "Address": project.project_address or "Not provided",
                    "Project Type": project.project_type or "General",
                    "Status": project.status or "Planning",
                    "Budget": float(project.budget) if project.budget else 0.0,
                    "Actual Cost": float(project.actual_cost) if project.actual_cost else 0.0,
                    "Start Date": project.start_date.isoformat() if project.start_date else "",
                    "End Date": project.end_date.isoformat() if project.end_date else "",
                    "Description": project.description or "",
                    "Notes": project.notes or "",
                }
                
                if project.extra:
                    project_dict.update(project.extra)
                
                projects_data.append(project_dict)
            
            self.cache.set(cache_key, projects_data)
            logger.info(f"[DB_SERVICE] Retrieved {len(projects_data)} projects from DB")
            return projects_data
    
    async def get_project_by_id(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get single project by ID."""
        cache_key = f"project_{project_id}"
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached
        
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Project).where(Project.project_id == project_id)
            )
            project = result.scalar_one_or_none()
            
            if not project:
                return None
            
            project_dict = {
                "Project ID": project.project_id,
                "Client ID": project.client_id or "",
                "Project Name": project.project_name or "Unnamed Project",
                "Address": project.project_address or "Not provided",
                "Status": project.status or "Planning",
                "Budget": float(project.budget) if project.budget else 0.0,
            }
            
            if project.extra:
                project_dict.update(project.extra)
            
            self.cache.set(cache_key, project_dict)
            return project_dict
    
    async def get_project_by_business_id(self, business_id: str) -> Optional[Dict[str, Any]]:
        """Get single project by business ID (e.g., PRJ-00001)."""
        cache_key = f"project_bid_{business_id}"
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached
        
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Project).where(Project.business_id == business_id)
            )
            project = result.scalar_one_or_none()
            
            if not project:
                return None
            
            project_dict = {
                "Project ID": project.project_id,
                "Business ID": project.business_id,
                "Client ID": project.client_id or "",
                "Project Name": project.project_name or "Unnamed Project",
                "Address": project.project_address or "Not provided",
                "Status": project.status or "Planning",
                "Budget": float(project.budget) if project.budget else 0.0,
            }
            
            if project.extra:
                project_dict.update(project.extra)
            
            self.cache.set(cache_key, project_dict)
            return project_dict
    
    async def upsert_project_from_sheet_row(self, row_dict: Dict[str, Any]) -> str:
        """Insert or update project from sheet row."""
        project_id = row_dict.get("Project ID") or row_dict.get("project_id")
        
        if not project_id:
            project_id = self._generate_id(row_dict.get("Project Name", "") + row_dict.get("Client ID", ""))
        
        typed_fields = {
            "project_id": project_id,
            "client_id": row_dict.get("Client ID"),
            "project_name": row_dict.get("Project Name"),
            "project_address": row_dict.get("Address") or row_dict.get("Project Address"),
            "project_type": row_dict.get("Project Type"),
            "status": row_dict.get("Status"),
            "budget": self._parse_numeric(row_dict.get("Budget")),
            "actual_cost": self._parse_numeric(row_dict.get("Actual Cost")),
            "start_date": self._parse_date(row_dict.get("Start Date")),
            "end_date": self._parse_date(row_dict.get("End Date")),
            "description": row_dict.get("Description"),
            "notes": row_dict.get("Notes"),
        }
        
        extra_fields = {}
        known_keys = {"Project ID", "Client ID", "Project Name", "Address", "Project Address", "Project Type", "Status", "Budget", "Actual Cost", "Start Date", "End Date", "Description", "Notes"}
        for key, value in row_dict.items():
            if key not in known_keys and value:
                extra_fields[key] = value
        
        if extra_fields:
            typed_fields["extra"] = extra_fields
        
        async with AsyncSessionLocal() as session:
            stmt = insert(Project).values(**typed_fields)
            stmt = stmt.on_conflict_do_update(
                index_elements=["project_id"],
                set_={k: v for k, v in typed_fields.items() if k != "project_id"}
            )
            
            await session.execute(stmt)
            await session.commit()
        
        self.cache.invalidate(f"project_{project_id}")
        self.cache.invalidate("projects_all_None")
        
        logger.info(f"[DB_SERVICE] Upserted project {project_id}")
        return project_id
    
    # ==================== PERMIT METHODS ====================
    
    async def get_permits_data(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get all permits matching GoogleService format."""
        cache_key = f"permits_all_{limit}"
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached
        
        async with AsyncSessionLocal() as session:
            query = select(Permit).order_by(Permit.created_at.desc())
            if limit:
                query = query.limit(limit)
            
            result = await session.execute(query)
            permits = result.scalars().all()
            
            permits_data = []
            for permit in permits:
                permit_dict = {
                    "Permit ID": permit.permit_id,
                    "Project ID": permit.project_id or "",
                    "Client ID": permit.client_id or "",
                    "Permit Number": permit.permit_number or "Not assigned",
                    "Permit Type": permit.permit_type or "Building",
                    "Status": permit.status or "Pending",
                    "Application Date": permit.application_date.isoformat() if permit.application_date else "",
                    "Approval Date": permit.approval_date.isoformat() if permit.approval_date else "",
                    "Expiration Date": permit.expiration_date.isoformat() if permit.expiration_date else "",
                    "Issuing Authority": permit.issuing_authority or "",
                    "Notes": permit.notes or "",
                }
                
                if permit.extra:
                    permit_dict.update(permit.extra)
                
                permits_data.append(permit_dict)
            
            self.cache.set(cache_key, permits_data)
            logger.info(f"[DB_SERVICE] Retrieved {len(permits_data)} permits from DB")
            return permits_data
    
    async def get_permit_by_id(self, permit_id: str) -> Optional[Dict[str, Any]]:
        """Get single permit by ID."""
        cache_key = f"permit_{permit_id}"
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached
        
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Permit).where(Permit.permit_id == permit_id)
            )
            permit = result.scalar_one_or_none()
            
            if not permit:
                return None
            
            permit_dict = {
                "Permit ID": permit.permit_id,
                "Project ID": permit.project_id or "",
                "Permit Number": permit.permit_number or "Not assigned",
                "Status": permit.status or "Pending",
            }
            
            if permit.extra:
                permit_dict.update(permit.extra)
            
            self.cache.set(cache_key, permit_dict)
            return permit_dict
    
    async def get_permit_by_business_id(self, business_id: str) -> Optional[Dict[str, Any]]:
        """Get single permit by business ID (e.g., PRM-00001)."""
        cache_key = f"permit_bid_{business_id}"
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached
        
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Permit).where(Permit.business_id == business_id)
            )
            permit = result.scalar_one_or_none()
            
            if not permit:
                return None
            
            permit_dict = {
                "Permit ID": permit.permit_id,
                "Business ID": permit.business_id,
                "Project ID": permit.project_id or "",
                "Permit Number": permit.permit_number or "Not assigned",
                "Status": permit.status or "Pending",
            }
            
            if permit.extra:
                permit_dict.update(permit.extra)
            
            self.cache.set(cache_key, permit_dict)
            return permit_dict
    
    async def upsert_permit_from_sheet_row(self, row_dict: Dict[str, Any]) -> str:
        """Insert or update permit from sheet row."""
        permit_id = row_dict.get("Permit ID") or row_dict.get("permit_id")
        
        if not permit_id:
            permit_id = self._generate_id(row_dict.get("Permit Number", "") + row_dict.get("Project ID", ""))
        
        typed_fields = {
            "permit_id": permit_id,
            "project_id": row_dict.get("Project ID"),
            "client_id": row_dict.get("Client ID"),
            "permit_number": row_dict.get("Permit Number"),
            "permit_type": row_dict.get("Permit Type"),
            "status": row_dict.get("Status"),
            "application_date": self._parse_date(row_dict.get("Application Date")),
            "approval_date": self._parse_date(row_dict.get("Approval Date")),
            "expiration_date": self._parse_date(row_dict.get("Expiration Date")),
            "issuing_authority": row_dict.get("Issuing Authority"),
            "notes": row_dict.get("Notes"),
        }
        
        extra_fields = {}
        known_keys = {"Permit ID", "Project ID", "Client ID", "Permit Number", "Permit Type", "Status", "Application Date", "Approval Date", "Expiration Date", "Issuing Authority", "Notes"}
        for key, value in row_dict.items():
            if key not in known_keys and value:
                extra_fields[key] = value
        
        if extra_fields:
            typed_fields["extra"] = extra_fields
        
        async with AsyncSessionLocal() as session:
            stmt = insert(Permit).values(**typed_fields)
            stmt = stmt.on_conflict_do_update(
                index_elements=["permit_id"],
                set_={k: v for k, v in typed_fields.items() if k != "permit_id"}
            )
            
            await session.execute(stmt)
            await session.commit()
        
        self.cache.invalidate(f"permit_{permit_id}")
        self.cache.invalidate("permits_all_None")
        
        logger.info(f"[DB_SERVICE] Upserted permit {permit_id}")
        return permit_id
    
    # ==================== PAYMENT METHODS ====================
    
    async def get_payments_data(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get all payments."""
        async with AsyncSessionLocal() as session:
            query = select(Payment).order_by(Payment.payment_date.desc())
            if limit:
                query = query.limit(limit)
            
            result = await session.execute(query)
            payments = result.scalars().all()
            
            payments_data = []
            for payment in payments:
                payment_dict = {
                    "Payment ID": payment.payment_id,
                    "Client ID": payment.client_id or "",
                    "Project ID": payment.project_id or "",
                    "Amount": float(payment.amount) if payment.amount else 0.0,
                    "Payment Date": payment.payment_date.isoformat() if payment.payment_date else "",
                    "Payment Method": payment.payment_method or "Check",
                    "Status": payment.status or "Pending",
                    "Check Number": payment.check_number or "",
                    "QB Payment ID": payment.qb_payment_id or "",
                }
                
                if payment.extra:
                    payment_dict.update(payment.extra)
                
                payments_data.append(payment_dict)
            
            return payments_data
    
    async def get_payment_by_business_id(self, business_id: str) -> Optional[Dict[str, Any]]:
        """Get single payment by business ID (e.g., PAY-00001)."""
        cache_key = f"payment_bid_{business_id}"
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached
        
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Payment).where(Payment.business_id == business_id)
            )
            payment = result.scalar_one_or_none()
            
            if not payment:
                return None
            
            payment_dict = {
                "Payment ID": payment.payment_id,
                "Business ID": payment.business_id,
                "Client ID": payment.client_id or "",
                "Project ID": payment.project_id or "",
                "Amount": float(payment.amount) if payment.amount else 0.0,
                "Payment Date": payment.payment_date.isoformat() if payment.payment_date else "",
                "Payment Method": payment.payment_method or "Check",
                "Status": payment.status or "Pending",
                "Check Number": payment.check_number or "",
                "QB Payment ID": payment.qb_payment_id or "",
            }
            
            if payment.extra:
                payment_dict.update(payment.extra)
            
            self.cache.set(cache_key, payment_dict)
            return payment_dict
    
    async def create_payment(
        self,
        client_id: str,
        amount: float,
        payment_method: str,
        payment_date: Optional[str] = None,
        status: str = "Cleared",
        invoice_id: Optional[str] = None,
        project_id: Optional[str] = None,
        check_number: Optional[str] = None,
        transaction_id: Optional[str] = None,
        qb_payment_id: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new payment record."""
        async with AsyncSessionLocal() as session:
            from datetime import datetime
            
            # Parse payment_date if provided as string
            parsed_date = None
            if payment_date:
                if isinstance(payment_date, str):
                    parsed_date = datetime.fromisoformat(payment_date.replace('Z', '+00:00'))
                else:
                    parsed_date = payment_date
            else:
                from datetime import timezone
                parsed_date = datetime.now(timezone.utc)
            
            payment = Payment(
                client_id=client_id,
                invoice_id=invoice_id,
                project_id=project_id,
                amount=amount,
                payment_date=parsed_date,
                payment_method=payment_method,
                status=status,
                check_number=check_number,
                transaction_id=transaction_id,
                qb_payment_id=qb_payment_id,
                notes=notes
            )
            
            session.add(payment)
            await session.commit()
            await session.refresh(payment)
            
            return {
                "Payment ID": payment.payment_id,
                "Business ID": payment.business_id,
                "Client ID": payment.client_id or "",
                "Project ID": payment.project_id or "",
                "Invoice ID": payment.invoice_id or "",
                "Amount": float(payment.amount) if payment.amount else 0.0,
                "Payment Date": payment.payment_date.isoformat() if payment.payment_date else "",
                "Payment Method": payment.payment_method or "Check",
                "Status": payment.status or "Pending",
                "Check Number": payment.check_number or "",
                "Transaction ID": payment.transaction_id or "",
                "QB Payment ID": payment.qb_payment_id or "",
                "Notes": payment.notes or ""
            }
    
    # ==================== HELPER METHODS ====================
    
    def _generate_id(self, seed: str) -> str:
        """Generate 8-character hex ID from seed string."""
        return hashlib.sha256(seed.encode()).hexdigest()[:8]
    
    def _parse_numeric(self, value: Any) -> Optional[float]:
        """Parse numeric value safely."""
        if value is None or value == "":
            return None
        try:
            if isinstance(value, str):
                # Remove currency symbols and commas
                value = value.replace("$", "").replace(",", "").strip()
            return float(value)
        except (ValueError, TypeError):
            return None
    
    def _parse_date(self, value: Any) -> Optional[datetime]:
        """Parse date value safely."""
        if value is None or value == "":
            return None
        
        if isinstance(value, datetime):
            return value
        
        try:
            # Try ISO format first
            return datetime.fromisoformat(str(value))
        except (ValueError, TypeError):
            pass
        
        try:
            # Try common date formats
            from dateutil import parser
            return parser.parse(str(value))
        except:
            return None
    
    # ==================== CLIENT CRUD METHODS ====================
    
    async def create_client(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new client.
        
        Args:
            data: Dict with client fields (full_name, email, phone, etc.)
        
        Returns:
            Created client as dict
        """
        async with AsyncSessionLocal() as session:
            client = Client(
                full_name=data.get("full_name"),
                email=data.get("email"),
                phone=data.get("phone"),
                address=data.get("address"),
                city=data.get("city"),
                state=data.get("state"),
                zip_code=data.get("zip_code"),
                status=data.get("status", "Active"),
                client_type=data.get("client_type", "Residential"),
                extra=data.get("extra")
            )
            
            session.add(client)
            await session.commit()
            await session.refresh(client)
            
            # Invalidate cache
            self.cache.clear()
            
            logger.info(f"[DB_SERVICE] Created client {client.client_id}")
            return await self.get_client_by_id(client.client_id)
    
    async def update_client(self, client_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing client.
        
        Args:
            client_id: UUID of client
            data: Dict with fields to update
        
        Returns:
            Updated client as dict
        """
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Client).where(Client.client_id == client_id)
            )
            client = result.scalar_one_or_none()
            
            if not client:
                raise ValueError(f"Client {client_id} not found")
            
            # Update fields if provided
            if "full_name" in data:
                client.full_name = data["full_name"]
            if "email" in data:
                client.email = data["email"]
            if "phone" in data:
                client.phone = data["phone"]
            if "address" in data:
                client.address = data["address"]
            if "city" in data:
                client.city = data["city"]
            if "state" in data:
                client.state = data["state"]
            if "zip_code" in data:
                client.zip_code = data["zip_code"]
            if "status" in data:
                client.status = data["status"]
            if "client_type" in data:
                client.client_type = data["client_type"]
            if "extra" in data:
                client.extra = data["extra"]
            
            await session.commit()
            await session.refresh(client)
            
            # Invalidate cache
            self.cache.invalidate(f"client_{client_id}")
            self.cache.clear()
            
            logger.info(f"[DB_SERVICE] Updated client {client_id}")
            return await self.get_client_by_id(client_id)
    
    async def delete_client(self, client_id: str) -> bool:
        """
        Delete a client.
        
        Args:
            client_id: UUID of client
        
        Returns:
            True if deleted, False if not found
        """
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                delete(Client).where(Client.client_id == client_id)
            )
            await session.commit()
            
            deleted = result.rowcount > 0
            
            if deleted:
                # Invalidate cache
                self.cache.invalidate(f"client_{client_id}")
                self.cache.clear()
                logger.info(f"[DB_SERVICE] Deleted client {client_id}")
            
            return deleted
    
    # ==================== PROJECT CRUD METHODS ====================
    
    async def create_project(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new project."""
        from app.db.models import Project
        
        async with AsyncSessionLocal() as session:
            project = Project(
                client_id=data.get("client_id"),
                project_name=data.get("project_name"),
                project_address=data.get("project_address"),
                city=data.get("city"),
                state=data.get("state"),
                zip_code=data.get("zip_code"),
                status=data.get("status", "Planning"),
                description=data.get("description"),
                start_date=data.get("start_date"),
                target_completion=data.get("target_completion"),
                extra=data.get("extra")
            )
            
            session.add(project)
            await session.commit()
            await session.refresh(project)
            
            self.cache.clear()
            logger.info(f"[DB_SERVICE] Created project {project.project_id}")
            return await self.get_project_by_id(project.project_id)
    
    async def update_project(self, project_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing project."""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Project).where(Project.project_id == project_id)
            )
            project = result.scalar_one_or_none()
            
            if not project:
                raise ValueError(f"Project {project_id} not found")
            
            # Update fields
            for key in ["client_id", "project_name", "project_address", "city", "state", "zip_code", "status", "description", "start_date", "target_completion", "extra"]:
                if key in data:
                    setattr(project, key, data[key])
            
            await session.commit()
            await session.refresh(project)
            
            self.cache.clear()
            logger.info(f"[DB_SERVICE] Updated project {project_id}")
            return await self.get_project_by_id(project_id)
    
    async def delete_project(self, project_id: str) -> bool:
        """Delete a project."""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                delete(Project).where(Project.project_id == project_id)
            )
            await session.commit()
            
            deleted = result.rowcount > 0
            if deleted:
                self.cache.clear()
                logger.info(f"[DB_SERVICE] Deleted project {project_id}")
            
            return deleted
    
    # ==================== INVOICE CRUD METHODS ====================
    
    async def get_invoices_data(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get all invoices."""
        from app.db.models import Invoice
        
        cache_key = f"invoices_all_{limit}"
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached
        
        async with AsyncSessionLocal() as session:
            query = select(Invoice).order_by(Invoice.created_at.desc())
            if limit:
                query = query.limit(limit)
            
            result = await session.execute(query)
            invoices = result.scalars().all()
            
            invoices_data = []
            for invoice in invoices:
                invoices_data.append({
                    "invoice_id": invoice.invoice_id,
                    "business_id": invoice.business_id,
                    "project_id": invoice.project_id,
                    "client_id": invoice.client_id,
                    "invoice_number": invoice.invoice_number,
                    "invoice_date": invoice.invoice_date.isoformat() if invoice.invoice_date else None,
                    "due_date": invoice.due_date.isoformat() if invoice.due_date else None,
                    "subtotal": float(invoice.subtotal) if invoice.subtotal else 0,
                    "tax_amount": float(invoice.tax_amount) if invoice.tax_amount else 0,
                    "total_amount": float(invoice.total_amount) if invoice.total_amount else 0,
                    "amount_paid": float(invoice.amount_paid) if invoice.amount_paid else 0,
                    "balance_due": float(invoice.balance_due) if invoice.balance_due else 0,
                    "status": invoice.status,
                    "line_items": invoice.line_items,
                    "qb_invoice_id": invoice.qb_invoice_id,
                    "sync_status": invoice.sync_status,
                    "notes": invoice.notes,
                    "created_at": invoice.created_at.isoformat() if invoice.created_at else None,
                })
            
            self.cache.set(cache_key, invoices_data)
            return invoices_data
    
    async def get_invoice_by_id(self, invoice_id: str) -> Optional[Dict[str, Any]]:
        """Get single invoice by ID."""
        from app.db.models import Invoice
        
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Invoice).where(Invoice.invoice_id == invoice_id)
            )
            invoice = result.scalar_one_or_none()
            
            if not invoice:
                return None
            
            return {
                "invoice_id": invoice.invoice_id,
                "business_id": invoice.business_id,
                "project_id": invoice.project_id,
                "client_id": invoice.client_id,
                "invoice_number": invoice.invoice_number,
                "invoice_date": invoice.invoice_date.isoformat() if invoice.invoice_date else None,
                "due_date": invoice.due_date.isoformat() if invoice.due_date else None,
                "subtotal": float(invoice.subtotal) if invoice.subtotal else 0,
                "tax_amount": float(invoice.tax_amount) if invoice.tax_amount else 0,
                "total_amount": float(invoice.total_amount) if invoice.total_amount else 0,
                "amount_paid": float(invoice.amount_paid) if invoice.amount_paid else 0,
                "balance_due": float(invoice.balance_due) if invoice.balance_due else 0,
                "status": invoice.status,
                "line_items": invoice.line_items,
                "notes": invoice.notes,
            }
    
    async def create_invoice(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new invoice."""
        from app.db.models import Invoice
        
        async with AsyncSessionLocal() as session:
            invoice = Invoice(
                project_id=data.get("project_id"),
                client_id=data.get("client_id"),
                invoice_number=data.get("invoice_number"),
                invoice_date=data.get("invoice_date"),
                due_date=data.get("due_date"),
                subtotal=data.get("subtotal"),
                tax_amount=data.get("tax_amount", 0),
                total_amount=data.get("total_amount"),
                amount_paid=data.get("amount_paid", 0),
                balance_due=data.get("balance_due"),
                status=data.get("status", "Draft"),
                line_items=data.get("line_items"),
                notes=data.get("notes"),
            )
            
            session.add(invoice)
            await session.commit()
            await session.refresh(invoice)
            
            self.cache.clear()
            logger.info(f"[DB_SERVICE] Created invoice {invoice.invoice_id}")
            return await self.get_invoice_by_id(invoice.invoice_id)
    
    async def update_invoice(self, invoice_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing invoice."""
        from app.db.models import Invoice
        
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Invoice).where(Invoice.invoice_id == invoice_id)
            )
            invoice = result.scalar_one_or_none()
            
            if not invoice:
                raise ValueError(f"Invoice {invoice_id} not found")
            
            # Update fields
            for key in ["invoice_date", "due_date", "status", "line_items", "tax_amount", "subtotal", "total_amount", "balance_due", "notes"]:
                if key in data:
                    setattr(invoice, key, data[key])
            
            await session.commit()
            await session.refresh(invoice)
            
            self.cache.clear()
            logger.info(f"[DB_SERVICE] Updated invoice {invoice_id}")
            return await self.get_invoice_by_id(invoice_id)
    
    async def delete_invoice(self, invoice_id: str) -> bool:
        """Delete an invoice."""
        from app.db.models import Invoice
        
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                delete(Invoice).where(Invoice.invoice_id == invoice_id)
            )
            await session.commit()
            
            deleted = result.rowcount > 0
            if deleted:
                self.cache.clear()
                logger.info(f"[DB_SERVICE] Deleted invoice {invoice_id}")
            
            return deleted
    
    async def get_invoices_by_project(self, project_id: str) -> List[Dict[str, Any]]:
        """Get all invoices for a specific project."""
        from app.db.models import Invoice
        
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Invoice).where(Invoice.project_id == project_id).order_by(Invoice.invoice_date.desc())
            )
            invoices = result.scalars().all()
            
            return [await self.get_invoice_by_id(inv.invoice_id) for inv in invoices]
    
    # ==================== SITE VISIT CRUD METHODS ====================
    
    async def get_site_visits_data(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get all site visits."""
        from app.db.models import SiteVisit
        
        async with AsyncSessionLocal() as session:
            query = select(SiteVisit).order_by(SiteVisit.visit_date.desc())
            if limit:
                query = query.limit(limit)
            
            result = await session.execute(query)
            visits = result.scalars().all()
            
            return [{
                "visit_id": v.visit_id,
                "business_id": v.business_id,
                "project_id": v.project_id,
                "visit_date": v.visit_date.isoformat() if v.visit_date else None,
                "purpose": v.purpose,
                "attendees": v.attendees,
                "observations": v.observations,
                "action_items": v.action_items,
                "photos": v.photos,
                "created_at": v.created_at.isoformat() if v.created_at else None,
            } for v in visits]
    
    async def get_site_visit_by_id(self, visit_id: str) -> Optional[Dict[str, Any]]:
        """Get single site visit by ID."""
        from app.db.models import SiteVisit
        
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(SiteVisit).where(SiteVisit.visit_id == visit_id)
            )
            visit = result.scalar_one_or_none()
            
            if not visit:
                return None
            
            return {
                "visit_id": visit.visit_id,
                "project_id": visit.project_id,
                "visit_date": visit.visit_date.isoformat() if visit.visit_date else None,
                "purpose": visit.purpose,
                "attendees": visit.attendees,
                "observations": visit.observations,
                "action_items": visit.action_items,
            }
    
    async def create_site_visit(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new site visit."""
        from app.db.models import SiteVisit
        
        async with AsyncSessionLocal() as session:
            visit = SiteVisit(
                project_id=data.get("project_id"),
                visit_date=data.get("visit_date"),
                purpose=data.get("purpose"),
                attendees=data.get("attendees"),
                observations=data.get("observations"),
                action_items=data.get("action_items"),
            )
            
            session.add(visit)
            await session.commit()
            await session.refresh(visit)
            
            logger.info(f"[DB_SERVICE] Created site visit {visit.visit_id}")
            return await self.get_site_visit_by_id(visit.visit_id)
    
    async def update_site_visit(self, visit_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a site visit."""
        from app.db.models import SiteVisit
        
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(SiteVisit).where(SiteVisit.visit_id == visit_id)
            )
            visit = result.scalar_one_or_none()
            
            if not visit:
                raise ValueError(f"Site visit {visit_id} not found")
            
            for key in ["visit_date", "purpose", "attendees", "observations", "action_items"]:
                if key in data:
                    setattr(visit, key, data[key])
            
            await session.commit()
            await session.refresh(visit)
            
            logger.info(f"[DB_SERVICE] Updated site visit {visit_id}")
            return await self.get_site_visit_by_id(visit_id)
    
    async def delete_site_visit(self, visit_id: str) -> bool:
        """Delete a site visit."""
        from app.db.models import SiteVisit
        
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                delete(SiteVisit).where(SiteVisit.visit_id == visit_id)
            )
            await session.commit()
            
            return result.rowcount > 0
    
    async def get_site_visits_by_project(self, project_id: str) -> List[Dict[str, Any]]:
        """Get all site visits for a project."""
        from app.db.models import SiteVisit
        
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(SiteVisit).where(SiteVisit.project_id == project_id).order_by(SiteVisit.visit_date.desc())
            )
            visits = result.scalars().all()
            
            return [await self.get_site_visit_by_id(v.visit_id) for v in visits]
    
    # ==================== JURISDICTION CRUD METHODS ====================
    
    async def get_jurisdictions_data(self) -> List[Dict[str, Any]]:
        """Get all jurisdictions."""
        async with AsyncSessionLocal() as session:
            # Note: jurisdictions table uses 'id' not 'jurisdiction_id'
            from sqlalchemy import text
            result = await session.execute(text("SELECT id, name, state, requirements, created_at FROM jurisdictions ORDER BY name"))
            rows = result.fetchall()
            
            return [{
                "id": str(row[0]),
                "name": row[1],
                "state": row[2],
                "requirements": row[3],
                "created_at": row[4].isoformat() if row[4] else None,
            } for row in rows]
    
    async def get_jurisdiction_by_id(self, jurisdiction_id: str) -> Optional[Dict[str, Any]]:
        """Get single jurisdiction by ID."""
        async with AsyncSessionLocal() as session:
            from sqlalchemy import text
            result = await session.execute(
                text("SELECT id, name, state, requirements FROM jurisdictions WHERE id = :id"),
                {"id": jurisdiction_id}
            )
            row = result.fetchone()
            
            if not row:
                return None
            
            return {
                "id": str(row[0]),
                "name": row[1],
                "state": row[2],
                "requirements": row[3],
            }
    
    async def create_jurisdiction(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new jurisdiction."""
        async with AsyncSessionLocal() as session:
            from sqlalchemy import text
            result = await session.execute(
                text("INSERT INTO jurisdictions (name, state, requirements) VALUES (:name, :state, :requirements) RETURNING id"),
                {
                    "name": data.get("name"),
                    "state": data.get("state"),
                    "requirements": data.get("requirements", {}),
                }
            )
            jurisdiction_id = result.fetchone()[0]
            await session.commit()
            
            logger.info(f"[DB_SERVICE] Created jurisdiction {jurisdiction_id}")
            return await self.get_jurisdiction_by_id(str(jurisdiction_id))
    
    async def update_jurisdiction(self, jurisdiction_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a jurisdiction."""
        async with AsyncSessionLocal() as session:
            from sqlalchemy import text
            
            # Build update query dynamically
            updates = []
            params = {"id": jurisdiction_id}
            
            if "name" in data:
                updates.append("name = :name")
                params["name"] = data["name"]
            if "state" in data:
                updates.append("state = :state")
                params["state"] = data["state"]
            if "requirements" in data:
                updates.append("requirements = :requirements")
                params["requirements"] = data["requirements"]
            
            if not updates:
                raise ValueError("No updates provided")
            
            query = f"UPDATE jurisdictions SET {', '.join(updates)}, updated_at = CURRENT_TIMESTAMP WHERE id = :id"
            result = await session.execute(text(query), params)
            await session.commit()
            
            if result.rowcount == 0:
                raise ValueError(f"Jurisdiction {jurisdiction_id} not found")
            
            logger.info(f"[DB_SERVICE] Updated jurisdiction {jurisdiction_id}")
            return await self.get_jurisdiction_by_id(jurisdiction_id)
    
    async def delete_jurisdiction(self, jurisdiction_id: str) -> bool:
        """Delete a jurisdiction."""
        async with AsyncSessionLocal() as session:
            from sqlalchemy import text
            result = await session.execute(
                text("DELETE FROM jurisdictions WHERE id = :id"),
                {"id": jurisdiction_id}
            )
            await session.commit()
            
            return result.rowcount > 0
    
    # ==================== USER CRUD METHODS ====================
    
    async def get_users_data(self) -> List[Dict[str, Any]]:
        """Get all users."""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(User).order_by(User.created_at.desc())
            )
            users = result.scalars().all()
            
            return [{
                "id": u.id,
                "supabase_user_id": u.supabase_user_id,
                "email": u.email,
                "full_name": u.full_name,
                "phone": u.phone,
                "role": u.role,
                "is_active": u.is_active,
                "created_at": u.created_at.isoformat() if u.created_at else None,
            } for u in users]
    
    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get single user by ID."""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                return None
            
            return {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "phone": user.phone,
                "role": user.role,
                "is_active": user.is_active,
            }
    
    async def create_user(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user."""
        async with AsyncSessionLocal() as session:
            user = User(
                email=data.get("email"),
                full_name=data.get("full_name"),
                phone=data.get("phone"),
                role=data.get("role", "client"),
                is_active=True,
            )
            
            session.add(user)
            await session.commit()
            await session.refresh(user)
            
            logger.info(f"[DB_SERVICE] Created user {user.id}")
            return await self.get_user_by_id(user.id)
    
    async def update_user(self, user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a user."""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                raise ValueError(f"User {user_id} not found")
            
            for key in ["full_name", "phone", "role", "is_active"]:
                if key in data:
                    setattr(user, key, data[key])
            
            await session.commit()
            await session.refresh(user)
            
            logger.info(f"[DB_SERVICE] Updated user {user_id}")
            return await self.get_user_by_id(user_id)
    
    async def delete_user(self, user_id: str) -> bool:
        """Delete a user."""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                delete(User).where(User.id == user_id)
            )
            await session.commit()
            
            return result.rowcount > 0
    
    async def append_sheet_data(self, sheet_name: str, values: List[List[Any]]):
        """
        Backwards-compatible method for appending data (like GoogleService).
        
        Maps sheet names to entity upserts.
        """
        if sheet_name == "Clients":
            for row in values:
                if len(row) > 0:
                    # Assume row is [Name, Email, Phone, ...]
                    # This is simplified - actual mapping needs to match sheet structure
                    pass
        
        logger.warning(f"[DB_SERVICE] append_sheet_data called for {sheet_name} - implement specific logic")
    
    async def create_sheet_tab(self, tab_name: str):
        """No-op in DB - tables created via migrations."""
        logger.info(f"[DB_SERVICE] create_sheet_tab called for {tab_name} - no action needed")


# Singleton instance
db_service = DBService()
