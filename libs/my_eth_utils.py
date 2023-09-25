from web3 import Web3
import json
import os

GAS_BUFFER = 3  # need 3x more as gas_estimate, but in playRoulette 3x failed

# Read the contents of the provided ABI and address JSON files
file_paths = {
    "CasinoAbi": os.path.join(os.path.dirname(__file__), 'Casino-1133.json'),
    "CasinoAddress": os.path.join(os.path.dirname(__file__), 'Casino-address-1133.json'),
    "RouletteAbi": os.path.join(os.path.dirname(__file__), 'Roulette-1133.json'),
    "RouletteAddress": os.path.join(os.path.dirname(__file__), 'Roulette-address-1133.json'),
    "DST20Abi": os.path.join(os.path.dirname(__file__), 'DST20.json')
}

file_contents = {}
for key, path in file_paths.items():
    with open(path, 'r') as file:
        file_contents[key] = file.read()

# Extract the actual ABI from the provided JSON
casino_abi = json.loads(file_contents["CasinoAbi"])["abi"]
casino_address = json.loads(file_contents["CasinoAddress"])["address"]
roulette_abi = json.loads(file_contents["RouletteAbi"])["abi"]
roulette_address = json.loads(file_contents["RouletteAddress"])["address"]
dst20_abi = json.loads(file_contents["DST20Abi"])

# Initialize web3 connection, choose a provider
#provider = 'https://testnet-dmc.mydefichain.com:20551'
# provider='https://changinode1.defiserver.de'
provider = 'http://127.0.0.1:20551'
w3 = Web3(Web3.HTTPProvider(provider))

# Get the token addresses from the casino contract
casino_contract = w3.eth.contract(address=casino_address, abi=casino_abi)
dusd_address = casino_contract.functions.dusdToken().call()
cas_address = casino_contract.functions.casToken().call()

# Set up the token contracts
dusd_contract = w3.eth.contract(address=dusd_address, abi=dst20_abi)
cas_contract = w3.eth.contract(address=cas_address, abi=dst20_abi)


def get_balance_dfi(address):
    balance_wei = w3.eth.get_balance(address)
    return w3.from_wei(balance_wei, 'ether')


def get_token_balance(token_contract, address):
    # Get the number of decimals the token uses
    decimals = token_contract.functions.decimals().call()
    balance_in_smallest_unit = token_contract.functions.balanceOf(address).call()
    # Convert balance from smallest unit to main token unit
    balance = balance_in_smallest_unit / (10 ** decimals)
    # Convert balance from smallest unit to main token unit using Web3
    balance = Web3.from_wei(balance_in_smallest_unit, 'ether') * (10 ** (18 - decimals))
    return balance


def get_balance_cas(address):
    return get_token_balance(cas_contract, address)


def get_balance_dusd(address):
    return get_token_balance(dusd_contract, address)


def create_and_send_transaction(contract, fn_name, args, address, private_key, nonce, gas_price, gas_buffer=GAS_BUFFER):
    txn = {
        'to': contract.address,
        'gas': 2000000,  # Temporary gas value
        'gasPrice': gas_price,
        'nonce': nonce,
        'data': contract.encodeABI(fn_name=fn_name, args=args)
    }
    gas_estimate = w3.eth.estimate_gas(txn)
    txn['gas'] = int(gas_estimate * gas_buffer)

    try:
        signed_txn = w3.eth.account.sign_transaction(txn, private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        print(f"tx_hash for {fn_name} {tx_hash.hex()}")
        return tx_hash

    except Exception as e:
        print(f"Error for {fn_name}: {e}")
        return None
