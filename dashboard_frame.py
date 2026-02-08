import customtkinter as ctk
import json
from tkinter import messagebox
import pyperclip

class DashboardFrame(ctk.CTkFrame):
    def __init__(self, master, api_client, data_manager):
        super().__init__(master)
        self.controller = master # Reference to main App
        self.api_client = api_client
        self.data_manager = data_manager

        # Layout Configuration
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1) # Results area expands

        # --- Search Area ---
        self.create_search_area()

        # --- Action Buttons ---
        self.create_action_buttons()

        # --- Info Display Area ---
        self.create_info_area()

        # --- Sidebar/History Preview (Right Side or Bottom) ---
        # For this design, we keep history in the search auto-fill or separate tab, 
        # but let's add a "Recent" quick list at bottom
        self.create_footer_area()


    def create_search_area(self):
        search_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 20))
        search_frame.columnconfigure(0, weight=1)

        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Enter IP address or Domain (e.g. 1.1.1.1, google.com)", height=40, font=("Roboto", 14))
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.search_entry.bind("<Return>", lambda e: self.on_search())

        self.search_btn = ctk.CTkButton(search_frame, text="Search", command=self.on_search, width=100, height=40, font=("Roboto", 14, "bold"))
        self.search_btn.grid(row=0, column=1)

    def create_action_buttons(self):
        action_frame = ctk.CTkFrame(self, fg_color="transparent")
        action_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 20))

        self.fav_btn = ctk.CTkButton(action_frame, text="Add to Favorites", command=self.add_fav, width=120)
        self.fav_btn.pack(side="left", padx=5)

        self.copy_btn = ctk.CTkButton(action_frame, text="Copy API JSON", command=self.copy_json, width=120, fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"))
        self.copy_btn.pack(side="left", padx=5)
        
        self.export_btn = ctk.CTkButton(action_frame, text="Export JSON", command=self.export_file, width=120, fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"))
        self.export_btn.pack(side="left", padx=5)


    def create_info_area(self):
        self.info_scroll = ctk.CTkScrollableFrame(self, label_text="IP Information")
        self.info_scroll.grid(row=2, column=0, columnspan=2, sticky="nsew")
        self.info_scroll.grid_columnconfigure(0, weight=1)
        self.info_scroll.grid_columnconfigure(1, weight=1)
        self.info_scroll.grid_columnconfigure(2, weight=1)

        # We will populate cards here dynamically
        self.info_cards = {}
        
        # Initial State
        self.status_label = ctk.CTkLabel(self.info_scroll, text="Ready to search.", font=("Roboto", 16))
        self.status_label.grid(row=0, column=0, columnspan=3, pady=50)

    def create_footer_area(self):
        # Maybe show recent history bubbles
        pass

    def on_search(self):
        query = self.search_entry.get().strip()
        if query:
            self.status_label.configure(text="Fetching data...")
            self.status_label.grid(row=0, column=0, columnspan=3, pady=50)
            self.controller.perform_search(query)

    def show_error(self, message):
         # Clear previous results
        for widget in self.info_scroll.winfo_children():
            widget.destroy()
        
        lbl = ctk.CTkLabel(self.info_scroll, text=f"Error: {message}", text_color="red", font=("Roboto", 16))
        lbl.grid(row=0, column=0, columnspan=3, pady=20)


    def update_display(self, data):
        # Clear previous
        for widget in self.info_scroll.winfo_children():
            widget.destroy()

        fields = [
            ("IP Address", data.get("query")),
            ("Country", f"{data.get('country')} ({data.get('countryCode')})"),
            ("Region", f"{data.get('regionName')} ({data.get('region')})"),
            ("City", data.get("city")),
            ("ZIP", data.get("zip")),
            ("Timezone", data.get("timezone")),
            ("ISP", data.get("isp")),
            ("Organization", data.get("org")),
            ("AS", data.get("as")),
            ("Coordinates", f"{data.get('lat')}, {data.get('lon')}")
        ]

        row = 0
        col = 0
        for title, value in fields:
            card = ctk.CTkFrame(self.info_scroll)
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            
            lbl_title = ctk.CTkLabel(card, text=title, font=("Roboto", 12), text_color="gray")
            lbl_title.pack(anchor="w", padx=10, pady=(10, 0))
            
            lbl_val = ctk.CTkLabel(card, text=str(value), font=("Roboto", 15, "bold"), wraplength=200)
            lbl_val.pack(anchor="w", padx=10, pady=(0, 10))

            col += 1
            if col > 2:
                col = 0
                row += 1

    def add_fav(self):
        query = self.search_entry.get().strip()
        if query:
            self.data_manager.add_favorite(query)
            # Optional: Toast notification

    def copy_json(self):
        if self.controller.current_data:
            pyperclip.copy(json.dumps(self.controller.current_data, indent=4))

    def export_file(self):
        if self.controller.current_data:
            try:
                with open("last_export.json", "w") as f:
                    json.dump(self.controller.current_data, f, indent=4)
                messagebox.showinfo("Export", "Saved to last_export.json")
            except Exception as e:
                messagebox.showerror("Error", str(e))
