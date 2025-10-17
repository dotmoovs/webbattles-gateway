#!/usr/bin/env python3
"""
Grant ORACLE_ROLE to a specific address on both contracts
"""

from web3 import Web3
import json
import sys
import time

# Configuration
SEPOLIA_RPC = "https://ethereum-sepolia-rpc.publicnode.com"
BASE_SEPOLIA_RPC = "https://sepolia.base.org"

CONTRACT_SEPOLIA = "0x17c3468D98b00bf24B6Bc1c67508d5D568E20cC6"
CONTRACT_BASE = "0xF3a5cd8F0cA7D6BdfD8b36B04A951626Aa7DEDf1"

# Admin private key (has DEFAULT_ADMIN_ROLE - the actual deployer)
ADMIN_PRIVATE_KEY = "puthereprivatekey"

# Address to grant ORACLE_ROLE to
ORACLE_ADDRESS = "0x1C0E28416f8f60358017529ff2752dB4bbc2e5bB"

# ORACLE_ROLE hash
ORACLE_ROLE = Web3.keccak(text="ORACLE_ROLE")

# Contract ABI (only need grantRole and hasRole)
ABI = [
    {
        "inputs": [{"internalType": "bytes32", "name": "role", "type": "bytes32"}, 
                   {"internalType": "address", "name": "account", "type": "address"}],
        "name": "grantRole",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "bytes32", "name": "role", "type": "bytes32"}, 
                   {"internalType": "address", "name": "account", "type": "address"}],
        "name": "hasRole",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "view",
        "type": "function"
    }
]

def grant_role_on_chain(chain_name, rpc_url, contract_address):
    """Grant ORACLE_ROLE on a specific chain"""
    print(f"\n{'='*70}")
    print(f"  {chain_name}")
    print(f"{'='*70}")
    
    # Connect to chain
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    
    if not w3.is_connected():
        print(f"❌ Failed to connect to {chain_name}")
        return False
    
    print(f"✅ Connected to {chain_name}")
    
    # Load contract
    contract = w3.eth.contract(address=Web3.to_checksum_address(contract_address), abi=ABI)
    
    # Load admin account
    admin = w3.eth.account.from_key(ADMIN_PRIVATE_KEY)
    print(f"   Admin: {admin.address}")
    
    # Check if role already granted
    has_role = contract.functions.hasRole(ORACLE_ROLE, Web3.to_checksum_address(ORACLE_ADDRESS)).call()
    
    if has_role:
        print(f"✅ {ORACLE_ADDRESS} already has ORACLE_ROLE")
        return True
    
    print(f"⚠️  {ORACLE_ADDRESS} does NOT have ORACLE_ROLE")
    print(f"   Granting role...")
    
    try:
        # Build transaction
        nonce = w3.eth.get_transaction_count(admin.address)
        gas_price = w3.eth.gas_price
        
        tx = contract.functions.grantRole(ORACLE_ROLE, Web3.to_checksum_address(ORACLE_ADDRESS)).build_transaction({
            'from': admin.address,
            'gas': 100000,
            'gasPrice': gas_price,
            'nonce': nonce,
        })
        
        # Sign and send
        signed_tx = w3.eth.account.sign_transaction(tx, ADMIN_PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        print(f"   TX sent: {tx_hash.hex()}")
        print(f"   Waiting for confirmation...")
        
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
        
        if receipt.status == 1:
            print(f"✅ ORACLE_ROLE granted successfully!")
            print(f"   Gas used: {receipt.gasUsed:,}")
            
            # Verify
            has_role = contract.functions.hasRole(ORACLE_ROLE, Web3.to_checksum_address(ORACLE_ADDRESS)).call()
            if has_role:
                print(f"✅ Verified: {ORACLE_ADDRESS} now has ORACLE_ROLE")
                return True
            else:
                print(f"⚠️  Warning: Role grant succeeded but verification failed")
                return False
        else:
            print(f"❌ Transaction failed (status=0)")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("="*70)
    print("  GRANT ORACLE_ROLE TO ADDRESS")
    print("="*70)
    print(f"\nTarget Address: {ORACLE_ADDRESS}")
    print(f"ORACLE_ROLE Hash: {ORACLE_ROLE.hex()}")
    
    # Grant on Sepolia
    sepolia_success = grant_role_on_chain("Sepolia", SEPOLIA_RPC, CONTRACT_SEPOLIA)
    
    time.sleep(2)
    
    # Grant on Base Sepolia
    base_success = grant_role_on_chain("Base Sepolia", BASE_SEPOLIA_RPC, CONTRACT_BASE)
    
    # Summary
    print(f"\n{'='*70}")
    print(f"  SUMMARY")
    print(f"{'='*70}")
    print(f"Sepolia:       {'✅ Success' if sepolia_success else '❌ Failed'}")
    print(f"Base Sepolia:  {'✅ Success' if base_success else '❌ Failed'}")
    
    if sepolia_success and base_success:
        print(f"\n✅ All done! {ORACLE_ADDRESS} now has ORACLE_ROLE on both chains!")
        print(f"\nYou can now run tests successfully! 🎉")
        return 0
    else:
        print(f"\n⚠️  Some operations failed. Check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
