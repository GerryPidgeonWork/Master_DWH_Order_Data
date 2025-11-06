# ====================================================================================================
# P10_user_config_TEMPLATE.py
# ----------------------------------------------------------------------------------------------------
# *** THIS IS A TEMPLATE ***
#
# PURPOSE:
#   This file is a template for your local configuration.
#
# INSTRUCTIONS:
#   1. RENAME this file to: P10_user_config.py
#   2. Fill in the email slots below with your team's common emails.
#   3. Leave any unused slots as empty strings ("").
#
#   (The GUI will automatically create radio buttons for any slot that is filled in.)
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
# 2. USER CONFIGURATION
# ----------------------------------------------------------------------------------------------------
# Define your team's preset emails here.
# ====================================================================================================

# --- REQUIRED: Fill in at least one email ---
EMAIL_SLOT_1 = "firstname.lastname@gopuff.com"
EMAIL_SLOT_2 = ""
EMAIL_SLOT_3 = ""
EMAIL_SLOT_4 = ""
EMAIL_SLOT_5 = ""