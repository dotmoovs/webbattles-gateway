#!/usr/bin/env python3

import json
import os
from dotenv import load_dotenv
from web3 import Web3

def configure_gateway_for_testnet():
    """Configure the gateway config for testnet deployment"""
    
    print("GATEWAY TESTNET CONFIGURATION")
    print("=" * 60)
    
    # Load environment variables
    env_path = os.path.join(os.path.dirname(__file__), "../../../EVM/.env")
    load_dotenv(env_path)
    
    # Get private keys from env
    private_key_sepolia = os.getenv("PRIVATE_KEY_SEPOLIA")
    private_key_base = os.getenv("PRIVATE_KEY_BASE")
    
    if not private_key_sepolia or not private_key_base:
        print("ERROR: Private keys not found in .env file")
        print("Please ensure EVM/.env contains:")
        print("  PRIVATE_KEY_SEPOLIA=your_key")
        print("  PRIVATE_KEY_BASE=your_key")
        return False
    
    # Add 0x prefix if not present
    if not private_key_sepolia.startswith('0x'):
        private_key_sepolia = '0x' + private_key_sepolia
    if not private_key_base.startswith('0x'):
        private_key_base = '0x' + private_key_base
    
    # Get wallet addresses from private keys
    account_sepolia = Web3().eth.account.from_key(private_key_sepolia)
    account_base = Web3().eth.account.from_key(private_key_base)
    
    print(f"Sepolia Account: {account_sepolia.address}")
    print(f"Base Account: {account_base.address}")
    
    # Load the template config
    config_path = os.path.join(os.path.dirname(__file__), "config/config-testnet.json")
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Update with actual values
    config['ccConfig']['oracleConfig'][0]['signingCredential']['ethAccount'] = account_sepolia.address
    config['ccConfig']['oracleConfig'][0]['signingCredential']['secret'] = private_key_sepolia
    
    config['ccConfig']['oracleConfig'][1]['signingCredential']['ethAccount'] = account_base.address
    config['ccConfig']['oracleConfig'][1]['signingCredential']['secret'] = private_key_base
    
    # Save the configured file
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print("\n✅ Gateway configuration updated!")
    print(f"Configuration saved to: {config_path}")
    
    # Now copy to the actual config location
    actual_config_path = os.path.join(os.path.dirname(__file__), "config/config.json")
    backup_path = os.path.join(os.path.dirname(__file__), "config/config-local-backup.json")
    
    # Backup the local config
    if os.path.exists(actual_config_path):
        with open(actual_config_path, 'r') as f:
            local_config = f.read()
        with open(backup_path, 'w') as f:
            f.write(local_config)
        print(f"✅ Local config backed up to: config-local-backup.json")
    
    # Copy testnet config to active config
    with open(config_path, 'r') as f:
        testnet_config = f.read()
    with open(actual_config_path, 'w') as f:
        f.write(testnet_config)
    
    print(f"✅ Testnet config activated in: config.json")
    print("\n" + "=" * 60)
    print("Gateway is now configured for Sepolia and Base Sepolia!")
    print("You can now run: docker-compose up -d")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    import sys
    success = configure_gateway_for_testnet()
    sys.exit(0 if success else 1)

