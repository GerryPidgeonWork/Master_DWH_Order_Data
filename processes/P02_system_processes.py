# ====================================================================================================
# P02_system_processes.py
# ----------------------------------------------------------------------------------------------------
# Provides environment detection and user folder resolution utilities.
#
# Purpose:
#   - Detect the user's operating environment (Windows, macOS, WSL, Linux, or iOS).
#   - Dynamically determine the correct default Downloads folder for file operations.
#   - Support cross-platform compatibility (Windows native, WSL, Mac, Linux).
#
# Usage:
#   from processes.P02_system_processes import detect_os, user_download_folder
#
# Example:
#   >>> detect_os()
#   'Windows (WSL)'
#   >>> user_download_folder()
#   WindowsPath('C:/Users/username/Downloads')
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
# 3. OPERATING SYSTEM DETECTION
# ----------------------------------------------------------------------------------------------------
# Identify which OS or subsystem Python is currently running on.
# Supports Windows, macOS, Linux, WSL, and iOS.
# ====================================================================================================

def detect_os() -> str:
    """
    Detect the current operating system or environment.

    Returns:
        str:
            One of the following labels:
            - "Windows"         : Running under native Windows Python.
            - "Windows (WSL)"   : Running under Windows Subsystem for Linux.
            - "macOS"           : Running under macOS (Darwin kernel).
            - "Linux"           : Running under standalone Linux.
            - "iOS"             : Running under Python on iOS (Pythonista, Pyto, etc.).
            - Otherwise, returns sys.platform for unknown systems.
    """
    # --- 1) Native Windows ---
    if sys.platform == "win32":
        return "Windows"

    # --- 2) macOS or iOS (Darwin kernel) ---
    if sys.platform == "darwin":
        import platform
        machine = platform.machine() or ""
        # iOS devices often report names beginning with "iP" (iPhone, iPad)
        if machine.startswith(("iP",)):
            return "iOS"
        return "macOS"

    # --- 3) Linux and WSL ---
    if sys.platform.startswith("linux"):
        import platform
        release = platform.uname().release.lower()
        # WSL identifiers appear in kernel release strings
        if "microsoft" in release or "wsl" in release:
            return "Windows (WSL)"
        return "Linux"

    # --- 4) Fallback for unrecognised systems ---
    return sys.platform


# ====================================================================================================
# 4. USER DOWNLOAD FOLDER DETECTION
# ----------------------------------------------------------------------------------------------------
# Determines the correct "Downloads" folder depending on OS type.
# ====================================================================================================

def user_download_folder() -> Path:
    """
    Return the current user's Downloads folder path depending on the OS.

    Returns:
        Path: A `pathlib.Path` object pointing to the user's Downloads directory.
    """
    os_type = detect_os()
    home = Path.home()

    # --- Windows native ---
    if os_type == "Windows":
        # This is the most reliable way on Windows
        return home / "Downloads"

    # --- Windows Subsystem for Linux (WSL) ---
    elif os_type == "Windows (WSL)":
        # Try to find the *Windows* Downloads folder from within WSL
        # This path is typically /mnt/c/Users/<username>/Downloads
        try:
            # We need to get the Windows username.
            # We can't use getpass.getuser() as that returns the *Linux* username.
            # A common (but not 100% foolproof) way is to check the /mnt/c/Users dir
            # and find a folder that matches the Linux user, or just grab the main one.
            # A more robust way is to read the wsl.conf, but that's too complex.
            #
            # Let's try a simpler, more direct approach: check common mount points.
            
            # 1. Get Linux username
            linux_user = getpass.getuser()
            
            # 2. Check for a windows path at /mnt/c/Users/<linux_user>/Downloads
            win_path_guess = Path(f"/mnt/c/Users/{linux_user}/Downloads")
            if win_path_guess.exists():
                return win_path_guess
            
            # 3. If that fails, fall back to the Linux home Downloads
            # This is /home/<linux_user>/Downloads
            wsl_linux_downloads = home / "Downloads"
            wsl_linux_downloads.mkdir(exist_ok=True) # Ensure it exists
            return wsl_linux_downloads

        except Exception:
            # If any error, fall back to the safe Linux home/Downloads
            return home / "Downloads"

    # --- macOS ---
    elif os_type == "macOS":
        return home / "Downloads"

    # --- Linux ---
    elif os_type == "Linux":
        return home / "Downloads"

    # --- iOS ---
    elif os_type == "iOS":
        # iOS doesn't expose a real "Downloads" directory to Python apps
        return home  # The app's sandboxed document root

    # --- Fallback (safe default) ---
    else:
        return home


# ====================================================================================================
# 5. MAIN EXECUTION (STANDALONE TEST)
# ----------------------------------------------------------------------------------------------------
# Allows the module to be run directly to verify OS detection.
# ====================================================================================================
if __name__ == "__main__":
    print(f"Detected OS: {detect_os()}")
    print(f"Download folder: {user_download_folder()}")