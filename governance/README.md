# Governance Proposal Agent

## Description

This agent provides alert if governance proposal is `EXECUTED`

## Supported Chains

- Ethereum

## Alerts

Describe each of the type of alerts fired by this agent

- AAVE-GOV-EXEC
  - Fired when a governance proposal is `EXECUTED`
  - Severity is always set to `"info"`
  - Type is always set to `"info"`
  - Metadata contains proposal `id` and `initiator_execution` address

## Test Data

The agent behaviour can be verified using `npm test`

The transaction can be emulated by inserting the actual AAVE_GOVERNANCE_V2 contract address into the
logs `address` parameter and encoding GOVERNANCE_PROPOSAL_EXECUTED ABI into the log `topics`
```python
# filler contains random data, it is necessary to call filter_log() function
filler = eth_abi.encode_abi(["address"], ["0xEC568fffba86c094cf06b22134B23074DFE2252c"])
topics = [event_abi_to_log_topic(json.loads(GOVERNANCE_PROPOSAL_EXECUTED_ABI)), filler]
tx_event = create_transaction_event({
    'receipt': {
        'logs': [
            {'topics': topics,
             'data': filler,
             'address': "0xEC568fffba86c094cf06b22134B23074DFE2252c"}, ]},

})
```