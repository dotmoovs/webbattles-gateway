#!/usr/bin/env python3

from web3 import Web3
import json
from config import *

def verify_cross_chain_battle():
    print("CROSS-CHAIN BATTLE VERIFICATION")
    print("-" * 50)
    
    w3_chain1 = Web3(Web3.HTTPProvider(CHAIN_1_RPC))
    w3_chain2 = Web3(Web3.HTTPProvider(CHAIN_2_RPC))
    
    print(f"Chain 1 Connected: {w3_chain1.is_connected()}")
    print(f"Chain 2 Connected: {w3_chain2.is_connected()}")
    
    with open(CONTRACT_ARTIFACTS_PATH, 'r') as file:
        contract_data = json.load(file)
    abi = contract_data["abi"]
    
    contract_chain1 = w3_chain1.eth.contract(address=CONTRACT_CHAIN_1, abi=abi)
    contract_chain2 = w3_chain2.eth.contract(address=CONTRACT_CHAIN_2, abi=abi)
    
    print(f"\nChecking battle: {LAST_BATTLE_ID}")
    
    battle1 = contract_chain1.functions.getBattle(LAST_BATTLE_ID).call()
    battle2 = contract_chain2.functions.getBattle(LAST_BATTLE_ID).call()
    
    print(f"\nCHAIN 1 BATTLE:")
    print(f"  Battle ID: {battle1[0].hex()}")
    print(f"  Challenger: {battle1[1]}")
    print(f"  Opponent: {battle1[2]}")
    print(f"  Bet Amount: {battle1[3] / 1e18} ETH")
    print(f"  Status: {battle1[4]}")
    print(f"  Winner: {battle1[5]}")
    print(f"  Created At: {battle1[6]}")
    print(f"  Battle Type: {battle1[8]}")
    
    print(f"\nCHAIN 2 BATTLE:")
    print(f"  Battle ID: {battle2[0].hex()}")
    print(f"  Challenger: {battle2[1]}")
    print(f"  Opponent: {battle2[2]}")
    print(f"  Bet Amount: {battle2[3] / 1e18} ETH")
    print(f"  Status: {battle2[4]}")
    print(f"  Winner: {battle2[5]}")
    print(f"  Created At: {battle2[6]}")
    print(f"  Battle Type: {battle2[8]}")
    
    if battle1[0] == battle2[0] and battle1[1] == battle2[1] and battle1[3] == battle2[3]:
        print(f"\nCROSS-CHAIN SYNC SUCCESSFUL!")
        print(f"Battle exists identically on both chains!")
    else:
        print(f"\nCROSS-CHAIN SYNC FAILED!")
        print(f"Battles do not match between chains.")

if __name__ == "__main__":
    verify_cross_chain_battle() 
    