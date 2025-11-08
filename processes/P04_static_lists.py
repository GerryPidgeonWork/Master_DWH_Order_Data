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

# ----------------------------------------------------------------------------------------------------
# FINAL_DF_ORDER
# ----------------------------------------------------------------------------------------------------
# Defines the canonical column order for the final combined DataFrame
# produced by M01_run_order_level.py (after joining order- and item-level data).
#
# This ensures:
#   • Consistent CSV exports across providers (Braintree, Uber, Deliveroo, etc.)
#   • Logical column grouping: identifiers → timestamps → financials → item metrics.
#   • Simplified downstream processing and validation.
#
# Note:
#   - All names are lowercase, following normalize_columns() output.
#   - The list length and order must align with the SELECT statements in the SQL templates.
# ----------------------------------------------------------------------------------------------------

FINAL_DF_ORDER = [
    # ---- Identifiers ----
    'gp_order_id', 'gp_order_id_obfuscated', 'mp_order_id',
    'payment_system', 'braintree_tx_index', 'braintree_tx_id',
    'location_name', 'order_vendor', 'vendor_group',

    # ---- Status and timestamps ----
    'order_completed', 'created_at_timestamp', 'delivered_at_timestamp',
    'created_at_day', 'created_at_week', 'created_at_month',
    'delivered_at_day', 'delivered_at_week', 'delivered_at_month',
    'ops_date_day', 'ops_date_week', 'ops_date_month',

    # ---- Financials: VAT and Revenue ----
    'blended_vat_rate', 'post_promo_sales_inc_vat',
    'delivery_fee_inc_vat', 'priority_fee_inc_vat',
    'small_order_fee_inc_vat', 'mp_bag_fee_inc_vat',
    'total_payment_inc_vat', 'tips_amount',
    'total_payment_with_tips_inc_vat',

    'post_promo_sales_exc_vat', 'delivery_fee_exc_vat',
    'priority_fee_exc_vat', 'small_order_fee_exc_vat',
    'mp_bag_fee_exc_vat', 'total_revenue_exc_vat',
    'cost_of_goods_inc_vat', 'cost_of_goods_exc_vat',

    # ---- Alternate metrics (for validation/reconciliation) ----
    'alt_post_promo_sales_inc_vat', 'alt_delivery_fee_exc_vat',
    'alt_priority_fee_exc_vat', 'alt_small_order_fee_exc_vat',
    'alt_total_payment_with_tips_inc_vat',

    # ---- Item-level breakdown ----
    'total_products',
    'item_quantity_count_0', 'item_quantity_count_5', 'item_quantity_count_20',
    'total_price_exc_vat_0', 'total_price_exc_vat_5', 'total_price_exc_vat_20',
    'total_price_inc_vat_0', 'total_price_inc_vat_5', 'total_price_inc_vat_20'
]
