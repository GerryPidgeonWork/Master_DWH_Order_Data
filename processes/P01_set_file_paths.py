# ====================================================================================================
# P01_set_file_paths.py
# ----------------------------------------------------------------------------------------------------
# Centralises all key file and directory paths for the project.
#
# Purpose:
#   - Define a single source of truth for the project's root directory.
#   - Build paths for data, credentials, and other key resources.
#   - Allow other modules to import paths without hardcoding.
#
# Usage:
#   from processes.P01_set_file_paths import PROJECT_ROOT, DATA_DIR, CREDENTIALS_DIR
#
# Example:
#   >>> print(PROJECT_ROOT)
#   /Users/username/Just-Eat-Project
#   >>> print(GDRIVE_CREDENTIALS_FILE)
#   /Users/username/Just-Eat-Project/credentials/credentials.json
#
# ----------------------------------------------------------------------------------------------------
# Author:       Gerry Pidgeon
# Created:      2025-11-05
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


# ====================================================================================================
# 3. PROJECT ROOT
# ----------------------------------------------------------------------------------------------------
# This block defines the 'PROJECT_ROOT' variable for this module and for
# any other module that needs to import it (e.g., P02, P09).
# ====================================================================================================
try:
    # .parent is /.../Just-Eat-Project/processes/
    # .parent.parent is /.../Just-Eat-Project/
    PROJECT_ROOT = Path(__file__).resolve().parent.parent
except NameError:
    # Fallback for interactive environments where __file__ isn't defined
    PROJECT_ROOT = Path.cwd()


# ====================================================================================================
# 4. CORE DIRECTORIES
# ----------------------------------------------------------------------------------------------------
PROCESSES_DIR = PROJECT_ROOT / "processes"
DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = PROJECT_ROOT / "logs"
CREDENTIALS_DIR = PROJECT_ROOT / "credentials"  # A dedicated folder is safer

# --- Ensure key directories exist ---
DATA_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)
CREDENTIALS_DIR.mkdir(parents=True, exist_ok=True)

# ====================================================================================================
# 5. GOOGLE DRIVE API FILES
# ----------------------------------------------------------------------------------------------------
# Paths for the Google Drive API credentials.
# P09_gdrive_api.py will look for these files here.
#
# *** IMPORTANT ***
# 1. Go to Google Cloud Console and download your 'credentials.json'.
# 2. Save it in the 'credentials' folder (created by this script).
#    Full path will be: /.../Just-Eat-Project/credentials/credentials.json
#
# 3. 'token.json' will be created in the same folder after you log in the first time.
# ====================================================================================================
GDRIVE_CREDENTIALS_FILE = CREDENTIALS_DIR / "credentials.json"
GDRIVE_TOKEN_FILE = CREDENTIALS_DIR / "token.json"

# =================================D===================================================================
# 6. MAIN EXECUTION (STANDALONE TEST)
# ----------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    print(f"Project Root: {PROJECT_ROOT}")
    print(f"Processes Dir: {PROCESSES_DIR}")
    print(f"Data Dir: {DATA_DIR}")
    print(f"Logs Dir: {LOGS_DIR}")
    print(f"Credentials Dir: {CREDENTIALS_DIR}")
    print(f"G-Drive Credentials: {GDRIVE_CREDENTIALS_FILE}")
    print(f"G-Drive Token: {GDRIVE_TOKEN_FILE}")