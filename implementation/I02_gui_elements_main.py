# ====================================================================================================
# I02_gui_elements_main.py
# ----------------------------------------------------------------------------------------------------
# DWH Orders-to-Cash Extractor GUI
# ----------------------------------------------------------------------------------------------------
# Purpose:
#   Provides a user interface for running the full DWH extraction process (Orders-to-Cash).
#   This window is launched by P05a AFTER connections/paths are established.
#
# Integration:
#   - Launched by processes/P05a_gui_elements_setup.py
#   - Calls implementation/I03_combine_sql.main() to run core logic
# ----------------------------------------------------------------------------------------------------
# Author:       Gerry Pidgeon
# Created:      2025-11-06
# Project:      DWHOrdersToCash (BoilerplateOrdersToCash v1.1)
# ====================================================================================================


# ====================================================================================================
# 1. SYSTEM IMPORTS
# ----------------------------------------------------------------------------------------------------
import sys
from pathlib import Path

# --- Standard boilerplate block ---
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.dont_write_bytecode = True  # Prevents __pycache__ folders


# ====================================================================================================
# 2. PROJECT IMPORTS
# ----------------------------------------------------------------------------------------------------
from processes.P00_set_packages import *        # Imports all packages from P00_set_packages.py
import processes.P07_module_configs as cfg

# --- Imports for this specific GUI ---
from implementation.I03_combine_sql import main as run_dwh_main


# ====================================================================================================
# 3. CONSOLE REDIRECTOR CLASS
# ----------------------------------------------------------------------------------------------------
class TextRedirector(io.TextIOBase):
    """Redirects stdout/stderr to a Tkinter Text widget."""

    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, message):
        try:
            # If app or widget is already destroyed, silently skip
            if not hasattr(self.text_widget, "winfo_exists"):
                return
            if not self.text_widget.winfo_exists():
                return

            self.text_widget.configure(state="normal")
            self.text_widget.insert("end", message)
            self.text_widget.see("end")
            self.text_widget.configure(state="disabled")

        except (tk.TclError, RuntimeError):
            # Happens when Tkinter interpreter or widget is gone — safely ignore
            pass

    def flush(self):
        pass

# ====================================================================================================
# 4. MAIN APPLICATION CLASS
# ----------------------------------------------------------------------------------------------------
class MainProjectGUI(tk.Toplevel):
    """Main Tkinter window for the DWH Orders-to-Cash extraction workflow."""

    def __init__(self, parent, snowflake_conn, gdrive_service, upload_method, local_path):
        super().__init__(parent)

        # --- Store passed arguments ---
        self.parent = parent
        self.snowflake_conn = snowflake_conn
        self.gdrive_service = gdrive_service
        self.local_path = local_path

        # --------------------------------------------------------------------------------------------
        # Window Configuration
        # --------------------------------------------------------------------------------------------
        self.title("📊 DWH Orders-to-Cash Extractor")
        self.geometry("900x800")
        self.minsize(900, 800)

        # Track user selections
        self.month_override_var = tk.StringVar()

        # Determine default reporting period
        self.default_month, self.start_date, self.end_date = self.get_default_month_period()

        # Handle window closure
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # --------------------------------------------------------------------------------------------
        # Main Frame
        # --------------------------------------------------------------------------------------------
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill="both", expand=True)

        # --------------------------------------------------------------------------------------------
        # Header Section
        # --------------------------------------------------------------------------------------------
        header = ttk.Label(
            main_frame,
            text="📊 DWH Orders-to-Cash Extractor",
            font=("Segoe UI", 16, "bold"),
        )
        header.pack(pady=(0, 10))

        sf_status = "✅ Connected" if self.snowflake_conn else "❌ Not Connected (Skipping Queries)"
        ttk.Label(
            main_frame,
            text=f"Snowflake Status: {sf_status}",
            foreground="green" if self.snowflake_conn else "red",
            font=("Segoe UI", 10, "bold"),
        ).pack(fill="x", pady=(0, 15))

        # --------------------------------------------------------------------------------------------
        # Reporting Period Section
        # --------------------------------------------------------------------------------------------
        month_frame = ttk.LabelFrame(main_frame, text="Reporting Period", padding=10)
        month_frame.pack(fill="x", pady=5)

        default_label = ttk.Label(
            month_frame,
            text=f"Default: {self.default_month.strftime('%B %Y')} "
                 f"({self.start_date} → {self.end_date})",
        )
        default_label.grid(row=0, column=0, columnspan=2, sticky="w", pady=2)

        ttk.Label(month_frame, text="Override (YYYY-MM):").grid(row=1, column=0, sticky="w", pady=2)
        ttk.Entry(month_frame, textvariable=self.month_override_var, width=10).grid(
            row=1, column=1, sticky="w", pady=2
        )

        # --------------------------------------------------------------------------------------------
        # GDrive Path Summary
        # --------------------------------------------------------------------------------------------
        gdrive_frame = ttk.LabelFrame(main_frame, text="Export Root Path (Set by Launcher)", padding=10)
        gdrive_frame.pack(fill="x", pady=5)

        ttk.Label(gdrive_frame, text=f"Root Folder: {self.local_path}").pack(fill="x", padx=5)
        ttk.Label(
            gdrive_frame,
            text="Files will be saved in subfolders within this root (e.g., /01 Braintree/03 DWH).",
            font=("Segoe UI", 8, "italic"),
        ).pack(fill="x", padx=5)

        # --------------------------------------------------------------------------------------------
        # Buttons
        # --------------------------------------------------------------------------------------------
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=15)

        self.run_button = ttk.Button(
            button_frame,
            text="▶ Run DWH Extraction",
            command=self.run_extraction,
            state="normal" if self.snowflake_conn else "disabled",
        )
        self.run_button.pack(side="left", padx=5)

        if not self.snowflake_conn:
            ttk.Label(
                button_frame, text="Cannot run: Snowflake not connected.", foreground="red"
            ).pack(side="left", padx=10)

        ttk.Button(button_frame, text="❌ Close", command=self.on_close).pack(side="right", padx=5)

        # --------------------------------------------------------------------------------------------
        # Status Output Box
        # --------------------------------------------------------------------------------------------
        status_frame = ttk.LabelFrame(main_frame, text="Status Output", padding=10)
        status_frame.pack(fill="both", expand=True, pady=(10, 0))

        self.status_box = tk.Text(
            status_frame, wrap="word", height=25, state="disabled", font=("Consolas", 10)
        )
        self.status_box.pack(fill="both", expand=True, side="left")

        scrollbar = ttk.Scrollbar(status_frame, command=self.status_box.yview)
        scrollbar.pack(side="right", fill="y")
        self.status_box.config(yscrollcommand=scrollbar.set)

        sys.stdout = TextRedirector(self.status_box)
        sys.stderr = TextRedirector(self.status_box)

        self.log("GUI initialized. Ready to start extraction.")

    # =================================================================================================
    # 5. HELPER METHODS
    # =================================================================================================
    def on_close(self):
        """Handle window closure and safely close connections."""
        if self.snowflake_conn:
            try:
                self.snowflake_conn.close()
                print("\nSnowflake connection closed by GUI.")
            except Exception as e:
                print(f"\nError closing Snowflake connection: {e}")
        self.parent.destroy()

    def get_default_month_period(self):
        """Determine default reporting period (previous or current month)."""
        today = dt.date.today()
        first_of_this_month = today.replace(day=1)
        last_month_end = first_of_this_month - dt.timedelta(days=1)
        first_of_last_month = last_month_end.replace(day=1)

        if today <= (last_month_end + dt.timedelta(days=9)):
            default_month = first_of_last_month
        else:
            default_month = first_of_this_month

        start_date = default_month.strftime("%Y-%m-01")
        last_day = calendar.monthrange(default_month.year, default_month.month)[1]
        end_date = default_month.replace(day=last_day).strftime("%Y-%m-%d")

        return default_month, start_date, end_date

    def log(self, message):
        """Append a message to the status box with auto-scroll."""
        timestamp = dt.datetime.now().strftime("%H:%M:%S")
        self.status_box.config(state="normal")
        self.status_box.insert("end", f"[{timestamp}] {message}\n")
        self.status_box.see("end")
        self.status_box.config(state="disabled")
        self.update_idletasks()

    # =================================================================================================
    # 6. CORE LOGIC
    # =================================================================================================
    def run_extraction(self):
        """Run the DWH extraction process with selected options."""
        if not self.snowflake_conn:
            messagebox.showerror("Error", "Cannot run: Snowflake is not connected.")
            return

        if "Path not set" in self.local_path or not Path(self.local_path).is_dir():
            messagebox.showerror(
                "Error",
                "Export Path Error: The Google Drive root path is invalid or not set.\n"
                "Please go back and set the path in the Initial Setup window.",
            )
            return

        override = self.month_override_var.get().strip()
        if override and not re.match(r"\d{4}-\d{2}$", override):
            messagebox.showerror("Error", "Invalid month format. Please use YYYY-MM (e.g., 2025-11).")
            return

        self.run_button.config(state="disabled")
        self.log("Starting DWH extraction...")

        start_date, end_date = self.start_date, self.end_date

        if override:
            try:
                year, month = map(int, override.split("-"))
                start_date = f"{year}-{month:02d}-01"
                last_day = calendar.monthrange(year, month)[1]
                end_date = f"{year}-{month:02d}-{last_day:02d}"
                self.log(f"Overriding period → {start_date} → {end_date}")
            except Exception:
                messagebox.showerror("Error", "Internal date conversion error.")
                self.run_button.config(state="normal")
                return

        cfg.REPORTING_START_DATE = start_date
        cfg.REPORTING_END_DATE = end_date

        threading.Thread(
            target=self._execute_main,
            args=(self.local_path, self.snowflake_conn),
            daemon=True,
        ).start()

    def _execute_main(self, local_root_path, conn):
        """Execute the core DWH extraction logic in a thread."""
        try:
            self.log("Starting core DWH extraction logic (I03)...")
            run_dwh_main(conn, local_root_path)
            self.log("✅ Extraction completed successfully. Files saved to GDrive root.")
        except Exception as e:
            self.log(f"❌ Critical Error: {e}")
            messagebox.showerror("Extraction Error", str(e))
        finally:
            self.log("Process finished.")
            self.run_button.config(state="normal")


# ====================================================================================================
# 7. MAIN EXECUTION
# ----------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    """
    This script should be launched via main/M00_run_gui.py or processes/P05a_gui_elements_setup.py.
    """
    print("This module should not be run directly.")
