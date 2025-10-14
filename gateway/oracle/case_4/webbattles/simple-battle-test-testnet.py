#!/usr/bin/env python3

from web3 import Web3
import json
import os
from dotenv import load_dotenv
from config_updater import update_config_variable

# Import testnet config
import sys
sys.path.insert(0, os.path.dirname(__file__))
from config import CONTRACT_CHAIN_1, CONTRACT_CHAIN_2, CONTRACT_ARTIFACTS_PATH

# Testnet configuration
CHAIN_1_RPC = "https://ethereum-sepolia-rpc.publicnode.com"
CHAIN_2_RPC = "https://sepolia.base.org"

def create_battle_testnet(network="sepolia"):
    """Create a battle on testnet (sepolia or base)"""
    
    print(f"WEBBATTLES TESTNET BATTLE CREATION")
    print("=" * 60)
    
    # Load environment variables
    env_path = os.path.join(os.path.dirname(__file__), "../../../../EVM/.env")
    load_dotenv(env_path)
    
    # Select network
    if network.lower() == "sepolia":
        rpc_url = CHAIN_1_RPC
        contract_address = CONTRACT_CHAIN_1
        private_key = os.getenv("PRIVATE_KEY_SEPOLIA")
        network_name = "Sepolia"
    else:  # base
        rpc_url = CHAIN_2_RPC
        contract_address = CONTRACT_CHAIN_2
        private_key = os.getenv("PRIVATE_KEY_BASE")
        network_name = "Base Sepolia"
    
    if not private_key:
        print(f"ERROR: Private key not found in .env file")
        print(f"Please add PRIVATE_KEY_SEPOLIA or PRIVATE_KEY_BASE to EVM/.env")
        return None
    
    # Connect to network
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    
    if not w3.is_connected():
        print(f"ERROR: Could not connect to {network_name}")
        return None
    
    print(f"Network: {network_name}")
    print(f"Connected: ✅")
    print(f"Chain ID: {w3.eth.chain_id}")
    
    # Load contract
    with open(CONTRACT_ARTIFACTS_PATH, 'r') as file:
        contract_data = json.load(file)
    abi = contract_data["abi"]
    
    contract = w3.eth.contract(address=contract_address, abi=abi)
    
    # Get account from private key
    account = w3.eth.account.from_key(private_key)
    print(f"Account: {account.address}")
    
    # Check balance
    balance = w3.eth.get_balance(account.address)
    print(f"Balance: {w3.from_wei(balance, 'ether')} ETH")
    
    if balance == 0:
        print(f"\nERROR: Account has no ETH!")
        print(f"Get testnet ETH from:")
        if network.lower() == "sepolia":
            print(f"  - https://sepoliafaucet.com/")
        else:
            print(f"  - https://www.alchemy.com/faucets/base-sepolia")
        return None
    
    # Battle parameters
    bet_amount = w3.to_wei(0.01, 'ether')  # 0.01 ETH for testnet
    battle_type = "Football Freestyle"
    
    print(f"\n" + "-" * 60)
    print(f"Creating battle on {network_name}...")
    print(f"Bet Amount: {w3.from_wei(bet_amount, 'ether')} ETH")
    print(f"Battle Type: {battle_type}")
    print(f"-" * 60)
    
    try:
        # Build transaction
        nonce = w3.eth.get_transaction_count(account.address)
        
        tx = contract.functions.createBattle(battle_type).build_transaction({
            'from': account.address,
            'value': bet_amount,
            'gas': 500000,
            'gasPrice': w3.eth.gas_price,
            'nonce': nonce,
        })
        
        # Sign transaction
        signed_tx = w3.eth.account.sign_transaction(tx, private_key)
        
        # Send transaction
        print(f"Sending transaction...")
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        print(f"Transaction Hash: {tx_hash.hex()}")
        
        # Wait for receipt
        print(f"Waiting for confirmation...")
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
        
        if receipt.status == 1:
            print(f"✅ Transaction confirmed!")
            print(f"Gas Used: {receipt.gasUsed:,}")
            
            # Parse logs to find BattleCreated event
            battle_id = None
            for log in receipt.logs:
                try:
                    decoded_log = contract.events.BattleCreated().process_log(log)
                    battle_id = decoded_log['args']['battleId'].hex()
                    break
                except:
                    continue
            
            if battle_id:
                print(f"\n" + "=" * 60)
                print(f"BATTLE CREATED SUCCESSFULLY!")
                print(f"=" * 60)
                print(f"Battle ID: {battle_id}")
                print(f"Network: {network_name}")
                print(f"Contract: {contract_address}")
                print(f"Transaction: {tx_hash.hex()}")
                
                # View on explorer
                if network.lower() == "sepolia":
                    print(f"View on Etherscan: https://sepolia.etherscan.io/tx/{tx_hash.hex()}")
                else:
                    print(f"View on BaseScan: https://sepolia.basescan.org/tx/{tx_hash.hex()}")
                
                print(f"=" * 60)
                
                # Update config with battle ID
                print(f"\nUpdating config.py with battle ID...")
                battle_id_with_prefix = battle_id if battle_id.startswith('0x') else f'0x{battle_id}'
                update_config_variable('LAST_BATTLE_ID', battle_id_with_prefix)
                
                return battle_id
            else:
                print(f"❌ Could not extract battle ID from logs")
                return None
        else:
            print(f"❌ Transaction failed!")
            return None
            
    except Exception as e:
        print(f"❌ Error creating battle: {e}")
        return None

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Create a battle on testnet')
    parser.add_argument('--network', choices=['sepolia', 'base'], default='sepolia',
                      help='Network to create battle on (default: sepolia)')
    args = parser.parse_args()
    
    battle_id = create_battle_testnet(args.network)
    
    if battle_id:
        print(f"\n✅ Battle creation successful!")
        print(f"\nNext steps:")
        print(f"  1. Register the oracle to sync between chains")
        print(f"  2. Execute oracle to replicate battle to other chain")
        print(f"  3. Use verify-cross-chain-battle.py to verify sync")
    else:
        print(f"\n❌ Battle creation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()

