# ====================================================================================================
# P05b_gui_elements_main.py
# ----------------------------------------------------------------------------------------------------
# Placeholder for the project's main GUI window.
#
# Purpose:
#   - Acts as the entry point after successful setup in P05a.
#   - Receives the active Snowflake connection and Google Drive path/service.
#   - Each project will replace this file with its own specific GUI layout.
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
# 2. PROJECT IMPORTS
# ----------------------------------------------------------------------------------------------------
# Bring in standard libraries and settings from the central import hub.
# ====================================================================================================
from processes.P00_set_packages import * # Imports all packages from P00_set_packages.py

# ====================================================================================================
# 2. MAIN GUI
# ----------------------------------------------------------------------------------------------------
# Bring in standard libraries and settings from the central import hub.
# ====================================================================================================

class DWHOrdersToCashGUI(tk.Toplevel):
    """
    Placeholder for the project's main GUI window.
    The final implementation will vary by project.
    """
    def __init__(self, parent, snowflake_conn, gdrive_service, upload_method, local_path):
        super().__init__(parent)
        self.title("Main Application Window (Placeholder)")
        self.geometry("500x300")
        self.configure(bg="#f7f7f7")

        # --- Store received references ---
        self.snowflake_conn = snowflake_conn
        self.gdrive_service = gdrive_service
        self.upload_method = upload_method
        self.local_path = local_path

        # --- Basic UI ---
        ttk.Label(self, text="✅ Setup Complete", font=("Arial", 14, "bold")).pack(pady=10)
        ttk.Label(self, text="This is the placeholder main GUI.", font=("Arial", 10, "italic")).pack(pady=5)
        ttk.Label(self, text=f"Upload Method: {self.upload_method}", font=("Arial", 10)).pack(pady=2)
        ttk.Label(self, text=f"Local Path: {self.local_path}", font=("Arial", 9, "italic")).pack(pady=2)

        # --- Snowflake / GDrive Status ---
        sf_status = "Connected" if self.snowflake_conn else "Not Connected"
        gdrive_status = "Connected" if self.gdrive_service else "Not Connected"
        ttk.Label(self, text=f"Snowflake: {sf_status}", foreground=("green" if self.snowflake_conn else "red")).pack(pady=2)
        ttk.Label(self, text=f"Google Drive: {gdrive_status}", foreground=("green" if self.gdrive_service else "red")).pack(pady=2)

        # --- Close Button ---
        ttk.Button(self, text="Close Application", command=self.quit, style="Accent.TButton").pack(pady=20)
