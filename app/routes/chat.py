from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional
import logging

from app.services.openai_service import openai_service
import app.services.google_service as google_service_module

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
    """
    try:
        message = chat_data.get("message", "")
        context = chat_data.get("context", {})
        
        logger.info(f"Processing chat message: {message[:100]}...")
        
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
        
        return {
            "response": ai_response,
            "action_taken": action_taken,
            "data_updated": data_updated,
            "function_results": function_results if function_results else None
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
        
        return {
            "status": "operational",
            "openai_status": openai_status,
            "sheets_status": sheets_status,
            "features": [
                "Natural language queries with full data access",
                "Permit data access (all fields)",
                "Project tracking (complete)",
                "Client management (all details)",
                "Site visits, subcontractors, documents",
                "Tasks, payments, inspectors",
                "Construction phase tracking",
                "Advanced filtering and search",
                "Cross-sheet data analysis",
                "Automated notifications"
            ]
        }
        
    except Exception as e:
        logger.error(f"Status check error: {e}")
        raise HTTPException(status_code=500, detail="Status check failed")
