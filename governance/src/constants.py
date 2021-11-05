AAVE_GOVERNANCE_V2_MAINNET = '0xEC568fffba86c094cf06b22134B23074DFE2252c'
AAVE_GOVERNANCE_V2_KOVAN = '0xc2eBaB3Bac8f2f5028f5C7317027A41EBFCa31D2'
GOVERNANCE_PROPOSAL_EXECUTED_ABI = """
{
  "anonymous": false,
  "inputs": [
    {
      "indexed": false,
      "internalType": "uint256",
      "name": "id",
      "type": "uint256"
    },
    {
      "indexed": true,
      "internalType": "address",
      "name": "initiatorExecution",
      "type": "address"
    }
  ],
  "name": "ProposalExecuted",
  "type": "event"
}"""