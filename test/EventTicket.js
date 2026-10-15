const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("EventTicket Verification System", function () {
  let EventTicket;
  let eventTicket;
  let owner;
  let addr1;
  let addr2;

  beforeEach(async function () {
    // Get the ContractFactory and Signers
    EventTicket = await ethers.getContractFactory("EventTicket");
    [owner, addr1, addr2] = await ethers.getSigners();

    // Deploy the contract with event details
    eventTicket = await EventTicket.deploy("Blockchain Conference 2026", "2026-12-01");
  });

  describe("Deployment", function () {
    it("Should set the right owner", async function () {
      expect(await eventTicket.owner()).to.equal(owner.address);
    });

    it("Should set the correct event name and date", async function () {
      expect(await eventTicket.eventName()).to.equal("Blockchain Conference 2026");
      expect(await eventTicket.eventDate()).to.equal("2026-12-01");
    });
  });

  describe("Minting Tickets", function () {
    it("Should allow the owner to mint a ticket", async function () {
      await expect(eventTicket.mintTicket(addr1.address))
        .to.emit(eventTicket, "TicketMinted")
        .withArgs(1, addr1.address);
      
      expect(await eventTicket.ownerOf(1)).to.equal(addr1.address);
      expect(await eventTicket.isTicketValid(1)).to.be.true;
    });

    it("Should fail if a non-owner tries to mint a ticket (prevents fakes)", async function () {
      await expect(eventTicket.connect(addr1).mintTicket(addr2.address))
        .to.be.revertedWithCustomError(eventTicket, "OwnableUnauthorizedAccount")
        .withArgs(addr1.address);
    });
  });

  describe("Verifying Tickets", function () {
    beforeEach(async function () {
      // Mint a ticket to addr1 for testing
      await eventTicket.mintTicket(addr1.address);
    });

    it("Should verify a valid ticket and mark it as used", async function () {
      expect(await eventTicket.isTicketValid(1)).to.be.true;

      await expect(eventTicket.verifyTicket(1))
        .to.emit(eventTicket, "TicketVerified")
        .withArgs(1, addr1.address);

      // Ticket should now be marked as used
      expect(await eventTicket.isTicketUsed(1)).to.be.true;
      expect(await eventTicket.isTicketValid(1)).to.be.false;
    });

    it("Should fail to verify a ticket that has already been used (prevents duplicates)", async function () {
      await eventTicket.verifyTicket(1); // First verification

      // Second verification should fail
      await expect(eventTicket.verifyTicket(1))
        .to.be.revertedWith("Ticket has already been used (duplicate)");
    });

    it("Should fail to verify a fake/non-existent ticket", async function () {
      await expect(eventTicket.verifyTicket(999))
        .to.be.revertedWith("Ticket does not exist (fake ticket)");
    });
  });

  describe("Non-transferable (Soulbound) property", function () {
    it("Should prevent transferring tickets to other addresses", async function () {
      await eventTicket.mintTicket(addr1.address);
      
      // Attempting to transfer the ticket should fail
      await expect(
        eventTicket.connect(addr1).transferFrom(addr1.address, addr2.address, 1)
      ).to.be.revertedWith("Event tickets are non-transferable");
    });
  });
});
