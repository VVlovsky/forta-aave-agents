import json
import forta_agent
from web3 import Web3
from src.constants import GET_FALLBACK_ORACLE, LendingPoolAddressesProvider
from forta_agent import Finding, FindingType, FindingSeverity, get_json_rpc_url

MARKET = 'MAIN'  # available options: MAIN, AMM
NETWORK = 'MAINNET'  # Specify your network here
LendingPoolAddressesProvider_address = LendingPoolAddressesProvider.get(MARKET + '_' + NETWORK)

web3 = Web3(Web3.HTTPProvider(get_json_rpc_url()))
with open('./src/LendingPoolAddressesProvider.json', 'r') as abi_file:
    abi = json.load(abi_file)


def handle_transaction(transaction_event: forta_agent.transaction_event.TransactionEvent):
    findings = []

    # get LendingPoolAddressesProvider contract address in the specified network
    contract = web3.eth.contract(address=Web3.toChecksumAddress(LendingPoolAddressesProvider_address), abi=abi)
    # get actual PriceOracle contract address from the LendingPoolAddressesProvider using getPriceOracle ABI
    price_oracle_address = contract.functions.getPriceOracle().call()
    # filter transaction events where GetFallbackOracle was called with PriceOracle address
    oracle_calls = transaction_event.filter_function(GET_FALLBACK_ORACLE, price_oracle_address)

    if oracle_calls:
        findings.append(Finding({
            'name': 'GetFallbackOracle() Function',
            'description': f'getFallbackOracle() function was called from {price_oracle_address}',
            'alert_id': "AAVE-SFO",
            'type': FindingType.Suspicious,
            'severity': FindingSeverity.Medium,
            'metadata': {
                'tx_hash': transaction_event.hash,
                'price_oracle': price_oracle_address
            }
        }))

    return findings
