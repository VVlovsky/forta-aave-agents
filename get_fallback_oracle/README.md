# GetFallbackOracle() Agent

## Description

This agent provides alert if `getFallbackOracle()` function is called

## Supported Chains

- `Ethereum`

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

- AAVE-SFO
  - Fired when a `getFallbackOracle()` function is called 
  - Severity is always set to `"medium"`
  - Type is always set to `"suspicious"` 
  - Metadata contains `tx_hash` and actual `price_oracle` address

## Test the Agent

The agent behaviour can be verified using `npm test`

The transaction can be emulated by inserting the actual PriceOracle contract address into the
transaction `to` parameter and encoding getFallbackOracle() ABI into the transaction `data`
```python
contract = web3.eth.contract(address=Web3.toChecksumAddress(LendingPoolAddressesProvider_mainnet), abi=abi)
price_oracle_address = contract.functions.getPriceOracle().call()
data = encode_hex(function_abi_to_4byte_selector(json.loads(GET_FALLBACK_ORACLE)))

tx_event = create_transaction_event({
    'transaction': {
        'to': price_oracle_address,
        'data': data}
})
```