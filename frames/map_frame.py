import customtkinter as ctk
import tkintermapview

class MapFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.map_widget = tkintermapview.TkinterMapView(self, corner_radius=10)
        self.map_widget.grid(row=0, column=0, sticky="nsew")
        
        # Initial Location (Default)
        self.map_widget.set_position(20, 0) 
        self.map_widget.set_zoom(2)

    def update_map(self, data):
        try:
            lat = float(data.get("lat"))
            lon = float(data.get("lon"))
            city = data.get("city", "Unknown")
            
            self.map_widget.set_position(lat, lon)
            self.map_widget.set_marker(lat, lon, text=city)
            self.map_widget.set_zoom(10)
        except (ValueError, TypeError):
            pass # Invalid coordinates
