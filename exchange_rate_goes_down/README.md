# Aave Tokens Exchange Rate Goes Down Agent

## Description

This agent provides alert if aToken / aToken exchange rate goes down

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

## Supported Tokens

All token pairs are supported. You can check available options here:

- For Main Market: https://docs.aave.com/developers/deployed-contracts/deployed-contracts
- For AMM Market: https://docs.aave.com/developers/deployed-contracts/amm-market

Please specify your pair in the `agent.py`. Default pair is `aUSDC / aDAI`

```python
TOKEN_1 = 'USDC'  # Specify first token name
TOKEN_2 = 'DAI'  # Specify second token name
```

## Alerts

Describe each of the type of alerts fired by this agent

- AAVE-EXR
    - Fired when aToken / aToken exchange rate goes down
    - Severity depends on how much did the exchange rate drop:
        - `FindingSeverity.Medium` if difference < 0.02
        - `FindingSeverity.High` if 0.02 < difference < 0.1
        - `FindingSeverity.Critical` if 0.1 < difference

    - Type is always set to `"info"`
    - Metadata:
        - `difference` - how much did the exchange rate drop
        - `1st_token` - 1st Token
        - `2nd_token` - 2nd Token
        - `market` - specified market

## Test Data

The agent behaviour can be verified using `npm test`

To test smart contracts behavior it is needed to create Web3 Mock and pass the mock as the argument into
the `provide_handle_block()`.

```python
class Web3Mock:
    def __init__(self, exchange_rate_1, exchange_rate_2):
        self.eth = EthMock(exchange_rate_1, exchange_rate_2)


class EthMock:
    def __init__(self, exchange_rate_1, exchange_rate_2):
        self.contract = ContractMock(exchange_rate_1, exchange_rate_2)


class ContractMock:
    def __init__(self, exchange_rate_1, exchange_rate_2):
        self.functions = FunctionsMock(exchange_rate_1, exchange_rate_2)

    def __call__(self, *args, **kwargs):
        return self


class FunctionsMock:
    def __init__(self, exchange_rate_1, exchange_rate_2):
        self.exchange_rate_1 = exchange_rate_1
        self.exchange_rate_2 = exchange_rate_2

    def getAssetsPrices(self, **_):
        return self

    def call(self, **_):
        return self.exchange_rate_1, self.exchange_rate_2
```