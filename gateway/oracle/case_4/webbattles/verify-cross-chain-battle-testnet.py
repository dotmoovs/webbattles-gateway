#!/usr/bin/env python3

from web3 import Web3
import json
import sys
import os

# Import from config.py
sys.path.insert(0, os.path.dirname(__file__))
from config import CONTRACT_CHAIN_1, CONTRACT_CHAIN_2, CONTRACT_ARTIFACTS_PATH, LAST_BATTLE_ID

# Testnet configuration
CHAIN_1_RPC = "https://ethereum-sepolia-rpc.publicnode.com"  # Sepolia
CHAIN_2_RPC = "https://sepolia.base.org"  # Base Sepolia

def verify_cross_chain_battle_testnet():
    """Verify that a battle is synced between Sepolia and Base Sepolia"""
    
    print("CROSS-CHAIN BATTLE VERIFICATION (TESTNET)")
    print("=" * 60)
    
    if not LAST_BATTLE_ID:
        print("ERROR: No battle ID configured in config.py")
        print("Run simple-battle-test-testnet.py first to create a battle")
        return False
    
    # Connect to both chains
    w3_sepolia = Web3(Web3.HTTPProvider(CHAIN_1_RPC))
    w3_base = Web3(Web3.HTTPProvider(CHAIN_2_RPC))
    
    print(f"Sepolia Connected: {'✅' if w3_sepolia.is_connected() else '❌'}")
    print(f"Base Sepolia Connected: {'✅' if w3_base.is_connected() else '❌'}")
    
    if not w3_sepolia.is_connected() or not w3_base.is_connected():
        print("\nERROR: Could not connect to testnets")
        return False
    
    # Load contract ABI
    with open(CONTRACT_ARTIFACTS_PATH, 'r') as file:
        contract_data = json.load(file)
    abi = contract_data["abi"]
    
    # Create contract instances
    contract_sepolia = w3_sepolia.eth.contract(address=CONTRACT_CHAIN_1, abi=abi)
    contract_base = w3_base.eth.contract(address=CONTRACT_CHAIN_2, abi=abi)
    
    print(f"\nChecking battle ID: {LAST_BATTLE_ID}")
    print(f"Sepolia Contract: {CONTRACT_CHAIN_1}")
    print(f"Base Contract: {CONTRACT_CHAIN_2}")
    print(f"\n" + "-" * 60)
    
    try:
        # Get battle from Sepolia
        print(f"Fetching battle from Sepolia...")
        battle_sepolia = contract_sepolia.functions.getBattle(LAST_BATTLE_ID).call()
        
        print(f"\n📍 SEPOLIA BATTLE:")
        print(f"  Battle ID: {battle_sepolia[0].hex()}")
        print(f"  Challenger: {battle_sepolia[1]}")
        print(f"  Opponent: {battle_sepolia[2]}")
        print(f"  Bet Amount: {battle_sepolia[3] / 1e18} ETH")
        print(f"  Status: {battle_sepolia[4]}")
        print(f"  Winner: {battle_sepolia[5]}")
        print(f"  Created At: {battle_sepolia[6]}")
        print(f"  Battle Type: {battle_sepolia[8]}")
        print(f"  View: https://sepolia.etherscan.io/address/{CONTRACT_CHAIN_1}")
        
    except Exception as e:
        print(f"❌ Error fetching battle from Sepolia: {e}")
        battle_sepolia = None
    
    try:
        # Get battle from Base
        print(f"\nFetching battle from Base Sepolia...")
        battle_base = contract_base.functions.getBattle(LAST_BATTLE_ID).call()
        
        print(f"\n📍 BASE SEPOLIA BATTLE:")
        print(f"  Battle ID: {battle_base[0].hex()}")
        print(f"  Challenger: {battle_base[1]}")
        print(f"  Opponent: {battle_base[2]}")
        print(f"  Bet Amount: {battle_base[3] / 1e18} ETH")
        print(f"  Status: {battle_base[4]}")
        print(f"  Winner: {battle_base[5]}")
        print(f"  Created At: {battle_base[6]}")
        print(f"  Battle Type: {battle_base[8]}")
        print(f"  View: https://sepolia.basescan.org/address/{CONTRACT_CHAIN_2}")
        
    except Exception as e:
        print(f"❌ Error fetching battle from Base: {e}")
        battle_base = None
    
    # Compare battles
    print(f"\n" + "=" * 60)
    
    if battle_sepolia and battle_base:
        # Check if battles match
        battle_id_match = battle_sepolia[0] == battle_base[0]
        challenger_match = battle_sepolia[1] == battle_base[1]
        bet_amount_match = battle_sepolia[3] == battle_base[3]
        status_match = battle_sepolia[4] == battle_base[4]
        battle_type_match = battle_sepolia[8] == battle_base[8]
        
        all_match = all([battle_id_match, challenger_match, bet_amount_match, status_match, battle_type_match])
        
        if all_match:
            print(f"✅ CROSS-CHAIN SYNC SUCCESSFUL!")
            print(f"Battle exists identically on both Sepolia and Base Sepolia!")
            print(f"\nMatching fields:")
            print(f"  ✅ Battle ID")
            print(f"  ✅ Challenger")
            print(f"  ✅ Bet Amount")
            print(f"  ✅ Status")
            print(f"  ✅ Battle Type")
        else:
            print(f"⚠️  PARTIAL SYNC")
            print(f"\nField comparison:")
            print(f"  {'✅' if battle_id_match else '❌'} Battle ID")
            print(f"  {'✅' if challenger_match else '❌'} Challenger")
            print(f"  {'✅' if bet_amount_match else '❌'} Bet Amount")
            print(f"  {'✅' if status_match else '❌'} Status")
            print(f"  {'✅' if battle_type_match else '❌'} Battle Type")
        
        print(f"=" * 60)
        return all_match
        
    elif battle_sepolia and not battle_base:
        print(f"⚠️  Battle exists on Sepolia but NOT on Base Sepolia")
        print(f"The oracle has not synced this battle yet.")
        print(f"=" * 60)
        return False
        
    elif battle_base and not battle_sepolia:
        print(f"⚠️  Battle exists on Base Sepolia but NOT on Sepolia")
        print(f"=" * 60)
        return False
        
    else:
        print(f"❌ Battle not found on either chain")
        print(f"=" * 60)
        return False

if __name__ == "__main__":
    success = verify_cross_chain_battle_testnet()
    sys.exit(0 if success else 1)

