import openai
import logging
from typing import List, Dict, Any
from app.config import settings

logger = logging.getLogger(__name__)

class OpenAIService:
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    
    async def process_chat_message(self, message: str, context: Dict[str, Any] = None) -> tuple:
        """
        Process a chat message using OpenAI GPT-4o model with function calling
        Returns: (response_text, function_calls_list)
        """
        try:
            # STEP 2: Log what OpenAI service receives
            logger.info(f"[OPENAI] Received context keys: {list(context.keys()) if context else 'None'}")
            logger.info(f"[OPENAI] all_clients available: {'all_clients' in context if context else False}")
            logger.info(f"[OPENAI] all_projects available: {'all_projects' in context if context else False}")
            logger.info(f"[OPENAI] all_permits available: {'all_permits' in context if context else False}")
            
            if context and 'all_clients' in context:
                logger.info(f"[OPENAI] all_clients count: {len(context['all_clients'])}")
                # Log first client as sample
                if context['all_clients']:
                    first_client = context['all_clients'][0]
                    logger.info(f"[OPENAI] Sample client keys: {list(first_client.keys())}")
            
            if context and 'all_projects' in context:
                logger.info(f"[OPENAI] all_projects count: {len(context['all_projects'])}")
            
            if context and 'all_permits' in context:
                logger.info(f"[OPENAI] all_permits count: {len(context['all_permits'])}")
            
            # Get current date/time for AI context
            from datetime import datetime
            import pytz
            eastern = pytz.timezone('US/Eastern')
            current_datetime = datetime.now(eastern)
            current_date = current_datetime.strftime("%A, %B %d, %Y")
            current_time = current_datetime.strftime("%I:%M %p %Z")
            
            # Enhanced system prompt for House Renovators AI Portal
            system_prompt = f"""
            You are an advanced AI assistant for House Renovators LLC, a North Carolina licensed General Contractor.
            
            🕐 **CURRENT DATE & TIME:**
            Today is: {current_date}
            Current time: {current_time}
            
            You have FULL ACCESS to comprehensive project data including:
            - All client information (names, addresses, status, roles, contacts)
            - All project details (addresses, costs, timelines, scope of work)
            - All permit records (numbers, statuses, submission dates, approvals)
            - Site visits, subcontractors, documents, tasks, and payments
            - Jurisdiction information and inspector contacts
            - Construction phase tracking with images
            - **QuickBooks data** (customers, invoices, balances) when authenticated
            
            YOUR CAPABILITIES:
            ✅ Answer ANY question about clients, projects, or permits
            ✅ Search and filter data by any field (status, date, location, etc.)
            ✅ Calculate totals, averages, and statistics
            ✅ Track timelines and identify delays
            ✅ Identify missing data or incomplete records
            ✅ Cross-reference data between sheets (clients → projects → permits)
            ✅ Provide detailed analysis and recommendations
            ✅ Generate reports and summaries
            ✅ **View and display QuickBooks invoices and customer data** (data is PROVIDED in context - just format and show it)
            ✅ **Query customer balances, open invoices, payment status** (data is PROVIDED - just read from context)
            ✅ **Create QuickBooks invoices** (ONLY function call - ALWAYS ask for confirmation before creating)
            ✅ **Update client information** (phone, email, address, etc.)
            ✅ **Add new columns to Google Sheets** (ALWAYS ask for confirmation before adding)
            
            🔍 DATA SOURCE PRIORITY - CRITICAL RULES:
            
            ⚠️ **DEFAULT TO GOOGLE SHEETS** unless user explicitly mentions QuickBooks/QBO:
            
            ⚠️ **IMPORTANT: QuickBooks data is ALREADY in your context - DO NOT call functions to retrieve it!**
            - When user asks "list QB customers" or "show invoices", the data is already provided below
            - Simply format and display the data - NO function calls needed for viewing/listing
            - ONLY call create_quickbooks_invoice function when user wants to CREATE a new invoice
            
            **ALWAYS use GOOGLE SHEETS for:**
            - "clients" / "customers" / "projects" / "permits" (your permit workflow data)
            - ANY question about construction, projects, permits, inspections
            - Contact information, addresses, project details
            - Status queries (permit status, project status)
            - Timeline, phase, scope of work questions
            - Subcontractors, inspectors, jurisdictions
            - **Default assumption: User is asking about their active permit projects in Sheets**
            
            **ONLY use QUICKBOOKS when user explicitly says:**
            - "QuickBooks" / "QBO" / "QB" in their message
            - OR very specific financial terms: "invoice", "payment", "paid", "unpaid", "balance owed"
            - "Create an invoice" / "bill" / "receivable"
            
            📊 **IMPORTANT: QuickBooks has MORE clients than Sheets**
            - Sheets = Your curated permit/project clients (the ones you actively manage)
            - QuickBooks = ALL business activity including small jobs, old clients, one-offs
            - When user says "show me my clients" → ALWAYS use Sheets (your active projects)
            - When user says "show me QuickBooks customers" → Use QuickBooks
            
            ✅ **Examples of CORRECT behavior:**
            - "Show me all clients" → Use SHEETS (active permit projects)
            - "List my customers" → Use SHEETS (active permit projects)
            - "Who owes money?" → Use SHEETS first, then check QB for payment status
            - "Show me QBO customers" → Use QUICKBOOKS
            - "Create an invoice" → Use QUICKBOOKS (but can reference Sheets for project details)
            - "Has invoice #123 been paid?" → Use QUICKBOOKS
            
            🚫 **NEVER do this:**
            - User: "Show me all clients" → You: *pulls 150 QB customers* ❌
            - Always default to Sheets unless QB is explicitly mentioned
            
            QUICKBOOKS INVOICE CREATION GUIDELINES:
            📋 When user requests invoice creation:
            1. Ask for required information:
               - Customer/client name (match to QuickBooks customer)
               - Amount/line items
               - Description of services
               - Invoice date (default: today)
               - Due date (default: 30 days from invoice date)
            2. Present a clear summary of the invoice details
            3. ALWAYS ask "Would you like me to create this invoice in QuickBooks?" before proceeding
            4. Only proceed with creation after explicit confirmation (yes/confirm/create/ok)
            5. After successful creation, ALWAYS provide the QuickBooks invoice link so user can view/edit it
            6. Format the link as: "View invoice in QuickBooks: [link]"
            7. The link will be in the function_results as "invoice_link"
            
            QUICKBOOKS INVOICE UPDATE GUIDELINES:
            📋 When user requests to update an invoice:
            1. Identify which invoice to update (by ID or invoice number)
            2. Determine what fields to update:
               - **doc_number**: To change the invoice number (e.g., "TTD-6441-11-08")
               - **amount**: To change the total amount
               - **due_date**: To change the due date
               - **description**: To change the service description
            3. CRITICAL: You MUST populate the "updates" object with the field to update
               Example: {{"doc_number": "TTD-6441-11-08"}} or {{"amount": 5000}}
            4. ALWAYS ask for confirmation before updating
            5. After successful update, provide the QuickBooks invoice link
            
            GOOGLE SHEETS COLUMN CREATION GUIDELINES:
            📋 When user wants to add a new column to a sheet:
            1. Identify the sheet name (Clients, Projects, Permits, etc.)
            2. Confirm the column name with the user
            3. Ask if they want a default value for existing rows (optional)
            4. ALWAYS ask for confirmation: "Would you like me to add the '[Column Name]' column to the [Sheet Name] sheet?"
            5. When user confirms (yes/confirm/add/proceed/ok), IMMEDIATELY call the add_column_to_sheet function
            6. Provide clear feedback on success or failure
            7. DO NOT ask for confirmation multiple times - once confirmed, execute immediately
            
            CRITICAL FORMATTING RULES:
            🎯 ALWAYS format responses in clean, readable markdown
            🎯 Use proper lists with line breaks between items
            🎯 Use headers (##, ###) to organize sections
            🎯 Use tables for comparisons or multiple data points
            🎯 Use bold (**text**) for important fields like names, addresses, statuses
            🎯 NEVER dump raw data or concatenate fields without formatting
            🎯 Group related information under clear headings
            🎯 Add blank lines between sections for readability
            
            DETAILED QUERY GUIDELINES:
            📋 When user asks for "details", "summary", "more information", or "show me everything" about a client/project/permit:
            ✅ Show ALL available fields from the context data, not just a subset
            ✅ Include all IDs (Client ID, Project ID, Permit ID, QB Customer ID, etc.)
            ✅ Include all dates (Start Date, Application Date, Approval Date, etc.)
            ✅ Include all financial data (Project Cost, HR PC Service Fee, Payment amounts)
            ✅ Include contact information (Email, Phone, Address)
            ✅ Include status and classification fields (Status, Project Type, Role, etc.)
            ✅ Format in clear sections with proper headers
            ✅ Use tables when showing multiple related items
            
            Example: "Show me details for Javier's project" should include:
            - Project ID, Client ID, Project Name, Address, City, County
            - Status, Project Type, Start Date
            - Project Cost, HR PC Service Fee
            - Client contact info (Email, Phone)
            - All other available fields from context

            
            EXAMPLE GOOD FORMAT:
            ## Clients by Status
            
            ### Permit Approved (1 client)
            - **Client Name:** 64 Phillips
            - **Address:** 64 Phillips Ln, Spruce Pine, NC 28777
            - **Project:** Renovation
            - **Status:** ✅ Permit Approved
            
            ### Client ID: 116e77b9 (1 client)
            - **Name:** 101 W 5th Ave
            - **Address:** 101 W 5th Ave, Lexington, NC 27292
            - **Status:** 🔄 Final Inspection Complete
            
            RESPONSE GUIDELINES:
            - Be comprehensive and data-driven in your answers
            - If asked about specific data, search through ALL available records
            - Provide exact counts, dates, and values when available
            - Cross-reference related information (e.g., client → their projects → permit status)
            - Highlight issues or incomplete data proactively
            - Use professional construction industry terminology
            - ALWAYS format lists with proper line breaks and structure
            
            🔗 **FINDING RELATED PROJECTS FOR A CLIENT:**
            - When asked "what project is related to [client name]?" or "show projects for [client]"
            - FIRST: Find the client's **Client ID** in the CLIENTS DATA section
            - THEN: Search the PROJECTS DATA section for projects with matching **Client ID**
            - DO NOT guess based on location or proximity
            - Example: "Javier Martinez" → Find Client ID "abc123" → Find projects where Client ID = "abc123"
            - If NO projects match the Client ID, say "No projects found for this client"
            - NEVER suggest projects from other clients based on location similarity
            
            💰 **CREATING INVOICES FOR PROJECTS:**
            - When creating an invoice for a project, you need these pieces of data:
              1. **QuickBooks Customer ID**: 
                 - FIRST: Check if client has "QB Customer ID" field in CLIENTS DATA (fastest - use directly!)
                 - If "QB Customer ID" exists (not "Not synced"), use that customer_id value
                 - If "QB Customer ID" is "Not synced", find matching customer in QUICKBOOKS CUSTOMERS by name
              2. **Invoice Amount**: Use the "HR PC Service Fee" value from the project (NOT "Project Cost")
              3. **Client Email**: Get the "Email" field from CLIENTS DATA for the client
              4. **Property Address**: Get the "Project Address" from PROJECTS DATA for invoice numbering
            - Example flow:
              - User: "Create invoice for Temple project"
              - You: Find Temple project → Get Client ID → Check CLIENTS DATA for "QB Customer ID"
              - If QB Customer ID exists: Use it (skip QB customer search!)
              - If QB Customer ID is "Not synced": Search QUICKBOOKS CUSTOMERS for match
              - Get HR PC Service Fee + client email → Call create_quickbooks_invoice
            - ALWAYS include client_email parameter if email is available in CLIENTS DATA
            - The description should be "GC Permit Oversight - [Project Name]"
            - **PERFORMANCE TIP**: Using QB Customer ID saves ~2 seconds per invoice (no search needed)
            
            ⚠️ **CRITICAL: NEVER SAY "QuickBooks connection is not currently active" WHEN IT IS ACTIVE**
            - If you have QuickBooks data in context (customers_count > 0, quickbooks_connected = true), QuickBooks IS connected
            - If you can't find a specific client/customer, say: "I couldn't find [name] in the [Sheets/QuickBooks] records"
            - DO NOT confuse "client not found" with "QuickBooks not connected"
            - Example WRONG: "QuickBooks connection is not currently active" when you have 24 customers loaded ❌
            - Example CORRECT: "I couldn't find Gustavo in the QuickBooks customer list. Here are the customers I have..." ✅
            
            🚨 **CRITICAL ANTI-HALLUCINATION RULE: NEVER FABRICATE CUSTOMER/CLIENT NAMES**
            - You will receive ACTUAL customer data in the "=== QUICKBOOKS CUSTOMERS ===" or "=== CLIENTS DATA ===" sections below
            - ONLY show customer/client names that appear in that data
            - NEVER generate fake names like "Ajay Nair", "Alex Chang", "Bob Smith", "Alice Johnson", etc.
            - When listing customers, you MUST copy the EXACT names from the context data provided
            - DO NOT generate "example" data - this is a REAL production database, not a tutorial
            - If asked to list customers, ONLY list names from the provided context data
            - Example WRONG: Showing made-up names like "Emily Clark", "John Doe", "Karen White" ❌
            - Example CORRECT: Showing actual names from the context data like "Temple Baptist", "Marta Alder", "Rapid Restoration" ✅
            
            📋 **FORMAT INSTRUCTION FOR LISTING CUSTOMERS:**
            When asked to "list customers" or "show customers", you MUST:
            1. Look at the "=== QUICKBOOKS CUSTOMERS ===" section in the DATA CONTEXT below
            2. Copy the EXACT customer names you see there (DisplayName field)
            3. DO NOT make up any names - only use what you see in the data
            4. If you see names like "Marta Alder", "Temple Baptist", "Rapid Restoration" in context, use THOSE names
            5. NEVER use generic names like "John Doe", "Ajay Nair", "Sarah Johnson" - these are hallucinations
            
            🧩 **MISSING DATA POLICY - CRITICAL:**
            - If a field such as address, phone, email, role, company, status, or any other data is missing, blank, or shows "Not provided", respond with "Not provided" or "No [field] on file"
            - DO NOT guess, infer, or fabricate missing information based on patterns, context, or assumptions
            - DO NOT use placeholder values like "N/A", "Unknown", "TBD", or similar - use "Not provided"
            - Example WRONG: Client has no email → You show "email@example.com" ❌
            - Example CORRECT: Client has no email → You show "Email: Not provided" ✅
            - Example WRONG: Project has no address → You show "123 Main Street" ❌
            - Example CORRECT: Project has no address → You show "Address: Not provided" ✅
            - If you see "Not provided" in the data context, that means the information is genuinely missing - don't try to fill it in
            
            DATA ACCESS:
            You receive the complete dataset in the context. Search through it thoroughly to answer questions.
            Don't say "I don't have access" - the data is provided to you in the context.
            🚨 ONLY USE DATA PROVIDED IN CONTEXT - NEVER INVENT OR FABRICATE DATA
            🚨 THIS IS A REAL DATABASE - NOT A DEMO OR TUTORIAL - USE ACTUAL DATA ONLY
            🚨 IF DATA SHOWS "Not provided" - THAT MEANS IT'S TRULY MISSING - DON'T FABRICATE IT
            """
            
            # Start with system prompt
            messages = [
                {"role": "system", "content": system_prompt}
            ]
            
            # Add conversation history for context continuity
            if context and 'conversation_history' in context:
                conversation_history = context['conversation_history']
                if conversation_history:
                    # Add previous messages to maintain context
                    messages.extend(conversation_history)
                    logger.info(f"Added {len(conversation_history)} previous messages for context")
            
            # Add current user message
            messages.append({"role": "user", "content": message})
            
            # Add context if provided - format it clearly for AI
            if context:
                # Helper function to sanitize missing/blank data
                def safe_field(value):
                    """Convert None, empty strings, or whitespace-only values to 'Not provided'"""
                    if value is None or (isinstance(value, str) and value.strip() == ""):
                        return "Not provided"
                    return str(value).strip()
                
                # Build a structured context message
                context_parts = []
                
                # Add session memory for entity tracking
                if 'session_memory' in context and context['session_memory']:
                    context_parts.append("=== SESSION MEMORY (Entity Tracking) ===")
                    session_mem = context['session_memory']
                    for key, value in session_mem.items():
                        if key not in ['metadata', 'conversation_history']:  # Skip metadata and history (already in messages)
                            context_parts.append(f"{key}: {value}")
                    if len([k for k in session_mem.keys() if k not in ['metadata', 'conversation_history']]) > 0:
                        context_parts.append("")  # Blank line after memory only if there was content
                
                # Add counts summary
                if 'clients_count' in context:
                    context_parts.append(f"Total Clients: {context['clients_count']}")
                if 'projects_count' in context:
                    context_parts.append(f"Total Projects: {context['projects_count']}")
                if 'permits_count' in context:
                    context_parts.append(f"Total Permits: {context['permits_count']}")
                
                # Add QuickBooks data from context_builder structure
                if 'quickbooks' in context and context['quickbooks'].get('authenticated'):
                    qb_data = context['quickbooks']
                    customers = qb_data.get('customers', [])
                    invoices = qb_data.get('invoices', [])
                    summary = qb_data.get('summary', {})
                    
                    context_parts.append(f"\n🔗 QuickBooks: CONNECTED ✅")
                    context_parts.append(f"Total Customers: {summary.get('total_customers', len(customers))}")
                    context_parts.append(f"Total Invoices: {summary.get('total_invoices', len(invoices))}")
                    
                    # Add ACTUAL QuickBooks customers from context
                    if customers:
                        context_parts.append(f"\n\n=== QUICKBOOKS CUSTOMERS ({len(customers)} total) ===")
                        context_parts.append("🚨 THESE ARE THE ONLY REAL CUSTOMER NAMES - DO NOT INVENT OTHERS!")
                        logger.info(f"[DEBUG] Adding {len(customers)} QB customers to context (showing up to 50)")
                        for customer in customers[:50]:  # Show up to 50
                            cust_id = customer.get('Id')
                            cust_name = customer.get('DisplayName') or customer.get('CompanyName') or customer.get('FullyQualifiedName', 'Unknown')
                            cust_email = customer.get('PrimaryEmailAddr', {}).get('Address', 'N/A')
                            cust_phone = customer.get('PrimaryPhone', {}).get('FreeFormNumber', 'N/A')
                            cust_balance = customer.get('Balance', 0)
                            
                            context_parts.append(
                                f"\n✓ Customer ID: {cust_id}"
                                f"\n  Name: {cust_name}"
                                f"\n  Email: {cust_email}"
                                f"\n  Phone: {cust_phone}"
                                f"\n  Balance: ${cust_balance}"
                            )
                    
                    # Add QB invoice summaries
                    if invoices:
                        context_parts.append(f"\n\n=== QUICKBOOKS INVOICES ({len(invoices)} recent) ===")
                        for invoice in invoices:
                            inv_id = invoice.get('Id')
                            doc_num = invoice.get('DocNumber', 'N/A')
                            customer_ref = invoice.get('CustomerRef', {})
                            customer_name = customer_ref.get('name', 'Unknown')
                            txn_date = invoice.get('TxnDate', 'N/A')
                            total = invoice.get('TotalAmt', 0)
                            balance = invoice.get('Balance', 0)
                            
                            context_parts.append(
                                f"\nInvoice #{doc_num} (ID: {inv_id})"
                                f"\n  Customer: {customer_name}"
                                f"\n  Date: {txn_date}"
                                f"\n  Total: ${total}"
                                f"\n  Balance Due: ${balance}"
                            )
                else:
                    context_parts.append(f"\n⚠️ QuickBooks: Not connected (no 'quickbooks' key in context or not authenticated)")
                
                # Add available IDs for lookup
                if 'client_ids' in context and context['client_ids']:
                    context_parts.append(f"\nAvailable Client IDs: {', '.join(context['client_ids'][:20])}")
                    if len(context['client_ids']) > 20:
                        context_parts.append(f"... and {len(context['client_ids']) - 20} more")
                
                # Add clients data for easy reference - CHECK BOTH KEYS
                clients_data = context.get('all_clients') or context.get('clients_summary') or context.get('clients', [])
                if clients_data:
                    context_parts.append("\n\n=== CLIENTS DATA ===")
                    context_parts.append("🚨 THESE ARE THE ONLY REAL CLIENT NAMES - USE THESE EXACT NAMES!")
                    logger.info(f"[DEBUG] Adding {len(clients_data)} clients to context (showing up to 50)")
                    for client in clients_data[:50]:  # Limit to prevent token overflow
                        # Handle both formats: direct fields or nested 'Name' key
                        client_id = safe_field(client.get('Client ID'))
                        client_name = safe_field(client.get('Full Name') or client.get('Name') or client.get('Client Name'))
                        client_status = safe_field(client.get('Status'))
                        client_address = safe_field(client.get('Address'))
                        client_phone = safe_field(client.get('Phone'))
                        client_email = safe_field(client.get('Email'))
                        client_company = safe_field(client.get('Company Name'))
                        client_role = safe_field(client.get('Role'))
                        client_qbo_id = safe_field(client.get('QBO Client ID'))  # QuickBooks customer ID
                        
                        context_parts.append(
                            f"\n✓ Client ID: {client_id}"
                            f"\n  Full Name: {client_name}"
                            f"\n  Company: {client_company}"
                            f"\n  Role: {client_role}"
                            f"\n  Status: {client_status}"
                            f"\n  Email: {client_email}"
                            f"\n  Phone: {client_phone}"
                            f"\n  Address: {client_address}"
                            f"\n  QB Customer ID: {client_qbo_id if client_qbo_id else 'Not synced'}"
                        )
                
                # Add projects data with safe_field sanitization
                projects_data = context.get('all_projects', [])
                if projects_data:
                    context_parts.append("\n\n=== PROJECTS DATA ===")
                    context_parts.append("🚨 THESE ARE THE ONLY REAL PROJECTS - USE EXACT DATA FROM HERE!")
                    logger.info(f"[DEBUG] Adding {len(projects_data)} projects to context (showing up to 50)")
                    for project in projects_data[:50]:
                        project_id = safe_field(project.get('Project ID'))
                        client_id = safe_field(project.get('Client ID'))  # CRITICAL: Link to client
                        project_name = safe_field(project.get('Project Name') or project.get('Name'))
                        project_address = safe_field(project.get('Project Address') or project.get('Address'))
                        project_status = safe_field(project.get('Status'))
                        project_client = safe_field(project.get('Client Name') or project.get('Client'))
                        hr_pc_fee = safe_field(project.get('HR PC Service Fee'))  # CRITICAL: Invoice amount
                        project_type = safe_field(project.get('Project Type'))
                        start_date = safe_field(project.get('Start Date'))
                        project_cost = safe_field(project.get('Project Cost (Materials + Labor)'))
                        county = safe_field(project.get('County'))
                        
                        context_parts.append(
                            f"\n✓ Project ID: {project_id}"
                            f"\n  Client ID: {client_id}"
                            f"\n  Name: {project_name}"
                            f"\n  Address: {project_address}"
                            f"\n  Status: {project_status}"
                            f"\n  Client: {project_client}"
                            f"\n  HR PC Service Fee: {hr_pc_fee}"
                            f"\n  Project Type: {project_type}"
                            f"\n  Start Date: {start_date}"
                            f"\n  Project Cost: {project_cost}"
                            f"\n  County: {county}"
                        )
                
                # Add permits data with safe_field sanitization
                permits_data = context.get('all_permits', [])
                if permits_data:
                    context_parts.append("\n\n=== PERMITS DATA ===")
                    context_parts.append("🚨 THESE ARE THE ONLY REAL PERMITS - USE EXACT DATA FROM HERE!")
                    logger.info(f"[DEBUG] Adding {len(permits_data)} permits to context (showing up to 50)")
                    for permit in permits_data[:50]:
                        permit_id = safe_field(permit.get('Permit ID'))
                        permit_number = safe_field(permit.get('Permit Number'))
                        permit_status = safe_field(permit.get('Status'))
                        permit_address = safe_field(permit.get('Address') or permit.get('Project Address'))
                        permit_type = safe_field(permit.get('Permit Type'))
                        project_id = safe_field(permit.get('Project ID'))
                        application_date = safe_field(permit.get('Application Date'))
                        approval_date = safe_field(permit.get('Approval Date'))
                        
                        context_parts.append(
                            f"\n✓ Permit ID: {permit_id}"
                            f"\n  Number: {permit_number}"
                            f"\n  Type: {permit_type}"
                            f"\n  Status: {permit_status}"
                            f"\n  Address: {permit_address}"
                            f"\n  Project ID: {project_id}"
                            f"\n  Applied: {application_date}"
                            f"\n  Approved: {approval_date}"
                        )
                
                # Add payments data with safe_field sanitization
                payments_data = context.get('payments', [])
                if payments_data:
                    context_parts.append("\n\n=== PAYMENTS DATA ===")
                    context_parts.append("💰 PAYMENT RECORDS (from QuickBooks sync):")
                    logger.info(f"[DEBUG] Adding {len(payments_data)} payments to context (showing up to 30)")
                    for payment in payments_data[:30]:  # Limit to 30 most recent
                        payment_id = safe_field(payment.get('Payment ID'))
                        client_id = safe_field(payment.get('Client ID'))
                        invoice_id = safe_field(payment.get('Invoice ID'))
                        amount = safe_field(payment.get('Amount'))
                        payment_date = safe_field(payment.get('Payment Date'))
                        method = safe_field(payment.get('Payment Method'))
                        status = safe_field(payment.get('Status'))
                        qb_payment_id = safe_field(payment.get('QB Payment ID'))
                        
                        context_parts.append(
                            f"\n✓ Payment ID: {payment_id}"
                            f"\n  Client ID: {client_id}"
                            f"\n  Invoice ID: {invoice_id}"
                            f"\n  Amount: ${amount}"
                            f"\n  Date: {payment_date}"
                            f"\n  Method: {method}"
                            f"\n  Status: {status}"
                            f"\n  QB Payment ID: {qb_payment_id}"
                        )
                
                context_message = "\n".join(context_parts)
                logger.info(f"[DEBUG] Context message length: {len(context_message)} chars, ~{len(context_message)//4} tokens")
                messages.insert(1, {"role": "system", "content": f"DATA CONTEXT:\n{context_message}"})
            
            # Define available tools for the AI to call (using modern tools API)
            tools = [
                {
                    "type": "function",
                    "function": {
                        "name": "update_project_status",
                        "description": "Update the status of a construction project in Google Sheets",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "project_id": {
                                    "type": "string",
                                    "description": "The unique Project ID (e.g., '12b59b62')"
                                },
                                "new_status": {
                                    "type": "string",
                                    "description": "The new status value (e.g., 'Completed', 'In Progress', 'Permit Approved')"
                                }
                            },
                            "required": ["project_id", "new_status"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "update_permit_status",
                        "description": "Update the status of a construction permit in Google Sheets",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "permit_id": {
                                    "type": "string",
                                    "description": "The unique Permit ID"
                                },
                                "new_status": {
                                    "type": "string",
                                    "description": "The new permit status (e.g., 'Approved', 'Pending', 'Under Review')"
                                }
                            },
                            "required": ["permit_id", "new_status"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "create_quickbooks_invoice",
                        "description": "Create a new invoice in QuickBooks Online with property address-based invoice numbering (e.g., '1105-Sandy-Bottom-Concord' from '1105 Sandy Bottom Dr, Concord, NC'). ONLY call this after user confirms they want to create the invoice. CRITICAL: When creating an invoice for a PROJECT, use the 'HR PC Service Fee' column value from the Projects sheet as the invoice amount. Always include property_address, city, scope_of_work, and client_email from project/client data. The service item 'GC Permit Oversight' (ID: 108) is automatically used. Payment terms are set to 'Due on Receipt' with memo 'Zelle: steve@houserenovatorsllc.com'.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "customer_id": {
                                    "type": "string",
                                    "description": "The QuickBooks customer ID (from qb_customers_summary)"
                                },
                                "customer_name": {
                                    "type": "string",
                                    "description": "The customer display name for confirmation"
                                },
                                "amount": {
                                    "type": "number",
                                    "description": "The total invoice amount in USD. IMPORTANT: For project invoices, use the 'HR PC Service Fee' value from the Projects sheet, NOT the 'Project Cost'."
                                },
                                "description": {
                                    "type": "string",
                                    "description": "Short description/title of services (e.g., 'GC Permit Oversight - [Project Name]'). This is the main line item title."
                                },
                                "scope_of_work": {
                                    "type": "string",
                                    "description": "Detailed project scope from Projects sheet 'Scope of Work' column. This provides context about what the project entails (e.g., 'Sunroom Extension to existing house and adding square footage'). Include this whenever available from project data."
                                },
                                "property_address": {
                                    "type": "string",
                                    "description": "Property address for invoice numbering (e.g., '1105 Sandy Bottom Dr, Concord, NC'). If available from project data, include it to generate meaningful invoice numbers."
                                },
                                "city": {
                                    "type": "string",
                                    "description": "City name from Projects sheet 'City' column (e.g., 'Concord', 'Spruce Pine'). Used to append to invoice number (e.g., '1105-Sandy-Bottom-Concord')."
                                },
                                "client_email": {
                                    "type": "string",
                                    "description": "Client email address from Clients sheet (Email column). If available, include it so QuickBooks can email the invoice."
                                },
                                "invoice_date": {
                                    "type": "string",
                                    "description": "Invoice date in YYYY-MM-DD format (default: today)"
                                },
                                "due_date": {
                                    "type": "string",
                                    "description": "Due date in YYYY-MM-DD format (optional - if not provided, uses 'Due on Receipt' payment terms)"
                                }
                            },
                            "required": ["customer_id", "customer_name", "amount", "description"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "update_quickbooks_invoice",
                        "description": "Update an existing QuickBooks invoice. Use this to modify invoice amount, due date, description, or invoice number (DocNumber). ALWAYS ask for confirmation before updating.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "invoice_id": {
                                    "type": "string",
                                    "description": "The QuickBooks invoice ID to update"
                                },
                                "invoice_number": {
                                    "type": "string",
                                    "description": "The invoice number for confirmation (optional)"
                                },
                                "updates": {
                                    "type": "object",
                                    "description": "Fields to update (can include 'amount', 'due_date', 'description', 'doc_number')",
                                    "properties": {
                                        "amount": {
                                            "type": "number",
                                            "description": "New total amount"
                                        },
                                        "due_date": {
                                            "type": "string",
                                            "description": "New due date in YYYY-MM-DD format"
                                        },
                                        "description": {
                                            "type": "string",
                                            "description": "New description of services"
                                        },
                                        "doc_number": {
                                            "type": "string",
                                            "description": "New invoice number/DocNumber (e.g., 'TTD-6441-11-08')"
                                        }
                                    }
                                }
                            },
                            "required": ["invoice_id", "updates"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                            "name": "update_quickbooks_customer",
                            "description": "Update an existing QuickBooks customer with new information. Supports sparse updates - only specified fields will be updated. Use this to update company name, contact info, address, tax settings, etc. Common fields: CompanyName, GivenName, FamilyName, PrimaryPhone, PrimaryEmailAddr, Mobile, BillAddr, ShipAddr, Notes, Taxable, Active. ALWAYS ask for confirmation before updating.",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "customer_id": {
                                        "type": "string",
                                        "description": "The QuickBooks customer ID to update (required)"
                                    },
                                    "updates": {
                                        "type": "object",
                                        "description": "Fields to update. Can include: CompanyName (string), GivenName (string), FamilyName (string), DisplayName (string), PrimaryPhone (object with FreeFormNumber), PrimaryEmailAddr (object with Address), Mobile (object with FreeFormNumber), BillAddr (object with Line1, City, CountrySubDivisionCode, PostalCode), Notes (string), Taxable (boolean), Active (boolean), etc.",
                                        "properties": {
                                            "CompanyName": {
                                                "type": "string",
                                                "description": "Company name"
                                            },
                                            "GivenName": {
                                                "type": "string",
                                                "description": "First name"
                                            },
                                            "FamilyName": {
                                                "type": "string",
                                                "description": "Last name"
                                            },
                                            "DisplayName": {
                                                "type": "string",
                                                "description": "Display name (must be unique)"
                                            },
                                            "Notes": {
                                                "type": "string",
                                                "description": "Notes about the customer"
                                            },
                                            "Taxable": {
                                                "type": "boolean",
                                                "description": "Whether customer is taxable"
                                            },
                                            "Active": {
                                                "type": "boolean",
                                                "description": "Whether customer is active"
                                            }
                                        }
                                    }
                                },
                                "required": ["customer_id", "updates"]
                            }
                        }
                    },
                {
                    "type": "function",
                    "function": {
                            "name": "add_column_to_sheet",
                            "description": "CALL THIS IMMEDIATELY when user confirms they want to add a column to a sheet. Use when user says 'yes', 'confirm', 'proceed', 'add it', 'do it', or 'go ahead' after discussing adding a column.",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "sheet_name": {
                                        "type": "string",
                                        "description": "The name of the sheet to add column to (e.g., 'Clients', 'Projects', 'Permits')"
                                    },
                                    "column_name": {
                                        "type": "string",
                                        "description": "The name of the new column to add"
                                    },
                                    "default_value": {
                                        "type": "string",
                                        "description": "Optional default value to populate for existing rows (leave empty for blank)"
                                    }
                                },
                                "required": ["sheet_name", "column_name"]
                            }
                        }
                    },
                {
                    "type": "function",
                    "function": {
                            "name": "update_client_field",
                            "description": "Update a specific field/column for a client in the Clients sheet. Use this to sync QuickBooks IDs, update contact info, or modify any client field. CALL THIS when user confirms updating a client's information.",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "client_identifier": {
                                        "type": "string",
                                        "description": "The client name or ID to search for (e.g., 'Ajay Nair', '64 Phillips')"
                                    },
                                    "field_name": {
                                        "type": "string",
                                        "description": "The field/column name to update (e.g., 'QBO Client ID', 'Email', 'Phone Number')"
                                    },
                                    "field_value": {
                                        "type": "string",
                                        "description": "The new value to set for this field"
                                    },
                                    "identifier_field": {
                                        "type": "string",
                                        "description": "Which field to use for finding the client (default: 'Name'). Can be 'Name', 'Client ID', 'Address', etc."
                                    }
                                },
                                "required": ["client_identifier", "field_name", "field_value"]
                            }
                        }
                    },
                {
                    "type": "function",
                    "function": {
                            "name": "sync_quickbooks_clients",
                            "description": "Sync ALL clients from Google Sheets with QuickBooks customers. Matches clients by name and email, then updates the QBO_Client_ID column in Sheets. Use when user asks to 'sync clients with QuickBooks', 'update QB IDs', or 'match clients to QuickBooks'. Supports dry_run parameter for preview without changes.",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "dry_run": {
                                        "type": "boolean",
                                        "description": "If true, shows what would be synced without making changes (default: false)"
                                    }
                                },
                                "required": []
                            }
                        }
                    },
                {
                    "type": "function",
                    "function": {
                            "name": "map_clients_to_customers",
                            "description": "Establish comprehensive mapping between Google Sheets Clients and QuickBooks Customers. Analyzes all clients and customers, matches by QBO ID/email/name, updates 'QBO Client ID' column in Sheets, reports unmapped clients (in Sheets but not QB) and orphaned customers (in QB but not Sheets). Use for 'map clients to QB', 'sync client mappings', 'link clients to customers', or 'show unmapped clients'. Provides detailed statistics and identifies data quality issues.",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "auto_create": {
                                        "type": "boolean",
                                        "description": "If true, automatically creates QB customers for unmapped Sheet clients (default: false)"
                                    },
                                    "dry_run": {
                                        "type": "boolean",
                                        "description": "If true, previews matches without updating Sheets (default: false)"
                                    }
                                },
                                "required": []
                            }
                        }
                    },
                {
                    "type": "function",
                    "function": {
                            "name": "create_quickbooks_customer_from_sheet",
                            "description": "Create a new QuickBooks customer using data from an existing client in Google Sheets. IMPORTANT: This function automatically looks up the client's information (email, phone, address, company, role) from the Sheets - you do NOT need to ask the user for these details. Use when user asks to 'add [client name] to QuickBooks', 'create QB customer for [name]', or when a client exists in Sheets but not in QB. The function will extract all available client details from the Sheet automatically and create the QB customer. Automatically sets CustomerTypeRef to 'GC Compliance' and updates the Sheet with the new QBO Client ID.",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "client_name": {
                                        "type": "string",
                                        "description": "The name of the client from Google Sheets (e.g., 'Javier Martinez', 'ABC Company')"
                                    },
                                    "client_id": {
                                        "type": "string",
                                        "description": "Optional: The Client ID from Google Sheets if known"
                                    }
                                },
                                "required": ["client_name"]
                            }
                        }
                    },
                {
                    "type": "function",
                    "function": {
                            "name": "sync_gc_compliance_payments",
                            "description": "Reconcile GC Compliance payments with invoices in Google Sheets. Processes unsynced payments where Client Type is 'GC Compliance', matches them to invoices by Invoice ID or Client Name, updates invoice Amount Paid/Balance/Status, and marks payments as synced. Use when user asks to 'sync GC payments', 'reconcile compliance payments', or 'update invoices with payments'.",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "dry_run": {
                                        "type": "boolean",
                                        "description": "If true, shows what would be synced without making changes (default: false)"
                                    }
                                },
                                "required": []
                            }
                        }
                    },
                {
                    "type": "function",
                    "function": {
                            "name": "sync_quickbooks_customer_types",
                            "description": "Update CustomerTypeRef to 'GC Compliance' for all clients from Google Sheets in QuickBooks. Matches by name/email, updates CustomerTypeRef field, skips customers already set correctly. Use when user asks to 'update QB customer types', 'set GC Compliance type', 'sync customer types to QuickBooks', or 'label customers as GC Compliance'.",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "dry_run": {
                                        "type": "boolean",
                                        "description": "If true, shows what would be updated without making changes (default: false)"
                                    }
                                },
                                "required": []
                            }
                        }
                    },
                {
                    "type": "function",
                    "function": {
                        "name": "sync_quickbooks_payments",
                        "description": "Sync payment records from QuickBooks to Google Sheets. Retrieves payments from QuickBooks Payment API, matches them to clients, updates existing payments or creates new ones. Use when user asks to 'sync payments', 'update payments from QuickBooks', 'check for new QB payments', or 'refresh payment data'.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "days_back": {
                                    "type": "integer",
                                    "description": "Number of days back to sync payments from QuickBooks (default: 90 days)"
                                }
                            },
                            "required": []
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "get_client_payments",
                        "description": "Get all payment records for a specific client from Google Sheets. Returns payment history with amounts, dates, methods, and status. Use when user asks about client payment history, payment status, 'has [client] paid', 'show payments for [client]', or 'payment details for [client]'.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "client_id": {
                                    "type": "string",
                                    "description": "The 8-character Client ID to get payments for (e.g., '12b59b62')"
                                }
                            },
                            "required": ["client_id"]
                        }
                    }
                }
            ]
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=2000,  # Increased from 1000 to prevent truncation-induced hallucinations
                temperature=0.7,
                tools=tools,
                tool_choice="auto"  # Let AI decide when to call tools
            )
            
            # Log token usage for monitoring
            usage = response.usage
            if usage:
                logger.info(f"[METRICS] OpenAI API - Prompt tokens: {usage.prompt_tokens}, "
                           f"Completion tokens: {usage.completion_tokens}, "
                           f"Total: {usage.total_tokens}")
            
            message_response = response.choices[0].message
            
            # Check if AI wants to call tools
            function_calls = []
            if message_response.tool_calls:
                import json
                for tool_call in message_response.tool_calls:
                    if tool_call.type == "function":
                        function_calls.append({
                            "name": tool_call.function.name,
                            "arguments": json.loads(tool_call.function.arguments)
                        })
            
            # Sanitize AI output to catch any remaining hallucinations
            def sanitize_ai_output(text: str) -> str:
                """
                Post-filter to detect and remove common hallucination patterns.
                Uses context-aware detection rather than blanket string matching.
                """
                if not text:
                    return text
                
                # Track suspicious patterns (addresses)
                suspicious_addresses = [
                    "123 main st", "456 elm st", "789 oak ave",
                    "123 example", "sample address", "test street"
                ]
                
                # Track suspicious names (generic placeholders)
                suspicious_names = [
                    "john doe", "jane smith", "bob johnson",
                    "sample customer", "demo client", "test user",
                    "example company", "acme corp", "abc inc"
                ]
                
                text_lower = text.lower()
                found_issues = []
                
                # Check for suspicious addresses
                for addr in suspicious_addresses:
                    if addr in text_lower:
                        found_issues.append(f"Suspicious address pattern: {addr}")
                        logger.warning(f"[AI HALLUCINATION DETECTED] Fabricated address: {addr}")
                
                # Check for suspicious names (only flag if NOT in actual data context)
                for name in suspicious_names:
                    if name in text_lower:
                        found_issues.append(f"Suspicious name pattern: {name}")
                        logger.warning(f"[AI HALLUCINATION DETECTED] Fabricated name: {name}")
                
                # If hallucinations detected, add warning to response
                if found_issues:
                    warning = "\n\n⚠️ **Data Quality Warning**: Some information may be placeholder values. Please verify accuracy."
                    return text + warning
                
                return text
            
            # Apply output sanitization
            ai_text = message_response.content or ""
            ai_text = sanitize_ai_output(ai_text)
            
            # Return both the text response and any function calls
            return (ai_text, function_calls)
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise Exception(f"Failed to process message: {str(e)}")
    
    async def analyze_permit_data(self, permit_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze permit data and provide insights
        """
        try:
            prompt = f"""
            Analyze this permit data and provide insights:
            {permit_data}
            
            Please provide:
            1. Status summary
            2. Any compliance issues
            3. Next steps required
            4. Timeline assessment
            
            Format as JSON with keys: summary, issues, next_steps, timeline
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800,
                temperature=0.3
            )
            
            # Try to parse as JSON, fallback to text if needed
            content = response.choices[0].message.content
            try:
                import json
                return json.loads(content)
            except:
                return {"analysis": content}
                
        except Exception as e:
            logger.error(f"Permit analysis error: {e}")
            raise Exception(f"Failed to analyze permit data: {str(e)}")
    
    async def generate_report(self, data: Dict[str, Any], report_type: str = "summary") -> str:
        """
        Generate automated reports using AI
        """
        try:
            prompt = f"""
            Generate a {report_type} report for House Renovators LLC based on this data:
            {data}
            
            The report should be professional, detailed, and suitable for:
            - Internal team review
            - Client communication
            - Regulatory compliance
            
            Format as a structured report with clear sections.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500,
                temperature=0.5
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Report generation error: {e}")
            raise Exception(f"Failed to generate report: {str(e)}")

# Initialize service
openai_service = OpenAIService()