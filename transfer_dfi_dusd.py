import os
from defichain import Node
from libs.read_accounts import read_accounts_from_csv
from libs.my_eth_utils import get_balance_dfi, get_balance_dusd
from libs.rpc_call import transferdomain


home_cookie = os.path.expanduser("~/.defi/changi/.cookie")
cookie_path = home_cookie if os.path.exists(home_cookie) else os.path.join(os.path.dirname(__file__), ".cookie")

with open(cookie_path, 'r') as f:
    username, password = f.read().strip().split(':')

node = Node(username, password, url="127.0.0.1", port=20554)  # Changi Testnet DFI RPC Port: 20554

dvmaddress="" # set dvm address or put in .dvmaddress.txt


def do_transfer(eth_address):
    if get_balance_dfi(eth_address) < 2:
        tx = transferdomain(node, dvmaddress, "2@DFI", eth_address)
        print(f"Sent DFI to {eth_address}. Transaction ID: {tx}")
    if get_balance_dusd(eth_address) < 10:
        tx = transferdomain(node, dvmaddress, "10@DUSD", eth_address)
        print(f"Sent DUSD to {eth_address}. Transaction ID: {tx}")

if __name__ == "__main__":
    # Read from file if empty
    if not dvmaddress:
        if os.path.exists(".dvmaddress.txt"):
            with open(".dvmaddress.txt", "r") as file:
                dvmaddress = file.readline().strip()
        else:
            print(".dvmaddress.txt not found!")
              
    accounts = read_accounts_from_csv()
    for account in accounts:
        address = account['address']
        do_transfer(address)
