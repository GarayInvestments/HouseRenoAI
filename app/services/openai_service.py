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
            ✅ **Access QuickBooks invoices and customer data**
            ✅ **Query customer balances, open invoices, payment status**
            ✅ **Create QuickBooks invoices** (ALWAYS ask for confirmation before creating)
            ✅ **Update client information** (phone, email, address, etc.)
            ✅ **Add new columns to Google Sheets** (ALWAYS ask for confirmation before adding)
            
            🔍 DATA SOURCE PRIORITY - CRITICAL RULES:
            
            ⚠️ **DEFAULT TO GOOGLE SHEETS** unless user explicitly mentions QuickBooks/QBO:
            
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
            
            DATA ACCESS:
            You receive the complete dataset in the context. Search through it thoroughly to answer questions.
            Don't say "I don't have access" - the data is provided to you in the context.
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
                
                # Add QuickBooks data summary
                if context.get('quickbooks_connected'):
                    context_parts.append(f"\n🔗 QuickBooks: CONNECTED")
                    context_parts.append(f"QuickBooks Customers: {context.get('qb_customers_count', 0)}")
                    context_parts.append(f"QuickBooks Invoices: {context.get('qb_invoices_count', 0)}")
                    
                    # Add QuickBooks customers summary
                    if 'qb_customers_summary' in context and context['qb_customers_summary']:
                        context_parts.append("\n\n=== QUICKBOOKS CUSTOMERS ===")
                        for customer in context['qb_customers_summary'][:30]:
                            context_parts.append(
                                f"\nQB Customer ID: {customer.get('id')}"
                                f"\n  Name: {customer.get('name')}"
                                f"\n  Email: {customer.get('email')}"
                                f"\n  Phone: {customer.get('phone')}"
                                f"\n  Balance: ${customer.get('balance', 0)}"
                            )
                    
                    # Add QB invoice summaries (NOT full objects - too large!)
                    if 'qb_invoices_summary' in context and context['qb_invoices_summary']:
                        context_parts.append(f"\n\n=== QUICKBOOKS INVOICES ({len(context['qb_invoices_summary'])} total) ===")
                        for invoice in context['qb_invoices_summary'][:30]:  # Limit to 30 most recent
                            context_parts.append(
                                f"\nInvoice #{invoice.get('doc_number')} (ID: {invoice.get('id')})"
                                f"\n  Customer: {invoice.get('customer_name')}"
                                f"\n  Date: {invoice.get('txn_date')}"
                                f"\n  Total: ${invoice.get('total', 0)}"
                                f"\n  Balance: ${invoice.get('balance', 0)}"
                                f"\n  Status: {invoice.get('status')}"
                            )
                else:
                    context_parts.append(f"\n⚠️ QuickBooks: Not connected")
                
                # Add available IDs for lookup
                if 'client_ids' in context and context['client_ids']:
                    context_parts.append(f"\nAvailable Client IDs: {', '.join(context['client_ids'][:20])}")
                    if len(context['client_ids']) > 20:
                        context_parts.append(f"... and {len(context['client_ids']) - 20} more")
                
                # Add clients summary for easy reference
                if 'clients_summary' in context and context['clients_summary']:
                    context_parts.append("\n\n=== CLIENTS DATA ===")
                    for client in context['clients_summary'][:50]:  # Limit to prevent token overflow
                        context_parts.append(
                            f"\nClient ID: {client.get('Client ID')}"
                            f"\n  Name: {client.get('Name')}"
                            f"\n  Status: {client.get('Status')}"
                            f"\n  Address: {client.get('Address')}"
                            f"\n  Phone: {client.get('Phone')}"
                            f"\n  Email: {client.get('Email')}"
                        )
                
                # Add full arrays for detailed queries
                if 'all_clients' in context:
                    context_parts.append(f"\n\n=== FULL CLIENT RECORDS ({len(context['all_clients'])} total) ===")
                    context_parts.append(str(context['all_clients']))
                
                if 'all_projects' in context:
                    context_parts.append(f"\n\n=== FULL PROJECT RECORDS ({len(context['all_projects'])} total) ===")
                    context_parts.append(str(context['all_projects']))
                
                if 'all_permits' in context:
                    context_parts.append(f"\n\n=== FULL PERMIT RECORDS ({len(context['all_permits'])} total) ===")
                    context_parts.append(str(context['all_permits']))
                
                context_message = "\n".join(context_parts)
                messages.insert(1, {"role": "system", "content": f"DATA CONTEXT:\n{context_message}"})
            
            # Define available functions for the AI to call
            functions = [
                {
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
                },
                {
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
                },
                {
                    "name": "create_quickbooks_invoice",
                    "description": "Create a new invoice in QuickBooks Online. ONLY call this after user confirms they want to create the invoice.",
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
                                "description": "The total invoice amount in USD"
                            },
                            "description": {
                                "type": "string",
                                "description": "Description of services/work performed"
                            },
                            "invoice_date": {
                                "type": "string",
                                "description": "Invoice date in YYYY-MM-DD format (default: today)"
                            },
                            "due_date": {
                                "type": "string",
                                "description": "Due date in YYYY-MM-DD format (default: 30 days from invoice date)"
                            }
                        },
                        "required": ["customer_id", "customer_name", "amount", "description"]
                    }
                },
                {
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
                },
                {
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
                },
                {
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
            ]
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=1000,
                temperature=0.7,
                functions=functions,
                function_call="auto"  # Let AI decide when to call functions
            )
            
            message_response = response.choices[0].message
            
            # Check if AI wants to call a function
            function_calls = []
            if message_response.function_call:
                import json
                function_calls.append({
                    "name": message_response.function_call.name,
                    "arguments": json.loads(message_response.function_call.arguments)
                })
            
            # Return both the text response and any function calls
            return (message_response.content or "", function_calls)
            
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