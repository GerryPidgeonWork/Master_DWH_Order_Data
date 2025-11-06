# ====================================================================================================
# P05_gui_elements.py
# ----------------------------------------------------------------------------------------------------
# Purpose:
#   Provides the "Initial Connection Launcher" GUI for the project.
#   This script acts as a "Login Window".
# ----------------------------------------------------------------------------------------------------
# Features:
#   - Dynamically loads emails from 'P10_user_config.py' to create radio buttons.
#   - **FIX**: Disables "Finish" button while Snowflake is in the process of connecting.
#   - "Finish & Launch" button is enabled once GDrive method is set (Snowflake is optional).
# ----------------------------------------------------------------------------------------------------
# Usage:
#   1. Edit 'processes/P10_user_config.py' with your team's emails.
#   2. Run this script via 'main/M00_run_setup.gui.py'
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

# --- Import App-specific functions ---
from processes.P08_snowflake_connector import connect_to_snowflake, SNOWFLAKE_EMAIL_DOMAIN
from processes.P09_gdrive_api import get_drive_service
from processes.P02_system_processes import detect_os

# --- Import the Main Application Window ---
from processes.P06_class_items import MainApplicationWindow

# --- Try to load the user config file ---
try:
    from processes.P10_user_config import (
        EMAIL_SLOT_1, EMAIL_SLOT_2, EMAIL_SLOT_3, EMAIL_SLOT_4, EMAIL_SLOT_5
    )
    PRESET_EMAILS = []
    seen_emails = set()
    for email in [EMAIL_SLOT_1, EMAIL_SLOT_2, EMAIL_SLOT_3, EMAIL_SLOT_4, EMAIL_SLOT_5]:
        if email and "firstname.lastname" not in email and email not in seen_emails:
            PRESET_EMAILS.append(email)
            seen_emails.add(email)
    CONFIG_FILE_EXISTS = True
except ImportError:
    print("Warning: 'processes/P10_user_config.py' not found.")
    print("Only 'Custom' email option will be shown.")
    PRESET_EMAILS = []
    CONFIG_FILE_EXISTS = False


# ====================================================================================================
# 3. MAIN APPLICATION CLASS (CONNECTION LAUNCHER)
# ----------------------------------------------------------------------------------------------------
class ConnectionLauncher(tk.Tk):
    """
    This class is the "Login Window" or "Launcher".
    Its job is to get connections and then launch the MainApplicationWindow.
    """
    def __init__(self):
        super().__init__()

        # --- App-wide variables ---
        self.snowflake_conn = None
        self.gdrive_service = None
        
        self.upload_method = tk.StringVar(value="local")
        
        default_local_path = "Path not set. Click 'Browse...'"
        os_type = detect_os()
        if os_type == "Windows":
            h_drive = Path("H:/") 
            if h_drive.exists() and h_drive.is_dir():
                default_local_path = str(h_drive.resolve())
        
        self.local_gdrive_path = tk.StringVar(value=default_local_path)
        
        # --- DYNAMIC HEIGHT CALCULATION ---
        num_email_rows = len(PRESET_EMAILS) + 1 # +1 for "Custom"
        base_height = 480 
        calculated_height = base_height + (num_email_rows * 25)
        
        # --- Window Setup ---
        self.title("Initial Connection Launcher")
        self.geometry(f"450x{calculated_height}")
        self.configure(bg="#f0f0f0")

        # --- Styling ---
        style = ttk.Style(self)
        style.configure("Accent.TButton", font=("Arial", 10, "bold"), padding=10)
        style.configure("TButton", padding=10)
        style.configure("TFrame", background="#f0f0f0")
        style.configure("TLabel", background="#f0f0f0")
        style.configure("TLabelframe", background="#f0f0f0", padding=10)
        style.configure("TLabelframe.Label", background="#f0f0f0", font=("Arial", 11, "bold"))
        style.configure("TRadiobutton", background="#f0f0f0")
        style.configure("Path.TLabel", background="#f0f0f0", font=("Arial", 8, "italic"))

        # --- Main Frame ---
        self.main_frame = ttk.Frame(self, padding="20 20 20 20")
        self.main_frame.pack(expand=True, fill=tk.BOTH)

        # --- 1. Email Selection Frame ---
        self.email_frame = ttk.LabelFrame(self.main_frame, text="1. Select Snowflake User (Optional)")
        self.email_frame.pack(fill=tk.X)
        self.email_frame.columnconfigure(1, weight=1)
        self.email_choice = tk.StringVar()
        self.small_font = tkFont.Font(family="Arial", size=9)
        
        current_row = 0
        for email in PRESET_EMAILS:
            name = email.split('@')[0].replace('.', ' ').title() 
            ttk.Radiobutton(
                self.email_frame, text=name, value=email,
                variable=self.email_choice, command=self.on_email_choice_change
            ).grid(row=current_row, column=0, columnspan=2, sticky=tk.W, padx=5, pady=2)
            current_row += 1

        ttk.Radiobutton(
            self.email_frame, text="Custom:", value="custom",
            variable=self.email_choice, command=self.on_email_choice_change
        ).grid(row=current_row, column=0, sticky=tk.W, padx=5, pady=2)
        
        self.custom_email_entry = ttk.Entry(
            self.email_frame, state=tk.DISABLED, 
            font=self.small_font, width=30
        )
        self.custom_email_entry.grid(row=current_row, column=1, sticky=tk.EW, padx=(0, 5), pady=2)

        if PRESET_EMAILS:
            self.email_choice.set(PRESET_EMAILS[0]) 
        else:
            self.email_choice.set("custom") 
            self.on_email_choice_change() 

        # --- 2. Snowflake Connection ---
        self.sf_button = ttk.Button(
            self.main_frame, text="2. Connect to Snowflake",
            command=self.run_snowflake_connection, style="Accent.TButton"
        )
        self.sf_button.pack(fill=tk.X, pady=(20, 5))
        self.sf_status = ttk.Label(self.main_frame, text="Status: Not Connected", font=("Arial", 9, "italic"))
        self.sf_status.pack(pady=(0, 15))

        # --- 3. Google Drive Upload Method ---
        self.upload_frame = ttk.LabelFrame(self.main_frame, text="3. Select Upload Method (Required)")
        self.upload_frame.pack(fill=tk.X, pady=5)
        self.upload_frame.columnconfigure(1, weight=1)

        ttk.Radiobutton(
            self.upload_frame, text="Use Google Drive API",
            value="api", variable=self.upload_method,
            command=self.on_upload_method_change
        ).grid(row=0, column=0, columnspan=2, sticky=tk.W, padx=5)

        ttk.Radiobutton(
            self.upload_frame, text="Use Local Mapped Drive",
            value="local", variable=self.upload_method,
            command=self.on_upload_method_change
        ).grid(row=1, column=0, columnspan=2, sticky=tk.W, padx=5)

        self.local_path_frame = ttk.Frame(self.upload_frame, padding=(0, 5, 0, 5))
        self.local_path_frame.grid(row=2, column=0, columnspan=2, sticky=tk.EW, padx=25)

        self.browse_button = ttk.Button(
            self.local_path_frame, text="Browse...",
            command=self.browse_for_gdrive_folder
        )
        self.browse_button.pack(side=tk.LEFT)

        self.local_path_label = ttk.Label(
            self.local_path_frame, textvariable=self.local_gdrive_path,
            style="Path.TLabel", relief=tk.SUNKEN, padding=5
        )
        self.local_path_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.local_path_frame.grid_remove()

        # --- 4. Google Drive Connection ---
        self.gdrive_api_button = ttk.Button(
            self.main_frame, text="4. Connect to Google Drive (API Method)",
            command=self.run_gdrive_api_connection
        )
        self.gdrive_api_button.pack(fill=tk.X, pady=5)
        self.gdrive_api_status = ttk.Label(self.main_frame, text="Status: Not Connected", font=("Arial", 9, "italic"))
        self.gdrive_api_status.pack(pady=(0, 15))

        # --- 5. FINISH BUTTON ---
        self.finish_button = ttk.Button(
            self.main_frame, text="Finish & Launch App",
            command=self.launch_main_app,
            state=tk.DISABLED 
        )
        self.finish_button.pack(fill=tk.X, pady=10)

        # --- Threading Queue ---
        self.thread_queue = queue.Queue()
        self.check_thread_queue()

        # --- Set Initial GUI State ---
        self.on_upload_method_change()
        if not CONFIG_FILE_EXISTS:
            messagebox.showwarning("Config File Missing",
                "Warning: 'processes/P10_user_config.py' not found.\n\n"
                "Only 'Custom' email entry will be available.")

    # ==================================================
    # WIDGET COMMANDS & HELPERS
    # ==================================================
    
    # --- *** THIS IS THE UPDATED FUNCTION *** ---
    def check_finish_button_state(self):
        """
        Enable the 'Finish' button only if all requirements are met.
        1. GDrive part must be ready.
        2. Snowflake part must NOT be in a "connecting" state.
        """
        
        # 1. Check GDrive status
        gdrive_ready = False
        if self.upload_method.get() == "api":
            gdrive_ready = (self.gdrive_service is not None)
        else: # "local"
            gdrive_ready = ("Path not set" not in self.local_gdrive_path.get())
            
        # 2. Check Snowflake status
        # We must ensure Snowflake is not in the *middle* of connecting.
        sf_status_text = self.sf_status.cget("text")
        sf_is_connecting = "Initializing" in sf_status_text or "Connecting" in sf_status_text
        
        # 3. Enable button ONLY if GDrive is ready AND Snowflake is not busy.
        if gdrive_ready and not sf_is_connecting:
            self.finish_button.config(state=tk.NORMAL)
        else:
            self.finish_button.config(state=tk.DISABLED)

    def on_upload_method_change(self):
        """Called when the GDrive upload method radio button is clicked."""
        if self.upload_method.get() == "local":
            self.local_path_frame.grid()
            self.gdrive_api_button.config(state=tk.DISABLED)
            self.gdrive_api_status.config(text="Status: Local path method selected", foreground="blue")
        else: # 'api'
            self.local_path_frame.grid_remove()
            if not self.gdrive_service:
                self.gdrive_api_button.config(state=tk.NORMAL)
            if not self.gdrive_service:
                self.gdrive_api_status.config(text="Status: Not Connected", foreground="black")
            else:
                self.gdrive_api_status.config(text="Status: ✅ Connected!", foreground="green")
        
        self.check_finish_button_state()

    def on_email_choice_change(self):
        """Called when any email radio button is clicked."""
        if self.email_choice.get() == "custom":
            self.custom_email_entry.config(state=tk.NORMAL)
            self.custom_email_entry.focus()
        else:
            self.custom_email_entry.config(state=tk.DISABLED)

    def browse_for_gdrive_folder(self):
        """Opens a dialog to select the local Google Drive folder."""
        path = filedialog.askdirectory(title="Select your Google Drive 'Shared drives' folder")
        if path:
            self.local_gdrive_path.set(path)
            print(f"Local Google Drive path set to: {path}")
            self.check_finish_button_state()

    def run_snowflake_connection(self):
        """Called when the Snowflake button is clicked."""
        # --- This function will now also call check_finish_button_state ---
        choice = self.email_choice.get()
        selected_email = ""

        if choice == "custom":
            selected_email = self.custom_email_entry.get().strip().lower()
            if not selected_email:
                messagebox.showerror("Email Error", "Please enter an email in the 'Custom' box.")
                return
            if not selected_email.endswith(f"@{SNOWFLAKE_EMAIL_DOMAIN}"):
                messagebox.showerror("Email Error", f"Invalid email. Must end with @{SNOWFLAKE_EMAIL_DOMAIN}")
                return
        else:
            selected_email = choice
        
        self.sf_button.config(state=tk.DISABLED)
        self.sf_status.config(text="Status: Initializing...", foreground="black")
        
        # --- Disable Finish button *immediately* ---
        self.check_finish_button_state() 
        
        self.run_in_thread(
            target_func=lambda: connect_to_snowflake(email_address=selected_email), 
            source_name="snowflake"
        )

    def run_gdrive_api_connection(self):
        """Called when the Google Drive API button is clicked."""
        self.gdrive_api_button.config(state=tk.DISABLED)
        self.gdrive_api_status.config(text="Status: Initializing...", foreground="black")
        
        # --- Disable Finish button *immediately* ---
        self.check_finish_button_state()

        self.run_in_thread(
            target_func=get_drive_service, 
            source_name="gdrive_api"
        )
    
    def launch_main_app(self):
        """Hide this window and launch the main application."""
        print("Launcher: Hiding connection window.")
        self.withdraw() 
        
        main_app = MainApplicationWindow(
            parent=self,
            snowflake_conn=self.snowflake_conn,
            gdrive_service=self.gdrive_service,
            upload_method=self.upload_method.get(),
            local_path=self.local_gdrive_path.get()
        )
        print("Launcher: MainApplicationWindow is now running.")


    # ==================================================
    # THREADING & BACKGROUND TASKS
    # ==================================================
    
    def check_thread_queue(self):
        """Check the message queue from background threads and update the GUI."""
        try:
            message = self.thread_queue.get(block=False)
            
            # --- Handle Snowflake Messages ---
            if message.get("source") == "snowflake":
                if "status" in message:
                    self.sf_status.config(text=f"Status: {message['status']}")
                if "connection" in message:
                    self_conn = message["connection"]
                    if self_conn:
                        self.snowflake_conn = self_conn
                        self.sf_status.config(text="Status: ✅ Connected!", foreground="green")
                        self.sf_button.config(state=tk.DISABLED)
                    else:
                        self.sf_status.config(text="Status: ❌ Connection Failed. Check console.", foreground="red")
                        self.sf_button.config(state=tk.NORMAL)

            # --- Handle Google Drive API Messages ---
            elif message.get("source") == "gdrive_api":
                if "status" in message:
                    self.gdrive_api_status.config(text=f"Status: {message['status']}")
                if "service" in message:
                    service = message["service"]
                    if service:
                        self.gdrive_service = service
                        self.gdrive_api_status.config(text="Status: ✅ Connected!", foreground="green")
                        self.gdrive_api_button.config(state=tk.DISABLED)
                    else:
                        self.gdrive_api_status.config(text="Status: ❌ Connection Failed. Check console.", foreground="red")
                        if self.upload_method.get() == "api":
                            self.gdrive_api_button.config(state=tk.NORMAL)
                        
        except queue.Empty:
            pass
        
        self.check_finish_button_state()
        self.after(100, self.check_thread_queue)

    def run_in_thread(self, target_func, source_name):
        """Generic wrapper to run a function in a background thread."""
        def thread_wrapper():
            try:
                self.thread_queue.put({"source": source_name, "status": "Connecting... (Check browser/console)"})
                result = target_func()
                
                if source_name == "snowflake":
                    self.thread_queue.put({"source": source_name, "connection": result})
                elif source_name == "gdrive_api":
                    self.thread_queue.put({"source": source_name, "service": result})
                    
            except Exception as e:
                print(f"Error in {source_name} thread: {e}")
                if source_name == "snowflake":
                    self.thread_queue.put({"source": source_name, "connection": None})
                elif source_name == "gdrive_api":
                    self.thread_queue.put({"source": source_name, "service": None})

        threading.Thread(target=thread_wrapper, daemon=True).start()


# ====================================================================================================
# 4. MAIN EXECUTION
# ----------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    print("Launching Initial Connection Launcher...")
    app = ConnectionLauncher()
    app.mainloop()