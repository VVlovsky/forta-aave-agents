GET_FALLBACK_ORACLE = """
   {
    "inputs": [],
    "name": "getFallbackOracle",
    "outputs": [
      {
        "internalType": "address",
        "name": "",
        "type": "address"
      }
    ],
    "stateMutability": "view",
    "type": "function"
   }"""

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

LendingPoolAddressesProvider = {
    'MAIN_MAINNET': "0xB53C1a33016B2DC2fF3653530bfF1848a515c8c5",
    'AMM_MAINNET': "0xAcc030EF66f9dFEAE9CbB0cd1B25654b82cFA8d5",
}
