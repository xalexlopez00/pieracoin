#!/usr/bin/env python3
"""
PieraCoin User Wallet
For regular users. No admin privileges.
Features: Generate wallets, check balances, view blockchain
"""

import requests
import json
import os
from colorama import Fore, Style, init

# Initialize colorama for colored output
init(autoreset=True)

# Server configuration (from environment or default)
SERVER_URL = os.getenv("SERVER_URL", "http://localhost:8080")

def print_banner():
    """Print application banner"""
    print(f"{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}💰 PieraCoin User Wallet v1.0")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")

def generate_wallet():
    """Generate a new wallet with mnemonic seed phrase"""
    try:
        print(f"{Fore.YELLOW}Generating new wallet...{Style.RESET_ALL}")
        response = requests.get(
            f"{SERVER_URL}/wallet/generate",
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            mnemonic = data.get("mnemonic", "")
            print(f"\n{Fore.GREEN}✓ New Wallet Generated!{Style.RESET_ALL}")
            print(f"\n{Fore.RED}⚠️  SAVE THIS SEED PHRASE SECURELY:{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}{mnemonic}{Style.RESET_ALL}")
            print(f"\n{Fore.RED}⚠️  Never share this phrase with anyone!{Style.RESET_ALL}")
            print(f"\nYou can use this phrase to recover your wallet later.")
        else:
            print(f"{Fore.RED}✗ Error: {response.status_code}{Style.RESET_ALL}")
            print(response.text)
    except requests.exceptions.ConnectionError:
        print(f"{Fore.RED}✗ Error: Cannot connect to server at {SERVER_URL}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}✗ Error: {str(e)}{Style.RESET_ALL}")

def check_balance():
    """Check wallet balance"""
    try:
        address = input(f"{Fore.YELLOW}Enter wallet address: {Style.RESET_ALL}").strip()
        if not address:
            print(f"{Fore.RED}✗ Address cannot be empty{Style.RESET_ALL}")
            return
        
        print(f"{Fore.YELLOW}Checking balance...{Style.RESET_ALL}")
        response = requests.get(
            f"{SERVER_URL}/balance/{address}",
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            print(f"{Fore.GREEN}✓ Balance Information:{Style.RESET_ALL}")
            print(json.dumps(data, indent=2))
        elif response.status_code == 404:
            print(f"{Fore.YELLOW}Address not found{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}✗ Error: {response.status_code}{Style.RESET_ALL}")
    except requests.exceptions.ConnectionError:
        print(f"{Fore.RED}✗ Error: Cannot connect to server at {SERVER_URL}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}✗ Error: {str(e)}{Style.RESET_ALL}")

def view_blockchain():
    """View blockchain information"""
    try:
        print(f"{Fore.YELLOW}Fetching blockchain...{Style.RESET_ALL}")
        response = requests.get(
            f"{SERVER_URL}/chain",
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            print(f"\n{Fore.GREEN}✓ Blockchain Information:{Style.RESET_ALL}")
            print(f"Total Blocks: {data.get('blocks', 0)}")
            
            blocks = data.get('chain', [])
            if blocks:
                print(f"\n{Fore.CYAN}Latest Block:{Style.RESET_ALL}")
                latest = blocks[-1]
                print(f"  Index: {latest.get('index', 'N/A')}")
                print(f"  Hash: {latest.get('hash', 'N/A')[:32]}...")
                print(f"  Timestamp: {latest.get('timestamp', 'N/A')}")
                print(f"  Transactions: {len(latest.get('transactions', []))}")
        else:
            print(f"{Fore.RED}✗ Error: {response.status_code}{Style.RESET_ALL}")
    except requests.exceptions.ConnectionError:
        print(f"{Fore.RED}✗ Error: Cannot connect to server at {SERVER_URL}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}✗ Error: {str(e)}{Style.RESET_ALL}")

def send_transaction():
    """Send a transaction"""
    try:
        from_addr = input(f"{Fore.YELLOW}From address: {Style.RESET_ALL}").strip()
        to_addr = input(f"{Fore.YELLOW}To address: {Style.RESET_ALL}").strip()
        amount = input(f"{Fore.YELLOW}Amount: {Style.RESET_ALL}").strip()
        
        if not all([from_addr, to_addr, amount]):
            print(f"{Fore.RED}✗ All fields are required{Style.RESET_ALL}")
            return
        
        try:
            amount = float(amount)
        except ValueError:
            print(f"{Fore.RED}✗ Invalid amount{Style.RESET_ALL}")
            return
        
        transaction = {
            "from": from_addr,
            "to": to_addr,
            "amount": amount,
            "fee": 0.001
        }
        
        print(f"{Fore.YELLOW}Sending transaction...{Style.RESET_ALL}")
        response = requests.post(
            f"{SERVER_URL}/transaction",
            json=transaction,
            timeout=10
        )
        if response.status_code == 200:
            print(f"{Fore.GREEN}✓ Transaction submitted!{Style.RESET_ALL}")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"{Fore.RED}✗ Error: {response.status_code}{Style.RESET_ALL}")
            print(response.text)
    except requests.exceptions.ConnectionError:
        print(f"{Fore.RED}✗ Error: Cannot connect to server at {SERVER_URL}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}✗ Error: {str(e)}{Style.RESET_ALL}")

def check_server_health():
    """Check if server is running"""
    try:
        response = requests.get(
            f"{SERVER_URL}/health",
            timeout=5
        )
        if response.status_code == 200:
            print(f"{Fore.GREEN}✓ Server is running{Style.RESET_ALL}")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"{Fore.RED}✗ Server returned error: {response.status_code}{Style.RESET_ALL}")
    except requests.exceptions.ConnectionError:
        print(f"{Fore.RED}✗ Server not running at {SERVER_URL}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}✗ Error: {str(e)}{Style.RESET_ALL}")

def main():
    """Main menu loop"""
    print_banner()
    print(f"{Fore.CYAN}Server: {SERVER_URL}\n{Style.RESET_ALL}")
    
    while True:
        print(f"\n{Fore.CYAN}{'='*60}")
        print("User Options:")
        print("1. Generate New Wallet")
        print("2. Check Balance")
        print("3. Send Transaction")
        print("4. View Blockchain")
        print("5. Check Server Health")
        print("6. Exit")
        print(f"{'='*60}{Style.RESET_ALL}")
        
        choice = input(f"\n{Fore.YELLOW}Select option (1-6): {Style.RESET_ALL}").strip()
        
        if choice == "1":
            generate_wallet()
        elif choice == "2":
            check_balance()
        elif choice == "3":
            send_transaction()
        elif choice == "4":
            view_blockchain()
        elif choice == "5":
            check_server_health()
        elif choice == "6":
            print(f"{Fore.GREEN}Thank you for using PieraCoin!{Style.RESET_ALL}")
            break
        else:
            print(f"{Fore.RED}Invalid option. Please select 1-6.{Style.RESET_ALL}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Wallet closed.{Style.RESET_ALL}")
