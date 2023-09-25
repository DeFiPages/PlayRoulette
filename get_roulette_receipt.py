from libs.my_eth_utils import w3, roulette_address
from libs.eth_batch import send_batch_json_rpc_request


def get_block_transactions(from_block, to_block, contract_address):
    block_transactions = {}
    for block_number in range(from_block, to_block + 1):
        block = w3.eth.get_block(block_number, full_transactions=True)
        total_tx_count = w3.eth.get_block_transaction_count(block_number)
        tx_hashes = [tx.hash.hex() for tx in block.transactions if tx.to == contract_address]
        if tx_hashes or total_tx_count:
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
from_block = 27641 #27600
to_block = w3.eth.block_number

# Get all transaction hashes for each block for the specified contract address in the block range
block_transactions = get_block_transactions(from_block, to_block, roulette_address)

# Go through each block and print the results
for block_number, block_data in block_transactions.items():
    tx_hashes = block_data["tx_hashes"]
    total_tx_count = block_data["total_tx_count"]

    transaction_receipts = get_batch_transaction_receipts(tx_hashes)

    succeeded = sum(1 for receipt in transaction_receipts.values() if receipt and int(receipt['status'], 16) == 1)
    failed = len(tx_hashes) - succeeded

    print(f"Block {block_number}: {succeeded} transactions to contract succeeded, {failed} transactions to contract failed, {total_tx_count} total transactions in block.")