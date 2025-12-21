"""
Public intake routes for client and project forms.

Allows unauthenticated submissions to create basic `Client` and `Project` records
with intake/planning statuses. Designed for client/owner data entry.

Endpoints:
- POST /v1/intake/client
- POST /v1/intake/project
"""

from fastapi import APIRouter, HTTPException, Depends, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from typing import Optional
import logging

from app.db.session import get_db
from app.db.models import Client, Project, ClientStatus, ProjectStatus

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/intake", tags=["intake"])


@router.post("/client")
async def intake_client(
    full_name: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    address: Optional[str] = Form(None),
    city: Optional[str] = Form(None),
    state: Optional[str] = Form(None),
    zip_code: Optional[str] = Form(None),
    client_type: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
):
    """Public client intake form. Creates a `Client` with status INTAKE."""
    if not (full_name or email or phone):
        raise HTTPException(status_code=400, detail="Provide at least name, email, or phone")

    client = Client(
        full_name=full_name,
        email=email,
        phone=phone,
        address=address,
        city=city,
        state=state,
        zip_code=zip_code,
        client_type=client_type,
        status=ClientStatus.INTAKE,
    )

    db.add(client)
    await db.commit()
    await db.refresh(client)

    logger.info(f"Client intake created: {client.client_id} (business_id: {client.business_id})")
    return {
        "success": True,
        "client_id": client.client_id,
        "business_id": client.business_id,
        "status": client.status.value if client.status else None,
        "message": "Client intake submitted. Our team will review your information.",
    }


@router.post("/project")
async def intake_project(
    client_id: Optional[str] = Form(None),
    project_name: Optional[str] = Form(None),
    project_address: Optional[str] = Form(None),
    project_type: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
):
    """Public project intake form. Creates a `Project` linked to a client."""
    if not client_id:
        raise HTTPException(status_code=400, detail="client_id is required to create a project")

    # Verify client exists
    result = await db.execute(select(Client).where(Client.client_id == client_id))
    client = result.scalar_one_or_none()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    project = Project(
        client_id=client_id,
        project_name=project_name,
        project_address=project_address,
        project_type=project_type,
        description=description,
        notes=notes,
        status=ProjectStatus.PLANNING,
    )

    db.add(project)
    await db.commit()
    await db.refresh(project)

    logger.info(f"Project intake created: {project.project_id} (business_id: {project.business_id}) for client {client_id}")
    return {
        "success": True,
        "project_id": project.project_id,
        "business_id": project.business_id,
        "client_id": project.client_id,
        "status": project.status.value if project.status else None,
        "message": "Project intake submitted. Our team will review details.",
    }
