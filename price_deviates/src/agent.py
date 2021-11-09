import json
from forta_agent import Finding, FindingType, FindingSeverity, get_json_rpc_url
from web3 import Web3

from src.constants import LendingPoolAddressesProvider, GET_ASSETS_PRICE_ABI, GET_FALLBACK_ORACLE
import time

# --------------------------SETUP SECTION-------------------------- #
SLEEP_SECONDS = 1200    # 20 min - check interval
PRICE_TH = 10           # 10% - minimal threshold
HIGH_PRICE_TH = 20      # 20% - threshold for the high severity
CRITICAL_PRICE_TH = 30  # 30% - threshold for the critical severity

MARKET = 'MAIN'      # available options: MAIN, AMM
NETWORK = 'MAINNET'  # There is only mainnet available at this moment
# ------------------------END SETUP SECTION------------------------ #

LendingPoolAddressesProvider_address = LendingPoolAddressesProvider.get(MARKET + '_' + NETWORK)

with open('./src/LendingPoolAddressesProvider.json', 'r') as abi_file:
    abi = json.load(abi_file)  # get LendingPoolAddressesProvider ABI

with open('./src/FallbackOracleABI.json', 'r') as abi_file:
    fbo_abi = json.load(abi_file)  # get FallbackOracle ABI

with open('./src/tokens.json', 'r') as tokens_file:
    tokens = json.load(tokens_file)  # get tokens addresses and symbols

web3 = Web3(Web3.HTTPProvider(get_json_rpc_url()))
lpap_contract = web3.eth.contract(address=Web3.toChecksumAddress(LendingPoolAddressesProvider_address), abi=abi)

get_assets_price_abi = json.loads(GET_ASSETS_PRICE_ABI)
get_fallback_oracle = json.loads(GET_FALLBACK_ORACLE)

last_check_unix_time = 0
json_market = 'proto' if MARKET == 'MAIN' else 'amm'


def provide_handle_block(w3):
    def handle_block(block_event):
        global last_check_unix_time
        findings = []

        if time.time() <= last_check_unix_time + SLEEP_SECONDS:
            return findings

        # Always get the latest price oracle address by calling getPriceOracle() on the LendingPoolAddressesProvider.
        # © https://docs.aave.com/developers/the-core-protocol/price-oracle
        price_oracle_address = lpap_contract.functions.getPriceOracle().call()
        price_oracle_contract = w3.eth.contract(address=Web3.toChecksumAddress(price_oracle_address),
                                                abi=[get_assets_price_abi, get_fallback_oracle])

        # Always get the latest fallback oracle address by calling getFallbackOracle() on the PriceOracle.
        fallback_oracle_address = price_oracle_contract.functions.getFallbackOracle().call()
        fallback_oracle_contract = w3.eth.contract(address=Web3.toChecksumAddress(fallback_oracle_address),
                                                   abi=fbo_abi)

        for token in tokens[json_market]:
            price_oracle_price = price_oracle_contract.functions.getAssetsPrices(assets=[token['address']]).call(
                block_identifier=int(block_event.block_number))[0]  # get price from the price_oracle_contract
            fallback_oracle_price = fallback_oracle_contract.functions.getAssetPrice(asset=token['address']).call(
                block_identifier=int(block_event.block_number))  # get price from the fallback_oracle_contract

            if price_oracle_price == 0 or fallback_oracle_price == 0:  # fallback_oracle does not work for some tokens
                continue

            # s = √(Σ(X - x̄)² / n - 1)
            # RSD = 100 * s / x̄
            avg = (price_oracle_price + fallback_oracle_price) / 2
            sigma = abs(price_oracle_price - avg) + abs(fallback_oracle_price - avg)
            relative_standard_deviation = 100 * sigma / avg

            if sigma > PRICE_TH:
                findings.append(Finding({
                    'name': 'Aave Oracles Price Deviation',
                    'description': f'FallbackOracle price for {token.get("symbol")} '
                                   f'deviates from PriceOracle by {int(relative_standard_deviation)}%',
                    'alert_id': 'AAVE-OPD',
                    'type': FindingType.Suspicious,
                    'severity': get_severity(relative_standard_deviation),
                    'metadata': {
                        'price_oracle_price': price_oracle_price,
                        'fallback_oracle_price': fallback_oracle_price,
                        'relative_standard_deviation': relative_standard_deviation,
                        'token_symbol': token.get("symbol"),
                        'actual_price_oracle_address': price_oracle_address,
                        'actual_fallback_oracle_address': fallback_oracle_address,
                        'block_number': block_event.block_number,
                        'market': MARKET
                    }
                }))

        last_check_unix_time = time.time()
        return findings

    return handle_block


def get_severity(relative_standard_deviation):
    if relative_standard_deviation < HIGH_PRICE_TH:
        return FindingSeverity.Medium
    elif relative_standard_deviation < CRITICAL_PRICE_TH:
        return FindingSeverity.High
    else:
        return FindingSeverity.Critical


def reset_time():
    global last_check_unix_time
    last_check_unix_time = 0


real_handle_block = provide_handle_block(web3)


def handle_block(block_event):
    return real_handle_block(block_event)
