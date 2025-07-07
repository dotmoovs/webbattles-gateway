// SPDX-License-Identifier: GPL-3.0

pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/utils/Strings.sol";

/**
 * @title WebBattles
 * @dev Simple battle creation contract with cross-chain oracle replication
 */
contract WebBattles is AccessControl {

    bytes32 public constant ORACLE_ROLE = keccak256("ORACLE_ROLE");

    enum BattleStatus {
        PENDING,
        ACTIVE,
        COMPLETED
    }

    struct Battle {
        bytes32 battleId;
        address challenger;
        address opponent;
        uint256 betAmount;
        BattleStatus status;
        address winner;
        uint256 createdAt;
        uint256 completedAt;
        string battleType;
    }

    // Events for oracle sync
    event UpdatedData(bytes32 id, string data, uint256 nonce);
    event BattleCreated(bytes32 indexed battleId, address indexed challenger, uint256 betAmount, string battleType);

    // State variables
    mapping(bytes32 => Battle) public battles;
    mapping(bytes32 => string) private oracleData;
    mapping(address => bytes32[]) public playerBattles;
    
    uint256 private nonce = 0;
    uint256 public totalBattles = 0;

    constructor() {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(ORACLE_ROLE, msg.sender);
    }

    // Oracle functions for cross-chain sync
    function setData(string memory data) external onlyRole(ORACLE_ROLE) {
        bytes32 dataId = keccak256(abi.encode(data));
        oracleData[dataId] = data;
        nonce++;
        emit UpdatedData(dataId, data, nonce);
    }

    function syncBattleData(string memory data) external onlyRole(ORACLE_ROLE) {
        bytes32 dataId = keccak256(abi.encode(data));
        oracleData[dataId] = data;
        nonce++;
        emit UpdatedData(dataId, data, nonce);
    }

    function replicateBattle(
        bytes32 battleId,
        address challenger,
        uint256 betAmount,
        string memory battleType
    ) external onlyRole(ORACLE_ROLE) {
        require(battles[battleId].challenger == address(0), "Battle already exists");
        
        battles[battleId] = Battle({
            battleId: battleId,
            challenger: challenger,
            opponent: address(0),
            betAmount: betAmount,
            status: BattleStatus.PENDING,
            winner: address(0),
            createdAt: block.timestamp,
            completedAt: 0,
            battleType: battleType
        });
        
        playerBattles[challenger].push(battleId);
        totalBattles++;
        
        emit BattleCreated(battleId, challenger, betAmount, battleType);
    }

    function createBattle(string memory battleType) external payable {
        require(msg.value > 0, "Bet amount must be greater than 0");
        require(bytes(battleType).length > 0, "Battle type required");
        
        bytes32 battleId = keccak256(abi.encodePacked(
            msg.sender, 
            msg.value, 
            battleType, 
            block.timestamp, 
            totalBattles
        ));
        
        battles[battleId] = Battle({
            battleId: battleId,
            challenger: msg.sender,
            opponent: address(0),
            betAmount: msg.value,
            status: BattleStatus.PENDING,
            winner: address(0),
            createdAt: block.timestamp,
            completedAt: 0,
            battleType: battleType
        });
        
        playerBattles[msg.sender].push(battleId);
        totalBattles++;
        
        // Sync battle creation via oracle
        string memory battleData = string(abi.encodePacked(
            "battle_created,",
            Strings.toHexString(uint256(battleId)),
            ",",
            Strings.toHexString(uint160(msg.sender)),
            ",",
            Strings.toString(msg.value),
            ",",
            battleType
        ));
        
        bytes32 dataId = keccak256(abi.encode(battleData));
        oracleData[dataId] = battleData;
        nonce++;
        emit UpdatedData(dataId, battleData, nonce);
        
        emit BattleCreated(battleId, msg.sender, msg.value, battleType);
    }

    // View functions
    function getBattle(bytes32 battleId) external view returns (Battle memory) {
        return battles[battleId];
    }
    
    function getData(bytes32 id) external view returns (string memory) {
        require(bytes(oracleData[id]).length > 0, "Data not found");
        return oracleData[id];
    }

    function getNonce() external view returns (uint256) {
        return nonce;
    }

    function getPlayerBattles(address player) external view returns (bytes32[] memory) {
        return playerBattles[player];
    }

    function grantOracleRole(address account) external onlyRole(DEFAULT_ADMIN_ROLE) {
        _grantRole(ORACLE_ROLE, account);
    }

    receive() external payable {}
} 
