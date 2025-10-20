import os
import sys
import json
import requests
from web3 import Web3, HTTPProvider

# --- Settings ---
SWAN_RPC = 'https://eth2-beacon-mainnet.nodereal.io/v1/70cd6a7a115b42b1a76f69167bcf0912'
WALLET_ADDRESS = '0xe945D527De9c5121EdA9cF48e23CDF691894D4c0'
print(f"[+] Using RPC: {SWAN_RPC}")

# Initialize test counter
tests_passed = 0
total_tests = 8

# Track which specific tests passed
general_rpc_tests_passed = 0
beacon_rpc_tests_passed = 0

# Track broken functions by category
broken_general_functions = []
broken_beacon_functions = []

# --- Connect to Node ---
try:
    w3 = Web3(HTTPProvider(SWAN_RPC))
    assert w3.is_connected(), "Web3 connection failed"
    print(f"[+] Successfully connected to RPC")
    tests_passed += 1
    general_rpc_tests_passed += 1
except Exception as e:
    print(f"[!] ERROR: Failed to connect to RPC: {e}")
    broken_general_functions.append("Web3 Connection")

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
    tests_passed += 1
    general_rpc_tests_passed += 1
except Exception as e:
    print(f"[!] eth_chainId check failed: {e}")
    broken_general_functions.append("eth_chainId")

# --- Check Wallet Balance ---
try:
    print("\n[*] Checking Wallet Balance")
    balance = w3.eth.get_balance(WALLET_ADDRESS)
    formatted_balance = f"{balance / 10**18:.8f}"
    print(f"[+] Wallet Balance: {formatted_balance} ETH")
    tests_passed += 1
    general_rpc_tests_passed += 1
except Exception as e:
    print(f"[!] Failed to fetch wallet balance: {e}")
    broken_general_functions.append("eth_getBalance")

# --- Check eth_getBlockByNumber (latest) ---
try:
    print("\n[*] Checking RPC Method: eth_getBlockByNumber")
    latest_block = w3.eth.get_block('latest')
    print(f"[+] eth_getBlockByNumber successful. Latest Block: {latest_block['number']}")
    tests_passed += 1
    general_rpc_tests_passed += 1
except Exception as e:
    print(f"[!] eth_getBlockByNumber check failed: {e}")
    broken_general_functions.append("eth_getBlockByNumber")

# --- Check eth_getBlockByHash ---
try:
    print("\n[*] Checking RPC Method: eth_getBlockByHash")
    block_by_hash = w3.eth.get_block(latest_block['hash'])
    print(f"[+] eth_getBlockByHash successful. Block Number: {block_by_hash['number']}")
    tests_passed += 1
    general_rpc_tests_passed += 1
except Exception as e:
    print(f"[!] eth_getBlockByHash check failed: {e}")
    broken_general_functions.append("eth_getBlockByHash")

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
        tests_passed += 1
        general_rpc_tests_passed += 1
    else:
        print(f"[!] debug_getRawReceipts returned no result: {receipts}")
        broken_general_functions.append("debug_getRawReceipts")
except Exception as e:
    print(f"[!] debug_getRawReceipts check failed: {e}")
    broken_general_functions.append("debug_getRawReceipts")

# --- Check eth_getStorageAt (random address) ---
try:
    print("\n[*] Checking RPC Method: eth_getStorageAt")
    storage_value = w3.eth.get_storage_at(WALLET_ADDRESS, 0)
    print(f"[+] eth_getStorageAt successful. Value: {storage_value.hex()}")
    tests_passed += 1
    general_rpc_tests_passed += 1
except Exception as e:
    print(f"[!] eth_getStorageAt check failed: {e}")
    broken_general_functions.append("eth_getStorageAt")

# --- Check /eth/v1/beacon/blob_sidecars/{block_id} ---
try:
    print("\n[*] Checking RPC Method: /eth/v1/beacon/blob_sidecars/{block_id} (Consensus Layer API)")
    # Consensus layer endpoint expects slot number, block root, or tags (head, finalized, etc)
    block_id = 'head'  # Use 'head' tag instead of execution block number
    beacon_url = SWAN_RPC.rstrip('/') + f"/eth/v1/beacon/blob_sidecars/{block_id}"
    blob_response = requests.get(beacon_url)
    if blob_response.status_code == 200:
        print(f"[+] blob_sidecars API successful for block {block_id}")
        tests_passed += 1
        beacon_rpc_tests_passed += 1
    elif blob_response.status_code == 400:
        print(f"[!] blob_sidecars API invalid request (400 Bad Request) - likely not a beacon node")
        broken_beacon_functions.append("blob_sidecars")
    elif blob_response.status_code == 404:
        print(f"[!] blob_sidecars not found for block {block_id} (404 Not Found)")
        broken_beacon_functions.append("blob_sidecars")
    elif blob_response.status_code == 401:
        print(f"[!] blob_sidecars requires authentication (401 Unauthorized)")
        broken_beacon_functions.append("blob_sidecars")
    else:
        print(f"[!] blob_sidecars unexpected status {blob_response.status_code}")
        broken_beacon_functions.append("blob_sidecars")
except Exception as e:
    print(f"[!] blob_sidecars check failed: {e}")
    broken_beacon_functions.append("blob_sidecars")

# Determine RPC type
rpc_type = "Unknown"
if general_rpc_tests_passed >= 5 and beacon_rpc_tests_passed >= 1:
    rpc_type = "Full RPC (Beacon and General)"
elif general_rpc_tests_passed >= 5 and beacon_rpc_tests_passed == 0:
    rpc_type = "General Only"
elif general_rpc_tests_passed < 5 and beacon_rpc_tests_passed >= 1:
    rpc_type = "Beacon Only"

# Print summary
print(f"\n[*] Node health check completed: {tests_passed}/{total_tests} tests passed")
print(f"[*] RPC Type: {rpc_type}")
print(f"[*] General RPC tests passed: {general_rpc_tests_passed}/6")
print(f"[*] Beacon RPC tests passed: {beacon_rpc_tests_passed}/1")

# Print broken functions by category
if broken_general_functions or broken_beacon_functions:
    print("\n[!] Function Broken:")
    
    if broken_general_functions:
        print("  General RPC:")
        for func in broken_general_functions:
            print(f"    - {func}")
    
    if broken_beacon_functions:
        print("  Beacon RPC:")
        for func in broken_beacon_functions:
            print(f"    - {func}")
