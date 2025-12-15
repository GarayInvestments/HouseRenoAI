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

from app.db.models import (
    Client, Project, Permit, Payment, User, 
    QuickBooksCustomerCache, QuickBooksInvoiceCache,
    LicensedBusiness, Qualifier, LicensedBusinessQualifier, OversightAction, ComplianceJustification
)
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
                "Invoice ID": payment.invoice_id or "",
                "Amount": float(payment.amount) if payment.amount else 0.0,
                "Payment Date": payment.payment_date.isoformat() if payment.payment_date else "",
                "Payment Method": payment.payment_method or "Check",
                "Status": payment.status or "Pending",
                "Check Number": payment.check_number or "",
                "Reference Number": payment.reference_number or "",
                "QB Payment ID": payment.qb_payment_id or "",
                "Notes": payment.notes or "",
            }
            
            if payment.extra:
                payment_dict.update(payment.extra)
            
            self.cache.set(cache_key, payment_dict)
            return payment_dict
    
    async def get_payment_by_payment_id(self, payment_id: str) -> Optional[Dict[str, Any]]:
        """Get single payment by payment_id (UUID)."""
        cache_key = f"payment_uuid_{payment_id}"
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached
        
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Payment).where(Payment.payment_id == payment_id)
            )
            payment = result.scalar_one_or_none()
            
            if not payment:
                return None
            
            payment_dict = {
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
                "Reference Number": payment.reference_number or "",
                "QB Payment ID": payment.qb_payment_id or "",
                "Notes": payment.notes or "",
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
            
            # Update fields - include all updatable project fields
            for key in [
                "client_id", "project_name", "project_address", "project_type",
                "city", "state", "zip_code", "status", "description", "notes",
                "budget", "actual_cost", "start_date", "end_date", "completion_date",
                "target_completion", "extra",
                # Phase Q compliance fields
                "licensed_business_id", "qualifier_id", "engagement_model",
                "oversight_required", "compliance_notes"
            ]:
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
    
    async def get_invoices_with_relations(self) -> List[Dict[str, Any]]:
        """Get all invoices with client and permit information."""
        from app.db.models import Invoice, Client, Permit, Project
        
        async with AsyncSessionLocal() as session:
            # Query with joins to get related data
            result = await session.execute(
                select(
                    Invoice,
                    Client.full_name.label("customer_name"),
                    Client.email.label("customer_email"),
                    Permit.permit_number,
                    Project.project_address.label("address")
                )
                .outerjoin(Client, Invoice.client_id == Client.client_id)
                .outerjoin(Project, Invoice.project_id == Project.project_id)
                .outerjoin(Permit, Invoice.project_id == Permit.project_id)
                .order_by(Invoice.due_date.desc())
            )
            
            rows = result.all()
            invoices = []
            
            for row in rows:
                invoice = row[0]
                invoices.append({
                    "invoice_id": str(invoice.invoice_id),
                    "business_id": invoice.business_id,
                    "qb_invoice_id": invoice.qb_invoice_id,
                    "project_id": str(invoice.project_id) if invoice.project_id else None,
                    "client_id": str(invoice.client_id) if invoice.client_id else None,
                    "invoice_number": invoice.invoice_number,
                    "doc_number": invoice.invoice_number,  # Alias for frontend compatibility
                    "customer_name": row.customer_name or "Unknown Client",
                    "customer_email": row.customer_email,
                    "permit_number": row.permit_number,
                    "address": row.address,
                    "invoice_date": invoice.invoice_date.isoformat() if invoice.invoice_date else None,
                    "due_date": invoice.due_date.isoformat() if invoice.due_date else None,
                    "subtotal": float(invoice.subtotal) if invoice.subtotal else 0,
                    "tax_amount": float(invoice.tax_amount) if invoice.tax_amount else 0,
                    "total_amount": float(invoice.total_amount) if invoice.total_amount else 0,
                    "amount_paid": float(invoice.amount_paid) if invoice.amount_paid else 0,
                    "balance_due": float(invoice.balance_due) if invoice.balance_due else 0,
                    "balance": float(invoice.balance_due) if invoice.balance_due else 0,  # Alias
                    "status": invoice.status,
                    "line_items": invoice.line_items or [],
                    "notes": invoice.notes,
                    "source": "internal_database"
                })
            
            logger.info(f"[DB_SERVICE] Retrieved {len(invoices)} invoices with relations")
            return invoices
    
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
            query = select(SiteVisit).order_by(SiteVisit.scheduled_date.desc())
            if limit:
                query = query.limit(limit)
            
            result = await session.execute(query)
            visits = result.scalars().all()
            
            return [{
                "visit_id": v.visit_id,
                "business_id": v.business_id,
                "project_id": v.project_id,
                "client_id": v.client_id,
                "visit_type": v.visit_type,
                "status": v.status,
                "scheduled_date": v.scheduled_date.isoformat() if v.scheduled_date else None,
                "start_time": v.start_time.isoformat() if v.start_time else None,
                "end_time": v.end_time.isoformat() if v.end_time else None,
                "attendees": v.attendees,
                "gps_location": v.gps_location,
                "photos": v.photos,
                "notes": v.notes,
                "weather": v.weather,
                "deficiencies": v.deficiencies,
                "follow_up_actions": v.follow_up_actions,
                "created_at": v.created_at.isoformat() if v.created_at else None,
                "updated_at": v.updated_at.isoformat() if v.updated_at else None,
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
                "business_id": visit.business_id,
                "project_id": visit.project_id,
                "client_id": visit.client_id,
                "visit_type": visit.visit_type,
                "status": visit.status,
                "scheduled_date": visit.scheduled_date.isoformat() if visit.scheduled_date else None,
                "start_time": visit.start_time.isoformat() if visit.start_time else None,
                "end_time": visit.end_time.isoformat() if visit.end_time else None,
                "attendees": visit.attendees,
                "gps_location": visit.gps_location,
                "photos": visit.photos,
                "notes": visit.notes,
                "weather": visit.weather,
                "deficiencies": visit.deficiencies,
                "follow_up_actions": visit.follow_up_actions,
                "created_at": visit.created_at.isoformat() if visit.created_at else None,
                "updated_at": visit.updated_at.isoformat() if visit.updated_at else None,
            }
    
    async def create_site_visit(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new site visit."""
        from app.db.models import SiteVisit
        
        async with AsyncSessionLocal() as session:
            visit = SiteVisit(
                project_id=data.get("project_id"),
                client_id=data.get("client_id"),
                visit_type=data.get("visit_type"),
                status=data.get("status", "scheduled"),
                scheduled_date=data.get("scheduled_date"),
                start_time=data.get("start_time"),
                end_time=data.get("end_time"),
                attendees=data.get("attendees"),
                gps_location=data.get("gps_location"),
                photos=data.get("photos"),
                notes=data.get("notes"),
                weather=data.get("weather"),
                deficiencies=data.get("deficiencies"),
                follow_up_actions=data.get("follow_up_actions"),
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
            
            updateable_fields = [
                "client_id", "visit_type", "status", "scheduled_date", "start_time", 
                "end_time", "attendees", "gps_location", "photos", "notes", 
                "weather", "deficiencies", "follow_up_actions"
            ]
            
            for key in updateable_fields:
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
                select(SiteVisit).where(SiteVisit.project_id == project_id).order_by(SiteVisit.scheduled_date.desc())
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
    
    # ==================== PHASE Q: QUALIFIER COMPLIANCE METHODS ====================
    
    async def create_licensed_business(self, business_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new licensed business entity.
        
        Args:
            business_data: Dict with keys:
                - business_name (required)
                - legal_name (required)
                - license_number (required)
                - license_type (required)
                - license_status (optional, defaults to 'active')
                - dba_name (optional)
                - address (optional)
                - phone (optional)
                - email (optional)
                - notes (optional)
                
        Returns:
            Dict with created business data including auto-generated business_id
        """
        async with AsyncSessionLocal() as session:
            try:
                # Create business (business_id auto-generated by trigger)
                new_business = LicensedBusiness(
                    business_name=business_data["business_name"],
                    legal_name=business_data["legal_name"],
                    license_number=business_data["license_number"],
                    license_type=business_data["license_type"],
                    license_status=business_data.get("license_status", "active"),
                    dba_name=business_data.get("dba_name"),
                    address=business_data.get("address"),
                    phone=business_data.get("phone"),
                    email=business_data.get("email"),
                    notes=business_data.get("notes"),
                )
                
                session.add(new_business)
                await session.commit()
                await session.refresh(new_business)
                
                logger.info(f"[DB_SERVICE] Created licensed business {new_business.business_id}")
                
                return {
                    "id": new_business.id,
                    "business_id": new_business.business_id,
                    "business_name": new_business.business_name,
                    "legal_name": new_business.legal_name,
                    "license_number": new_business.license_number,
                    "license_type": new_business.license_type,
                    "license_status": new_business.license_status,
                }
                
            except Exception as e:
                await session.rollback()
                logger.error(f"[DB_SERVICE] Failed to create licensed business: {e}")
                raise
    
    async def update_licensed_business(self, business_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update an existing licensed business.
        
        Args:
            business_id: UUID or business_id format (LB-00001) to update
            update_data: Dict with fields to update
            
        Returns:
            Dict with updated business data or None if not found
        """
        async with AsyncSessionLocal() as session:
            try:
                # Find business by UUID or business_id
                stmt = select(LicensedBusiness).where(
                    (LicensedBusiness.id == business_id) | (LicensedBusiness.business_id == business_id)
                )
                result = await session.execute(stmt)
                business = result.scalar_one_or_none()
                
                if not business:
                    return None
                
                # Update fields
                for key, value in update_data.items():
                    if hasattr(business, key):
                        setattr(business, key, value)
                
                await session.commit()
                await session.refresh(business)
                
                logger.info(f"[DB_SERVICE] Updated licensed business {business.business_id}")
                
                return {
                    "id": business.id,
                    "business_id": business.business_id,
                    "business_name": business.business_name,
                    "legal_name": business.legal_name,
                    "license_number": business.license_number,
                    "license_type": business.license_type,
                    "license_status": business.license_status,
                    "is_active": business.is_active,
                }
                
            except Exception as e:
                await session.rollback()
                logger.error(f"[DB_SERVICE] Failed to update licensed business {business_id}: {e}")
                raise
    
    async def create_qualifier(self, qualifier_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new qualifier (must link to existing user via user_id).
        
        Args:
            qualifier_data: Dict with keys:
                - user_id (required) - FK to users.id (1:1 relationship)
                - full_name (required)
                - qualifier_id_number (required) - NC qualifier ID
                - license_type (required)
                - license_status (optional, defaults to 'active')
                - max_licenses_allowed (optional, defaults to 2)
                - email (optional)
                - phone (optional)
                - notes (optional)
                
        Returns:
            Dict with created qualifier data including auto-generated qualifier_id
            
        Raises:
            Exception if user_id doesn't exist or is already linked to another qualifier
        """
        async with AsyncSessionLocal() as session:
            try:
                # Create qualifier (qualifier_id auto-generated by trigger)
                new_qualifier = Qualifier(
                    user_id=qualifier_data["user_id"],
                    full_name=qualifier_data["full_name"],
                    qualifier_id_number=qualifier_data["qualifier_id_number"],
                    license_type=qualifier_data["license_type"],
                    license_status=qualifier_data.get("license_status", "active"),
                    max_licenses_allowed=qualifier_data.get("max_licenses_allowed", 2),
                    email=qualifier_data.get("email"),
                    phone=qualifier_data.get("phone"),
                    notes=qualifier_data.get("notes"),
                )
                
                session.add(new_qualifier)
                await session.commit()
                await session.refresh(new_qualifier)
                
                logger.info(f"[DB_SERVICE] Created qualifier {new_qualifier.qualifier_id} for user {new_qualifier.user_id}")
                
                return {
                    "id": new_qualifier.id,
                    "qualifier_id": new_qualifier.qualifier_id,
                    "user_id": new_qualifier.user_id,
                    "full_name": new_qualifier.full_name,
                    "qualifier_id_number": new_qualifier.qualifier_id_number,
                    "license_type": new_qualifier.license_type,
                    "license_status": new_qualifier.license_status,
                    "max_licenses_allowed": new_qualifier.max_licenses_allowed,
                }
                
            except Exception as e:
                await session.rollback()
                logger.error(f"[DB_SERVICE] Failed to create qualifier: {e}")
                raise
    
    async def update_qualifier(self, qualifier_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update an existing qualifier.
        
        Args:
            qualifier_id: UUID or qualifier_id format (QF-00001) to update
            update_data: Dict with fields to update
            
        Returns:
            Dict with updated qualifier data or None if not found
        """
        async with AsyncSessionLocal() as session:
            try:
                # Find qualifier by UUID or qualifier_id
                stmt = select(Qualifier).where(
                    (Qualifier.id == qualifier_id) | (Qualifier.qualifier_id == qualifier_id)
                )
                result = await session.execute(stmt)
                qualifier = result.scalar_one_or_none()
                
                if not qualifier:
                    return None
                
                # Update fields
                for key, value in update_data.items():
                    if hasattr(qualifier, key):
                        setattr(qualifier, key, value)
                
                await session.commit()
                await session.refresh(qualifier)
                
                logger.info(f"[DB_SERVICE] Updated qualifier {qualifier.qualifier_id}")
                
                return {
                    "id": qualifier.id,
                    "qualifier_id": qualifier.qualifier_id,
                    "user_id": qualifier.user_id,
                    "full_name": qualifier.full_name,
                    "qualifier_id_number": qualifier.qualifier_id_number,
                    "license_type": qualifier.license_type,
                    "license_status": qualifier.license_status,
                    "max_licenses_allowed": qualifier.max_licenses_allowed,
                    "is_active": qualifier.is_active,
                }
                
            except Exception as e:
                await session.rollback()
                logger.error(f"[DB_SERVICE] Failed to update qualifier {qualifier_id}: {e}")
                raise
    
    async def assign_qualifier_to_business(
        self, 
        licensed_business_id: str, 
        qualifier_id: str, 
        start_date: datetime,
        end_date: Optional[datetime] = None,
        relationship_type: str = "qualification",
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Assign qualifier to licensed business (creates LBQ relationship).
        
        Database trigger enforces capacity limit (max 2 businesses per qualifier with overlapping dates).
        
        Args:
            licensed_business_id: UUID of licensed business
            qualifier_id: UUID of qualifier
            start_date: When qualification begins
            end_date: When qualification ends (None = ongoing)
            relationship_type: Type of relationship (default: "qualification")
            notes: Optional notes
            
        Returns:
            Dict with created relationship data
            
        Raises:
            Exception if capacity exceeded (trigger will block with friendly error)
        """
        async with AsyncSessionLocal() as session:
            try:
                # Calculate cutoff_date if end_date provided (last day at 11:59:59 PM)
                cutoff_date = None
                if end_date:
                    cutoff_date = datetime.combine(end_date, datetime.max.time())
                
                new_assignment = LicensedBusinessQualifier(
                    licensed_business_id=licensed_business_id,
                    qualifier_id=qualifier_id,
                    start_date=start_date,
                    end_date=end_date,
                    cutoff_date=cutoff_date,
                    relationship_type=relationship_type,
                    notes=notes,
                )
                
                session.add(new_assignment)
                await session.commit()
                await session.refresh(new_assignment)
                
                logger.info(f"[DB_SERVICE] Assigned qualifier {qualifier_id} to business {licensed_business_id}")
                
                return {
                    "id": new_assignment.id,
                    "licensed_business_id": new_assignment.licensed_business_id,
                    "qualifier_id": new_assignment.qualifier_id,
                    "start_date": new_assignment.start_date.isoformat() if new_assignment.start_date else None,
                    "end_date": new_assignment.end_date.isoformat() if new_assignment.end_date else None,
                    "cutoff_date": new_assignment.cutoff_date.isoformat() if new_assignment.cutoff_date else None,
                    "relationship_type": new_assignment.relationship_type,
                }
                
            except Exception as e:
                await session.rollback()
                logger.error(f"[DB_SERVICE] Failed to assign qualifier: {e}")
                # Re-raise with original error (trigger error messages are user-friendly)
                raise
    
    async def create_oversight_action(self, action_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create oversight action (site visit, plan review, etc.).
        
        Database trigger enforces cutoff_date (no actions after qualifier relationship ends).
        
        Args:
            action_data: Dict with keys:
                - project_id (required)
                - licensed_business_id (required)
                - qualifier_id (required)
                - action_type (required): site_visit, plan_review, permit_review, 
                  client_meeting, inspection_attendance, phone_consultation
                - action_date (required): When action occurred (enforced by cutoff trigger)
                - duration_minutes (optional)
                - location (optional)
                - attendees (optional): List of {name, role} dicts
                - notes (optional)
                - photos (optional): List of photo URLs
                - created_by (optional): User ID who created this action
                
        Returns:
            Dict with created action data including auto-generated action_id
            
        Raises:
            Exception if action_date > cutoff_date (trigger will block)
        """
        async with AsyncSessionLocal() as session:
            try:
                new_action = OversightAction(
                    project_id=action_data["project_id"],
                    licensed_business_id=action_data["licensed_business_id"],
                    qualifier_id=action_data["qualifier_id"],
                    action_type=action_data["action_type"],
                    action_date=action_data["action_date"],
                    duration_minutes=action_data.get("duration_minutes"),
                    location=action_data.get("location"),
                    attendees=action_data.get("attendees"),
                    notes=action_data.get("notes"),
                    photos=action_data.get("photos"),
                    created_by=action_data.get("created_by"),
                )
                
                session.add(new_action)
                await session.commit()
                await session.refresh(new_action)
                
                logger.info(f"[DB_SERVICE] Created oversight action {new_action.action_id} for project {new_action.project_id}")
                
                return {
                    "id": new_action.id,
                    "action_id": new_action.action_id,
                    "project_id": new_action.project_id,
                    "licensed_business_id": new_action.licensed_business_id,
                    "qualifier_id": new_action.qualifier_id,
                    "action_type": new_action.action_type,
                    "action_date": new_action.action_date.isoformat(),
                    "location": new_action.location,
                    "notes": new_action.notes,
                }
                
            except Exception as e:
                await session.rollback()
                logger.error(f"[DB_SERVICE] Failed to create oversight action: {e}")
                raise
    
    async def create_compliance_justification(self, justification_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create compliance justification (rule override tracking).
        
        Args:
            justification_data: Dict with keys:
                - rule_type (required): capacity_limit, cutoff_date, oversight_minimum
                - entity_type (required): qualifier, licensed_business, project
                - entity_id (required): UUID of affected entity
                - justification_text (required): Why override was needed
                - risk_assessment (optional)
                - requested_by (optional): User ID who requested override
                - approved_by (optional): User ID who approved
                - approval_status (optional, defaults to 'pending')
                
        Returns:
            Dict with created justification data including auto-generated justification_id
        """
        async with AsyncSessionLocal() as session:
            try:
                new_justification = ComplianceJustification(
                    rule_type=justification_data["rule_type"],
                    entity_type=justification_data["entity_type"],
                    entity_id=justification_data["entity_id"],
                    justification_text=justification_data["justification_text"],
                    risk_assessment=justification_data.get("risk_assessment"),
                    requested_by=justification_data.get("requested_by"),
                    approved_by=justification_data.get("approved_by"),
                    approval_status=justification_data.get("approval_status", "pending"),
                )
                
                session.add(new_justification)
                await session.commit()
                await session.refresh(new_justification)
                
                logger.info(f"[DB_SERVICE] Created compliance justification {new_justification.justification_id}")
                
                return {
                    "id": new_justification.id,
                    "justification_id": new_justification.justification_id,
                    "rule_type": new_justification.rule_type,
                    "entity_type": new_justification.entity_type,
                    "entity_id": new_justification.entity_id,
                    "justification_text": new_justification.justification_text,
                    "approval_status": new_justification.approval_status,
                }
                
            except Exception as e:
                await session.rollback()
                logger.error(f"[DB_SERVICE] Failed to create compliance justification: {e}")
                raise
    
    async def get_qualifier_by_user_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get qualifier by user_id (1:1 relationship).
        
        Returns:
            Dict with qualifier data or None if user is not a qualifier
        """
        cache_key = f"qualifier_user_{user_id}"
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached
        
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Qualifier).where(Qualifier.user_id == user_id)
            )
            qualifier = result.scalar_one_or_none()
            
            if not qualifier:
                return None
            
            qualifier_data = {
                "id": qualifier.id,
                "qualifier_id": qualifier.qualifier_id,
                "user_id": qualifier.user_id,
                "full_name": qualifier.full_name,
                "qualifier_id_number": qualifier.qualifier_id_number,
                "license_type": qualifier.license_type,
                "license_status": qualifier.license_status,
                "max_licenses_allowed": qualifier.max_licenses_allowed,
                "email": qualifier.email,
                "phone": qualifier.phone,
            }
            
            self.cache.set(cache_key, qualifier_data)
            logger.info(f"[DB_SERVICE] Retrieved qualifier {qualifier.qualifier_id} for user {user_id}")
            return qualifier_data
    
    async def get_active_qualifier_assignments(self, qualifier_id: str) -> List[Dict[str, Any]]:
        """
        Get all active business assignments for a qualifier (where end_date IS NULL).
        
        Returns:
            List of dicts with relationship data
        """
        cache_key = f"qualifier_assignments_{qualifier_id}"
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached
        
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(LicensedBusinessQualifier)
                .where(
                    LicensedBusinessQualifier.qualifier_id == qualifier_id,
                    LicensedBusinessQualifier.end_date.is_(None)
                )
                .order_by(LicensedBusinessQualifier.start_date.desc())
            )
            assignments = result.scalars().all()
            
            assignments_data = []
            for assignment in assignments:
                assignments_data.append({
                    "id": assignment.id,
                    "licensed_business_id": assignment.licensed_business_id,
                    "qualifier_id": assignment.qualifier_id,
                    "start_date": assignment.start_date.isoformat() if assignment.start_date else None,
                    "cutoff_date": assignment.cutoff_date.isoformat() if assignment.cutoff_date else None,
                    "relationship_type": assignment.relationship_type,
                })
            
            self.cache.set(cache_key, assignments_data, ttl_seconds=60)  # Shorter TTL for active data
            logger.info(f"[DB_SERVICE] Retrieved {len(assignments_data)} active assignments for qualifier {qualifier_id}")
            return assignments_data
    
    async def check_qualifier_capacity(self, qualifier_id: str) -> Dict[str, Any]:
        """
        Check if qualifier can take on another business (enforces max_licenses_allowed).
        
        Returns:
            Dict with:
                - can_assign: bool - Whether qualifier has capacity
                - current_count: int - Current active assignments
                - max_allowed: int - Maximum allowed (from qualifiers table)
                - remaining: int - Remaining capacity
        """
        async with AsyncSessionLocal() as session:
            # Get qualifier to check max_licenses_allowed
            result = await session.execute(
                select(Qualifier).where(Qualifier.id == qualifier_id)
            )
            qualifier = result.scalar_one_or_none()
            
            if not qualifier:
                raise ValueError(f"Qualifier {qualifier_id} not found")
            
            # Count active assignments (end_date IS NULL)
            count_result = await session.execute(
                select(func.count())
                .select_from(LicensedBusinessQualifier)
                .where(
                    LicensedBusinessQualifier.qualifier_id == qualifier_id,
                    LicensedBusinessQualifier.end_date.is_(None)
                )
            )
            current_count = count_result.scalar()
            
            max_allowed = qualifier.max_licenses_allowed
            remaining = max_allowed - current_count
            can_assign = remaining > 0
            
            logger.info(f"[DB_SERVICE] Qualifier {qualifier.qualifier_id} capacity: {current_count}/{max_allowed} (can_assign={can_assign})")
            
            return {
                "can_assign": can_assign,
                "current_count": current_count,
                "max_allowed": max_allowed,
                "remaining": remaining,
            }


# Singleton instance
db_service = DBService()
