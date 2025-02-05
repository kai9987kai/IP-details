import socket
import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
import threading
import os
import json
import time
import pyperclip  # For clipboard functionality
import requests  # For HTTP requests

# Optional: Pillow for image handling if needed (not used here)
try:
    from PIL import Image, ImageTk
except ImportError:
    Image = ImageTk = None

# New API using ip-api.com (no API key required)
API_BASE_URL = "http://ip-api.com/json/"

class IPInfoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("IP Information")
        self.root.minsize(600, 550)
        self.root.attributes("-topmost", True)
        try:
            self.root.iconbitmap('favicon.ico')
        except Exception:
            pass

        # Status variable (initialize early for theme functions)
        self.status_var = tk.StringVar(value="Ready")
        self.current_theme = "light"

        # Latest API data (for export)
        self.last_data = {}

        # Setup ttk style for modern look
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.set_theme(self.current_theme)

        # Main container frame with grid layout
        self.container = ttk.Frame(self.root, padding=10)
        self.container.grid(row=0, column=0, sticky="nsew")
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        self.create_top_section()
        self.create_input_section()
        self.create_output_section()
        self.create_additional_options_section()
        self.create_history_and_favorites_section()
        self.create_bottom_section()
        self.create_status_bar()
        self.create_menu()

        # Auto-refresh (Advanced Options): check every refresh_interval ms
        self.auto_refresh_enabled = tk.BooleanVar(value=False)
        self.refresh_interval = 10000  # 10 seconds
        self.root.after(self.refresh_interval, self.check_auto_refresh)

    def set_theme(self, theme):
        if theme == "light":
            bg = "#F5F5F5"
            fg = "#000000"
            status_bg = "#DDDDDD"
        else:
            bg = "#333333"
            fg = "#F5F5F5"
            status_bg = "#555555"
        self.root.configure(background=bg)
        self.style.configure("TFrame", background=bg)
        self.style.configure("TLabel", background=bg, foreground=fg, font=("Helvetica", 12))
        self.style.configure("Header.TLabel", font=("Helvetica", 16, "bold"), background=bg, foreground=fg)
        self.style.configure("TButton", font=("Helvetica", 12))
        self.style.configure("TEntry", font=("Helvetica", 12, "bold"))
        self.status_var.set(f"{theme.title()} theme enabled")

    def create_top_section(self):
        top_frame = ttk.Frame(self.container)
        top_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        top_frame.columnconfigure(1, weight=1)
        # Emoji logo
        self.logo_label = ttk.Label(top_frame, text="🌐", font=("Helvetica", 48))
        self.logo_label.grid(row=0, column=0, padx=5)
        # Title
        self.title_label = ttk.Label(top_frame, text="IP Information", style="Header.TLabel")
        self.title_label.grid(row=0, column=1, sticky="w", padx=5)
        # Theme toggle button
        self.theme_btn = ttk.Button(top_frame, text="Toggle Theme", command=self.toggle_theme)
        self.theme_btn.grid(row=0, column=2, padx=5)

    def create_input_section(self):
        input_frame = ttk.Frame(self.container)
        input_frame.grid(row=1, column=0, sticky="ew", pady=5)
        input_frame.columnconfigure(1, weight=1)
        ttk.Label(input_frame, text="Enter IP or Domain:", font=("Helvetica", 12, "bold")).grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.ip_entry = ttk.Entry(input_frame)
        self.ip_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        clear_input_btn = ttk.Button(input_frame, text="Clear Input", command=lambda: self.ip_entry.delete(0, tk.END))
        clear_input_btn.grid(row=0, column=2, padx=5, pady=5)
        # Buttons: Fetch Info, Copy Data, Clear Output
        fetch_btn = ttk.Button(input_frame, text="Fetch Info", command=self.threaded_fetch_info)
        fetch_btn.grid(row=1, column=0, columnspan=2, pady=10)
        copy_btn = ttk.Button(input_frame, text="Copy Data", command=self.copy_all_data)
        copy_btn.grid(row=1, column=2, padx=5, pady=10)
        # Progress bar
        self.progress = ttk.Progressbar(input_frame, orient="horizontal", mode="indeterminate")
        self.progress.grid(row=2, column=0, columnspan=3, sticky="ew", padx=5, pady=5)

    def create_output_section(self):
        # Use a Notebook to separate Conversion and Extra Info tabs
        self.notebook = ttk.Notebook(self.container)
        self.notebook.grid(row=2, column=0, sticky="nsew", pady=5)
        # Define fields based on ip-api.com data:
        self.fields = {
            "query": "IP",
            "country": "Country",
            "countryCode": "Country Code",
            "region": "Region",
            "regionName": "Region Name",
            "city": "City",
            "zip": "ZIP",
            "lat": "Latitude",
            "lon": "Longitude",
            "timezone": "Timezone",
            "isp": "ISP",
            "org": "Organization",
            "as": "AS"
        }
        # Create a frame for results
        self.result_frame = ttk.Frame(self.notebook, padding=10)
        self.result_frame.columnconfigure(1, weight=1)
        self.notebook.add(self.result_frame, text="Results")
        self.result_labels = {}
        row = 0
        for key, label in self.fields.items():
            ttk.Label(self.result_frame, text=label + ":", font=("Helvetica", 12, "bold")).grid(row=row, column=0, sticky="e", padx=5, pady=3)
            self.result_labels[key] = ttk.Label(self.result_frame, text="", font=("Helvetica", 12))
            self.result_labels[key].grid(row=row, column=1, sticky="w", padx=5, pady=3)
            row += 1

    def create_additional_options_section(self):
        # Additional Options: View on Map and Export Data
        add_opt_frame = ttk.Frame(self.container, padding=10)
        add_opt_frame.grid(row=3, column=0, sticky="ew", pady=5)
        add_opt_frame.columnconfigure(0, weight=1)
        view_map_btn = ttk.Button(add_opt_frame, text="View on Map", command=self.view_on_map)
        view_map_btn.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        export_btn = ttk.Button(add_opt_frame, text="Export Data", command=self.export_data)
        export_btn.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        add_opt_frame.columnconfigure(1, weight=1)

    def create_history_and_favorites_section(self):
        mid_frame = ttk.Frame(self.container)
        mid_frame.grid(row=4, column=0, sticky="nsew", pady=5)
        mid_frame.columnconfigure(0, weight=1)
        mid_frame.columnconfigure(1, weight=1)
        # History Labelframe
        self.history_frame = ttk.Labelframe(mid_frame, text="Search History", padding=5)
        self.history_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.history_frame.columnconfigure(0, weight=1)
        self.history_listbox = tk.Listbox(self.history_frame, font=("Helvetica", 12))
        self.history_listbox.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        history_scroll = ttk.Scrollbar(self.history_frame, orient="vertical", command=self.history_listbox.yview)
        history_scroll.grid(row=0, column=1, sticky="ns", padx=5, pady=5)
        self.history_listbox.config(yscrollcommand=history_scroll.set)
        self.history_listbox.bind("<Double-Button-1>", self.on_history_double_click)
        self.load_history()
        clear_history_btn = ttk.Button(self.history_frame, text="Clear History", command=self.clear_history)
        clear_history_btn.grid(row=1, column=0, columnspan=2, pady=5)
        # Favorites Labelframe
        self.fav_frame = ttk.Labelframe(mid_frame, text="Favorites", padding=5)
        self.fav_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        self.fav_frame.columnconfigure(0, weight=1)
        self.fav_listbox = tk.Listbox(self.fav_frame, font=("Helvetica", 12))
        self.fav_listbox.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        fav_scroll = ttk.Scrollbar(self.fav_frame, orient="vertical", command=self.fav_listbox.yview)
        fav_scroll.grid(row=0, column=1, sticky="ns", padx=5, pady=5)
        self.fav_listbox.config(yscrollcommand=fav_scroll.set)
        self.fav_listbox.bind("<Double-Button-1>", self.on_fav_double_click)
        self.load_favorites()
        add_fav_btn = ttk.Button(self.fav_frame, text="Add to Favorites", command=self.add_favorite)
        add_fav_btn.grid(row=1, column=0, columnspan=2, pady=5)
        clear_fav_btn = ttk.Button(self.fav_frame, text="Clear Favorites", command=self.clear_favorites)
        clear_fav_btn.grid(row=2, column=0, columnspan=2, pady=5)

    def create_bottom_section(self):
        bottom_frame = ttk.Frame(self.container)
        bottom_frame.grid(row=5, column=0, sticky="ew", pady=10)
        bottom_frame.columnconfigure(0, weight=1)
        self.adv_options_btn = ttk.Button(bottom_frame, text="Advanced Options", command=self.open_advanced_options)
        self.adv_options_btn.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

    def create_status_bar(self):
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief="sunken", anchor="w", padding=5, font=("Helvetica", 10))
        self.status_bar.grid(row=6, column=0, sticky="ew")

    def create_menu(self):
        self.menu = tk.Menu(self.root)
        file_menu = tk.Menu(self.menu, tearoff=0)
        file_menu.add_command(label="About", command=self.show_about)
        file_menu.add_command(label="Exit", command=self.root.destroy)
        self.menu.add_cascade(label="File", menu=file_menu)
        help_menu = tk.Menu(self.menu, tearoff=0)
        help_menu.add_command(label="Contact", command=lambda: messagebox.showinfo("Contact", "Email: your_email@example.com"))
        self.menu.add_cascade(label="Help", menu=help_menu)
        self.root.config(menu=self.menu)

    def toggle_theme(self):
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        self.set_theme(self.current_theme)

    def threaded_fetch_info(self):
        threading.Thread(target=self.fetch_info, daemon=True).start()

    def fetch_info(self):
        self.set_status("Fetching data...")
        self.progress.start(10)
        ip_or_domain = self.ip_entry.get().strip()
        if not ip_or_domain:
            messagebox.showerror("Input Error", "Please enter an IP address or domain.")
            self.progress.stop()
            self.set_status("Ready")
            return
        url = API_BASE_URL + ip_or_domain
        try:
            response = requests.get(url)
            json_data = response.json()
            if json_data.get("status") != "success":
                messagebox.showerror("API Error", json_data.get("message", "Unknown error"))
                self.set_status("Error fetching data")
                self.progress.stop()
                return
            # Store latest data for export
            self.last_data = json_data
            # Update result labels
            for key in self.fields.keys():
                value = json_data.get(key, "N/A")
                self.result_labels[key].config(text=str(value))
            self.set_status("Data fetched successfully")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.set_status("Error")
        finally:
            self.progress.stop()

    def copy_all_data(self):
        if not self.last_data:
            messagebox.showerror("No Data", "No data available to copy.")
            return
        pyperclip.copy(json.dumps(self.last_data, indent=2))
        self.set_status("Data copied to clipboard")

    def view_on_map(self):
        lat = self.result_labels.get("lat").cget("text")
        lon = self.result_labels.get("lon").cget("text")
        try:
            float(lat)
            float(lon)
        except ValueError:
            messagebox.showerror("Map Error", "Latitude and Longitude not available.")
            return
        url = f"https://www.google.com/maps?q={lat},{lon}"
        webbrowser.open_new(url)
        self.set_status("Opened map in browser")

    def export_data(self):
        if not self.last_data:
            messagebox.showerror("No Data", "No data to export.")
            return
        try:
            with open("ip_data_export.json", "w") as f:
                json.dump(self.last_data, f, indent=2)
            messagebox.showinfo("Export", "Data exported to ip_data_export.json")
            self.set_status("Data exported successfully")
        except Exception as e:
            messagebox.showerror("Export Error", f"Error exporting data: {str(e)}")
            self.set_status("Export failed")

    def check_auto_refresh(self):
        if self.auto_refresh_enabled.get():
            self.threaded_fetch_info()
        self.root.after(self.refresh_interval, self.check_auto_refresh)

    def open_advanced_options(self):
        adv_win = tk.Toplevel(self.root)
        adv_win.title("Advanced Options")
        adv_win.transient(self.root)
        adv_win.grab_set()
        adv_win.resizable(False, False)
        adv_win.geometry("")  # Auto-size
        ttk.Label(adv_win, text="Advanced Options", font=("Helvetica", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=10)
        # Ping Domain
        ttk.Button(adv_win, text="Ping Domain", command=self.ping_domain).grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        self.ping_result = ttk.Label(adv_win, text="Ping: N/A", font=("Helvetica", 12))
        self.ping_result.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        # Auto Refresh
        self.auto_refresh_enabled = tk.BooleanVar(value=False)
        ttk.Checkbutton(adv_win, text="Auto Refresh Data", variable=self.auto_refresh_enabled).grid(row=2, column=0, columnspan=2, padx=10, pady=5)
        # Additional advanced options: Copy Data and Export Data
        ttk.Button(adv_win, text="Export Data", command=self.export_data).grid(row=3, column=0, padx=10, pady=5, sticky="ew")
        ttk.Button(adv_win, text="View on Map", command=self.view_on_map).grid(row=3, column=1, padx=10, pady=5, sticky="ew")
        ttk.Button(adv_win, text="Close", command=adv_win.destroy).grid(row=4, column=0, columnspan=2, pady=10)

    def ping_domain(self):
        text = self.ip_entry.get().strip()
        if not text:
            messagebox.showerror("Input Error", "Please enter an IP address or domain to ping.")
            return
        try:
            if "://" in text:
                domain = text.split("://")[1].split("/")[0]
            else:
                domain = text.split("/")[0]
            start = time.time()
            socket.gethostbyname(domain)
            elapsed = (time.time() - start) * 1000  # in ms
            self.ping_result.config(text=f"Ping: {int(elapsed)} ms")
            self.set_status("Ping successful")
        except Exception as e:
            messagebox.showerror("Ping Error", f"Error: {str(e)}")
            self.ping_result.config(text="Ping: Error")

    def add_favorite(self):
        text = self.ip_entry.get().strip()
        if text:
            favs = self.get_favorites()
            if text not in favs:
                favs.insert(0, text)
                favs = favs[:10]
                self.save_favorites(favs)
                self.load_favorites()
                self.set_status("Added to favorites")
            else:
                self.set_status("Already in favorites")
        else:
            messagebox.showerror("Input Error", "Please enter text to add as favorite.")

    def get_favorites(self):
        if os.path.exists("favorites.txt"):
            try:
                with open("favorites.txt", "r") as f:
                    return f.read().splitlines()
            except Exception:
                return []
        return []

    def save_favorites(self, favs):
        try:
            with open("favorites.txt", "w") as f:
                f.write("\n".join(favs))
        except Exception as e:
            print("Error saving favorites:", e)

    def load_favorites(self):
        favs = self.get_favorites()
        self.fav_listbox.delete(0, tk.END)
        for fav in favs:
            self.fav_listbox.insert(tk.END, fav)

    def clear_favorites(self):
        if messagebox.askyesno("Clear Favorites", "Are you sure you want to clear favorites?"):
            if os.path.exists("favorites.txt"):
                os.remove("favorites.txt")
            self.load_favorites()
            self.set_status("Favorites cleared")

    def on_fav_double_click(self, event):
        selection = self.fav_listbox.curselection()
        if selection:
            fav = self.fav_listbox.get(selection[0])
            self.ip_entry.delete(0, tk.END)
            self.ip_entry.insert(0, fav)

    def get_history(self):
        if os.path.exists("history.txt"):
            try:
                with open("history.txt", "r") as f:
                    return f.read().splitlines()
            except Exception:
                return []
        return []

    def save_history(self, history):
        try:
            with open("history.txt", "w") as f:
                f.write("\n".join(history))
        except Exception as e:
            print("Error saving history:", e)

    def add_history(self, query):
        history = self.get_history()
        if query not in history:
            history.insert(0, query)
            history = history[:10]
            self.save_history(history)
            self.load_history()

    def load_history(self):
        history = self.get_history()
        self.history_listbox.delete(0, tk.END)
        for item in history:
            self.history_listbox.insert(tk.END, item)

    def clear_history(self):
        if messagebox.askyesno("Clear History", "Are you sure you want to clear history?"):
            if os.path.exists("history.txt"):
                os.remove("history.txt")
            self.load_history()
            self.set_status("History cleared")

    def on_history_double_click(self, event):
        selection = self.history_listbox.curselection()
        if selection:
            text = self.history_listbox.get(selection[0])
            self.ip_entry.delete(0, tk.END)
            self.ip_entry.insert(0, text)

    def show_about(self):
        about_text = (
            "IP Information App v2.0\nDeveloped by Kai Piper\n\n"
            "This application fetches detailed IP and location data using the ip-api.com API,\n"
            "and offers advanced features like viewing on map, exporting data, pinging, and favorites management."
        )
        messagebox.showinfo("About", about_text)

    def set_status(self, text):
        self.status_var.set(text)

if __name__ == "__main__":
    root = tk.Tk()
    app = IPInfoApp(root)
    root.mainloop()
