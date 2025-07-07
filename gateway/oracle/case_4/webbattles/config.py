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
SYNC_TASK_ID = "919da023-75b8-48fd-8058-3ecfc69a3d40"
REPLICATION_TASK_ID = "fa99a30c-b291-457b-89bc-f5cc048a1cd7"

# Last created battle (updated by test scripts)
LAST_BATTLE_ID = "0x75b6fdaaec55283cdb313e794d294c8492598a27cdeba3036767ea8c7365ccf0" 
