from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional
import logging
import base64
import io
from PIL import Image
import PyPDF2

import app.services.google_service as google_service_module
import app.services.openai_service as openai_service_module

logger = logging.getLogger(__name__)
router = APIRouter()

def get_google_service():
    """Helper function to get Google service with proper error handling"""
    if not hasattr(google_service_module, 'google_service') or google_service_module.google_service is None:
        raise HTTPException(status_code=503, detail="Google service not initialized")
    return google_service_module.google_service

def get_openai_service():
    """Helper function to get OpenAI service with proper error handling"""
    if not hasattr(openai_service_module, 'openai_service') or openai_service_module.openai_service is None:
        raise HTTPException(status_code=503, detail="OpenAI service not initialized")
    return openai_service_module.openai_service

@router.post("/extract")
async def extract_document_data(
    file: UploadFile = File(...),
    document_type: str = Form(..., description="Type: 'project' or 'permit'"),
    client_id: Optional[str] = Form(None, description="Optional client ID to associate")
):
    """
    Upload a PDF or image and extract structured data using AI
    """
    try:
        # Validate file type
        allowed_types = ['application/pdf', 'image/jpeg', 'image/jpg', 'image/png', 'image/webp']
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400, 
                detail=f"File type {file.content_type} not supported. Please upload PDF or image (JPG, PNG, WEBP)"
            )
        
        # Validate document type
        if document_type not in ['project', 'permit']:
            raise HTTPException(status_code=400, detail="document_type must be 'project' or 'permit'")
        
        # Read file content
        file_content = await file.read()
        logger.info(f"Processing {file.content_type} file: {file.filename} ({len(file_content)} bytes)")
        
        # Process based on file type
        if file.content_type == 'application/pdf':
            extracted_text = await extract_text_from_pdf(file_content)
            # For PDF, we'll use text extraction + GPT-4
            extracted_data = await process_with_gpt4_text(extracted_text, document_type)
        else:
            # For images, use GPT-4 Vision
            base64_image = base64.b64encode(file_content).decode('utf-8')
            extracted_data = await process_with_gpt4_vision(base64_image, file.content_type, document_type)
        
        # Add client_id if provided
        if client_id:
            extracted_data['Client ID'] = client_id
        
        logger.info(f"Successfully extracted data from {file.filename}")
        return {
            "status": "success",
            "filename": file.filename,
            "document_type": document_type,
            "extracted_data": extracted_data,
            "message": f"Data extracted successfully. Review and confirm to create {document_type}."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to extract document data: {e}")
        raise HTTPException(status_code=500, detail=f"Document extraction failed: {str(e)}")

@router.post("/create-from-extract")
async def create_record_from_extraction(
    document_type: str = Form(...),
    extracted_data: dict = Form(...)
):
    """
    Create a project or permit record from extracted data
    """
    try:
        google_service = get_google_service()
        
        if document_type == 'project':
            sheet_name = 'Projects'
            id_field = 'Project ID'
            # Generate project ID if not provided
            if 'Project ID' not in extracted_data:
                projects = await google_service.get_projects_data()
                extracted_data['Project ID'] = f"P-{len(projects) + 1:03d}"
        elif document_type == 'permit':
            sheet_name = 'Permits'
            id_field = 'Permit ID'
            # Generate permit ID if not provided
            if 'Permit ID' not in extracted_data:
                permits = await google_service.get_permits_data()
                extracted_data['Permit ID'] = f"PER-{len(permits) + 1:03d}"
        else:
            raise HTTPException(status_code=400, detail="Invalid document_type")
        
        # Add the record to Google Sheets
        success = await google_service.append_record(sheet_name, extracted_data)
        
        if not success:
            raise HTTPException(status_code=500, detail=f"Failed to create {document_type}")
        
        record_id = extracted_data.get(id_field, 'Unknown')
        logger.info(f"Created {document_type} {record_id} from extracted data")
        
        return {
            "status": "success",
            "message": f"{document_type.capitalize()} created successfully",
            "record_id": record_id,
            "data": extracted_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create record: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create {document_type}: {str(e)}")

async def extract_text_from_pdf(pdf_content: bytes) -> str:
    """Extract text from PDF file"""
    try:
        pdf_file = io.BytesIO(pdf_content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        
        return text.strip()
    except Exception as e:
        logger.error(f"PDF extraction failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to extract text from PDF")

async def process_with_gpt4_text(text: str, document_type: str) -> dict:
    """Process extracted text with GPT-4 to get structured data"""
    import json
    
    try:
        openai_service = get_openai_service()
        
        if document_type == 'project':
            prompt = f"""Extract project information from this document and return it as a JSON object with these fields:
- Project Name
- Project Address
- Project Type (e.g., Residential, Commercial)
- Client ID (if mentioned)
- Start Date (format: YYYY-MM-DD)
- Status (default: "Planning")
- Budget (if mentioned)
- Description

Document text:
{text}

Return only valid JSON, no other text."""
        else:  # permit
            prompt = f"""Extract permit information from this document and return it as a JSON object with these fields:
- Permit Number
- Permit Type
- Project ID (if mentioned)
- Permit Status (default: "Permit Submitted")
- Submit Date (format: YYYY-MM-DD)
- Issue Date (format: YYYY-MM-DD, if mentioned)
- Expiration Date (format: YYYY-MM-DD, if mentioned)
- Description

Document text:
{text}

Return only valid JSON, no other text."""
        
        # Use OpenAI client to extract structured data
        response = openai_service.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
            temperature=0.3
        )
        
        if not response or not response.choices:
            raise ValueError("No response from AI")
        
        # Parse JSON from response
        content = response.choices[0].message.content
        if not content:
            raise ValueError("AI returned empty response")
        
        # Strip markdown code blocks (same logic as vision processing)
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        extracted_data = json.loads(content)
        return extracted_data
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse AI response as JSON: {e}")
        raise HTTPException(status_code=500, detail="AI returned invalid data format")
    except Exception as e:
        logger.error(f"GPT-4 text processing failed: {e}")
        raise HTTPException(status_code=500, detail="AI processing failed")

async def process_with_gpt4_vision(base64_image: str, mime_type: str, document_type: str) -> dict:
    """Process image with GPT-4 Vision to get structured data"""
    import json
    
    try:
        openai_service = get_openai_service()
        
        if document_type == 'project':
            prompt = """Analyze this image/document and extract project information. Return a JSON object with these fields:
- Project Name
- Project Address
- Project Type (e.g., Residential, Commercial, Renovation)
- Start Date (format: YYYY-MM-DD, if visible)
- Status (default: "Planning")
- Budget (if mentioned)
- Description (brief summary of what you see)

Return only valid JSON, no other text."""
        else:  # permit
            prompt = """Analyze this permit document image and extract information. Return a JSON object with these fields:
- Permit Number
- Permit Type (e.g., Building Permit, Electrical, Plumbing)
- Permit Status (default: "Permit Submitted")
- Submit Date (format: YYYY-MM-DD, if visible)
- Issue Date (format: YYYY-MM-DD, if visible)
- Expiration Date (format: YYYY-MM-DD, if visible)
- Description (what type of work is permitted)

Return only valid JSON, no other text."""
        
        # Use OpenAI Vision API with the configured client
        import json
        
        response = openai_service.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=1000
        )
        
        result = response.choices[0].message.content
        
        if not result:
            raise HTTPException(status_code=500, detail="No response from AI")
        
        # Extract JSON from response (might have markdown code blocks)
        if "```json" in result:
            result = result.split("```json")[1].split("```")[0].strip()
        elif "```" in result:
            result = result.split("```")[1].split("```")[0].strip()
        
        extracted_data = json.loads(result)
        return extracted_data
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON from AI response: {e}")
        raise HTTPException(status_code=500, detail="AI returned invalid JSON format")
    except Exception as e:
        logger.error(f"GPT-4 Vision processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"AI vision processing failed: {str(e)}")
