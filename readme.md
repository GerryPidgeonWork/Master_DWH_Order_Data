Python GUI Boilerplate (Snowflake & Google Drive)

This is a reusable boilerplate for creating Python GUI applications that need to connect to Snowflake (using Okta SSO) and Google Drive (via API or local mapped drive).

It is designed as a "launcher" that handles all authentication up-front, then passes the live, ready-to-use connection objects to a main application window.

Key Features

Snowflake Connector (P08):

Connects using Okta SSO (externalbrowser), which opens a browser for authentication.

Automatically finds the best available Role/Warehouse for the user based on a priority list (e.g., OKTA_ANALYTICS_ROLE > OKTA_READER_ROLE).

Handles connection timeouts and errors gracefully.

Google Drive Connector (P09):

Provides two methods for file operations, selectable in the GUI:

Local Mapped Drive: (Default) Lets the user browse and select their local H:\ drive.

API Method: Connects directly to the Google Drive API.

GUI Launcher (P05):

A user-friendly "Initial Connection Launcher" built with tkinter.

Dynamically creates email radio buttons from the P10_user_config.py file.

Uses background threads for all connections so the GUI never freezes.

Launches the main app (P06) only when connections are ready.

Configurable (P10):

User-friendly setup. A new user just edits processes/P10_user_config.py to add their team's emails.

Executable Ready:

Includes a .gitignore file and instructions for building a .exe with PyInstaller.

Project Structure

GPPythonBoilerplate/
│
├── .venv/                  # Virtual environment
│
├── credentials/
│   └── credentials.json    # Google API key (Must be added manually)
│
├── main/
│   └── M00_run_setup.gui.py # *** MAIN ENTRY POINT TO RUN THE APP ***
│
├── processes/
│   ├── P00_set_packages.py        # Central hub for all 'import' statements
│   ├── P01_set_file_paths.py      # Manages all project file paths
│   ├── P02_system_processes.py    # OS detection (for H: drive default)
│   ├── P05_gui_elements.py        # The "Launcher" GUI window
│   ├── P06_class_items.py         # The "Main App" window (placeholder)
│   ├── P08_snowflake_connector.py # Snowflake/Okta connection logic
│   ├── P09_gdrive_api.py          # Google Drive API connection logic
│   └── P10_user_config.py       # User-editable email list
│
└── requirements.txt        # List of Python packages


1. Setup & Configuration

Before running the application, you must complete these setup steps.

Step 1: Install Python Packages

This project uses a central package file (P00_set_packages.py). Install all dependencies using pip.

Create a requirements.txt file (if one doesn't exist) from your .venv:

pip freeze > requirements.txt


Install packages (for any new user):

pip install -r requirements.txt


Step 2: Configure User Email

Open processes/P10_user_config.py.

Add your team's most common emails to EMAIL_SLOT_1, EMAIL_SLOT_2, etc.

Save the file. The GUI will automatically create radio buttons for any slots you fill in.

# processes/P10_user_config.py

# --- REQUIRED: Fill in your team's common emails ---
EMAIL_SLOT_1 = "firstname.lastname@gopuff.com"
EMAIL_SLOT_2 = ""
EMAIL_SLOT_3 = ""
EMAIL_SLOT_4 = ""
EMAIL_SLOT_5 = ""


Step 3: (Optional) Google Drive API Setup

If you want to use the Google Drive API method, you must get your own credentials.

Go to the Google Cloud Console.

Create a new project.

Enable the "Google Drive API".

Go to "Credentials" -> "Create Credentials" -> "OAuth client ID".

Select "Desktop app" for the application type.

Click "Download JSON".

Rename the downloaded file to credentials.json and place it in the credentials/ folder.

2. How to Run

Open your terminal (PowerShell, cmd, etc.).

Navigate to the project's root folder (GPPythonBoilerplate/).

Activate your virtual environment (e.g., .\.venv\Scripts\Activate.ps1).

Run the main entry point script:

python main/M00_run_setup.gui.py


The "Initial Connection Launcher" will appear.

(Optional) Click "Connect to Snowflake". Your browser will open for Okta login.

Select your Google Drive upload method.

API: Click "Connect to Google Drive". Your browser will open for login.

Local: Click "Browse..." and select your local Google Drive folder (e.g., H:\Shared drives).

Once the "Finish & Launch App" button is active, click it to open the main application.

3. Building an Executable (.exe)

You can bundle this entire application into a single .exe file using PyInstaller.

Make sure PyInstaller is installed (pip install pyinstaller).

Run the following command from the root directory (GPPythonBoilerplate/):

pyinstaller --onefile --name "GopuffApp" --add-data "credentials;credentials" main/M00_run_setup.gui.py


--onefile: Creates a single .exe file.

--add-data "credentials;credentials": Crucial step. This bundles the credentials.json file inside the executable.

main/M00_run_setup.gui.py: This is the main entry point.

Your final GopuffApp.exe file will be in the new dist/ folder.