# ====================================================================================================
# P00_set_packages.py
# ----------------------------------------------------------------------------------------------------
# Centralises all package imports for the project.
#
# Purpose:
#   - Provide a single file to manage all external and standard library imports.
#   - Simplify other modules, which can just import * from this file.
#   - List all project dependencies in one place.
#
# Usage:
#   from processes.P00_set_packages import *
#
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
# 2. STANDARD LIBRARY IMPORTS
# ----------------------------------------------------------------------------------------------------
# Import common Python standard libraries used across the project.
# ====================================================================================================
import os                                                                   # Interact with the operating system (file paths, env variables)
import io                                                                   # Handle in-memory byte streams (for API file up/downloads)
import getpass                                                              # Get user information like username (used in P02)
import platform                                                             # Get OS-specific identifiers (release, machine type)
import re                                                                   # Regular expressions for pattern matching
import sys                                                                  # Access system-specific parameters, e.g., sys.path
import csv                                                                  # Read/write CSV files natively
import time                                                                 # Time utilities (sleep, timestamps, timing performance)
import json                                                                 # Read/write JSON files for configs or structured data
import glob                                                                 # Pattern-based file searches (e.g., *.csv, *.py)
import shutil                                                               # File operations: copy, move, delete
import logging                                                              # Standard logging for info/warning/error tracking
import threading                                                            # Run lightweight concurrent tasks
import contextlib                                                           # Manage temporary context scopes (e.g., redirect_stdout)
import datetime as dt                                                       # Shortcut alias for datetime module (used as dt.date / dt.datetime)
import calendar                                                             # Calendar operations (e.g., month ranges, weekday checks)
from typing import Dict, List, Tuple, Optional, Any                         # Standard type hints used across the project

# --- GUI-SPECIFIC IMPORTS ---
import tkinter as tk                                                        # Standard Python GUI toolkit
from tkinter import ttk                                                     # Themed, modern widgets for the GUI
from tkinter import messagebox                                              # Standard GUI popup dialogs (for errors)
from tkinter import font as tkFont                                          # To create custom fonts
from tkinter import filedialog                                              # Standard open/save file dialogs
import queue                                                                # Thread-safe queue for GUI <-> thread communication


# ====================================================================================================
# 3. GOOGLE API & OAUTH IMPORTS
# ----------------------------------------------------------------------------------------------------
# (pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib)
# Imports for Google API authentication and service building.
# ====================================================================================================
from google.auth.transport.requests import Request                          # Handles OAuth 2.0 transport and token refresh requests
from google.oauth2.credentials import Credentials                           # Manages OAuth 2.0 access and refresh tokens
from google_auth_oauthlib.flow import InstalledAppFlow                      # Manages the OAuth 2.0 flow for desktop apps
from googleapiclient.discovery import build                                 # Builds the API service object (the "resource")
from googleapiclient.errors import HttpError                                # Standard error handling for API calls
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload       # Handles media (file) upload and download


# ====================================================================================================
# 4. OTHER THIRD-PARTY IMPORTS
# ----------------------------------------------------------------------------------------------------
import pandas as pd                                                         # (pip install pandas) Data analysis and manipulation
import numpy as np                                                          # (installed with pandas) Numerical arrays, fast math ops
import snowflake.connector                                                  # (pip install snowflake-connector-python) Run SQL in Snowflake

# ====================================================================================================
# 5. LOGGING CONFIGURATION
# ----------------------------------------------------------------------------------------------------
# Provides a consistent logging setup for all modules in the project.
# Each time the boilerplate is imported, it ensures the logs directory exists
# and that logging writes both to file and console with a standard format.
# ====================================================================================================

# Define log directory (relative to project root)
LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Define log file name (timestamped daily)
LOG_FILE = LOG_DIR / f"{dt.datetime.now():%Y-%m-%d}.log"

# Define a common log format
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(threadName)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Configure root logger
logging.basicConfig(
    level=logging.INFO,                     # Default level (can override per module)
    format=LOG_FORMAT,
    datefmt=DATE_FORMAT,
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)