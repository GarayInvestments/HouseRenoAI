"""
Set initial client statuses based on business logic.

Default logic:
- Clients with active projects → ACTIVE
- Clients with completed projects only → COMPLETED
- Clients with no projects → INTAKE
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.session import AsyncSessionLocal
from app.db.models import Client, Project, ClientStatus
from sqlalchemy import select, func


async def set_client_statuses():
    """Set intelligent default statuses for all clients."""
    
    async with AsyncSessionLocal() as db:
        # Get all clients
        result = await db.execute(
            select(Client).order_by(Client.full_name)
        )
        clients = result.scalars().all()
        
        updated_count = 0
        
        for client in clients:
            # Count projects by status
            project_result = await db.execute(
                select(
                    func.count(Project.project_id).label('total'),
                    func.count(Project.project_id).filter(
                        Project.status.in_(['Active', 'In Progress', 'Planning', 'Permit Under Review', 'Inspections In Progress'])
                    ).label('active_count'),
                    func.count(Project.project_id).filter(
                        Project.status == 'Completed'
                    ).label('completed_count')
                ).where(Project.client_id == client.client_id)
            )
            counts = project_result.first()
            
            # Determine status
            new_status = None
            if counts.total == 0:
                new_status = ClientStatus.INTAKE
                reason = "No projects"
            elif counts.active_count > 0:
                new_status = ClientStatus.ACTIVE
                reason = f"{counts.active_count} active project(s)"
            elif counts.completed_count == counts.total:
                new_status = ClientStatus.COMPLETED
                reason = f"All {counts.total} project(s) completed"
            else:
                new_status = ClientStatus.INTAKE
                reason = "Mixed project states"
            
            # Update client
            client.status = new_status
            print(f"✅ {client.full_name} → {new_status.value} ({reason})")
            updated_count += 1
        
        # Commit all changes
        await db.commit()
        
        print("\n" + "=" * 80)
        print(f"✅ Successfully updated {updated_count} clients")
        print("=" * 80)


if __name__ == "__main__":
    asyncio.run(set_client_statuses())
