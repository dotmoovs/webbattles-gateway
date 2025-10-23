# PILOT #1 - DOTMOOVS CROSS-CHAIN INTEGRATION
## Components, Architecture & Information Flow

---

## 1. COMPONENTS / COMPONENTES

### 1.1 WebBattles Smart Contract

**Purpose**: Core smart contract for battle creation and cross-chain replication.

**Deployed On**:
- Ethereum Sepolia (Chain 1 - Origin)
- Base Sepolia (Chain 2 - Destination)

**Main Functionalities**:
- `createBattle()`: Creates new battle on the origin chain
- `replicateBattle()`: Replicates battle data from another chain (restricted to oracle role)
- `syncBattleData()`: Synchronizes battle metadata across chains (restricted to oracle role)
- `getBattle()`: Retrieves battle information

**Battle Data Structure**:
```
- battleId: Unique identifier (bytes32)
- challenger: Battle creator address
- opponent: Opponent address
- betAmount: Staked amount in ETH
- status: Battle state (PENDING, ACTIVE, COMPLETED)
- winner: Winner address
- createdAt: Creation timestamp
- completedAt: Completion timestamp
- battleType: Type of battle (e.g., "Football Freestyle")
```

**Events Emitted**:
- `BattleCreated`: Emitted when a battle is created
- `UpdatedData`: Emitted for metadata synchronization

**Access Control**:
- Role-based permissions (Admin, Oracle)
- Only oracle can execute cross-chain replication functions

---

### 1.2 SATP Gateway (Third-Party Middleware)

**Provider**: INESC-ID / Hyperledger Cacti

**Purpose**: Acts as middleware for secure cross-chain communication and event-driven transaction execution.

**Functionality** (Black Box):
- Listens to blockchain events via WebSocket
- Processes events and triggers corresponding actions on destination chains
- Manages transaction signing and submission
- Provides REST API for oracle task registration and management

**Interface**:
- REST API endpoints for task registration
- WebSocket connections to blockchain nodes
- Automatic event-to-transaction mapping

**Note**: The internal workings of the SATP Gateway are managed by the third-party provider. Dotmoovs interacts with it via configuration and API calls.

---

### 1.3 Blockchain Networks

#### Ethereum Sepolia (Chain 1)
- **Type**: Ethereum Testnet
- **Role**: Origin chain for battle creation
- **Contract**: WebBattles.sol deployed at 0x[ADDRESS]

#### Base Sepolia (Chain 2)
- **Type**: Base Layer 2 Testnet
- **Role**: Destination chain for battle replication
- **Contract**: WebBattles.sol deployed at 0x[ADDRESS]

---

### 1.4 Deployment & Configuration Scripts

**Language**: Python

**Scripts**:
- Contract deployment automation
- Oracle task registration
- Battle creation and verification utilities

---

## 2. ARCHITECTURE / ARQUITETURA

### 2.1 System Architecture

The system consists of three main components connected in a simple architecture:

**WebBattles Smart Contracts** are deployed identically on both Ethereum Sepolia (origin chain) and Base Sepolia (destination chain). When a user creates a battle on the origin chain, the contract emits events that are captured by the **SATP Gateway** via WebSocket connections. The Gateway then automatically triggers the replication function on the destination chain, ensuring the battle data is synchronized across both blockchains.

```
┌─────────────────────────────────────────────────────────────┐
│              WebBattles Cross-Chain System                   │
└─────────────────────────────────────────────────────────────┘

    ┌──────────────────┐                    ┌──────────────────┐
    │  Ethereum        │                    │  Base            │
    │  Sepolia         │                    │  Sepolia         │
    │                  │                    │                  │
    │  WebBattles.sol  │                    │  WebBattles.sol  │
    │  - createBattle()│                    │  - replicateBattle()
    │  - Events        │                    │  - syncBattleData()
    └────────┬─────────┘                    └────────▲─────────┘
             │                                       │
             │ Events (WebSocket)                    │ Transactions
             │                                       │
             └───────────►┌────────────┐◄───────────┘
                          │    SATP    │
                          │   Gateway  │
                          │ (Third-Party)
                          └────────────┘
```

### 2.2 Deployment Architecture

The pilot was deployed on public testnets to validate the cross-chain functionality in a realistic environment. The **Ethereum Sepolia** network serves as the origin chain where battles are initially created, while **Base Sepolia** acts as the destination chain for replication. The **SATP Gateway**, operated by INESC-ID, is hosted separately and connects to both networks to facilitate the cross-chain communication.

```
┌──────────────────────────────────────────────────────────────┐
│                    Testnet Environment                        │
└──────────────────────────────────────────────────────────────┘

┌────────────────────┐                      ┌────────────────────┐
│ Ethereum Sepolia   │                      │ Base Sepolia       │
│ (Origin Chain)     │                      │ (Destination)      │
│                    │                      │                    │
│ WebBattles         │                      │ WebBattles         │
│ Contract: 0x...    │                      │ Contract: 0x...    │
└─────────┬──────────┘                      └──────────▲─────────┘
          │                                            │
          │                                            │
          └──────────►┌──────────────┐◄───────────────┘
                      │ SATP Gateway │
                      │ (INESC-ID)   │
                      └──────────────┘
```

---

## 3. INFORMATION FLOW / FLUXO DE INFORMAÇÃO

### 3.1 Battle Creation and Cross-Chain Replication Flow

```
┌──────────────────────────────────────────────────────────┐
│  STEP 1: Battle Creation on Origin Chain                 │
└──────────────────────────────────────────────────────────┘

User/Player
   │
   │ Creates battle: createBattle("Football Freestyle") + 0.1 ETH
   ▼
Ethereum Sepolia - WebBattles Contract
   │
   │ • Generates unique battleId
   │ • Stores battle data
   │ • Emits BattleCreated event
   ▼
Battle stored on Chain 1


┌──────────────────────────────────────────────────────────┐
│  STEP 2: Event Detection & Processing                    │
└──────────────────────────────────────────────────────────┘

Sepolia emits: BattleCreated(battleId, challenger, betAmount, type)
   │
   │ WebSocket connection
   ▼
SATP Gateway
   │
   │ • Detects event
   │ • Extracts battle parameters
   │ • Prepares replication transaction
   ▼
Transaction ready for destination chain


┌──────────────────────────────────────────────────────────┐
│  STEP 3: Cross-Chain Replication                         │
└──────────────────────────────────────────────────────────┘

SATP Gateway
   │
   │ Calls: replicateBattle(battleId, challenger, betAmount, type)
   ▼
Base Sepolia - WebBattles Contract
   │
   │ • Validates battle doesn't exist
   │ • Stores battle replica with same battleId
   │ • Emits BattleCreated event
   ▼
Battle replicated on Chain 2


┌──────────────────────────────────────────────────────────┐
│  STEP 4: Data Consistency                                │
└──────────────────────────────────────────────────────────┘

Both chains now contain identical battle data:
   - Same battleId
   - Same challenger address
   - Same bet amount
   - Same battle type
   - Same status

Cross-chain synchronization complete ✓
```

### 3.2 Data Consistency Mechanism

The system ensures data consistency through:

1. **Deterministic Battle IDs**: 
   - Battle IDs are generated using `keccak256(challenger, betAmount, battleType, timestamp, counter)`
   - Same ID used across all chains

2. **Parameter Replication**:
   - Gateway extracts exact parameters from Chain 1 event
   - Passes identical parameters to Chain 2 replication function

3. **Smart Contract Validation**:
   - Contract verifies battle doesn't already exist
   - Role-based access control (only oracle can replicate)

4. **Event-Driven Architecture**:
   - Automatic trigger on battle creation
   - No manual intervention required

### 3.3 Information Flow Summary

```
Chain 1 (Sepolia)              Gateway               Chain 2 (Base Sepolia)
─────────────────              ───────               ──────────────────────

createBattle()
     │
     │ Emit Event
     ├──────────────────────► Detect Event
     │                              │
     │                        Extract Params
     │                              │
     │                        Build Transaction
     │                              │
     │                              ├────────────────► replicateBattle()
     │                              │                        │
     │                              │                  Store Battle
     │                              │                        │
     │                              ◄────────────────  Return Success
     │
[Battle on Chain 1]                              [Battle on Chain 2]
     │                                                        │
     └────────────────── Same battleId ─────────────────────┘
                    Same challenger, amount, type
```

---

## 4. SUMMARY / RESUMO

### Components:
- **WebBattles Smart Contract**: Deployed on Sepolia and Base Sepolia
- **SATP Gateway**: Third-party middleware (INESC-ID) for cross-chain communication
- **Blockchain Networks**: Ethereum Sepolia (origin) and Base Sepolia (destination)

### Architecture:
- Simple 3-component architecture: Chain 1 ↔ Gateway ↔ Chain 2
- Event-driven design using WebSocket connections
- Role-based access control on smart contracts

### Information Flow:
1. Battle created on Chain 1 → Event emitted
2. Gateway detects event → Extracts parameters
3. Gateway triggers replication on Chain 2 → Battle stored
4. Data consistency ensured through deterministic IDs and parameter validation

---

**Note**: Performance metrics (synchronization time, creation time, data consistency verification) are covered separately in the evaluation section.

