#!/usr/bin/env python3
"""
PieraCoin Central Command
Admin GUI with mining, network control, wallet overview and minting.
"""

import json
import os
import sys
import threading
import time
import hashlib

import customtkinter as ctk
import requests
from tkinter import messagebox

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

DEFAULT_SERVER = os.getenv("SERVER_URL", "https://pieracoin.onrender.com")

class AdminApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("PieraCoin Central Command")
        self.geometry("980x700")
        self.minsize(900, 650)
        self.admin_key = ""
        self.server_url = DEFAULT_SERVER
        self.headers = {}
        self.mining_thread = None
        self.global_mine_paused = False
        self.build_login_screen()

    def build_login_screen(self):
        self.login_frame = ctk.CTkFrame(self, corner_radius=20)
        self.login_frame.place(relx=0.5, rely=0.5, anchor=ctk.CENTER, relwidth=0.6, relheight=0.5)

        ctk.CTkLabel(self.login_frame, text="PieraCoin Central Command", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=(24, 10))
        ctk.CTkLabel(self.login_frame, text="Admin Key", anchor="w").pack(padx=20, pady=(10, 4))
        self.admin_entry = ctk.CTkEntry(self.login_frame, placeholder_text="Enter ADMIN_KEY")
        self.admin_entry.pack(fill="x", padx=20)

        ctk.CTkLabel(self.login_frame, text="Server URL", anchor="w").pack(padx=20, pady=(16, 4))
        self.server_entry = ctk.CTkEntry(self.login_frame, placeholder_text=self.server_url)
        self.server_entry.pack(fill="x", padx=20)

        self.login_button = ctk.CTkButton(self.login_frame, text="Connect", command=self.try_login, fg_color="#1f6aa5")
        self.login_button.pack(pady=24, padx=20, fill="x")

    def try_login(self):
        admin_key = self.admin_entry.get().strip()
        server_url = self.server_entry.get().strip() or self.server_url

        if not admin_key:
            messagebox.showerror("Authentication Required", "Please enter your ADMIN_KEY.")
            return

        self.admin_key = admin_key
        self.server_url = server_url.rstrip("/")
        self.headers = {
            "X-Admin-Key": self.admin_key,
            "Content-Type": "application/json",
        }

        try:
            response = requests.get(f"{self.server_url}/health", timeout=8)
            if response.status_code == 200:
                self.login_frame.destroy()
                self.build_main_interface()
            else:
                messagebox.showerror("Connection Failed", f"Server returned {response.status_code}")
        except Exception as err:
            messagebox.showerror("Connection Failed", str(err))

    def build_main_interface(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(6, weight=1)

        ctk.CTkLabel(self.sidebar, text="Central Command", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, padx=20, pady=(20, 10))
        ctk.CTkButton(self.sidebar, text="Refresh Status", command=self.refresh_dashboard).grid(row=1, column=0, padx=20, pady=8, sticky="ew")
        ctk.CTkButton(self.sidebar, text="Pause Global Mining", command=self.pause_global_mining).grid(row=2, column=0, padx=20, pady=8, sticky="ew")
        ctk.CTkButton(self.sidebar, text="Resume Global Mining", command=self.resume_global_mining).grid(row=3, column=0, padx=20, pady=8, sticky="ew")
        ctk.CTkButton(self.sidebar, text="Refresh Wallet List", command=self.refresh_wallets).grid(row=4, column=0, padx=20, pady=8, sticky="ew")
        ctk.CTkButton(self.sidebar, text="Logout", command=self.restart_app, fg_color="#d44a4a", hover_color="#b73a3a").grid(row=5, column=0, padx=20, pady=8, sticky="ew")

        self.tabview = ctk.CTkTabview(self, width=700)
        self.tabview.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.tabview.add("Dashboard")
        self.tabview.add("Mining")
        self.tabview.add("Wallets")
        self.tabview.add("Mint")

        self.build_dashboard_tab()
        self.build_mining_tab()
        self.build_wallets_tab()
        self.build_mint_tab()

        self.refresh_dashboard()
        self.refresh_wallets()

    def build_dashboard_tab(self):
        tab = self.tabview.tab("Dashboard")
        tab.grid_columnconfigure(0, weight=1)
        self.status_text = ctk.CTkTextbox(tab, width=640, height=420, fg_color="#1b1b1b", corner_radius=12)
        self.status_text.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

    def build_mining_tab(self):
        tab = self.tabview.tab("Mining")
        tab.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(tab, text="Local Mining", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, pady=(20, 10), sticky="w", padx=20)
        ctk.CTkLabel(tab, text="Miner address for reward:").grid(row=1, column=0, sticky="w", padx=20)
        self.miner_address_entry = ctk.CTkEntry(tab, placeholder_text="Enter reward address")
        self.miner_address_entry.grid(row=2, column=0, padx=20, pady=(4, 12), sticky="ew")

        self.progress = ctk.CTkProgressBar(tab, width=600)
        self.progress.grid(row=3, column=0, padx=20, pady=(8, 12), sticky="ew")
        self.progress.set(0)

        self.mine_button = ctk.CTkButton(tab, text="Start Local Mine", command=self.start_local_mine, fg_color="#1f6aa5")
        self.mine_button.grid(row=4, column=0, padx=20, pady=10, sticky="ew")

        self.mining_status = ctk.CTkLabel(tab, text="Ready to mine.")
        self.mining_status.grid(row=5, column=0, padx=20, pady=10, sticky="w")

    def build_wallets_tab(self):
        tab = self.tabview.tab("Wallets")
        tab.grid_columnconfigure(0, weight=1)

        self.wallets_list = ctk.CTkTextbox(tab, width=640, height=400, fg_color="#1b1b1b", corner_radius=12)
        self.wallets_list.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

    def build_mint_tab(self):
        tab = self.tabview.tab("Mint")
        tab.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(tab, text="Inject PIERAs", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, pady=(20, 10), sticky="w", padx=20)
        ctk.CTkLabel(tab, text="Destination address:").grid(row=1, column=0, sticky="w", padx=20)
        self.mint_address_entry = ctk.CTkEntry(tab, placeholder_text="Enter target address")
        self.mint_address_entry.grid(row=2, column=0, padx=20, pady=(4, 10), sticky="ew")

        ctk.CTkLabel(tab, text="Amount to mint:").grid(row=3, column=0, sticky="w", padx=20)
        self.mint_amount_entry = ctk.CTkEntry(tab, placeholder_text="Enter amount")
        self.mint_amount_entry.grid(row=4, column=0, padx=20, pady=(4, 12), sticky="ew")

        ctk.CTkButton(tab, text="Inject Coins", command=self.inject_coins, fg_color="#1f6aa5").grid(row=5, column=0, padx=20, pady=10, sticky="ew")
        self.mint_status = ctk.CTkLabel(tab, text="Ready to mint.")
        self.mint_status.grid(row=6, column=0, padx=20, pady=10, sticky="w")

    def api_get(self, path, admin=False):
        url = f"{self.server_url}{path}"
        headers = self.headers if admin else {"Content-Type": "application/json"}
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        return response.json()

    def api_post(self, path, payload=None, admin=False):
        url = f"{self.server_url}{path}"
        headers = self.headers if admin else {"Content-Type": "application/json"}
        response = requests.post(url, json=payload or {}, headers=headers, timeout=20)
        response.raise_for_status()
        return response.json()

    def refresh_dashboard(self):
        def task():
            try:
                health = self.api_get("/health")
                chain = self.api_get("/chain")
                text = json.dumps({"health": health, "chain": {"blocks": chain.get("blocks")}}, indent=2)
                self.status_text.delete("0.0", ctk.END)
                self.status_text.insert(ctk.END, text)
            except Exception as err:
                self.status_text.delete("0.0", ctk.END)
                self.status_text.insert(ctk.END, f"Error refreshing dashboard:\n{err}")

        threading.Thread(target=task, daemon=True).start()

    def refresh_wallets(self):
        def task():
            try:
                data = self.api_get("/wallets", admin=True)
                wallets = data.get("wallets", [])
                self.wallets_list.delete("0.0", ctk.END)
                if not wallets:
                    self.wallets_list.insert(ctk.END, "No generated addresses yet.")
                    return
                for addr in wallets:
                    self.wallets_list.insert(ctk.END, f"{addr}\n")
            except Exception as err:
                self.wallets_list.delete("0.0", ctk.END)
                self.wallets_list.insert(ctk.END, f"Error loading wallets:\n{err}")

        threading.Thread(target=task, daemon=True).start()

    def pause_global_mining(self):
        def task():
            try:
                self.api_post("/miner/stop", admin=True)
                messagebox.showinfo("Global Mining", "Global mining has been paused.")
            except Exception as err:
                messagebox.showerror("Error", str(err))

        threading.Thread(target=task, daemon=True).start()

    def resume_global_mining(self):
        def task():
            try:
                self.api_post("/miner/start", admin=True)
                messagebox.showinfo("Global Mining", "Global mining has been resumed.")
            except Exception as err:
                messagebox.showerror("Error", str(err))

        threading.Thread(target=task, daemon=True).start()

    def start_local_mine(self):
        if self.mining_thread and self.mining_thread.is_alive():
            messagebox.showwarning("Mining", "Mining is already in progress.")
            return
        address = self.miner_address_entry.get().strip()
        if not address:
            messagebox.showwarning("Mining", "Please enter a miner address first.")
            return
        self.mining_thread = threading.Thread(target=self.local_mine, args=(address,), daemon=True)
        self.mining_thread.start()

    def local_mine(self, miner_address):
        duration = 45.0
        start_time = time.time()
        self.progress.set(0)
        self.mining_status.configure(text="Mining in progress...")

        while time.time() - start_time < duration:
            _ = hashlib.sha256(f"{self.server_url}-{miner_address}-{time.time()}".encode()).hexdigest()
            progress = min(1.0, (time.time() - start_time) / duration)
            self.progress.set(progress)
            time.sleep(0.02)

        try:
            response = self.api_post("/mine", {"miner_address": miner_address})
            self.mining_status.configure(text="Mining completed. Reward sent.")
            messagebox.showinfo("Mining Complete", f"Block mined successfully!\n{json.dumps(response, indent=2)}")
        except Exception as err:
            self.mining_status.configure(text="Mining completed with errors.")
            messagebox.showerror("Mining Error", str(err))
        finally:
            self.progress.set(1)

    def inject_coins(self):
        address = self.mint_address_entry.get().strip()
        amount = self.mint_amount_entry.get().strip()
        if not address or not amount:
            messagebox.showwarning("Mint", "Please enter address and amount.")
            return

        try:
            amount_value = float(amount)
        except ValueError:
            messagebox.showerror("Mint", "Amount must be a valid number.")
            return

        def task():
            try:
                result = self.api_post("/mint", {"address": address, "amount": amount_value}, admin=True)
                self.mint_status.configure(text="Mint completed successfully.")
                messagebox.showinfo("Mint Success", json.dumps(result, indent=2))
            except Exception as err:
                self.mint_status.configure(text="Mint failed.")
                messagebox.showerror("Mint Error", str(err))

        threading.Thread(target=task, daemon=True).start()

    def restart_app(self):
        self.destroy()
        os.execl(sys.executable, sys.executable, *sys.argv)

if __name__ == "__main__":
    app = AdminApp()
    app.mainloop()
