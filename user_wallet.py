#!/usr/bin/env python3
"""
PieraCoin Miner & Wallet
User GUI with local mining effort, wallet generation, balances and history.
"""

import json
import os
import threading
import time
import hashlib

import customtkinter as ctk
import requests
from tkinter import messagebox

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

DEFAULT_SERVER = os.getenv("SERVER_URL", "https://pieracoin.onrender.com")

class UserWalletApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("PieraCoin Miner & Wallet")
        self.geometry("960x720")
        self.minsize(900, 660)
        self.server_url = DEFAULT_SERVER
        self.mining_thread = None
        self.build_interface()

    def build_interface(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_rowconfigure(6, weight=1)

        ctk.CTkLabel(sidebar, text="PieraCoin Wallet", font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, padx=20, pady=(20, 10))
        ctk.CTkButton(sidebar, text="Generate Wallet", command=self.generate_wallet, fg_color="#1f6aa5").grid(row=1, column=0, padx=20, pady=8, sticky="ew")
        ctk.CTkButton(sidebar, text="Check Balance", command=self.check_balance, fg_color="#1f6aa5").grid(row=2, column=0, padx=20, pady=8, sticky="ew")
        ctk.CTkButton(sidebar, text="View Transaction History", command=self.load_history, fg_color="#1f6aa5").grid(row=3, column=0, padx=20, pady=8, sticky="ew")
        ctk.CTkButton(sidebar, text="Check Server Health", command=self.check_server_health, fg_color="#1f6aa5").grid(row=4, column=0, padx=20, pady=8, sticky="ew")
        ctk.CTkLabel(sidebar, text="Server URL:").grid(row=5, column=0, padx=20, pady=(20, 4), sticky="w")
        self.server_entry = ctk.CTkEntry(sidebar, placeholder_text=self.server_url)
        self.server_entry.grid(row=6, column=0, padx=20, pady=(0, 20), sticky="ew")
        ctk.CTkButton(sidebar, text="Update Server", command=self.update_server).grid(row=7, column=0, padx=20, pady=(0, 20), sticky="ew")

        self.tabview = ctk.CTkTabview(self, width=700)
        self.tabview.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.tabview.add("Wallet")
        self.tabview.add("Mining")
        self.tabview.add("Balance")
        self.tabview.add("History")

        self.build_wallet_tab()
        self.build_mining_tab()
        self.build_balance_tab()
        self.build_history_tab()

    def build_wallet_tab(self):
        tab = self.tabview.tab("Wallet")
        tab.grid_columnconfigure(0, weight=1)

        self.mnemonic_text = ctk.CTkTextbox(tab, width=660, height=200, fg_color="#1b1b1b", corner_radius=12)
        self.mnemonic_text.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        self.address_label = ctk.CTkLabel(tab, text="Address: -", wraplength=660)
        self.address_label.grid(row=1, column=0, padx=20, pady=(0, 16), sticky="w")

    def build_mining_tab(self):
        tab = self.tabview.tab("Mining")
        tab.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(tab, text="Miner Address", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, padx=20, pady=(20, 8), sticky="w")
        self.mine_address_entry = ctk.CTkEntry(tab, placeholder_text="Enter your wallet address")
        self.mine_address_entry.grid(row=1, column=0, padx=20, pady=(0, 16), sticky="ew")

        self.mine_progress = ctk.CTkProgressBar(tab, width=660)
        self.mine_progress.grid(row=2, column=0, padx=20, pady=(0, 16), sticky="ew")
        self.mine_progress.set(0)

        self.mine_button = ctk.CTkButton(tab, text="Start Mining", command=self.start_mining, fg_color="#1f6aa5")
        self.mine_button.grid(row=3, column=0, padx=20, pady=8, sticky="ew")

        self.mine_status = ctk.CTkLabel(tab, text="Press start to begin mining.")
        self.mine_status.grid(row=4, column=0, padx=20, pady=10, sticky="w")

    def build_balance_tab(self):
        tab = self.tabview.tab("Balance")
        tab.grid_columnconfigure(0, weight=1)

        self.balance_address_entry = ctk.CTkEntry(tab, placeholder_text="Enter address to check balance")
        self.balance_address_entry.grid(row=0, column=0, padx=20, pady=(20, 12), sticky="ew")

        ctk.CTkButton(tab, text="Query Balance", command=self.check_balance, fg_color="#1f6aa5").grid(row=1, column=0, padx=20, pady=8, sticky="ew")

        self.balance_result = ctk.CTkTextbox(tab, width=660, height=220, fg_color="#1b1b1b", corner_radius=12)
        self.balance_result.grid(row=2, column=0, padx=20, pady=12, sticky="nsew")

    def build_history_tab(self):
        tab = self.tabview.tab("History")
        tab.grid_columnconfigure(0, weight=1)

        ctk.CTkButton(tab, text="Refresh History", command=self.load_history, fg_color="#1f6aa5").grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        self.history_text = ctk.CTkTextbox(tab, width=660, height=500, fg_color="#1b1b1b", corner_radius=12)
        self.history_text.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

    def update_server(self):
        server = self.server_entry.get().strip()
        if server:
            self.server_url = server.rstrip("/")
            messagebox.showinfo("Server Updated", f"Server set to {self.server_url}")

    def api_get(self, path):
        response = requests.get(f"{self.server_url}{path}", timeout=15)
        response.raise_for_status()
        return response.json()

    def api_post(self, path, payload):
        response = requests.post(f"{self.server_url}{path}", json=payload, timeout=20)
        response.raise_for_status()
        return response.json()

    def generate_wallet(self):
        def task():
            try:
                data = self.api_get("/wallet/generate")
                self.mnemonic_text.delete("0.0", ctk.END)
                self.mnemonic_text.insert(ctk.END, data.get("mnemonic", ""))
                self.address_label.configure(text=f"Address: {data.get('address', '-')}")
            except Exception as err:
                messagebox.showerror("Error", f"Could not generate wallet: {err}")

        threading.Thread(target=task, daemon=True).start()

    def start_mining(self):
        address = self.mine_address_entry.get().strip()
        if not address:
            messagebox.showwarning("Mining", "Please enter a miner address first.")
            return
        if self.mining_thread and self.mining_thread.is_alive():
            messagebox.showwarning("Mining", "Mining is already running.")
            return
        self.mining_thread = threading.Thread(target=self.run_mining, args=(address,), daemon=True)
        self.mining_thread.start()

    def run_mining(self, miner_address):
        duration = 45.0
        start_time = time.time()
        self.mine_status.configure(text="Mining in progress...")
        self.mine_progress.set(0)

        while time.time() - start_time < duration:
            hashlib.sha256(f"{miner_address}-{time.time()}".encode()).hexdigest()
            progress = min(1.0, (time.time() - start_time) / duration)
            self.mine_progress.set(progress)
            time.sleep(0.02)

        try:
            data = self.api_post("/mine", {"miner_address": miner_address})
            self.mine_status.configure(text="Mining completed successfully.")
            messagebox.showinfo("Mining Complete", f"Block mined and reward credited.\n{json.dumps(data, indent=2)}")
        except Exception as err:
            self.mine_status.configure(text="Mining finished with error.")
            messagebox.showerror("Mining Error", str(err))
        finally:
            self.mine_progress.set(1)

    def check_balance(self):
        address = self.balance_address_entry.get().strip()
        if not address:
            messagebox.showwarning("Balance", "Please enter an address.")
            return

        def task():
            try:
                data = self.api_get(f"/balance/{address}")
                self.balance_result.delete("0.0", ctk.END)
                self.balance_result.insert(ctk.END, json.dumps(data, indent=2))
            except Exception as err:
                messagebox.showerror("Error", str(err))

        threading.Thread(target=task, daemon=True).start()

    def load_history(self):
        def task():
            try:
                data = self.api_get("/transactions")
                self.history_text.delete("0.0", ctk.END)
                for tx in data.get("transactions", []):
                    self.history_text.insert(ctk.END, json.dumps(tx, indent=2) + "\n---\n")
            except Exception as err:
                messagebox.showerror("Error", str(err))

        threading.Thread(target=task, daemon=True).start()

    def check_server_health(self):
        def task():
            try:
                data = self.api_get("/health")
                messagebox.showinfo("Server Health", json.dumps(data, indent=2))
            except Exception as err:
                messagebox.showerror("Error", str(err))

        threading.Thread(target=task, daemon=True).start()

if __name__ == "__main__":
    app = UserWalletApp()
    app.mainloop()
