# ====================================================================================================
# I03_combine_sql.py
# ----------------------------------------------------------------------------------------------------
# Executes both SQL queries to produce consolidated DWH export files for all delivery providers.
# ----------------------------------------------------------------------------------------------------
# Integration:
#   - Called by implementation/I02_gui_elements_main.py in a background thread.
#   - Executes SQL scripts:
#         • sql/S01_order_level.sql
#         • sql/S02_item_level.sql
#   - Uses central provider registry & folder structure from processes/P01_set_file_paths.py
#   - Outputs per-provider CSVs into each provider’s /03 DWH folder.
# ----------------------------------------------------------------------------------------------------
# Author:       Gerry Pidgeon
# Created:      2025-11-06
# Project:      DWHOrdersToCash  (BoilerplateOrdersToCash v1.1)
# ====================================================================================================


# ====================================================================================================
# 1. SYSTEM IMPORTS
# ----------------------------------------------------------------------------------------------------
import sys
from pathlib import Path

# --- Standard boilerplate block ---
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.dont_write_bytecode = True


# ====================================================================================================
# 2. PROJECT IMPORTS
# ----------------------------------------------------------------------------------------------------
from processes.P00_set_packages import *     # Core packages
import processes.P07_module_configs as cfg   # Dynamic configuration (dates set by GUI)
from processes.P03_shared_functions import normalize_columns, read_sql_clean
from processes.P04_static_lists import FINAL_DF_ORDER
from processes.P01_set_file_paths import get_folder_across_providers


# ====================================================================================================
# 3. HELPER FUNCTION
# ----------------------------------------------------------------------------------------------------
def get_sql_path(filename: str) -> Path:
    """
    Returns the absolute path to an SQL file, compatible with both Python and PyInstaller builds.
    """
    base_path = getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent)
    sql_path = Path(base_path) / "sql" / filename
    if not sql_path.exists():
        raise FileNotFoundError(f"❌ SQL file not found: {sql_path}")
    return sql_path


# ====================================================================================================
# 4. QUERY EXECUTION
# ----------------------------------------------------------------------------------------------------
def run_order_level_query(conn):
    """Executes the order-level SQL query (S01_order_level.sql) against Snowflake."""
    start_date, end_date = cfg.REPORTING_START_DATE, cfg.REPORTING_END_DATE
    sql_query = (
        get_sql_path("S01_order_level.sql")
        .read_text(encoding="utf-8")
        .replace("{{start_date}}", start_date)
        .replace("{{end_date}}", end_date)
    )

    print(f"⏳ Executing order-level query for {start_date} → {end_date} ...", end="", flush=True)
    t0 = time.time()
    df_orders = read_sql_clean(conn, sql_query)
    print(f"\r✅ Order-level query complete in {time.time() - t0:,.1f}s — {len(df_orders):,} rows.")
    return df_orders


def run_item_level_query(conn, df_orders):
    """Executes the item-level SQL query (S02_item_level.sql) for all gp_order_id values."""
    gp_order_ids = df_orders["gp_order_id"].dropna().unique().tolist()
    if not gp_order_ids:
        raise ValueError("❌ No valid gp_order_id values found in the order-level data.")

    print(f"⏳ Uploading {len(gp_order_ids):,} order IDs to Snowflake ...", end="", flush=True)
    cur = conn.cursor()
    cur.execute("CREATE OR REPLACE TEMP TABLE temp_order_ids (gp_order_id STRING);")

    chunk_size = 25_000
    t0 = time.time()
    for i in range(0, len(gp_order_ids), chunk_size):
        chunk = [(oid,) for oid in gp_order_ids[i:i + chunk_size]]
        cur.executemany("INSERT INTO temp_order_ids (gp_order_id) VALUES (%s);", chunk)
        done = min(i + chunk_size, len(gp_order_ids))
        pct = done / len(gp_order_ids) * 100
        print(f"\r   ⏳ Inserted {done:,}/{len(gp_order_ids):,} IDs ({pct:,.1f} %)", end="", flush=True)
    print(f"\r✅ Uploaded {len(gp_order_ids):,} IDs in {time.time() - t0:,.1f}s — running item-level query ...", end="", flush=True)
    cur.close()

    sql_query = get_sql_path("S02_item_level.sql").read_text(encoding="utf-8")
    sql_query = sql_query.replace("{{order_id_list}}", "SELECT gp_order_id FROM temp_order_ids")

    t1 = time.time()
    df_items = read_sql_clean(conn, sql_query)
    print(f"\n✅ Item-level query complete in {time.time() - t1:,.1f}s — {len(df_items):,} rows.")
    return df_items


# ====================================================================================================
# 5. DATA TRANSFORMATION
# ----------------------------------------------------------------------------------------------------
def transform_item_data(df_orders, df_items):
    """Merge item-level data into order-level dataset and pivot VAT bands horizontally."""
    print("⏳ Starting data transformation and pivot ...")

    df_items["vat_band"] = df_items["vat_band"].replace({
        "0% VAT Band": "0", "5% VAT Band": "5",
        "20% VAT Band": "20", "Other / Unknown VAT Band": "other"
    })

    df_pivot = (
        df_items.pivot_table(
            index="gp_order_id",
            columns="vat_band",
            values=["item_quantity_count", "total_price_inc_vat", "total_price_exc_vat"],
            aggfunc="sum", fill_value=0,
        )
    )
    df_pivot.columns = [f"{metric}_{band}" for metric, band in df_pivot.columns]
    df_pivot["total_products"] = df_pivot.filter(like="item_quantity_count_").sum(axis=1)

    df_final = df_orders.merge(df_pivot, how="left", left_on="gp_order_id", right_index=True)

    # Blank duplicates for multi-transaction orders
    item_cols = [c for c in df_final.columns if any(x in c for x in
                 ["item_quantity_count", "total_price_inc_vat", "total_price_exc_vat", "total_products"])]
    mask = (df_final["braintree_tx_index"].notna()) & (df_final["braintree_tx_index"] >= 2)
    df_final.loc[mask, item_cols] = np.nan

    df_final = df_final.sort_values(by=["gp_order_id", "braintree_tx_index"])
    df_final = df_final[FINAL_DF_ORDER]

    print(f"✅ Combined order + item data: {len(df_final):,} rows, {len(df_final.columns):,} columns.")
    return df_final


# ====================================================================================================
# 6. MAIN ORCHESTRATION FUNCTION
# ----------------------------------------------------------------------------------------------------
def main(conn, local_root_path: str):
    """
    Orchestrates the full DWH export workflow.

    Args:
        conn:              Live Snowflake connection object (from GUI)
        local_root_path:   Root Google Drive / local export folder selected in GUI
    """
    try:
        # 1️⃣  Run queries
        df_orders = run_order_level_query(conn)
        df_items = run_item_level_query(conn, df_orders)

        # 2️⃣  Combine
        df_final = transform_item_data(df_orders, df_items)

        # 3️⃣  Close connection
        conn.close()
        print("\n🔒 Connection closed cleanly.\n")

        # 4️⃣  Determine period label
        start_date = cfg.REPORTING_START_DATE
        period_label = pd.to_datetime(start_date).strftime("%y.%m")

        # 5️⃣  Get cross-provider DWH folders
        provider_paths = get_folder_across_providers("03_dwh")

        # 6️⃣  Simple filter rules per provider
        provider_rules = {
            "braintree": (df_final["vendor_group"].str.lower() == "dtc") &
                         (df_final["payment_system"].str.lower() != "paypal"),
            "paypal":    (df_final["vendor_group"].str.lower() == "dtc") &
                         (df_final["payment_system"].str.lower() == "paypal"),
            "uber":      (df_final["order_vendor"].str.lower() == "uber"),
            "deliveroo": (df_final["order_vendor"].str.lower() == "deliveroo"),
            "justeat":   (df_final["order_vendor"].str.lower().isin(["just eat", "justeat"])),
            "amazon":    (df_final["order_vendor"].str.lower() == "amazon uk"),
        }

        # 7️⃣  Export loop (across providers)
        for provider, path in provider_paths.items():
            if provider not in provider_rules:
                print(f"⚠️ No filter rule defined for {provider}, skipping.")
                continue

            rule = provider_rules[provider]
            df_subset = df_final.loc[rule]

            if df_subset.empty:
                print(f"⚠️ No rows found for {provider.capitalize()}, skipping.")
                continue

            path.mkdir(parents=True, exist_ok=True)
            filename = f"{period_label} - {provider.capitalize()} DWH data.csv"
            file_path = path / filename

            df_subset.to_csv(file_path, index=False)
            print(f"💾 Saved {len(df_subset):,} rows for {provider.capitalize()} → {file_path}")

    except Exception as e:
        if 'conn' in locals() and conn:
            try:
                conn.close()
                print("\n🔒 Connection closed due to error.")
            except:
                pass
        raise e


# ====================================================================================================
# 7. STANDALONE EXECUTION
# ----------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    print("This module is designed to be called by I02_gui_elements_main.py.")
