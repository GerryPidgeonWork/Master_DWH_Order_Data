# ====================================================================================================
# P03_shared_functions.py
# ----------------------------------------------------------------------------------------------------
# Provides common reusable helper functions used across multiple project modules.
#
# Purpose:
#   - Centralise frequently used logic (file handling, timestamp formatting, data validation, etc.)
#   - Avoid duplication by keeping shared functions in one consistent location.
#   - Ensure consistent logging, formatting, and error handling across projects.
#
# Typical Functions (to be added as needed):
#   - File utilities (e.g., safe file move/copy, timestamped filenames, CSV/JSON readers)
#   - Date/time helpers (e.g., get_timestamp(), current_week_range())
#   - Validation helpers (e.g., is_valid_email(), clean_string())
#   - GUI-safe wrappers for threading or file dialogs
#
# Usage:
#   from processes.P03_shared_functions import <function_name>
#
# Example:
#   >>> from processes.P03_shared_functions import get_timestamp
#   >>> get_timestamp()
#   '2025-11-07_143512'
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
def read_sql_clean(conn, sql_query: str) -> pd.DataFrame:
    """
    Execute an SQL query using a given Snowflake connection, suppressing console output,
    and returning a DataFrame with normalized column names.

    Steps performed:
        1. Executes the SQL query via pandas.read_sql().
        2. Silences any driver-level stdout/stderr output (for cleaner logs).
        3. Applies normalize_columns() to ensure column consistency.

    Args:
        conn: Active database connection (e.g. Snowflake connector).
        sql_query (str): Fully-formed SQL query string to execute.

    Returns:
        pd.DataFrame: Query results with standardized column naming.

    Example:
        >>> df_orders = read_sql_clean(conn, "SELECT * FROM core.orders LIMIT 5")
        >>> df_orders.head()
    """
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        df = pd.read_sql(sql_query, conn)
    return normalize_columns(df)