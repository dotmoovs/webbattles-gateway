#!/usr/bin/env python3

import requests
import json
import sys
from web3 import Web3
from config import *

def get_battle_from_chain1(battle_id):
    """
    Get actual battle data from Chain 1 to use real values instead of defaults
    """
    w3 = Web3(Web3.HTTPProvider(CHAIN_1_RPC))
    
    with open(CONTRACT_ARTIFACTS_PATH, 'r') as file:
        contract_data = json.load(file)
    
    contract = w3.eth.contract(address=CONTRACT_CHAIN_1, abi=contract_data["abi"])
    battle = contract.functions.getBattle(battle_id).call()
    
    return {
        'battleId': '0x' + battle[0].hex(),  # Add 0x prefix for proper bytes32 format
        'challenger': battle[1],
        'opponent': battle[2], 
        'betAmount': str(battle[3]),
        'status': battle[4],
        'winner': battle[5],
        'createdAt': battle[6],
        'completedAt': battle[7],
        'battleType': battle[8]
    }

def execute_oracle(params):
    """
    Calls the /api/v1/@hyperledger/cactus-plugin-satp-hermes/oracle/execute endpoint
    """
    headers = {"Content-Type": "application/json"}
    response = requests.post(ORACLE_EXECUTE_URL, json=params, headers=headers)
    response.raise_for_status()
    return response.json()

def execute_webbattles_update(method="sync"):
    """
    Execute oracle update for WebBattles contracts using actual battle data from Chain 1
    """
    with open(CONTRACT_ARTIFACTS_PATH, 'r') as file:
        contract_data = json.load(file)
    
    # Get actual battle data from Chain 1
    print(f"Getting battle data from Chain 1...")
    battle_data = get_battle_from_chain1(LAST_BATTLE_ID)
    
    print(f"Real battle data:")
    print(f"  Battle ID: {battle_data['battleId']}")
    print(f"  Challenger: {battle_data['challenger']}")
    print(f"  Bet Amount: {int(battle_data['betAmount']) / 1e18} ETH")
    print(f"  Battle Type: {battle_data['battleType']}")
    
    if method == "replicate":
        method_name = "replicateBattle"
        # Use REAL battle data instead of defaults
        params_data = [
            battle_data['battleId'], 
            battle_data['challenger'],  # Real challenger address
            battle_data['betAmount'],   # Real bet amount
            battle_data['battleType']   # Real battle type
        ]
    else:
        method_name = "syncBattleData"
        # Use real battle data for sync too
        params_data = [f"battle_created,{battle_data['battleId']},{battle_data['challenger']},{battle_data['betAmount']},{battle_data['battleType']}"]
    
    # Use direct execution format like the working case_4 example
    req_params = {
        'destinationNetworkId': { 
            'id': DESTINATION_NETWORK_ID, 
            'ledgerType': 'ETHEREUM' 
        },
        'destinationContract': {
            "contractAbi": contract_data["abi"],
            "contractName": "WebBattles",
            "contractBytecode": contract_data["bytecode"],
            "contractAddress": CONTRACT_CHAIN_2,
            "methodName": method_name,
            "params": params_data
        },
        'taskType': 'UPDATE'
    }
    
    print(f"\nExecuting {method_name} via direct oracle execution")
    print(f"Target contract: {CONTRACT_CHAIN_2}")
    print(f"Using REAL challenger: {battle_data['challenger']}")
    
    result = execute_oracle(req_params)
    
    # Check for operations array directly in the response
    operations = result.get("operations", [])
    if operations:
        operation = operations[0]
        status = operation.get("status", "")
        output = operation.get("output", {})
        
        if status == "SUCCESS":
            receipt = output.get("transactionReceipt", {})
            print(f"\nOracle execution successful!")
            print(f"Method: {method_name}")
            print(f"Transaction: {receipt.get('transactionHash', 'N/A')}")
            gas_used = receipt.get('gasUsed', 'N/A')
            print(f"Gas Used: {gas_used:,}" if isinstance(gas_used, int) else f"Gas Used: {gas_used}")
            print(f"Status: {status}")
            return True
        else:
            print(f"Oracle execution failed: {output.get('output', 'Unknown error')}")
            return False
    else:
        print(f"Oracle execution failed: {result}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python oracle-webbattles-execute-update.py [sync|replicate|both]")
        print("This script uses direct execution (not registered tasks)")
        print("\nOptions:")
        print("  sync      - Execute syncBattleData only")
        print("  replicate - Execute replicateBattle only") 
        print("  both      - Execute both sync and replicate")
        sys.exit(1)
    
    method = sys.argv[1] if len(sys.argv) > 1 else "sync"
    
    if method == "both":
        print("Executing BOTH sync and replicate operations...")
        print("=" * 60)
        
        # Execute sync first
        print("\n1. SYNC OPERATION:")
        print("-" * 30)
        sync_success = execute_webbattles_update("sync")
        
        print("\n" + "=" * 60)
        
        # Execute replicate second
        print("\n2. REPLICATE OPERATION:")
        print("-" * 30)
        replicate_success = execute_webbattles_update("replicate")
        
        print("\n" + "=" * 60)
        print("\nSUMMARY:")
        print(f"Sync: {'SUCCESS' if sync_success else 'FAILED'}")
        print(f"Replicate: {'SUCCESS' if replicate_success else 'FAILED'}")
        
        if sync_success and replicate_success:
            print("\nBoth operations completed successfully!")
            print("You can now run: python3 verify-cross-chain-battle.py")
        else:
            print("\nSome operations failed. Check the logs above.")
    else:
        print(f"Executing oracle update with method: {method}")
        execute_webbattles_update(method)

if __name__ == "__main__":
    main() 
    