#!/usr/bin/env python3

from web3 import Web3
import json
from time import sleep
from config import *
from config_updater import update_config_variable

def create_battle_test():
    print("WEBBATTLES CROSS-CHAIN ORACLE TEST")
    print("-" * 50)
    
    w3_chain1 = Web3(Web3.HTTPProvider(CHAIN_1_RPC))
    w3_chain2 = Web3(Web3.HTTPProvider(CHAIN_2_RPC))
    
    print(f"Chain 1 (port 8545): Connected = {w3_chain1.is_connected()}")
    print(f"Chain 2 (port 8546): Connected = {w3_chain2.is_connected()}")
    
    with open(CONTRACT_ARTIFACTS_PATH, 'r') as file:
        contract_data = json.load(file)
    abi = contract_data["abi"]
    
    contract_chain1 = w3_chain1.eth.contract(address=CONTRACT_CHAIN_1, abi=abi)
    
    accounts = w3_chain1.eth.accounts
    challenger = accounts[0]
    bet_amount = w3_chain1.to_wei(0.1, 'ether')
    battle_type = DEFAULT_BATTLE_TYPE
    
    print(f"\nCreating battle on Chain 1...")
    print(f"Challenger: {challenger}")
    print(f"Bet Amount: {bet_amount} wei ({bet_amount / 1e18} ETH)")
    print(f"Battle Type: {battle_type}")
    
    tx_hash = contract_chain1.functions.createBattle(battle_type).transact({
        'from': challenger,
        'value': bet_amount,
        'gas': 500000
    })
    
    receipt = w3_chain1.eth.wait_for_transaction_receipt(tx_hash)
    
    if receipt.status == 1:
        # Parse logs to find BattleCreated event
        battle_id = None
        for log in receipt.logs:
            try:
                # Decode the BattleCreated event
                decoded_log = contract_chain1.events.BattleCreated().process_log(log)
                battle_id = decoded_log['args']['battleId'].hex()
                break
            except:
                continue
        
        if battle_id:
            print(f"\nBattle created successfully!")
            print(f"Transaction Hash: {tx_hash.hex()}")
            print(f"Battle ID: {battle_id}")
            print(f"Gas Used: {receipt.gasUsed:,}")
            print(f"\nOracle will now sync this battle to Chain 2...")
            
            # Auto-update config.py with new battle ID (ensure 0x prefix)
            print("Updating config.py with new battle ID...")
            battle_id_with_prefix = battle_id if battle_id.startswith('0x') else f'0x{battle_id}'
            update_config_variable('LAST_BATTLE_ID', battle_id_with_prefix)
            
            return battle_id
        else:
            print("Could not extract battle ID from logs")
            return None
    else:
        print("Battle creation failed!")
        return None

if __name__ == "__main__":
    battle_id = create_battle_test()
    if battle_id:
        print(f"\nTest completed! Battle {battle_id} ready for cross-chain sync.") 
        