# Ethereum Blockchain Helper

A Python utility for interacting with Ethereum blockchain networks and checking node health.

## Features

- Connect to Ethereum nodes via RPC
- Check network chain ID and identify network type
- Query wallet balances
- Retrieve block information
- Check various RPC methods including:
  - eth_chainId
  - eth_getBlockByNumber
  - eth_getBlockByHash
  - debug_getRawReceipts
  - eth_getStorageAt
  - /eth/v1/beacon/blob_sidecars/{block_id}
- Identify RPC type (Full RPC, Beacon Only, or General Only)
- Detect and categorize broken functions

## Installation

1. Clone this repository
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the eth_helper.py script to perform a comprehensive node health check:

```bash
python eth_helper.py
```

## Configuration

The script uses the following default settings:

- RPC Endpoint: https://mainnet-eth-beacon-mtl.nebulablock.com
- Wallet Address: 0xe945D527De9c5121EdA9cF48e23CDF691894D4c0

You can modify these settings in the script to connect to different networks or check different wallet addresses.

## Output

The script provides detailed information about:

1. Connection status to the RPC endpoint
2. Network identification (chain ID and network name)
3. Wallet balance
4. Block information
5. Various RPC method checks
6. RPC type identification (Full RPC, Beacon Only, or General Only)
7. Summary of tests passed
8. List of broken functions categorized by type (General RPC or Beacon RPC)

Example output:
```
[+] Using RPC: https://mainnet-eth-beacon-mtl.nebulablock.com
[+] Successfully connected to RPC

[*] Checking RPC Method: eth_chainId
[+] Network: Ethereum Mainnet

[*] Checking Wallet Balance
[+] Wallet Balance: 0.12345678 ETH

...

[*] Node health check completed: 7/8 tests passed
[*] RPC Type: Full RPC (Beacon and General)
[*] General RPC tests passed: 6/6
[*] Beacon RPC tests passed: 1/1

[!] Function Broken:
  General RPC:
    - eth_getBlockByHash
```

## Requirements

- Python 3.6+
- web3
- requests

See requirements.txt for specific package versions. 