# ====================================================================================================
# P08_snowflake_connector.py
# ----------------------------------------------------------------------------------------------------
# Purpose:
#   Provides a simplified and multi-user-friendly connection layer to Snowflake via Okta SSO.
#   This boilerplate is pre-configured for the Gopuff Snowflake environment.
#
# Features:
#   • Hardcoded for Gopuff Account and Email Domain (non-secret).
#   • Accepts a user email from the GUI.
#   • Automatically finds and sets the best available Role/Warehouse.
#
# ----------------------------------------------------------------------------------------------------
# Usage (example):
#   from processes.P08_snowflake_connector import connect_to_snowflake
#
#   user_email = "user.name@gopuff.com"   # Retrieved from GUI input
#   conn = connect_to_snowflake(email_address=user_email)
#
# ----------------------------------------------------------------------------------------------------
# Author:       Gerry Pidgeon
# Created:      2025-11-07
# Project:      GP Boilerplate
# ====================================================================================================


# ====================================================================================================
# 1. SYSTEM IMPORTS
# ----------------------------------------------------------------------------------------------------
import sys
from pathlib import Path

# --- Standard block for all modules ---
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.dont_write_bytecode = True  # Prevents __pycache__ folders from being created


# ====================================================================================================
# 2. PROJECT IMPORTS
# ----------------------------------------------------------------------------------------------------
from processes.P00_set_packages import *  # Imports all packages from P00_set_packages.py

# NOTE: The GUI handles user configuration (P10_user_config.py). It is not imported here.


# ====================================================================================================
# 3. DEFAULT SNOWFLAKE CONFIGURATION
# ----------------------------------------------------------------------------------------------------
# Configuration for the Gopuff Snowflake account and Okta SSO authentication.
# These are non-secret identifiers and safe for GitHub storage.
# ====================================================================================================

SNOWFLAKE_ACCOUNT = "HC77929-GOPUFF"
SNOWFLAKE_EMAIL_DOMAIN = "gopuff.com"

CONTEXT_PRIORITY = [
    {"role": "OKTA_ANALYTICS_ROLE", "warehouse": "ANALYTICS"},
    {"role": "OKTA_READER_ROLE",    "warehouse": "READER_WH"},
]

DEFAULT_DATABASE = "DBT_PROD"
DEFAULT_SCHEMA = "CORE"
AUTHENTICATOR = "externalbrowser"
TIMEOUT_SECONDS = 20


# ====================================================================================================
# 4. BUILD SNOWFLAKE CREDENTIALS
# ----------------------------------------------------------------------------------------------------
def _get_snowflake_credentials(email_address: str):
    """
    (Internal)
    Validate the provided email and return a credentials dictionary
    suitable for Okta SSO authentication via the external browser method.
    """
    if not email_address or "@" not in email_address:
        print(f"❌ Invalid email provided: '{email_address}'.")
        return None

    if not email_address.endswith(f"@{SNOWFLAKE_EMAIL_DOMAIN}"):
        print(f"❌ CRITICAL ERROR: Email '{email_address}' does not match domain '{SNOWFLAKE_EMAIL_DOMAIN}'.")
        return None

    os.environ["SNOWFLAKE_USER"] = email_address
    print(f"\n📧 Using email: {email_address}\n")

    return {
        "user": email_address,
        "account": SNOWFLAKE_ACCOUNT,
        "authenticator": AUTHENTICATOR,
    }


# ====================================================================================================
# 5. SET SNOWFLAKE CONTEXT (ROLE, WAREHOUSE, DATABASE, SCHEMA)
# ----------------------------------------------------------------------------------------------------
def _set_snowflake_context(conn, role: str, warehouse: str,
                           database: str = DEFAULT_DATABASE,
                           schema: str = DEFAULT_SCHEMA):
    """
    (Internal)
    Set the Snowflake session context for the active connection.

    Returns:
        bool: True on success, False on failure.
    """
    print(f"\nAttempting to set context with Role={role}, Warehouse={warehouse}...")
    cur = conn.cursor()
    try:
        cur.execute(f"USE ROLE {role};")
        cur.execute(f"USE WAREHOUSE {warehouse};")
        cur.execute(f"USE DATABASE {database};")
        cur.execute(f"USE SCHEMA {schema};")
    except Exception as e:
        print(f"\n❌ Error setting context: {e}")
        cur.close()
        return False

    cur.execute("SELECT CURRENT_ROLE(), CURRENT_WAREHOUSE(), CURRENT_DATABASE(), CURRENT_SCHEMA();")
    r, wh, db, sc = cur.fetchone()
    print(f"\n📂 Active Context: Role={r}, Warehouse={wh}, Database={db}, Schema={sc}\n")
    cur.close()
    return True


# ====================================================================================================
# 6. CONNECT TO SNOWFLAKE (PUBLIC FUNCTION)
# ----------------------------------------------------------------------------------------------------
def connect_to_snowflake(email_address: str):
    """
    Establish a Snowflake connection using Okta SSO and automatically set the
    best available Role/Warehouse based on the priority list.

    Args:
        email_address (str): Full user email (e.g. user.name@gopuff.com)

    Returns:
        snowflake.connector.connection.SnowflakeConnection | None
    """
    creds = _get_snowflake_credentials(email_address)
    if not creds:
        return None

    conn_container = {}

    def _connect():
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            try:
                conn = snowflake.connector.connect(**creds)
                conn_container["conn"] = conn
            except Exception as e:
                conn_container["error"] = e

    print("🔄 Attempting Snowflake connection...\n")
    print("Please check your browser to complete Okta authentication.")

    thread = threading.Thread(target=_connect)
    thread.start()
    thread.join(timeout=TIMEOUT_SECONDS)

    if thread.is_alive():
        print(f"⏰ Timeout: No authentication detected after {TIMEOUT_SECONDS} seconds.")
        return None

    if "error" in conn_container:
        err = str(conn_container["error"])
        print(f"❌ Connection failed: {err}")
        if "differs from the user currently logged in" in err:
            print("Tip: Your browser may be logged into a different Okta account.")
            os.environ.pop("SNOWFLAKE_USER", None)
        return None

    if "conn" not in conn_container:
        print("❌ Unknown connection error.")
        return None

    # --- Connection successful ---
    conn = conn_container["conn"]
    print(f"✅ Connected successfully as {creds['user']}\n")
    print("Retrieving available roles and warehouses...")

    try:
        cur = conn.cursor()
        available_roles = {row[1] for row in cur.execute("SHOW ROLES;")}
        available_whs = {row[0] for row in cur.execute("SHOW WAREHOUSES;")}
        cur.close()
    except Exception as e:
        print(f"❌ Error retrieving roles/warehouses: {e}")
        conn.close()
        return None

    for context in CONTEXT_PRIORITY:
        role = context["role"]
        wh = context["warehouse"]
        print(f"Checking for: Role={role}, Warehouse={wh}...")
        if role in available_roles and wh in available_whs:
            print("✅ Found matching context. Setting...")
            if _set_snowflake_context(conn, role, wh):
                return conn
            else:
                print(f"⚠️ Failed to apply context {role}/{wh}. Trying next...")
        else:
            print("Context not available.")

    print("❌ No valid role/warehouse context found.")
    print("Ensure you have access to one of the following pairs:")
    for c in CONTEXT_PRIORITY:
        print(f"  - {c['role']} / {c['warehouse']}")
    conn.close()
    return None


# ====================================================================================================
# 7. STANDALONE TEST
# ----------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    """
    Manual test runner for verifying Snowflake connection and auto-context setup.
    """
    try:
        from processes.P10_user_config import EMAIL_SLOT_1

        if not EMAIL_SLOT_1 or "firstname.lastname" in EMAIL_SLOT_1:
            print("❌ Test Failed: Please set EMAIL_SLOT_1 in 'P10_user_config.py' to run this test.")
            sys.exit(1)

        print(f"--- Running Standalone Test ({EMAIL_SLOT_1}) ---")
        conn = connect_to_snowflake(email_address=EMAIL_SLOT_1)

        if conn:
            print("✅ Connection established successfully.")
            cur = conn.cursor()
            cur.execute("""
                SELECT CURRENT_USER(), CURRENT_ACCOUNT(), CURRENT_ROLE(),
                       CURRENT_WAREHOUSE(), CURRENT_DATABASE(), CURRENT_SCHEMA();
            """)
            result = cur.fetchone()
            print("\n--- Active Session Context ---")
            print(
                f"👤 User: {result[0]}\n"
                f"🏢 Account: {result[1]}\n"
                f"🧩 Role: {result[2]}\n"
                f"🏭 Warehouse: {result[3]}\n"
                f"📚 Database: {result[4]}\n"
                f"📁 Schema: {result[5]}"
            )
            cur.close()
            conn.close()
            print("\n🔒 Connection closed cleanly.")
        else:
            print("❌ Standalone test failed. connect_to_snowflake() returned None.")

    except ImportError:
        print("❌ Test Failed: 'processes/P10_user_config.py' not found.")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n❌ Connection aborted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
