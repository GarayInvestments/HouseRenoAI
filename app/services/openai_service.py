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
            # System prompt for House Renovators AI Portal
            system_prompt = """
            You are the AI assistant for House Renovators LLC, a North Carolina licensed General Contractor.
            
            Your role is to help with:
            - Permit management and tracking
            - Project status updates
            - Inspection scheduling and results
            - Compliance with NC building codes
            - Team communication and coordination
            
            Always provide accurate, professional responses related to construction, permits, and project management.
            When you need to update data or perform actions, clearly indicate what function calls are needed.
            """
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ]
            
            # Add context if provided
            if context:
                context_message = f"Current context: {context}"
                messages.insert(1, {"role": "system", "content": context_message})
            
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