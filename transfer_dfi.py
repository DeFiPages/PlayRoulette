import os
import time

from defichain import Node
from libs.read_accounts import read_accounts_from_csv
from libs.my_eth_utils import get_balance_dfi, get_balance_dusd
from libs.rpc_call import transferdomain, wait_for_confirmation

home_cookie = os.path.expanduser("~/.defi/changi/.cookie")
cookie_path = home_cookie if os.path.exists(home_cookie) else os.path.join(os.path.dirname(__file__), ".cookie")

with open(cookie_path, 'r') as f:
    username, password = f.read().strip().split(':')

node = Node(username, password, url="127.0.0.1", port=20554)  # Changi Testnet DFI RPC Port: 20554


def transfer_to_accounts(dvmaddress, accounts, amount, tokenname):
    MAX_RETRIES = 5  # Number of retries
    transaction_count = 0
    last_successful_txid = None

    def get_balance(eth_address, tokenname):
        if tokenname == "DFI":
            return get_balance_dfi(eth_address)
        elif tokenname == "DUSD":
            return get_balance_dusd(eth_address)
        else:
            raise ValueError(f"Unknown tokenname: {tokenname}")

    for account in accounts:
        eth_address = account['address']

        current_balance = get_balance(eth_address, tokenname)
        print(f"Current balance for {eth_address}: {current_balance}")

        if current_balance < float(amount):
            retry_count = 0

            while retry_count < MAX_RETRIES:
                try:
                    tx = transferdomain(node, dvmaddress, f"{amount}@{tokenname}", eth_address)
                    print(f"Sent {tokenname} to {eth_address}. Transaction ID: {tx}")
                    transaction_count += 1

                    if transaction_count == 64:
                        print("Waiting after 64 tx for the last transaction to be confirmed before proceeding...")
                        wait_for_confirmation(node, tx)
                        transaction_count = 0

                    last_successful_txid = tx
                    break

                except Exception as e:
                    error_msg = str(e)
                    if "evm-low-fee" in error_msg or "too-many-evm-txs-by-sender" in error_msg or "Invalid nonce" in error_msg:
                        print(
                            f"Exception occurred: {e}. Waiting for the last successful transaction to be confirmed before retrying...")

                        if last_successful_txid:
                            wait_for_confirmation(node, last_successful_txid)
                            transaction_count = 0

                        retry_count += 1
                    else:
                        raise e

            if retry_count == MAX_RETRIES:
                print(f"Failed to send transaction to {eth_address} after {MAX_RETRIES} retries.")

    return transaction_count, last_successful_txid


if __name__ == "__main__":

    dvmaddress = ""  # set dvm address with dfi token or put in .dfiaddress.txt

    # Read from file if empty
    if not dvmaddress:
        if os.path.exists(".dfiaddress.txt"):
            with open(".dfiaddress.txt", "r") as file:
                dvmaddress = file.readline().strip()
        else:
            print(".dfiaddress.txt not found!")

    accounts = read_accounts_from_csv()
    accounts.extend(read_accounts_from_csv(".ethereum_accounts.txt.vps"))
    transfer_to_accounts(dvmaddress, accounts, 10, "DFI")


