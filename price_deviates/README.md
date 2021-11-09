# Aave Price Deviates Agent

## Description

This agent provides alert if getFallbackOracle() returns a price that deviates more than 10% from last price delivered
by getAssetPrice()

## Equation

Get the standard deviation:
`s = √(Σ(X - x̄)² / n - 1)`

Get the relative standard deviation:
`RSD = 100 * s / x̄`

## Setup

You can specify your parameters in the `agent.py`

```python
# --------------------------SETUP SECTION-------------------------- #
SLEEP_SECONDS = 1200  # 20 min - check interval
PRICE_TH = 10  # 10% - minimal threshold
HIGH_PRICE_TH = 20  # 20% - threshold for the high severity
CRITICAL_PRICE_TH = 30  # 30% - threshold for the critical severity

MARKET = 'MAIN'  # available options: MAIN, AMM
NETWORK = 'MAINNET'  # There is only mainnet available at this moment
# ------------------------END SETUP SECTION------------------------ #
```

## Supported Chains

- Ethereum

## Supported Markets

- `Main Market` - Main Aave Market
- `AMM Market` - The AMM market supports LP tokens from certain Automated Market Maker (AMM) decentralised exchanges,
  such as Uniswap v2 and Balancer.

## Alerts

Describe each of the type of alerts fired by this agent

- AAVE-FL
    - Fired when relative standard deviation ≥ 10%
    - Severity depends on the relative standard deviation:
        - `FindingSeverity.Medium` if 10% ≤ RSD < 20%
        - `FindingSeverity.High` if 20% ≤ RSD < 30%
        - `FindingSeverity.Critical` if 30% ≤ RSD
    - Type is always set to `"Suspicious"`
    - Metadata:
        - `price_oracle_price` - price which was returned by the price oracle
        - `fallback_oracle_price` - price which was returned by the fallback oracle
        - `relative_standard_deviation` - counted RSD
        - `token_symbol` - token for which price deviates
        - `actual_price_oracle_address` - price oracle address
        - `actual_fallback_oracle_address` - fallback oracle address
        - `block_number` - block number
        - `market` - specified market

## Test Code

The agent behaviour can be verified using `npm test`

To test smart contracts behavior it is needed to create Web3 Mock and pass the mock as the argument into
the `provide_handle_block()`.
```python
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
```


## Test Data

```json
20 findings for block 0x82d4a23b253b0834cc0e5e143ecb5950a9742c1e92b5fc4f464b01cbeea6ab78 {
  "name": "Aave Oracles Price Deviation",
  "description": "FallbackOracle price for USDT deviates from PriceOracle by 90%",
  "alertId": "AAVE-OPD",
  "protocol": "ethereum",
  "severity": "Critical",
  "type": "Suspicious",
  "metadata": {
    "price_oracle_price": 209687125839534,
    "fallback_oracle_price": 556410000000000,
    "relative_standard_deviation": 90.51668841088701,
    "token_symbol": "USDT",
    "actual_price_oracle_address": "0xA50ba011c48153De246E5192C8f9258A2ba79Ca9",
    "actual_fallback_oracle_address": "0x5B09E578cfEAa23F1b11127A658855434e4F3e09",
    "block_number": 13582107,
    "market": "MAIN"
  }
},{
  "name": "Aave Oracles Price Deviation",
  "description": "FallbackOracle price for WBTC deviates from PriceOracle by 76%",
  "alertId": "AAVE-OPD",
  "protocol": "ethereum",
  "severity": "Critical",
  "type": "Suspicious",
  "metadata": {
    "price_oracle_price": 14058512140390260000,
    "fallback_oracle_price": 31611663000000000000,
    "relative_standard_deviation": 76.8692075546078,
    "token_symbol": "WBTC",
    "actual_price_oracle_address": "0xA50ba011c48153De246E5192C8f9258A2ba79Ca9",
    "actual_fallback_oracle_address": "0x5B09E578cfEAa23F1b11127A658855434e4F3e09",
    "block_number": 13582107,
    "market": "MAIN"
  }
},{
  "name": "Aave Oracles Price Deviation",
  "description": "FallbackOracle price for YFI deviates from PriceOracle by 94%",
  "alertId": "AAVE-OPD",
  "protocol": "ethereum",
  "severity": "Critical",
  "type": "Suspicious",
  "metadata": {
    "price_oracle_price": 7375158255707686000,
    "fallback_oracle_price": 20695442000000000000,
    "relative_standard_deviation": 94.90558536655345,
    "token_symbol": "YFI",
    "actual_price_oracle_address": "0xA50ba011c48153De246E5192C8f9258A2ba79Ca9",
    "actual_fallback_oracle_address": "0x5B09E578cfEAa23F1b11127A658855434e4F3e09",
    "block_number": 13582107,
    "market": "MAIN"
  }
},{
  "name": "Aave Oracles Price Deviation",
  "description": "FallbackOracle price for ZRX deviates from PriceOracle by 93%",
  "alertId": "AAVE-OPD",
  "protocol": "ethereum",
  "severity": "Critical",
  "type": "Suspicious",
  "metadata": {
    "price_oracle_price": 278000000000000,
    "fallback_oracle_price": 767600000000000,
    "relative_standard_deviation": 93.6495791889824,
    "token_symbol": "ZRX",
    "actual_price_oracle_address": "0xA50ba011c48153De246E5192C8f9258A2ba79Ca9",
    "actual_fallback_oracle_address": "0x5B09E578cfEAa23F1b11127A658855434e4F3e09",
    "block_number": 13582107,
    "market": "MAIN"
  }
},{
  "name": "Aave Oracles Price Deviation",
  "description": "FallbackOracle price for UNI deviates from PriceOracle by 102%",
  "alertId": "AAVE-OPD",
  "protocol": "ethereum",
  "severity": "Critical",
  "type": "Suspicious",
  "metadata": {
    "price_oracle_price": 5604832348158875,
    "fallback_oracle_price": 17327330000000000,
    "relative_standard_deviation": 102.23630439963523,
    "token_symbol": "UNI",
    "actual_price_oracle_address": "0xA50ba011c48153De246E5192C8f9258A2ba79Ca9",
    "actual_fallback_oracle_address": "0x5B09E578cfEAa23F1b11127A658855434e4F3e09",
    "block_number": 13582107,
    "market": "MAIN"
  }
},{
  "name": "Aave Oracles Price Deviation",
  "description": "FallbackOracle price for AAVE deviates from PriceOracle by 102%",
  "alertId": "AAVE-OPD",
  "protocol": "ethereum",
  "severity": "Critical",
  "type": "Suspicious",
  "metadata": {
    "price_oracle_price": 69950000000000000,
    "fallback_oracle_price": 217916490000000000,
    "relative_standard_deviation": 102.8021636002162,
    "token_symbol": "AAVE",
    "actual_price_oracle_address": "0xA50ba011c48153De246E5192C8f9258A2ba79Ca9",
    "actual_fallback_oracle_address": "0x5B09E578cfEAa23F1b11127A658855434e4F3e09",
    "block_number": 13582107,
    "market": "MAIN"
  }
},{
  "name": "Aave Oracles Price Deviation",
  "description": "FallbackOracle price for BAT deviates from PriceOracle by 51%",
  "alertId": "AAVE-OPD",
  "protocol": "ethereum",
  "severity": "Critical",
  "type": "Suspicious",
  "metadata": {
    "price_oracle_price": 259781840000000,
    "fallback_oracle_price": 438070000000000,
    "relative_standard_deviation": 51.09627854531415,
    "token_symbol": "BAT",
    "actual_price_oracle_address": "0xA50ba011c48153De246E5192C8f9258A2ba79Ca9",
    "actual_fallback_oracle_address": "0x5B09E578cfEAa23F1b11127A658855434e4F3e09",
    "block_number": 13582107,
    "market": "MAIN"
  }
},{
  "name": "Aave Oracles Price Deviation",
  "description": "FallbackOracle price for BUSD deviates from PriceOracle by 91%",
  "alertId": "AAVE-OPD",
  "protocol": "ethereum",
  "severity": "Critical",
  "type": "Suspicious",
  "metadata": {
    "price_oracle_price": 207965464515670,
    "fallback_oracle_price": 556750000000000,
    "relative_standard_deviation": 91.21942779206944,
    "token_symbol": "BUSD",
    "actual_price_oracle_address": "0xA50ba011c48153De246E5192C8f9258A2ba79Ca9",
    "actual_fallback_oracle_address": "0x5B09E578cfEAa23F1b11127A658855434e4F3e09",
    "block_number": 13582107,
    "market": "MAIN"
  }
},{
  "name": "Aave Oracles Price Deviation",
  "description": "FallbackOracle price for DAI deviates from PriceOracle by 90%",
  "alertId": "AAVE-OPD",
  "protocol": "ethereum",
  "severity": "Critical",
  "type": "Suspicious",
  "metadata": {
    "price_oracle_price": 208886287023453,
    "fallback_oracle_price": 556510000000000,
    "relative_standard_deviation": 90.83496193283604,
    "token_symbol": "DAI",
    "actual_price_oracle_address": "0xA50ba011c48153De246E5192C8f9258A2ba79Ca9",
    "actual_fallback_oracle_address": "0x5B09E578cfEAa23F1b11127A658855434e4F3e09",
    "block_number": 13582107,
    "market": "MAIN"
  }
},{
  "name": "Aave Oracles Price Deviation",
  "description": "FallbackOracle price for ENJ deviates from PriceOracle by 55%",
  "alertId": "AAVE-OPD",
  "protocol": "ethereum",
  "severity": "Critical",
  "type": "Suspicious",
  "metadata": {
    "price_oracle_price": 638725290000000,
    "fallback_oracle_price": 1133230000000000,
    "relative_standard_deviation": 55.814580964963284,
    "token_symbol": "ENJ",
    "actual_price_oracle_address": "0xA50ba011c48153De246E5192C8f9258A2ba79Ca9",
    "actual_fallback_oracle_address": "0x5B09E578cfEAa23F1b11127A658855434e4F3e09",
    "block_number": 13582107,
    "market": "MAIN"
  }
},{
  "name": "Aave Oracles Price Deviation",
  "description": "FallbackOracle price for KNC deviates from PriceOracle by 103%",
  "alertId": "AAVE-OPD",
  "protocol": "ethereum",
  "severity": "Critical",
  "type": "Suspicious",
  "metadata": {
    "price_oracle_price": 420100000000000,
    "fallback_oracle_price": 1317100000000000,
    "relative_standard_deviation": 103.26962928851025,
    "token_symbol": "KNC",
    "actual_price_oracle_address": "0xA50ba011c48153De246E5192C8f9258A2ba79Ca9",
    "actual_fallback_oracle_address": "0x5B09E578cfEAa23F1b11127A658855434e4F3e09",
    "block_number": 13582107,
    "market": "MAIN"
  }
},{
  "name": "Aave Oracles Price Deviation",
  "description": "FallbackOracle price for LINK deviates from PriceOracle by 77%",
  "alertId": "AAVE-OPD",
  "protocol": "ethereum",
  "severity": "Critical",
  "type": "Suspicious",
  "metadata": {
    "price_oracle_price": 7210000000000000,
    "fallback_oracle_price": 16387480000000000,
    "relative_standard_deviation": 77.78355993945117,
    "token_symbol": "LINK",
    "actual_price_oracle_address": "0xA50ba011c48153De246E5192C8f9258A2ba79Ca9",
    "actual_fallback_oracle_address": "0x5B09E578cfEAa23F1b11127A658855434e4F3e09",
    "block_number": 13582107,
    "market": "MAIN"
  }
},{
  "name": "Aave Oracles Price Deviation",
  "description": "FallbackOracle price for MANA deviates from PriceOracle by 49%",
  "alertId": "AAVE-OPD",
  "protocol": "ethereum",
  "severity": "Critical",
  "type": "Suspicious",
  "metadata": {
    "price_oracle_price": 539092042254407,
    "fallback_oracle_price": 324590000000000,
    "relative_standard_deviation": 49.67152997519962,
    "token_symbol": "MANA",
    "actual_price_oracle_address": "0xA50ba011c48153De246E5192C8f9258A2ba79Ca9",
    "actual_fallback_oracle_address": "0x5B09E578cfEAa23F1b11127A658855434e4F3e09",
    "block_number": 13582107,
    "market": "MAIN"
  }
},{
  "name": "Aave Oracles Price Deviation",
  "description": "FallbackOracle price for MKR deviates from PriceOracle by 59%",
  "alertId": "AAVE-OPD",
  "protocol": "ethereum",
  "severity": "Critical",
  "type": "Suspicious",
  "metadata": {
    "price_oracle_price": 667374197991198800,
    "fallback_oracle_price": 1230504000000000000,
    "relative_standard_deviation": 59.343091943923845,
    "token_symbol": "MKR",
    "actual_price_oracle_address": "0xA50ba011c48153De246E5192C8f9258A2ba79Ca9",
    "actual_fallback_oracle_address": "0x5B09E578cfEAa23F1b11127A658855434e4F3e09",
    "block_number": 13582107,
    "market": "MAIN"
  }
},{
  "name": "Aave Oracles Price Deviation",
  "description": "FallbackOracle price for REN deviates from PriceOracle by 105%",
  "alertId": "AAVE-OPD",
  "protocol": "ethereum",
  "severity": "Critical",
  "type": "Suspicious",
  "metadata": {
    "price_oracle_price": 206701748056430,
    "fallback_oracle_price": 668710000000000,
    "relative_standard_deviation": 105.55221653566122,
    "token_symbol": "REN",
    "actual_price_oracle_address": "0xA50ba011c48153De246E5192C8f9258A2ba79Ca9",
    "actual_fallback_oracle_address": "0x5B09E578cfEAa23F1b11127A658855434e4F3e09",
    "block_number": 13582107,
    "market": "MAIN"
  }
},{
  "name": "Aave Oracles Price Deviation",
  "description": "FallbackOracle price for SNX deviates from PriceOracle by 133%",
  "alertId": "AAVE-OPD",
  "protocol": "ethereum",
  "severity": "Critical",
  "type": "Suspicious",
  "metadata": {
    "price_oracle_price": 2225269587982298,
    "fallback_oracle_price": 11237520000000000,
    "relative_standard_deviation": 133.88384856081512,
    "token_symbol": "SNX",
    "actual_price_oracle_address": "0xA50ba011c48153De246E5192C8f9258A2ba79Ca9",
    "actual_fallback_oracle_address": "0x5B09E578cfEAa23F1b11127A658855434e4F3e09",
    "block_number": 13582107,
    "market": "MAIN"
  }
},{
  "name": "Aave Oracles Price Deviation",
  "description": "FallbackOracle price for sUSD deviates from PriceOracle by 91%",
  "alertId": "AAVE-OPD",
  "protocol": "ethereum",
  "severity": "Critical",
  "type": "Suspicious",
  "metadata": {
    "price_oracle_price": 208675811920195,
    "fallback_oracle_price": 560430000000000,
    "relative_standard_deviation": 91.47094785348058,
    "token_symbol": "sUSD",
    "actual_price_oracle_address": "0xA50ba011c48153De246E5192C8f9258A2ba79Ca9",
    "actual_fallback_oracle_address": "0x5B09E578cfEAa23F1b11127A658855434e4F3e09",
    "block_number": 13582107,
    "market": "MAIN"
  }
},{
  "name": "Aave Oracles Price Deviation",
  "description": "FallbackOracle price for TUSD deviates from PriceOracle by 90%",
  "alertId": "AAVE-OPD",
  "protocol": "ethereum",
  "severity": "Critical",
  "type": "Suspicious",
  "metadata": {
    "price_oracle_price": 209170000000000,
    "fallback_oracle_price": 556710000000000,
    "relative_standard_deviation": 90.75573196845458,
    "token_symbol": "TUSD",
    "actual_price_oracle_address": "0xA50ba011c48153De246E5192C8f9258A2ba79Ca9",
    "actual_fallback_oracle_address": "0x5B09E578cfEAa23F1b11127A658855434e4F3e09",
    "block_number": 13582107,
    "market": "MAIN"
  }
},{
  "name": "Aave Oracles Price Deviation",
  "description": "FallbackOracle price for USDC deviates from PriceOracle by 90%",
  "alertId": "AAVE-OPD",
  "protocol": "ethereum",
  "severity": "Critical",
  "type": "Suspicious",
  "metadata": {
    "price_oracle_price": 209190398034568,
    "fallback_oracle_price": 556470000000000,
    "relative_standard_deviation": 90.71374276556303,
    "token_symbol": "USDC",
    "actual_price_oracle_address": "0xA50ba011c48153De246E5192C8f9258A2ba79Ca9",
    "actual_fallback_oracle_address": "0x5B09E578cfEAa23F1b11127A658855434e4F3e09",
    "block_number": 13582107,
    "market": "MAIN"
  }
},{
  "name": "Aave Oracles Price Deviation",
  "description": "FallbackOracle price for CRV deviates from PriceOracle by 17%",
  "alertId": "AAVE-OPD",
  "protocol": "ethereum",
  "severity": "Medium",
  "type": "Suspicious",
  "metadata": {
    "price_oracle_price": 1018692482568371,
    "fallback_oracle_price": 1213140000000000,
    "relative_standard_deviation": 17.42492045889221,
    "token_symbol": "CRV",
    "actual_price_oracle_address": "0xA50ba011c48153De246E5192C8f9258A2ba79Ca9",
    "actual_fallback_oracle_address": "0x5B09E578cfEAa23F1b11127A658855434e4F3e09",
    "block_number": 13582107,
    "market": "MAIN"
  }
}
```
