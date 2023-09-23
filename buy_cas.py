from libs.read_accounts import read_accounts_from_csv
from libs.my_eth_utils import w3, dusd_contract, casino_contract, casino_address, get_balance_dusd, create_and_send_transaction




def buy_tokens(dusd_amount, address, private_key):

    if get_balance_dusd(address) < dusd_amount:
        print(f"Error: Insufficient DUSD balance for {address}. Please ensure you have at least {dusd_amount} DUSD.")
        return
    
    # Convert DUSD amount to Wei
    dusd_amount_wei = w3.to_wei(dusd_amount, 'ether')
    
    gas_price = w3.to_wei(13.5, 'gwei')
    
    nonce = w3.eth.get_transaction_count(address)
    print(f"nonce {nonce}")
    nonce = w3.eth.get_transaction_count(address, 'pending')
    print(f"nonce pending {nonce}")

    # Send approve transaction
    create_and_send_transaction(dusd_contract, 'approve', [casino_address, dusd_amount_wei], address, private_key, nonce, gas_price)

    # Increment nonce for next transaction
    nonce += 1

    # Send buyCASTokens transaction
    create_and_send_transaction(casino_contract, 'buyCASTokens', [dusd_amount_wei], address, private_key, nonce, gas_price)


if __name__ == "__main__":
    accounts = read_accounts_from_csv()
    for account in accounts:
        address = account['address']
        pk = account['private_key']
        dusd_amount_to_buy = 10  # Replace with the desired amount
        buy_tokens(dusd_amount_to_buy,address, pk)
 
    