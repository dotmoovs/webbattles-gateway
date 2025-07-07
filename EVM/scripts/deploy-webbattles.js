const { ethers } = require("hardhat");
const fs = require("fs");
const path = require("path");

async function updateConfig(contractAddress, networkName) {
  const configPath = path.join(__dirname, "../../gateway/oracle/case_4/webbattles/config.py");
  
  if (fs.existsSync(configPath)) {
    let configContent = fs.readFileSync(configPath, 'utf8');
    
    if (networkName === "hardhat1") {
      configContent = configContent.replace(
        /CONTRACT_CHAIN_1 = ".*"/,
        `CONTRACT_CHAIN_1 = "${contractAddress}"`
      );
    } else if (networkName === "hardhat2") {
      configContent = configContent.replace(
        /CONTRACT_CHAIN_2 = ".*"/,
        `CONTRACT_CHAIN_2 = "${contractAddress}"`
      );
    }
    
    fs.writeFileSync(configPath, configContent);
    console.log(`Updated config.py with ${networkName} address: ${contractAddress}`);
  }
}

async function main() {
  console.log("Deploying WebBattles Contract...");
  
  // Get the contract factory
  const WebBattles = await ethers.getContractFactory("WebBattles");
  
  // Deploy the contract
  const webBattles = await WebBattles.deploy();
  
  // Wait for deployment to complete
  await webBattles.waitForDeployment();
  
  const contractAddress = await webBattles.getAddress();
  console.log("WebBattles deployed to:", contractAddress);
  
  // Get deployer account
  const [deployer] = await ethers.getSigners();
  console.log("Deployed by account:", deployer.address);
  console.log("Account balance:", ethers.formatEther(await ethers.provider.getBalance(deployer.address)), "ETH");
  
  // Get network info
  const network = await ethers.provider.getNetwork();
  const networkName = network.name;
  
  // Update config.py with new address
  await updateConfig(contractAddress, networkName);
  
  // Display contract info
  console.log("\n" + "=".repeat(60));
  console.log("WEBBATTLES CONTRACT DEPLOYED");
  console.log("=".repeat(60));
  console.log(`Contract Address: ${contractAddress}`);
  console.log(`Network: ${networkName}`);
  console.log(`Total Battles: ${await webBattles.totalBattles()}`);
  
  // Grant roles info
  console.log("\nROLES GRANTED TO DEPLOYER:");
  console.log("   - DEFAULT_ADMIN_ROLE");
  console.log("   - ORACLE_ROLE");
  
  console.log("\nAVAILABLE FUNCTIONS:");
  console.log("   - createBattle(battleType) payable");
  console.log("   - replicateBattle(battleId, challenger, betAmount, battleType)");
  console.log("   - syncBattleData(data)");
  console.log("   - getBattle(battleId)");
  console.log("   - getPlayerBattles(player)");
  
  console.log("\nNEXT STEPS:");
  console.log("1. Config.py automatically updated with contract address");
  console.log("2. Start the SATP gateway: docker compose up");
  console.log("3. Register with oracle: python3 oracle-webbattles-register.py");
  console.log("4. Create your first battle!");
  
  return {
    contract: webBattles,
    address: contractAddress
  };
}

// Handle errors
main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("Deployment failed:", error);
    process.exit(1);
  }); 