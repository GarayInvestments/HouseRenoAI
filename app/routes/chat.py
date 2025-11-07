from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional
import logging

from app.services.openai_service import openai_service
import app.services.google_service as google_service_module
from app.services.quickbooks_service import quickbooks_service
from app.memory.memory_manager import memory_manager

logger = logging.getLogger(__name__)
router = APIRouter()

def _group_by_field(data: list, field: str) -> dict:
    """Group data items by a specific field value"""
    grouped = {}
    for item in data:
        value = item.get(field, 'Unknown')
        if value not in grouped:
            grouped[value] = []
        grouped[value].append(item)
    return {k: len(v) for k, v in grouped.items()}

def get_google_service():
    """Helper function to get Google service with proper error handling"""
    if not hasattr(google_service_module, 'google_service') or google_service_module.google_service is None:
        raise HTTPException(status_code=503, detail="Google service not initialized")
    return google_service_module.google_service

@router.post("/")
async def process_chat_message(chat_data: Dict[str, Any]):
    """
    Process a chat message using OpenAI and perform any necessary actions
    Includes short-term memory for conversational context
    """
    try:
        message = chat_data.get("message", "")
        context = chat_data.get("context", {})
        session_id = chat_data.get("session_id", "default")  # Get session ID from frontend
        
        logger.info(f"Processing chat message for session {session_id}: {message[:100]}...")
        
        # Load session memory and add to context
        session_memory = memory_manager.get_all(session_id)
        if session_memory:
            context["session_memory"] = session_memory
            logger.debug(f"Loaded session memory: {session_memory}")
        else:
            context["session_memory"] = {}
        
        # Always fetch comprehensive data for AI context
        try:
            google_service = get_google_service()
            
            # Fetch all core data
            permits = await google_service.get_permits_data()
            projects = await google_service.get_projects_data()
            clients = await google_service.get_clients_data()
            
            # Build comprehensive context with ALL data
            # Extract client IDs for easy reference
            client_ids = [c.get('Client ID', 'N/A') for c in clients if c.get('Client ID')]
            project_ids = [p.get('Project ID', 'N/A') for p in projects if p.get('Project ID')]
            permit_ids = [p.get('Permit ID', 'N/A') for p in permits if p.get('Permit ID')]
            
            context.update({
                # Counts
                'permits_count': len(permits),
                'projects_count': len(projects),
                'clients_count': len(clients),
                
                # ID Lists for quick lookup
                'client_ids': client_ids,
                'project_ids': project_ids,
                'permit_ids': permit_ids,
                
                # Full data arrays (AI can access everything)
                'all_permits': permits,
                'all_projects': projects,
                'all_clients': clients,
                
                # Summary data for quick reference
                'permits_by_status': _group_by_field(permits, 'Permit Status'),
                'projects_by_status': _group_by_field(projects, 'Status'),
                'clients_by_status': _group_by_field(clients, 'Status'),
                
                # Client summary for easy lookup
                'clients_summary': [
                    {
                        'Client ID': c.get('Client ID'),
                        'Name': c.get('Name'),
                        'Status': c.get('Status'),
                        'Address': c.get('Address'),
                        'Phone': c.get('Phone Number'),
                        'Email': c.get('Email')
                    } for c in clients
                ],
                
                # Additional metadata
                'available_sheets': [
                    'Clients', 'Projects', 'Permits', 'Site Visits',
                    'Subcontractors', 'Documents', 'Tasks', 'Payments',
                    'Jurisdiction', 'Inspectors', 'Construction Phase Tracking',
                    'Phase Tracking Images'
                ],
                
                # Data structure guide for AI
                'data_guide': {
                    'Clients': 'All client records with Status, Contact Info, etc.',
                    'Projects': 'All project records linked to clients',
                    'Permits': 'All permit records linked to projects',
                    'Site Visits': 'Construction site visit logs',
                    'Subcontractors': 'Subcontractor assignments and details',
                    'Documents': 'Project documents and files',
                    'Tasks': 'Task tracking and assignments',
                    'Payments': 'Payment records and invoicing',
                    'Jurisdiction': 'Permitting jurisdiction details',
                    'Inspectors': 'Inspector contact information',
                    'Construction Phase Tracking': 'Phase progress tracking',
                    'Phase Tracking Images': 'Construction progress photos'
                }
            })
            
            logger.info(f"Loaded full context: {len(permits)} permits, {len(projects)} projects, {len(clients)} clients")
            
            # Add QuickBooks data if available
            try:
                if quickbooks_service and quickbooks_service.is_authenticated():
                    qb_customers = await quickbooks_service.get_customers()
                    qb_invoices = await quickbooks_service.get_invoices()
                    
                    context.update({
                        'quickbooks_connected': True,
                        'qb_customers_count': len(qb_customers),
                        'qb_invoices_count': len(qb_invoices),
                        'qb_customers': qb_customers,
                        'qb_invoices': qb_invoices,
                        'qb_customers_summary': [
                            {
                                'id': c.get('Id'),
                                'name': c.get('DisplayName') or c.get('CompanyName') or c.get('FullyQualifiedName'),
                                'email': c.get('PrimaryEmailAddr', {}).get('Address') if c.get('PrimaryEmailAddr') else None,
                                'phone': c.get('PrimaryPhone', {}).get('FreeFormNumber') if c.get('PrimaryPhone') else None,
                                'balance': c.get('Balance', 0)
                            } for c in qb_customers
                        ]
                    })
                    logger.info(f"Added QuickBooks context: {len(qb_customers)} customers, {len(qb_invoices)} invoices")
                else:
                    context['quickbooks_connected'] = False
            except Exception as qb_err:
                logger.warning(f"Could not fetch QuickBooks data: {qb_err}")
                context['quickbooks_connected'] = False
            
        except Exception as e:
            logger.warning(f"Could not fetch data context: {e}")
            context.update({
                'error': 'Could not load full data context',
                'available_data': 'limited'
            })
        
        # Process message with OpenAI (now returns tuple: response, function_calls)
        ai_response, function_calls = await openai_service.process_chat_message(message, context)
        
        # Execute any function calls requested by AI
        action_taken = None
        data_updated = False
        function_results = []
        memory_updates = {}  # Track what to remember
        
        if function_calls:
            google_service = get_google_service()
            
            for func_call in function_calls:
                func_name = func_call["name"]
                func_args = func_call["arguments"]
                
                try:
                    if func_name == "update_project_status":
                        project_id = func_args["project_id"]
                        new_status = func_args["new_status"]
                        
                        # Execute the update
                        success = await google_service.update_record_by_id(
                            sheet_name='Projects',
                            id_field='Project ID',
                            record_id=project_id,
                            updates={'Status': new_status}
                        )
                        
                        if success:
                            action_taken = f"Updated project {project_id} status to {new_status}"
                            data_updated = True
                            function_results.append({
                                "function": func_name,
                                "status": "success",
                                "details": f"Project {project_id} status updated to {new_status}"
                            })
                            # Remember this in session memory
                            memory_updates["last_project_id"] = project_id
                            memory_updates["last_action"] = f"updated_project_status_{new_status}"
                            logger.info(f"AI executed: {action_taken}")
                        else:
                            function_results.append({
                                "function": func_name,
                                "status": "failed",
                                "error": "Update operation failed"
                            })
                    
                    elif func_name == "update_permit_status":
                        permit_id = func_args["permit_id"]
                        new_status = func_args["new_status"]
                        
                        # Execute the update
                        success = await google_service.update_record_by_id(
                            sheet_name='Permits',
                            id_field='Permit ID',
                            record_id=permit_id,
                            updates={'Permit Status': new_status}
                        )
                        
                        if success:
                            action_taken = f"Updated permit {permit_id} status to {new_status}"
                            data_updated = True
                            function_results.append({
                                "function": func_name,
                                "status": "success",
                                "details": f"Permit {permit_id} status updated to {new_status}"
                            })
                            # Remember this in session memory
                            memory_updates["last_permit_id"] = permit_id
                            memory_updates["last_action"] = f"updated_permit_status_{new_status}"
                            logger.info(f"AI executed: {action_taken}")
                        else:
                            function_results.append({
                                "function": func_name,
                                "status": "failed",
                                "error": "Update operation failed"
                            })
                    
                    elif func_name == "update_client_data":
                        client_id = func_args["client_id"]
                        updates = func_args["updates"]
                        
                        # Execute the update
                        success = await google_service.update_record_by_id(
                            sheet_name='Clients',
                            id_field='Client ID',
                            record_id=client_id,
                            updates=updates
                        )
                        
                        if success:
                            fields_updated = ", ".join(updates.keys())
                            action_taken = f"Updated client {client_id}: {fields_updated}"
                            data_updated = True
                            function_results.append({
                                "function": func_name,
                                "status": "success",
                                "details": f"Client {client_id} updated: {fields_updated}"
                            })
                            # Remember this in session memory
                            memory_updates["last_client_id"] = client_id
                            memory_updates["last_action"] = "updated_client_data"
                            logger.info(f"AI executed: {action_taken}")
                        else:
                            function_results.append({
                                "function": func_name,
                                "status": "failed",
                                "error": "Update operation failed"
                            })
                    
                except Exception as e:
                    logger.error(f"Function call execution error: {e}")
                    function_results.append({
                        "function": func_name,
                        "status": "error",
                        "error": str(e)
                    })
        
        # Update session memory with any new context
        if memory_updates:
            for key, value in memory_updates.items():
                memory_manager.set(session_id, key, value)
            logger.debug(f"Updated session memory: {memory_updates}")
        
        # Auto-detect and store entities mentioned in the message
        # This helps with follow-up questions like "update its status"
        if "project" in message.lower() and not memory_updates.get("last_project_id"):
            # Try to extract project ID from message
            for project in context.get('all_projects', []):
                project_id = project.get('Project ID', '')
                if project_id and project_id.lower() in message.lower():
                    memory_manager.set(session_id, "last_project_id", project_id)
                    memory_manager.set(session_id, "last_mentioned_entity", "project")
                    break
        
        if "permit" in message.lower() and not memory_updates.get("last_permit_id"):
            # Try to extract permit ID from message
            for permit in context.get('all_permits', []):
                permit_id = permit.get('Permit ID', '')
                if permit_id and permit_id.lower() in message.lower():
                    memory_manager.set(session_id, "last_permit_id", permit_id)
                    memory_manager.set(session_id, "last_mentioned_entity", "permit")
                    break
        
        if "client" in message.lower() and not memory_updates.get("last_client_id"):
            # Try to extract client ID from message
            for client in context.get('all_clients', []):
                client_id = client.get('Client ID', '')
                if client_id and client_id.lower() in message.lower():
                    memory_manager.set(session_id, "last_client_id", client_id)
                    memory_manager.set(session_id, "last_mentioned_entity", "client")
                    break
        
        return {
            "response": ai_response,
            "action_taken": action_taken,
            "data_updated": data_updated,
            "function_results": function_results if function_results else None,
            "session_id": session_id,
            "memory_active": len(memory_manager.get_all(session_id)) > 0
        }
        
    except Exception as e:
        logger.error(f"Chat processing error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process message: {str(e)}")

@router.post("/query")
async def advanced_query(query_data: Dict[str, Any]):
    """
    Advanced query endpoint for specific data requests
    Supports filtering, sorting, and aggregations
    """
    try:
        sheet_name = query_data.get("sheet", "all")
        filters = query_data.get("filters", {})
        fields = query_data.get("fields", [])
        
        google_service = get_google_service()
        
        if sheet_name == "all":
            data = await google_service.get_comprehensive_data()
        else:
            data = await google_service.get_all_sheet_data(sheet_name)
        
        # Apply filters if provided
        if filters and isinstance(data, list):
            filtered_data = []
            for item in data:
                matches = all(item.get(k) == v for k, v in filters.items())
                if matches:
                    filtered_data.append(item)
            data = filtered_data
        
        # Select specific fields if requested
        if fields and isinstance(data, list):
            data = [{k: item.get(k) for k in fields} for item in data]
        
        return {
            "sheet": sheet_name,
            "count": len(data) if isinstance(data, list) else sum(len(v) for v in data.values()),
            "data": data
        }
        
    except Exception as e:
        logger.error(f"Query error: {e}")
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

@router.get("/memory/{session_id}")
async def get_session_memory(session_id: str):
    """
    Get current memory for a session
    """
    try:
        memory = memory_manager.get_all(session_id)
        return {
            "session_id": session_id,
            "memory": memory,
            "active": len(memory) > 0
        }
    except Exception as e:
        logger.error(f"Memory retrieval error: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve memory")

@router.post("/memory/{session_id}/clear")
async def clear_session_memory(session_id: str):
    """
    Clear memory for a specific session
    """
    try:
        memory_manager.clear(session_id)
        logger.info(f"Cleared memory for session: {session_id}")
        return {
            "session_id": session_id,
            "status": "cleared"
        }
    except Exception as e:
        logger.error(f"Memory clear error: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear memory")

@router.get("/memory/stats")
async def get_memory_stats():
    """
    Get statistics about memory usage
    """
    try:
        stats = memory_manager.get_stats()
        return stats
    except Exception as e:
        logger.error(f"Memory stats error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get memory stats")

@router.get("/sessions")
async def list_sessions():
    """
    List all active chat sessions with metadata
    """
    try:
        sessions = memory_manager.list_sessions()
        return {
            "sessions": sessions,
            "total": len(sessions)
        }
    except Exception as e:
        logger.error(f"Failed to list sessions: {e}")
        raise HTTPException(status_code=500, detail="Failed to list sessions")

@router.post("/sessions")
async def create_session(session_data: Optional[dict] = None):
    """
    Create a new chat session with optional metadata
    """
    try:
        import uuid
        from datetime import datetime
        
        session_id = f"session_{uuid.uuid4().hex[:16]}"
        session_data = session_data or {}
        
        # Initialize session with metadata
        metadata = {
            "created_at": datetime.utcnow().isoformat(),
            "title": session_data.get("title", "New Chat"),
            "message_count": 0
        }
        
        memory_manager.set(session_id, "metadata", metadata)
        
        return {
            "session_id": session_id,
            "metadata": metadata
        }
    except Exception as e:
        logger.error(f"Failed to create session: {e}")
        raise HTTPException(status_code=500, detail="Failed to create session")

@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """
    Delete a specific chat session and all its data
    """
    try:
        memory_manager.clear(session_id)
        logger.info(f"Deleted session: {session_id}")
        return {
            "session_id": session_id,
            "status": "deleted"
        }
    except Exception as e:
        logger.error(f"Failed to delete session: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete session")

@router.get("/sessions/{session_id}")
async def get_session_details(session_id: str):
    """
    Get full details and history for a specific session
    """
    try:
        memory = memory_manager.get_all(session_id)
        metadata = memory_manager.get(session_id, "metadata") or {}
        
        return {
            "session_id": session_id,
            "metadata": metadata,
            "memory": memory,
            "active": len(memory) > 0
        }
    except Exception as e:
        logger.error(f"Failed to get session details: {e}")
        raise HTTPException(status_code=500, detail="Failed to get session details")

@router.put("/sessions/{session_id}/metadata")
async def update_session_metadata(session_id: str, metadata: dict):
    """
    Update session metadata (e.g., rename chat)
    """
    try:
        current_metadata = memory_manager.get(session_id, "metadata") or {}
        current_metadata.update(metadata)
        memory_manager.set(session_id, "metadata", current_metadata)
        
        return {
            "session_id": session_id,
            "metadata": current_metadata
        }
    except Exception as e:
        logger.error(f"Failed to update session metadata: {e}")
        raise HTTPException(status_code=500, detail="Failed to update session metadata")

@router.get("/status")
async def get_chat_status():
    """
    Get the current status of the chat system
    """
    try:
        # Test OpenAI connection
        openai_status = "connected"
        try:
            await openai_service.process_chat_message("test")
        except:
            openai_status = "error"
        
        # Test Google Sheets connection
        sheets_status = "connected"
        try:
            google_service = get_google_service()
            await google_service.read_sheet_data("A1:A1")
        except:
            sheets_status = "error"
        
        # Get memory stats
        memory_stats = memory_manager.get_stats()
        
        return {
            "status": "operational",
            "openai_status": openai_status,
            "sheets_status": sheets_status,
            "memory_stats": memory_stats,
            "features": [
                "Natural language queries with full data access",
                "Session memory for context retention",
                "Permit data access (all fields)",
                "Project tracking (complete)",
                "Client management (all details)",
                "Site visits, subcontractors, documents",
                "Tasks, payments, inspectors",
                "Construction phase tracking",
                "Advanced filtering and search",
                "Cross-sheet data analysis",
                "Automated notifications",
                "Client data updates (CRUD)"
            ]
        }
        
    except Exception as e:
        logger.error(f"Status check error: {e}")
        raise HTTPException(status_code=500, detail="Status check failed")
