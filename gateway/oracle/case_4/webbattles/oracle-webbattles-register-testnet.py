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

def register_webbattles_battle_task():
    """Register webbattles battle replication task for testnets"""
    
    # Load contract ABI
    with open(CONTRACT_ARTIFACTS_PATH, 'r') as file:
        contract_data = json.load(file)
    
    # Use testnet network IDs
    req_params = {
        'sourceNetworkId': { 'id': 'Sepolia', 'ledgerType': 'ETHEREUM' },
        'sourceContract': {
            "contractName": "WebBattles", 
            "contractAbi": contract_data["abi"],
            "contractAddress": CONTRACT_CHAIN_1,
        },
        'destinationNetworkId': { 'id': 'BaseSepolia', 'ledgerType': 'ETHEREUM' },
        'destinationContract': {
            "contractAbi": contract_data["abi"],
            "contractName": "WebBattles",
            "contractBytecode": contract_data["bytecode"],
            "contractAddress": CONTRACT_CHAIN_2,
            "methodName": "replicateBattle",
        },
        'listeningOptions': {
            "eventSignature": "BattleCreated(bytes32,address,uint256,string)",
            "filterParams": ["battleId", "challenger", "betAmount", "battleType"],
        },
        'taskMode': 'EVENT_LISTENING',
        'taskType': 'READ_AND_UPDATE'
    }
    
    return register_oracle(req_params)

if __name__ == "__main__":
    print("Registering WebBattles Oracle Task for Testnets...")
    print(f"Sepolia Contract: {CONTRACT_CHAIN_1}")
    print(f"Base Sepolia Contract: {CONTRACT_CHAIN_2}")
    print()
    
    print("Registering battle replication task...")
    try:
        battle_response = register_webbattles_battle_task()
        battle_id = battle_response.get("taskID")
        print(f"✅ Battle task registered: {battle_id}")
        
        # Auto-update config.py with new task ID
        print("\nUpdating config.py with new task ID...")
        update_multiple_config_variables({
            'REPLICATION_TASK_ID': battle_id
        })
        print("✅ Config updated successfully!")
        
    except Exception as e:
        print(f"❌ Battle task failed: {e}")
        import traceback
        traceback.print_exc()

