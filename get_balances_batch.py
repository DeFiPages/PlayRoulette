from libs.read_accounts import read_accounts_from_csv
from libs.eth_batch import get_batch_dfi_balance, get_batch_dusd_balance, get_batch_cas_balance

if __name__ == "__main__":
    accounts = read_accounts_from_csv()
    addresses = [account['address'] for account in accounts]

    dfi_balances = get_batch_dfi_balance(addresses)
    cas_balances = get_batch_cas_balance(addresses)
    dusd_balances = get_batch_dusd_balance(addresses)

    for address in addresses:
        print(f"{address}: {dfi_balances[address]} DFI, {dusd_balances[address]} DUSD, {cas_balances[address]} CAS")