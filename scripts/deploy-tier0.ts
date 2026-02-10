import { ethers } from "hardhat";

/**
 * Deploy Tier0Lending contract to Base testnet
 * Usage: npx hardhat run scripts/deploy-tier0.ts --network base-sepolia
 */
async function main() {
  console.log("🚀 Deploying Tier0Lending contract...");

  // Base Sepolia USDC address (testnet)
  const USDC_ADDRESS = "0x036CbD53842c5426634e7929541eC2318f3dCF7e";

  // Get deployer
  const [deployer] = await ethers.getSigners();
  console.log("📝 Deploying from:", deployer.address);

  // Check balance
  const balance = await ethers.provider.getBalance(deployer.address);
  console.log("💰 Balance:", ethers.formatEther(balance), "ETH");

  // Deploy contract
  const Tier0Lending = await ethers.getContractFactory("Tier0Lending");
  const tier0 = await Tier0Lending.deploy(USDC_ADDRESS);

  await tier0.waitForDeployment();
  const address = await tier0.getAddress();

  console.log("✅ Tier0Lending deployed to:", address);
  console.log("📋 USDC address:", USDC_ADDRESS);

  // Verify deployment
  const minLoan = await tier0.MIN_LOAN();
  const maxLoan = await tier0.MAX_LOAN();
  const loanTerm = await tier0.LOAN_TERM();

  console.log("\n📊 Contract Configuration:");
  console.log("  Min loan:", ethers.formatUnits(minLoan, 6), "USDC");
  console.log("  Max loan:", ethers.formatUnits(maxLoan, 6), "USDC");
  console.log("  Loan term:", Number(loanTerm) / 86400, "days");

  console.log("\n🎯 Next steps:");
  console.log("1. Verify contract on BaseScan:");
  console.log(`   npx hardhat verify --network base-sepolia ${address} ${USDC_ADDRESS}`);
  console.log("2. Deposit liquidity:");
  console.log(`   Call depositLiquidity(amount) with USDC`);
  console.log("3. Test loan flow:");
  console.log(`   requestLoan(500000) // $0.50 loan`);

  // Save deployment info
  const deploymentInfo = {
    network: "base-sepolia",
    address: address,
    usdc: USDC_ADDRESS,
    deployer: deployer.address,
    timestamp: new Date().toISOString(),
    minLoan: ethers.formatUnits(minLoan, 6),
    maxLoan: ethers.formatUnits(maxLoan, 6),
    loanTerm: Number(loanTerm) / 86400,
  };

  console.log("\n💾 Deployment info saved to deployments/tier0-lending.json");
  
  const fs = require("fs");
  const path = require("path");
  const deploymentsDir = path.join(__dirname, "..", "deployments");
  if (!fs.existsSync(deploymentsDir)) {
    fs.mkdirSync(deploymentsDir);
  }
  fs.writeFileSync(
    path.join(deploymentsDir, "tier0-lending.json"),
    JSON.stringify(deploymentInfo, null, 2)
  );
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
