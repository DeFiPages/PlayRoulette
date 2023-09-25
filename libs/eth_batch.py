import json
import requests
from typing import List, Optional, Any, Dict

from libs.my_eth_utils import w3, cas_address, dusd_address

def send_batch_json_rpc_request(endpoint: str, method: str, params_list: List[List[Optional[Any]]]) -> List[
    Dict[str, Any]]:
    """
    Send a batch JSON-RPC request to the specified endpoint.

    :param endpoint: The URL of the Ethereum node's JSON-RPC endpoint.
    :param method: The JSON-RPC method to call.
    :param params_list: A list where each element is a list of parameters for the JSON-RPC method.
    :return: A list of dictionaries containing the responses from the server.
    """
    # Prepare batch RPC payload
    batch_rpc_payload = [{
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": idx,
    } for idx, params in enumerate(params_list)]

    # Send batch request
    try:
        response = requests.post(endpoint, json=batch_rpc_payload, headers={'Content-Type': 'application/json'})
        response.raise_for_status()
        return response.json()
    except requests.HTTPError:
        print(f"Error: Received status code {response.status_code} with response: {response.text}")
        return []
    except (json.JSONDecodeError, Exception) as e:
        print(f"Error sending batch JSON-RPC request: {e}")
        return []


def get_batch_nonces(addresses: List[str], block_identifier: str = 'pending') -> Dict[
    str, Optional[int]]:
    method = 'eth_getTransactionCount'
    params_list = [[address, block_identifier] for address in addresses]
    endpoint = w3.provider.endpoint_uri
    response_data = send_batch_json_rpc_request(endpoint, method, params_list)

    nonces = {}
    for resp, address in zip(response_data, addresses):
        if 'result' in resp:
            nonces[address] = int(resp['result'], 16)
        else:
            print(f"Error getting nonce for {address}: {resp.get('error', {}).get('message', 'Unknown error')}")
            nonces[address] = None
    return nonces


def get_batch_dfi_balance(addresses: List[str]) -> Dict[str, int]:
    method = 'eth_getBalance'
    params_list = [[address, 'latest'] for address in addresses]
    response_data = send_batch_json_rpc_request(w3.provider.endpoint_uri, method, params_list)

    balances = {}
    for resp, address in zip(response_data, addresses):
        if 'result' in resp:
            balances[address] = w3.from_wei(int(resp['result'], 16), 'ether')
        else:
            print(f"Error getting balance for {address}: {resp.get('error', {}).get('message', 'Unknown error')}")
            balances[address] = None
    return balances


def get_batch_balance_of(endpoint: str, contract_address: str, addresses: list) -> dict:
    method = 'eth_call'
    params_list = []

    # ABI encoding for balanceOf function: balanceOf(address)
    function_signature = 'balanceOf(address)'
    # First 4 bytes of the hash of the function signature
    function_selector = w3.keccak(text=function_signature)[0:4].hex()

    for address in addresses:
        # Convert hexadecimal address string to bytes
        address_bytes = bytes.fromhex(address[2:])
        # ABI encoding for the address parameter. Address is left-padded with zeros to 32 bytes.
        encoded_address = address_bytes.rjust(32, b'\x00').hex()
        data = function_selector + encoded_address
        params = [{'to': contract_address, 'data': data}, 'latest']
        params_list.append(params)

    response_data = send_batch_json_rpc_request(endpoint, method, params_list)

    balances = {}
    for resp, address in zip(response_data, addresses):
        if 'result' in resp:
            balances[address] = int(resp['result'], 16) if resp['result'] != '0x' else 0
        else:
            print(f"Error getting balance for {address}: {resp.get('error', {}).get('message', 'Unknown error')}")
            balances[address] = None

    return balances


def get_batch_cas_balance(addresses: List[str]) -> Dict[str, int]:
    return get_batch_balance_of(w3.provider.endpoint_uri, cas_address, addresses)


def get_batch_dusd_balance_in_wei(addresses: List[str]) -> Dict[str, int]:
    return get_batch_balance_of(w3.provider.endpoint_uri, dusd_address, addresses)


def get_batch_dusd_balance(addresses: List[str]) -> Dict[str, int]:
    dusd_balances_wei = get_batch_dusd_balance_in_wei(addresses)
    dusd_balances = {address: w3.from_wei(balance_wei, 'ether') for address, balance_wei in dusd_balances_wei.items()}
    return dusd_balances


def create_signed_transaction(contract, fn_name, args, address, private_key, nonce, gas_price, gas_estimate):
    txn = {
        'to': contract.address,
        'gas': gas_estimate,
        'gasPrice': gas_price,
        'nonce': nonce,
        'data': contract.encodeABI(fn_name=fn_name, args=args)
    }
    try:
        signed_txn = w3.eth.account.sign_transaction(txn, private_key)
        return signed_txn
    except Exception as e:
        print(f"Error signing transaction for {fn_name}: {e}")
        return None
