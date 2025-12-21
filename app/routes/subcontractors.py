"""
Subcontractor management routes.

Public form endpoint allows clients to submit subcontractor information
for their building permits. Authenticated endpoints allow internal management.

Endpoints:
- POST /v1/subcontractors/form - Public form submission (permit/project lookup)
- GET /v1/subcontractors/project/{project_id} - List subcontractors for project
- GET /v1/subcontractors/permit/{permit_id} - List subcontractors for permit
- GET /v1/subcontractors/{subcontractor_id} - Get single subcontractor
- PATCH /v1/subcontractors/{subcontractor_id}/approve - Approve subcontractor (admin)
- PATCH /v1/subcontractors/{subcontractor_id}/reject - Reject subcontractor (admin)
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, Query, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from typing import List, Optional
from uuid import uuid4
import logging

from app.db.session import get_db
from app.db.models import Subcontractor, Project, Permit, User
from app.services.supabase_auth_service import SupabaseAuthService
from app.routes.auth_supabase import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/subcontractors", tags=["subcontractors"])


class SubcontractorRequest:
    """Request model for subcontractor form submission"""
    full_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    company_name: Optional[str] = None
    trade: str
    license_number: Optional[str] = None
    license_state: Optional[str] = None
    bond_number: Optional[str] = None
    bond_amount: Optional[float] = None
    notes: Optional[str] = None
    project_id: Optional[str] = None  # For form submission
    permit_id: Optional[str] = None  # For form submission


@router.post("/form")
async def submit_subcontractor_form(
    full_name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    company_name: Optional[str] = Form(None),
    trade: str = Form(...),
    license_number: Optional[str] = Form(None),
    license_state: Optional[str] = Form(None),
    bond_number: Optional[str] = Form(None),
    bond_amount: Optional[float] = Form(None),
    notes: Optional[str] = Form(None),
    project_id: Optional[str] = Form(None),
    permit_id: Optional[str] = Form(None),
    coi_file: Optional[UploadFile] = File(None),
    workers_comp_file: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db),
    authorization: str | None = Header(None),
):
    """
    Public endpoint for submitting subcontractor information via form.
    
    Can submit for either a project or permit (or both).
    Optionally attach COI and Workers Comp documents.
    
    Returns: Created subcontractor record with status pending_approval
    """
    logger.info(f"Subcontractor form submission: {full_name} ({trade}) for project={project_id}, permit={permit_id}")
    
    # Validate that at least project_id or permit_id is provided
    if not project_id and not permit_id:
        raise HTTPException(
            status_code=400,
            detail="Must provide either project_id or permit_id"
        )
    
    # Verify project/permit exist
    if project_id:
        project = await db.execute(
            select(Project).where(Project.project_id == project_id)
        )
        if not project.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Project not found")
    
    if permit_id:
        permit = await db.execute(
            select(Permit).where(Permit.permit_id == permit_id)
        )
        if not permit.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Permit not found")
    
    # Handle file uploads (simplified - in production use proper document service)
    coi_doc_id = None
    workers_comp_doc_id = None
    coi_uploaded_at = None
    workers_comp_uploaded_at = None
    
    if coi_file:
        coi_doc_id = f"coi_{uuid4()}"
        coi_uploaded_at = datetime.utcnow()
        logger.info(f"COI uploaded: {coi_doc_id}")
    
    if workers_comp_file:
        workers_comp_doc_id = f"workers_comp_{uuid4()}"
        workers_comp_uploaded_at = datetime.utcnow()
        logger.info(f"Workers Comp uploaded: {workers_comp_doc_id}")
    
    # Create subcontractor record
    # Optional identity capture
    extra = {}
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1]
        auth = SupabaseAuthService()
        payload = auth.verify_jwt(token)
        if payload:
            extra.update({
                "submitted_by_email": payload.get("email"),
                "submitted_by_user_id": payload.get("sub"),
                "submitted_at": datetime.utcnow().isoformat(),
            })

    subcontractor = Subcontractor(
        subcontractor_id=str(uuid4()),
        project_id=project_id,
        permit_id=permit_id,
        full_name=full_name,
        email=email,
        phone=phone,
        company_name=company_name,
        trade=trade.upper(),
        license_number=license_number,
        license_state=license_state,
        bond_number=bond_number,
        bond_amount=bond_amount,
        coi_document_id=coi_doc_id,
        coi_uploaded_at=coi_uploaded_at,
        workers_comp_document_id=workers_comp_doc_id,
        workers_comp_uploaded_at=workers_comp_uploaded_at,
        status="pending_approval",
        notes=notes,
        extra=extra or None,
    )
    
    db.add(subcontractor)
    await db.commit()
    await db.refresh(subcontractor)
    
    logger.info(f"Subcontractor created: {subcontractor.subcontractor_id} (business_id: {subcontractor.business_id})")
    
    return {
        "success": True,
        "subcontractor_id": subcontractor.subcontractor_id,
        "business_id": subcontractor.business_id,
        "status": subcontractor.status,
        "message": "Subcontractor information submitted. Awaiting approval."
    }


@router.get("/project/{project_id}")
async def get_project_subcontractors(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all subcontractors for a project (authenticated)"""
    
    # Verify project exists and user has access
    project = await db.execute(
        select(Project).where(Project.project_id == project_id)
    )
    if not project.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Project not found")
    
    result = await db.execute(
        select(Subcontractor)
        .where(Subcontractor.project_id == project_id)
        .order_by(Subcontractor.created_at.desc())
    )
    subcontractors = result.scalars().all()
    
    logger.info(f"Retrieved {len(subcontractors)} subcontractors for project {project_id}")
    
    return {
        "project_id": project_id,
        "subcontractors": subcontractors,
        "count": len(subcontractors)
    }


@router.get("/permit/{permit_id}")
async def get_permit_subcontractors(
    permit_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all subcontractors for a permit (authenticated)"""
    
    # Verify permit exists
    permit = await db.execute(
        select(Permit).where(Permit.permit_id == permit_id)
    )
    if not permit.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Permit not found")
    
    result = await db.execute(
        select(Subcontractor)
        .where(Subcontractor.permit_id == permit_id)
        .order_by(Subcontractor.created_at.desc())
    )
    subcontractors = result.scalars().all()
    
    logger.info(f"Retrieved {len(subcontractors)} subcontractors for permit {permit_id}")
    
    return {
        "permit_id": permit_id,
        "subcontractors": subcontractors,
        "count": len(subcontractors)
    }


@router.get("/{subcontractor_id}")
async def get_subcontractor(
    subcontractor_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get single subcontractor details (authenticated)"""
    
    result = await db.execute(
        select(Subcontractor).where(Subcontractor.subcontractor_id == subcontractor_id)
    )
    subcontractor = result.scalar_one_or_none()
    
    if not subcontractor:
        raise HTTPException(status_code=404, detail="Subcontractor not found")
    
    logger.info(f"Retrieved subcontractor {subcontractor_id}")
    
    return subcontractor


@router.patch("/{subcontractor_id}/approve")
async def approve_subcontractor(
    subcontractor_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Approve a pending subcontractor (admin only)"""
    
    # TODO: Check user role/permissions
    
    result = await db.execute(
        select(Subcontractor).where(Subcontractor.subcontractor_id == subcontractor_id)
    )
    subcontractor = result.scalar_one_or_none()
    
    if not subcontractor:
        raise HTTPException(status_code=404, detail="Subcontractor not found")
    
    subcontractor.status = "approved"
    subcontractor.approved_by = current_user.id
    subcontractor.approved_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(subcontractor)
    
    logger.info(f"Subcontractor {subcontractor_id} approved by {current_user.email}")
    
    return {
        "success": True,
        "subcontractor": subcontractor,
        "status": subcontractor.status
    }


@router.patch("/{subcontractor_id}/reject")
async def reject_subcontractor(
    subcontractor_id: str,
    rejection_reason: str = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Reject a pending subcontractor (admin only)"""
    
    # TODO: Check user role/permissions
    
    result = await db.execute(
        select(Subcontractor).where(Subcontractor.subcontractor_id == subcontractor_id)
    )
    subcontractor = result.scalar_one_or_none()
    
    if not subcontractor:
        raise HTTPException(status_code=404, detail="Subcontractor not found")
    
    subcontractor.status = "rejected"
    subcontractor.rejection_reason = rejection_reason
    subcontractor.approved_by = current_user.id
    subcontractor.approved_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(subcontractor)
    
    logger.info(f"Subcontractor {subcontractor_id} rejected: {rejection_reason}")
    
    return {
        "success": True,
        "subcontractor": subcontractor,
        "status": subcontractor.status
    }
