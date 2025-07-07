#!/usr/bin/env python3

import subprocess
import os
import sys
from config_updater import update_multiple_config_variables

def deploy_to_chain(network_name, port):
    """Deploy WebBattles contract to a specific chain"""
    
    print(f"\nDeploying to {network_name} (port {port})")
    
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

def deploy_both_chains():
    """Deploy contracts to both chains and update config"""
    
    print("DEPLOYING WEBBATTLES CONTRACTS")
    print("Deploying to both chains and updating config.py")
    
    # Deploy to both chains
    chain1_address = deploy_to_chain("hardhat1", 8545)
    chain2_address = deploy_to_chain("hardhat2", 8546)
    
    if chain1_address and chain2_address:
        print(f"\nUpdating config.py")
        
        # Update config with both addresses
        update_multiple_config_variables({
            'CONTRACT_CHAIN_1': chain1_address,
            'CONTRACT_CHAIN_2': chain2_address
        })
        
        print(f"\nDEPLOYMENT COMPLETE")
        print(f"Chain 1: {chain1_address}")
        print(f"Chain 2: {chain2_address}")
        
        return True
    else:
        print(f"\nDEPLOYMENT FAILED")
        print("One or more deployments failed.")
        return False

if __name__ == "__main__":
    success = deploy_both_chains()
    sys.exit(0 if success else 1) 