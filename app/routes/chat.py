from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional
import logging
import time

from app.services.openai_service import openai_service
import app.services.google_service as google_service_module
from app.services.quickbooks_service import quickbooks_service
from app.memory.memory_manager import memory_manager
from app.handlers.ai_functions import FUNCTION_HANDLERS
from app.utils.context_builder import build_context
from app.utils.logger import SessionLogger
from app.utils.timing import RequestTimer

# Session-aware logger for multi-user debugging
session_logger = SessionLogger(__name__)
logger = logging.getLogger(__name__)  # Keep for backward compatibility
router = APIRouter()

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
    # Start performance tracking
    request_start = time.time()
    
    # Reference quickbooks_service at function level to avoid scope issues
    qb_service = quickbooks_service
    
    try:
        message = chat_data.get("message", "")
        context = chat_data.get("context", {})
        session_id = chat_data.get("session_id", "default")  # Get session ID from frontend
        
        # Initialize request timer for detailed performance tracking
        timer = RequestTimer(session_id)
        
        session_logger.info(session_id, f"Processing message: {message[:100]}...")
        
        # Load session memory (conversation history) and add to context
        timer.start("memory_load")
        session_memory = memory_manager.get_all(session_id)
        
        # Get conversation history (last 10 messages to keep context manageable)
        conversation_history = session_memory.get("conversation_history", [])
        timer.stop("memory_load")
        session_logger.info(session_id, f"Loaded {len(conversation_history)} messages from history")
        
        if session_memory:
            context["session_memory"] = session_memory
            session_logger.debug(session_id, f"Session memory keys: {list(session_memory.keys())}")
        else:
            context["session_memory"] = {}
            session_logger.info(session_id, "No session memory found")
        
        # Add conversation history to context for OpenAI
        context["conversation_history"] = conversation_history[-10:]  # Last 10 exchanges
        
        # Smart context loading - only fetch what's needed based on message
        timer.start("context_build")
        
        try:
            google_service = get_google_service()
            
            # Use smart context builder to determine what data to load
            context = await build_context(
                message=message,
                google_service=google_service,
                qb_service=qb_service,
                session_memory=context.get("session_memory", {})
            )
            
            # Re-add conversation history (build_context overwrites)
            context["conversation_history"] = conversation_history[-10:]
            
            timer.stop("context_build")
            
        except Exception as e:
            timer.stop("context_build")
            session_logger.warning(session_id, f"Could not fetch data context: {e}")
            context.update({
                'error': 'Could not load full data context',
                'available_data': 'limited'
            })
        
        # Process message with OpenAI (now returns tuple: response, function_calls)
        timer.start("openai_call")
        ai_response, function_calls = await openai_service.process_chat_message(message, context)
        timer.stop("openai_call")
        
        # CRITICAL: Detect common hallucination patterns BEFORE any other validation
        import re
        
        # Known fake names that GPT commonly generates (excluding real customers like Ajay Nair)
        fake_name_patterns = [
            r'\bAlex\s+Chang\b', r'\bAlice\s+Johnson\b', r'\bBob\s+Smith\b',
            r'\bCharlotte\s+Wells\b', r'\bDavid\s+Brown\b', r'\bEmily\s+Clark\b', r'\bEthan\s+Thomas\b',
            r'\bIsabella\s+Martinez\b', r'\bJames\s+Taylor\b', r'\bJennifer\s+Lee\b', r'\bJohn\s+Doe\b',
            r'\bKaren\s+White\b', r'\bKevin\s+Nguyen\b', r'\bLaura\s+King\b', r'\bLinda\s+Green\b',
            r'\bMark\s+Davis\b', r'\bMichael\s+Johnson\b', r'\bNancy\s+Wilson\b', r'\bOlivia\s+Harris\b',
            r'\bPatricia\s+Lewis\b', r'\bRobert\s+Moore\b', r'\bSarah\s+Adams\b', r'\bThomas\s+Anderson\b'
        ]
        
        # Check for any fake names in response
        for pattern in fake_name_patterns:
            if re.search(pattern, ai_response, re.IGNORECASE):
                session_logger.error(
                    session_id,
                    f"🚨 AI HALLUCINATION DETECTED: Fabricated name found matching pattern '{pattern}'"
                )
                ai_response = (
                    f"⚠️ **Data Integrity Error**\n\n"
                    f"I detected that I was about to show you fabricated customer data (made-up names that don't exist in your system). "
                    f"This is a safety feature to prevent misinformation.\n\n"
                    f"**What I can do:**\n"
                    f"- Show you ONLY real customer data from your QuickBooks and Google Sheets\n"
                    f"- Search for specific customers by name\n"
                    f"- List actual invoices with real data\n\n"
                    f"Please ask your question again, and I'll make sure to show you only verified data from your system."
                )
                break
        
        # CRITICAL VALIDATION: Check for fabricated QuickBooks data
        # Prevents AI hallucination of QB Client IDs that don't exist
        if 'quickbooks' in context.get('contexts_loaded', []):
            qb_data = context.get('quickbooks', {})
            qb_customers = qb_data.get('customers', [])
            
            if qb_customers:
                # Extract all valid QB Client IDs from context
                valid_qb_ids = set()
                for customer in qb_customers:
                    qb_id = customer.get('Id')
                    if qb_id:
                        valid_qb_ids.add(str(qb_id))
                
                # Check if AI response contains QB Client IDs
                import re
                # Look for patterns like "QB Client ID: 166" or "QuickBooks ID 166"
                qb_id_pattern = r'(?:QB|QuickBooks)\s+(?:Client\s+)?ID[:\s]+(\d+)'
                found_ids = re.findall(qb_id_pattern, ai_response, re.IGNORECASE)
                
                # Validate each ID exists in loaded context
                for found_id in found_ids:
                    if found_id not in valid_qb_ids:
                        session_logger.error(
                            session_id,
                            f"🚨 AI HALLUCINATION DETECTED: QB Client ID {found_id} not in loaded context. "
                            f"Valid IDs: {valid_qb_ids}"
                        )
                        
                        # Check if client exists in Sheets but not synced to QB
                        sheets_clients = context.get('all_clients', [])
                        mentioned_in_message = None
                        
                        for client in sheets_clients:
                            client_name = client.get('Full Name') or client.get('Client Name', '')
                            if client_name.lower() in message.lower():
                                mentioned_in_message = client
                                break
                        
                        if mentioned_in_message:
                            client_name = mentioned_in_message.get('Full Name') or mentioned_in_message.get('Client Name')
                            qbo_id = mentioned_in_message.get('QBO_Client_ID')
                            
                            if not qbo_id:
                                # Client exists in Sheets but not synced to QuickBooks
                                ai_response = (
                                    f"⚠️ **Data Sync Issue Detected**\n\n"
                                    f"{client_name} exists in our database but hasn't been synced to QuickBooks yet. "
                                    f"Please sync this client to QuickBooks before viewing their financial details.\n\n"
                                    f"_Note: I cannot fabricate QuickBooks data for clients that aren't synced._"
                                )
                            else:
                                # Client has QBO_Client_ID but AI got it wrong
                                ai_response = (
                                    f"⚠️ **Verification Required**\n\n"
                                    f"I detected inconsistent QuickBooks data for {client_name}. "
                                    f"Please verify this client's QuickBooks ID manually.\n\n"
                                    f"_Tip: Cross-check in QuickBooks Online to ensure accuracy._"
                                )
                        else:
                            # Generic error - couldn't find what client they're asking about
                            ai_response = (
                                f"⚠️ **Data Verification Required**\n\n"
                                f"I found inconsistent QuickBooks Client ID information. "
                                f"Please verify this data in QuickBooks Online before taking action.\n\n"
                                f"_Note: Always verify financial data before creating invoices or processing payments._"
                            )
        
        # Execute any function calls requested by AI
        action_taken = None
        data_updated = False
        function_results = []
        memory_updates = {}  # Track what to remember
        
        if function_calls:
            timer.start("function_execution")
            google_service = get_google_service()
            
            for func_call in function_calls:
                func_name = func_call["name"]
                func_args = func_call["arguments"]
                
                try:
                    if func_name in FUNCTION_HANDLERS:
                        handler = FUNCTION_HANDLERS[func_name]
                        
                        # Route to appropriate service based on function name
                        if func_name in ['sync_quickbooks_customer_types', 'create_quickbooks_customer_from_sheet']:
                            # These functions need both services
                            result = await handler(func_args, google_service, quickbooks_service, memory_manager, session_id)
                        elif 'quickbooks' in func_name:
                            result = await handler(func_args, quickbooks_service, memory_manager, session_id)
                        else:
                            result = await handler(func_args, google_service, memory_manager, session_id)
                        
                        # Extract action and data_updated flags for backward compatibility
                        if result.get("status") == "success":
                            if result.get("action_taken"):
                                action_taken = result.get("action_taken")
                            if result.get("data_updated"):
                                data_updated = True
                        
                        # Collect any memory updates from handler
                        if "memory_updates" in result:
                            memory_updates.update(result["memory_updates"])
                        
                        function_results.append(result)
                    else:
                        function_results.append({
                            "function": func_name,
                            "status": "error",
                            "error": f"Unknown function: {func_name}"
                        })
                
                except Exception as e:
                    session_logger.error(session_id, f"Function call execution error: {e}")
                    function_results.append({
                        "function": func_name,
                        "status": "error",
                        "error": str(e)
                    })
            
            timer.stop("function_execution")
        
        # Update session memory with any new context
        if memory_updates:
            for key, value in memory_updates.items():
                memory_manager.set(session_id, key, value)
            session_logger.debug(session_id, f"Updated memory: {memory_updates}")
        
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
            session_logger.warning(session_id, f"Failed to sync session to Sheets: {sync_err}")
        
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
        session_logger.info(session_id, f"Saved conversation: {len(conversation_history)} messages total")
        
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
        
        # Log comprehensive performance metrics with timing breakdown
        request_duration_ms = (time.time() - request_start) * 1000
        timing_summary = timer.get_summary()
        
        # Detailed timing log
        session_logger.info(
            session_id,
            f"Request completed in {request_duration_ms:.0f}ms | "
            f"Context: {timing_summary.get('context_build', 0):.2f}s | "
            f"OpenAI: {timing_summary.get('openai_call', 0):.2f}s | "
            f"Functions: {timing_summary.get('function_execution', 0):.2f}s | "
            f"Action: {action_taken or 'none'}"
        )
        
        return {
            "response": ai_response,
            "action_taken": action_taken,
            "data_updated": data_updated,
            "function_results": function_results if function_results else None,
            "session_id": session_id,
            "memory_active": len(memory_manager.get_all(session_id)) > 0
        }
        
    except Exception as e:
        request_duration_ms = (time.time() - request_start) * 1000
        # Try to get session_id, fall back to None if not defined yet
        sid = locals().get('session_id') or chat_data.get('session_id')
        session_logger.error(sid, f"Chat error after {request_duration_ms:.0f}ms: {e}")
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
