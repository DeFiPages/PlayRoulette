from enum import Enum
from libs.read_accounts import read_accounts_from_csv
from libs.eth_utils import w3,  roulette_address, roulette_abi, get_balance_cas, create_and_send_transaction


roulette_contract = w3.eth.contract(address=roulette_address, abi=roulette_abi)

class Color(Enum):
    GREEN = 0
    RED = 1
    BLACK = 2
    

def play_roulette(address, private_key):
    nonce = w3.eth.get_transaction_count(address, 'pending')
#    print(f"nonce pending {nonce}")
    selectedColor = Color.BLACK.value
    tokensBet = 1  # Or whatever value you have
    if get_balance_cas(address) < tokensBet:
        print(f"Error: Insufficient CAS balance for {address} to bet. Please ensure you have at least {tokensBet} CAS.")
        return
    
    gas_price = w3.to_wei(13.5, 'gwei')
    gas_buffer = 6
    create_and_send_transaction(roulette_contract, 'playRoulette', [selectedColor, tokensBet], address, private_key, nonce, gas_price, gas_buffer)

def print_roulette_game_events(from_block=0, to_block='latest'):
    # Define the event signature for the RouletteGame event
    roulette_game_event = roulette_contract.events.RouletteGame()

    # Filter the logs based on the event signature
    logs = roulette_game_event.get_logs(fromBlock=from_block, toBlock=to_block)

    # Process the logs to get the data
    for log in logs:
        # Extract event data
        event_data = log['args']
        NumberWin = event_data['NumberWin']
        result = event_data['result']
        tokensEarned = event_data['tokensEarned']

        # Print the event data
        print(f"NumberWin: {NumberWin}, Result: {result}, Tokens Earned: {tokensEarned}")

if __name__ == "__main__":
    #print_roulette_game_events(from_block=12607)
  
    current_block = w3.eth.block_number    
    print(f"Current block number: {current_block}")
    accounts = read_accounts_from_csv()
    for account in accounts:
        address = account['address']
        pk = account['private_key']
        play_roulette(address, pk)

 
    