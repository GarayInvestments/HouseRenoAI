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
        # Don't initialize automatically, wait for explicit call
        
    def initialize(self):
        """Initialize or re-initialize Google API services"""
        self._initialize_services()
    
    def _initialize_services(self):
        """Initialize Google API services"""
        try:
            logger.info(f"Initializing Google services with file: {settings.GOOGLE_SERVICE_ACCOUNT_FILE}")
            
            # Load service account credentials
            if os.path.exists(settings.GOOGLE_SERVICE_ACCOUNT_FILE):
                logger.info("Service account file exists, loading credentials...")
                
                SCOPES = [
                    "https://www.googleapis.com/auth/spreadsheets",
                    "https://www.googleapis.com/auth/drive.readonly"
                ]
                
                try:
                    self.credentials = service_account.Credentials.from_service_account_file(
                        settings.GOOGLE_SERVICE_ACCOUNT_FILE, 
                        scopes=SCOPES
                    )
                    logger.info("Credentials loaded successfully")
                except Exception as cred_error:
                    logger.error(f"Failed to load credentials: {cred_error}")
                    raise
                
                # Build services
                try:
                    self.sheets_service = build("sheets", "v4", credentials=self.credentials)
                    logger.info("Sheets service built successfully")
                except Exception as sheets_error:
                    logger.error(f"Failed to build sheets service: {sheets_error}")
                    raise
                
                try:
                    self.drive_service = build("drive", "v3", credentials=self.credentials)
                    logger.info("Drive service built successfully")
                except Exception as drive_error:
                    logger.error(f"Failed to build drive service: {drive_error}")
                    raise
                
                logger.info("Google services initialized successfully")
            else:
                logger.error(f"Service account file not found: {settings.GOOGLE_SERVICE_ACCOUNT_FILE}")
                
        except Exception as e:
            logger.error(f"Failed to initialize Google services: {e}")
            logger.error(f"Exception type: {type(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            # Don't raise here to allow the service to start, but log the error
    
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
    
    async def create_sheet_tab(self, sheet_name: str) -> bool:
        """
        Create a new sheet tab in the spreadsheet
        
        Args:
            sheet_name: Name of the sheet tab to create
            
        Returns:
            True if created successfully, False otherwise
        """
        try:
            request = {
                "addSheet": {
                    "properties": {
                        "title": sheet_name
                    }
                }
            }
            
            self.sheets_service.spreadsheets().batchUpdate(
                spreadsheetId=settings.SHEET_ID,
                body={"requests": [request]}
            ).execute()
            
            logger.info(f"✅ Created new sheet tab: {sheet_name}")
            return True
            
        except Exception as e:
            # Check if sheet already exists
            if "already exists" in str(e).lower():
                logger.info(f"Sheet {sheet_name} already exists")
                return True
            logger.error(f"Failed to create sheet tab {sheet_name}: {e}")
            return False
    
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
    
    async def get_all_sheet_data(self, sheet_name: str, max_rows: int = 1000) -> List[Dict[str, Any]]:
        """Generic method to get data from any sheet"""
        try:
            data = await self.read_sheet_data(f'{sheet_name}!A1:Z{max_rows}')
            
            if not data or len(data) < 2:
                return []
            
            headers = data[0]
            records = []
            
            for row in data[1:]:
                if len(row) > 0:
                    record = {}
                    for i, header in enumerate(headers):
                        record[header] = row[i] if i < len(row) else ""
                    records.append(record)
            
            logger.info(f"Retrieved {len(records)} records from {sheet_name}")
            return records
            
        except Exception as e:
            logger.error(f"Failed to get {sheet_name} data: {e}")
            return []
    
    async def update_record_by_id(
        self, 
        sheet_name: str, 
        id_field: str, 
        record_id: str, 
        updates: Dict[str, Any]
    ) -> bool:
        """
        Update a specific record in a sheet by ID
        
        Args:
            sheet_name: Name of the sheet (e.g., 'Projects', 'Permits')
            id_field: Name of the ID column (e.g., 'Project ID', 'Permit ID')
            record_id: The ID value to search for
            updates: Dictionary of field names and new values
            
        Returns:
            True if update succeeded, False otherwise
        """
        try:
            # Read the sheet data
            data = await self.read_sheet_data(f'{sheet_name}!A1:Z1000')
            
            if not data or len(data) < 2:
                logger.error(f"No data found in {sheet_name}")
                return False
            
            headers = data[0]
            
            # Find the ID column index
            try:
                id_column_index = headers.index(id_field)
            except ValueError:
                logger.error(f"ID field '{id_field}' not found in {sheet_name} headers: {headers}")
                return False
            
            # Find the row with matching ID
            row_index = None
            for i, row in enumerate(data[1:], start=2):  # Start at 2 because row 1 is headers
                if len(row) > id_column_index and row[id_column_index] == record_id:
                    row_index = i
                    break
            
            if row_index is None:
                logger.error(f"Record with {id_field}='{record_id}' not found in {sheet_name}")
                return False
            
            # Update the specific cells
            update_success = True
            for field_name, new_value in updates.items():
                try:
                    field_column_index = headers.index(field_name)
                except ValueError:
                    logger.warning(f"Field '{field_name}' not found in {sheet_name} headers, skipping")
                    continue
                
                # Convert column index to letter (A=0, B=1, etc.)
                column_letter = self._column_index_to_letter(field_column_index)
                cell_range = f'{sheet_name}!{column_letter}{row_index}'
                
                try:
                    await self.write_sheet_data(cell_range, [[str(new_value)]])
                    logger.info(f"Updated {sheet_name} {id_field}={record_id}, {field_name}={new_value} at {cell_range}")
                except Exception as e:
                    logger.error(f"Failed to update {cell_range}: {e}")
                    update_success = False
            
            return update_success
            
        except Exception as e:
            logger.error(f"Failed to update record in {sheet_name}: {e}")
            return False
    
    def _column_index_to_letter(self, index: int) -> str:
        """Convert 0-based column index to Excel column letter (0='A', 25='Z', 26='AA')"""
        result = ""
        while index >= 0:
            result = chr(index % 26 + ord('A')) + result
            index = index // 26 - 1
        return result
    
    async def add_column_to_sheet(
        self, 
        sheet_name: str, 
        column_name: str, 
        default_value: str = "",
        position: Optional[int] = None
    ) -> bool:
        """
        Add a new column to a sheet with an optional default value for existing rows
        
        Args:
            sheet_name: Name of the sheet (e.g., 'Projects', 'Permits', 'Clients')
            column_name: Name of the new column to add
            default_value: Default value to populate for existing rows (optional)
            position: Column index to insert at (None = append to end)
            
        Returns:
            True if column was added successfully, False otherwise
        """
        try:
            logger.info(f"Adding column '{column_name}' to {sheet_name}")
            
            # Read the sheet to get current structure
            data = await self.read_sheet_data(f'{sheet_name}!A1:Z1000')
            
            if not data or len(data) == 0:
                logger.error(f"Could not read data from {sheet_name}")
                return False
            
            headers = data[0]
            
            # Check if column already exists
            if column_name in headers:
                logger.warning(f"Column '{column_name}' already exists in {sheet_name}")
                return False
            
            # Determine where to add the column
            if position is None or position >= len(headers):
                # Append to end
                column_index = len(headers)
                column_letter = self._column_index_to_letter(column_index)
                
                # Add header
                header_range = f'{sheet_name}!{column_letter}1'
                await self.write_sheet_data(header_range, [[column_name]])
                logger.info(f"Added header '{column_name}' at {header_range}")
                
                # Add default value to all existing rows if specified
                if default_value and len(data) > 1:
                    row_count = len(data)
                    values = [[default_value] for _ in range(row_count - 1)]  # Exclude header row
                    data_range = f'{sheet_name}!{column_letter}2:{column_letter}{row_count}'
                    await self.write_sheet_data(data_range, values)
                    logger.info(f"Populated {row_count - 1} rows with default value '{default_value}'")
            else:
                # Insert at specific position (more complex - requires shifting)
                logger.warning(f"Insert at specific position not yet implemented, appending to end")
                return await self.add_column_to_sheet(sheet_name, column_name, default_value, None)
            
            logger.info(f"Successfully added column '{column_name}' to {sheet_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add column to {sheet_name}: {e}")
            return False
    
    async def update_client_field(
        self,
        client_identifier: str,
        field_name: str,
        field_value: str,
        identifier_field: str = "Name"
    ) -> bool:
        """
        Update a specific field for a client in the Clients sheet
        
        Args:
            client_identifier: The value to search for (e.g., client name, ID)
            field_name: Name of the field/column to update (e.g., 'QBO Client ID')
            field_value: New value to set
            identifier_field: Which field to use for finding the client (default: 'Name')
            
        Returns:
            True if update succeeded, False otherwise
            
        Example:
            await update_client_field("Ajay Nair", "QBO Client ID", "164")
        """
        try:
            logger.info(f"Updating {field_name} for client '{client_identifier}' to '{field_value}'")
            
            # Read the Clients sheet
            data = await self.read_sheet_data('Clients!A1:Z1000')
            
            if not data or len(data) < 2:
                logger.error("Could not read Clients sheet or no data found")
                return False
            
            headers = data[0]
            
            # Find the column index for the identifier field (try variations)
            actual_identifier_field = None
            if identifier_field in headers:
                actual_identifier_field = identifier_field
            elif identifier_field == "Name":
                # Try common name field variations
                for name_field in ["Full Name", "Client Name", "Name", "Contact Name"]:
                    if name_field in headers:
                        actual_identifier_field = name_field
                        break
            
            if actual_identifier_field is None:
                logger.error(f"Identifier field '{identifier_field}' not found in Clients sheet. Available fields: {headers}")
                return False
            
            identifier_col_index = headers.index(actual_identifier_field)
            logger.info(f"Using identifier field: {actual_identifier_field}")
            
            # Find the column index for the field to update
            if field_name not in headers:
                logger.error(f"Field '{field_name}' not found in Clients sheet. Available fields: {headers}")
                return False
            
            field_col_index = headers.index(field_name)
            field_col_letter = self._column_index_to_letter(field_col_index)
            
            # Find the row with matching client
            row_number = None
            for i, row in enumerate(data[1:], start=2):  # Start from row 2 (skip header)
                if len(row) > identifier_col_index:
                    cell_value = row[identifier_col_index]
                    # Case-insensitive comparison
                    if str(cell_value).lower().strip() == str(client_identifier).lower().strip():
                        row_number = i
                        break
            
            if row_number is None:
                logger.error(f"Client '{client_identifier}' not found in Clients sheet")
                return False
            
            # Update the cell
            cell_range = f'Clients!{field_col_letter}{row_number}'
            await self.write_sheet_data(cell_range, [[field_value]])
            logger.info(f"Successfully updated {cell_range} to '{field_value}'")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update client field: {e}")
            return False
    
    async def append_record(self, sheet_name: str, record_data: Dict[str, Any]) -> bool:
        """
        Append a new record to a sheet with proper field mapping
        
        Args:
            sheet_name: Name of the sheet (e.g., 'Projects', 'Permits')
            record_data: Dictionary of field names and values to add
            
        Returns:
            True if append succeeded, False otherwise
        """
        try:
            logger.info(f"Appending record to {sheet_name}")
            logger.debug(f"Record data keys: {list(record_data.keys())}")
            
            # Read the sheet to get headers
            data = await self.read_sheet_data(f'{sheet_name}!A1:Z1')
            
            if not data or len(data) == 0:
                logger.error(f"Could not read headers from {sheet_name}")
                return False
            
            headers = data[0]
            logger.info(f"{sheet_name} headers: {headers}")
            
            # Build row matching header order
            row_values = []
            unmatched_fields = []
            
            for header in headers:
                if header in record_data:
                    row_values.append(str(record_data[header]))
                else:
                    row_values.append("")  # Empty string for missing fields
            
            # Check for fields in record_data that don't match any header
            for field in record_data.keys():
                if field not in headers:
                    unmatched_fields.append(field)
            
            if unmatched_fields:
                logger.warning(f"Fields not found in {sheet_name} headers: {unmatched_fields}")
                logger.warning(f"These fields will be ignored: {[f'{k}={record_data[k]}' for k in unmatched_fields]}")
            
            logger.info(f"Appending row with {len(row_values)} values to {sheet_name}")
            logger.debug(f"Row values: {row_values}")
            
            # Append the row
            success = await self.append_sheet_data(f'{sheet_name}!A:Z', [row_values])
            
            if success:
                logger.info(f"Successfully appended record to {sheet_name}")
            else:
                logger.error(f"Failed to append record to {sheet_name}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to append record to {sheet_name}: {e}", exc_info=True)
            return False
    
    async def get_comprehensive_data(self) -> Dict[str, Any]:
        """Get data from all sheets for comprehensive AI context"""
        try:
            return {
                'Clients': await self.get_clients_data(),
                'Projects': await self.get_projects_data(),
                'Permits': await self.get_permits_data(),
                'Site Visits': await self.get_all_sheet_data('Site Visits'),
                'Subcontractors': await self.get_all_sheet_data('Subcontractors'),
                'Documents': await self.get_all_sheet_data('Documents'),
                'Tasks': await self.get_all_sheet_data('Tasks'),
                'Payments': await self.get_all_sheet_data('Payments'),
                'Jurisdiction': await self.get_all_sheet_data('Jurisdiction'),
                'Inspectors': await self.get_all_sheet_data('Inspectors'),
                'Construction Phase Tracking': await self.get_all_sheet_data('Construction Phase Tracking'),
                'Phase Tracking Images': await self.get_all_sheet_data('Phase Tracking Images')
            }
        except Exception as e:
            logger.error(f"Failed to get comprehensive data: {e}")
            return {}
    
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
    
    # ============== CHAT SESSION MANAGEMENT ==============
    
    async def save_session(self, session_data: Dict[str, Any]) -> bool:
        """
        Save or update a chat session to Google Sheets
        
        Args:
            session_data: Dictionary with session info
                - session_id (required)
                - user_email (optional)
                - title (optional)
                - created_at (optional)
                - last_activity (optional)
                - message_count (optional)
        
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            sheet_name = 'Chat_Sessions'
            session_id = session_data.get('session_id')
            
            if not session_id:
                logger.error("session_id is required to save session")
                return False
            
            # Ensure Chat_Sessions sheet exists with headers
            try:
                # Try to read the sheet to check if it exists
                sessions = await self.get_all_sheet_data(sheet_name)
                
                # Check if sheet is truly empty (no headers) vs just no data
                # If we get empty list, sheet might not exist OR might just be empty
                # Try to read just the first row to check for headers
                if not sessions:
                    test_read = await self.read_sheet_data(f"{sheet_name}!A1:A1")
                    if not test_read:
                        # Sheet doesn't exist - create it
                        raise Exception("Sheet does not exist")
                    # Sheet exists but is empty, continue
                    
            except Exception as sheet_error:
                # Sheet doesn't exist - create it with headers
                logger.info(f"Chat_Sessions sheet doesn't exist, creating it...")
                
                # First, create the sheet tab
                tab_created = await self.create_sheet_tab(sheet_name)
                if not tab_created:
                    logger.error(f"Failed to create {sheet_name} tab")
                    return False
                
                # Then add headers
                try:
                    headers = [['Session ID', 'User Email', 'Title', 'Created At', 'Last Activity', 'Message Count']]
                    await self.write_sheet_data(f"{sheet_name}!A1:F1", headers)
                    logger.info(f"✅ Created {sheet_name} sheet with headers")
                    sessions = []  # Empty list since sheet is new
                except Exception as create_error:
                    logger.error(f"Failed to write headers to {sheet_name}: {create_error}")
                    return False
            
            # Check if session already exists
            existing_row = None
            for i, session in enumerate(sessions):
                if session.get('Session ID') == session_id:
                    existing_row = i + 2  # +2 for header row and 1-indexed
                    break
            
            if existing_row:
                # Update existing session - update the entire row
                row_data = [
                    session_data.get('session_id', ''),
                    session_data.get('user_email', ''),
                    session_data.get('title', ''),
                    session_data.get('created_at', ''),
                    session_data.get('last_activity', ''),
                    str(session_data.get('message_count', 0))
                ]
                
                range_name = f"{sheet_name}!A{existing_row}:F{existing_row}"
                await self.write_sheet_data(range_name, [row_data])
                
                logger.info(f"Updated session {session_id} in row {existing_row}")
                return True
            
            # Insert new session
            row_data = [
                session_data.get('session_id', ''),
                session_data.get('user_email', ''),
                session_data.get('title', 'New Chat'),
                session_data.get('created_at', ''),
                session_data.get('last_activity', ''),
                str(session_data.get('message_count', 0))
            ]
            
            range_name = f"{sheet_name}!A:F"
            success = await self.append_sheet_data(range_name, [row_data])
            
            if success:
                logger.info(f"Saved new session {session_id} to Google Sheets")
            else:
                logger.error(f"Failed to save session {session_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to save session: {e}", exc_info=True)
            return False
    
    async def load_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Load a specific chat session from Google Sheets
        
        Args:
            session_id: The session ID to load
        
        Returns:
            Session data dict or None if not found
        """
        try:
            sessions = await self.get_all_sheet_data('Chat_Sessions')
            
            for session in sessions:
                if session.get('Session ID') == session_id:
                    return {
                        'session_id': session.get('Session ID'),
                        'user_email': session.get('User Email'),
                        'title': session.get('Title'),
                        'created_at': session.get('Created At'),
                        'last_activity': session.get('Last Activity'),
                        'message_count': int(session.get('Message Count', 0) or 0)
                    }
            
            logger.warning(f"Session {session_id} not found in Google Sheets")
            return None
            
        except Exception as e:
            logger.error(f"Failed to load session {session_id}: {e}")
            return None
    
    async def load_all_sessions(self, user_email: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Load all chat sessions from Google Sheets, optionally filtered by user
        
        Args:
            user_email: Optional email to filter sessions by user
        
        Returns:
            List of session data dicts
        """
        try:
            sessions = await self.get_all_sheet_data('Chat_Sessions')
            
            result = []
            for session in sessions:
                session_data = {
                    'session_id': session.get('Session ID'),
                    'user_email': session.get('User Email'),
                    'title': session.get('Title'),
                    'created_at': session.get('Created At'),
                    'last_activity': session.get('Last Activity'),
                    'message_count': int(session.get('Message Count', 0) or 0)
                }
                
                # Filter by user if specified
                if user_email is None or session_data['user_email'] == user_email:
                    result.append(session_data)
            
            logger.info(f"Loaded {len(result)} sessions from Google Sheets")
            return result
            
        except Exception as e:
            logger.error(f"Failed to load sessions: {e}")
            return []
    
    async def delete_session(self, session_id: str) -> bool:
        """
        Delete a chat session from Google Sheets
        
        Args:
            session_id: The session ID to delete
        
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            sheet_name = 'Chat_Sessions'
            
            # Get the actual sheetId for Chat_Sessions FIRST to avoid extra API call
            spreadsheet = self.sheets_service.spreadsheets().get(
                spreadsheetId=settings.SHEET_ID
            ).execute()
            
            sheet_id = None
            for sheet in spreadsheet.get('sheets', []):
                if sheet['properties']['title'] == sheet_name:
                    sheet_id = sheet['properties']['sheetId']
                    break
            
            if sheet_id is None:
                logger.error(f"{sheet_name} sheet not found in spreadsheet")
                return False
            
            # Re-fetch sessions immediately before deletion to get latest row numbers
            # This prevents race conditions when multiple deletes happen quickly
            sessions = await self.get_all_sheet_data(sheet_name)
            
            row_to_delete = None
            for i, session in enumerate(sessions):
                if session.get('Session ID') == session_id:
                    row_to_delete = i + 2  # +2 for header row and 1-indexed
                    break
            
            if row_to_delete is None:
                logger.warning(f"Session {session_id} not found for deletion (may have been already deleted)")
                return False
            
            # Delete the row using Google Sheets API
            request = {
                "deleteDimension": {
                    "range": {
                        "sheetId": sheet_id,  # Use actual sheetId instead of hardcoded 0
                        "dimension": "ROWS",
                        "startIndex": row_to_delete - 1,  # 0-indexed for API
                        "endIndex": row_to_delete
                    }
                }
            }
            
            self.sheets_service.spreadsheets().batchUpdate(
                spreadsheetId=settings.SHEET_ID,
                body={"requests": [request]}
            ).execute()
            
            logger.info(f"Deleted session {session_id} from Google Sheets (row {row_to_delete})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete session {session_id}: {e}", exc_info=True)
            return False

# Service instance will be initialized during startup
google_service: Optional[GoogleService] = None