# ====================================================================================================
# P06_class_items.py
# ----------------------------------------------------------------------------------------------------
# Purpose:
#   This is the MAIN APPLICATION window.
#   It is launched by the 'P05' Connection Launcher after successful setup.
#   It receives the live connection objects (Snowflake, GDrive) and
#   contains the actual logic for the project-specific application.
#
#   Each project can modify or extend this file with its own widgets and logic.
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
from processes.P00_set_packages import *  # Imports all packages from P00_set_packages.py


# ====================================================================================================
# 3. MAIN APPLICATION WINDOW CLASS
# ----------------------------------------------------------------------------------------------------
class MainApplicationWindow(tk.Toplevel):
    """
    This is the main application window, launched after the P05 launcher.
    It holds the project’s functional logic (e.g. queries, file handling, etc.)
    and receives active Snowflake/GDrive connection objects.
    """
    def __init__(self, parent, snowflake_conn=None, gdrive_service=None, upload_method=None, local_path=None):
        super().__init__(parent)

        print("MainApplicationWindow: __init__ started.")

        # --- Store connection references ---
        self.parent = parent
        self.sf_conn = snowflake_conn
        self.gdrive_service = gdrive_service
        self.upload_method = upload_method
        self.local_path = local_path

        # --- Window Setup ---
        self.title("Main Application")
        self.geometry("500x300")
        self.configure(bg="#f7f7f7")

        # --- Handle user closing the window ---
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # --- Main Frame ---
        self.main_frame = ttk.Frame(self, padding=20)
        self.main_frame.pack(expand=True, fill=tk.BOTH)

        ttk.Label(self.main_frame, text="Main Application Window", font=("Arial", 16, "bold")).pack(pady=10)

        # --- Snowflake Connection Status ---
        sf_status = "✅ Connected" if self.sf_conn else "❌ Not Connected"
        ttk.Label(self.main_frame, text=f"Snowflake Connection: {sf_status}").pack(anchor=tk.W)

        # --- Google Drive / Local Folder Info ---
        if self.upload_method == "api":
            gdrive_status = "✅ Connected" if self.gdrive_service else "❌ Not Connected"
            ttk.Label(self.main_frame, text="Google Drive Method: API").pack(anchor=tk.W)
            ttk.Label(self.main_frame, text=f"Google Drive Status: {gdrive_status}").pack(anchor=tk.W)
        else:  # Local mapped drive
            ttk.Label(self.main_frame, text="Google Drive Method: Local").pack(anchor=tk.W)
            ttk.Label(self.main_frame, text=f"Local Path: {self.local_path}").pack(anchor=tk.W)

        # --- Placeholder Area ---
        ttk.Label(
            self.main_frame,
            text="\nThis is where the real application logic and widgets will go.",
            font=("Arial", 10, "italic"),
        ).pack(pady=20)

        # --- Close Button ---
        ttk.Button(self.main_frame, text="Close Application", command=self.on_close, style="Accent.TButton").pack(pady=10)

    # ------------------------------------------------------------------------------------------------
    # EVENT HANDLERS
    # ------------------------------------------------------------------------------------------------
    def on_close(self):
        """Cleanly close all connections and exit the application."""
        print("MainApplicationWindow: Closing...")

        # --- Attempt to close Snowflake connection safely ---
        if self.sf_conn and hasattr(self.sf_conn, "close"):
            try:
                self.sf_conn.close()
                print("Snowflake connection closed successfully.")
            except Exception as e:
                print(f"Error closing Snowflake connection: {e}")

        # --- Destroy launcher (root) and quit Tk ---
        try:
            if self.parent:
                self.parent.destroy()
            self.destroy()
        except Exception as e:
            print(f"Error destroying windows: {e}")

        # --- Exit cleanly to release terminal / console ---
        sys.exit(0)


# ====================================================================================================
# 4. MAIN EXECUTION
# ----------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    """
    This script is not intended to be run directly.
    It should be launched via 'P05a_gui_elements_setup.py',
    which passes the active connection objects into this class.
    """
    print("⚠️  This is the main application module (P06_class_items.py).")
    print("It is not intended to be run directly.")
    print("Please run 'P05a_gui_elements_setup.py' to start the application.")