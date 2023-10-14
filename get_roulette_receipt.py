from libs.my_eth_utils import w3, roulette_address
from libs.eth_batch import send_batch_json_rpc_request
import sys

def get_batch_blocks(from_block, to_block):
    method = 'eth_getBlockByNumber'
    params_list = [[hex(block_number), True] for block_number in range(from_block, to_block + 1)]
    endpoint = w3.provider.endpoint_uri
    response_data = send_batch_json_rpc_request(endpoint, method, params_list)
    if 'error' in response_data:
        print(response_data)
    return response_data

def extract_relevant_txs(batch_blocks, contract_address):
    relevant_txs = {}
    for block_data in batch_blocks:
        if isinstance(block_data, dict):
            if 'result' in block_data:
                block = block_data['result']
                block_number = int(block['number'], 16)  # Convert hex to int
                tx_hashes = [tx['hash'] for tx in block['transactions'] if tx['to'] == contract_address]
                if tx_hashes:
                    relevant_txs[block_number] = {
                        "total_tx_count": len(tx_hashes),
                        "tx_hashes": tx_hashes,
                    }
            else:
                print(f"Error for block: {block_data.get('error', {}).get('message', 'Unknown error')}")
        else:
            print(f"Unexpected block data type. Received: {block_data}")
    return relevant_txs



def get_block_transactions(from_block, to_block, contract_address, batch_size=100):
    block_transactions = {}
    for start_block in range(from_block, to_block + 1, batch_size):
        end_block = min(start_block + batch_size - 1, to_block)

        batch_blocks = get_batch_blocks(start_block, end_block)
        relevant_txs = extract_relevant_txs(batch_blocks, contract_address)
        block_transactions.update(relevant_txs)

        print(f"Processed blocks {start_block} to {end_block}.")
    return block_transactions


def get_block_transactions_(from_block, to_block, contract_address):
    block_transactions = {}
    for block_number in range(from_block, to_block + 1):
        if block_number % 100 == 0:
            sys.stdout.write(f"Fetching transactions for block {block_number} out of {to_block}...\r")
            sys.stdout.flush()
        block = w3.eth.get_block(block_number, full_transactions=True)
        tx_hashes = [tx.hash.hex() for tx in block.transactions if tx.to == contract_address]
        total_tx_count = len(tx_hashes)
        if tx_hashes:  # Only add blocks with tx to the specified contract address
            block_transactions[block_number] = {
                "total_tx_count": total_tx_count,
                "tx_hashes": tx_hashes,
            }
    return block_transactions

def get_batch_transaction_receipts(transaction_hashes):
    method = 'eth_getTransactionReceipt'
    params_list = [[tx_hash] for tx_hash in transaction_hashes]
    response_data = send_batch_json_rpc_request(w3.provider.endpoint_uri, method, params_list)

    receipts = {}
    for resp, tx_hash in zip(response_data, transaction_hashes):
        if 'result' in resp:
            receipts[tx_hash] = resp['result']
        else:
            print(f"Error getting receipt for {tx_hash}: {resp.get('error', {}).get('message', 'Unknown error')}")
            receipts[tx_hash] = None
    return receipts

# Specify the block range
from_block = 1500 # Example starting block number
to_block = w3.eth.block_number

# Get all transaction hashes for each block for the specified contract address in the block range
block_transactions = get_block_transactions(from_block, to_block, roulette_address)

total_transactions_count = 0
# Go through each block and print the results
for block_number, block_data in block_transactions.items():
    tx_hashes = block_data["tx_hashes"]
    total_tx_count = block_data["total_tx_count"]

    total_transactions_count += total_tx_count

    transaction_receipts = get_batch_transaction_receipts(tx_hashes)

    succeeded = sum(1 for receipt in transaction_receipts.values() if receipt and int(receipt['status'], 16) == 1)
    failed = total_tx_count - succeeded

    print(
        f"Block {block_number}: "
        f"{succeeded} transactions succeeded, "
        f"{failed} transactions failed, "
        f"{total_tx_count} total transactions in block."
    )
print(f"Total transactions: {total_transactions_count}")
