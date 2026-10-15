const hre = require("hardhat");

async function main() {
  console.log("Starting deployment...");

  // Get the contract factory
  const EventTicket = await hre.ethers.getContractFactory("EventTicket");

  // Deploy the contract with initialization parameters
  const eventName = "Blockchain Conference 2026";
  const eventDate = "2026-12-01";
  
  console.log(`Deploying EventTicket contract for: ${eventName} on ${eventDate}`);
  const eventTicket = await EventTicket.deploy(eventName, eventDate);

  await eventTicket.waitForDeployment();
  const address = await eventTicket.getAddress();

  console.log(`\n✅ EventTicket smart contract successfully deployed!`);
  console.log(`📄 Contract Address: ${address}`);
  console.log(`\nYou can now interact with this contract using Hardhat tasks or a frontend application.`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
