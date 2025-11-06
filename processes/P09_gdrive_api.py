# ====================================================================================================
# P09_gdrive_api.py
# ----------------------------------------------------------------------------------------------------
# Provides Google Drive API authentication and core functions.
#
# Purpose:
#   - Authenticate with the Google Drive API using OAuth 2.0.
#   - Create a reusable 'service' object for making API calls.
#   - Provide functions for listing, uploading, downloading, and finding files/folders.
#
# ----------------------------------------------------------------------------------------------------
#   *** HOW TO USE ***
#
# 1. Install required libraries:
#    (Handled by P00_set_packages.py)
#
# 2. Enable Google Drive API in Google Cloud Console:
#    https://console.cloud.google.com/
#
# 3. Create OAuth 2.0 Credentials for a "Desktop app":
#    - Go to "APIs & Services" -> "Credentials".
#    - "+ CREATE CREDENTIALS" -> "OAuth client ID" -> "Desktop app".
#    - Download the JSON file.
#
# 4. Rename the downloaded file to "credentials.json" and place it
#    in the "credentials" folder (defined in P01_set_file_paths.py).
#
# 5. Run this script ONCE from your terminal to authenticate:
#    python processes/P09_gdrive_api.py
#
# 6. Your web browser will open. Log in to your Google account and
#    grant the script permission to access your Google Drive.
#
# 7. After you approve, a file named "token.json" will be saved
#    in the "credentials" folder.
#
#    **NEVER SHARE token.json OR credentials.json!**
# ----------------------------------------------------------------------------------------------------
# Author:       Gerry Pidgeon
# Created:      2025-11-06
# Project:      Just Eat Orders-to-Cash Reconciliation
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
# We need full 'drive' access (not readonly) to upload and download files.
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
    # The file token.json stores the user's access and refresh tokens.
    if os.path.exists(GDRIVE_TOKEN_FILE):
        try:
            creds = Credentials.from_authorized_user_file(GDRIVE_TOKEN_FILE, SCOPES)
        except Exception as e:
            print(f"Error loading token.json: {e}. Re-authenticating...")
            creds = None

    # If there are no (valid) credentials available, let the user log in.
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
        
        # Save the credentials for the next run
        try:
            with open(GDRIVE_TOKEN_FILE, 'w') as token:
                token.write(creds.to_json())
        except Exception as e:
            print(f"Error saving token file: {e}")

    # Build and return the service object
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
    """
    Finds the ID of a Google Drive folder by its name.
    
    Args:
        service: The authenticated Google Drive service object.
        folder_name (str): The exact name of the folder to find.

    Returns:
        str | None: The folder ID if found, otherwise None.
    """
    if not service:
        print("Service object is not valid.")
        return None
        
    try:
        query = f"mimeType='application/vnd.google-apps.folder' and name='{folder_name}' and trashed=false"
        results = service.files().list(
            q=query,
            pageSize=1,
            fields="files(id, name)"
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
    """
    Finds the ID of a Google Drive file by its name.
    
    Args:
        service: The authenticated Google Drive service object.
        file_name (str): The exact name of the file to find.
        in_folder_id (str, optional): The ID of a folder to search within.

    Returns:
        str | None: The file ID if found, otherwise None.
    """
    if not service:
        print("Service object is not valid.")
        return None
        
    try:
        # Base query for file name and not a folder
        query = f"name='{file_name}' and mimeType!='application/vnd.google-apps.folder' and trashed=false"
        
        # Add folder condition if provided
        if in_folder_id:
            query += f" and '{in_folder_id}' in parents"
            
        results = service.files().list(
            q=query,
            pageSize=1,
            fields="files(id, name)"
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

    Args:
        service: The authenticated Google Drive service object.
        local_filepath (Path): The pathlib.Path object of the local file to upload.
        gdrive_folder_id (str, optional): The ID of the Drive folder to upload into.
                                          If None, uploads to root "My Drive".
        gdrive_filename (str, optional): The name to save the file as in Google Drive.
                                         If None, uses the local file's name.
    
    Returns:
        str | None: The new Google Drive file ID if successful, otherwise None.
    """
    if not service:
        print("Service object is not valid.")
        return None
    
    if not local_filepath.exists():
        print(f"Error: Local file not found at '{local_filepath}'")
        return None
        
    try:
        # Set filename in Google Drive
        if gdrive_filename is None:
            gdrive_filename = local_filepath.name

        file_metadata = {'name': gdrive_filename}
        
        # Set parent folder if provided
        if gdrive_folder_id:
            file_metadata['parents'] = [gdrive_for_id]

        # Create the media upload object
        media = MediaFileUpload(local_filepath, resumable=True)
        
        # Create the file and upload
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
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


def download_file(service, gdrive_file_id: str, local_save_path: Path):
    """
    Downloads a file from Google Drive.

    Args:
        service: The authenticated Google Drive service object.
        gdrive_file_id (str): The ID of the file to download.
        local_save_path (Path): The full local path (incl. filename) to save the file.
    """
    if not service:
        print("Service object is not valid.")
        return
        
    try:
        # Ensure the parent directory for the save path exists
        local_save_path.parent.mkdir(parents=True, exist_ok=True)

        request = service.files().get_media(fileId=gdrive_file_id)
        
        # Use io.BytesIO to hold the file in memory
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        
        done = False
        print(f"Starting download for file ID: {gdrive_file_id}...")
        while done is False:
            status, done = downloader.next_chunk()
            print(f"Download {int(status.progress() * 100)}%.")
            
        # Once done, write the in-memory file to disk
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
    # 1. Authenticate
    drive_service = get_drive_service()
    
    if drive_service:
        print("\n" + "="*50)
        print("--- TEST 1: LISTING FILES ---")
        print("="*50)
        list_drive_files(drive_service, 5) # Test the list function

        # --- UPLOAD/DOWNLOAD TEST ---
        # We will create a dummy test file, upload it, then download it
        # to your OS's Downloads folder.
        
        print("\n" + "="*50)
        print("--- TEST 2: UPLOAD & DOWNLOAD ---")
        print("="*50)
        
        # 2. Define test file paths
        test_file_name = "gdrive_api_test.txt"
        local_upload_path = PROJECT_ROOT / test_file_name
        local_download_path = user_download_folder() / f"downloaded_{test_file_name}"
        
        # 3. Create a local dummy file
        try:
            print(f"Creating local test file at: {local_upload_path}")
            with open(local_upload_path, 'w') as f:
                f.write("Hello from the GDrive API script!\n")
                f.write(f"Timestamp: {dt.datetime.now()}")
            
            # 4. Upload the file (to root 'My Drive')
            print("\nAttempting to upload file...")
            uploaded_file_id = upload_file(drive_service, local_upload_path)
            
            if uploaded_file_id:
                
                # 5. Download the file
                print("\nAttempting to download the file...")
                download_file(drive_service, uploaded_file_id, local_download_path)
                
                # 6. Clean up (optional: delete the test file from Drive)
                try:
                    print(f"\nCleaning up: Deleting '{test_file_name}' from Google Drive.")
                    drive_service.files().delete(fileId=uploaded_file_id).execute()
                    print("Cleanup successful.")
                except HttpError as e:
                    print(f"Error cleaning up file: {e}")

            # 7. Clean up local test file
            if local_upload_path.exists():
                print(f"Cleaning up: Deleting local file '{local_upload_path}'")
                os.remove(local_upload_path)
            
            print("\n" + "="*50)
            print("--- TEST COMPLETE ---")
            print("="*50)
            print(f"Check your Downloads folder for '{local_download_path.name}'!")

        except Exception as e:
            print(f"An error occurred during the upload/download test: {e}")
            # Clean up local file if it exists
            if local_upload_path.exists():
                os.remove(local_upload_path)