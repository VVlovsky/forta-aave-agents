# Aave FlashLoan Transaction Agent

## Description

This agent provides alert if flash loan transaction value ≥ $10m

## Supported Chains

- Ethereum

## Supported Markets

- `Main Market` - Main Aave Market
- `AMM Market` - The AMM market supports LP tokens from certain Automated Market Maker (AMM) decentralised exchanges,
  such as Uniswap v2 and Balancer.

## Market Setup

You can specify market in the `agent.py`

```python
MARKET = 'MAIN'  # available options: MAIN, AMM
```

## Alerts

Describe each of the type of alerts fired by this agent

- AAVE-FL
    - Fired when flash loan transaction value ≥ $10m
    - Severity depends on the loan transaction value:
        - `FindingSeverity.Medium` if $10m <= value < $30m
        - `FindingSeverity.High` if $30m <= value $50m
        - `FindingSeverity.Critical` if $50m <= value

    - Type is always set to `"info"`
    - Metadata:
        - `total_usd` - flash loan transaction value
        - `market` - specified market
        - `tx_hash` - hash of the transaction
        - `receiver` - receiver of the flash loan

## Test Data

The agent behaviour can be verified using `npm test`

To test smart contracts behavior it is needed to create Web3 Mock and pass the mock as the argument into
the `provide_handle_block()`.

```python
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
```

The transaction can be emulated by inserting the actual LendingPool contract address into the
transaction `to` parameter and encoding flashLoan() function with parameters into the transaction `data`:
```python
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
```