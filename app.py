import customtkinter as ctk
from PIL import Image
import os
import threading

# Import Frames
from gui.frames.dashboard_frame import DashboardFrame
from gui.frames.map_frame import MapFrame
from gui.frames.tools_frame import ToolsFrame
from gui.frames.settings_frame import SettingsFrame

from core.api_client import IPAPIClient
from core.data_manager import DataManager

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("IP Intelligence Suite")
        self.geometry("1100x700")
        
        # Theme Setup
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        # Initialize Core Modules
        self.api_client = IPAPIClient()
        self.data_manager = DataManager(os.path.join(os.getcwd(), "data"))
        self.current_data = None # Holds the currently fetched IP data

        # Grid Layout (1x2)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # --- Sidebar ---
        self.create_sidebar()

        # --- Main Content Area ---
        self.active_frame = None
        
        # Instantiate Frames
        self.frames = {}
        self.frames["Dashboard"] = DashboardFrame(self, self.api_client, self.data_manager)
        self.frames["Map"] = MapFrame(self)
        self.frames["Tools"] = ToolsFrame(self)
        self.frames["Settings"] = SettingsFrame(self, self.data_manager)

        # Start with Dashboard
        self.select_frame("Dashboard")

    def create_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1)

        # Logo / Title
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="IP Intel Suite", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Navigation Buttons
        self.sidebar_buttons = {}
        btn_names = ["Dashboard", "Map", "Tools", "Settings"]
        
        for i, name in enumerate(btn_names):
            btn = ctk.CTkButton(self.sidebar_frame, corner_radius=0, height=40, border_spacing=10, text=name,
                                fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                anchor="w", command=lambda n=name: self.select_frame(n))
            btn.grid(row=i+1, column=0, sticky="ew")
            self.sidebar_buttons[name] = btn

        # Theme Switch
        self.appearance_mode_label = ctk.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=6, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(self.sidebar_frame, values=["Dark", "Light", "System"],
                                                               command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=7, column=0, padx=20, pady=(10, 20))


    def select_frame(self, name):
        # Update Button Styles
        for btn_name, btn in self.sidebar_buttons.items():
            if btn_name == name:
                btn.configure(fg_color=("gray75", "gray25"))
            else:
                btn.configure(fg_color="transparent")

        # Show Frame
        if self.active_frame:
            self.active_frame.grid_forget()
        
        self.active_frame = self.frames[name]
        self.active_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
        # If switching to Map, ensure it renders correctly (sometimes needs resize event)
        if name == "Map" and self.current_data:
            self.frames["Map"].update_map(self.current_data)


    def change_appearance_mode_event(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)

    # --- Global Search / Data Handling ---
    def perform_search(self, query):
        """Called by Dashboard to initiate a search. Available to other frames if needed."""
        # This function updates the state and notifies all frames
        def _search_thread():
            data = self.api_client.fetch_data(query)
            self.after(0, lambda: self.handle_search_result(query, data))

        threading.Thread(target=_search_thread, daemon=True).start()

    def handle_search_result(self, query, data):
        if data.get("status") == "success":
            self.current_data = data
            self.data_manager.add_to_history(query)
            
            # Update all frames that care about data
            self.frames["Dashboard"].update_display(data)
            self.frames["Map"].update_map(data)
            self.frames["Tools"].set_target(query)
        else:
            # Show error in current frame (Dashboard handles its own errors usually, but we can have global toast)
            self.frames["Dashboard"].show_error(data.get("message", "Unknown Error"))
