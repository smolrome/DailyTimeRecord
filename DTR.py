import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from datetime import datetime, timedelta
import csv
import json
import os
import webbrowser
import hashlib
import pickle
from tkcalendar import Calendar, DateEntry
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import requests
from PIL import Image, ImageTk
import sys
import time

class AdvancedTimeRecordApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Time Record System")
        self.root.geometry("1400x900")
        self.root.state('zoomed')  # Start maximized
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # CLI indicator
        print("Starting the Advanced Time Record System...")

        # GUI indicator (Splash screen or status message)
        self.show_startup_message()

        # Security and authentication
        self.current_user = None
        self.users_file = "users.dat"
        self.backup_url = "https://your-backup-service.com/api"  # Replace with actual service

        # Settings
        self.settings = {
            'work_hours_per_day': 8,
            'overtime_threshold': 8,
            'break_deduction': True,
            'auto_backup': False,
            'dark_mode': False,
            'notifications': True
        }

        # Initialize data structures
        self.initialize_data()

        # UI Theme
        self.setup_theme()

        # Create login screen first
        self.create_login_screen()

        # CLI indicator for running
        print("Advanced Time Record System is now running.")

    def show_startup_message(self):
        """Display a startup message in the GUI."""
        startup_label = tk.Label(self.root, text="Starting the Advanced Time Record System...",
                                 font=("Arial", 14), bg="#f0f8ff", fg="#003366")
        startup_label.place(relx=0.5, rely=0.5, anchor="center")
        self.root.update_idletasks()  # Force the UI to update immediately
        time.sleep(2)  # Simulate a delay for the startup message
        startup_label.destroy()  # Remove the startup message
    
    def initialize_data(self):
        """Initialize all data structures"""
        self.clock_in_time = None
        self.clock_out_time = None
        self.break_start_time = None
        self.break_end_time = None
        self.work_sessions = []
        self.break_sessions = []
        self.current_date = datetime.now().date()
        self.weekly_data = []
        self.monthly_data = []
        
    def setup_theme(self):
        """Configure UI theme colors"""
        self.light_theme = {
            'bg': "#f0f8ff",
            'header': "#0078d7",
            'button': "#4da6ff",
            'button_hover': "#1a8cff",
            'text': "#003366",
            'entry_bg': "#ffffff",
            'warning': "#ff6666",
            'success': "#66cc66",
            'frame': "#e6f2ff"
        }
        
        self.dark_theme = {
            'bg': "#2d2d2d",
            'header': "#1a3d5f",
            'button': "#3a6ea5",
            'button_hover': "#4d88c7",
            'text': "#e0e0e0",
            'entry_bg': "#3d3d3d",
            'warning': "#cc3333",
            'success': "#339966",
            'frame': "#1e1e1e"
        }
        
        self.current_theme = self.light_theme
    
    def create_login_screen(self):
        """Create login/registration interface"""
        self.clear_window()
        
        login_frame = tk.Frame(self.root, bg=self.current_theme['bg'])
        login_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        tk.Label(login_frame, text="Advanced Time Record System", 
                font=("Arial", 18, "bold"), bg=self.current_theme['bg'], 
                fg=self.current_theme['text']).grid(row=0, column=0, columnspan=2, pady=20)
        
        tk.Label(login_frame, text="Username:", bg=self.current_theme['bg'], 
                fg=self.current_theme['text']).grid(row=1, column=0, pady=5, sticky="e")
        self.username_entry = tk.Entry(login_frame, bg=self.current_theme['entry_bg'])
        self.username_entry.grid(row=1, column=1, pady=5)
        
        tk.Label(login_frame, text="Password:", bg=self.current_theme['bg'], 
                fg=self.current_theme['text']).grid(row=2, column=0, pady=5, sticky="e")
        self.password_entry = tk.Entry(login_frame, show="*", bg=self.current_theme['entry_bg'])
        self.password_entry.grid(row=2, column=1, pady=5)
        
        login_btn = tk.Button(login_frame, text="Login", command=self.authenticate_user,
                            bg=self.current_theme['button'], fg="white")
        login_btn.grid(row=3, column=0, columnspan=2, pady=10, ipadx=20)
        
        register_btn = tk.Button(login_frame, text="Register New User", command=self.register_user,
                               bg=self.current_theme['button'], fg="white")
        register_btn.grid(row=4, column=0, columnspan=2, pady=5, ipadx=20)
        
        recovery_btn = tk.Button(login_frame, text="Forgot Password?", command=self.recover_password,
                               bg=self.current_theme['bg'], fg=self.current_theme['text'], bd=0)
        recovery_btn.grid(row=5, column=0, columnspan=2, pady=5)
    
    def authenticate_user(self):
        """Authenticate user credentials"""
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return
        
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()
        
        try:
            with open(self.users_file, "rb") as f:
                users = pickle.load(f)
                
                if username in users and users[username]['password'] == hashed_pw:
                    self.current_user = username
                    self.load_user_data()
                else:
                    messagebox.showerror("Error", "Invalid username or password")
        except FileNotFoundError:
            messagebox.showerror("Error", "No users registered yet")
    
    def register_user(self):
        """Register a new user"""
        username = simpledialog.askstring("Registration", "Enter username:")
        if not username:
            return
        
        password = simpledialog.askstring("Registration", "Enter password:", show="*")
        if not password:
            return
        
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()
        
        try:
            with open(self.users_file, "rb") as f:
                users = pickle.load(f)
        except FileNotFoundError:
            users = {}
        
        if username in users:
            messagebox.showerror("Error", "Username already exists")
            return
        
        users[username] = {
            'password': hashed_pw,
            'created': datetime.now().strftime("%Y-%m-%d"),
            'admin': False
        }
        
        with open(self.users_file, "wb") as f:
            pickle.dump(users, f)
        
        messagebox.showinfo("Success", "User registered successfully")
    
    def recover_password(self):
        """Password recovery workflow"""
        messagebox.showinfo("Password Recovery", 
                          "Please contact your system administrator to reset your password")
    
    def load_user_data(self):
        """Load user-specific data"""
        user_dir = f"users/{self.current_user}"
        if not os.path.exists(user_dir):
            os.makedirs(user_dir)
        
        # Load settings
        settings_file = f"{user_dir}/settings.json"
        if (os.path.exists(settings_file)):
            with open(settings_file, "r") as f:
                self.settings.update(json.load(f))
        
        # Create main interface before loading records
        self.create_main_interface()
        
        # Now load records (UI elements exist)
        self.load_records()
        
        # Load weekly/monthly summaries
        self.load_summaries()
    
    def create_main_interface(self):
        """Create the main application interface"""
        self.clear_window()
        
        # Configure theme
        if self.settings['dark_mode']:
            self.current_theme = self.dark_theme
            self.root.configure(bg=self.dark_theme['bg'])
        else:
            self.current_theme = self.light_theme
            self.root.configure(bg=self.light_theme['bg'])
        
        # Menu Bar
        self.create_menu_bar()
        
        # Header
        self.create_header()
        
        # Main content area
        main_frame = tk.Frame(self.root, bg=self.current_theme['bg'])
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Left panel - Time tracking
        left_panel = tk.Frame(main_frame, bg=self.current_theme['frame'], padx=10, pady=10)
        left_panel.pack(side="left", fill="y")
        
        self.create_time_tracking_section(left_panel)
        self.create_break_section(left_panel)
        self.create_summary_section(left_panel)
        
        # Right panel - Records and analytics
        right_panel = tk.Frame(main_frame, bg=self.current_theme['frame'], padx=10, pady=10)
        right_panel.pack(side="right", fill="both", expand=True)
        
        self.create_records_section(right_panel)
        self.create_analytics_section(right_panel)
        
        # Status bar
        self.create_status_bar()
        
        # Update clock
        self.update_clock()
    
    def create_menu_bar(self):
        """Create the application menu bar"""
        menubar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        # Add this under the File menu
        file_menu.add_command(label="Add Past Records", command=self.add_past_records)
        file_menu.add_command(label="Export to CSV", command=self.export_to_csv)
        file_menu.add_command(label="Export to JSON", command=self.export_to_json)
        file_menu.add_separator()
        file_menu.add_command(label="Print Summary", command=self.print_summary)
        file_menu.add_separator()
        file_menu.add_command(label="Backup Data", command=self.backup_data)
        file_menu.add_command(label="Restore Data", command=self.restore_data)
        file_menu.add_separator()
        file_menu.add_command(label="Settings", command=self.open_settings)
        file_menu.add_separator()
        file_menu.add_command(label="Logout", command=self.logout)
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Reports menu
        reports_menu = tk.Menu(menubar, tearoff=0)
        reports_menu.add_command(label="Daily Report", command=lambda: self.generate_report('daily'))
        reports_menu.add_command(label="Weekly Report", command=lambda: self.generate_report('weekly'))
        reports_menu.add_command(label="Monthly Report", command=lambda: self.generate_report('monthly'))
        reports_menu.add_command(label="Custom Report", command=lambda: self.generate_report('custom'))
        menubar.add_cascade(label="Reports", menu=reports_menu)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        tools_menu.add_command(label="Calculate Overtime", command=self.calculate_overtime)
        tools_menu.add_command(label="Time Analysis", command=self.show_time_analysis)
        tools_menu.add_command(label="Productivity Stats", command=self.show_productivity_stats)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="User Guide", command=self.show_user_guide)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menubar)
        
    def add_past_records(self):
        """Open a dialog to manually input past work records"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Past Work Records")
        dialog.geometry("600x500")
        dialog.resizable(False, False)
        dialog.grab_set()  # Make the dialog modal

        # Date selection
        tk.Label(dialog, text="Date:", font=("Arial", 11)).pack(pady=(10, 0))
        date_entry = DateEntry(dialog, date_pattern="yyyy-mm-dd", font=("Arial", 11))
        date_entry.pack(pady=5)

        # Start time
        tk.Label(dialog, text="Start Time (HH:MM):", font=("Arial", 11)).pack(pady=(10, 0))
        start_time_entry = tk.Entry(dialog, font=("Arial", 11))
        start_time_entry.pack(pady=5)

        # End time
        tk.Label(dialog, text="End Time (HH:MM):", font=("Arial", 11)).pack(pady=(10, 0))
        end_time_entry = tk.Entry(dialog, font=("Arial", 11))
        end_time_entry.pack(pady=5)

        # Task/Project selection
        tk.Label(dialog, text="Task/Project:", font=("Arial", 11)).pack(pady=(10, 0))
        task_var = tk.StringVar(value="General Work")
        task_menu = ttk.Combobox(dialog, textvariable=task_var, 
                            values=["General Work", "Project A", "Project B", "Meeting", "Training"])
        task_menu.pack(pady=5)

        # Break time (optional)
        tk.Label(dialog, text="Break Duration (minutes, optional):", font=("Arial", 11)).pack(pady=(10, 0))
        break_entry = tk.Entry(dialog, font=("Arial", 11))
        break_entry.pack(pady=5)

        # Notes
        tk.Label(dialog, text="Notes (optional):", font=("Arial", 11)).pack(pady=(10, 0))
        notes_text = tk.Text(dialog, height=4, width=50, font=("Arial", 10))
        notes_text.pack(pady=5)

        def save_record():
            try:
                # Parse inputs
                date_str = date_entry.get()
                work_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                
                start_time = datetime.strptime(start_time_entry.get(), "%H:%M").time()
                end_time = datetime.strptime(end_time_entry.get(), "%H:%M").time()
                
                start_datetime = datetime.combine(work_date, start_time)
                end_datetime = datetime.combine(work_date, end_time)
                
                if start_datetime >= end_datetime:
                    messagebox.showerror("Error", "End time must be after start time")
                    return
                
                # Add work session
                self.work_sessions.append({
                    'date': work_date,
                    'start': start_datetime,
                    'end': end_datetime,
                    'task': task_var.get()
                })
                
                # Add break session if specified
                break_minutes = break_entry.get()
                if break_minutes and break_minutes.isdigit():
                    break_minutes = int(break_minutes)
                    break_start = start_datetime + (end_datetime - start_datetime) / 2  # Middle of work session
                    break_end = break_start + timedelta(minutes=break_minutes)
                    
                    self.break_sessions.append({
                        'date': work_date,
                        'start': break_start,
                        'end': break_end,
                        'type': "Manual Break"
                    })
                
                # Save notes if any
                notes = notes_text.get("1.0", "end-1c")
                if notes.strip():
                    # Store notes in a way that makes sense for your app
                    pass
                
                # Update UI and save data
                self.update_records()
                self.update_summary()
                self.save_records()
                
                messagebox.showinfo("Success", "Record added successfully")
                dialog.destroy()
                
            except ValueError as e:
                messagebox.showerror("Input Error", f"Invalid time format. Please use HH:MM.\nError: {e}")

        # Save button
        save_btn = tk.Button(dialog, text="Save Record", command=save_record,
                            bg=self.current_theme['button'], fg="white", font=("Arial", 10))
        save_btn.pack(pady=10)
    
    def create_header(self):
        """Create application header"""
        header_frame = tk.Frame(self.root, bg=self.current_theme['header'])
        header_frame.pack(fill="x", padx=5, pady=5)
        
        # User info
        user_label = tk.Label(header_frame, text=f"User: {self.current_user}", 
                            font=("Arial", 10), bg=self.current_theme['header'], fg="white")
        user_label.pack(side="left", padx=10)
        
        # Logo/Title
        title_label = tk.Label(header_frame, text="Advanced Time Record System", 
                             font=("Arial", 16, "bold"), bg=self.current_theme['header'], fg="white")
        title_label.pack(side="left", padx=10, expand=True)
        
        # Date and time
        self.date_label = tk.Label(header_frame, text=self.current_date.strftime("%A, %B %d, %Y"), 
                                 font=("Arial", 10), bg=self.current_theme['header'], fg="white")
        self.date_label.pack(side="right", padx=10)
        
        self.clock_label = tk.Label(header_frame, text="", font=("Arial", 10), 
                                   bg=self.current_theme['header'], fg="white")
        self.clock_label.pack(side="right", padx=10)
    
    def create_time_tracking_section(self, parent):
        """Create time tracking controls"""
        time_frame = tk.LabelFrame(parent, text="Time Tracking", font=("Arial", 12, "bold"),
                                 bg=self.current_theme['frame'], fg=self.current_theme['text'], padx=10, pady=10)
        time_frame.pack(fill="x", padx=5, pady=5)
        
        self.clock_in_btn = tk.Button(time_frame, text="Clock In", command=self.clock_in,
                                     bg=self.current_theme['button'], fg="white", font=("Arial", 12),
                                     activebackground=self.current_theme['button_hover'], width=10)
        self.clock_in_btn.grid(row=0, column=0, padx=5, pady=5)
        
        self.clock_out_btn = tk.Button(time_frame, text="Clock Out", command=self.clock_out,
                                      bg=self.current_theme['button'], fg="white", font=("Arial", 12),
                                      activebackground=self.current_theme['button_hover'], width=10, state="disabled")
        self.clock_out_btn.grid(row=0, column=1, padx=5, pady=5)
        
        self.status_label = tk.Label(time_frame, text="Status: Not clocked in", 
                                    font=("Arial", 12), bg=self.current_theme['frame'], fg=self.current_theme['text'])
        self.status_label.grid(row=0, column=2, padx=10, pady=5, sticky="w")
        
        self.clock_in_display = tk.Label(time_frame, text="Clock In: --:-- --", 
                                        font=("Arial", 11), bg=self.current_theme['frame'], fg=self.current_theme['text'])
        self.clock_in_display.grid(row=1, column=0, padx=5, pady=5)
        
        self.clock_out_display = tk.Label(time_frame, text="Clock Out: --:-- --", 
                                         font=("Arial", 11), bg=self.current_theme['frame'], fg=self.current_theme['text'])
        self.clock_out_display.grid(row=1, column=1, padx=5, pady=5)
        
        self.total_worked_label = tk.Label(time_frame, text="Total Worked: 00:00:00", 
                                          font=("Arial", 11), bg=self.current_theme['frame'], fg=self.current_theme['text'])
        self.total_worked_label.grid(row=1, column=2, padx=10, pady=5, sticky="w")
        
        # Add location tracking
        self.location_label = tk.Label(time_frame, text="Location: Office", 
                                      font=("Arial", 10), bg=self.current_theme['frame'], fg=self.current_theme['text'])
        self.location_label.grid(row=2, column=0, columnspan=3, pady=5)
        
        # Add project/task selection
        self.task_var = tk.StringVar(value="General Work")
        tk.Label(time_frame, text="Task/Project:", bg=self.current_theme['frame'], 
                fg=self.current_theme['text']).grid(row=3, column=0, pady=5, sticky="e")
        task_menu = ttk.Combobox(time_frame, textvariable=self.task_var, 
                               values=["General Work", "Project A", "Project B", "Meeting", "Training"])
        task_menu.grid(row=3, column=1, columnspan=2, pady=5, sticky="we")
    
    def create_break_section(self, parent):
        """Create break management controls"""
        break_frame = tk.LabelFrame(parent, text="Break Management", font=("Arial", 12, "bold"),
                                   bg=self.current_theme['frame'], fg=self.current_theme['text'], padx=10, pady=10)
        break_frame.pack(fill="x", padx=5, pady=5)
        
        self.start_break_btn = tk.Button(break_frame, text="Start Break", command=self.start_break,
                                        bg=self.current_theme['button'], fg="white", font=("Arial", 12),
                                        activebackground=self.current_theme['button_hover'], width=10, state="disabled")
        self.start_break_btn.grid(row=0, column=0, padx=5, pady=5)
        
        self.end_break_btn = tk.Button(break_frame, text="End Break", command=self.end_break,
                                      bg=self.current_theme['button'], fg="white", font=("Arial", 12),
                                      activebackground=self.current_theme['button_hover'], width=10, state="disabled")
        self.end_break_btn.grid(row=0, column=1, padx=5, pady=5)
        
        self.break_status_label = tk.Label(break_frame, text="Break: Not on break", 
                                          font=("Arial", 12), bg=self.current_theme['frame'], fg=self.current_theme['text'])
        self.break_status_label.grid(row=0, column=2, padx=10, pady=5, sticky="w")
        
        self.break_start_display = tk.Label(break_frame, text="Break Start: --:-- --", 
                                           font=("Arial", 11), bg=self.current_theme['frame'], fg=self.current_theme['text'])
        self.break_start_display.grid(row=1, column=0, padx=5, pady=5)
        
        self.break_end_display = tk.Label(break_frame, text="Break End: --:-- --", 
                                         font=("Arial", 11), bg=self.current_theme['frame'], fg=self.current_theme['text'])
        self.break_end_display.grid(row=1, column=1, padx=5, pady=5)
        
        self.total_break_label = tk.Label(break_frame, text="Total Break: 00:00:00", 
                                          font=("Arial", 11), bg=self.current_theme['frame'], fg=self.current_theme['text'])
        self.total_break_label.grid(row=1, column=2, padx=10, pady=5, sticky="w")
        
        # Break type selection
        self.break_type_var = tk.StringVar(value="Lunch")
        tk.Label(break_frame, text="Break Type:", bg=self.current_theme['frame'], 
                fg=self.current_theme['text']).grid(row=2, column=0, pady=5, sticky="e")
        break_menu = ttk.Combobox(break_frame, textvariable=self.break_type_var, 
                                values=["Lunch", "Short Break", "Meeting", "Personal"])
        break_menu.grid(row=2, column=1, columnspan=2, pady=5, sticky="we")
    
    def create_summary_section(self, parent):
        """Create daily summary section"""
        summary_frame = tk.LabelFrame(parent, text="Daily Summary", font=("Arial", 12, "bold"),
                                     bg=self.current_theme['frame'], fg=self.current_theme['text'], padx=10, pady=10)
        summary_frame.pack(fill="x", padx=5, pady=5)
        
        # Summary labels
        tk.Label(summary_frame, text="Total Work Time:", font=("Arial", 11), 
                bg=self.current_theme['frame'], fg=self.current_theme['text']).grid(row=0, column=0, padx=5, pady=2, sticky="e")
        self.total_work_summary = tk.Label(summary_frame, text="00:00:00", font=("Arial", 11, "bold"), 
                                          bg=self.current_theme['frame'], fg=self.current_theme['text'])
        self.total_work_summary.grid(row=0, column=1, padx=5, pady=2, sticky="w")
        
        tk.Label(summary_frame, text="Total Break Time:", font=("Arial", 11), 
                bg=self.current_theme['frame'], fg=self.current_theme['text']).grid(row=1, column=0, padx=5, pady=2, sticky="e")
        self.total_break_summary = tk.Label(summary_frame, text="00:00:00", font=("Arial", 11, "bold"), 
                                           bg=self.current_theme['frame'], fg=self.current_theme['text'])
        self.total_break_summary.grid(row=1, column=1, padx=5, pady=2, sticky="w")
        
        tk.Label(summary_frame, text="Net Work Time:", font=("Arial", 11), 
                bg=self.current_theme['frame'], fg=self.current_theme['text']).grid(row=2, column=0, padx=5, pady=2, sticky="e")
        self.net_work_summary = tk.Label(summary_frame, text="00:00:00", font=("Arial", 11, "bold"), 
                                        bg=self.current_theme['frame'], fg=self.current_theme['text'])
        self.net_work_summary.grid(row=2, column=1, padx=5, pady=2, sticky="w")
        
        # Overtime calculation
        tk.Label(summary_frame, text="Overtime:", font=("Arial", 11), 
                bg=self.current_theme['frame'], fg=self.current_theme['text']).grid(row=3, column=0, padx=5, pady=2, sticky="e")
        self.overtime_label = tk.Label(summary_frame, text="00:00:00", font=("Arial", 11, "bold"), 
                                      bg=self.current_theme['frame'], fg=self.current_theme['text'])
        self.overtime_label.grid(row=3, column=1, padx=5, pady=2, sticky="w")
        
        # Notes section
        tk.Label(summary_frame, text="Notes:", font=("Arial", 11), 
                bg=self.current_theme['frame'], fg=self.current_theme['text']).grid(row=4, column=0, padx=5, pady=5, sticky="ne")
        
        self.notes_text = tk.Text(summary_frame, height=4, width=50, font=("Arial", 10),
                                bg=self.current_theme['entry_bg'], fg=self.current_theme['text'])
        self.notes_text.grid(row=4, column=1, columnspan=2, padx=5, pady=5, sticky="w")
        
        # Save notes button
        self.save_notes_btn = tk.Button(summary_frame, text="Save Notes", command=self.save_notes,
                                       bg=self.current_theme['button'], fg="white", font=("Arial", 10),
                                       activebackground=self.current_theme['button_hover'])
        self.save_notes_btn.grid(row=5, column=1, padx=5, pady=5, sticky="w")
    
    def create_records_section(self, parent):
        """Create records display section"""
        records_frame = tk.LabelFrame(parent, text="Today's Records", font=("Arial", 12, "bold"),
                                      bg=self.current_theme['frame'], fg=self.current_theme['text'], padx=10, pady=10)
        records_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Create a frame for the treeview and scrollbar
        tree_frame = tk.Frame(records_frame, bg=self.current_theme['frame'])
        tree_frame.pack(fill="both", expand=True)
        
        # Treeview for records
        columns = ("ID", "Type", "Start Time", "End Time", "Duration", "Task", "Details")
        self.records_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=8)
        
        # Configure columns
        self.records_tree.heading("ID", text="ID")
        self.records_tree.column("ID", width=40, anchor="center")
        
        self.records_tree.heading("Type", text="Type")
        self.records_tree.column("Type", width=80, anchor="center")
        
        self.records_tree.heading("Start Time", text="Start Time")
        self.records_tree.column("Start Time", width=120, anchor="center")
        
        self.records_tree.heading("End Time", text="End Time")
        self.records_tree.column("End Time", width=120, anchor="center")
        
        self.records_tree.heading("Duration", text="Duration")
        self.records_tree.column("Duration", width=80, anchor="center")
        
        self.records_tree.heading("Task", text="Task/Project")
        self.records_tree.column("Task", width=100, anchor="center")
        
        self.records_tree.heading("Details", text="Details")
        self.records_tree.column("Details", width=150)
        
        self.records_tree.pack(side="left", fill="both", expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.records_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.records_tree.configure(yscrollcommand=scrollbar.set)
        
        # Context menu
        self.record_context_menu = tk.Menu(self.root, tearoff=0)
        self.record_context_menu.add_command(label="Edit Record", command=self.on_edit_record)
        self.record_context_menu.add_command(label="Delete Record", command=self.on_delete_record)
        self.record_context_menu.add_separator()
        self.record_context_menu.add_command(label="Add Note", command=self.add_note_to_record)
        
        # Bind right-click event
        self.records_tree.bind("<Button-3>", self.show_record_context_menu)
        # Bind double-click for quick edit
        self.records_tree.bind("<Double-1>", self.on_record_double_click)
    
    def create_analytics_section(self, parent):
        """Create analytics and visualization section"""
        analytics_frame = tk.LabelFrame(parent, text="Time Analytics", font=("Arial", 12, "bold"),
                                      bg=self.current_theme['frame'], fg=self.current_theme['text'], padx=10, pady=10)
        analytics_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Tab control for different analytics views
        self.analytics_notebook = ttk.Notebook(analytics_frame)
        self.analytics_notebook.pack(fill="both", expand=True)
        
        # Daily analytics tab
        daily_tab = ttk.Frame(self.analytics_notebook)
        self.analytics_notebook.add(daily_tab, text="Today")
        
        # Weekly analytics tab
        weekly_tab = ttk.Frame(self.analytics_notebook)
        self.analytics_notebook.add(weekly_tab, text="This Week")
        
        # Monthly analytics tab
        monthly_tab = ttk.Frame(self.analytics_notebook)
        self.analytics_notebook.add(monthly_tab, text="This Month")
        
        # Project analytics tab
        project_tab = ttk.Frame(self.analytics_notebook)
        self.analytics_notebook.add(project_tab, text="By Project")
        
        # Create charts (will be populated with data)
        self.create_daily_analytics(daily_tab)
        self.create_weekly_analytics(weekly_tab)
        self.create_monthly_analytics(monthly_tab)
        self.create_project_analytics(project_tab)
    
    def create_daily_analytics(self, parent):
        """Create daily analytics charts"""
        # Time distribution pie chart
        fig, ax = plt.subplots(figsize=(5, 3), dpi=100)
        ax.set_title("Today's Time Distribution")
        self.daily_pie_canvas = FigureCanvasTkAgg(fig, master=parent)
        self.daily_pie_canvas.get_tk_widget().pack(side="left", fill="both", expand=True)
        
        # Productivity timeline
        fig2, ax2 = plt.subplots(figsize=(5, 3), dpi=100)
        ax2.set_title("Productivity Timeline")
        self.daily_timeline_canvas = FigureCanvasTkAgg(fig2, master=parent)
        self.daily_timeline_canvas.get_tk_widget().pack(side="right", fill="both", expand=True)
    
    def create_weekly_analytics(self, parent):
        """Create weekly analytics charts"""
        fig, ax = plt.subplots(figsize=(5, 3), dpi=100)
        ax.set_title("Weekly Work Hours")
        self.weekly_bar_canvas = FigureCanvasTkAgg(fig, master=parent)
        self.weekly_bar_canvas.get_tk_widget().pack(fill="both", expand=True)
    
    def create_monthly_analytics(self, parent):
        """Create monthly analytics charts"""
        fig, ax = plt.subplots(figsize=(5, 3), dpi=100)
        ax.set_title("Monthly Overview")
        self.monthly_line_canvas = FigureCanvasTkAgg(fig, master=parent)
        self.monthly_line_canvas.get_tk_widget().pack(fill="both", expand=True)
    
    def create_project_analytics(self, parent):
        """Create project-based analytics charts"""
        fig, ax = plt.subplots(figsize=(5, 3), dpi=100)
        ax.set_title("Time by Project")
        self.project_pie_canvas = FigureCanvasTkAgg(fig, master=parent)
        self.project_pie_canvas.get_tk_widget().pack(fill="both", expand=True)
    
    def create_status_bar(self):
        """Create application status bar"""
        self.status_bar = tk.Label(self.root, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W,
                                 bg=self.current_theme['frame'], fg=self.current_theme['text'])
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def update_status(self, message):
        """Update status bar message"""
        self.status_bar.config(text=message)
        self.root.update_idletasks()
    
    def clear_window(self):
        """Clear all widgets from the root window."""
        # Cancel the clock update if it is scheduled
        if hasattr(self, 'clock_update_id') and self.clock_update_id:
            self.root.after_cancel(self.clock_update_id)
            self.clock_update_id = None
    
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def load_records(self):
        """Load records for the current user."""
        user_dir = f"users/{self.current_user}"
        records_file = f"{user_dir}/records.json"
        
        if os.path.exists(records_file):
            with open(records_file, "r") as f:
                data = json.load(f)
                
                # Load work sessions
                self.work_sessions = []
                for session in data.get("work_sessions", []):
                    start = datetime.fromisoformat(session['start']) if session['start'] else None
                    end = datetime.fromisoformat(session['end']) if session['end'] else None
                    self.work_sessions.append({
                        'date': self.current_date,
                        'start': start,
                        'end': end,
                        'task': session.get('task', 'General Work')
                    })
                
                # Load break sessions
                self.break_sessions = []
                for session in data.get("break_sessions", []):
                    start = datetime.fromisoformat(session['start']) if session['start'] else None
                    end = datetime.fromisoformat(session['end']) if session['end'] else None
                    self.break_sessions.append({
                        'date': self.current_date,
                        'start': start,
                        'end': end,
                        'type': session.get('type', 'Lunch')
                    })
        
        # Update UI if widgets exist
        if hasattr(self, 'records_tree'):
            self.update_records()
            self.update_summary()
    
    def update_records(self):
        """Update the records displayed in the Treeview."""
        # Clear existing records
        for item in self.records_tree.get_children():
            self.records_tree.delete(item)
        
        # Add work sessions
        for idx, session in enumerate(self.work_sessions):
            start_time = session['start'].strftime('%I:%M:%S %p') if session['start'] else "--:-- --"
            end_time = session['end'].strftime('%I:%M:%S %p') if session['end'] else "--:-- --"
            duration = str(session['end'] - session['start']).split('.')[0] if session['start'] and session['end'] else "In progress"
            self.records_tree.insert("", "end", values=(
                idx + 1, 
                "Work", 
                start_time, 
                end_time, 
                duration, 
                session.get('task', 'General Work'),
                ""
            ))
        
        # Add break sessions
        for idx, session in enumerate(self.break_sessions):
            start_time = session['start'].strftime('%I:%M:%S %p') if session['start'] else "--:-- --"
            end_time = session['end'].strftime('%I:%M:%S %p') if session['end'] else "--:-- --"
            duration = str(session['end'] - session['start']).split('.')[0] if session['start'] and session['end'] else "In progress"
            self.records_tree.insert("", "end", values=(
                idx + 1, 
                "Break", 
                start_time, 
                end_time, 
                duration, 
                session.get('type', 'Lunch'),
                ""
            ))
    
    def update_summary(self):
        """Update the daily summary section."""
        if not hasattr(self, 'total_work_summary'):
            return
            
        # Calculate total worked time
        total_worked = timedelta()
        for session in self.work_sessions:
            if session['start'] and session['end']:
                total_worked += (session['end'] - session['start'])
        
        # Calculate total break time
        total_break = timedelta()
        for session in self.break_sessions:
            if session['start'] and session['end']:
                total_break += (session['end'] - session['start'])
        
        # Calculate net work time
        net_work = total_worked - total_break
        
        # Calculate overtime
        overtime = timedelta()
        if total_worked > timedelta(hours=self.settings['work_hours_per_day']):
            overtime = total_worked - timedelta(hours=self.settings['work_hours_per_day'])
        
        # Update UI labels
        self.total_work_summary.config(text=str(total_worked).split('.')[0])
        self.total_break_summary.config(text=str(total_break).split('.')[0])
        self.net_work_summary.config(text=str(net_work).split('.')[0])
        self.overtime_label.config(text=str(overtime).split('.')[0])
    
    def clock_in(self):
        """Record clock-in time"""
        self.clock_in_time = datetime.now()
        self.clock_in_display.config(text=f"Clock In: {self.clock_in_time.strftime('%I:%M %p')}")
        self.status_label.config(text="Status: Clocked in")
        self.clock_in_btn.config(state="disabled")
        self.clock_out_btn.config(state="normal")
        self.start_break_btn.config(state="normal")
        
        # Add to work sessions
        self.work_sessions.append({
            'date': self.current_date,
            'start': self.clock_in_time,
            'end': None,
            'task': self.task_var.get()
        })
        
        self.update_records()
        self.save_records()
    
    def clock_out(self):
        """Record clock-out time"""
        self.clock_out_time = datetime.now()
        self.clock_out_display.config(text=f"Clock Out: {self.clock_out_time.strftime('%I:%M %p')}")
        self.status_label.config(text="Status: Clocked out")
        self.clock_out_btn.config(state="disabled")
        self.start_break_btn.config(state="disabled")
        self.end_break_btn.config(state="disabled")
        
        # Update last work session
        if self.work_sessions:
            self.work_sessions[-1]['end'] = self.clock_out_time
        
        self.update_records()
        self.update_summary()
        self.save_records()
    
    def start_break(self):
        """Record break start time"""
        self.break_start_time = datetime.now()
        self.break_start_display.config(text=f"Break Start: {self.break_start_time.strftime('%I:%M %p')}")
        self.break_status_label.config(text="Break: On break")
        self.start_break_btn.config(state="disabled")
        self.end_break_btn.config(state="normal")
        
        # Add to break sessions
        self.break_sessions.append({
            'date': self.current_date,
            'start': self.break_start_time,
            'end': None,
            'type': self.break_type_var.get()
        })
        
        self.update_records()
        self.save_records()
    
    def end_break(self):
        """Record break end time"""
        self.break_end_time = datetime.now()
        self.break_end_display.config(text=f"Break End: {self.break_end_time.strftime('%I:%M %p')}")
        self.break_status_label.config(text="Break: Not on break")
        self.end_break_btn.config(state="disabled")
        self.start_break_btn.config(state="normal")
        
        # Update last break session
        if self.break_sessions:
            self.break_sessions[-1]['end'] = self.break_end_time
        
        self.update_records()
        self.update_summary()
        self.save_records()
    
    def save_notes(self):
        """Save user notes"""
        notes = self.notes_text.get("1.0", "end-1c")
        messagebox.showinfo("Notes Saved", "Your notes have been saved for this session.")
    
    def save_records(self):
        """Save records to file"""
        user_dir = f"users/{self.current_user}"
        if not os.path.exists(user_dir):
            os.makedirs(user_dir)
        
        data = {
            "work_sessions": [],
            "break_sessions": [],
            "notes": self.notes_text.get("1.0", "end-1c")
        }
        
        for session in self.work_sessions:
            data["work_sessions"].append({
                "start": session['start'].isoformat() if session['start'] else None,
                "end": session['end'].isoformat() if session['end'] else None,
                "task": session.get('task', 'General Work')
            })
        
        for session in self.break_sessions:
            data["break_sessions"].append({
                "start": session['start'].isoformat() if session['start'] else None,
                "end": session['end'].isoformat() if session['end'] else None,
                "type": session.get('type', 'Lunch')
            })
        
        with open(f"{user_dir}/records.json", "w") as f:
            json.dump(data, f, indent=4)
    
    def export_to_csv(self):
        """Export records to CSV file"""
        file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                filetypes=[("CSV files", "*.csv")],
                                                title="Save as CSV")
        if file_path:
            with open(file_path, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Type", "Date", "Start Time", "End Time", "Duration", "Task/Type", "Details"])
                
                for session in self.work_sessions:
                    start_time = session['start'].strftime('%I:%M:%S %p') if session['start'] else ""
                    end_time = session['end'].strftime('%I:%M:%S %p') if session['end'] else ""
                    duration = str(session['end'] - session['start']).split('.')[0] if session['end'] else ""
                    writer.writerow(["Work", session['date'], start_time, end_time, duration, session.get('task', 'General Work'), ""])
                
                for session in self.break_sessions:
                    start_time = session['start'].strftime('%I:%M:%S %p') if session['start'] else ""
                    end_time = session['end'].strftime('%I:%M:%S %p') if session['end'] else ""
                    duration = str(session['end'] - session['start']).split('.')[0] if session['end'] else ""
                    writer.writerow(["Break", session['date'], start_time, end_time, duration, session.get('type', 'Lunch'), ""])
            
            messagebox.showinfo("Export Successful", f"Data exported to {file_path}")
    
    def export_to_json(self):
        """Export records to JSON file"""
        file_path = filedialog.asksaveasfilename(defaultextension=".json",
                                                filetypes=[("JSON files", "*.json")],
                                                title="Save as JSON")
        if file_path:
            data = {
                "date": str(self.current_date),
                "work_sessions": [],
                "break_sessions": [],
                "notes": self.notes_text.get("1.0", "end-1c")
            }
            
            for session in self.work_sessions:
                data["work_sessions"].append({
                    "start": session['start'].isoformat() if session['start'] else None,
                    "end": session['end'].isoformat() if session['end'] else None,
                    "task": session.get('task', 'General Work'),
                    "duration": str(session['end'] - session['start']) if session['end'] else None
                })
            
            for session in self.break_sessions:
                data["break_sessions"].append({
                    "start": session['start'].isoformat() if session['start'] else None,
                    "end": session['end'].isoformat() if session['end'] else None,
                    "type": session.get('type', 'Lunch'),
                    "duration": str(session['end'] - session['start']) if session['end'] else None
                })
            
            with open(file_path, 'w') as file:
                json.dump(data, file, indent=4)
            
            messagebox.showinfo("Export Successful", f"Data exported to {file_path}")
    
    def print_summary(self):
        """Generate printable summary"""
        html = f"""
        <html>
        <head>
            <title>Daily Time Record - {self.current_date}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #0078d7; }}
                table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #e6f2ff; }}
                .summary {{ background-color: #f5f5f5; padding: 15px; margin-bottom: 20px; }}
            </style>
        </head>
        <body>
            <h1>Daily Time Record - {self.current_date}</h1>
            
            <div class="summary">
                <h2>Summary</h2>
                <p><strong>Total Work Time:</strong> {self.total_work_summary.cget("text")}</p>
                <p><strong>Total Break Time:</strong> {self.total_break_summary.cget("text")}</p>
                <p><strong>Net Work Time:</strong> {self.net_work_summary.cget("text")}</p>
                <p><strong>Overtime:</strong> {self.overtime_label.cget("text")}</p>
            </div>
            
            <h2>Time Records</h2>
            <table>
                <tr>
                    <th>Type</th>
                    <th>Start Time</th>
                    <th>End Time</th>
                    <th>Duration</th>
                    <th>Task/Type</th>
                </tr>
        """
        
        for session in self.work_sessions:
            start_time = session['start'].strftime('%I:%M:%S %p') if session['start'] else "--:-- --"
            end_time = session['end'].strftime('%I:%M:%S %p') if session['end'] else "--:-- --"
            duration = str(session['end'] - session['start']).split('.')[0] if session['end'] else "In progress"
            html += f"""
                <tr>
                    <td>Work</td>
                    <td>{start_time}</td>
                    <td>{end_time}</td>
                    <td>{duration}</td>
                    <td>{session.get('task', 'General Work')}</td>
                </tr>
            """
        
        for session in self.break_sessions:
            start_time = session['start'].strftime('%I:%M:%S %p') if session['start'] else "--:-- --"
            end_time = session['end'].strftime('%I:%M:%S %p') if session['end'] else "--:-- --"
            duration = str(session['end'] - session['start']).split('.')[0] if session['end'] else "In progress"
            html += f"""
                <tr>
                    <td>Break</td>
                    <td>{start_time}</td>
                    <td>{end_time}</td>
                    <td>{duration}</td>
                    <td>{session.get('type', 'Lunch')}</td>
                </tr>
            """
        
        html += f"""
            </table>
            
            <h2>Notes</h2>
            <p>{self.notes_text.get("1.0", "end-1c") or "No notes recorded."}</p>
            
            <p style="margin-top: 30px;">Generated on {datetime.now().strftime('%Y-%m-%d %I:%M %p')}</p>
        </body>
        </html>
        """
        
        temp_file = "temp_summary.html"
        with open(temp_file, "w") as f:
            f.write(html)
        
        webbrowser.open(temp_file)
    
    def backup_data(self):
        """Backup user data to cloud"""
        messagebox.showinfo("Backup", "This feature would backup your data to the cloud in a real implementation")
    
    def restore_data(self):
        """Restore user data from cloud"""
        messagebox.showinfo("Restore", "This feature would restore your data from the cloud in a real implementation")
    
    def open_settings(self):
        """Open settings dialog"""
        messagebox.showinfo("Settings", "This would open a settings dialog in a real implementation")
    
    def logout(self):
        """Log out current user"""
        self.current_user = None
        self.initialize_data()
        self.create_login_screen()
    
    def generate_report(self, report_type):
        """Generate different types of reports"""
        messagebox.showinfo("Report", f"This would generate a {report_type} report in a real implementation")
    
    def calculate_overtime(self):
        """Calculate overtime hours"""
        messagebox.showinfo("Overtime", "This would calculate overtime hours in a real implementation")
    
    def show_time_analysis(self):
        """Show time analysis"""
        messagebox.showinfo("Time Analysis", "This would show time analysis in a real implementation")
    
    def show_productivity_stats(self):
        """Show productivity statistics"""
        messagebox.showinfo("Productivity", "This would show productivity stats in a real implementation")
    
    def show_user_guide(self):
        """Show user guide"""
        messagebox.showinfo("User Guide", "This would show the user guide in a real implementation")
    
    def show_about(self):
        """Show about dialog"""
        messagebox.showinfo("About", "Advanced Time Record System\nVersion 1.0")
    
    def on_edit_record(self):
        """Edit selected record"""
        selected_item = self.records_tree.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a record to edit")
            return
        
        item = self.records_tree.item(selected_item[0])
        record_id = int(item['values'][0]) - 1
        record_type = item['values'][1]
        
        self.edit_record(record_id, record_type)
    
    def on_delete_record(self):
        """Delete selected record"""
        selected_item = self.records_tree.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a record to delete")
            return
        
        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this record?"):
            return
        
        item = self.records_tree.item(selected_item[0])
        record_id = int(item['values'][0]) - 1
        record_type = item['values'][1]
        
        if record_type == "Work":
            if record_id < len(self.work_sessions):
                del self.work_sessions[record_id]
        else:
            if record_id < len(self.break_sessions):
                del self.break_sessions[record_id]
        
        self.update_records()
        self.update_summary()
        self.save_records()
    
    def add_note_to_record(self):
        """Add note to selected record"""
        selected_item = self.records_tree.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a record to add a note")
            return
        
        note = simpledialog.askstring("Add Note", "Enter note for this record:")
        if note:
            # In a real implementation, you would store this note with the record
            messagebox.showinfo("Note Added", "Note has been added to the record")
    
    def show_record_context_menu(self, event):
        """Show context menu for records"""
        item = self.records_tree.identify('item', event.x, event.y)
        if item:
            self.records_tree.selection_set(item)
            self.record_context_menu.post(event.x_root, event.y_root)
    
    def on_record_double_click(self, event):
        """Handle double-click on record"""
        self.on_edit_record()
    
    def edit_record(self, record_id, record_type):
        """Edit a specific record"""
        if record_type == "Work":
            if record_id >= len(self.work_sessions):
                return
            session = self.work_sessions[record_id]
        else:
            if record_id >= len(self.break_sessions):
                return
            session = self.break_sessions[record_id]
        
        edit_dialog = tk.Toplevel(self.root)
        edit_dialog.title(f"Edit {record_type} Record")
        edit_dialog.geometry("400x300")
        edit_dialog.resizable(False, False)
        edit_dialog.grab_set()
        
        # Start time
        tk.Label(edit_dialog, text="Start Time:", font=("Arial", 11)).pack(pady=(10, 0))
        start_time_str = session['start'].strftime("%Y-%m-%d %H:%M:%S") if session['start'] else ""
        start_time_entry = tk.Entry(edit_dialog, font=("Arial", 11), width=25)
        start_time_entry.insert(0, start_time_str)
        start_time_entry.pack(pady=5)
        
        # End time
        tk.Label(edit_dialog, text="End Time:", font=("Arial", 11)).pack(pady=(10, 0))
        end_time_str = session['end'].strftime("%Y-%m-%d %H:%M:%S") if session['end'] else ""
        end_time_entry = tk.Entry(edit_dialog, font=("Arial", 11), width=25)
        end_time_entry.insert(0, end_time_str)
        end_time_entry.pack(pady=5)
        
        # Task/Type
        tk.Label(edit_dialog, text=f"{'Task' if record_type == 'Work' else 'Type'}:", 
                font=("Arial", 11)).pack(pady=(10, 0))
        task_type_var = tk.StringVar(value=session.get('task', 'General Work') if record_type == 'Work' else session.get('type', 'Lunch'))
        if record_type == "Work":
            task_menu = ttk.Combobox(edit_dialog, textvariable=task_type_var, 
                                   values=["General Work", "Project A", "Project B", "Meeting", "Training"])
        else:
            task_menu = ttk.Combobox(edit_dialog, textvariable=task_type_var, 
                                   values=["Lunch", "Short Break", "Meeting", "Personal"])
        task_menu.pack(pady=5)
        
        # Format hint
        tk.Label(edit_dialog, text="Format: YYYY-MM-DD HH:MM:SS", font=("Arial", 9), fg="gray").pack()
        
        def save_changes():
            try:
                # Parse start time
                start_str = start_time_entry.get()
                new_start = datetime.strptime(start_str, "%Y-%m-%d %H:%M:%S") if start_str else None
                
                # Parse end time
                end_str = end_time_entry.get()
                new_end = datetime.strptime(end_str, "%Y-%m-%d %H:%M:%S") if end_str else None
                
                # Validate times
                if new_start and new_end and new_start > new_end:
                    messagebox.showerror("Invalid Times", "Start time cannot be after end time")
                    return
                
                # Update the record
                if record_type == "Work":
                    self.work_sessions[record_id]['start'] = new_start
                    self.work_sessions[record_id]['end'] = new_end
                    self.work_sessions[record_id]['task'] = task_type_var.get()
                else:
                    self.break_sessions[record_id]['start'] = new_start
                    self.break_sessions[record_id]['end'] = new_end
                    self.break_sessions[record_id]['type'] = task_type_var.get()
                
                # Update UI and save
                self.update_records()
                self.update_summary()
                self.save_records()
                
                edit_dialog.destroy()
                messagebox.showinfo("Success", "Record updated successfully")
                
            except ValueError:
                messagebox.showerror("Invalid Format", "Please use the format: YYYY-MM-DD HH:MM:SS")
        
        save_btn = tk.Button(edit_dialog, text="Save Changes", command=save_changes,
                            bg=self.current_theme['button'], fg="white", font=("Arial", 10),
                            activebackground=self.current_theme['button_hover'])
        save_btn.pack(pady=20)
    
    def update_clock(self):
        """Update the clock display"""
        now = datetime.now()
        current_time = now.strftime("%I:%M:%S %p")
        self.clock_label.config(text=current_time)
        
        # Update worked time if clocked in
        if self.clock_in_time and not self.clock_out_time:
            if self.break_start_time and not self.break_end_time:
                # On break, don't count this time
                pass
            else:
                worked_time = now - self.clock_in_time
                # Subtract break times
                for break_session in self.break_sessions:
                    if break_session['end']:
                        worked_time -= (break_session['end'] - break_session['start'])
                self.total_worked_label.config(text=f"Total Worked: {str(worked_time).split('.')[0]}")
    
        # Schedule the next clock update
        self.clock_update_id = self.root.after(1000, self.update_clock)

    def load_summaries(self):
        """Load weekly and monthly summary data"""
        user_dir = f"users/{self.current_user}"
        
        # Load weekly summary
        weekly_file = f"{user_dir}/weekly_summary.json"
        if os.path.exists(weekly_file):
            with open(weekly_file, "r") as f:
                self.weekly_data = json.load(f)
        
        # Load monthly summary
        monthly_file = f"{user_dir}/monthly_summary.json"
        if os.path.exists(monthly_file):
            with open(monthly_file, "r") as f:
                self.monthly_data = json.load(f)
                
    def on_close(self):
        """Handle application close event."""
        if hasattr(self, 'clock_update_id') and self.clock_update_id:
            self.root.after_cancel(self.clock_update_id)  # Cancel the scheduled clock update

        # CLI progress indicator
        print("Closing the program", end="", flush=True)
        for _ in range(5):  # Simulate a 5-step progress
            print(".", end="", flush=True)
            time.sleep(0.5)  # Delay for half a second
        print(" Done!")

        print("Program is closing...")
        self.root.destroy()  # Close the application
        
if __name__ == "__main__":
    root = tk.Tk()
    app = AdvancedTimeRecordApp(root)
    root.mainloop()