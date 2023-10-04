import os
import csv

def read_accounts_from_csv(account_file_name = ".ethereum_accounts.txt"):
    """
    Reads Ethereum accounts from a CSV file and returns them.

     """
    file_name = os.path.join(os.path.dirname(__file__), "..", account_file_name)
    accounts = []
    with open(file_name, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            accounts.append({
                "address": row["Address"],
                "private_key": row["Private Key"]
            })
    return accounts
