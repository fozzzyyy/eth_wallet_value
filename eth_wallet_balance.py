import os
from uniswap import Uniswap
from web3 import Web3
import requests
import json

infura_project = "" #enter infura project id here
w3 = Web3(Web3.HTTPProvider(f"https://mainnet.infura.io/v3/{infura_project}"))
os.environ["PROVIDER"] = f"https://mainnet.infura.io/v3/{infura_project}"

address = "" # enter eth wallet address here (must be in proper format with capital letters)
private_key = None
uniswap_wrapper = Uniswap(address, private_key, version=2)

r = requests.get(f"https://api.ethplorer.io/getAddressInfo/{address}?apiKey=freekey")
x = json.loads(r.text)

tokens = x["tokens"]

token_eth_sum = 0

print(f"ETH:\t{x['ETH']['balance']}")

for token in tokens:
    if token["tokenInfo"]["name"] != "WETH":
        check_addr = Web3.toChecksumAddress(token["tokenInfo"]["address"])
        eth_equiv = uniswap_wrapper.get_token_eth_input_price(
            check_addr,
            int(token["balance"])
            )
        token_eth_sum += eth_equiv
        print(f"{token['tokenInfo']['symbol']}\t{eth_equiv / 10**18}")
    else:
        token_eth_sum += int(token['balance'])
        print(f"{token['tokenInfo']['symbol']}\t{int(token['balance'])/ 10**18}")

print(f"Total:\t{x['ETH']['balance']*factor+token_eth_sum/10**18}")
