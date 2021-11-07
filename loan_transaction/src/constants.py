USD_TH = 10000000
HIGH_USD_TH = 30000000
CRITICAL_USD_TH = 50000000


LendingPoolAddressesProvider = {
    'MAIN_MAINNET': "0xB53C1a33016B2DC2fF3653530bfF1848a515c8c5",
    'AMM_MAINNET': "0xAcc030EF66f9dFEAE9CbB0cd1B25654b82cFA8d5",
}

GET_ASSETS_PRICE_ABI = """
  {
    "inputs": [
      {
        "internalType": "address[]",
        "name": "assets",
        "type": "address[]"
      }
    ],
    "name": "getAssetsPrices",
    "outputs": [
      {
        "internalType": "uint256[]",
        "name": "",
        "type": "uint256[]"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  }"""

FLASH_LOAN_FUNCTION = """
{
  "inputs": [
    {
      "internalType": "address",
      "name": "receiverAddress",
      "type": "address"
    },
    {
      "internalType": "address[]",
      "name": "assets",
      "type": "address[]"
    },
    {
      "internalType": "uint256[]",
      "name": "amounts",
      "type": "uint256[]"
    },
    {
      "internalType": "uint256[]",
      "name": "modes",
      "type": "uint256[]"
    },
    {
      "internalType": "address",
      "name": "onBehalfOf",
      "type": "address"
    },
    {
      "internalType": "bytes",
      "name": "params",
      "type": "bytes"
    },
    {
      "internalType": "uint16",
      "name": "referralCode",
      "type": "uint16"
    }
  ],
  "name": "flashLoan",
  "outputs": [],
  "stateMutability": "nonpayable",
  "type": "function"
}"""
