// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title EventTicket
 * @dev A decentralized event ticket verification system.
 * This contract creates blockchain-based digital event tickets using the ERC721 (NFT) standard.
 * Each ticket is unique and verifiable. Duplicate/fake tickets are prevented.
 */
contract EventTicket is ERC721, Ownable {
    uint256 private _nextTokenId;

    // Mapping from token ID to whether it has been used/scanned
    mapping(uint256 => bool) public isTicketUsed;

    // Event details
    string public eventName;
    string public eventDate;

    // Emitted when a ticket is successfully verified and marked as used
    event TicketVerified(uint256 indexed tokenId, address attendee);
    event TicketMinted(uint256 indexed tokenId, address indexed attendee);

    /**
     * @dev Initializes the contract by setting a `name` and a `symbol` to the token collection.
     * Also sets the event details.
     */
    constructor(string memory _eventName, string memory _eventDate) 
        ERC721("EventTicket", "TKT") 
        Ownable(msg.sender)
    {
        eventName = _eventName;
        eventDate = _eventDate;
        _nextTokenId = 1; // Start token IDs at 1
    }

    /**
     * @dev Mints a new ticket to the specified address.
     * Only the owner (event organizer) can mint tickets, preventing fake tickets.
     */
    function mintTicket(address attendee) public onlyOwner returns (uint256) {
        uint256 tokenId = _nextTokenId++;
        _mint(attendee, tokenId);
        
        emit TicketMinted(tokenId, attendee);
        return tokenId;
    }

    /**
     * @dev Verifies a ticket and marks it as used.
     * Prevents duplicate usage of the same ticket.
     * Can only be called by the event organizer (or an authorized verifier if role-based access was used).
     */
    function verifyTicket(uint256 tokenId) public onlyOwner {
        require(_ownerOf(tokenId) != address(0), "Ticket does not exist (fake ticket)");
        require(!isTicketUsed[tokenId], "Ticket has already been used (duplicate)");

        // Mark ticket as used to prevent duplicate entry
        isTicketUsed[tokenId] = true;

        emit TicketVerified(tokenId, ownerOf(tokenId));
    }

    /**
     * @dev Check if a ticket is valid (exists and not used).
     */
    function isTicketValid(uint256 tokenId) public view returns (bool) {
        return _ownerOf(tokenId) != address(0) && !isTicketUsed[tokenId];
    }

    /**
     * @dev Overrides the default ERC721 _update function to disable transfers.
     * This makes the tickets "soulbound", meaning they cannot be resold or transferred,
     * tying the ticket directly to the original buyer's address.
     */
    function _update(address to, uint256 tokenId, address auth) internal virtual override returns (address) {
        address from = _ownerOf(tokenId);
        // Allow minting (from == address(0)) and burning (to == address(0)) but prevent standard transfers
        require(from == address(0) || to == address(0), "Event tickets are non-transferable");
        return super._update(to, tokenId, auth);
    }
}
