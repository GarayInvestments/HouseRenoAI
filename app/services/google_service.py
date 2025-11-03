import os
import json
import logging
import requests
from typing import List, Dict, Any, Optional
from google.oauth2 import service_account
from googleapiclient.discovery import build
from app.config import settings

logger = logging.getLogger(__name__)

class GoogleService:
    def __init__(self):
        self.credentials = None
        self.sheets_service = None
        self.drive_service = None
        self._initialize_services()
    
    def _initialize_services(self):
        """Initialize Google API services"""
        try:
            # Load service account credentials
            if os.path.exists(settings.GOOGLE_SERVICE_ACCOUNT_FILE):
                SCOPES = [
                    "https://www.googleapis.com/auth/spreadsheets",
                    "https://www.googleapis.com/auth/drive.readonly"
                ]
                
                self.credentials = service_account.Credentials.from_service_account_file(
                    settings.GOOGLE_SERVICE_ACCOUNT_FILE, 
                    scopes=SCOPES
                )
                
                # Build services
                self.sheets_service = build("sheets", "v4", credentials=self.credentials)
                self.drive_service = build("drive", "v3", credentials=self.credentials)
                
                logger.info("Google services initialized successfully")
            else:
                logger.error(f"Service account file not found: {settings.GOOGLE_SERVICE_ACCOUNT_FILE}")
                
        except Exception as e:
            logger.error(f"Failed to initialize Google services: {e}")
            raise
    
    async def read_sheet_data(self, range_name: str, sheet_id: str = None) -> List[List[str]]:
        """Read data from Google Sheets"""
        try:
            sheet_id = sheet_id or settings.SHEET_ID
            
            result = self.sheets_service.spreadsheets().values().get(
                spreadsheetId=sheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            logger.info(f"Read {len(values)} rows from sheet range: {range_name}")
            return values
            
        except Exception as e:
            logger.error(f"Failed to read sheet data: {e}")
            raise
    
    async def write_sheet_data(self, range_name: str, values: List[List[str]], sheet_id: str = None) -> bool:
        """Write data to Google Sheets"""
        try:
            sheet_id = sheet_id or settings.SHEET_ID
            
            body = {
                'values': values
            }
            
            result = self.sheets_service.spreadsheets().values().update(
                spreadsheetId=sheet_id,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()
            
            logger.info(f"Updated {result.get('updatedCells', 0)} cells in range: {range_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to write sheet data: {e}")
            raise
    
    async def append_sheet_data(self, range_name: str, values: List[List[str]], sheet_id: str = None) -> bool:
        """Append data to Google Sheets"""
        try:
            sheet_id = sheet_id or settings.SHEET_ID
            
            body = {
                'values': values
            }
            
            result = self.sheets_service.spreadsheets().values().append(
                spreadsheetId=sheet_id,
                range=range_name,
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()
            
            logger.info(f"Appended {len(values)} rows to sheet")
            return True
            
        except Exception as e:
            logger.error(f"Failed to append sheet data: {e}")
            raise
    
    async def get_permits_data(self) -> List[Dict[str, Any]]:
        """Get all permits data from the sheet"""
        try:
            # Assuming permits are in a sheet named 'Permits' starting from row 2 (headers in row 1)
            data = await self.read_sheet_data('Permits!A1:Z1000')
            
            if not data:
                return []
            
            headers = data[0]
            permits = []
            
            for row in data[1:]:
                if len(row) > 0:  # Skip empty rows
                    permit = {}
                    for i, header in enumerate(headers):
                        permit[header] = row[i] if i < len(row) else ""
                    permits.append(permit)
            
            return permits
            
        except Exception as e:
            logger.error(f"Failed to get permits data: {e}")
            raise
    
    async def get_projects_data(self) -> List[Dict[str, Any]]:
        """Get all projects data from the sheet"""
        try:
            data = await self.read_sheet_data('Projects!A1:Z1000')
            
            if not data:
                return []
            
            headers = data[0]
            projects = []
            
            for row in data[1:]:
                if len(row) > 0:
                    project = {}
                    for i, header in enumerate(headers):
                        project[header] = row[i] if i < len(row) else ""
                    projects.append(project)
            
            return projects
            
        except Exception as e:
            logger.error(f"Failed to get projects data: {e}")
            raise
    
    async def get_clients_data(self) -> List[Dict[str, Any]]:
        """Get all clients data from the sheet"""
        try:
            data = await self.read_sheet_data('Clients!A1:Z1000')
            
            if not data:
                return []
            
            headers = data[0]
            clients = []
            
            for row in data[1:]:
                if len(row) > 0:
                    client = {}
                    for i, header in enumerate(headers):
                        client[header] = row[i] if i < len(row) else ""
                    clients.append(client)
            
            return clients
            
        except Exception as e:
            logger.error(f"Failed to get clients data: {e}")
            raise
    
    async def notify_chat(self, message: str) -> bool:
        """Send notification to Google Chat webhook"""
        try:
            if not settings.CHAT_WEBHOOK_URL:
                logger.warning("Chat webhook URL not configured")
                return False
            
            payload = {"text": message}
            
            response = requests.post(
                settings.CHAT_WEBHOOK_URL,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                logger.info("Chat notification sent successfully")
                return True
            else:
                logger.error(f"Chat notification failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send chat notification: {e}")
            return False

# Initialize service
google_service = GoogleService()