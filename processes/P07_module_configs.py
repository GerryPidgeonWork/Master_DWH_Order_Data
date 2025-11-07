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
#   from processes.P07_module_configs import DEFAULT_WAREHOUSE, FILE_NAMING_RULES
#
# Example:
#   >>> from processes.P07_module_configs import SUPPORTED_PROVIDERS
#   >>> SUPPORTED_PROVIDERS["justeat"]
#   'Just Eat Orders-to-Cash'
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
from processes.P00_set_packages import *  # Imports all packages from P00_set_packages.py
