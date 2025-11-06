# ====================================================================================================
# P08_snowflake_connector.py
# ----------------------------------------------------------------------------------------------------
# Purpose:
#   Provides a simplified and multi-user-friendly connection layer to Snowflake via Okta SSO.
#   This boilerplate is pre-configured for the Gopuff Snowflake environment.
# ----------------------------------------------------------------------------------------------------
# Features:
#   • Hardcoded for Gopuff Account and Email Domain (non-secret).
#   • Accepts a user email from the GUI.
#   • Automatically finds and sets the best available Role/Warehouse.
# ----------------------------------------------------------------------------------------------------
# Usage (in a GUI):
#   from processes.P08_snowflake_connector import connect_to_snowflake
#
#   user_email = "gerry.pidgeon@gopuff.com" # Get this from GUI
#   conn = connect_to_snowflake(email_address=user_email)
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

# NOTE: We no longer import the user config here. The GUI is responsible for it.


# ====================================================================================================
# 3. Default Snowflake Configuration
# ----------------------------------------------------------------------------------------------------
# Configuration for the Gopuff Snowflake account and connection details.
# ====================================================================================================

# --- Gopuff-specific Configuration (Hardcoded, not secrets) ---
SNOWFLAKE_ACCOUNT = "HC77929-GOPUFF"
SNOWFLAKE_EMAIL_DOMAIN = "gopuff.com"

# --- Context Priority List ---
CONTEXT_PRIORITY = [
    {"role": "OKTA_ANALYTICS_ROLE", "warehouse": "ANALYTICS"},
    {"role": "OKTA_READER_ROLE",    "warehouse": "READER_WH"},
]

# --- Fallback defaults for database/schema ---
DEFAULT_DATABASE = "DBT_PROD"
DEFAULT_SCHEMA = "CORE"
AUTHENTICATOR = "externalbrowser"
TIMEOUT_SECONDS = 20


# ====================================================================================================
# 4. get_snowflake_credentials()
# ----------------------------------------------------------------------------------------------------
def _get_snowflake_credentials(email_address: str):
    """(Internal) Builds the credentials dict from the provided email."""
    
    # Simple validation
    if not email_address or "@" not in email_address:
         print(f"❌ CRITICAL ERROR: Invalid email provided: '{email_address}'.")
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
# 5. set_snowflake_context()
# ----------------------------------------------------------------------------------------------------
def _set_snowflake_context(conn, role: str, warehouse: str, 
                           database: str = DEFAULT_DATABASE, 
                           schema: str = DEFAULT_SCHEMA):
    """
    (Internal) Set the Snowflake session context for the active connection.
    Returns True on success, False on failure.
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
# 6. connect_to_snowflake() - (PRIMARY PUBLIC FUNCTION)
# ----------------------------------------------------------------------------------------------------
def connect_to_snowflake(email_address: str):
    """
    Establish a Snowflake connection using Okta SSO and automatically set the
    best available context (Role/Warehouse) based on a priority list.
    
    Args:
        email_address (str): The user's full @gopuff.com email address.
    
    Returns:
        snowflake.connector.connection.SnowflakeConnection:
            An active, context-set Snowflake connection object.
            Returns None if connection or context-setting fails.
    """
    creds = _get_snowflake_credentials(email_address)
    if not creds:
        return None # Error was already printed

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
        print(f"⏰ Timeout: No authentication detected after {TIMEOUT_SECONDS} seconds. Exiting.")
        return None

    if "error" in conn_container:
        err = str(conn_container["error"])
        print(f"\n❌ Connection failed: {err}")
        if "differs from the user currently logged in" in err:
            print("Tip: Your browser may be logged into a different Okta account.")
            os.environ.pop("SNOWFLAKE_USER", None)
        return None
    
    if "conn" not in conn_container:
        print("\n❌ Unknown connection error. Exiting.")
        return None

    # --- Connection Successful, Now Find Context ---
    conn = conn_container["conn"]
    print(f"✅ Connected successfully as {creds['user']}\n")
    print("Finding available roles and warehouses...")
    
    try:
        cur = conn.cursor()
        available_roles = {row[1] for row in cur.execute("SHOW ROLES;")}
        available_warehouses = {row[0] for row in cur.execute("SHOW WAREHOUSES;")}
        cur.close()
    except Exception as e:
        print(f"❌ Error getting roles/warehouses: {e}")
        conn.close()
        return None

    # --- Check Priority List ---
    for context in CONTEXT_PRIORITY:
        role = context["role"]
        wh = context["warehouse"]
        
        print(f"Checking for: Role={role}, Warehouse={wh}...")
        
        if role in available_roles and wh in available_warehouses:
            print(f"✅ Found matching context. Setting...")
            if _set_snowflake_context(conn, role, wh):
                return conn
            else:
                print(f"Failed to apply context {role}/{wh}. Trying next...")
        else:
            print("Context not available.")

    # --- If loop finishes, no context was found/set ---
    print("❌ Critical Error: No valid role/warehouse context found for this user.")
    print("Please ensure you have access to one of the following pairs:")
    for c in CONTEXT_PRIORITY:
        print(f"  - {c['role']} / {c['warehouse']}")
    conn.close()
    return None


# ====================================================================================================
# 7. Standalone test
# ----------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    """
    Manual test runner for verifying the new connection and auto-context flow.
    """
    try:
        # The test will now try to import the config file itself
        from processes.P10_user_config import EMAIL_SLOT_1
        
        if not EMAIL_SLOT_1 or "firstname.lastname" in EMAIL_SLOT_1:
            print("❌ Test Failed: Please set EMAIL_SLOT_1 in 'P10_user_config.py' to run the standalone test.")
            sys.exit(1)
            
        print(f"--- Running Standalone Test (as {EMAIL_SLOT_1}) ---")
        conn = connect_to_snowflake(email_address=EMAIL_SLOT_1)
        
        if conn:
            print("✅ Standalone test successful. Connection established and context set.")
            
            cur = conn.cursor()
            cur.execute("""
                SELECT CURRENT_USER(), CURRENT_ACCOUNT(), CURRENT_ROLE(),
                       CURRENT_WAREHOUSE(), CURRENT_DATABASE(), CURRENT_SCHEMA();
            """)
            result = cur.fetchone()
            print("\n--- Final Session Context ---")
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
        print("This test requires the config file to exist.")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n❌ Connection aborted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        sys.exit(1)