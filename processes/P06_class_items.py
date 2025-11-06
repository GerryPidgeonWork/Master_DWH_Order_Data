# ====================================================================================================
# P06_class_items.py
# ----------------------------------------------------------------------------------------------------
# Purpose:
#   This is the MAIN APPLICATION window.
#   It is launched by the 'P05' Connection Launcher.
#   It receives the live connection objects (Snowflake, GDrive) and
#   contains the actual logic for the application (e.g., running queries).
# ----------------------------------------------------------------------------------------------------
# Author:       Gerry Pidgeon
# Created:      2025-11-06
# Project:      Python Boilerplate
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
# 3. MAIN APPLICATION WINDOW CLASS
# ----------------------------------------------------------------------------------------------------
class MainApplicationWindow(tk.Toplevel):
    """
    This is the main application window.
    It runs *after* the P05 launcher window.
    """
    def __init__(self, parent, snowflake_conn, gdrive_service, upload_method, local_path):
        super().__init__(parent)
        
        print("MainApplicationWindow: __init__ started.")
        
        # --- Store the connection objects ---
        self.parent = parent
        self.sf_conn = snowflake_conn
        self.gdrive_service = gdrive_service
        self.upload_method = upload_method
        self.local_path = local_path
        
        # --- Window Setup ---
        self.title("Main Application")
        self.geometry("500x300")
        
        # --- Handle this window being closed ---
        # When user clicks the 'X' on this window,
        # it should close the *entire* app (including the hidden launcher)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # --- Placeholder Widgets to show connections ---
        self.main_frame = ttk.Frame(self, padding=20)
        self.main_frame.pack(expand=True, fill=tk.BOTH)
        
        ttk.Label(self.main_frame, text="Main Application Window", font=("Arial", 16, "bold")).pack(pady=10)
        
        # Display Snowflake status
        sf_status = "✅ Connected" if self.sf_conn else "❌ Not Connected"
        ttk.Label(self.main_frame, text=f"Snowflake Connection: {sf_status}").pack(anchor=tk.W)
        
        # Display GDrive status
        if self.upload_method == 'api':
            gdrive_status = "✅ Connected" if self.gdrive_service else "❌ Not Connected"
            ttk.Label(self.main_frame, text=f"Google Drive Method: API").pack(anchor=tk.W)
            ttk.Label(self.main_frame, text=f"Google Drive Status: {gdrive_status}").pack(anchor=tk.W)
        else: # 'local'
            ttk.Label(self.main_frame, text=f"Google Drive Method: Local").pack(anchor=tk.W)
            ttk.Label(self.main_frame, text=f"Local Path: {self.local_path}").pack(anchor=tk.W)
            
        # --- TODO: Add your main app widgets here ---
        # (e.g., Query box, Run button, Export button)
        ttk.Label(self.main_frame, text="\nThis is where the real application logic goes.",
                  font=("Arial", 10, "italic")).pack(pady=20)


    def on_close(self):
        """Called when the user clicks the 'X' on this window."""
        print("MainApplicationWindow: Closing...")
        
        # Close the Snowflake connection cleanly
        if self.sf_conn:
            try:
                self.sf_conn.close()
                print("Snowflake connection closed.")
            except Exception as e:
                print(f"Error closing Snowflake connection: {e}")
        
        # Destroy the parent (the hidden launcher window),
        # which will terminate the entire application (mainloop)
        self.parent.destroy()


# ====================================================================================================
# 4. MAIN EXECUTION
# ----------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    """
    This script is not intended to be run directly.
    It should be launched by 'P05_gui_elements.py'.
    
    Running this file directly will fail, as it expects connection
    objects to be passed to its __init__ method.
    """
    print("This is the main application module (P06_class_items.py).")
    print("It is not intended to be run directly.")
    print("\nPlease run 'P05_gui_elements.py' to start the application.")