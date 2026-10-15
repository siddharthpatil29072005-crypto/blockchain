# Decentralized Event Ticket Verification System

This project is a blockchain-based digital event ticket system designed to issue verifiably unique and secure event tickets, while strictly preventing duplicate or fake tickets.

## Features

1. **Unique Digital Tickets:** Tickets are minted as ERC721 Non-Fungible Tokens (NFTs), guaranteeing each ticket has a unique Token ID on the blockchain.
2. **Anti-Fake:** Only the authorized event organizer (contract owner) can mint tickets. Any ticket not issued by the smart contract is easily identified as fake.
3. **Anti-Duplicate / Single Use Verification:** The system includes a `verifyTicket(tokenId)` function that scans a ticket and permanently marks it as `used`. Subsequent attempts to verify the same ticket will be rejected.
4. **Soulbound / Non-transferable:** Once a ticket is issued to an attendee's wallet, it cannot be transferred or resold, preventing scalping or ticket reassignment outside the organizer's purview.

## Smart Contract

The core logic is found in `contracts/EventTicket.sol`. 

Key functions:
- `mintTicket(address attendee)`: Mints a unique ticket for an attendee.
- `verifyTicket(uint256 tokenId)`: Scans a ticket at the venue. Only the contract owner can call this.
- `isTicketValid(uint256 tokenId)`: Publicly checks if a ticket is valid (exists and is unused).

## Setup & Deployment

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Compile the contract:**
   ```bash
   npx hardhat compile
   ```

3. **Run the tests:**
   ```bash
   npx hardhat test
   ```

## How It Works in Practice

1. **Setup:** The Event Organizer deploys the `EventTicket` smart contract, specifying the Event Name and Date.
2. **Issuance:** Attendees purchase a ticket (via a separate payment portal or mint function). The Event Organizer calls `mintTicket(attendeeAddress)`, issuing a ticket to the attendee's wallet.
3. **Check-in/Verification:**
   - At the venue gate, the attendee presents their wallet address or a signed message proving they own the token ID.
   - The gatekeeper (Event Organizer) calls `verifyTicket(tokenId)` on the smart contract.
   - The contract checks if the ticket is valid and not already used.
   - If valid, it marks the ticket as used, preventing anyone else from entering with the same ticket (duplicate).
   - If the token ID doesn't exist on the contract, the ticket is rejected (fake).
