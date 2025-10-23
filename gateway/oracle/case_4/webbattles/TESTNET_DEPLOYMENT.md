# Testnet Deployment Guide

This guide explains how to deploy WebBattles contracts to testnets (Sepolia and Base Sepolia).

## Prerequisites

1. **Get Testnet ETH**
   - Sepolia ETH: https://sepoliafaucet.com/
   - Base Sepolia ETH: https://www.alchemy.com/faucets/base-sepolia

2. **Install dotenv package**
   ```bash
   cd ../../../../EVM
   npm install dotenv
   ```

## Setup

1. **Create a `.env` file in the `EVM` directory**:
   ```bash
   cd ../../../../EVM
   touch .env
   ```

2. **Add your private keys to `.env`**:
   ```env
   # Required: Your wallet private keys (without 0x prefix)
   PRIVATE_KEY_SEPOLIA=your_sepolia_private_key_here
   PRIVATE_KEY_BASE=your_base_sepolia_private_key_here

   # Optional: Custom RPC URLs (defaults are provided)
   # SEPOLIA_RPC_URL=https://eth-sepolia.g.alchemy.com/v2/YOUR_API_KEY
   # BASE_SEPOLIA_RPC_URL=https://base-sepolia.g.alchemy.com/v2/YOUR_API_KEY
   ```

   **⚠️ SECURITY WARNING**: Never commit your `.env` file or share your private keys!

## Deployment

Run the testnet deployment script:

```bash
python3 deploy-contracts-testnet.py
```

This will:
1. Deploy the WebBattles contract to Sepolia
2. Deploy the WebBattles contract to Base Sepolia
3. Update your `config.py` with the new contract addresses
4. Display the deployment results

## Expected Output

```
DEPLOYING WEBBATTLES CONTRACTS TO TESTNETS
Deploying to Sepolia and Base Sepolia
============================================================

Deploying to sepolia
WebBattles deployed to: 0x...
sepolia deployment successful: 0x...

Deploying to baseSepolia
WebBattles deployed to: 0x...
baseSepolia deployment successful: 0x...

============================================================
DEPLOYMENT COMPLETE
============================================================
Sepolia:       0x...
Base Sepolia:  0x...
============================================================
```

## Verify Deployments

After deployment, you can verify your contracts on block explorers:

- **Sepolia**: https://sepolia.etherscan.io/address/YOUR_CONTRACT_ADDRESS
- **Base Sepolia**: https://sepolia.basescan.org/address/YOUR_CONTRACT_ADDRESS

## Network Information

- **Sepolia**
  - Chain ID: 11155111
  - RPC: https://rpc.sepolia.org
  - Explorer: https://sepolia.etherscan.io

- **Base Sepolia**
  - Chain ID: 84532
  - RPC: https://sepolia.base.org
  - Explorer: https://sepolia.basescan.org

## Troubleshooting

**Issue**: "Deployment failed"
- Check that your wallets have sufficient testnet ETH
- Verify your private keys are correct (without 0x prefix)
- Ensure RPC URLs are accessible

**Issue**: "accounts: process.env.PRIVATE_KEY_SEPOLIA ? [process.env.PRIVATE_KEY_SEPOLIA] : []"
- Make sure you installed dotenv: `npm install dotenv`
- Verify your `.env` file exists in the EVM directory
- Check that your `.env` file has no syntax errors

