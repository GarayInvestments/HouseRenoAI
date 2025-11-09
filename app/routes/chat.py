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
    # Reference quickbooks_service at function level to avoid scope issues
    qb_service = quickbooks_service
    
    try:
        message = chat_data.get("message", "")
        context = chat_data.get("context", {})
        session_id = chat_data.get("session_id", "default")  # Get session ID from frontend
        
        logger.info(f"Processing chat message for session {session_id}: {message[:100]}...")
        
        # Load session memory (conversation history) and add to context
        session_memory = memory_manager.get_all(session_id)
        
        # Get conversation history (last 10 messages to keep context manageable)
        conversation_history = session_memory.get("conversation_history", [])
        logger.info(f"Loaded {len(conversation_history)} previous messages from conversation history")
        
        if session_memory:
            context["session_memory"] = session_memory
            logger.info(f"Session memory keys: {list(session_memory.keys())}")
        else:
            context["session_memory"] = {}
            logger.info(f"No session memory found for session {session_id}")
        
        # Add conversation history to context for OpenAI
        context["conversation_history"] = conversation_history[-10:]  # Last 10 exchanges
        
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
            is_auth = False  # Initialize outside try block to avoid scope error
            try:
                logger.info(f"QuickBooks service exists: {qb_service is not None}")
                if qb_service:
                    # Use get_status() which reloads tokens if needed (more reliable than is_authenticated)
                    qb_status = qb_service.get_status()
                    is_auth = qb_status.get("authenticated", False)
                    logger.info(f"QuickBooks status: {qb_status}")
                    
                    # If not authenticated but we have a refresh token, try to refresh
                    if not is_auth and qb_service.refresh_token:
                        logger.info("QB not authenticated but refresh token exists, attempting refresh...")
                        try:
                            await qb_service.refresh_access_token()
                            logger.info("Successfully refreshed QB token")
                            is_auth = True
                        except Exception as refresh_err:
                            logger.warning(f"QB token refresh failed: {refresh_err}")
                            is_auth = False
                
                if qb_service and is_auth:
                    qb_customers = await qb_service.get_customers()
                    qb_invoices = await qb_service.get_invoices()
                    
                    logger.info(f"Successfully fetched QB data: {len(qb_customers)} customers, {len(qb_invoices)} invoices")
                    
                    # Only send summaries to reduce token usage
                    # Full data is too large (56k tokens, limit is 30k)
                    context.update({
                        'quickbooks_connected': True,
                        'qb_customers_count': len(qb_customers),
                        'qb_invoices_count': len(qb_invoices),
                        # Send compact customer summaries only
                        'qb_customers_summary': [
                            {
                                'id': c.get('Id'),
                                'name': c.get('DisplayName') or c.get('CompanyName') or c.get('FullyQualifiedName'),
                                'email': c.get('PrimaryEmailAddr', {}).get('Address') if c.get('PrimaryEmailAddr') else None,
                                'phone': c.get('PrimaryPhone', {}).get('FreeFormNumber') if c.get('PrimaryPhone') else None,
                                'balance': c.get('Balance', 0)
                            } for c in qb_customers
                        ],
                        # Send compact invoice summaries only (not full objects)
                        'qb_invoices_summary': [
                            {
                                'id': inv.get('Id'),
                                'doc_number': inv.get('DocNumber'),
                                'customer_name': inv.get('CustomerRef', {}).get('name'),
                                'txn_date': inv.get('TxnDate'),
                                'total': inv.get('TotalAmt', 0),
                                'balance': inv.get('Balance', 0),
                                'status': 'Paid' if inv.get('Balance', 0) == 0 else 'Unpaid'
                            } for inv in qb_invoices
                        ]
                    })
                    logger.info(f"Added QuickBooks context: {len(qb_customers)} customers, {len(qb_invoices)} invoices (summaries only)")
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
                            action_taken = f"Updated client {client_id} data"
                            data_updated = True
                            function_results.append({
                                "function": func_name,
                                "status": "success",
                                "details": f"Client {client_id} updated: {', '.join(updates.keys())}"
                            })
                            logger.info(f"AI executed: {action_taken}")
                        else:
                            function_results.append({
                                "function": func_name,
                                "status": "failed",
                                "error": "Update operation failed"
                            })
                    
                    elif func_name == "create_quickbooks_invoice":
                        from datetime import datetime, timedelta
                        
                        # Extract parameters
                        customer_id = func_args["customer_id"]
                        customer_name = func_args["customer_name"]
                        amount = func_args["amount"]
                        description = func_args["description"]
                        invoice_date = func_args.get("invoice_date", datetime.now().strftime("%Y-%m-%d"))
                        due_date = func_args.get("due_date", (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"))
                        
                        # Check QB authentication
                        if not qb_service or not qb_service.is_authenticated():
                            function_results.append({
                                "function": func_name,
                                "status": "failed",
                                "error": "QuickBooks is not authenticated. Please connect to QuickBooks first."
                            })
                            continue
                        
                        try:
                            # Get QB items to use for the line item (you may need to adjust this)
                            # For now, we'll use a generic service item or the first available item
                            items = await qb_service.get_items()
                            if not items:
                                function_results.append({
                                    "function": func_name,
                                    "status": "failed",
                                    "error": "No QuickBooks items/services found. Please create at least one service item in QuickBooks."
                                })
                                continue
                            
                            # Use first service/non-inventory item
                            service_item = next((item for item in items if item.get('Type') in ['Service', 'NonInventory']), items[0])
                            
                            # Build invoice data
                            invoice_data = {
                                "CustomerRef": {"value": customer_id},
                                "TxnDate": invoice_date,
                                "DueDate": due_date,
                                "Line": [{
                                    "Amount": amount,
                                    "DetailType": "SalesItemLineDetail",
                                    "Description": description,
                                    "SalesItemLineDetail": {
                                        "ItemRef": {"value": service_item.get('Id')},
                                        "Qty": 1,
                                        "UnitPrice": amount
                                    }
                                }]
                            }
                            
                            # Create the invoice
                            invoice = await qb_service.create_invoice(invoice_data)
                            
                            # Construct QuickBooks invoice link
                            invoice_id = invoice.get('Id')
                            invoice_number = invoice.get('DocNumber')
                            qb_invoice_link = f"https://app.qbo.intuit.com/app/invoice?txnId={invoice_id}" if invoice_id else None
                            
                            action_taken = f"Created QuickBooks invoice for {customer_name} - ${amount}"
                            data_updated = True
                            function_results.append({
                                "function": func_name,
                                "status": "success",
                                "details": f"Invoice #{invoice_number} created for {customer_name} - ${amount}",
                                "invoice_number": invoice_number,
                                "invoice_id": invoice_id,
                                "invoice_link": qb_invoice_link
                            })
                            logger.info(f"AI executed: {action_taken}")
                            
                            # Store invoice details in memory for follow-up questions
                            memory_updates["last_invoice_id"] = invoice_id
                            memory_updates["last_invoice_number"] = invoice_number
                            memory_updates["last_invoice_link"] = qb_invoice_link
                            
                        except Exception as invoice_error:
                            logger.error(f"Failed to create invoice: {invoice_error}")
                            function_results.append({
                                "function": func_name,
                                "status": "failed",
                                "error": f"Failed to create invoice: {str(invoice_error)}"
                            })
                    
                    elif func_name == "update_quickbooks_invoice":
                        invoice_id = func_args["invoice_id"]
                        invoice_number = func_args.get("invoice_number", "")
                        updates = func_args["updates"]
                        
                        # Check QB authentication
                        if not qb_service or not qb_service.is_authenticated():
                            function_results.append({
                                "function": func_name,
                                "status": "failed",
                                "error": "QuickBooks is not authenticated. Please connect to QuickBooks first."
                            })
                            continue
                        
                        try:
                            # Get the existing invoice to have full data
                            existing_invoice = await qb_service.get_invoice_by_id(invoice_id)
                            
                            # Build updated invoice data
                            updated_invoice_data = {**existing_invoice}
                            
                            # Update amount (modify line item)
                            if "amount" in updates:
                                new_amount = updates["amount"]
                                if updated_invoice_data.get("Line"):
                                    # Update the first line item amount
                                    updated_invoice_data["Line"][0]["Amount"] = new_amount
                                    if "SalesItemLineDetail" in updated_invoice_data["Line"][0]:
                                        updated_invoice_data["Line"][0]["SalesItemLineDetail"]["UnitPrice"] = new_amount
                            
                            # Update due date
                            if "due_date" in updates:
                                updated_invoice_data["DueDate"] = updates["due_date"]
                            
                            # Update description
                            if "description" in updates:
                                if updated_invoice_data.get("Line"):
                                    updated_invoice_data["Line"][0]["Description"] = updates["description"]
                            
                            # Update DocNumber (invoice number)
                            if "doc_number" in updates:
                                updated_invoice_data["DocNumber"] = updates["doc_number"]
                            
                            # Update the invoice
                            updated_invoice = await qb_service.update_invoice(invoice_id, updated_invoice_data)
                            
                            # Build description of what was updated
                            update_details = []
                            if "amount" in updates:
                                update_details.append(f"amount to ${updates['amount']}")
                            if "due_date" in updates:
                                update_details.append(f"due date to {updates['due_date']}")
                            if "description" in updates:
                                update_details.append(f"description")
                            if "doc_number" in updates:
                                update_details.append(f"invoice number to {updates['doc_number']}")
                            
                            update_summary = ", ".join(update_details)
                            invoice_num = invoice_number or updated_invoice.get('DocNumber', invoice_id)
                            
                            action_taken = f"Updated QuickBooks invoice #{invoice_num}: {update_summary}"
                            data_updated = True
                            
                            # Construct link
                            qb_invoice_link = f"https://app.qbo.intuit.com/app/invoice?txnId={invoice_id}"
                            
                            function_results.append({
                                "function": func_name,
                                "status": "success",
                                "details": f"Invoice #{invoice_num} updated: {update_summary}",
                                "invoice_number": invoice_num,
                                "invoice_id": invoice_id,
                                "invoice_link": qb_invoice_link
                            })
                            logger.info(f"AI executed: {action_taken}")
                            
                            # Store invoice details in memory
                            memory_updates["last_invoice_id"] = invoice_id
                            memory_updates["last_invoice_number"] = invoice_num
                            memory_updates["last_invoice_link"] = qb_invoice_link
                            
                        except Exception as invoice_error:
                            logger.error(f"Failed to update invoice: {invoice_error}")
                            function_results.append({
                                "function": func_name,
                                "status": "failed",
                                "error": f"Failed to update invoice: {str(invoice_error)}"
                            })
                    
                    elif func_name == "add_column_to_sheet":
                        sheet_name = func_args["sheet_name"]
                        column_name = func_args["column_name"]
                        default_value = func_args.get("default_value", "")
                        
                        # Execute the column addition
                        success = await google_service.add_column_to_sheet(
                            sheet_name=sheet_name,
                            column_name=column_name,
                            default_value=default_value
                        )
                        
                        if success:
                            action_taken = f"Added column '{column_name}' to {sheet_name}"
                            data_updated = True
                            function_results.append({
                                "function": func_name,
                                "status": "success",
                                "details": f"Column '{column_name}' added to {sheet_name}" + 
                                          (f" with default value '{default_value}'" if default_value else "")
                            })
                            logger.info(f"AI executed: {action_taken}")
                        else:
                            function_results.append({
                                "function": func_name,
                                "status": "failed",
                                "error": f"Failed to add column '{column_name}' to {sheet_name}"
                            })
                    
                    elif func_name == "update_client_field":
                        client_identifier = func_args["client_identifier"]
                        field_name = func_args["field_name"]
                        field_value = func_args["field_value"]
                        identifier_field = func_args.get("identifier_field", "Name")
                        
                        # Execute the client field update
                        success = await google_service.update_client_field(
                            client_identifier=client_identifier,
                            field_name=field_name,
                            field_value=field_value,
                            identifier_field=identifier_field
                        )
                        
                        if success:
                            action_taken = f"Updated {field_name} for client '{client_identifier}' to '{field_value}'"
                            data_updated = True
                            function_results.append({
                                "function": func_name,
                                "status": "success",
                                "details": f"Updated {field_name} to '{field_value}' for client '{client_identifier}'"
                            })
                            logger.info(f"AI executed: {action_taken}")
                        else:
                            function_results.append({
                                "function": func_name,
                                "status": "failed",
                                "error": f"Failed to update {field_name} for client '{client_identifier}'"
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
        
        # Sync session activity to Google Sheets (async, non-blocking)
        try:
            from datetime import datetime
            
            # Get current metadata
            metadata = memory_manager.get(session_id, "metadata")
            if metadata:
                metadata['last_activity'] = datetime.utcnow().isoformat()
                metadata['message_count'] = metadata.get('message_count', 0) + 1
                
                # Update in memory
                memory_manager.set(session_id, "metadata", metadata)
                
                # Save to Sheets (don't wait for it to avoid blocking response)
                google_service = get_google_service()
                import asyncio
                asyncio.create_task(google_service.save_session(metadata))
        except Exception as sync_err:
            logger.warning(f"Failed to sync session to Sheets: {sync_err}")
        
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
        
        # Save conversation history for context in future messages
        conversation_history = session_memory.get("conversation_history", [])
        conversation_history.append({
            "role": "user",
            "content": message[:500]  # Truncate long messages to save memory
        })
        conversation_history.append({
            "role": "assistant",
            "content": ai_response[:500]  # Truncate long responses
        })
        # Keep only last 20 messages (10 exchanges) to prevent memory bloat
        if len(conversation_history) > 20:
            conversation_history = conversation_history[-20:]
        memory_manager.set(session_id, "conversation_history", conversation_history, ttl_minutes=30)
        logger.info(f"Saved conversation history: {len(conversation_history)} messages total")
        
        # If function was executed but AI didn't return text, generate a confirmation
        if function_results and not ai_response:
            success_results = [r for r in function_results if r.get("status") == "success"]
            if success_results:
                # Check if it's an invoice creation - include link if available
                invoice_result = next((r for r in success_results if r.get("function") == "create_quickbooks_invoice"), None)
                if invoice_result and invoice_result.get("invoice_link"):
                    invoice_link = invoice_result["invoice_link"]
                    invoice_number = invoice_result.get("invoice_number", "")
                    ai_response = f"✅ Done! {action_taken}\n\n📄 [View Invoice #{invoice_number} in QuickBooks]({invoice_link})"
                else:
                    ai_response = f"✅ Done! {action_taken}"
            else:
                ai_response = "❌ There was an issue completing that action. Please try again."
        
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
async def list_sessions(user_email: Optional[str] = None):
    """
    List all chat sessions from Google Sheets (persistent) and memory (active)
    Combines both sources for complete session list
    """
    try:
        google_service = get_google_service()
        
        # Load sessions from Google Sheets (persistent storage)
        sheet_sessions = await google_service.load_all_sessions(user_email)
        
        # Also get active sessions from memory
        memory_sessions = memory_manager.list_sessions()
        
        # Merge: prioritize Sheets data, add memory-only sessions
        session_map = {s['session_id']: s for s in sheet_sessions}
        
        for mem_session in memory_sessions:
            if mem_session['session_id'] not in session_map:
                session_map[mem_session['session_id']] = mem_session
        
        sessions = list(session_map.values())
        
        return {
            "sessions": sessions,
            "total": len(sessions),
            "from_sheets": len(sheet_sessions),
            "from_memory": len(memory_sessions)
        }
    except Exception as e:
        logger.error(f"Failed to list sessions: {e}")
        raise HTTPException(status_code=500, detail="Failed to list sessions")

@router.post("/sessions")
async def create_session(session_data: Optional[dict] = None):
    """
    Create a new chat session with optional metadata
    Saves to both memory (fast) and Google Sheets (persistent)
    """
    try:
        import uuid
        from datetime import datetime
        import pytz
        
        session_id = f"session_{uuid.uuid4().hex[:16]}"
        session_data = session_data or {}
        
        # Get current time in EST
        est = pytz.timezone('America/New_York')
        now_est = datetime.now(est)
        timestamp = now_est.isoformat()
        
        # Format title as EST timestamp: "Nov 7, 2025 3:45 PM"
        default_title = now_est.strftime("%b %d, %Y %I:%M %p EST")
        
        # Initialize session with metadata
        metadata = {
            "session_id": session_id,
            "user_email": session_data.get("user_email", ""),
            "created_at": timestamp,
            "last_activity": timestamp,
            "title": session_data.get("title", default_title),
            "message_count": 0
        }
        
        # Save to memory (fast access)
        memory_manager.set(session_id, "metadata", metadata)
        
        # Save to Google Sheets (persistent storage)
        google_service = get_google_service()
        saved_to_sheets = await google_service.save_session(metadata)
        
        if not saved_to_sheets:
            logger.warning(f"Session {session_id} saved to memory but failed to save to Sheets")
        
        return {
            "session_id": session_id,
            "metadata": metadata,
            "persisted": saved_to_sheets
        }
    except Exception as e:
        logger.error(f"Failed to create session: {e}")
        raise HTTPException(status_code=500, detail="Failed to create session")

@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """
    Delete a specific chat session from both memory and Google Sheets
    """
    try:
        # Delete from memory
        memory_manager.clear(session_id)
        
        # Delete from Google Sheets
        google_service = get_google_service()
        deleted_from_sheets = await google_service.delete_session(session_id)
        
        logger.info(f"Deleted session: {session_id} (memory: yes, sheets: {deleted_from_sheets})")
        
        return {
            "session_id": session_id,
            "status": "deleted",
            "deleted_from_sheets": deleted_from_sheets
        }
    except Exception as e:
        logger.error(f"Failed to delete session: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete session")

@router.get("/sessions/{session_id}")
async def get_session_details(session_id: str):
    """
    Get full details and history for a specific session
    Loads from Google Sheets if not in memory (for resumed sessions)
    """
    try:
        # Try to get from memory first (active sessions)
        memory = memory_manager.get_all(session_id)
        metadata = memory_manager.get(session_id, "metadata")
        
        # If not in memory, try to load from Google Sheets
        if not metadata:
            google_service = get_google_service()
            sheet_metadata = await google_service.load_session(session_id)
            
            if sheet_metadata:
                metadata = sheet_metadata
                # Restore to memory for faster subsequent access
                memory_manager.set(session_id, "metadata", metadata)
            else:
                metadata = {}
        
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
    Updates both memory and Google Sheets
    """
    try:
        from datetime import datetime
        
        # Get current metadata from memory or Sheets
        current_metadata = memory_manager.get(session_id, "metadata")
        
        if not current_metadata:
            google_service = get_google_service()
            current_metadata = await google_service.load_session(session_id) or {}
        
        # Update with new values
        current_metadata.update(metadata)
        current_metadata['last_activity'] = datetime.utcnow().isoformat()
        
        # Save to memory
        memory_manager.set(session_id, "metadata", current_metadata)
        
        # Save to Google Sheets
        google_service = get_google_service()
        saved_to_sheets = await google_service.save_session(current_metadata)
        
        return {
            "session_id": session_id,
            "metadata": current_metadata,
            "persisted": saved_to_sheets
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
