"""
AI Function Handlers

This module contains all function handlers that the AI can call to interact with
Google Sheets, QuickBooks, and other services. Each handler follows a consistent
pattern with error handling and logging.
"""

import logging
from typing import Dict, Any
from datetime import datetime, timedelta
from fastapi import HTTPException

logger = logging.getLogger(__name__)


async def handle_update_project_status(
    args: Dict[str, Any],
    google_service,
    memory_manager,
    session_id: str
) -> Dict[str, Any]:
    """
    Update project status in Google Sheets
    
    Args:
        args: Function arguments containing project_id and new_status
        google_service: Google Sheets service instance
        memory_manager: Session memory manager
        session_id: Current session ID
        
    Returns:
        Dictionary with status and details
    """
    try:
        project_id = args["project_id"]
        new_status = args["new_status"]
        
        # Execute the update
        success = await google_service.update_record_by_id(
            sheet_name='Projects',
            id_field='Project ID',
            record_id=project_id,
            updates={'Status': new_status}
        )
        
        if success:
            # Remember this in session memory
            memory_manager.set(session_id, "last_project_id", project_id)
            memory_manager.set(session_id, "last_action", f"updated_project_status_{new_status}")
            
            logger.info(f"AI executed: Updated project {project_id} status to {new_status}")
            
            return {
                "status": "success",
                "details": f"Project {project_id} status updated to {new_status}",
                "action_taken": f"Updated project {project_id} status to {new_status}",
                "data_updated": True
            }
        else:
            return {
                "status": "failed",
                "error": "Update operation failed"
            }
            
    except Exception as e:
        logger.error(f"Error updating project status: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating project status: {str(e)}")


async def handle_update_permit_status(
    args: Dict[str, Any],
    google_service,
    memory_manager,
    session_id: str
) -> Dict[str, Any]:
    """
    Update permit status in Google Sheets
    
    Args:
        args: Function arguments containing permit_id and new_status
        google_service: Google Sheets service instance
        memory_manager: Session memory manager
        session_id: Current session ID
        
    Returns:
        Dictionary with status and details
    """
    try:
        permit_id = args["permit_id"]
        new_status = args["new_status"]
        
        # Execute the update
        success = await google_service.update_record_by_id(
            sheet_name='Permits',
            id_field='Permit ID',
            record_id=permit_id,
            updates={'Permit Status': new_status}
        )
        
        if success:
            # Remember this in session memory
            memory_manager.set(session_id, "last_permit_id", permit_id)
            memory_manager.set(session_id, "last_action", f"updated_permit_status_{new_status}")
            
            logger.info(f"AI executed: Updated permit {permit_id} status to {new_status}")
            
            return {
                "status": "success",
                "details": f"Permit {permit_id} status updated to {new_status}",
                "action_taken": f"Updated permit {permit_id} status to {new_status}",
                "data_updated": True
            }
        else:
            return {
                "status": "failed",
                "error": "Update operation failed"
            }
            
    except Exception as e:
        logger.error(f"Error updating permit status: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating permit status: {str(e)}")


async def handle_update_client_data(
    args: Dict[str, Any],
    google_service,
    memory_manager,
    session_id: str
) -> Dict[str, Any]:
    """
    Update client data in Google Sheets
    
    Args:
        args: Function arguments containing client_id and updates dict
        google_service: Google Sheets service instance
        memory_manager: Session memory manager
        session_id: Current session ID
        
    Returns:
        Dictionary with status and details
    """
    try:
        client_id = args["client_id"]
        updates = args["updates"]
        
        # Execute the update
        success = await google_service.update_record_by_id(
            sheet_name='Clients',
            id_field='Client ID',
            record_id=client_id,
            updates=updates
        )
        
        if success:
            logger.info(f"AI executed: Updated client {client_id} data")
            
            return {
                "status": "success",
                "details": f"Client {client_id} updated: {', '.join(updates.keys())}",
                "action_taken": f"Updated client {client_id} data",
                "data_updated": True
            }
        else:
            return {
                "status": "failed",
                "error": "Update operation failed"
            }
            
    except Exception as e:
        logger.error(f"Error updating client data: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating client data: {str(e)}")


async def handle_create_quickbooks_invoice(
    args: Dict[str, Any],
    qb_service,
    memory_manager,
    session_id: str
) -> Dict[str, Any]:
    """
    Create QuickBooks invoice
    
    Args:
        args: Function arguments containing customer_id, customer_name, amount, description, etc.
        qb_service: QuickBooks service instance
        memory_manager: Session memory manager
        session_id: Current session ID
        
    Returns:
        Dictionary with status, invoice details, and link
    """
    try:
        # Extract parameters
        customer_id = args["customer_id"]
        customer_name = args["customer_name"]
        amount = args["amount"]
        description = args["description"]
        invoice_date = args.get("invoice_date", datetime.now().strftime("%Y-%m-%d"))
        due_date = args.get("due_date", (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"))
        
        # Check QB authentication
        if not qb_service or not qb_service.is_authenticated():
            return {
                "status": "failed",
                "error": "QuickBooks is not authenticated. Please connect to QuickBooks first."
            }
        
        # Get QB items to use for the line item
        items = await qb_service.get_items()
        if not items:
            return {
                "status": "failed",
                "error": "No QuickBooks items/services found. Please create at least one service item in QuickBooks."
            }
        
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
        
        # Store invoice details in memory for follow-up questions
        memory_manager.set(session_id, "last_invoice_id", invoice_id)
        memory_manager.set(session_id, "last_invoice_number", invoice_number)
        memory_manager.set(session_id, "last_invoice_link", qb_invoice_link)
        
        logger.info(f"AI executed: Created QuickBooks invoice for {customer_name} - ${amount}")
        
        return {
            "status": "success",
            "details": f"Invoice #{invoice_number} created for {customer_name} - ${amount}",
            "invoice_number": invoice_number,
            "invoice_id": invoice_id,
            "invoice_link": qb_invoice_link,
            "action_taken": f"Created QuickBooks invoice for {customer_name} - ${amount}",
            "data_updated": True
        }
        
    except Exception as e:
        logger.error(f"Failed to create invoice: {e}")
        return {
            "status": "failed",
            "error": f"Failed to create invoice: {str(e)}"
        }


async def handle_update_quickbooks_invoice(
    args: Dict[str, Any],
    qb_service,
    memory_manager,
    session_id: str
) -> Dict[str, Any]:
    """
    Update QuickBooks invoice
    
    Args:
        args: Function arguments containing invoice_id, invoice_number (optional), and updates dict
        qb_service: QuickBooks service instance
        memory_manager: Session memory manager
        session_id: Current session ID
        
    Returns:
        Dictionary with status and details
    """
    try:
        invoice_id = args["invoice_id"]
        invoice_number = args.get("invoice_number", "")
        updates = args["updates"]
        
        logger.info(f"Update invoice request - ID: {invoice_id}, Updates: {updates}")
        
        # Check QB authentication
        if not qb_service or not qb_service.is_authenticated():
            return {
                "status": "failed",
                "error": "QuickBooks is not authenticated. Please connect to QuickBooks first."
            }
        
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
        
        logger.info(f"AI executed: Updated QuickBooks invoice #{invoice_num}: {update_summary}")
        
        # Construct QuickBooks invoice link
        qb_invoice_link = f"https://app.qbo.intuit.com/app/invoice?txnId={invoice_id}"
        
        return {
            "status": "success",
            "details": f"Invoice #{invoice_num} updated: {update_summary}",
            "invoice_number": invoice_num,
            "invoice_id": invoice_id,
            "invoice_link": qb_invoice_link,
            "action_taken": f"Updated QuickBooks invoice #{invoice_num}: {update_summary}",
            "data_updated": True
        }
        
    except Exception as e:
        logger.error(f"Failed to update invoice: {e}")
        return {
            "status": "failed",
            "error": f"Failed to update invoice: {str(e)}"
        }


async def handle_add_column_to_sheet(
    args: Dict[str, Any],
    google_service,
    memory_manager,
    session_id: str
) -> Dict[str, Any]:
    """
    Add a new column to a Google Sheet
    
    Args:
        args: Function arguments containing sheet_name, column_name, and optional default_value
        google_service: Google Sheets service instance
        memory_manager: Session memory manager
        session_id: Current session ID
        
    Returns:
        Dictionary with status and details
    """
    try:
        sheet_name = args["sheet_name"]
        column_name = args["column_name"]
        default_value = args.get("default_value", "")
        
        # Execute the column addition
        success = await google_service.add_column_to_sheet(
            sheet_name=sheet_name,
            column_name=column_name,
            default_value=default_value
        )
        
        if success:
            logger.info(f"AI executed: Added column '{column_name}' to {sheet_name}")
            
            details = f"Column '{column_name}' added to {sheet_name}"
            if default_value:
                details += f" with default value '{default_value}'"
            
            return {
                "status": "success",
                "details": details,
                "action_taken": f"Added column '{column_name}' to {sheet_name}",
                "data_updated": True
            }
        else:
            return {
                "status": "failed",
                "error": f"Failed to add column '{column_name}' to {sheet_name}"
            }
            
    except Exception as e:
        logger.error(f"Error adding column to sheet: {e}")
        raise HTTPException(status_code=500, detail=f"Error adding column to sheet: {str(e)}")


async def handle_update_client_field(
    args: Dict[str, Any],
    google_service,
    memory_manager,
    session_id: str
) -> Dict[str, Any]:
    """
    Update a specific field for a client (searched by name or other identifier)
    
    Args:
        args: Function arguments containing client_identifier, field_name, field_value, and optional identifier_field
        google_service: Google Sheets service instance
        memory_manager: Session memory manager
        session_id: Current session ID
        
    Returns:
        Dictionary with status and details
    """
    try:
        client_identifier = args["client_identifier"]
        field_name = args["field_name"]
        field_value = args["field_value"]
        identifier_field = args.get("identifier_field", "Name")
        
        # Execute the client field update
        success = await google_service.update_client_field(
            client_identifier=client_identifier,
            field_name=field_name,
            field_value=field_value,
            identifier_field=identifier_field
        )
        
        if success:
            logger.info(f"AI executed: Updated {field_name} for client '{client_identifier}' to '{field_value}'")
            
            return {
                "status": "success",
                "details": f"Updated {field_name} to '{field_value}' for client '{client_identifier}'",
                "action_taken": f"Updated {field_name} for client '{client_identifier}' to '{field_value}'",
                "data_updated": True
            }
        else:
            return {
                "status": "failed",
                "error": f"Failed to update {field_name} for client '{client_identifier}'"
            }
            
    except Exception as e:
        logger.error(f"Error updating client field: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating client field: {str(e)}")


async def handle_sync_quickbooks_clients(
    args: Dict[str, Any],
    quickbooks_service,
    memory_manager,
    session_id: str
) -> Dict[str, Any]:
    """
    Sync all clients from Google Sheets with QuickBooks customers
    Matches by name/email and updates QBO_Client_ID column
    
    Args:
        args: Function arguments (dry_run: bool optional)
        quickbooks_service: QuickBooks service instance  
        memory_manager: Session memory manager
        session_id: Current session ID
        
    Returns:
        Dictionary with sync results
    """
    try:
        dry_run = args.get("dry_run", False)
        logger.info(f"[SYNC DEBUG] Received args: {args}, dry_run={dry_run}")
        
        # Import google_service here to avoid circular dependency
        import app.services.google_service as google_service_module
        google_service = google_service_module.google_service
        
        if not google_service:
            return {
                "status": "failed",
                "error": "Google service not available"
            }
        
        # Get all clients from Sheets
        clients_data = await google_service.get_all_sheet_data('Clients')
        if not clients_data:
            return {
                "status": "failed",
                "error": "No clients found in database"
            }
        
        # Get all QB customers
        qb_customers = await quickbooks_service.get_customers()
        if not qb_customers:
            return {
                "status": "failed",
                "error": "No QuickBooks customers found"
            }
        
        # Build QB lookup by name and email
        qb_by_name = {}
        qb_by_email = {}
        for customer in qb_customers:
            # Name variations
            display_name = customer.get('DisplayName', '').lower().strip()
            company_name = customer.get('CompanyName', '').lower().strip()
            full_name = customer.get('FullyQualifiedName', '').lower().strip()
            
            qb_id = str(customer.get('Id'))
            
            if display_name:
                qb_by_name[display_name] = qb_id
            if company_name:
                qb_by_name[company_name] = qb_id
            if full_name:
                qb_by_name[full_name] = qb_id
            
            # Email lookup
            email_obj = customer.get('PrimaryEmailAddr', {})
            if isinstance(email_obj, dict):
                email = email_obj.get('Address', '').lower().strip()
                if email:
                    qb_by_email[email] = qb_id
        
        # Match and sync
        matched = []
        not_matched = []
        already_synced = []
        updates_made = []
        
        for client in clients_data:
            client_name = (client.get('Full Name') or client.get('Client Name') or '').strip()
            client_email = (client.get('Email') or '').strip().lower()
            current_qbo_id = client.get('QBO_Client_ID')
            client_id = client.get('Client ID')
            
            if not client_name:
                continue
            
            # Check if already has QBO ID
            if current_qbo_id:
                already_synced.append({
                    "name": client_name,
                    "qbo_id": current_qbo_id
                })
                continue
            
            # Try to match
            qb_id = None
            match_method = None
            
            # Try name matching (with variations)
            client_name_lower = client_name.lower().strip()
            client_name_no_llc = client_name_lower.replace(' llc', '').replace(', llc', '').strip()
            
            if client_name_lower in qb_by_name:
                qb_id = qb_by_name[client_name_lower]
                match_method = "exact_name"
            elif client_name_no_llc in qb_by_name:
                qb_id = qb_by_name[client_name_no_llc]
                match_method = "name_without_llc"
            elif client_email and client_email in qb_by_email:
                qb_id = qb_by_email[client_email]
                match_method = "email"
            
            if qb_id:
                matched.append({
                    "name": client_name,
                    "email": client_email,
                    "qbo_id": qb_id,
                    "match_method": match_method
                })
                
                # Update in Sheets (unless dry run)
                if not dry_run and client_id:
                    success = await google_service.update_record_by_id(
                        sheet_name='Clients',
                        id_field='Client ID',
                        record_id=client_id,
                        updates={'QBO_Client_ID': qb_id}
                    )
                    if success:
                        updates_made.append(client_name)
            else:
                not_matched.append({
                    "name": client_name,
                    "email": client_email
                })
        
        # Build result message
        result_message = f"**QuickBooks Sync Results**\n\n"
        result_message += f"✅ Matched: {len(matched)}\n"
        result_message += f"⏭️ Already synced: {len(already_synced)}\n"
        result_message += f"❌ Not matched: {len(not_matched)}\n"
        
        if dry_run:
            result_message += f"\n🔍 **DRY RUN MODE** - No changes were made\n"
        else:
            result_message += f"\n✏️ Updated: {len(updates_made)} clients\n"
        
        if matched:
            result_message += f"\n**Newly Matched:**\n"
            for m in matched[:10]:  # Show first 10
                result_message += f"- {m['name']} → QB ID {m['qbo_id']} ({m['match_method']})\n"
            if len(matched) > 10:
                result_message += f"... and {len(matched) - 10} more\n"
        
        if not_matched:
            result_message += f"\n**Not Found in QuickBooks:**\n"
            for nm in not_matched[:5]:  # Show first 5
                result_message += f"- {nm['name']}\n"
            if len(not_matched) > 5:
                result_message += f"... and {len(not_matched) - 5} more\n"
        
        logger.info(f"QB Sync: Matched {len(matched)}, Already synced {len(already_synced)}, "
                   f"Not matched {len(not_matched)}, Updated {len(updates_made)}")
        
        return {
            "status": "success",
            "details": result_message,
            "action_taken": f"Synced {len(matched)} clients with QuickBooks" + (" (dry run)" if dry_run else ""),
            "data_updated": len(updates_made) > 0,
            "sync_stats": {
                "matched": len(matched),
                "already_synced": len(already_synced),
                "not_matched": len(not_matched),
                "updated": len(updates_made)
            }
        }
        
    except Exception as e:
        logger.error(f"Error syncing QuickBooks clients: {e}")
        return {
            "status": "failed",
            "error": f"Sync failed: {str(e)}"
        }


# Handler registry - maps function names to handler functions
FUNCTION_HANDLERS = {
    "update_project_status": handle_update_project_status,
    "update_permit_status": handle_update_permit_status,
    "update_client_data": handle_update_client_data,
    "create_quickbooks_invoice": handle_create_quickbooks_invoice,
    "update_quickbooks_invoice": handle_update_quickbooks_invoice,
    "add_column_to_sheet": handle_add_column_to_sheet,
    "update_client_field": handle_update_client_field,
    "sync_quickbooks_clients": handle_sync_quickbooks_clients,
}
