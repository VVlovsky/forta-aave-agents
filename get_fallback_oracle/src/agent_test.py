import json
from eth_utils import encode_hex, function_abi_to_4byte_selector
from forta_agent import create_transaction_event, get_json_rpc_url
from web3 import Web3
from agent import handle_transaction
from src.constants import LendingPoolAddressesProvider, GET_FALLBACK_ORACLE

MARKET = 'MAIN'  # available options: MAIN, AMM
NETWORK = 'MAINNET'  # Specify your network here
LendingPoolAddressesProvider_address = LendingPoolAddressesProvider.get(MARKET + '_' + NETWORK)

web3 = Web3(Web3.HTTPProvider(get_json_rpc_url()))
with open('./src/LendingPoolAddressesProvider.json', 'r') as abi_file:
    abi = json.load(abi_file)


class TestFallbackOracleAgent:
    def test_returns_finding_if_function_is_in_data_and_price_oracle_address_is_correct(self):
        contract = web3.eth.contract(address=Web3.toChecksumAddress(LendingPoolAddressesProvider_address), abi=abi)
        price_oracle_address = contract.functions.getPriceOracle().call()
        data = encode_hex(function_abi_to_4byte_selector(json.loads(GET_FALLBACK_ORACLE)))

        tx_event = create_transaction_event({
            'transaction': {
                'to': price_oracle_address,
                'data': data}
        })
        findings = handle_transaction(tx_event)
        assert len(findings) == 1

    def test_returns_zero_findings_if_address_is_incorrect(self):
        price_oracle_address = "0xTEST"
        data = encode_hex(function_abi_to_4byte_selector(json.loads(GET_FALLBACK_ORACLE)))
        tx_event = create_transaction_event({
            'transaction': {
                'to': price_oracle_address,
                'data': data}
        })
        findings = handle_transaction(tx_event)
        assert len(findings) == 0

    def test_returns_zero_findings_if_data_dont_include_oracle(self):
        contract = web3.eth.contract(address=Web3.toChecksumAddress(LendingPoolAddressesProvider_address), abi=abi)
        price_oracle_address = contract.functions.getPriceOracle().call()
        data = "0x0000000000"

        tx_event = create_transaction_event({
            'transaction': {
                'to': price_oracle_address,
                'data': data}
        })
        findings = handle_transaction(tx_event)
        assert len(findings) == 0
