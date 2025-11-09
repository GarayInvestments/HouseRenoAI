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
            current_qbo_id = client.get('QBO Client ID')  # Column name has SPACE not underscore
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
                        updates={'QBO Client ID': qb_id}  # Column name has SPACE not underscore
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


async def handle_create_quickbooks_customer_from_sheet(
    args: Dict[str, Any],
    google_service,
    quickbooks_service,
    memory_manager,
    session_id: str
) -> Dict[str, Any]:
    """
    Create a new QuickBooks customer based on a client in Google Sheets.
    
    Looks up client by name or ID in Sheets, then creates matching customer in QB.
    Automatically sets CustomerTypeRef to 'GC Compliance'.
    
    Args:
        args: Function arguments containing client_name or client_id
        google_service: Google Sheets service instance
        quickbooks_service: QuickBooks service instance
        memory_manager: Session memory manager
        session_id: Current session ID
        
    Returns:
        Dictionary with created customer details
    """
    try:
        client_identifier = args.get("client_name") or args.get("client_id")
        if not client_identifier:
            return {
                "status": "failed",
                "error": "Must provide client_name or client_id"
            }
        
        logger.info(f"[CREATE QB CUSTOMER] Looking up client: {client_identifier}")
        
        # Check QB authentication
        if not quickbooks_service or not quickbooks_service.is_authenticated():
            return {
                "status": "failed",
                "error": "QuickBooks is not authenticated. Please connect to QuickBooks first."
            }
        
        # Get all clients from Sheets
        clients_data = await google_service.get_clients_data()
        
        # Find matching client
        target_client = None
        for client in clients_data:
            client_name = (client.get('Full Name') or client.get('Client Name', '')).strip()
            client_id = str(client.get('Client ID', '')).strip()
            
            if (client_name.lower() == client_identifier.lower() or 
                client_id == client_identifier):
                target_client = client
                break
        
        if not target_client:
            return {
                "status": "failed",
                "error": f"Client '{client_identifier}' not found in Google Sheets"
            }
        
        # Extract client data with comprehensive field mapping
        client_name = (target_client.get('Full Name') or target_client.get('Client Name', '')).strip()
        client_email = target_client.get('Email', '').strip()
        client_phone = target_client.get('Phone', '').strip()
        client_address = target_client.get('Address', '').strip()
        client_city = target_client.get('City', '').strip()
        client_state = target_client.get('State', '').strip()
        client_zip = target_client.get('Zip', '').strip()
        
        # Extract additional fields (Company Name, Role, Status, etc.)
        client_company = target_client.get('Company Name', '').strip()
        client_role = target_client.get('Role', '').strip()
        client_status = target_client.get('Status', '').strip()
        client_id = target_client.get('Client ID', '').strip()
        
        if not client_name:
            return {
                "status": "failed",
                "error": "Client has no name in Google Sheets"
            }
        
        logger.info(f"[CREATE QB CUSTOMER] Found client: {client_name}")
        logger.info(f"[CREATE QB CUSTOMER] Client details - Email: {client_email}, Phone: {client_phone}, Company: {client_company}, Role: {client_role}")
        
        # Check if customer already exists in QB
        qb_customers = await quickbooks_service.get_customers()
        for customer in qb_customers:
            qb_name = customer.get('DisplayName', '').strip().lower()
            if qb_name == client_name.lower():
                return {
                    "status": "failed",
                    "error": f"Customer '{client_name}' already exists in QuickBooks (ID: {customer.get('Id')})",
                    "existing_customer": {
                        "id": customer.get('Id'),
                        "name": customer.get('DisplayName'),
                        "email": customer.get('PrimaryEmailAddr', {}).get('Address', 'N/A')
                    }
                }
        
        # Build customer data for QuickBooks
        customer_data = {
            "DisplayName": client_name,
            "CustomerTypeRef": {
                "name": "GC Compliance"
            }
        }
        
        # Add email if available
        if client_email:
            customer_data["PrimaryEmailAddr"] = {
                "Address": client_email
            }
        
        # Add phone if available
        if client_phone:
            customer_data["PrimaryPhone"] = {
                "FreeFormNumber": client_phone
            }
        
        # Add address if available
        if client_address or client_city or client_state or client_zip:
            bill_addr = {}
            if client_address:
                bill_addr["Line1"] = client_address
            if client_city:
                bill_addr["City"] = client_city
            if client_state:
                bill_addr["CountrySubDivisionCode"] = client_state
            if client_zip:
                bill_addr["PostalCode"] = client_zip
            
            if bill_addr:
                customer_data["BillAddr"] = bill_addr
        
        # Create customer in QuickBooks
        logger.info(f"[CREATE QB CUSTOMER] Creating QB customer: {client_name}")
        created_customer = await quickbooks_service.create_customer(customer_data)
        
        qb_customer_id = created_customer.get('Id')
        qb_display_name = created_customer.get('DisplayName')
        
        logger.info(f"[CREATE QB CUSTOMER] Created customer ID {qb_customer_id}: {qb_display_name}")
        
        # Update Google Sheets with QBO Client ID
        sheet_client_id = target_client.get('Client ID', '')
        if sheet_client_id:
            try:
                await google_service.update_record_by_id(
                    sheet_name='Clients',
                    id_field='Client ID',
                    record_id=sheet_client_id,
                    updates={'QBO Client ID': qb_customer_id}
                )
                logger.info(f"[CREATE QB CUSTOMER] Updated Sheet client {sheet_client_id} with QBO ID {qb_customer_id}")
            except Exception as e:
                logger.warning(f"[CREATE QB CUSTOMER] Could not update Sheet with QBO ID: {e}")
        
        # Store in session memory
        memory_manager.set(session_id, "last_created_customer", {
            "qb_id": qb_customer_id,
            "name": qb_display_name,
            "email": client_email
        })
        
        result = {
            "status": "success",
            "message": f"Created QuickBooks customer: {qb_display_name}",
            "customer": {
                "qb_id": qb_customer_id,
                "display_name": qb_display_name,
                "email": client_email or "N/A",
                "phone": client_phone or "N/A",
                "company": client_company or "N/A",
                "role": client_role or "N/A",
                "status": client_status or "N/A",
                "address": client_address or "N/A",
                "city": client_city or "N/A",
                "state": client_state or "N/A",
                "zip": client_zip or "N/A",
                "type": "GC Compliance"
            },
            "sheet_updated": bool(sheet_client_id)
        }
        
        logger.info(f"[CREATE QB CUSTOMER] Success: {result['message']}")
        return result
        
    except Exception as e:
        logger.error(f"[CREATE QB CUSTOMER] Error: {e}", exc_info=True)
        return {
            "status": "failed",
            "error": f"Failed to create customer: {str(e)}"
        }


async def handle_sync_gc_compliance_payments(
    args: Dict[str, Any],
    google_service,
    memory_manager,
    session_id: str
) -> Dict[str, Any]:
    """
    Reconcile GC Compliance payments with invoices.
    
    Process:
    1. Get all payments where Client Type == "GC Compliance"
    2. Get all invoices
    3. Match payments to invoices by Invoice ID or Client Name
    4. Update invoice: Amount Paid, Balance, Status
    5. Mark payment as synced with timestamp
    
    Args:
        args: Function arguments (dry_run optional)
        google_service: Google Sheets service instance
        memory_manager: Session memory manager
        session_id: Current session ID
        
    Returns:
        Dictionary with sync results
    """
    try:
        dry_run = args.get("dry_run", False)
        logger.info(f"[GC PAYMENTS SYNC] Starting sync (dry_run={dry_run})")
        
        # Get all sheet data
        all_data = await google_service.get_all_sheet_data()
        
        # Extract relevant tabs
        payments = all_data.get('Payments', [])
        invoices = all_data.get('Invoices', [])
        clients = all_data.get('Clients', [])
        
        logger.info(f"[GC PAYMENTS SYNC] Found {len(payments)} payments, {len(invoices)} invoices")
        
        # Build client type lookup
        client_type_map = {}
        for client in clients:
            client_name = client.get('Full Name') or client.get('Client Name', '')
            client_type = client.get('Client Type', '')
            if client_name:
                client_type_map[client_name.strip().lower()] = client_type
        
        # Filter GC Compliance payments that haven't been synced
        gc_payments = []
        for payment in payments:
            client_name = payment.get('Client Name', '').strip()
            client_type = client_type_map.get(client_name.lower(), '')
            is_synced = str(payment.get('Is Synced', '')).strip().upper()
            
            if client_type == 'GC Compliance' and is_synced != 'TRUE':
                gc_payments.append(payment)
        
        logger.info(f"[GC PAYMENTS SYNC] Found {len(gc_payments)} unsynced GC Compliance payments")
        
        if not gc_payments:
            return {
                "status": "success",
                "message": "No unsynced GC Compliance payments to process",
                "processed": 0,
                "matched": 0,
                "unmatched": 0
            }
        
        # Build invoice lookup by Invoice ID and Client Name
        invoice_map = {}
        for invoice in invoices:
            invoice_id = str(invoice.get('Invoice ID', '')).strip()
            client_name = invoice.get('Client Name', '').strip().lower()
            
            if invoice_id:
                invoice_map[f"id:{invoice_id}"] = invoice
            if client_name:
                if f"name:{client_name}" not in invoice_map:
                    invoice_map[f"name:{client_name}"] = []
                invoice_map[f"name:{client_name}"].append(invoice)
        
        # Process each payment
        matched_payments = []
        unmatched_payments = []
        invoice_updates = {}  # Track updates per invoice
        payment_updates = []  # Track payment rows to mark as synced
        
        for payment in gc_payments:
            payment_id = payment.get('Payment ID', '')
            invoice_id = str(payment.get('Invoice ID', '')).strip()
            client_name = payment.get('Client Name', '').strip()
            amount = payment.get('Amount', 0)
            payment_date = payment.get('Payment Date', '')
            
            # Try to parse amount
            try:
                if isinstance(amount, str):
                    amount = float(amount.replace('$', '').replace(',', '').strip())
                else:
                    amount = float(amount)
            except (ValueError, TypeError):
                logger.warning(f"[GC PAYMENTS SYNC] Invalid amount for payment {payment_id}: {amount}")
                amount = 0
            
            matched_invoice = None
            match_method = None
            
            # Match by Invoice ID first
            if invoice_id:
                matched_invoice = invoice_map.get(f"id:{invoice_id}")
                if matched_invoice:
                    match_method = "Invoice ID"
            
            # Fallback to Client Name
            if not matched_invoice and client_name:
                client_invoices = invoice_map.get(f"name:{client_name.lower()}", [])
                if client_invoices:
                    # Find the first unpaid or partially paid invoice
                    for inv in client_invoices:
                        balance = inv.get('Balance', 0)
                        try:
                            if isinstance(balance, str):
                                balance = float(balance.replace('$', '').replace(',', '').strip())
                            else:
                                balance = float(balance)
                        except (ValueError, TypeError):
                            balance = 0
                        
                        if balance > 0:
                            matched_invoice = inv
                            match_method = "Client Name"
                            break
            
            if matched_invoice:
                matched_payments.append({
                    "payment_id": payment_id,
                    "invoice_id": matched_invoice.get('Invoice ID', ''),
                    "client_name": client_name,
                    "amount": amount,
                    "payment_date": payment_date,
                    "match_method": match_method
                })
                
                # Track invoice update
                inv_id = matched_invoice.get('Invoice ID', '')
                if inv_id not in invoice_updates:
                    invoice_updates[inv_id] = {
                        "invoice": matched_invoice,
                        "payments_applied": 0,
                        "total_paid": 0
                    }
                
                invoice_updates[inv_id]["payments_applied"] += 1
                invoice_updates[inv_id]["total_paid"] += amount
                
                # Track payment to mark as synced
                payment_updates.append({
                    "payment_id": payment_id,
                    "payment_date": payment_date
                })
            else:
                unmatched_payments.append({
                    "payment_id": payment_id,
                    "client_name": client_name,
                    "amount": amount,
                    "invoice_id": invoice_id or "N/A"
                })
        
        logger.info(f"[GC PAYMENTS SYNC] Matched: {len(matched_payments)}, Unmatched: {len(unmatched_payments)}")
        
        # Apply updates if not dry run
        invoices_updated = 0
        payments_marked = 0
        
        if not dry_run:
            # Update invoices
            for inv_id, update_info in invoice_updates.items():
                invoice = update_info["invoice"]
                total_paid_from_payments = update_info["total_paid"]
                
                # Get current values
                current_paid = invoice.get('Amount Paid', 0)
                try:
                    if isinstance(current_paid, str):
                        current_paid = float(current_paid.replace('$', '').replace(',', '').strip())
                    else:
                        current_paid = float(current_paid)
                except (ValueError, TypeError):
                    current_paid = 0
                
                total_amount = invoice.get('Total Amount', 0)
                try:
                    if isinstance(total_amount, str):
                        total_amount = float(total_amount.replace('$', '').replace(',', '').strip())
                    else:
                        total_amount = float(total_amount)
                except (ValueError, TypeError):
                    total_amount = 0
                
                # Calculate new values
                new_paid = current_paid + total_paid_from_payments
                new_balance = total_amount - new_paid
                
                # Determine status
                if new_balance <= 0:
                    new_status = "Paid"
                elif new_paid > 0:
                    new_status = "Partially Paid"
                else:
                    new_status = invoice.get('Status', 'Unpaid')
                
                # Update invoice
                success = await google_service.update_record_by_id(
                    sheet_name='Invoices',
                    id_field='Invoice ID',
                    record_id=inv_id,
                    updates={
                        'Amount Paid': new_paid,
                        'Balance': new_balance,
                        'Status': new_status
                    }
                )
                
                if success:
                    invoices_updated += 1
                    logger.info(f"[GC PAYMENTS SYNC] Updated Invoice {inv_id}: Paid=${new_paid:.2f}, Balance=${new_balance:.2f}, Status={new_status}")
            
            # Mark payments as synced
            current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            for payment_update in payment_updates:
                success = await google_service.update_record_by_id(
                    sheet_name='Payments',
                    id_field='Payment ID',
                    record_id=payment_update["payment_id"],
                    updates={
                        'Is Synced': 'TRUE',
                        'Synced At': current_timestamp
                    }
                )
                
                if success:
                    payments_marked += 1
        
        # Store in session memory
        memory_manager.set(session_id, "last_gc_payment_sync", {
            "matched": len(matched_payments),
            "unmatched": len(unmatched_payments),
            "invoices_updated": invoices_updated,
            "payments_marked": payments_marked
        })
        
        result = {
            "status": "success",
            "dry_run": dry_run,
            "processed": len(gc_payments),
            "matched": len(matched_payments),
            "unmatched": len(unmatched_payments),
            "invoices_updated": invoices_updated,
            "payments_marked": payments_marked,
            "matched_details": matched_payments[:10],  # First 10 for brevity
            "unmatched_details": unmatched_payments
        }
        
        if dry_run:
            result["message"] = "Dry run complete - no changes made"
        else:
            result["message"] = f"Synced {payments_marked} payments to {invoices_updated} invoices"
        
        logger.info(f"[GC PAYMENTS SYNC] Complete: {result['message']}")
        return result
        
    except Exception as e:
        logger.error(f"[GC PAYMENTS SYNC] Error: {e}", exc_info=True)
        return {
            "status": "failed",
            "error": f"Sync failed: {str(e)}"
        }


async def handle_sync_quickbooks_customer_types(
    args: Dict[str, Any],
    google_service,
    quickbooks_service,
    memory_manager,
    session_id: str
) -> Dict[str, Any]:
    """
    Sync CustomerTypeRef to 'GC Compliance' for all Sheet clients in QuickBooks.
    
    Process:
    1. Get all clients from Google Sheets
    2. Match with QuickBooks customers by name/email
    3. Update CustomerTypeRef = {"name": "GC Compliance"}
    4. Skip customers already set correctly
    
    Args:
        args: Function arguments (dry_run optional)
        google_service: Google Sheets service instance
        quickbooks_service: QuickBooks service instance
        memory_manager: Session memory manager
        session_id: Current session ID
        
    Returns:
        Dictionary with sync results
    """
    try:
        dry_run = args.get("dry_run", False)
        logger.info(f"[QB TYPE SYNC] AI function called (dry_run={dry_run})")
        
        # Execute sync via QuickBooks service
        result = await quickbooks_service.sync_gc_customer_types_from_sheets(
            google_service=google_service,
            dry_run=dry_run
        )
        
        # Store in session memory
        if result.get("status") == "success":
            memory_manager.set(session_id, "last_qb_type_sync", {
                "matched": result.get("matched", 0),
                "updated": result.get("updated", 0),
                "skipped": result.get("skipped_already_set", 0),
                "not_found": result.get("not_found_in_qb", 0)
            })
        
        return result
        
    except Exception as e:
        logger.error(f"[QB TYPE SYNC] Error: {e}", exc_info=True)
        return {
            "status": "failed",
            "error": f"Customer type sync failed: {str(e)}"
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
    "create_quickbooks_customer_from_sheet": handle_create_quickbooks_customer_from_sheet,
    "sync_gc_compliance_payments": handle_sync_gc_compliance_payments,
    "sync_quickbooks_customer_types": handle_sync_quickbooks_customer_types,
}
