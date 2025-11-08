# ====================================================================================================
# P07_module_configs.py
# ----------------------------------------------------------------------------------------------------
# Central configuration hub for project-level constants, parameters, and reference dictionaries.
#
# Purpose:
#   - Define configurable settings, mappings, and enumerations that influence application behaviour.
#   - Provide a single import location for constants used across multiple modules.
#   - Separate static configuration from logic to make maintenance, updates, and reuse easier.
#
# Typical Contents (to be added as needed):
#   - Default GUI parameters (window sizes, colour themes, button text)
#   - Snowflake or API environment settings (role, warehouse, schema defaults)
#   - File handling constants (naming templates, allowed extensions, folder mappings)
#   - Lookup dictionaries for providers, statuses, or processing modes
#   - Application version info, author metadata, and timestamps
#
# Usage:
#   from processes.P07_module_configs import REPORTING_START_DATE, REPORTING_END_DATE
#
# Example:
#   >>> from processes.P07_module_configs import REPORTING_START_DATE
#   >>> print(REPORTING_START_DATE)
#
# ----------------------------------------------------------------------------------------------------
# Author:       Gerry Pidgeon
# Created:      2025-11-07
# Project:      DWHOrdersToCash (BoilerplateOrdersToCash v1.1)
# ====================================================================================================


# ====================================================================================================
# 1. SYSTEM IMPORTS
# ----------------------------------------------------------------------------------------------------
import sys
from pathlib import Path

# --- Standard boilerplate block ---
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.dont_write_bytecode = True  # Prevents __pycache__ folders from being created


# ====================================================================================================
# 2. PROJECT IMPORTS
# ----------------------------------------------------------------------------------------------------
from processes.P00_set_packages import *  # Imports all packages from P00_set_packages.py


# ====================================================================================================
# 3. DYNAMIC RUNTIME VARIABLES (SET BY GUI)
# ----------------------------------------------------------------------------------------------------
# These variables are dynamically set by the DWH Orders-to-Cash GUI before executing the main process.
# Integration:
#   - I02_gui_elements_main.py sets the reporting period values when the user starts the extraction.
#   - I03_combine_sql.py reads these values when constructing SQL query parameters.
# ----------------------------------------------------------------------------------------------------
REPORTING_START_DATE = ""
REPORTING_END_DATE = ""
