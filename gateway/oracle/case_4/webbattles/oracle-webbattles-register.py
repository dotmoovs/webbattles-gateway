#!/usr/bin/env python3

import requests
import json
from config import *
from config_updater import update_multiple_config_variables

def register_oracle(params):
    """
    Calls the /api/v1/@hyperledger/cactus-plugin-satp-hermes/oracle/register endpoint
    with the given params as JSON body.
    """
    url = "http://localhost:4010/api/v1/@hyperledger/cactus-plugin-satp-hermes/oracle/register"
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json=params, headers=headers)
    response.raise_for_status()
    return response.json()

def register_webbattles_sync_task():
    """Register webbattles sync task using the working oracle4 pattern"""
    
    # Load contract ABI
    with open(CONTRACT_ARTIFACTS_PATH, 'r') as file:
        contract_data = json.load(file)
    
    # Use the exact pattern from working oracle4
    req_params = {
        'sourceNetworkId': { 'id': 'HardhatTestNetwork1', 'ledgerType': 'ETHEREUM' },
        'sourceContract': {
            "contractName": "WebBattles",
            "contractAbi": contract_data["abi"],
            "contractAddress": CONTRACT_CHAIN_1,
        },
        'destinationNetworkId': { 'id': 'HardhatTestNetwork2', 'ledgerType': 'ETHEREUM' },
        'destinationContract': {
            "contractAbi": contract_data["abi"],
            "contractName": "WebBattles",
            "contractBytecode": contract_data["bytecode"],
            "contractAddress": CONTRACT_CHAIN_2,
            "methodName": "syncBattleData",
            # Use simple parameter like oracle4 - oracle will pass the filtered data
        },
        'listeningOptions': {
            "eventSignature": "UpdatedData(bytes32,string,uint256)",
            # Use simple filtering like oracle4 - just pass the data field
            "filterParams": ["data"],
        },
        'taskMode': 'EVENT_LISTENING',
        'taskType': 'READ_AND_UPDATE'
    }
    
    return register_oracle(req_params)

def register_webbattles_battle_task():
    """Register webbattles battle replication task using the working oracle4 pattern"""
    
    # Load contract ABI
    with open(CONTRACT_ARTIFACTS_PATH, 'r') as file:
        contract_data = json.load(file)
    
    # Use the exact pattern from working oracle4
    req_params = {
        'sourceNetworkId': { 'id': 'HardhatTestNetwork1', 'ledgerType': 'ETHEREUM' },
        'sourceContract': {
            "contractName": "WebBattles", 
            "contractAbi": contract_data["abi"],
            "contractAddress": CONTRACT_CHAIN_1,
        },
        'destinationNetworkId': { 'id': 'HardhatTestNetwork2', 'ledgerType': 'ETHEREUM' },
        'destinationContract': {
            "contractAbi": contract_data["abi"],
            "contractName": "WebBattles",
            "contractBytecode": contract_data["bytecode"],
            "contractAddress": CONTRACT_CHAIN_2,
            "methodName": "replicateBattle",
            # Oracle4 pattern - let oracle handle the parameter mapping
        },
        'listeningOptions': {
            "eventSignature": "BattleCreated(bytes32,address,uint256,string)",
            # Use simple filtering like oracle4 - oracle will handle parameter mapping
            "filterParams": ["battleId", "challenger", "betAmount", "battleType"],
        },
        'taskMode': 'EVENT_LISTENING',
        'taskType': 'READ_AND_UPDATE'
    }
    
    return register_oracle(req_params)

if __name__ == "__main__":
    print("Registering WebBattles Oracle Tasks (Oracle4 Pattern)...")
    print(f"Chain 1 Contract: {CONTRACT_CHAIN_1}")
    print(f"Chain 2 Contract: {CONTRACT_CHAIN_2}")
    print()
    
    print("Registering sync task...")
    try:
        sync_response = register_webbattles_sync_task()
        sync_id = sync_response.get("taskID")
        print(f"Sync task registered: {sync_id}")
    except Exception as e:
        print(f"Sync task failed: {e}")
        sync_id = None
    
    print("\nRegistering battle replication task...")
    try:
        battle_response = register_webbattles_battle_task()
        battle_id = battle_response.get("taskID")
        print(f"Battle task registered: {battle_id}")
    except Exception as e:
        print(f"Battle task failed: {e}")
        battle_id = None
    
    if sync_id and battle_id:
        print(f"\nAll tasks registered successfully!")
        print(f"Sync Task ID: {sync_id}")
        print(f"Battle Task ID: {battle_id}")
        
        # Auto-update config.py with new task IDs
        print("\nUpdating config.py with new task IDs...")
        update_multiple_config_variables({
            'SYNC_TASK_ID': sync_id,
            'REPLICATION_TASK_ID': battle_id
        })
        print("Config updated successfully!")
    else:
        print("\nRegistration failed - not all tasks were registered") 