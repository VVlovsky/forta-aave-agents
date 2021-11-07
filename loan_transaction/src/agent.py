import json

import forta_agent
from forta_agent import Finding, FindingType, FindingSeverity, Web3, get_json_rpc_url
from src.constants import LendingPoolAddressesProvider, GET_ASSETS_PRICE_ABI, FLASH_LOAN_FUNCTION, USD_TH, \
    CRITICAL_USD_TH, \
    HIGH_USD_TH

MARKET = 'MAIN'  # available options: MAIN, AMM
NETWORK = 'MAINNET'  # There is only mainnet available at this moment
LendingPoolAddressesProvider_address = LendingPoolAddressesProvider.get(MARKET + '_' + NETWORK)

web3 = Web3(Web3.HTTPProvider(get_json_rpc_url()))
get_assets_price_abi = json.loads(GET_ASSETS_PRICE_ABI)
with open('./src/LendingPoolAddressesProvider.json', 'r') as abi_file:
    abi = json.load(abi_file)
with open('./src/tokens.json', 'r') as tokens_file:
    tokens = json.load(tokens_file)

# Always get the latest price oracle address by calling getPriceOracle() on the LendingPoolAddressesProvider contract.
# © https://docs.aave.com/developers/the-core-protocol/price-oracle
lpap_contract = web3.eth.contract(address=Web3.toChecksumAddress(LendingPoolAddressesProvider_address), abi=abi)
price_oracle_address = lpap_contract.functions.getPriceOracle().call()  # get price oracle address
lending_pool_address = lpap_contract.functions.getLendingPool().call()  # get lending pool address

json_market = 'proto' if MARKET == 'MAIN' else 'amm'
USDT_address = next((x['address'] for x in tokens[json_market] if x['aTokenSymbol'] == 'aUSDT'), None)


def provide_handle_transaction(w3):
    def handle_transaction(transaction_event: forta_agent.transaction_event.TransactionEvent):
        findings = []

        # create price oracle contract
        price_oracle_contract = w3.eth.contract(address=Web3.toChecksumAddress(price_oracle_address),
                                                abi=[get_assets_price_abi])
        # filter transaction by flashLoan() with lending pool address
        results = transaction_event.filter_function(FLASH_LOAN_FUNCTION, lending_pool_address)
        for result in results:
            args = result[1]
            assets = args.get('assets', [])  # get the asset's addresses from in the loan
            amounts = args.get('amounts', [])  # get the asset's amounts from in the loan

            # total amount in USD = (sum of (each asset price in wETH * amount of each asset)) / USDT price in wETH
            total_usd = sum([price_oracle_contract.functions.getAssetsPrices(assets=[asset]).call(
                        block_identifier=int(transaction_event.block_number))[0] * amounts[i] for i, asset in
                        enumerate(assets)]) / price_oracle_contract.functions.getAssetsPrices([USDT_address]).call()[0]

            print(total_usd)
            if total_usd >= USD_TH:
                findings.append(Finding({
                    'name': 'AAVE FlashLoan Transaction',
                    'description': f'FlashLoan transaction value ${int(total_usd)}',
                    'alert_id': 'AAVE-FL',
                    'type': FindingType.Info,
                    'severity': get_severity(total_usd),
                    'metadata': {
                        'transaction_amount': total_usd,
                        'market': MARKET,
                        'tx_hash': transaction_event.transaction.hash,
                        'receiver': args.get('receiverAddress', 'UNKNOWN RECEIVER')
                    }
                }))

        return findings

    return handle_transaction


def get_severity(amount):
    if amount < HIGH_USD_TH:
        return FindingSeverity.Medium
    elif amount < CRITICAL_USD_TH:
        return FindingSeverity.High
    else:
        return FindingSeverity.Critical


real_handle_transaction = provide_handle_transaction(web3)


def handle_transaction(transaction_event):
    return real_handle_transaction(transaction_event)
