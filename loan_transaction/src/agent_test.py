import json

import eth_abi
from eth_utils import encode_hex, function_abi_to_4byte_selector
from forta_agent import FindingSeverity, FindingType, get_json_rpc_url, create_transaction_event
from web3 import Web3

from agent import provide_handle_transaction, MARKET, NETWORK
from src.constants import LendingPoolAddressesProvider, FLASH_LOAN_FUNCTION


class Web3Mock:
    def __init__(self, prices):
        self.eth = EthMock(prices)


class EthMock:
    def __init__(self, prices):
        self.contract = ContractMock(prices)


class ContractMock:
    def __init__(self, prices):
        self.functions = FunctionsMock(prices)

    def __call__(self, *args, **kwargs):
        return self


class FunctionsMock:
    def __init__(self, prices):
        self.prices = prices
        self.asset = 'USDT'

    def getAssetsPrices(self, assets):
        self.assets = assets
        return self

    def call(self, **_):
        return [self.prices.get(asset) for asset in self.assets]


web3 = Web3(Web3.HTTPProvider(get_json_rpc_url()))
with open('./src/LendingPoolAddressesProvider.json', 'r') as abi_file:
    abi = json.load(abi_file)

LendingPoolAddressesProvider_address = LendingPoolAddressesProvider.get(MARKET + '_' + NETWORK)


class TestFlashLoanAgent:

    def test_returns_finding_with_medium_if_flash_loan_total_bigger_than_10kk(self):
        w3 = Web3Mock(prices={'0xdAC17F958D2ee523a2206206994597C13D831ec7': 218474666888275,  # USDT address and price
                              '0x0000000000000000000000000000000000000000': 813456443213438,  # Random address and price
                              '0x1111111111111111111111111111111111111111': 999999999999999,  # Random address and price
                              })

        lpap_contract = web3.eth.contract(address=Web3.toChecksumAddress(LendingPoolAddressesProvider_address), abi=abi)
        lending_pool_address = lpap_contract.functions.getLendingPool().call()  # get lending pool address
        func = function_abi_to_4byte_selector(json.loads(FLASH_LOAN_FUNCTION))

        params = eth_abi.encode_abi(["address", "address[]", "uint256[]", "uint256[]", "address", "bytes", "uint16"],
                                    ["0x3333333333333333333333333333333333333333",  # Receiver address
                                    ["0x0000000000000000000000000000000000000000",  # Token addresses
                                     "0x1111111111111111111111111111111111111111"], [2000000, 2000000],  # Amounts
                                    [1], "0x0000000000000000000000000000000000000000", bytes(0), 0])
                                     # modes, onBehalfOf, params, referralCode

        data = encode_hex(func + params)

        tx_event = create_transaction_event({
            'transaction': {
                'to': lending_pool_address,
                'data': data,
                'hash': "123"
            },
            'block': {
                'number': 0
            }
        })

        findings = provide_handle_transaction(w3)(tx_event)

        assert findings
        for finding in findings:
            assert finding.alert_id == 'AAVE-FL'
            assert finding.description == 'FlashLoan transaction value $16601068'
            assert finding.name == 'AAVE FlashLoan Transaction'
            assert finding.severity == FindingSeverity.Medium
            assert finding.type == FindingType.Info
            assert finding.metadata['transaction_amount'] == 16601068.389689447
            assert finding.metadata['market'] == MARKET
            assert finding.metadata['tx_hash'] == "123"
            assert finding.metadata['receiver'] == "0x3333333333333333333333333333333333333333"

    def test_returns_finding_with_high_if_flash_loan_total_bigger_than_30kk(self):
        w3 = Web3Mock(prices={'0xdAC17F958D2ee523a2206206994597C13D831ec7': 218474666888275,  # USDT address and price
                              '0x0000000000000000000000000000000000000000': 813456443213438,  # Random address and price
                              '0x1111111111111111111111111111111111111111': 999999999999999,  # Random address and price
                              })

        lpap_contract = web3.eth.contract(address=Web3.toChecksumAddress(LendingPoolAddressesProvider_address), abi=abi)
        lending_pool_address = lpap_contract.functions.getLendingPool().call()  # get lending pool address
        func = function_abi_to_4byte_selector(json.loads(FLASH_LOAN_FUNCTION))

        params = eth_abi.encode_abi(["address", "address[]", "uint256[]", "uint256[]", "address", "bytes", "uint16"],
                                    ["0x3333333333333333333333333333333333333333",
                                     ["0x0000000000000000000000000000000000000000",  # Token addresses
                                      "0x1111111111111111111111111111111111111111"], [4000000, 4000000],  # Amounts
                                     [1], "0x0000000000000000000000000000000000000000", bytes(0), 0])

        data = encode_hex(func + params)

        tx_event = create_transaction_event({
            'transaction': {
                'to': lending_pool_address,
                'data': data,
                'hash': "123"
            },
            'block': {
                'number': 0
            }
        })

        findings = provide_handle_transaction(w3)(tx_event)

        assert findings
        for finding in findings:
            assert finding.alert_id == 'AAVE-FL'
            assert finding.description == 'FlashLoan transaction value $33202136'
            assert finding.name == 'AAVE FlashLoan Transaction'
            assert finding.severity == FindingSeverity.High
            assert finding.type == FindingType.Info
            assert finding.metadata['transaction_amount'] == 33202136.779378895
            assert finding.metadata['market'] == MARKET
            assert finding.metadata['tx_hash'] == "123"
            assert finding.metadata['receiver'] == "0x3333333333333333333333333333333333333333"

    def test_returns_finding_with_critical_if_flash_loan_total_bigger_than_50kk(self):
        w3 = Web3Mock(prices={'0xdAC17F958D2ee523a2206206994597C13D831ec7': 218474666888275,  # USDT address and price
                              '0x0000000000000000000000000000000000000000': 813456443213438,  # Random address and price
                              '0x1111111111111111111111111111111111111111': 999999999999999,  # Random address and price
                              })

        lpap_contract = web3.eth.contract(address=Web3.toChecksumAddress(LendingPoolAddressesProvider_address), abi=abi)
        lending_pool_address = lpap_contract.functions.getLendingPool().call()  # get lending pool address
        func = function_abi_to_4byte_selector(json.loads(FLASH_LOAN_FUNCTION))

        params = eth_abi.encode_abi(["address", "address[]", "uint256[]", "uint256[]", "address", "bytes", "uint16"],
                                    ["0x3333333333333333333333333333333333333333",
                                     ["0x0000000000000000000000000000000000000000",  # Token addresses
                                      "0x1111111111111111111111111111111111111111"], [8000000, 8000000],  # Amounts
                                     [1], "0x0000000000000000000000000000000000000000", bytes(0), 0])

        data = encode_hex(func + params)

        tx_event = create_transaction_event({
            'transaction': {
                'to': lending_pool_address,
                'data': data,
                'hash': "123"
            },
            'block': {
                'number': 0
            }
        })

        findings = provide_handle_transaction(w3)(tx_event)

        assert findings
        for finding in findings:
            assert finding.alert_id == 'AAVE-FL'
            assert finding.description == 'FlashLoan transaction value $66404273'
            assert finding.name == 'AAVE FlashLoan Transaction'
            assert finding.severity == FindingSeverity.Critical
            assert finding.type == FindingType.Info
            assert finding.metadata['transaction_amount'] == 66404273.55875779
            assert finding.metadata['market'] == MARKET
            assert finding.metadata['tx_hash'] == "123"
            assert finding.metadata['receiver'] == "0x3333333333333333333333333333333333333333"

    def test_returns_zero_finding_if_flash_loan_total_below_10kk(self):
        w3 = Web3Mock(prices={'0xdAC17F958D2ee523a2206206994597C13D831ec7': 218474666888275,  # USDT address and price
                              '0x0000000000000000000000000000000000000000': 813456443213438,  # Random address and price
                              '0x1111111111111111111111111111111111111111': 999999999999999,  # Random address and price
                              })

        lpap_contract = web3.eth.contract(address=Web3.toChecksumAddress(LendingPoolAddressesProvider_address), abi=abi)
        lending_pool_address = lpap_contract.functions.getLendingPool().call()  # get lending pool address
        func = function_abi_to_4byte_selector(json.loads(FLASH_LOAN_FUNCTION))

        params = eth_abi.encode_abi(["address", "address[]", "uint256[]", "uint256[]", "address", "bytes", "uint16"],
                                    ["0x3333333333333333333333333333333333333333",
                                     ["0x0000000000000000000000000000000000000000",  # Token addresses
                                      "0x1111111111111111111111111111111111111111"], [1000000, 1000000],  # Amounts
                                     [1], "0x0000000000000000000000000000000000000000", bytes(0), 0])

        data = encode_hex(func + params)

        tx_event = create_transaction_event({
            'transaction': {
                'to': lending_pool_address,
                'data': data,
                'hash': "123"
            },
            'block': {
                'number': 0
            }
        })

        findings = provide_handle_transaction(w3)(tx_event)

        assert not findings

    def test_returns_zero_finding_if_not_flash_loan(self):
        w3 = Web3Mock(prices={'0xdAC17F958D2ee523a2206206994597C13D831ec7': 218474666888275,  # USDT address and price
                              '0x0000000000000000000000000000000000000000': 813456443213438,  # Random address and price
                              '0x1111111111111111111111111111111111111111': 999999999999999,  # Random address and price
                              })

        lpap_contract = web3.eth.contract(address=Web3.toChecksumAddress(LendingPoolAddressesProvider_address), abi=abi)
        lending_pool_address = lpap_contract.functions.getLendingPool().call()  # get lending pool address

        tx_event = create_transaction_event({
            'transaction': {
                'to': lending_pool_address,
                'data': "",
                'hash': "123"
            },
            'block': {
                'number': 0
            }
        })

        findings = provide_handle_transaction(w3)(tx_event)

        assert not findings

    def test_returns_zero_finding_if_address_is_wrong(self):
        w3 = Web3Mock(prices={'0xdAC17F958D2ee523a2206206994597C13D831ec7': 218474666888275,  # USDT address and price
                              '0x0000000000000000000000000000000000000000': 813456443213438,  # Random address and price
                              '0x1111111111111111111111111111111111111111': 999999999999999,  # Random address and price
                              })

        func = function_abi_to_4byte_selector(json.loads(FLASH_LOAN_FUNCTION))
        params = eth_abi.encode_abi(["address", "address[]", "uint256[]", "uint256[]", "address", "bytes", "uint16"],
                                    ["0x3333333333333333333333333333333333333333",
                                     ["0x0000000000000000000000000000000000000000",  # Token addresses
                                      "0x1111111111111111111111111111111111111111"], [1000000, 1000000],  # Amounts
                                     [1], "0x0000000000000000000000000000000000000000", bytes(0), 0])

        data = encode_hex(func + params)

        tx_event = create_transaction_event({
            'transaction': {
                'to': "0x3333333333333333333333333333333333333333",
                'data': data,
                'hash': "123"
            },
            'block': {
                'number': 0
            }
        })

        findings = provide_handle_transaction(w3)(tx_event)

        assert not findings
