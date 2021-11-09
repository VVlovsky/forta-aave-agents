import json
import re
import time

from forta_agent import FindingSeverity, FindingType, create_block_event, get_json_rpc_url
from web3 import Web3

from src.agent import provide_handle_block, MARKET, LendingPoolAddressesProvider_address, get_fallback_oracle, \
    reset_time

with open('./src/LendingPoolAddressesProvider.json', 'r') as abi_file:
    abi = json.load(abi_file)  # get LendingPoolAddressesProvider ABI


class Web3Mock:
    def __init__(self, price_oracle_address, fallback_oracle_address, price_oracle_price, fallback_oracle_price):
        self.eth = EthMock(price_oracle_address, fallback_oracle_address, price_oracle_price, fallback_oracle_price)


class EthMock:
    def __init__(self, price_oracle_address, fallback_oracle_address, price_oracle_price, fallback_oracle_price):
        self.contract = ContractMock(price_oracle_address, fallback_oracle_address, price_oracle_price,
                                     fallback_oracle_price, "")


class ContractMock:
    def __init__(self, price_oracle_address, fallback_oracle_address, price_oracle_price, fallback_oracle_price,
                 address):
        self.price_oracle_price = price_oracle_price
        self.fallback_oracle_price = fallback_oracle_price
        self.price_oracle_address = price_oracle_address
        self.fallback_oracle_address = fallback_oracle_address
        self.contract = address
        self.functions = FunctionsMock(price_oracle_address, fallback_oracle_address, price_oracle_price,
                                       fallback_oracle_price, self)

    def __call__(self, address, *args, **kwargs):
        self.contract = address
        return ContractMock(self.price_oracle_address, self.fallback_oracle_address, self.price_oracle_price,
                            self.fallback_oracle_price, self.contract)


class FunctionsMock:
    def __init__(self, price_oracle_address, fallback_oracle_address, price_oracle_price, fallback_oracle_price,
                 contract):
        self.price_oracle_price = price_oracle_price
        self.fallback_oracle_price = fallback_oracle_price
        self.price_oracle_address = price_oracle_address
        self.fallback_oracle_address = fallback_oracle_address
        self.contract = contract
        self.return_value = ""

    def getAssetsPrices(self, **_):
        if self.contract.contract and self.contract.contract == self.fallback_oracle_address:
            self.return_value = [self.fallback_oracle_price]
        else:
            self.return_value = [self.price_oracle_price]
        return self

    def getAssetPrice(self, **_):
        if self.contract.contract and self.contract.contract == self.fallback_oracle_address:
            self.return_value = self.fallback_oracle_price
        else:
            self.return_value = self.price_oracle_price
        return self

    def getFallbackOracle(self):
        self.return_value = self.fallback_oracle_address
        return self

    def getPriceOracle(self):
        self.return_value = self.price_oracle_address
        return self

    def call(self, **_):
        return self.return_value


class TestExchangeRateAgent:
    block_event = create_block_event({
        'block': {
            'number': 0
        }
    })

    web3 = Web3(Web3.HTTPProvider(get_json_rpc_url()))
    lpap_contract = web3.eth.contract(address=Web3.toChecksumAddress(LendingPoolAddressesProvider_address), abi=abi)
    price_oracle_address = lpap_contract.functions.getPriceOracle().call()
    price_oracle_contract = web3.eth.contract(address=Web3.toChecksumAddress(price_oracle_address),
                                              abi=[get_fallback_oracle])
    fallback_oracle_address = price_oracle_contract.functions.getFallbackOracle().call()

    def test_returns_zero_findings_if_prices_are_similar(self):
        w3 = Web3Mock(self.price_oracle_address, self.fallback_oracle_address, 100, 95)
        findings = provide_handle_block(w3)(self.block_event)
        assert len(findings) == 0

    def test_returns_zero_returns_findings_if_one_price_is_zero(self):
        w3 = Web3Mock(self.price_oracle_address, self.fallback_oracle_address, 100, 0)
        findings = provide_handle_block(w3)(self.block_event)
        assert len(findings) == 0

    def test_returns_zero_findings_if_time_window_dont_passed(self):
        reset_time()
        w3 = Web3Mock(self.price_oracle_address, self.fallback_oracle_address, 100, 50)
        provide_handle_block(w3)(self.block_event)
        time.sleep(1)
        findings = provide_handle_block(w3)(self.block_event)
        assert len(findings) == 0

    def test_returns_finding_medium_if_price_changed_more_than_th(self):
        reset_time()
        w3 = Web3Mock(self.price_oracle_address, self.fallback_oracle_address, 100, 85)
        avg = (100 + 85) / 2
        sigma = abs(100 - avg) + abs(85 - avg)  # s = √(Σ(X - x̄)² / n - 1)
        relative_standard_deviation = 100 * sigma / avg  # RSD = 100 * s / x̄
        findings = provide_handle_block(w3)(self.block_event)

        assert findings
        assert findings[0].alert_id == 'AAVE-OPD'
        assert re.match(
            fr'FallbackOracle price for [a-zA-Z]+ deviates from PriceOracle by {int(relative_standard_deviation)}%',
            findings[0].description)
        assert findings[0].metadata['price_oracle_price'] == 100
        assert findings[0].metadata['fallback_oracle_price'] == 85
        assert findings[0].metadata['actual_price_oracle_address'] == '0xA50ba011c48153De246E5192C8f9258A2ba79Ca9'
        assert findings[0].metadata['actual_fallback_oracle_address'] == '0x5B09E578cfEAa23F1b11127A658855434e4F3e09'
        assert findings[0].metadata['block_number'] == 0
        assert findings[0].metadata['relative_standard_deviation'] == relative_standard_deviation
        assert findings[0].metadata['market'] == MARKET
        assert findings[0].type == FindingType.Suspicious
        assert findings[0].severity == FindingSeverity.Medium

    def test_returns_finding_high_if_price_changed_more_than_high_th(self):
        reset_time()
        w3 = Web3Mock(self.price_oracle_address, self.fallback_oracle_address, 100, 75)
        avg = (100 + 75) / 2
        sigma = abs(100 - avg) + abs(75 - avg)  # s = √(Σ(X - x̄)² / n - 1)
        relative_standard_deviation = 100 * sigma / avg  # RSD = 100 * s / x̄
        findings = provide_handle_block(w3)(self.block_event)

        assert findings
        assert findings[0].alert_id == 'AAVE-OPD'
        assert re.match(
            fr'FallbackOracle price for [a-zA-Z]+ deviates from PriceOracle by {int(relative_standard_deviation)}%',
            findings[0].description)
        assert findings[0].metadata['price_oracle_price'] == 100
        assert findings[0].metadata['fallback_oracle_price'] == 75
        assert findings[0].metadata['actual_price_oracle_address'] == '0xA50ba011c48153De246E5192C8f9258A2ba79Ca9'
        assert findings[0].metadata['actual_fallback_oracle_address'] == '0x5B09E578cfEAa23F1b11127A658855434e4F3e09'
        assert findings[0].metadata['block_number'] == 0
        assert findings[0].metadata['relative_standard_deviation'] == relative_standard_deviation
        assert findings[0].metadata['market'] == MARKET
        assert findings[0].type == FindingType.Suspicious
        assert findings[0].severity == FindingSeverity.High

    def test_returns_finding_critical_if_price_changed_more_than_critical_th(self):
        reset_time()
        w3 = Web3Mock(self.price_oracle_address, self.fallback_oracle_address, 100, 60)
        avg = (100 + 60) / 2
        sigma = abs(100 - avg) + abs(60 - avg)  # s = √(Σ(X - x̄)² / n - 1)
        relative_standard_deviation = 100 * sigma / avg  # RSD = 100 * s / x̄
        findings = provide_handle_block(w3)(self.block_event)

        assert findings
        assert findings[0].alert_id == 'AAVE-OPD'
        assert re.match(
            fr'FallbackOracle price for [a-zA-Z]+ deviates from PriceOracle by {int(relative_standard_deviation)}%',
            findings[0].description)
        assert findings[0].metadata['price_oracle_price'] == 100
        assert findings[0].metadata['fallback_oracle_price'] == 60
        assert findings[0].metadata['actual_price_oracle_address'] == '0xA50ba011c48153De246E5192C8f9258A2ba79Ca9'
        assert findings[0].metadata['actual_fallback_oracle_address'] == '0x5B09E578cfEAa23F1b11127A658855434e4F3e09'
        assert findings[0].metadata['block_number'] == 0
        assert findings[0].metadata['relative_standard_deviation'] == relative_standard_deviation
        assert findings[0].metadata['market'] == MARKET
        assert findings[0].type == FindingType.Suspicious
        assert findings[0].severity == FindingSeverity.Critical
