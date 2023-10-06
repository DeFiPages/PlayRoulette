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
confirmation_times = []
for i, account in enumerate(accounts):
    address = account['address']
    cas = get_balance_cas(address)
    if cas > 150:
        print(f"Current balance for {address}: {cas}")
        continue  # Skip to the next iteration
    transaction = casino_contract.functions.transferCASToAddress(address, 100).build_transaction({
        'gas': 100000,
        'gasPrice': w3.to_wei(60, 'gwei'),
        'nonce': nonce,
    })

    signed_txn = w3.eth.account.sign_transaction(transaction, YOUR_PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    counter += 1  # Increment counter only when a transaction is sent
    #print(f"{i} out of {len(accounts)}: Sent to {address} with transaction hash: {tx_hash.hex()}")
    print(f"{i} ", end="")
    nonce += 1

    # If it's the 60th transaction in the batch, wait for its confirmation
    if counter % 60 == 0:
        start_time = time.time()  # Start timer
        print()
        print(f"Waiting for confirmation of {tx_hash.hex()}", end="")
        wait_for_confirmation(tx_hash)
        end_time = time.time()  # End timer

        elapsed_time = end_time - start_time
        confirmation_times.append(elapsed_time)

        print(f" - Time taken: {elapsed_time:.2f} seconds")

# Calculate and print statistics for the confirmation times
if confirmation_times:
    avg_time = sum(confirmation_times) / len(confirmation_times)
    min_time = min(confirmation_times)
    max_time = max(confirmation_times)
    p5_time = sorted(confirmation_times)[int(0.05 * len(confirmation_times))]  # 5% Percentil
    p50_time = sorted(confirmation_times)[int(0.5 * len(confirmation_times))]  # Median
    p95_time = sorted(confirmation_times)[int(0.95 * len(confirmation_times))]  # 95% Percentil
    print(f"Stats: Avg={avg_time:.2f}s, Min={min_time:.2f}s, Max={max_time:.2f}s, "
          f"P5={p5_time:.2f}s, P50={p50_time:.2f}s, P95={p95_time:.2f}s")
