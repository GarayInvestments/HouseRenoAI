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
            # Enhanced system prompt for House Renovators AI Portal
            system_prompt = """
            You are an advanced AI assistant for House Renovators LLC, a North Carolina licensed General Contractor.
            
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
            5. Provide clear feedback on success or failure
            
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
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ]
            
            # Add context if provided - format it clearly for AI
            if context:
                # Build a structured context message
                context_parts = []
                
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
                    "name": "add_column_to_sheet",
                    "description": "Add a new column to a Google Sheet (Clients, Projects, Permits, etc.). Ask user for confirmation before adding.",
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