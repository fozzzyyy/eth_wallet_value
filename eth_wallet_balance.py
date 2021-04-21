import os
from uniswap import Uniswap
from web3 import Web3
import requests
import json
from datetime import datetime

address = "" # eth wallet address
private_key = None

bscscan_api_key = "" # get api key from bscscan
bsc_wallet = "" # bsc wallet address

infura_project = "2feeeb516ef94c818346cb441c42ed5f"
w3 = Web3(Web3.HTTPProvider(f"https://mainnet.infura.io/v3/{infura_project}"))
os.environ["PROVIDER"] = f"https://mainnet.infura.io/v3/{infura_project}"

cmc_url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
cmc_key = "" # coinmarketcap api key
cmc_eth_id = 1027
cmc_bnb_id = 1839
cmc_fiat_id = 2791 # example value for GBP
fiat_symbol = "£"

cmc_request = requests.get(f"{cmc_url}?id={cmc_eth_id},{cmc_bnb_id}&convert_id={cmc_fiat_id}",
                           headers={"X-CMC_PRO_API_KEY":f"{cmc_key}"})
cmc_json = json.loads(cmc_request.text)
eth_to_fiat = cmc_json["data"][f"{cmc_eth_id}"]["quote"][f"{cmc_fiat_id}"]["price"]
bnb_to_fiat = cmc_json["data"][f"{cmc_bnb_id}"]["quote"][f"{cmc_fiat_id}"]["price"]

uniswap_wrapper = Uniswap(address, private_key, version=2)

r = requests.get(f"https://api.ethplorer.io/getAddressInfo/{address}?apiKey=freekey")
x = json.loads(r.text)

print(datetime.now())

tokens = x["tokens"]

token_eth_sum = 0

print(f"ETH\t{x['ETH']['balance']*factor:.18f}")

for token in tokens:
    if token["tokenInfo"]["name"] != "WETH":
        check_addr = Web3.toChecksumAddress(token["tokenInfo"]["address"])
        eth_equiv = uniswap_wrapper.get_token_eth_input_price(
            check_addr,
            int(token["balance"])
            )*factor
        token_eth_sum += eth_equiv
        print(f"{token['tokenInfo']['symbol']}\t{eth_equiv / 10**18:.18f}")
    else:
        token_eth_sum += int(token['balance'])*factor
        print(f"{token['tokenInfo']['symbol']}\t{int(token['balance'])/ 10**18:.18f}")

eth_total = x['ETH']['balance']*factor+token_eth_sum/10**18

print(f"Total:\t{eth_total:.18f}")
print(f"{fiat_symbol}{eth_total*eth_to_fiat:.2f}")
print()


rb = requests.get(f"https://api.bscscan.com/api?module=account&action=balance&address={bsc_wallet}&tag=latest&apikey={bscscan_api_key}")
j_bnb_balance = json.loads(rb.text)
bnb_balance = int(j_bnb_balance["result"])
print(f"BNB\t{bnb_balance/10**18}")
bnb_sum = bnb_balance

bsc_prices = json.loads(requests.get("https://api.pancakeswap.info/api/tokens").text)["data"]


# temp, find some way of getting tokens automatically
bsc_tokens = {"SFMN":"0x8076C74C5e3F5852037F31Ff0093Eeb8c8ADd8D3",
              "Hungry":"0x812Ff2420EC87eB40Da80a596f14756ACf98Dacc"}
decimals = {"SFMN":9,
            "Hungry":8}

for t in bsc_tokens:
    bscscan_request = requests.get(f"https://api.bscscan.com/api?module=account&action=tokenbalance&contractaddress={bsc_tokens[t]}&address={bsc_wallet}&tag=latest&apikey={bscscan_api_key}")
    jab = json.loads(bscscan_request.text)
    token_balance = int(jab["result"])
    dec = decimals[t]
    token_bnb_equiv = token_balance * float(bsc_prices[bsc_tokens[t]]["price_BNB"])*10**(18-dec)
    bnb_sum += token_bnb_equiv
    print(f"{t}\t{token_bnb_equiv/10**18:.18f}")
    
print(f"Total:\t{bnb_sum/10**18:.18f}")
print(f"{fiat_symbol}{bnb_sum*bnb_to_fiat/10**18:.2f}")





