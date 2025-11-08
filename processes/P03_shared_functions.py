# ====================================================================================================
# P03_shared_functions.py
# ----------------------------------------------------------------------------------------------------
# Provides common reusable helper functions used across multiple project modules.
# ----------------------------------------------------------------------------------------------------
# Purpose:
#   - Centralise frequently used logic (file handling, timestamp formatting, data validation, etc.)
#   - Avoid duplication and ensure consistent conventions across all modules.
# ----------------------------------------------------------------------------------------------------
# Author:       Gerry Pidgeon
# Created:      2025-11-07
# Project:      BoilerplateOrdersToCash (v1.1)
# ====================================================================================================


# ====================================================================================================
# 1. SYSTEM IMPORTS
# ----------------------------------------------------------------------------------------------------
import sys
import io
import re
import time
import shutil
import datetime as dt
import contextlib
from pathlib import Path

# --- Standard import block (ensures cross-module visibility) ---
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.dont_write_bytecode = True


# ====================================================================================================
# 2. PROJECT IMPORTS
# ----------------------------------------------------------------------------------------------------
from processes.P00_set_packages import *  # pandas, numpy, etc.


# ====================================================================================================
# 3. DATAFRAME HELPERS
# ----------------------------------------------------------------------------------------------------
def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardises column names to snake_case (lowercase, underscores instead of spaces or symbols).

    Example:
        'Created At (Local)' -> 'created_at_local'
    """
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(r"[^0-9a-zA-Z]+", "_", regex=True)
        .str.replace(r"__+", "_", regex=True)
        .str.strip("_")
    )
    return df


def read_sql_clean(conn, sql_query: str) -> pd.DataFrame:
    """
    Execute an SQL query using a Snowflake connection and return a cleaned DataFrame.

    Steps performed:
        1. Executes query using pandas.read_sql()
        2. Suppresses driver output (for cleaner logs)
        3. Normalises column names with normalize_columns()

    Args:
        conn: Active database connection (e.g., Snowflake connector)
        sql_query (str): SQL query text

    Returns:
        pd.DataFrame: Query results with normalised column names
    """
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        df = pd.read_sql(sql_query, conn)
    return normalize_columns(df)


# ====================================================================================================
# 4. FILE & PATH UTILITIES
# ----------------------------------------------------------------------------------------------------
def safe_write_csv(df: pd.DataFrame, file_path: Path, index: bool = False) -> None:
    """
    Safely writes a DataFrame to CSV, creating directories if needed.

    Example:
        safe_write_csv(df_orders, Path("outputs/2025-11/orders.csv"))
    """
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(file_path, index=index)
        print(f"💾 Saved file → {file_path}")
    except Exception as e:
        print(f"❌ Failed to write CSV: {e}")
        raise


def safe_move_file(src: Path, dst: Path) -> None:
    """
    Moves a file safely, creating destination folders if required.
    """
    try:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))
        print(f"📂 Moved: {src.name} → {dst}")
    except Exception as e:
        print(f"❌ Move failed for {src}: {e}")


# ====================================================================================================
# 5. DATE/TIME HELPERS
# ----------------------------------------------------------------------------------------------------
def get_timestamp(fmt: str = "%Y-%m-%d_%H%M%S") -> str:
    """
    Returns a formatted timestamp string (default: 2025-11-07_143512).
    """
    return dt.datetime.now().strftime(fmt)


def current_month_range(reference: dt.date | None = None) -> tuple[str, str]:
    """
    Returns start and end dates (YYYY-MM-DD) for the current or given month.
    """
    if reference is None:
        reference = dt.date.today()
    first = reference.replace(day=1)
    last = (first + dt.timedelta(days=32)).replace(day=1) - dt.timedelta(days=1)
    return first.strftime("%Y-%m-%d"), last.strftime("%Y-%m-%d")


# ====================================================================================================
# 6. LOGGING / DISPLAY HELPERS
# ----------------------------------------------------------------------------------------------------
def print_divider(label: str = "", width: int = 90):
    """
    Prints a divider line with optional centered label.
    """
    if label:
        side = (width - len(label) - 2) // 2
        print(f"{'-' * side} {label} {'-' * side}")
    else:
        print("-" * width)


def print_elapsed(start_time: float, label: str = "Operation") -> None:
    """
    Prints the elapsed time for an operation.
    """
    elapsed = time.time() - start_time
    print(f"⏱️  {label} completed in {elapsed:,.2f}s")


# ====================================================================================================
# 7. STANDALONE TEST
# ----------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    print_divider("Shared Function Test")
    print("Timestamp:", get_timestamp())
    print("Month Range:", current_month_range())
