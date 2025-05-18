import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd

class SleepTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sleep Tracker")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f0f0")
        
        # Initialize database
        self.init_database()
        
        # User state
        self.current_user_id = None
        self.is_logged_in = False
        
        # Create authentication frame
        self.auth_frame = ttk.Frame(self.root, padding=20)
        self.auth_frame.pack(fill=tk.BOTH, expand=True)
        
        self.show_login_screen()
    
    def init_database(self):
        """Initialize the SQLite database with required tables."""
        try:
            # Connect to database (creates it if it doesn't exist)
            conn = sqlite3.connect('sleep_tracker.db')
            cursor = conn.cursor()
            
            # Create Users table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS Users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                name TEXT,
                email TEXT,
                date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # Create Sleep_Sessions table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS Sleep_Sessions (
                session_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                sleep_start_time TIMESTAMP NOT NULL,
                sleep_end_time TIMESTAMP,
                duration INTEGER,
                date DATE NOT NULL,
                FOREIGN KEY (user_id) REFERENCES Users (user_id)
            )
            ''')
            
            # Create Sleep_Quality table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS Sleep_Quality (
                quality_id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                rating INTEGER CHECK (rating >= 1 AND rating <= 10),
                times_woken INTEGER DEFAULT 0,
                notes TEXT,
                FOREIGN KEY (session_id) REFERENCES Sleep_Sessions (session_id)
            )
            ''')
            
            # Create Sleep_Factors table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS Sleep_Factors (
                factor_id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                caffeine_intake BOOLEAN DEFAULT 0,
                exercise BOOLEAN DEFAULT 0,
                screen_time_before_bed INTEGER DEFAULT 0,
                stress_level INTEGER CHECK (stress_level >= 1 AND stress_level <= 10),
                FOREIGN KEY (session_id) REFERENCES Sleep_Sessions (session_id)
            )
            ''')
            
            conn.commit()
            conn.close()
            print("Database initialized successfully")
        except Exception as e:
            print(f"Error initializing database: {e}")
    
    def show_login_screen(self):
        """Display the login screen."""
        # Clear the frame
        for widget in self.auth_frame.winfo_children():
            widget.destroy()
        
        # Create login widgets
        ttk.Label(self.auth_frame, text="Sleep Tracker", font=("Arial", 20)).pack(pady=10)
        
        ttk.Label(self.auth_frame, text="Username:").pack(pady=5)
        self.username_entry = ttk.Entry(self.auth_frame, width=30)
        self.username_entry.pack(pady=5)
        
        ttk.Label(self.auth_frame, text="Password:").pack(pady=5)
        self.password_entry = ttk.Entry(self.auth_frame, width=30, show="*")
        self.password_entry.pack(pady=5)
        
        ttk.Button(self.auth_frame, text="Login", command=self.login).pack(pady=10)
        ttk.Button(self.auth_frame, text="Register", command=self.show_register_screen).pack(pady=5)
    
    def show_register_screen(self):
        """Display the registration screen."""
        # Clear the frame
        for widget in self.auth_frame.winfo_children():
            widget.destroy()
        
        # Create registration widgets
        ttk.Label(self.auth_frame, text="Register New Account", font=("Arial", 20)).pack(pady=10)
        
        ttk.Label(self.auth_frame, text="Username:").pack(pady=5)
        self.reg_username_entry = ttk.Entry(self.auth_frame, width=30)
        self.reg_username_entry.pack(pady=5)
        
        ttk.Label(self.auth_frame, text="Password:").pack(pady=5)
        self.reg_password_entry = ttk.Entry(self.auth_frame, width=30, show="*")
        self.reg_password_entry.pack(pady=5)
        
        ttk.Label(self.auth_frame, text="Name:").pack(pady=5)
        self.reg_name_entry = ttk.Entry(self.auth_frame, width=30)
        self.reg_name_entry.pack(pady=5)
        
        ttk.Label(self.auth_frame, text="Email:").pack(pady=5)
        self.reg_email_entry = ttk.Entry(self.auth_frame, width=30)
        self.reg_email_entry.pack(pady=5)
        
        ttk.Button(self.auth_frame, text="Register", command=self.register).pack(pady=10)
        ttk.Button(self.auth_frame, text="Back to Login", command=self.show_login_screen).pack(pady=5)
    
    def register(self):
        """Register a new user."""
        username = self.reg_username_entry.get()
        password = self.reg_password_entry.get()
        name = self.reg_name_entry.get()
        email = self.reg_email_entry.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Username and password are required")
            return
        
        try:
            conn = sqlite3.connect('sleep_tracker.db')
            cursor = conn.cursor()
            
            # Check if username already exists
            cursor.execute("SELECT user_id FROM Users WHERE username = ?", (username,))
            if cursor.fetchone():
                messagebox.showerror("Error", "Username already exists")
                conn.close()
                return
            
            # Insert new user
            cursor.execute(
                "INSERT INTO Users (username, password, name, email) VALUES (?, ?, ?, ?)",
                (username, password, name, email)
            )
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", "Registration successful! You can now login.")
            self.show_login_screen()
        except Exception as e:
            messagebox.showerror("Error", f"Registration failed: {e}")
    
    def login(self):
        """Authenticate the user and show the main app if successful."""
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Username and password are required")
            return
        
        try:
            conn = sqlite3.connect('sleep_tracker.db')
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT user_id FROM Users WHERE username = ? AND password = ?",
                (username, password)
            )
            user = cursor.fetchone()
            conn.close()
            
            if user:
                self.current_user_id = user[0]
                self.is_logged_in = True
                self.show_main_app()
            else:
                messagebox.showerror("Error", "Invalid username or password")
        except Exception as e:
            messagebox.showerror("Error", f"Login failed: {e}")
    
    def show_main_app(self):
        """Display the main application after successful login."""
        # Destroy the authentication frame
        self.auth_frame.destroy()
        
        # Create main app frame
        self.main_frame = ttk.Frame(self.root, padding=20)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create dashboard frame
        self.dashboard_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.dashboard_frame, text="Dashboard")
        
        # Create record sleep tab
        self.create_record_sleep_tab()
        
        # Initialize dashboard
        self.update_dashboard()
        
        # Logout button
        ttk.Button(self.main_frame, text="Logout", command=self.logout).pack(pady=10)
    
    def update_dashboard(self):
        """Update the dashboard with current sleep data."""
        # Clear existing widgets
        for widget in self.dashboard_frame.winfo_children():
            widget.destroy()
        
        ttk.Label(self.dashboard_frame, text="Sleep Dashboard", font=("Arial", 16)).pack(pady=10)
        
        # Create left and right frames for layout
        left_frame = ttk.Frame(self.dashboard_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        right_frame = ttk.Frame(self.dashboard_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        
        # Summary stats in left frame
        stats_frame = ttk.LabelFrame(left_frame, text="Sleep Summary", padding=10)
        stats_frame.pack(fill=tk.X, pady=5)
        
        # Get sleep data
        try:
            conn = sqlite3.connect('sleep_tracker.db')
            cursor = conn.cursor()
            
            # Get average sleep duration for last 7 days
            cursor.execute('''
            SELECT AVG(duration) FROM Sleep_Sessions
            WHERE user_id = ? AND date >= date('now', '-7 days')
            ''', (self.current_user_id,))
            avg_duration = cursor.fetchone()[0]
            
            # Get average sleep quality for last 7 days
            cursor.execute('''
            SELECT AVG(sq.rating) FROM Sleep_Quality sq
            JOIN Sleep_Sessions ss ON sq.session_id = ss.session_id
            WHERE ss.user_id = ? AND ss.date >= date('now', '-7 days')
            ''', (self.current_user_id,))
            avg_quality = cursor.fetchone()[0]
            
            # Get last sleep session
            cursor.execute('''
            SELECT sleep_start_time, sleep_end_time, duration
            FROM Sleep_Sessions
            WHERE user_id = ?
            ORDER BY sleep_start_time DESC
            LIMIT 1
            ''', (self.current_user_id,))
            last_session = cursor.fetchone()
            
            conn.close()
            
            # Display stats
            if avg_duration:
                avg_hours = round(avg_duration / 60, 1)
                ttk.Label(stats_frame, text=f"Average Sleep Duration (7 days): {avg_hours} hours").pack(anchor="w", pady=2)
            else:
                ttk.Label(stats_frame, text="Average Sleep Duration (7 days): No data").pack(anchor="w", pady=2)
            
            if avg_quality:
                ttk.Label(stats_frame, text=f"Average Sleep Quality (7 days): {round(avg_quality, 1)}/10").pack(anchor="w", pady=2)
            else:
                ttk.Label(stats_frame, text="Average Sleep Quality (7 days): No data").pack(anchor="w", pady=2)
            
            if last_session:
                start_time = datetime.strptime(last_session[0], "%Y-%m-%d %H:%M:%S")
                end_time = datetime.strptime(last_session[1], "%Y-%m-%d %H:%M:%S") if last_session[1] else "In progress"
                duration = f"{round(last_session[2] / 60, 1)} hours" if last_session[2] else "In progress"
                
                ttk.Label(stats_frame, text=f"Last Sleep Session:").pack(anchor="w", pady=2)
                ttk.Label(stats_frame, text=f"  Start: {start_time.strftime('%Y-%m-%d %H:%M')}").pack(anchor="w", pady=2)
                ttk.Label(stats_frame, text=f"  End: {end_time.strftime('%Y-%m-%d %H:%M') if isinstance(end_time, datetime) else end_time}").pack(anchor="w", pady=2)
                ttk.Label(stats_frame, text=f"  Duration: {duration}").pack(anchor="w", pady=2)
            else:
                ttk.Label(stats_frame, text="Last Sleep Session: No data").pack(anchor="w", pady=2)
        
        except Exception as e:
            ttk.Label(stats_frame, text=f"Error retrieving sleep data: {e}").pack(anchor="w", pady=2)
        
        # Quick actions in left frame
        actions_frame = ttk.LabelFrame(left_frame, text="Quick Actions", padding=10)
        actions_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(actions_frame, text="Start Sleep Session", command=self.start_sleep_session).pack(pady=5)
        ttk.Button(actions_frame, text="End Current Session", command=self.end_sleep_session).pack(pady=5)
        
        # Sleep history in right frame
        history_frame = ttk.LabelFrame(right_frame, text="Recent Sleep History", padding=10)
        history_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Create treeview for sleep records
        columns = ("date", "start_time", "end_time", "duration", "quality")
        self.history_tree = ttk.Treeview(history_frame, columns=columns, show="headings", height=6)
        
        # Define headings
        self.history_tree.heading("date", text="Date")
        self.history_tree.heading("start_time", text="Start Time")
        self.history_tree.heading("end_time", text="End Time")
        self.history_tree.heading("duration", text="Duration (hrs)")
        self.history_tree.heading("quality", text="Quality (1-10)")
        
        # Define columns
        self.history_tree.column("date", width=100)
        self.history_tree.column("start_time", width=100)
        self.history_tree.column("end_time", width=100)
        self.history_tree.column("duration", width=100)
        self.history_tree.column("quality", width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.history_tree.yview)
        self.history_tree.configure(yscroll=scrollbar.set)
        
        # Pack treeview and scrollbar
        self.history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Statistics in right frame
        stats_frame = ttk.LabelFrame(right_frame, text="Sleep Statistics", padding=10)
        stats_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Time range selection
        range_frame = ttk.Frame(stats_frame)
        range_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(range_frame, text="Time Range:").pack(side=tk.LEFT, padx=5)
        self.time_range = ttk.Combobox(range_frame, width=15, 
                                     values=["Last 7 Days", "Last 30 Days", "Last 90 Days", "All Time"])
        self.time_range.pack(side=tk.LEFT, padx=5)
        self.time_range.set("Last 7 Days")
        
        ttk.Button(range_frame, text="Generate Statistics", command=self.generate_statistics).pack(side=tk.LEFT, padx=5)
        
        # Frame for charts
        self.charts_frame = ttk.Frame(stats_frame)
        self.charts_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Load initial data
        self.load_sleep_history()
        self.generate_statistics()
    
    def create_record_sleep_tab(self):
        """Create the tab for recording sleep sessions."""
        record_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(record_frame, text="Record Sleep")
        
        ttk.Label(record_frame, text="Record Sleep Session", font=("Arial", 16)).pack(pady=10)
        
        # Date selection
        date_frame = ttk.Frame(record_frame)
        date_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(date_frame, text="Date:").pack(side=tk.LEFT, padx=5)
        self.date_entry = ttk.Entry(date_frame, width=10)
        self.date_entry.pack(side=tk.LEFT, padx=5)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # Sleep time entries
        time_frame = ttk.Frame(record_frame)
        time_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(time_frame, text="Sleep Start:").grid(row=0, column=0, padx=5, pady=5)
        self.sleep_start_hour = ttk.Combobox(time_frame, width=2, values=[f"{i:02d}" for i in range(24)])
        self.sleep_start_hour.grid(row=0, column=1, padx=2, pady=5)
        self.sleep_start_hour.set("22")
        
        ttk.Label(time_frame, text=":").grid(row=0, column=2)
        
        self.sleep_start_min = ttk.Combobox(time_frame, width=2, values=[f"{i:02d}" for i in range(0, 60, 5)])
        self.sleep_start_min.grid(row=0, column=3, padx=2, pady=5)
        self.sleep_start_min.set("00")
        
        ttk.Label(time_frame, text="Sleep End:").grid(row=1, column=0, padx=5, pady=5)
        self.sleep_end_hour = ttk.Combobox(time_frame, width=2, values=[f"{i:02d}" for i in range(24)])
        self.sleep_end_hour.grid(row=1, column=1, padx=2, pady=5)
        self.sleep_end_hour.set("06")
        
        ttk.Label(time_frame, text=":").grid(row=1, column=2)
        
        self.sleep_end_min = ttk.Combobox(time_frame, width=2, values=[f"{i:02d}" for i in range(0, 60, 5)])
        self.sleep_end_min.grid(row=1, column=3, padx=2, pady=5)
        self.sleep_end_min.set("30")
        
        # Sleep quality
        quality_frame = ttk.LabelFrame(record_frame, text="Sleep Quality", padding=10)
        quality_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(quality_frame, text="Rating (1-10):").pack(anchor="w", pady=2)
        self.quality_scale = ttk.Scale(quality_frame, from_=1, to=10, orient=tk.HORIZONTAL)
        self.quality_scale.pack(fill=tk.X, pady=5)
        self.quality_scale.set(7)
        
        quality_value_frame = ttk.Frame(quality_frame)
        quality_value_frame.pack(fill=tk.X)
        
        for i in range(1, 11):
            ttk.Label(quality_value_frame, text=str(i)).pack(side=tk.LEFT, expand=True)
        
        ttk.Label(quality_frame, text="Times Woken:").pack(anchor="w", pady=5)
        self.times_woken = ttk.Spinbox(quality_frame, from_=0, to=20, width=5)
        self.times_woken.pack(anchor="w", pady=2)
        self.times_woken.set(0)
        
        # Sleep factors
        factors_frame = ttk.LabelFrame(record_frame, text="Sleep Factors", padding=10)
        factors_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.caffeine_var = tk.BooleanVar()
        ttk.Checkbutton(factors_frame, text="Caffeine Consumption", variable=self.caffeine_var).pack(anchor="w", pady=2)
        
        self.exercise_var = tk.BooleanVar()
        ttk.Checkbutton(factors_frame, text="Exercise During Day", variable=self.exercise_var).pack(anchor="w", pady=2)
        
        screen_frame = ttk.Frame(factors_frame)
        screen_frame.pack(fill=tk.X, pady=2)
        ttk.Label(screen_frame, text="Screen Time Before Bed (minutes):").pack(side=tk.LEFT, padx=5)
        self.screen_time = ttk.Spinbox(screen_frame, from_=0, to=240, width=5)
        self.screen_time.pack(side=tk.LEFT, padx=5)
        self.screen_time.set(30)
        
        stress_frame = ttk.Frame(factors_frame)
        stress_frame.pack(fill=tk.X, pady=2)
        ttk.Label(stress_frame, text="Stress Level (1-10):").pack(side=tk.LEFT, padx=5)
        self.stress_level = ttk.Spinbox(stress_frame, from_=1, to=10, width=5)
        self.stress_level.pack(side=tk.LEFT, padx=5)
        self.stress_level.set(5)
        
        # Notes
        notes_frame = ttk.LabelFrame(record_frame, text="Notes", padding=10)
        notes_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.notes_text = tk.Text(notes_frame, height=4, width=40)
        self.notes_text.pack(fill=tk.X, pady=5)
        
        # Save button
        ttk.Button(record_frame, text="Save Sleep Record", command=self.save_sleep_record).pack(pady=10)
    
    def generate_statistics(self):
        """Generate sleep statistics based on selected time range."""
        # Clear existing charts
        for widget in self.charts_frame.winfo_children():
            widget.destroy()
        
        # Get date range
        range_selection = self.time_range.get()
        days_back = 7
        if range_selection == "Last 30 Days":
            days_back = 30
        elif range_selection == "Last 90 Days":
            days_back = 90
        elif range_selection == "All Time":
            days_back = 3650  # ~10 years
        
        try:
            conn = sqlite3.connect('sleep_tracker.db')
            
            # Get sleep data
            query = f'''
            SELECT ss.date, ss.duration, sq.rating, sf.caffeine_intake, sf.exercise, 
                   sf.screen_time_before_bed, sf.stress_level
            FROM Sleep_Sessions ss
            LEFT JOIN Sleep_Quality sq ON ss.session_id = sq.session_id
            LEFT JOIN Sleep_Factors sf ON ss.session_id = sf.session_id
            WHERE ss.user_id = ? AND ss.date >= date('now', '-{days_back} days')
            ORDER BY ss.date
            '''
            
            df = pd.read_sql_query(query, conn, params=(self.current_user_id,))
            conn.close()
            
            if df.empty:
                ttk.Label(self.charts_frame, text="No sleep data available for selected time range").pack(pady=20)
                return
            
            # Convert duration from minutes to hours
            df['duration'] = df['duration'] / 60
            
            # Create figure with subplots
            fig = plt.figure(figsize=(10, 8))
            
            # Sleep duration over time
            ax1 = fig.add_subplot(2, 1, 1)
            ax1.plot(df['date'], df['duration'], 'b-', marker='o')
            ax1.set_title('Sleep Duration Over Time')
            ax1.set_ylabel('Hours')
            ax1.set_xlabel('Date')
            ax1.grid(True)
            
            # Sleep quality over time
            ax2 = fig.add_subplot(2, 1, 2)
            ax2.plot(df['date'], df['rating'], 'g-', marker='o')
            ax2.set_title('Sleep Quality Over Time')
            ax2.set_ylabel('Quality Rating (1-10)')
            ax2.set_xlabel('Date')
            ax2.grid(True)
            
            # Adjust layout
            plt.tight_layout()
            
            # Embed in tkinter
            canvas = FigureCanvasTkAgg(fig, master=self.charts_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
            # Summary statistics
            summary_frame = ttk.LabelFrame(self.charts_frame, text="Summary Statistics", padding=10)
            summary_frame.pack(fill=tk.X, pady=10)
            
            avg_duration = df['duration'].mean()
            avg_quality = df['rating'].mean()
            correlation = df['duration'].corr(df['rating']) if len(df) > 1 else None
            
            ttk.Label(summary_frame, text=f"Average Sleep Duration: {avg_duration:.2f} hours").pack(anchor="w", pady=2)
            ttk.Label(summary_frame, text=f"Average Sleep Quality: {avg_quality:.2f}/10").pack(anchor="w", pady=2)
            
            if correlation is not None:
                ttk.Label(summary_frame, text=f"Correlation between Duration and Quality: {correlation:.2f}").pack(anchor="w", pady=2)
            
            # Factors analysis
            if 'caffeine_intake' in df.columns and not df['caffeine_intake'].isna().all():
                caffeine_effect = df.groupby('caffeine_intake')['duration'].mean()
                ttk.Label(summary_frame, text=f"Avg. Sleep Duration with Caffeine: {caffeine_effect.get(1, 0):.2f} hours").pack(anchor="w", pady=2)
                ttk.Label(summary_frame, text=f"Avg. Sleep Duration without Caffeine: {caffeine_effect.get(0, 0):.2f} hours").pack(anchor="w", pady=2)
            
            if 'exercise' in df.columns and not df['exercise'].isna().all():
                exercise_effect = df.groupby('exercise')['duration'].mean()
                ttk.Label(summary_frame, text=f"Avg. Sleep Duration with Exercise: {exercise_effect.get(1, 0):.2f} hours").pack(anchor="w", pady=2)
                ttk.Label(summary_frame, text=f"Avg. Sleep Duration without Exercise: {exercise_effect.get(0, 0):.2f} hours").pack(anchor="w", pady=2)
        
        except Exception as e:
            ttk.Label(self.charts_frame, text=f"Error generating statistics: {e}").pack(pady=20)
    
    def load_sleep_history(self):
        """Load sleep history into the treeview."""
        # Clear existing items
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        try:
            conn = sqlite3.connect('sleep_tracker.db')
            cursor = conn.cursor()
            
            # Get sleep records
            cursor.execute('''
            SELECT ss.date, ss.sleep_start_time, ss.sleep_end_time, ss.duration, sq.rating
            FROM Sleep_Sessions ss
            LEFT JOIN Sleep_Quality sq ON ss.session_id = sq.session_id
            WHERE ss.user_id = ?
            ORDER BY ss.date DESC, ss.sleep_start_time DESC
            ''', (self.current_user_id,))
            
            records = cursor.fetchall()
            conn.close()
            
            # Insert records into treeview
            for record in records:
                date = record[0]
                start_time = datetime.strptime(record[1], "%Y-%m-%d %H:%M:%S").strftime("%H:%M")
                end_time = datetime.strptime(record[2], "%Y-%m-%d %H:%M:%S").strftime("%H:%M") if record[2] else "In progress"
                duration = f"{record[3] / 60:.2f}" if record[3] else "N/A"
                quality = record[4] if record[4] else "N/A"
                
                self.history_tree.insert("", tk.END, values=(date, start_time, end_time, duration, quality))
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load sleep history: {e}")
    
    def start_sleep_session(self):
        """Start a new sleep session."""
        try:
            conn = sqlite3.connect('sleep_tracker.db')
            cursor = conn.cursor()
            
            # Check if there's an active session
            cursor.execute('''
            SELECT session_id FROM Sleep_Sessions
            WHERE user_id = ? AND sleep_end_time IS NULL
            ''', (self.current_user_id,))
            
            active_session = cursor.fetchone()
            
            if active_session:
                messagebox.showinfo("Already Active", "You already have an active sleep session. End it before starting a new one.")
                conn.close()
                return
            
            # Insert new session
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            current_date = datetime.now().strftime("%Y-%m-%d")
            
            cursor.execute('''
            INSERT INTO Sleep_Sessions (user_id, sleep_start_time, date)
            VALUES (?, ?, ?)
            ''', (self.current_user_id, current_time, current_date))
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", f"Sleep session started at {current_time}")
            
            # Refresh dashboard
            self.notebook.select(0)  # Switch to dashboard tab
            self.update_dashboard()
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start sleep session: {e}")
    
    def end_sleep_session(self):
        """End the current sleep session."""
        try:
            conn = sqlite3.connect('sleep_tracker.db')
            cursor = conn.cursor()
            
            # Check for active session
            cursor.execute('''
            SELECT session_id, sleep_start_time FROM Sleep_Sessions
            WHERE user_id = ? AND sleep_end_time IS NULL
            ''', (self.current_user_id,))
            
            active_session = cursor.fetchone()
            
            if not active_session:
                messagebox.showinfo("No Active Session", "You don't have an active sleep session to end.")
                conn.close()
                return
            
            session_id = active_session[0]
            start_time = datetime.strptime(active_session[1], "%Y-%m-%d %H:%M:%S")
            end_time = datetime.now()
            end_time_str = end_time.strftime("%Y-%m-%d %H:%M:%S")
            
            # Calculate duration in minutes
            duration = int((end_time - start_time).total_seconds() / 60)
            
            # Update session
            cursor.execute('''
            UPDATE Sleep_Sessions
            SET sleep_end_time = ?, duration = ?
            WHERE session_id = ?
            ''', (end_time_str, duration, session_id))
            
            conn.commit()
            conn.close()
            
            # Ask for sleep quality data
            self.show_end_session_dialog(session_id, duration)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to end sleep session: {e}")
    
    def show_end_session_dialog(self, session_id, duration):
        """Show dialog to collect sleep quality data."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Sleep Session Ended")
        dialog.geometry("400x500")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text=f"Sleep Session Ended", font=("Arial", 16)).pack(pady=10)
        ttk.Label(dialog, text=f"Duration: {duration / 60:.2f} hours").pack(pady=5)
        
        # Sleep quality
        quality_frame = ttk.LabelFrame(dialog, text="Sleep Quality", padding=10)
        quality_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(quality_frame, text="Rating (1-10):").pack(anchor="w", pady=2)
        quality_scale = ttk.Scale(quality_frame, from_=1, to=10, orient=tk.HORIZONTAL)
        quality_scale.pack(fill=tk.X, pady=5)
        quality_scale.set(7)
        
        quality_value_frame = ttk.Frame(quality_frame)
        quality_value_frame.pack(fill=tk.X)
        
        for i in range(1, 11):
            ttk.Label(quality_value_frame, text=str(i)).pack(side=tk.LEFT, expand=True)
        
        ttk.Label(quality_frame, text="Times Woken:").pack(anchor="w", pady=5)
        times_woken = ttk.Spinbox(quality_frame, from_=0, to=20, width=5)
        times_woken.pack(anchor="w", pady=2)
        times_woken.set(0)
        
        # Sleep factors
        factors_frame = ttk.LabelFrame(dialog, text="Sleep Factors", padding=10)
        factors_frame.pack(fill=tk.X, padx=10, pady=5)
        
        caffeine_var = tk.BooleanVar()
        ttk.Checkbutton(factors_frame, text="Caffeine Consumption", variable=caffeine_var).pack(anchor="w", pady=2)
        
        exercise_var = tk.BooleanVar()
        ttk.Checkbutton(factors_frame, text="Exercise During Day", variable=exercise_var).pack(anchor="w", pady=2)
        
        screen_frame = ttk.Frame(factors_frame)
        screen_frame.pack(fill=tk.X, pady=2)
        ttk.Label(screen_frame, text="Screen Time Before Bed (minutes):").pack(side=tk.LEFT, padx=5)
        screen_time = ttk.Spinbox(screen_frame, from_=0, to=240, width=5)
        screen_time.pack(side=tk.LEFT, padx=5)
        screen_time.set(30)
        
        stress_frame = ttk.Frame(factors_frame)
        stress_frame.pack(fill=tk.X, pady=2)
        ttk.Label(stress_frame, text="Stress Level (1-10):").pack(side=tk.LEFT, padx=5)
        stress_level = ttk.Spinbox(stress_frame, from_=1, to=10, width=5)
        stress_level.pack(side=tk.LEFT, padx=5)
        stress_level.set(5)
        
        # Notes
        notes_frame = ttk.LabelFrame(dialog, text="Notes", padding=10)
        notes_frame.pack(fill=tk.X, padx=10, pady=5)
        
        notes_text = tk.Text(notes_frame, height=4, width=40)
        notes_text.pack(fill=tk.X, pady=5)
        
        def save_quality_data():
            try:
                conn = sqlite3.connect('sleep_tracker.db')
                cursor = conn.cursor()
                
                # Insert quality data
                cursor.execute('''
                INSERT INTO Sleep_Quality (session_id, rating, times_woken, notes)
                VALUES (?, ?, ?, ?)
                ''', (session_id, int(quality_scale.get()), int(times_woken.get()), notes_text.get("1.0", tk.END).strip()))
                
                # Insert factors data
                cursor.execute('''
                INSERT INTO Sleep_Factors 
                (session_id, caffeine_intake, exercise, screen_time_before_bed, stress_level)
                VALUES (?, ?, ?, ?, ?)
                ''', (session_id, caffeine_var.get(), exercise_var.get(), 
                      int(screen_time.get()), int(stress_level.get())))
                
                conn.commit()
                conn.close()
                
                messagebox.showinfo("Success", "Sleep data saved successfully!")
                dialog.destroy()
                
                # Refresh dashboard
                self.update_dashboard()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save sleep data: {e}")
        
        ttk.Button(dialog, text="Save Sleep Data", command=save_quality_data).pack(pady=10)
    
    def save_sleep_record(self):
        """Save a manual sleep record from the form."""
        try:
            # Get form data
            date_str = self.date_entry.get()
            start_hour = self.sleep_start_hour.get()
            start_min = self.sleep_start_min.get()
            end_hour = self.sleep_end_hour.get()
            end_min = self.sleep_end_min.get()
            
            # Validate time format
            try:
                start_time = datetime.strptime(f"{date_str} {start_hour}:{start_min}", "%Y-%m-%d %H:%M")
                end_time = datetime.strptime(f"{date_str} {end_hour}:{end_min}", "%Y-%m-%d %H:%M")
                
                # Handle overnight sleep (end time earlier than start time)
                if end_time < start_time:
                    end_time += timedelta(days=1)
                
                # Format for database
                start_time_str = start_time.strftime("%Y-%m-%d %H:%M:%S")
                end_time_str = end_time.strftime("%Y-%m-%d %H:%M:%S")
                
                # Calculate duration in minutes
                duration = int((end_time - start_time).total_seconds() / 60)
                
            except ValueError as e:
                messagebox.showerror("Error", f"Invalid date or time format: {e}")
                return
            
            # Get quality data
            quality_rating = int(self.quality_scale.get())
            times_woken = int(self.times_woken.get())
            notes = self.notes_text.get("1.0", tk.END).strip()
            
            # Get factors data
            caffeine = self.caffeine_var.get()
            exercise = self.exercise_var.get()
            screen_time = int(self.screen_time.get())
            stress_level = int(self.stress_level.get())
            
            # Save to database
            conn = sqlite3.connect('sleep_tracker.db')
            cursor = conn.cursor()
            
            # Insert sleep session
            cursor.execute('''
            INSERT INTO Sleep_Sessions (user_id, sleep_start_time, sleep_end_time, duration, date)
            VALUES (?, ?, ?, ?, ?)
            ''', (self.current_user_id, start_time_str, end_time_str, duration, date_str))
            
            session_id = cursor.lastrowid
            
            # Insert quality data
            cursor.execute('''
            INSERT INTO Sleep_Quality (session_id, rating, times_woken, notes)
            VALUES (?, ?, ?, ?)
            ''', (session_id, quality_rating, times_woken, notes))
            
            # Insert factors data
            cursor.execute('''
            INSERT INTO Sleep_Factors 
            (session_id, caffeine_intake, exercise, screen_time_before_bed, stress_level)
            VALUES (?, ?, ?, ?, ?)
            ''', (session_id, caffeine, exercise, screen_time, stress_level))
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", "Sleep record saved successfully!")
            
            # Clear form
            self.date_entry.delete(0, tk.END)
            self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
            self.quality_scale.set(7)
            self.times_woken.set(0)
            self.caffeine_var.set(False)
            self.exercise_var.set(False)
            self.screen_time.set(30)
            self.stress_level.set(5)
            self.notes_text.delete("1.0", tk.END)
            
            # Refresh dashboard
            self.update_dashboard()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save sleep record: {e}")
    
    def logout(self):
        """Log out the current user and return to login screen."""
        self.current_user_id = None
        self.is_logged_in = False
        
        # Destroy main frame
        self.main_frame.destroy()
        
        # Create authentication frame
        self.auth_frame = ttk.Frame(self.root, padding=20)
        self.auth_frame.pack(fill=tk.BOTH, expand=True)
        
        self.show_login_screen()


if __name__ == "__main__":
    root = tk.Tk()
    app = SleepTrackerApp(root)
    root.mainloop()
