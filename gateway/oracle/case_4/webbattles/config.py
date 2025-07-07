# WebBattles Cross-Chain Oracle Configuration

# Contract addresses (updated automatically by deployment scripts)
CONTRACT_CHAIN_1 = "0x5FbDB2315678afecb367f032d93F642f64180aa3"
CONTRACT_CHAIN_2 = "0xbdEd0D2bf404bdcBa897a74E6657f1f12e5C6fb6"

# Network configuration
CHAIN_1_RPC = "http://localhost:8545"
CHAIN_2_RPC = "http://localhost:8546"

# SATP Gateway configuration
GATEWAY_BASE_URL = "http://localhost:4010"
ORACLE_REGISTER_URL = f"{GATEWAY_BASE_URL}/api/v1/@hyperledger/cactus-plugin-satp-hermes/oracle/register"
ORACLE_EXECUTE_URL = f"{GATEWAY_BASE_URL}/api/v1/@hyperledger/cactus-plugin-satp-hermes/oracle/execute"

# Network IDs for oracle registration
SOURCE_NETWORK_ID = "HardhatTestNetwork1"
DESTINATION_NETWORK_ID = "HardhatTestNetwork2"

# Contract artifacts path
CONTRACT_ARTIFACTS_PATH = "../../../../EVM/artifacts/contracts/WebBattles.sol/WebBattles.json"

# Battle configuration
DEFAULT_BET_AMOUNT = "100000000000000000"  # 0.1 ETH in wei
DEFAULT_BATTLE_TYPE = "Football Freestyle"
DEFAULT_CHALLENGER = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"

# Last registered oracle task IDs (updated by registration script)
SYNC_TASK_ID = "13d10de9-1214-48c8-a85e-2748ca04da66"
REPLICATION_TASK_ID = "c92c1a82-6b1e-43a2-a5bb-71886478d8b9"

# Last created battle (updated by test scripts)
LAST_BATTLE_ID = "0x5d98e8727b4901286c1c14ad5dad2b4c812cd240405954836bb7226e88d9b86a" 
