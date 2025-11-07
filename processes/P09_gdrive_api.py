# ====================================================================================================
# P09_gdrive_api.py
# ----------------------------------------------------------------------------------------------------
# Provides Google Drive API authentication and core functions.
#
# Purpose:
#   - Authenticate with the Google Drive API using OAuth 2.0.
#   - Provide functions for uploading files from local disk and from Pandas DataFrames (in memory).
# ----------------------------------------------------------------------------------------------------
# Author:       Gerry Pidgeon
# Created:      2025-11-07
# Project:      GP Boilerplate
# ====================================================================================================


# ====================================================================================================
# 1. SYSTEM IMPORTS
# ----------------------------------------------------------------------------------------------------
# Add parent directory to sys.path so this module can import other "processes" packages.
# ====================================================================================================
import sys
from pathlib import Path

# --- Standard block for all modules ---
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.dont_write_bytecode = True  # Prevents __pycache__ folders from being created


# ====================================================================================================
# 2. PROJECT IMPORTS
# ----------------------------------------------------------------------------------------------------
# Bring in standard libraries and settings from the central import hub.
# ====================================================================================================
from processes.P00_set_packages import * # Imports all packages from P00_set_packages.py
import datetime as dt # Used in the standalone test block

# --- Import project paths ---
from processes.P01_set_file_paths import (
    GDRIVE_CREDENTIALS_FILE, GDRIVE_TOKEN_FILE, PROJECT_ROOT
)
# --- Import OS-specific functions ---
from processes.P02_system_processes import user_download_folder


# ====================================================================================================
# 3. CONSTANTS AND SCOPES
# ----------------------------------------------------------------------------------------------------
# Define what permissions we are asking for.
SCOPES = ['https://www.googleapis.com/auth/drive']


# ====================================================================================================
# 4. AUTHENTICATION FUNCTION
# ----------------------------------------------------------------------------------------------------

def get_drive_service():
    """
    Authenticates with the Google Drive API and returns a service object.
    
    Handles the OAuth 2.0 flow, storing credentials in the file
    specified by GDRIVE_TOKEN_FILE for future runs.
    """
    creds = None
    if os.path.exists(GDRIVE_TOKEN_FILE):
        try:
            creds = Credentials.from_authorized_user_file(GDRIVE_TOKEN_FILE, SCOPES)
        except Exception as e:
            print(f"Error loading token.json: {e}. Re-authenticating...")
            creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Error refreshing token: {e}")
                print(f"Please delete '{GDRIVE_TOKEN_FILE}' and re-run.")
                return None
        else:
            if not os.path.exists(GDRIVE_CREDENTIALS_FILE):
                print(f"Error: '{GDRIVE_CREDENTIALS_FILE}' not found.")
                print("Please download it from Google Cloud Console and save it in the 'credentials' folder.")
                return None
            
            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    GDRIVE_CREDENTIALS_FILE, SCOPES)
                creds = flow.run_local_server(port=0)
            except Exception as e:
                print(f"Error during authentication flow: {e}")
                return None
        
        try:
            with open(GDRIVE_TOKEN_FILE, 'w') as token:
                token.write(creds.to_json())
        except Exception as e:
            print(f"Error saving token file: {e}")

    try:
        service = build('drive', 'v3', credentials=creds)
        print("Google Drive API service created successfully.")
        return service
    except HttpError as error:
        print(f'An error occurred building the service: {error}')
        return None
    except Exception as error:
        print(f'An unexpected error occurred: {error}')
        return None

# ====================================================================================================
# 5. API HELPER FUNCTIONS (Finding files/folders)
# ----------------------------------------------------------------------------------------------------

def list_drive_files(service, num_files=10):
    """
    Lists the first 'num_files' files and folders in the user's Google Drive.
    """
    if not service:
        print("Service object is not valid. Cannot list files.")
        return

    try:
        print(f"\nListing first {num_files} files from Google Drive:")
        results = service.files().list(
            pageSize=num_files,
            fields="nextPageToken, files(id, name, mimeType)"
        ).execute()
        
        items = results.get('files', [])

        if not items:
            print('No files found.')
            return
        
        print('Files:')
        for item in items:
            print(f"- {item['name']} (ID: {item['id']}, Type: {item['mimeType']})")
            
    except HttpError as error:
        print(f'An error occurred: {error}')
    except Exception as error:
        print(f'An unexpected error occurred: {error}')


def find_folder_id(service, folder_name: str) -> str | None:
    """Finds the ID of a Google Drive folder by its name."""
    if not service:
        print("Service object is not valid.")
        return None
        
    try:
        query = f"mimeType='application/vnd.google-apps.folder' and name='{folder_name}' and trashed=false"
        results = service.files().list(
            q=query, pageSize=1, fields="files(id, name)"
        ).execute()
        
        items = results.get('files', [])
        
        if not items:
            print(f"No folder found with name: '{folder_name}'")
            return None
        else:
            folder_id = items[0]['id']
            print(f"Found folder '{folder_name}' (ID: {folder_id})")
            return folder_id
            
    except HttpError as error:
        print(f'An error occurred finding folder: {error}')
        return None

def find_file_id(service, file_name: str, in_folder_id: str = None) -> str | None:
    """Finds the ID of a Google Drive file by its name."""
    if not service:
        print("Service object is not valid.")
        return None
        
    try:
        query = f"name='{file_name}' and mimeType!='application/vnd.google-apps.folder' and trashed=false"
        if in_folder_id:
            query += f" and '{in_folder_id}' in parents"
            
        results = service.files().list(
            q=query, pageSize=1, fields="files(id, name)"
        ).execute()
        
        items = results.get('files', [])
        
        if not items:
            print(f"No file found with name: '{file_name}'")
            return None
        else:
            file_id = items[0]['id']
            print(f"Found file '{file_name}' (ID: {file_id})")
            return file_id
            
    except HttpError as error:
        print(f'An error occurred finding file: {error}')
        return None


# ====================================================================================================
# 6. API CORE FUNCTIONS (Upload / Download)
# ----------------------------------------------------------------------------------------------------

def upload_file(service, local_filepath: Path, gdrive_folder_id: str = None, gdrive_filename: str = None) -> str | None:
    """
    Uploads a local file to Google Drive.
    """
    if not service:
        print("Service object is not valid.")
        return None
    
    if not local_filepath.exists():
        print(f"Error: Local file not found at '{local_filepath}'")
        return None
        
    try:
        if gdrive_filename is None:
            gdrive_filename = local_filepath.name

        file_metadata = {'name': gdrive_filename}
        if gdrive_folder_id:
            file_metadata['parents'] = [gdrive_folder_id]

        media = MediaFileUpload(local_filepath, resumable=True)
        file = service.files().create(
            body=file_metadata, media_body=media, fields='id'
        ).execute()
        
        file_id = file.get('id')
        print(f"File '{gdrive_filename}' uploaded successfully (ID: {file_id})")
        return file_id

    except HttpError as error:
        print(f'An error occurred during upload: {error}')
        return None
    except Exception as e:
        print(f'An unexpected error occurred during upload: {e}')
        return None

def upload_dataframe_as_csv(service, csv_buffer: io.StringIO, filename: str, gdrive_folder_id: str = None) -> str | None:
    """
    Uploads a Pandas DataFrame (as CSV data in memory) to Google Drive.
    
    This function is used by the main GUI app to avoid saving temporary files.
    
    Args:
        service: The authenticated Google Drive service object.
        csv_buffer (io.StringIO): The CSV data buffer created from df.to_csv().
        filename (str): The name to save the file as in Google Drive (must end in .csv).
        gdrive_folder_id (str, optional): The ID of the Drive folder to upload into.
    
    Returns:
        str | None: The new Google Drive file ID if successful, otherwise None.
    """
    if not service:
        print("Service object is not valid.")
        return None

    try:
        # Create an io.BytesIO object from the StringIO content
        media_content = io.BytesIO(csv_buffer.getvalue().encode('utf-8'))
        
        file_metadata = {'name': filename}
        if gdrive_folder_id:
            file_metadata['parents'] = [gdrive_folder_id]

        # Use MediaIoBaseUpload to stream the in-memory data
        media = MediaIoBaseUpload(
            media_content,
            mimetype='text/csv',
            chunksize=1024*1024, # 1MB chunk size
            resumable=True
        )
        
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        
        file_id = file.get('id')
        print(f"Report '{filename}' uploaded successfully to Drive (ID: {file_id})")
        return file_id

    except HttpError as error:
        print(f'An API error occurred during upload: {error}')
        return None
    except Exception as e:
        print(f'An unexpected error occurred during upload: {e}')
        return None


def download_file(service, gdrive_file_id: str, local_save_path: Path):
    """
    Downloads a file from Google Drive.
    """
    if not service:
        print("Service object is not valid.")
        return
        
    try:
        local_save_path.parent.mkdir(parents=True, exist_ok=True)

        request = service.files().get_media(fileId=gdrive_file_id)
        
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        
        done = False
        print(f"Starting download for file ID: {gdrive_file_id}...")
        while done is False:
            status, done = downloader.next_chunk()
            print(f"Download {int(status.progress() * 100)}%.")
            
        with open(local_save_path, 'wb') as f:
            f.write(fh.getbuffer())
            
        print(f"\nFile downloaded successfully and saved to:")
        print(f"{local_save_path}")

    except HttpError as error:
        print(f'An error occurred during download: {error}')
    except Exception as e:
        print(f'An unexpected error occurred during download: {e}')


# ====================================================================================================
# 7. MAIN EXECUTION (STANDALONE TEST)
# ----------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    # This is placeholder code for testing the API functions outside the GUI.
    # It requires credentials/credentials.json to be present.
    print("--- Running P09 Standalone Test (Authentication only) ---")
    drive_service = get_drive_service()
    
    if drive_service:
        list_drive_files(drive_service, 5)