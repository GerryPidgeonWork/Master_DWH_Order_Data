# ====================================================================================================
# P04_static_lists.py
# ----------------------------------------------------------------------------------------------------
# Central repository for static reference data, constants, and lookup dictionaries.
#
# Purpose:
#   - Store shared, unchanging data used across multiple project modules.
#   - Provide a single import location for mappings, code lists, and enumerations.
#   - Keep static data separate from logic to simplify maintenance and updates.
#
# Typical Contents (to be added as needed):
#   - Column rename maps (e.g., DWH_COLUMN_RENAME_MAP, JET_COLUMN_RENAME_MAP)
#   - Fixed dropdown values or menu options for GUIs
#   - Country or currency codes
#   - File type or status enumerations
#   - Error message templates or constants
#
# Usage:
#   from processes.P04_static_lists import DWH_COLUMN_RENAME_MAP
#
# Example:
#   >>> from processes.P04_static_lists import COUNTRY_CODES
#   >>> COUNTRY_CODES["DE"]
#   'Germany'
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
