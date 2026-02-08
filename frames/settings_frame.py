import customtkinter as ctk

class SettingsFrame(ctk.CTkFrame):
    def __init__(self, master, data_manager):
        super().__init__(master)
        self.data_manager = data_manager
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1) # List area

        # Left: History
        self.history_frame = ctk.CTkFrame(self)
        self.history_frame.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=10, pady=10)
        self.history_frame.grid_columnconfigure(0, weight=1)
        self.history_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(self.history_frame, text="Search History", font=("Roboto", 16, "bold")).grid(row=0, column=0, pady=10)
        
        self.history_list = ctk.CTkScrollableFrame(self.history_frame)
        self.history_list.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        ctk.CTkButton(self.history_frame, text="Clear History", fg_color="#FF5555", hover_color="#AA3333", command=self.clear_history).grid(row=2, column=0, pady=10)


        # Right: Favorites
        self.fav_frame = ctk.CTkFrame(self)
        self.fav_frame.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=10, pady=10)
        self.fav_frame.grid_columnconfigure(0, weight=1)
        self.fav_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(self.fav_frame, text="Favorites", font=("Roboto", 16, "bold")).grid(row=0, column=0, pady=10)
        
        self.fav_list = ctk.CTkScrollableFrame(self.fav_frame)
        self.fav_list.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        self.refresh_lists()
        
        # Add Refresh Button to entire frame (top right or similar) mainly for debug or manual sync
        self.refresh_btn = ctk.CTkButton(self, text="Refresh Lists", command=self.refresh_lists)
        self.refresh_btn.grid(row=2, column=0, columnspan=2, pady=10)

    def refresh_lists(self):
        # Clear
        for w in self.history_list.winfo_children(): w.destroy()
        for w in self.fav_list.winfo_children(): w.destroy()

        # Load History
        for item in self.data_manager.get_history():
            btn = ctk.CTkButton(self.history_list, text=item, command=lambda i=item: self.load_item(i), 
                                fg_color="transparent", border_width=1, text_color=("gray10", "gray90"))
            btn.pack(fill="x", pady=2)

        # Load Favorites
        for item in self.data_manager.get_favorites():
            f_frame = ctk.CTkFrame(self.fav_list, fg_color="transparent")
            f_frame.pack(fill="x", pady=2)
            
            btn = ctk.CTkButton(f_frame, text=item, command=lambda i=item: self.load_item(i),
                                fg_color="transparent", border_width=1, text_color=("gray10", "gray90"))
            btn.pack(side="left", fill="x", expand=True)
            
            del_btn = ctk.CTkButton(f_frame, text="X", width=30, fg_color="#FF5555", command=lambda i=item: self.remove_fav(i))
            del_btn.pack(side="right", padx=5)

    def load_item(self, item):
        # Switch to dashboard and search
        self.master.select_frame("Dashboard")
        self.master.frames["Dashboard"].search_entry.delete(0, "end")
        self.master.frames["Dashboard"].search_entry.insert(0, item)
        self.master.frames["Dashboard"].on_search()

    def clear_history(self):
        self.data_manager.clear_history()
        self.refresh_lists()

    def remove_fav(self, item):
        self.data_manager.remove_favorite(item)
        self.refresh_lists()
