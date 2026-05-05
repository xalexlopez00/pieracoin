#!/usr/bin/env python3
"""
PieraCoin Admin Panel
Only for administrators. Contains the master API key.
"""

import requests
import json
import os
from colorama import Fore, Style, init

# Initialize colorama for colored output
init(autoreset=True)

# ⚠️ ADMIN SECRET KEY - KEEP THIS SAFE AND SECRET
ADMIN_KEY = os.getenv("ADMIN_KEY", "your-super-secret-admin-key-here")

# Server configuration
SERVER_URL = os.getenv("SERVER_URL", "http://localhost:8080")

# Headers for authenticated requests
HEADERS = {
    "X-Admin-Key": ADMIN_KEY,
    "Content-Type": "application/json"
}

def print_banner():
    """Print application banner"""
    print(f"{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}🛡️  PieraCoin Admin Panel v1.0")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")

def start_miner():
    """Start the miner"""
    try:
        print(f"{Fore.YELLOW}Starting miner...{Style.RESET_ALL}")
        response = requests.post(
            f"{SERVER_URL}/miner/start",
            headers=HEADERS,
            timeout=10
        )
        if response.status_code == 200:
            print(f"{Fore.GREEN}✓ Miner started successfully!{Style.RESET_ALL}")
            print(json.dumps(response.json(), indent=2))
        elif response.status_code == 401:
            print(f"{Fore.RED}✗ Unauthorized: Invalid admin key{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}✗ Error: {response.status_code}{Style.RESET_ALL}")
            print(response.text)
    except requests.exceptions.ConnectionError:
        print(f"{Fore.RED}✗ Error: Cannot connect to server at {SERVER_URL}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}✗ Error: {str(e)}{Style.RESET_ALL}")

def stop_miner():
    """Stop the miner"""
    try:
        print(f"{Fore.YELLOW}Stopping miner...{Style.RESET_ALL}")
        response = requests.post(
            f"{SERVER_URL}/miner/stop",
            headers=HEADERS,
            timeout=10
        )
        if response.status_code == 200:
            print(f"{Fore.GREEN}✓ Miner stopped successfully!{Style.RESET_ALL}")
            print(json.dumps(response.json(), indent=2))
        elif response.status_code == 401:
            print(f"{Fore.RED}✗ Unauthorized: Invalid admin key{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}✗ Error: {response.status_code}{Style.RESET_ALL}")
            print(response.text)
    except requests.exceptions.ConnectionError:
        print(f"{Fore.RED}✗ Error: Cannot connect to server at {SERVER_URL}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}✗ Error: {str(e)}{Style.RESET_ALL}")

def check_system_status():
    """Check system status and metrics"""
    try:
        print(f"{Fore.YELLOW}Fetching system status...{Style.RESET_ALL}")
        
        # Get health status
        health_response = requests.get(
            f"{SERVER_URL}/health",
            timeout=10
        )
        
        # Get metrics (requires admin key)
        metrics_response = requests.get(
            f"{SERVER_URL}/metrics",
            headers=HEADERS,
            timeout=10
        )
        
        if health_response.status_code == 200:
            print(f"{Fore.GREEN}✓ Server Status:{Style.RESET_ALL}")
            print(json.dumps(health_response.json(), indent=2))
        
        if metrics_response.status_code == 200:
            print(f"\n{Fore.GREEN}✓ Metrics:{Style.RESET_ALL}")
            print(metrics_response.text[:500])  # Print first 500 chars
        elif metrics_response.status_code == 401:
            print(f"{Fore.RED}✗ Unauthorized: Invalid admin key for metrics{Style.RESET_ALL}")
        
    except requests.exceptions.ConnectionError:
        print(f"{Fore.RED}✗ Error: Cannot connect to server at {SERVER_URL}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}✗ Error: {str(e)}{Style.RESET_ALL}")

def mine_block():
    """Mine a single block"""
    try:
        print(f"{Fore.YELLOW}Mining block...{Style.RESET_ALL}")
        response = requests.post(
            f"{SERVER_URL}/mine",
            headers=HEADERS,
            timeout=30  # Mining can take time
        )
        if response.status_code == 200:
            print(f"{Fore.GREEN}✓ Block mined successfully!{Style.RESET_ALL}")
            print(json.dumps(response.json(), indent=2))
        elif response.status_code == 401:
            print(f"{Fore.RED}✗ Unauthorized: Invalid admin key{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}✗ Error: {response.status_code}{Style.RESET_ALL}")
    except requests.exceptions.Timeout:
        print(f"{Fore.YELLOW}⏱️  Mining is taking a while...{Style.RESET_ALL}")
    except requests.exceptions.ConnectionError:
        print(f"{Fore.RED}✗ Error: Cannot connect to server at {SERVER_URL}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}✗ Error: {str(e)}{Style.RESET_ALL}")

def view_blockchain():
    """View the blockchain"""
    try:
        print(f"{Fore.YELLOW}Fetching blockchain...{Style.RESET_ALL}")
        response = requests.get(
            f"{SERVER_URL}/chain",
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            print(f"{Fore.GREEN}✓ Blockchain Info:{Style.RESET_ALL}")
            print(f"Total blocks: {data.get('blocks', 0)}")
            print(f"Chain length: {len(data.get('chain', []))}")
        else:
            print(f"{Fore.RED}✗ Error: {response.status_code}{Style.RESET_ALL}")
    except requests.exceptions.ConnectionError:
        print(f"{Fore.RED}✗ Error: Cannot connect to server at {SERVER_URL}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}✗ Error: {str(e)}{Style.RESET_ALL}")

def main():
    """Main menu loop"""
    print_banner()
    
    if ADMIN_KEY == "your-super-secret-admin-key-here":
        print(f"{Fore.RED}⚠️  WARNING: Using default admin key!{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Set ADMIN_KEY environment variable for production{Style.RESET_ALL}\n")
    
    print(f"{Fore.CYAN}Server: {SERVER_URL}\n{Style.RESET_ALL}")
    
    while True:
        print(f"\n{Fore.CYAN}{'='*60}")
        print("Admin Options:")
        print("1. Start Miner")
        print("2. Stop Miner")
        print("3. Check System Status")
        print("4. Mine Single Block")
        print("5. View Blockchain")
        print("6. Exit")
        print(f"{'='*60}{Style.RESET_ALL}")
        
        choice = input(f"\n{Fore.YELLOW}Select option (1-6): {Style.RESET_ALL}").strip()
        
        if choice == "1":
            start_miner()
        elif choice == "2":
            stop_miner()
        elif choice == "3":
            check_system_status()
        elif choice == "4":
            mine_block()
        elif choice == "5":
            view_blockchain()
        elif choice == "6":
            print(f"{Fore.GREEN}Goodbye!{Style.RESET_ALL}")
            break
        else:
            print(f"{Fore.RED}Invalid option. Please select 1-6.{Style.RESET_ALL}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Admin panel closed.{Style.RESET_ALL}")
