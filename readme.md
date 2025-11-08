# 🧮 DWH Orders-to-Cash (Built on GP Python Boilerplate v1.1)

A **Data Warehouse Orders-to-Cash extraction and export tool**, built on the **GP Python Boilerplate (Universal GUI Framework)**.

This project connects to **Snowflake (Okta SSO)**, runs optimized SQL scripts to extract **order-level and item-level data**, merges them, and exports **provider-specific CSVs** into your shared Google Drive structure.

It is a **Boilerplate-compliant implementation**, meaning:

* All reusable components remain locked in `/processes`
* All customization lives inside `/implementation`
* It can be cloned or extended easily for new providers (Uber, Deliveroo, PayPal, etc.)

---

## 🌟 Key Features

### 🔍 Data Extraction & Combination

* Executes two Snowflake SQL queries:

  * `S01_order_level.sql`: Order metadata, transactions, and core financials
  * `S02_item_level.sql`: Item-level VAT band details (0%, 5%, 20%)
* Combines both datasets using consistent `gp_order_id` joins
* Outputs a fully normalized, column-aligned DataFrame (`FINAL_DF_ORDER`)

### 📦 Provider-Level Export

* Automatically splits final data by **vendor group and payment system**
* Exports one CSV per provider (Braintree, PayPal, Uber, Deliveroo, Just Eat, Amazon)
* Saves outputs directly to each provider’s `/03 DWH` folder in Google Drive

### 🔐 Authentication & Integration

* **Snowflake Okta SSO** (externalbrowser)
* **Google Drive integration** via mapped drive (default) or API credentials
* Connection setup and authentication handled entirely by the **Universal Launcher**

### 🪟 Unified GUI Workflow

* Reuses the standard **Launcher + Main GUI** flow from the Boilerplate
* Project GUI (`MainProjectGUI`) allows:

  * Month selection and override
  * Display of Snowflake connection status
  * Real-time status logging inside a scrollable output box
* Supports clean multithreaded background execution with safe shutdown

---

## 🧩 Folder & Module Structure

```
DWHOrdersToCash/
│
├── main/
│   ├── M00_run_gui.py               # 🚀 Main entry (launches universal connection GUI)
│   └── M01_load_project_config.py   # Routes to this project’s launcher
│
├── implementation/
│   ├── I01_project_launcher.py      # Imports and launches DWHOrdersToCash Main GUI
│   ├── I02_gui_elements_main.py     # MainProjectGUI — core extraction interface
│   └── I03_combine_sql.py           # Executes SQLs, merges data, exports CSVs
│
├── sql/
│   ├── S01_order_level.sql          # Order-level data from Snowflake
│   └── S02_item_level.sql           # Item-level VAT band aggregation
│
├── processes/                       # 🔒 Locked boilerplate modules
│   ├── P00_set_packages.py
│   ├── P01_set_file_paths.py
│   ├── P02_system_processes.py
│   ├── P03_shared_functions.py
│   ├── P04_static_lists.py
│   ├── P05a_gui_elements_setup.py
│   ├── P06_logging_utils.py
│   ├── P07_module_configs.py
│   ├── P08_snowflake_connector.py
│   ├── P09_gdrive_api.py
│   └── P10_user_config.py
│
└── credentials/
    └── credentials.json   # (optional for API mode)
```

---

## ⚙️ Setup & Run Instructions

### Step 1 – Install Dependencies

```bash
pip install -r requirements.txt
```

or manually:

```bash
pip install pandas snowflake-connector-python google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

---

### Step 2 – Configure Google Drive Root

When the app starts, the launcher will ask you to select a **mapped drive** (e.g. `H:\`)
This root is stored and passed dynamically to build all provider folder paths.

---

### Step 3 – Run the App

```bash
python main/M00_run_gui.py
```

You’ll see:

1. Okta browser login (Snowflake)
2. Optional Google Drive setup
3. The main **DWH Orders-to-Cash GUI** window

Click **▶ Run DWH Extraction** to execute the workflow.

---

## 📊 Outputs

Each successful run generates:

```
H:\Shared drives\Automation Projects\Accounting\Orders to Cash\
│
├── 01 Braintree\03 DWH\YY.MM - Braintree DWH data.csv
├── 02 Paypal\03 DWH\YY.MM - Paypal DWH data.csv
├── 03 Uber Eats\03 DWH\YY.MM - Uber DWH data.csv
├── 04 Deliveroo\03 DWH\YY.MM - Deliveroo DWH data.csv
├── 05 Just Eat\03 DWH\YY.MM - Just Eat DWH data.csv
└── 06 Amazon\03 DWH\YY.MM - Amazon DWH data.csv
```

Each file is fully cleaned, normalized, and ready for downstream reconciliation.

---

## 🧠 Architecture Summary

```
M00_run_gui.py
  └── P05a_gui_elements_setup.ConnectionLauncher
        └── M01_load_project_config.launch_project_main()
              └── I01_project_launcher.launch_main_app()
                    └── I02_gui_elements_main.MainProjectGUI()
                          └── I03_combine_sql.main()
```

---

## 🧩 Customization

If you need to adapt this for other data pipelines:

* Replace SQL files in `/sql/`
* Update transformation logic in `I03_combine_sql.py`
* Keep the GUI and launcher unchanged — they’re already compliant with Boilerplate v1.1

---

## 🧱 Version & Author

**Version:** 1.1-DWH (Boilerplate Compliant)
**Author:** Gerry Pidgeon
**Created:** November 2025
**Project:** *Data Warehouse Orders-to-Cash (Snowflake → Shared Drive Export)*
