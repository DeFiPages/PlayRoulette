# Play Roulette

This project serves as a test for the decentralized crypto casino located at [Decentralized Crypto Casino](https://github.com/DeFiPages/Decentralized-Crypto-Casino).

## Prerequisites

Before you begin, ensure you've completed the following steps:

### 1. Create Ethereum Accounts

- Modify the `num_accounts` variable in `create_eth_addresses.py`.
- Execute `create_eth_addresses.py`.
- After execution, the addresses and private keys will be saved in `.ethereum_accounts.txt`.

### 2. Transfer DFI and DUSD to the Ethereum Addresses

- Prepare a file named `.dvmaddress.txt` containing the dvm address. Ensure it has `num_accounts*2` DFI tokens and `num_accounts*10` DUSD.
  
  _Note: If the script isn't run at the Changi node, copy the `.cookie` file from the node (located at `~/.defi/changi/.cookie`) to the project root folder._

- Verify your connection to the node at `url="127.0.0.1"`, `port=20554`. This might require SSH port forwarding.
  
- Execute `transfer_dfi_dusd.py`.
  
  This script checks the token balance at the Ethereum address. If insufficient, it initiates a transfer and prints the transaction ID. Ensure the transactions are confirmed before re-running the script.

### 3. Purchase CAS Token with DUSD

- Execute `buy_cas.py` to purchase 1000 CAS Tokens using 10 DUSD.

## Periodic Test

For regular testing:

- Run `play_roulette.py` periodically. This will simulate a roulette game, placing a bet on BLACK using 1 CAS for all addresses.


## Note

The EVM RPC URL is set in `libs/my_eth_utils.py` to the local port: `http://127.0.0.1:20551`.

Alternatives include public URLs like `https://testnet-dmc.mydefichain.com:20551`
But to many requests can results to the error:
`HTTPError: 429 Client Error: Too Many Requests for url: https://testnet-dmc.mydefichain.com:20551/`

## Run with crontab at the changi node

Clone source and install requirements

```{python}
git clone https://github.com/DeFiPages/PlayRoulette.git
cd PlayRoulette
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt

```
Execute tasks in [Prerequisites](#prerequisites)

All eth accounts must have 2 DFI for gas and 1000 CAS Token to play.

In crontab -e append to run hourly:

```sh
42 * * * * /bin/bash -c 'date;cd ~/PlayRoulette && source venv/bin/activate && python3 play_roulette.py'  >> ~/play_roulette.log 2>&1
```

Check that the full path `~/PlayRoulette/venv/bin/activate` is correct.


