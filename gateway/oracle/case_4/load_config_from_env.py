#!/usr/bin/env python3
"""
Helper script to load config with secrets from environment variables.
This prevents hardcoding secrets in config files.

Usage:
    export PRIVATE_KEY=0xYourPrivateKeyHere
    export ETH_ACCOUNT=0xYourAccountAddress
    python load_config_from_env.py config/config-template.json
"""

import json
import os
import sys

def load_config_with_env(config_path, output_path=None):
    """Load config file and replace placeholders with environment variables."""
    
    # Read the template config
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Get environment variables
    private_key = os.environ.get('PRIVATE_KEY')
    eth_account = os.environ.get('ETH_ACCOUNT')
    
    if not private_key:
        raise ValueError("PRIVATE_KEY environment variable not set!")
    if not eth_account:
        raise ValueError("ETH_ACCOUNT environment variable not set!")
    
    # Update the config with actual values
    if 'ccConfig' in config and 'oracleConfig' in config['ccConfig']:
        for oracle in config['ccConfig']['oracleConfig']:
            if 'signingCredential' in oracle:
                oracle['signingCredential']['ethAccount'] = eth_account
                oracle['signingCredential']['secret'] = private_key
    
    # Write to output file or return
    if output_path:
        with open(output_path, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"✅ Config written to: {output_path}")
    else:
        return config

def main():
    if len(sys.argv) < 2:
        print("Usage: python load_config_from_env.py <config-template-path> [output-path]")
        print("\nExample:")
        print("  export PRIVATE_KEY=0x...")
        print("  export ETH_ACCOUNT=0x...")
        print("  python load_config_from_env.py config/config-template.json config/config.json")
        sys.exit(1)
    
    config_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        load_config_with_env(config_path, output_path)
        print("✅ Config loaded successfully with environment variables")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

