import phonenumbers
from phonenumbers import carrier, geocoder, timezone
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import sqlite3
import pandas as pd
import folium
from opencage.geocoder import OpenCageGeocode
from datetime import datetime
import os
import webbrowser

class PhoneNumberTracker:
    def __init__(self):
        self.setup_database()
        self.setup_gui()
        
    def setup_database(self):
        """Initialize SQLite database with phone tracking logs table"""
        try:
            self.conn = sqlite3.connect("phone_tracker.db")
            self.cursor = self.conn.cursor()
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS phone_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    phone_number TEXT,
                    country TEXT,
                    carrier TEXT,
                    time_zones TEXT,
                    valid TEXT,
                    possible TEXT,
                    latitude REAL,
                    longitude REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            self.conn.commit()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to setup database: {str(e)}")

    def get_local_info(self, phone_number, api_key):
        """Get phone number information and location details"""
        if not phone_number or not api_key:
            messagebox.showerror("Error", "Please enter both phone number and API key!")
            return None

        try:
            # Add country code if not provided
            if not phone_number.startswith('+'):
                phone_number = '+' + phone_number
                
            parsed_number = phonenumbers.parse(phone_number)
            
            # Basic phone number validation
            if not phonenumbers.is_possible_number(parsed_number):
                messagebox.showerror("Error", "Invalid phone number format!")
                return None

            country = geocoder.description_for_number(parsed_number, "en")
            sim_provider = carrier.name_for_number(parsed_number, "en")
            time_zones = ", ".join(timezone.time_zones_for_number(parsed_number))
            is_valid = "Yes" if phonenumbers.is_valid_number(parsed_number) else "No"
            is_possible = "Yes" if phonenumbers.is_possible_number(parsed_number) else "No"
            
            # Geocode location using OpenCage
            opencage_geocoder = OpenCageGeocode(api_key)
            results = opencage_geocoder.geocode(country)
            
            if results:
                lat, lng = results[0]['geometry']['lat'], results[0]['geometry']['lng']
                details = {
                    "Phone Number": phone_number,
                    "Country": country or "Unknown",
                    "Carrier": sim_provider or "Unknown",
                    "Time Zones": time_zones,
                    "Valid": is_valid,
                    "Possible": is_possible,
                    "Latitude": lat,
                    "Longitude": lng
                }
                self.save_to_database(details)
                messagebox.showinfo("Success", "Phone number tracked successfully!")
                return details
            else:
                messagebox.showwarning("Warning", "Location data not found for this number")
                return None

        except phonenumbers.phonenumberutil.NumberParseException:
            messagebox.showerror("Error", "Invalid phone number format!")
            return None
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            return None

    def save_to_database(self, details):
        """Save tracking results to database"""
        try:
            self.cursor.execute("""
                INSERT INTO phone_logs 
                (phone_number, country, carrier, time_zones, valid, possible, latitude, longitude)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                details["Phone Number"],
                details["Country"],
                details["Carrier"],
                details["Time Zones"],
                details["Valid"],
                details["Possible"],
                details["Latitude"],
                details["Longitude"]
            ))
            self.conn.commit()
            self.view_logs()  # Refresh the table
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to save data: {str(e)}")

    def generate_map(self, phone_number):
        """Generate and save an HTML map for the phone number location"""
        if not phone_number:
            messagebox.showerror("Error", "Please enter a phone number first!")
            return

        try:
            self.cursor.execute(
                "SELECT country, latitude, longitude FROM phone_logs WHERE phone_number = ? ORDER BY id DESC LIMIT 1", 
                (phone_number,)
            )
            result = self.cursor.fetchone()
            
            if result and result[1] and result[2]:
                map_file = "phone_location_map.html"
                myMap = folium.Map(location=[result[1], result[2]], zoom_start=9)
                folium.Marker(
                    [result[1], result[2]],
                    popup=f"Country: {result[0]}<br>Phone: {phone_number}",
                    icon=folium.Icon(color='red', icon='info-sign')
                ).add_to(myMap)
                myMap.save(map_file)
                webbrowser.open(map_file)  # Open map in default browser
            else:
                messagebox.showwarning("Warning", "No location data found for this number")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate map: {str(e)}")

    def search_number(self):
        """Search for a specific phone number in the database"""
        number = self.search_entry.get()
        if not number:
            messagebox.showerror("Error", "Enter a phone number to search!")
            return
            
        try:
            self.cursor.execute("SELECT * FROM phone_logs WHERE phone_number LIKE ?", (f"%{number}%",))
            logs = self.cursor.fetchall()
            if not logs:
                messagebox.showinfo("Info", "No records found for this number")
            self.update_table(logs)
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Search failed: {str(e)}")

    def view_logs(self):
        """Retrieve and display all logs in the table"""
        try:
            self.cursor.execute("SELECT * FROM phone_logs ORDER BY id DESC")
            logs = self.cursor.fetchall()
            self.update_table(logs)
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to retrieve logs: {str(e)}")

    def export_to_csv(self):
        """Export database logs to CSV file"""
        try:
            df = pd.read_sql_query("SELECT * FROM phone_logs", self.conn)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"phone_tracker_logs_{timestamp}.csv"
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")],
                initialfile=default_filename
            )
            
            if filename:
                df.to_csv(filename, index=False)
                messagebox.showinfo("Success", f"Logs exported to {os.path.basename(filename)}")
                # Open the directory containing the file
                os.startfile(os.path.dirname(os.path.abspath(filename)))
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export data: {str(e)}")

    def clear_logs(self):
        """Clear all logs from the database"""
        if messagebox.askyesno("Confirm", "Are you sure you want to delete all logs?"):
            try:
                self.cursor.execute("DELETE FROM phone_logs")
                self.conn.commit()
                self.view_logs()
                messagebox.showinfo("Success", "All logs have been cleared")
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f"Failed to clear logs: {str(e)}")

    def update_table(self, logs):
        """Update the treeview table with new data"""
        for item in self.log_table.get_children():
            self.log_table.delete(item)
        
        for log in logs:
            self.log_table.insert('', 'end', values=log)

    def setup_gui(self):
        """Setup the graphical user interface"""
        self.root = tk.Tk()
        self.root.title("Phone Number Tracker")
        self.root.geometry("1000x700")
        
        # Style configuration
        style = ttk.Style()
        style.configure("Treeview", rowheight=25)
        style.configure("TButton", padding=5)
        
        # Create main frames
        input_frame = ttk.Frame(self.root, padding="10")
        input_frame.pack(fill="x")
        
        button_frame = ttk.Frame(self.root, padding="10")
        button_frame.pack(fill="x")
        
        # Input fields
        ttk.Label(input_frame, text="Phone Number:").grid(row=0, column=0, padx=5)
        self.entry = ttk.Entry(input_frame, width=30)
        self.entry.grid(row=0, column=1, padx=5)
        
        ttk.Label(input_frame, text="OpenCage API Key:").grid(row=0, column=2, padx=5)
        self.api_key_entry = ttk.Entry(input_frame, width=40, show="*")
        self.api_key_entry.grid(row=0, column=3, padx=5)
        
        # Buttons
        track_button = ttk.Button(
            button_frame, 
            text="Track Number",
            command=lambda: self.get_local_info(self.entry.get(), self.api_key_entry.get())
        )
        track_button.pack(side="left", padx=5)
        
        view_logs_button = ttk.Button(button_frame, text="View All Logs", command=self.view_logs)
        view_logs_button.pack(side="left", padx=5)
        
        export_button = ttk.Button(button_frame, text="Export to CSV", command=self.export_to_csv)
        export_button.pack(side="left", padx=5)
        
        clear_button = ttk.Button(button_frame, text="Clear Logs", command=self.clear_logs)
        clear_button.pack(side="left", padx=5)
        
        # Search frame
        search_frame = ttk.Frame(self.root, padding="10")
        search_frame.pack(fill="x")
        
        ttk.Label(search_frame, text="Search Number:").pack(side="left", padx=5)
        self.search_entry = ttk.Entry(search_frame, width=30)
        self.search_entry.pack(side="left", padx=5)
        
        search_button = ttk.Button(search_frame, text="Search", command=self.search_number)
        search_button.pack(side="left", padx=5)
        
        map_button = ttk.Button(
            search_frame, 
            text="Generate Map",
            command=lambda: self.generate_map(self.entry.get())
        )
        map_button.pack(side="left", padx=5)
        
        # Table
        columns = ("ID", "Phone Number", "Country", "Carrier", "Time Zones", 
                  "Valid", "Possible", "Latitude", "Longitude", "Timestamp")
        self.log_table = ttk.Treeview(self.root, columns=columns, show="headings")
        
        # Configure columns
        for col in columns:
            self.log_table.heading(col, text=col)
            self.log_table.column(col, width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.log_table.yview)
        self.log_table.configure(yscrollcommand=scrollbar.set)
        
        self.log_table.pack(expand=True, fill="both", padx=10, pady=5)
        scrollbar.pack(side="right", fill="y")
        
        # Status bar
        self.status_bar = ttk.Label(self.root, text="Ready", relief="sunken")
        self.status_bar.pack(fill="x", side="bottom", padx=10, pady=5)

    def run(self):
        """Start the application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = PhoneNumberTracker()
    app.run()
