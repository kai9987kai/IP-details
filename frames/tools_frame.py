import customtkinter as ctk
import threading
from core.network_utils import NetworkUtils

class ToolsFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.tabview.add("DNS Lookup")
        self.tabview.add("Ping Check")

        self.build_dns_tab()
        self.build_ping_tab()
        
        self.current_target = ""

    def set_target(self, target):
        self.current_target = target
        # Pre-fill entries
        self.dns_entry.delete(0, "end")
        self.dns_entry.insert(0, target)
        self.ping_entry.delete(0, "end")
        self.ping_entry.insert(0, target)

    def build_dns_tab(self):
        tab = self.tabview.tab("DNS Lookup")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(2, weight=1)

        input_frm = ctk.CTkFrame(tab, fg_color="transparent")
        input_frm.grid(row=0, column=0, sticky="ew", pady=10)
        
        self.dns_entry = ctk.CTkEntry(input_frm, placeholder_text="Domain to lookup")
        self.dns_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        btn = ctk.CTkButton(input_frm, text="Fetch Records", command=self.run_dns)
        btn.pack(side="left")

        self.dns_textbox = ctk.CTkTextbox(tab, font=("Consolas", 12))
        self.dns_textbox.grid(row=2, column=0, sticky="nsew")

    def build_ping_tab(self):
        tab = self.tabview.tab("Ping Check")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(2, weight=1)

        input_frm = ctk.CTkFrame(tab, fg_color="transparent")
        input_frm.grid(row=0, column=0, sticky="ew", pady=10)

        self.ping_entry = ctk.CTkEntry(input_frm, placeholder_text="Host/IP to ping")
        self.ping_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        btn = ctk.CTkButton(input_frm, text="Ping", command=self.run_ping)
        btn.pack(side="left")

        self.ping_result_lbl = ctk.CTkLabel(tab, text="Ready", font=("Roboto", 24))
        self.ping_result_lbl.grid(row=1, column=0, pady=40)
        
        self.ping_log = ctk.CTkTextbox(tab, height=100)
        self.ping_log.grid(row=2, column=0, sticky="nsew")

    def run_dns(self):
        domain = self.dns_entry.get().strip()
        if not domain: return
        
        self.dns_textbox.delete("0.0", "end")
        self.dns_textbox.insert("0.0", "Fetching DNS records...\n")
        
        def _task():
            records = NetworkUtils.get_dns_records(domain)
            text = f"DNS Report for: {domain}\n" + "-"*40 + "\n"
            for rtype, values in records.items():
                text += f"[{rtype}]\n"
                if not values:
                    text += "  (No records found)\n"
                for v in values:
                    text += f"  {v}\n"
                text += "\n"
            
            self.after(0, lambda: self._update_dns_text(text))

        threading.Thread(target=_task, daemon=True).start()

    def _update_dns_text(self, text):
        self.dns_textbox.delete("0.0", "end")
        self.dns_textbox.insert("0.0", text)

    def run_ping(self):
        host = self.ping_entry.get().strip()
        if not host: return

        self.ping_result_lbl.configure(text="Pinging...")
        
        def _task():
            ms = NetworkUtils.ping_host(host)
            
            def _ui():
                if ms is not None:
                    self.ping_result_lbl.configure(text=f"{ms} ms", text_color="#2CC985") # Greenish
                    self.ping_log.insert("end", f"Reply from {host}: time={ms}ms\n")
                else:
                    self.ping_result_lbl.configure(text="Timeout", text_color="#FF5555")
                    self.ping_log.insert("end", f"Request timed out for {host}\n")
                self.ping_log.see("end")

            self.after(0, _ui)

        threading.Thread(target=_task, daemon=True).start()
