import time
import json
import requests
from enum import Enum

from libs.read_accounts import read_accounts_from_csv
from libs.my_eth_utils import w3, roulette_address, roulette_abi
from libs.eth_batch import get_batch_nonces, get_batch_cas_balance, create_signed_transaction

BATCH_SIZE = 10000  # Maximum number of addresses per batch


class Color(Enum):
    GREEN = 0
    RED = 1
    BLACK = 2


selected_color = Color.BLACK.value
tokens_bet = 1

roulette_contract = w3.eth.contract(address=roulette_address, abi=roulette_abi)


def estimate_gas(first_nonce, gas_price):
    if not first_nonce:
        raise ValueError("No valid nonce available for gas estimation")

    try:
        return int(w3.eth.estimate_gas({
            'to': roulette_contract.address,
            'gas': 2000000,
            'gasPrice': gas_price,
            'nonce': first_nonce,
            'data': roulette_contract.encodeABI(
                fn_name='playRoulette', args=[selected_color, tokens_bet]
            )
        }) * 6)
    except Exception as e:
        print(f"Error estimating gas: {e}")
        raise


def process_account(account, gas_estimate, gas_price, id):
    address = account['address']
    private_key = account['private_key']
    nonce = account['nonce']
    cas_balance = account['cas_balance']
    if nonce is None or cas_balance is None or cas_balance < tokens_bet:
        return None

    try:
        signed_txn = create_signed_transaction(
            roulette_contract, 'playRoulette', [selected_color, tokens_bet],
            address, private_key, nonce, gas_price, gas_estimate
        )
        if not signed_txn:
            return None

        return {
            "jsonrpc": "2.0",
            "method": "eth_sendRawTransaction",
            "params": [signed_txn.rawTransaction.hex()],
            "id": id,
        }

    except Exception as e:
        print(f"Error processing account {address}: {e}")
        return None


def send_batch_requests(rpc_payloads):
    try:
        response = requests.post(
            w3.provider.endpoint_uri,
            json=list(rpc_payloads),
            headers={'Content-Type': 'application/json'}
        )
        response.raise_for_status()

        for result in response.json():
            print(f"tx_hash {result.get('result')}")
    except (requests.RequestException, json.JSONDecodeError) as e:
        print(f"Error sending batch transactions: {e}")


def play_roulette_batch(accounts):
    total_accounts = len(accounts)

    # Get addresses, nonces and cas_balances for all accounts
    all_addresses = [account['address'] for account in accounts]
    all_nonces = get_batch_nonces(all_addresses)
    all_cas_balances = get_batch_cas_balance(all_addresses)

    # Append nonce and cas_balance to each account in accounts list
    for account in accounts:
        address = account['address']
        account['nonce'] = all_nonces.get(address, None)
        account['cas_balance'] = all_cas_balances.get(address, None)

    for i in range(0, total_accounts, BATCH_SIZE):
        batch_accounts = accounts[i:i + BATCH_SIZE]
        print(f"Processing batch {i // BATCH_SIZE + 1} of {((total_accounts - 1) // BATCH_SIZE) + 1}")
        gas_price = w3.to_wei(13.5, 'gwei')
        gas_estimate = estimate_gas(batch_accounts[0]['nonce'], gas_price)
        rpc_payloads = []
        for account in batch_accounts:
            rpc_payload = process_account(account, gas_estimate, gas_price, len(rpc_payloads))
            if rpc_payload:
                rpc_payloads.append(rpc_payload)

        send_batch_requests(rpc_payloads)


if __name__ == "__main__":
    current_block = w3.eth.block_number
    print(f"Current block number: {current_block}")
    accounts = read_accounts_from_csv()
    start_time = time.time()  # Capture the start time
    play_roulette_batch(accounts)
    end_time = time.time()  # Capture the end time

    duration = end_time - start_time  # Calculate the duration
    print(f"Duration of play_roulette_batch: {duration} seconds")
