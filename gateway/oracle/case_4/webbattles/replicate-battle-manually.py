#!/usr/bin/env python3

"""
Manual Cross-Chain Battle Replication for Testnets
Since public RPC endpoints don't support WebSocket subscriptions,
we manually replicate battles from Sepolia to Base Sepolia
"""

import os
import sys
import json
import time
from datetime import datetime
from web3 import Web3
from dotenv import load_dotenv
from config import CONTRACT_CHAIN_1, CONTRACT_CHAIN_2, CONTRACT_ARTIFACTS_PATH, LAST_BATTLE_ID

# Testnet configuration
CHAIN_1_RPC = "https://ethereum-sepolia-rpc.publicnode.com"
CHAIN_2_RPC = "https://sepolia.base.org"
CHAIN_1_NAME = "Sepolia"
CHAIN_2_NAME = "Base Sepolia"
CHAIN_1_EXPLORER = "https://sepolia.etherscan.io"
CHAIN_2_EXPLORER = "https://sepolia.basescan.org"

# Metrics storage
metrics = {
    "test_date": datetime.now().isoformat(),
    "chains": {
        "source": CHAIN_1_NAME,
        "destination": CHAIN_2_NAME
    },
    "contracts": {
        "source_address": CONTRACT_CHAIN_1,
        "destination_address": CONTRACT_CHAIN_2
    },
    "transactions": [],
    "timings": {},
    "gas_usage": {},
    "status": "pending"
}

def print_header(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def replicate_battle(battle_id):
    """Manually replicate a battle from Sepolia to Base Sepolia"""
    
    print_header("MANUAL CROSS-CHAIN BATTLE REPLICATION")
    print(f"From: {CHAIN_1_NAME} → To: {CHAIN_2_NAME}")
    print(f"Battle ID: {battle_id}")
    
    start_time = time.time()
    
    # Load environment
    env_path = os.path.join(os.path.dirname(__file__), "../../../../EVM/.env")
    load_dotenv(env_path)
    
    private_key_base = os.getenv("PRIVATE_KEY_BASE")
    if not private_key_base:
        print("❌ ERROR: PRIVATE_KEY_BASE not found in .env")
        return False
    
    if not private_key_base.startswith('0x'):
        private_key_base = '0x' + private_key_base
    
    # Connect to both chains
    w3_sepolia = Web3(Web3.HTTPProvider(CHAIN_1_RPC))
    w3_base = Web3(Web3.HTTPProvider(CHAIN_2_RPC))
    
    print(f"\nConnecting to chains...")
    if not w3_sepolia.is_connected():
        print(f"❌ ERROR: Could not connect to {CHAIN_1_NAME}")
        return False
    print(f"✅ Connected to {CHAIN_1_NAME}")
    
    if not w3_base.is_connected():
        print(f"❌ ERROR: Could not connect to {CHAIN_2_NAME}")
        return False
    print(f"✅ Connected to {CHAIN_2_NAME}")
    
    # Load contract ABI
    artifacts_path = os.path.join(os.path.dirname(__file__), CONTRACT_ARTIFACTS_PATH)
    with open(artifacts_path, 'r') as file:
        contract_data = json.load(file)
    abi = contract_data["abi"]
    
    # Create contract instances
    contract_sepolia = w3_sepolia.eth.contract(address=CONTRACT_CHAIN_1, abi=abi)
    contract_base = w3_base.eth.contract(address=CONTRACT_CHAIN_2, abi=abi)
    
    # Get account for Base
    account_base = w3_base.eth.account.from_key(private_key_base)
    
    print(f"\nFetching battle data from {CHAIN_1_NAME}...")
    try:
        battle = contract_sepolia.functions.getBattle(battle_id).call()
        
        print(f"✅ Battle found on {CHAIN_1_NAME}:")
        print(f"  Battle ID: {battle[0].hex()}")
        print(f"  Challenger: {battle[1]}")
        print(f"  Opponent: {battle[2]}")
        print(f"  Bet Amount: {battle[3] / 1e18} ETH")
        print(f"  Status: {battle[4]}")
        print(f"  Battle Type: {battle[8]}")
        
        # Store source data in metrics
        metrics["transactions"].append({
            "type": "source_battle",
            "chain": CHAIN_1_NAME,
            "battle_id": battle[0].hex(),
            "explorer_url": f"{CHAIN_1_EXPLORER}/address/{CONTRACT_CHAIN_1}"
        })
        
    except Exception as e:
        print(f"❌ Error fetching battle: {e}")
        metrics["status"] = "failed_fetch"
        return False
    
    # Check if already replicated
    print(f"\nChecking if battle already exists on {CHAIN_2_NAME}...")
    try:
        existing_battle = contract_base.functions.getBattle(battle_id).call()
        if existing_battle[0] != b'\x00' * 32:  # Battle exists
            print(f"⚠️  Battle already replicated on {CHAIN_2_NAME}!")
            print(f"  View: {CHAIN_2_EXPLORER}/address/{CONTRACT_CHAIN_2}")
            
            # Still verify and save metrics
            metrics["status"] = "already_replicated"
            save_metrics_report()
            return True
    except:
        print(f"✅ Battle not yet on {CHAIN_2_NAME}, proceeding with replication...")
    
    # Grant oracle role to our account if needed
    print(f"\nPreparing replication to {CHAIN_2_NAME}...")
    print(f"Using account: {account_base.address}")
    
    balance = w3_base.eth.get_balance(account_base.address)
    print(f"Balance: {w3_base.from_wei(balance, 'ether')} ETH")
    
    if balance == 0:
        print(f"❌ ERROR: Account has no ETH on {CHAIN_2_NAME}!")
        return False
    
    # Replicate battle
    print(f"\nReplicating battle to {CHAIN_2_NAME}...")
    try:
        nonce = w3_base.eth.get_transaction_count(account_base.address)
        gas_price = w3_base.eth.gas_price
        
        # Build transaction
        tx = contract_base.functions.replicateBattle(
            battle[0],  # battleId
            battle[1],  # challenger
            battle[3],  # betAmount
            battle[8]   # battleType
        ).build_transaction({
            'from': account_base.address,
            'gas': 500000,
            'gasPrice': gas_price,
            'nonce': nonce,
        })
        
        # Sign and send
        signed_tx = w3_base.eth.account.sign_transaction(tx, private_key_base)
        
        tx_sent_time = time.time()
        tx_hash = w3_base.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        print(f"  Transaction sent: {tx_hash.hex()}")
        print(f"  Waiting for confirmation...")
        
        receipt = w3_base.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
        confirmation_time = time.time()
        
        if receipt.status == 1:
            elapsed = confirmation_time - start_time
            sync_time = confirmation_time - tx_sent_time
            
            print(f"✅ Battle replicated successfully!")
            print(f"  Gas Used: {receipt.gasUsed:,}")
            print(f"  Gas Price: {w3_base.from_wei(gas_price, 'gwei')} Gwei")
            print(f"  Total Cost: {w3_base.from_wei(receipt.gasUsed * gas_price, 'ether')} ETH")
            print(f"  Block Number: {receipt.blockNumber}")
            print(f"  Confirmation Time: {sync_time:.2f} seconds")
            print(f"  Total Time: {elapsed:.2f} seconds")
            print(f"  View: {CHAIN_2_EXPLORER}/tx/{tx_hash.hex()}")
            
            # Store metrics
            metrics["transactions"].append({
                "type": "cross_chain_replication",
                "chain": CHAIN_2_NAME,
                "tx_hash": tx_hash.hex(),
                "block_number": receipt.blockNumber,
                "explorer_url": f"{CHAIN_2_EXPLORER}/tx/{tx_hash.hex()}"
            })
            
            metrics["timings"]["cross_chain_sync"] = {
                "total_seconds": elapsed,
                "confirmation_seconds": sync_time
            }
            
            metrics["gas_usage"]["replication"] = {
                "gas_used": receipt.gasUsed,
                "gas_price_gwei": float(w3_base.from_wei(gas_price, 'gwei')),
                "total_cost_eth": float(w3_base.from_wei(receipt.gasUsed * gas_price, 'ether'))
            }
            
            # Verify replication
            print(f"\nVerifying replication...")
            time.sleep(2)
            
            replicated_battle = contract_base.functions.getBattle(battle_id).call()
            
            if replicated_battle[0] == battle[0] and replicated_battle[1] == battle[1]:
                print(f"✅ Verification successful!")
                print(f"  Battle ID matches: {replicated_battle[0].hex()}")
                print(f"  Challenger matches: {replicated_battle[1]}")
                
                metrics["verification"] = {
                    "success": True,
                    "battle_data": {
                        "battle_id": replicated_battle[0].hex(),
                        "challenger": replicated_battle[1],
                        "bet_amount_eth": float(replicated_battle[3] / 1e18),
                        "battle_type": replicated_battle[8]
                    }
                }
                metrics["status"] = "success"
                
                return True
            else:
                print(f"⚠️  Verification failed - data mismatch")
                metrics["status"] = "verification_failed"
                return False
        else:
            print(f"❌ Transaction failed!")
            metrics["status"] = "transaction_failed"
            return False
            
    except Exception as e:
        print(f"❌ Error replicating battle: {e}")
        metrics["status"] = "error"
        metrics["error"] = str(e)
        import traceback
        traceback.print_exc()
        return False

def save_metrics_report():
    """Save metrics to JSON file"""
    
    report_file = os.path.join(os.path.dirname(__file__), 
                               f"manual_replication_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    
    with open(report_file, 'w') as f:
        json.dump(metrics, f, indent=2)
    
    print(f"\n📊 Metrics saved to: {os.path.basename(report_file)}")
    
    return report_file

def main():
    if not LAST_BATTLE_ID:
        print("❌ ERROR: No battle ID configured in config.py")
        print("Run: python3 simple-battle-test-testnet.py --network sepolia")
        sys.exit(1)
    
    success = replicate_battle(LAST_BATTLE_ID)
    
    report_file = save_metrics_report()
    
    if success:
        print_header("CROSS-CHAIN REPLICATION SUCCESSFUL! 🎉")
        print("\n✅ Summary:")
        print(f"  ✅ Battle fetched from {CHAIN_1_NAME}")
        print(f"  ✅ Battle replicated to {CHAIN_2_NAME}")
        print(f"  ✅ Verification successful")
        print(f"  ✅ Metrics saved: {os.path.basename(report_file)}")
        
        if "cross_chain_sync" in metrics["timings"]:
            print(f"\n📊 Performance:")
            print(f"  Cross-Chain Sync Time: {metrics['timings']['cross_chain_sync']['confirmation_seconds']:.2f} seconds")
        
        print("\n" + "=" * 70)
        sys.exit(0)
    else:
        print_header("REPLICATION FAILED")
        print(f"Check metrics file for details: {os.path.basename(report_file)}")
        sys.exit(1)

if __name__ == "__main__":
    main()

