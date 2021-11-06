from forta_agent import Finding, FindingType, FindingSeverity, get_json_rpc_url
from src.constants import LendingPoolAddressesProvider, GET_ASSETS_PRICE_ABI
import json
from web3 import Web3

web3 = Web3(Web3.HTTPProvider(get_json_rpc_url()))
get_assets_price_abi = json.loads(GET_ASSETS_PRICE_ABI)

TOKEN_1 = 'USDC'  # Specify first token name
TOKEN_2 = 'DAI'  # Specify second token name

MARKET = 'AMM'  # available options: MAIN, AMM
NETWORK = 'MAINNET'  # There is only mainnet available at this moment
LendingPoolAddressesProvider_address = LendingPoolAddressesProvider.get(MARKET + '_' + NETWORK)

exchange_rate_history = [0]
with open('./src/tokens.json', 'r') as tokens_file:
    tokens = json.load(tokens_file)
with open('./src/LendingPoolAddressesProvider.json', 'r') as abi_file:
    abi = json.load(abi_file)

# Always get the latest price oracle address by calling getPriceOracle() on the LendingPoolAddressesProvider contract.
# © https://docs.aave.com/developers/the-core-protocol/price-oracle
lpap_contract = web3.eth.contract(address=Web3.toChecksumAddress(LendingPoolAddressesProvider_address), abi=abi)
price_oracle_address = lpap_contract.functions.getPriceOracle().call()

json_market = 'proto' if MARKET == 'MAIN' else 'amm'
token_first = next((x for x in tokens[json_market] if x['symbol'] == TOKEN_1), None)
token_second = next((x for x in tokens[json_market] if x['symbol'] == TOKEN_2), None)
token_first_address = token_first['address']
token_second_address = token_second['address']


def get_severity(dif):
    if dif < 0.02:
        return FindingSeverity.Medium
    elif 0.02 <= dif < 0.1:
        return FindingSeverity.High
    elif dif >= 0.1:
        return FindingSeverity.Critical
    else:
        return FindingSeverity.Info


def provide_handle_block(w3):
    def handle_block(block_event):
        findings = []
        price_oracle_contract = w3.eth.contract(address=Web3.toChecksumAddress(price_oracle_address),
                                                abi=[get_assets_price_abi])

        price1, price2 = price_oracle_contract.functions.getAssetsPrices(
            assets=[token_first_address, token_second_address]).call(
            block_identifier=int(block_event.block_number))

        exchange_rate = price1 / price2

        if exchange_rate < exchange_rate_history[-1]:
            dif = exchange_rate_history[-1] - exchange_rate

            findings.append(Finding({
                'name': 'Aave Exchange Rate Down',
                'description': f'{TOKEN_1}/{TOKEN_2} Exchange Rate Goes Down',
                'alert_id': f'AAVE-EXR',
                'type': FindingType.Info,
                'severity': get_severity(dif),
                'metadata': {
                    'difference': dif,
                    '1st_token': TOKEN_1,
                    '2nd_token': TOKEN_2,
                    'market': MARKET
                }
            }))

        exchange_rate_history.append(exchange_rate)
        return findings

    return handle_block


real_handle_block = provide_handle_block(web3)


def handle_block(block_event):
    return real_handle_block(block_event)
