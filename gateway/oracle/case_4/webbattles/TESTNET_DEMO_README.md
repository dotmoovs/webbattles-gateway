# WebBattles Cross-Chain Testnet Demo

This demo shows how to create a battle on Sepolia and automatically sync it to Base Sepolia using the SATP cross-chain oracle.

## Prerequisites

✅ Contracts deployed to Sepolia and Base Sepolia  
✅ `.env` file configured with private keys  
✅ Testnet ETH in your wallet  
✅ Docker Desktop running  

## Quick Start (Automated Demo)

### 1. Start the Gateway

```bash
cd /Users/hugoduarte/Desktop/Dotmoovs/webbattles-gateway/gateway/oracle/case_4
./start-gateway.sh
```

This will:
- Start the SATP gateway in Docker
- Wait for it to be ready
- Show you when it's ready to use

### 2. Run the Full Demo

```bash
cd webbattles
python3 run-full-testnet-demo.py
```

This single script will:
1. ✅ Check if the gateway is running
2. ✅ Create a battle on Sepolia testnet
3. ✅ Register the cross-chain oracle
4. ✅ Execute the sync to Base Sepolia
5. ✅ Verify the battle exists on both chains

## What You'll See

```
======================================================================
  WEBBATTLES CROSS-CHAIN TESTNET DEMO
======================================================================
Networks: Sepolia ↔️  Base Sepolia

──────────────────────────────────────────────────────────────────────
STEP 1: Checking SATP Gateway Status
──────────────────────────────────────────────────────────────────────
✅ Gateway is running!

──────────────────────────────────────────────────────────────────────
STEP 2: Creating Battle on Sepolia
──────────────────────────────────────────────────────────────────────
✅ Connected to Sepolia
Account: 0x3Be45D4851C74b0CA97089d73e7b95D9385505b0
Balance: 0.109 ETH

Creating battle...
  Transaction sent: 0x...
  Waiting for confirmation...
✅ Battle created successfully!
  Battle ID: 0x...
  Gas Used: 125,432

──────────────────────────────────────────────────────────────────────
STEP 3: Registering Oracle
──────────────────────────────────────────────────────────────────────
Registering sync task (Sepolia listener)...
✅ Sync task registered: abc-123...
Registering replication task (Base Sepolia writer)...
✅ Replication task registered: def-456...

──────────────────────────────────────────────────────────────────────
STEP 4: Executing Cross-Chain Sync
──────────────────────────────────────────────────────────────────────
Fetching battle data from Sepolia...
Syncing battle to Base Sepolia...
  Battle ID: 0x...
  Challenger: 0x3Be45D4851C74b0CA97089d73e7b95D9385505b0
  Bet Amount: 0.01 ETH
✅ Cross-chain sync executed successfully!

──────────────────────────────────────────────────────────────────────
STEP 5: Verifying Cross-Chain Sync
──────────────────────────────────────────────────────────────────────
Checking Sepolia...
✅ Battle found on Sepolia

Checking Base Sepolia...
✅ Battle found on Base Sepolia

Comparison:
  Battle ID: ✅
  Challenger: ✅
  Bet Amount: ✅

🎉 CROSS-CHAIN SYNC SUCCESSFUL!

======================================================================
  DEMO COMPLETED SUCCESSFULLY! 🎉
======================================================================

You have successfully:
  ✅ Created a battle on Sepolia
  ✅ Registered cross-chain oracle
  ✅ Synced battle to Base Sepolia
  ✅ Verified cross-chain consistency
```

## Individual Scripts

If you want to run steps manually:

### Create a Battle
```bash
python3 simple-battle-test-testnet.py --network sepolia
```

### Verify Cross-Chain Sync
```bash
python3 verify-cross-chain-battle-testnet.py
```

## Troubleshooting

**Gateway not starting?**
- Make sure Docker Desktop is running
- Check logs: `docker compose logs -f`

**Battle creation fails?**
- Make sure you have testnet ETH
- Check your .env file has the correct private key

**Sync fails?**
- Make sure gateway is running
- Check gateway logs for errors
- Ensure both networks are accessible

## Deployed Contracts

- **Sepolia**: `0x17c3468D98b00bf24B6Bc1c67508d5D568E20cC6`
- **Base Sepolia**: `0xF3a5cd8F0cA7D6BdfD8b36B04A951626Aa7DEDf1`

## Stop the Gateway

When you're done:
```bash
cd /Users/hugoduarte/Desktop/Dotmoovs/webbattles-gateway/gateway/oracle/case_4
docker compose down
```

