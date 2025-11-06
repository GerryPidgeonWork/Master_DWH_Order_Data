# ====================================================================================================
# M00_run_setup.gui.py
# ----------------------------------------------------------------------------------------------------
# *** MAIN APPLICATION ENTRY POINT ***
#
# Purpose:
#   This is the single, main script to launch the entire application.
#   It sets up the correct system path and then starts the GUI.
# ----------------------------------------------------------------------------------------------------
# Author:       Gerry Pidgeon
# Created:      2025-11-06
# Project:      Python Boilerplate
# ====================================================================================================


# ====================================================================================================
# 1. SYSTEM IMPORTS
# ----------------------------------------------------------------------------------------------------
# Add the parent (root) directory to the system path.
# This allows this script to find and import the 'processes' folder.
# ====================================================================================================
import sys
from pathlib import Path

# __file__ is .../GoogleDriveImplementation/main/M00_run_setup.gui.py
# .parent is .../main
# .parent.parent is .../GoogleDriveImplementation (the project root)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.dont_write_bytecode = True


# ====================================================================================================
# 2. PROJECT IMPORTS
# ----------------------------------------------------------------------------------------------------
# Now that the path is set, we can import the GUI launcher from 'processes'
# ====================================================================================================
from processes.P00_set_packages import * # Imports all packages from P00_set_packages.py
from processes.P05_gui_elements import ConnectionLauncher


# ====================================================================================================
# 3. MAIN EXECUTION
# ----------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    """
    This is the main entry point for the whole app.
    """
    print("Launching Initial Connection Launcher...") # <-- NAME CHANGED HERE
    
    # Create an instance of the launcher app (from P05)
    app = ConnectionLauncher()
    
    # Start the GUI main loop
    app.mainloop()