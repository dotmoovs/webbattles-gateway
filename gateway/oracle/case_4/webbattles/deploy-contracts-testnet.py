#!/usr/bin/env python3

import subprocess
import os
import sys
from config_updater import update_multiple_config_variables

def deploy_to_chain(network_name):
    """Deploy WebBattles contract to a specific testnet"""
    
    print(f"\nDeploying to {network_name}")
    
    # Change to EVM directory
    evm_dir = os.path.join(os.path.dirname(__file__), "../../../../EVM")
    
    try:
        # Run the deployment
        result = subprocess.run([
            "npx", "hardhat", "run", "scripts/deploy-webbattles.js",
            "--network", network_name
        ], cwd=evm_dir, capture_output=True, text=True, check=True)
        
        print(result.stdout)
        
        # Extract contract address from output
        lines = result.stdout.split('\n')
        contract_address = None
        for line in lines:
            if "WebBattles deployed to:" in line:
                contract_address = line.split(": ")[1].strip()
                break
        
        if contract_address:
            print(f"{network_name} deployment successful: {contract_address}")
            return contract_address
        else:
            print(f"Could not extract contract address from output")
            return None
            
    except subprocess.CalledProcessError as e:
        print(f"Deployment failed: {e.stderr}")
        return None

def deploy_testnets():
    """Deploy contracts to Sepolia and Base Sepolia testnets"""
    
    print("DEPLOYING WEBBATTLES CONTRACTS TO TESTNETS")
    print("Deploying to Sepolia and Base Sepolia")
    print("=" * 60)
    
    # Deploy to both testnets
    sepolia_address = deploy_to_chain("sepolia")
    base_sepolia_address = deploy_to_chain("baseSepolia")
    
    if sepolia_address and base_sepolia_address:
        print(f"\n" + "=" * 60)
        print(f"DEPLOYMENT COMPLETE")
        print(f"=" * 60)
        print(f"Sepolia:       {sepolia_address}")
        print(f"Base Sepolia:  {base_sepolia_address}")
        print(f"=" * 60)
        
        # Update config with both addresses
        print(f"\nUpdating config.py")
        update_multiple_config_variables({
            'CONTRACT_CHAIN_1': sepolia_address,
            'CONTRACT_CHAIN_2': base_sepolia_address
        })
        
        print("\nIMPORTANT: Update your .env file with:")
        print(f"  SEPOLIA_CONTRACT={sepolia_address}")
        print(f"  BASE_SEPOLIA_CONTRACT={base_sepolia_address}")
        
        return True
    else:
        print(f"\n" + "=" * 60)
        print(f"DEPLOYMENT FAILED")
        print(f"=" * 60)
        print("One or more deployments failed.")
        print("Please check:")
        print("  1. Your .env file has PRIVATE_KEY_SEPOLIA and PRIVATE_KEY_BASE")
        print("  2. Your wallets have sufficient testnet ETH")
        print("  3. RPC URLs are working")
        return False

if __name__ == "__main__":
    success = deploy_testnets()
    sys.exit(0 if success else 1)

