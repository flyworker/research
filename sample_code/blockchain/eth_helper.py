import os
import sys
import json
import requests
from web3 import Web3, HTTPProvider

# --- Settings ---
SWAN_RPC = 'https://mainnet-eth-mtl.nebulablock.com'
WALLET_ADDRESS = '0xe945D527De9c5121EdA9cF48e23CDF691894D4c0'

# --- Connect to Node ---
try:
    w3 = Web3(HTTPProvider(SWAN_RPC))
    assert w3.is_connected(), "Web3 connection failed"
except Exception as e:
    print(f"[!] ERROR: Failed to connect to RPC: {e}")
    sys.exit(1)

# --- Check eth_chainId ---
try:
    print("\n[*] Checking RPC Method: eth_chainId")
    chain_id = w3.eth.chain_id
    network_name = {
        1: "Ethereum Mainnet",
        5: "Goerli Testnet",
        11155111: "Sepolia Testnet",
        254: "Swan Mainnet"
    }.get(chain_id, f"Unknown Network (Chain ID: {chain_id})")
    print(f"[+] Network: {network_name}")
except Exception as e:
    print(f"[!] eth_chainId check failed: {e}")

# --- Check Wallet Balance ---
try:
    print("\n[*] Checking Wallet Balance")
    balance = w3.eth.get_balance(WALLET_ADDRESS)
    formatted_balance = f"{balance / 10**18:.8f}"
    print(f"[+] Wallet Balance: {formatted_balance} ETH")
except Exception as e:
    print(f"[!] Failed to fetch wallet balance: {e}")

# --- Check eth_getBlockByNumber (latest) ---
try:
    print("\n[*] Checking RPC Method: eth_getBlockByNumber")
    latest_block = w3.eth.get_block('latest')
    print(f"[+] eth_getBlockByNumber successful. Latest Block: {latest_block['number']}")
except Exception as e:
    print(f"[!] eth_getBlockByNumber check failed: {e}")

# --- Check eth_getBlockByHash ---
try:
    print("\n[*] Checking RPC Method: eth_getBlockByHash")
    block_by_hash = w3.eth.get_block(latest_block['hash'])
    print(f"[+] eth_getBlockByHash successful. Block Number: {block_by_hash['number']}")
except Exception as e:
    print(f"[!] eth_getBlockByHash check failed: {e}")

# --- Check debug_getRawReceipts (manual RPC call) ---
try:
    print("\n[*] Checking RPC Method: debug_getRawReceipts")
    payload = {
        "jsonrpc": "2.0",
        "method": "debug_getRawReceipts",
        "params": [hex(latest_block['number'])],
        "id": 1
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(SWAN_RPC, data=json.dumps(payload), headers=headers)
    receipts = response.json()
    if 'result' in receipts:
        print(f"[+] debug_getRawReceipts successful. Receipts count: {len(receipts['result'])}")
    else:
        print(f"[!] debug_getRawReceipts returned no result: {receipts}")
except Exception as e:
    print(f"[!] debug_getRawReceipts check failed: {e}")

# --- Check eth_getStorageAt (random address) ---
try:
    print("\n[*] Checking RPC Method: eth_getStorageAt")
    storage_value = w3.eth.get_storage_at(WALLET_ADDRESS, 0)
    print(f"[+] eth_getStorageAt successful. Value: {storage_value.hex()}")
except Exception as e:
    print(f"[!] eth_getStorageAt check failed: {e}")

# --- Check /eth/v1/beacon/blob_sidecars/{block_id} ---
try:
    print("\n[*] Checking RPC Method: /eth/v1/beacon/blob_sidecars/{block_id} (Consensus Layer API)")
    # Consensus layer endpoint expects slot number, block root, or tags (head, finalized, etc)
    block_id = 'head'  # Use 'head' tag instead of execution block number
    beacon_url = SWAN_RPC.rstrip('/') + f"/eth/v1/beacon/blob_sidecars/{block_id}"
    blob_response = requests.get(beacon_url)
    if blob_response.status_code == 200:
        print(f"[+] blob_sidecars API successful for block {block_id}")
    elif blob_response.status_code == 400:
        print(f"[!] blob_sidecars API invalid request (400 Bad Request) - likely not a beacon node")
    elif blob_response.status_code == 404:
        print(f"[!] blob_sidecars not found for block {block_id} (404 Not Found)")
    elif blob_response.status_code == 401:
        print(f"[!] blob_sidecars requires authentication (401 Unauthorized)")
    else:
        print(f"[!] blob_sidecars unexpected status {blob_response.status_code}")
except Exception as e:
    print(f"[!] blob_sidecars check failed: {e}")

print("\n[*] Node health check completed.")
