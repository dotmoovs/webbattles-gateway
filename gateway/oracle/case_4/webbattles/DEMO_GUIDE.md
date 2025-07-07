# WebBattles Cross-Chain Oracle Demo Guide

## Overview

This demo showcases cross-chain oracle synchronization between two Ethereum chains using the SATP Gateway. When a battle is created on Chain 1, the oracle replicates it to Chain 2 with **automatic configuration management**.

## System Architecture

```
Chain 1 (Origin) → Oracle → SATP Gateway → Chain 2 (Destination)
createBattle() → Oracle Processing → syncBattleData() + replicateBattle()
```

## Prerequisites

- **Docker and Docker Compose** - For SATP Gateway
- **Node.js v20.x** - For Hardhat (not v23+)
- **Python 3.12+** - With requests and web3 modules

## Initial Setup

### 1. Start the Gateway (Docker)
In **Terminal 1**, from the `case_4` directory:
```bash
cd gateway/oracle/case_4
docker compose up
```
This will start the Gateway with the configuration file located in `./config/config.json`.

### 2. Start the Hardhat EVM Blockchains
In **Terminal 2**, from the `case_4` directory:
```bash
cd ../../../EVM && npx hardhat node --hostname 0.0.0.0 --port 8545
```

In **Terminal 3**, from the `case_4` directory:
```bash
cd ../../../EVM && npx hardhat node --hostname 0.0.0.0 --port 8546
```

**Keep these terminals running** throughout the demo!

## Quick Demo

### Step 1: Ensure Prerequisites
```bash
# Check gateway is running
cd ../
docker ps | grep satp

# Check Hardhat nodes
curl http://localhost:8545 && curl http://localhost:8546
```

### Step 2: Deploy Contracts
```bash
cd webbattles
python3 deploy-contracts.py
```
**Automatically updates** `CONTRACT_CHAIN_1` and `CONTRACT_CHAIN_2` in config.py

### Step 3: Register Oracle
```bash
python3 oracle-webbattles-register.py
```
**Automatically updates** `SYNC_TASK_ID` and `REPLICATION_TASK_ID` in config.py

### Step 4: Create Battle
```bash
python3 simple-battle-test.py
```
**Automatically updates** `LAST_BATTLE_ID` in config.py

### Step 5: Execute Cross-Chain Sync
```bash
python3 oracle-webbattles-execute-update.py both
```

### Step 6: Verify Success
```bash
python3 verify-cross-chain-battle.py
```

## Expected Output

### Battle Creation Success
```
WEBBATTLES CROSS-CHAIN ORACLE TEST
--------------------------------------------------
Chain 1 (port 8545): Connected = True
Chain 2 (port 8546): Connected = True

Creating battle on Chain 1...
Challenger: 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266
Bet Amount: 100000000000000000 wei (0.1 ETH)

Battle created successfully!
Transaction Hash: 0x...
Battle ID: 0x...
Gas Used: 385,668
Updating config.py with new battle ID...
```

### Cross-Chain Sync Success
```
SYNC OPERATION: SUCCESS
Transaction Hash: 0x...
Gas Used: 194,313

REPLICATION OPERATION: SUCCESS  
Transaction Hash: 0x...
Gas Used: 181,445
```

### Cross-Chain Verification Success
```
CROSS-CHAIN BATTLE VERIFICATION
--------------------------------------------------
CHAIN 1 BATTLE:
  Battle ID: a36c0f196ffd226be203e64ad2d938a0e995b72a08297f6f72fd7b7e98c54f20
  Challenger: 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266
  Bet Amount: 0.1 ETH
  Battle Type: Football Freestyle

CHAIN 2 BATTLE:
  Battle ID: a36c0f196ffd226be203e64ad2d938a0e995b72a08297f6f72fd7b7e98c54f20
  Challenger: 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266  
  Bet Amount: 0.1 ETH
  Battle Type: Football Freestyle

CROSS-CHAIN SYNC SUCCESSFUL! Battle exists identically on both chains!
```

## Files Overview

### **Essential Files (KEEP)**
- `config.py` - **Auto-updating configuration**
- `config_updater.py` - **Auto-update utility**
- `oracle-webbattles-register.py` - **Working oracle registration**
- `simple-battle-test.py` - **Battle creation + auto-config**
- `oracle-webbattles-execute-update.py` - **Manual oracle execution**
- `verify-cross-chain-battle.py` - **Cross-chain verification**
- `oracle-webbattles-check-status.py` - **Status checking**
- `deploy-contracts.py` - **Python deployment helper**


## Technical Architecture

### **Smart Contract Functions**
- `createBattle()` - Creates battles with ETH bets
- `syncBattleData()` - Oracle sync function
- `replicateBattle()` - Oracle replication function
- `getBattle()` - View battle details

### **Oracle Events**
- `UpdatedData(dataId, data, nonce)` - Triggers sync
- `BattleCreated(battleId, challenger, amount, battleType)` - Triggers replication

### **Auto-Configuration System**
```python
# config_updater.py automatically updates:
update_config_variable('CONTRACT_CHAIN_1', '0x...')
update_config_variable('SYNC_TASK_ID', 'uuid...')
update_config_variable('LAST_BATTLE_ID', '0x...')
```

## Troubleshooting

### **Gateway Issues**
```bash
# Restart shared gateway if needed
cd ../
docker compose restart
```

### **Check Connections**
```bash
# Check oracle status
python3 oracle-webbattles-check-status.py

# Check if contracts deployed
python3 -c "from config import *; print(f'Chain1: {CONTRACT_CHAIN_1}'); print(f'Chain2: {CONTRACT_CHAIN_2}')"
```

## Success Criteria

1. **Battle Creation**: New battle on Chain 1 with auto-updated config
2. **Cross-Chain Sync**: `syncBattleData` success on Chain 2
3. **Cross-Chain Replication**: `replicateBattle` success on Chain 2
4. **Verification**: Identical battle data on both chains

**Demo Complete!** The WebBattles oracle successfully demonstrates cross-chain data synchronization with automatic configuration management. 
