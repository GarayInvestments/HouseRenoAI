import openai
import logging
from typing import List, Dict, Any
from app.config import settings

logger = logging.getLogger(__name__)

class OpenAIService:
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    
    async def process_chat_message(self, message: str, context: Dict[str, Any] = None) -> str:
        """
        Process a chat message using OpenAI GPT-4o model
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
            
            YOUR CAPABILITIES:
            ✅ Answer ANY question about clients, projects, or permits
            ✅ Search and filter data by any field (status, date, location, etc.)
            ✅ Calculate totals, averages, and statistics
            ✅ Track timelines and identify delays
            ✅ Identify missing data or incomplete records
            ✅ Cross-reference data between sheets (clients → projects → permits)
            ✅ Provide detailed analysis and recommendations
            ✅ Generate reports and summaries
            
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
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=1000,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
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