from libs.read_accounts import read_accounts_from_csv
from libs.my_eth_utils import w3, casino_contract, get_balance_cas
from web3.exceptions import TransactionNotFound
import time


def wait_for_confirmation(tx_hash):
    while True:
        try:
            receipt = w3.eth.get_transaction_receipt(tx_hash)
            if receipt:
                return receipt
        except TransactionNotFound:
            pass
        time.sleep(10)  # Check every 10 seconds


assert w3.is_connected()

accounts = read_accounts_from_csv(".deployer_account.txt")

YOUR_PRIVATE_KEY = accounts[0]['private_key']
YOUR_OWNER_ADDRESS = accounts[0]['address']

nonce = w3.eth.get_transaction_count(YOUR_OWNER_ADDRESS, 'pending')

accounts = read_accounts_from_csv()
accounts.extend(read_accounts_from_csv(".ethereum_accounts.txt.vps"))

counter = 0
# Batch send 100 CAS Tokens to each address
for i, account in enumerate(accounts):
    address = account['address']
    cas = get_balance_cas(address)
    if cas > 0:
        print(f"Current balance for {address}: {cas}")
        continue  # Skip to the next iteration
    transaction = casino_contract.functions.transferCASToAddress(address, 100).build_transaction({
        'gas': 80000,
        'gasPrice': w3.to_wei(60, 'gwei'),
        'nonce': nonce,
    })

    signed_txn = w3.eth.account.sign_transaction(transaction, YOUR_PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    counter += 1  # Increment counter only when a transaction is sent
    print(f"{i} out of {len(accounts)}: Sent to {address} with transaction hash: {tx_hash.hex()}")

    nonce += 1

    # If it's the 60th transaction in the batch, wait for its confirmation
    if counter % 60 == 0:
        print(f"Waiting for confirmation of the last transaction in the batch: {tx_hash.hex()}")
        wait_for_confirmation(tx_hash)
