import os
import csv
from eth_account import Account

# how many addresses and private keys will appended to .ethereum_accounts.txt
num_accounts = 10 

def generate_addresses_and_keys():
    accounts = []
    for _ in range(num_accounts):
        account = Account.create()
        accounts.append({
            "address": account.address,
            "private_key": account._private_key.hex()
        })
    return accounts

def save_to_csv(filename, accounts):
    # Check if file exists and get its size
    file_exists = os.path.isfile(filename)
    file_size = os.path.getsize(filename) if file_exists else 0

    with open(filename, "a", newline='') as f:
        writer = csv.writer(f)
        
        # Only write header if file is empty
        if file_size == 0:
            writer.writerow(["Address", "Private Key"])

        for acc in accounts:
            writer.writerow([acc["address"], acc["private_key"]])


if __name__ == "__main__":
    filename = ".ethereum_accounts.txt"    
    accounts = generate_addresses_and_keys()
    save_to_csv(filename, accounts)
    print(f"Saved {num_accounts} accounts to {filename}")