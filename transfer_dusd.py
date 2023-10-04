import os
from libs.read_accounts import read_accounts_from_csv
from transfer_dfi import transfer_to_accounts

if __name__ == "__main__":

    dvmaddress = ""  # set dvm address with dfi token or put in .dfiaddress.txt

    # Read from file if empty
    if not dvmaddress:
        if os.path.exists(".dusdaddress.txt"):
            with open(".dusdaddress.txt", "r") as file:
                dvmaddress = file.readline().strip()
        else:
            print(".dusdaddress.txt not found!")

    accounts = read_accounts_from_csv()
    transfer_to_accounts(dvmaddress, accounts, 10, "DUSD")
