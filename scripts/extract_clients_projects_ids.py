"""
Extract client and project IDs for reference documentation.
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.session import AsyncSessionLocal
from app.db.models import Client, Project
from sqlalchemy import select


async def extract_ids():
    """Extract client and project IDs."""
    
    async with AsyncSessionLocal() as db:
        # Get all clients
        result = await db.execute(
            select(Client).order_by(Client.full_name)
        )
        clients = result.scalars().all()
        
        # Get all projects
        result = await db.execute(
            select(Project).order_by(Project.client_id, Project.project_name)
        )
        projects = result.scalars().all()
        
        # Generate markdown
        output = []
        output.append("# Client and Project Reference IDs")
        output.append("")
        output.append(f"**Generated**: December 14, 2025")
        output.append(f"**Total Clients**: {len(clients)}")
        output.append(f"**Total Projects**: {len(projects)}")
        output.append("")
        output.append("---")
        output.append("")
        
        # Clients section
        output.append("## Clients")
        output.append("")
        output.append("| Client ID | Business ID | Full Name | QB Customer ID | Email | Phone |")
        output.append("|-----------|-------------|-----------|----------------|-------|-------|")
        
        for client in clients:
            qb_id = client.qb_customer_id or "N/A"
            email = client.email or "N/A"
            phone = client.phone or "N/A"
            business_id = client.business_id or "N/A"
            full_name = client.full_name or "N/A"
            output.append(f"| {client.client_id} | {business_id} | {full_name} | {qb_id} | {email} | {phone} |")
        
        output.append("")
        output.append("---")
        output.append("")
        
        # Projects section
        output.append("## Projects")
        output.append("")
        output.append("| Project ID | Business ID | Client ID | Client Name | Project Name | Status | Address |")
        output.append("|------------|-------------|-----------|-------------|--------------|--------|---------|")
        
        for project in projects:
            client = next((c for c in clients if c.client_id == project.client_id), None)
            client_name = client.full_name if client else "Unknown"
            status = project.status or "N/A"
            address = project.project_address or "N/A"
            business_id = project.business_id or "N/A"
            project_name = project.project_name or "N/A"
            output.append(f"| {project.project_id} | {business_id} | {project.client_id} | {client_name} | {project_name} | {status} | {address} |")
        
        output.append("")
        output.append("---")
        output.append("")
        
        # Projects grouped by client
        output.append("## Projects by Client")
        output.append("")
        
        for client in clients:
            client_projects = [p for p in projects if p.client_id == client.client_id]
            if client_projects:
                qb_id = client.qb_customer_id or "N/A"
                business_id = client.business_id or "N/A"
                output.append(f"### {client.full_name} (Client ID: {client.client_id}, Business ID: {business_id}, QB: {qb_id})")
                output.append("")
                output.append("| Project ID | Business ID | Project Name | Status | Address |")
                output.append("|------------|-------------|--------------|--------|---------|")
                for project in client_projects:
                    status = project.status or "N/A"
                    address = project.project_address or "N/A"
                    proj_business_id = project.business_id or "N/A"
                    project_name = project.project_name or "N/A"
                    output.append(f"| {project.project_id} | {proj_business_id} | {project_name} | {status} | {address} |")
                output.append("")
        
        # Write to file
        doc_path = Path(__file__).parent.parent / "docs" / "reference" / "CLIENTS_PROJECTS_IDS.md"
        doc_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(doc_path, "w", encoding="utf-8") as f:
            f.write("\n".join(output))
        
        print(f"✅ Documentation created: {doc_path}")
        print(f"   - {len(clients)} clients")
        print(f"   - {len(projects)} projects")
        
        return doc_path


if __name__ == "__main__":
    asyncio.run(extract_ids())
