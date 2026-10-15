import zipfile
import html

def escape_xml(s):
    return html.escape(s).replace("'", "&apos;")

def make_p(text, bold=False, italic=False, size=22, space_before=0, space_after=160, align="left", color="222222", is_code=False):
    # size in half-points (22 = 11pt, 28 = 14pt, 32 = 16pt)
    # space in twips (20 twips = 1 pt)
    font_name = "Consolas" if is_code else "Calibri"
    b_tag = "<w:b/>" if bold else ""
    i_tag = "<w:i/>" if italic else ""
    jc_tag = f'<w:jc w:val="{align}"/>' if align != "left" else ""
    
    xml = f"""<w:p>
  <w:pPr>
    <w:spacing w:before="{space_before}" w:after="{space_after}" w:line="276" w:lineRule="auto"/>
    {jc_tag}
  </w:pPr>
  <w:r>
    <w:rPr>
      <w:rFonts w:ascii="{font_name}" w:hAnsi="{font_name}"/>
      {b_tag}
      {i_tag}
      <w:color w:val="{color}"/>
      <w:sz w:val="{size}"/>
    </w:rPr>
    <w:t xml:space="preserve">{escape_xml(text)}</w:t>
  </w:r>
</w:p>"""
    return xml

def make_bullet(text, prefix=""):
    xml = f"""<w:p>
  <w:pPr>
    <w:pStyle w:val="ListParagraph"/>
    <w:spacing w:before="40" w:after="80" w:line="260" w:lineRule="auto"/>
    <w:ind w:left="480" w:hanging="240"/>
  </w:pPr>
  <w:r>
    <w:rPr>
      <w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/>
      <w:b/>
      <w:color w:val="1F2438"/>
      <w:sz w:val="22"/>
    </w:rPr>
    <w:t xml:space="preserve">{escape_xml(prefix)}</w:t>
  </w:r>
  <w:r>
    <w:rPr>
      <w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/>
      <w:color w:val="333333"/>
      <w:sz w:val="22"/>
    </w:rPr>
    <w:t xml:space="preserve">{escape_xml(text)}</w:t>
  </w:r>
</w:p>"""
    return xml

def make_page_break():
    return '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'

def make_table(rows_data, col_widths, headers=True):
    # col_widths in twips (1440 twips = 1 inch)
    # rows_data: list of list of str
    tbl = [
        '<w:tbl>',
        '  <w:tblPr>',
        '    <w:tblW w:w="9360" w:type="dxa"/>',
        '    <w:jc w:val="center"/>',
        '    <w:tblBorders>',
        '      <w:top w:val="single" w:sz="6" w:space="0" w:color="CCCCCC"/>',
        '      <w:left w:val="single" w:sz="6" w:space="0" w:color="CCCCCC"/>',
        '      <w:bottom w:val="single" w:sz="6" w:space="0" w:color="CCCCCC"/>',
        '      <w:right w:val="single" w:sz="6" w:space="0" w:color="CCCCCC"/>',
        '      <w:insideH w:val="single" w:sz="4" w:space="0" w:color="E0E0E0"/>',
        '      <w:insideV w:val="single" w:sz="4" w:space="0" w:color="E0E0E0"/>',
        '    </w:tblBorders>',
        '  </w:tblPr>',
        '  <w:tblGrid>'
    ]
    for w in col_widths:
        tbl.append(f'    <w:gridCol w:w="{w}"/>')
    tbl.append('  </w:tblGrid>')
    
    for r_idx, row in enumerate(rows_data):
        is_h = headers and (r_idx == 0)
        bg = '1F2438' if is_h else ('F8F9FA' if r_idx % 2 == 1 else 'FFFFFF')
        txt_color = 'FFFFFF' if is_h else '222222'
        
        tbl.append('  <w:tr>')
        if is_h:
            tbl.append('    <w:trPr><w:tblHeader/></w:trPr>')
            
        for c_idx, cell_text in enumerate(row):
            w = col_widths[c_idx]
            bold_cell = is_h or (c_idx == 0 and not is_h)
            bold_tag = '<w:b/>' if bold_cell else ''
            pass_color = '008800' if cell_text.strip() == 'Pass' else txt_color
            align_right = '<w:jc w:val="right"/>' if (len(row) == 3 and c_idx == 2 and not is_h) else ''
            
            tbl.append(f"""    <w:tc>
      <w:tcPr>
        <w:tcW w:w="{w}" w:type="dxa"/>
        <w:shd w:val="clear" w:color="auto" w:fill="{bg}"/>
        <w:tcMar>
          <w:top w:w="120" w:type="dxa"/>
          <w:bottom w:w="120" w:type="dxa"/>
          <w:left w:w="160" w:type="dxa"/>
          <w:right w:w="160" w:type="dxa"/>
        </w:tcMar>
      </w:tcPr>
      <w:p>
        <w:pPr>
          <w:spacing w:before="0" w:after="0" w:line="240" w:lineRule="auto"/>
          {align_right}
        </w:pPr>
        <w:r>
          <w:rPr>
            <w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/>
            {bold_tag}
            <w:color w:val="{pass_color}"/>
            <w:sz w:val="19"/>
          </w:rPr>
          <w:t xml:space="preserve">{escape_xml(str(cell_text))}</w:t>
        </w:r>
      </w:p>
    </w:tc>""")
        tbl.append('  </w:tr>')
    tbl.append('</w:tbl>')
    return '\n'.join(tbl)

def build_document_xml():
    body = []
    
    # helper functions
    def title(t):
        body.append(make_p(t, bold=True, size=32, space_before=100, space_after=240, color="1F2438"))
    
    def chap(num, name):
        body.append(make_p(f"CHAPTER {num}", bold=True, size=28, space_before=100, space_after=60, color="1F2438"))
        body.append(make_p(name, bold=True, size=28, space_before=0, space_after=240, color="1F2438"))
        
    def subhead(t):
        body.append(make_p(t, bold=True, size=24, space_before=160, space_after=80, color="1F2438"))
        
    def p(t, italic=False, is_code=False):
        body.append(make_p(t, italic=italic, is_code=is_code, size=18 if is_code else 22, space_after=140, color="203A43" if is_code else "2E3338"))
        
    def code_block(code_str):
        for line in code_str.strip().split("\n"):
            body.append(make_p(line, is_code=True, size=18, space_after=40, color="203A43"))

    # ================= PAGE 1: ABSTRACT =================
    title("ABSTRACT")
    abstract_text = (
        "Traditional event ticketing infrastructures rely on centralized web servers and relational databases, "
        "introducing critical vulnerabilities including single points of failure, unmitigated ticket scalping, predatory "
        "secondary market markups, and widespread counterfeiting via duplicated barcodes or screenshots. This project "
        "designs and implements a Decentralized Event Ticket Verification System powered by Ethereum smart contracts "
        "to definitively eliminate duplicate and fraudulent admissions. Developed using Solidity, the system models every "
        "admission pass as an immutable ERC-721 Non-Fungible Token (NFT) cryptographically linked to a unique Token ID upon "
        "issuance. Only the authenticated event organizer holds authorization to mint tickets, strictly eliminating "
        "unauthorized or counterfeit creations. To prevent secondary scalping and black-market reselling, tickets enforce "
        "non-transferable (soulbound) properties, binding admission privileges directly to the recipient wallet. During gate "
        "admission, the smart contract verifies token legitimacy and executes an irreversible state change, marking the token "
        "as used to instantly reject subsequent presentation attempts. A responsive decentralized application (DApp) frontend "
        "developed in React and Vite connects to the local Hardhat execution network via ethers.js, featuring automated on-the-fly "
        "wallet generation and a live registry dashboard. Rigorous automated testing confirms 100% prevention of duplicate entry "
        "and fake ticket attempts."
    )
    p(abstract_text)
    body.append(make_page_break())

    # ================= PAGE 2: TABLE OF CONTENTS =================
    title("TABLE OF CONTENTS")
    toc_data = [
        ["Chapter", "Title", "Page No."],
        ["1", "Introduction", "1"],
        ["2", "Literature Survey / Existing System", "3"],
        ["3", "System Requirements & Design", "5"],
        ["4", "Implementation", "8"],
        ["5", "Testing & Results", "12"],
        ["6", "Conclusion and Future Scope", "15"],
        ["", "References", "16"],
        ["", "Appendix", "17"]
    ]
    body.append(make_table(toc_data, [1500, 6360, 1500], headers=True))
    body.append(make_page_break())

    # ================= PAGE 3: CHAPTER 1: INTRODUCTION =================
    chap("1", "INTRODUCTION")
    subhead("1.1 Overview of Blockchain Technology")
    p("Blockchain is an immutable, distributed, and cryptographically verified ledger system functioning across peer-to-peer computer networks without reliance on a centralized coordinating intermediary. Through distributed consensus protocols, cryptographic hashing, and automated state-transition logic, blockchain guarantees fault tolerance, chronological auditability, and tamper resistance.")
    p("Within event ticketing and digital rights verification, blockchain's core properties—namely structural immutability, programmatic transparency, and non-fungible digital scarcity—establish a superior operational paradigm. By encoding ticketing parameters directly into programmable smart contracts, event organizers can eliminate unauthorized intermediaries, enforce transparent authenticity verifications, and eliminate fraud.")

    subhead("1.2 Problem Statement")
    p("Contemporary event ticketing platforms suffer from endemic ticket fraud, including fraudulent duplication via static barcode screenshots, bot-driven ticket scalping, predatory secondary market markups, and lack of transparency. Centralized database architectures present single points of failure, lack public auditability, and fail to prevent unauthorized ticket alterations. A cryptographically enforceable verification architecture is required to guarantee ticket uniqueness and permanently prevent duplicate or counterfeit entries.")

    subhead("1.3 Objectives")
    body.append(make_bullet("To design and deploy a secure Solidity smart contract utilizing the ERC-721 token standard for issuing unique digital event tickets.", "• "))
    body.append(make_bullet("To eliminate dependency on centralized database authorities by establishing ticket verification directly on the blockchain ledger.", "• "))
    body.append(make_bullet("To provide a verifiable, transparent mechanism preventing duplicate ticket check-ins through irreversible state transitions.", "• "))
    body.append(make_bullet("To enforce soulbound (non-transferable) token properties, preventing unauthorized scalping and secondary reselling.", "• "))
    body.append(make_bullet("To construct a responsive decentralized application (DApp) enabling organizers to mint tickets on-the-fly and verify attendee credentials in real time.", "• "))

    subhead("1.4 Scope of the Project")
    p("The scope covers the design and implementation of the Solidity smart contract, comprehensive unit test automation, local EVM network deployment via Hardhat, and a reactive frontend DApp equipped with automatic keypair generation. The project demonstrates organizer-controlled minting, single-use gate consumption, and live registry synchronization. The scope intentionally excludes fiat payment gateways, gas subsidization relayers (ERC-4337), and physical optical hardware scanners.")
    body.append(make_page_break())

    # ================= PAGE 4: CHAPTER 2: LITERATURE SURVEY =================
    chap("2", "LITERATURE SURVEY / EXISTING SYSTEM")
    subhead("2.1 Existing (Traditional/Centralized) Approach")
    p("Conventional ticketing systems (such as Ticketmaster, Eventbrite, or venue-specific servers) manage admission passes inside centralized relational databases (e.g., PostgreSQL, MySQL). When an attendee purchases a ticket, the server assigns a database record and transmits an email containing a static barcode, QR code, or PDF. At the event entrance, gate scanning devices query the central server via local WiFi or cellular network to toggle a database flag marking the ticket as admitted.")

    subhead("2.2 Drawbacks of Existing System")
    body.append(make_bullet("Single Point of Failure: If centralized cloud services or local venue internet connections fail, gate operations stall and attendee verification halts entirely.", "• "))
    body.append(make_bullet("Vulnerability to Duplication: Static barcodes, PDFs, and QR codes can be screenshotted or photocopied, allowing fraudulent copies to be distributed to multiple attendees.", "• "))
    body.append(make_bullet("Uncontrolled Secondary Scalping: Automated scalping bots acquire tickets in bulk and resell them at inflated prices without organizer consent or artist royalties.", "• "))
    body.append(make_bullet("Internal Database Tampering: Insiders or compromised database administrators can alter records, forge complimentary passes, or modify attendance figures without an auditable ledger.", "• "))
    body.append(make_bullet("Zero Public Verifiability: Attendees and third parties have no transparent method to verify genuine ticket provenance before purchase.", "• "))

    subhead("2.3 Proposed Solution Overview")
    p("The proposed Decentralized Event Ticket Verification System eliminates these weaknesses by mapping each ticket to an ERC-721 Non-Fungible Token (NFT) deployed on an EVM blockchain. Each ticket possesses an immutable Token ID minted exclusively through the event organizer's cryptographic signature. Non-transferability is enforced at the bytecode level, binding the ticket to the designated attendee wallet. When scanned at the gate, the contract marks the ticket as used on-chain, rendering duplicate entries structurally and mathematically impossible.")
    body.append(make_page_break())

    # ================= PAGE 5: CHAPTER 3: SYSTEM REQUIREMENTS & DESIGN =================
    chap("3", "SYSTEM REQUIREMENTS & DESIGN")
    subhead("3.1 Hardware & Software Requirements")
    req_data = [
        ["Category", "Requirement"],
        ["Hardware", "Minimum 8 GB RAM, Intel Core i5 / AMD Ryzen 5, 10 GB Storage, Internet connectivity"],
        ["Blockchain Platform", "Ethereum / EVM-Compatible Local Testnet (Cancun EVM target)"],
        ["Smart Contract Language", "Solidity (v0.8.28)"],
        ["Development Framework", "Hardhat Framework (v2.22.0), Node.js (v20+ / v22+), npm"],
        ["Smart Contract Standards", "OpenZeppelin Contracts (v5.6.1 - ERC721, Ownable)"],
        ["Local Blockchain Node", "Hardhat Network (RPC: http://127.0.0.1:8545, ChainID: 31337)"],
        ["Web3 Client Library", "ethers.js (v6.16.0) for JSON-RPC provider and transaction signing"],
        ["Frontend Environment", "React 19, Vite (v8.3), HTML5, CSS3 Grid & Flexbox"],
        ["Operating System & Tools", "Windows 11 / Linux / macOS, Visual Studio Code, Git"]
    ]
    body.append(make_table(req_data, [2800, 6560], headers=True))

    subhead("3.2 System Architecture Diagram")
    p("+-----------------------------------------------------------------------------------------+\n"
      "|                                SYSTEM ARCHITECTURE                                      |\n"
      "+-----------------------------------------------------------------------------------------+\n"
      "| [ Event Organizer / Gatekeeper ]                      [ Attendee ]                      |\n"
      "|                 |                                          |                            |\n"
      "|                 v                                          v                            |\n"
      "| +-------------------------------------------------------------------------------------+ |\n"
      "| |                               React Frontend DApp (Vite)                            | |\n"
      "| |  - Keypair Generator Form   - Gate Verification Module   - Live Blockchain Registry | |\n"
      "| +-------------------------------------------------------------------------------------+ |\n"
      "|                                            | (ethers.js JSON-RPC Calls)                 |\n"
      "|                                            v                                            |\n"
      "| +-------------------------------------------------------------------------------------+ |\n"
      "| |                                ethers.js Client Layer (v6)                          | |\n"
      "| |  - JsonRpcProvider (HTTP)   - Wallet Signing (Private Key)   - Contract Event Filter | |\n"
      "| +-------------------------------------------------------------------------------------+ |\n"
      "|                                            | (EVM Transactions & Inquiries)             |\n"
      "|                                            v                                            |\n"
      "| +-------------------------------------------------------------------------------------+ |\n"
      "| |                       Solidity Smart Contract (EventTicket.sol)                     | |\n"
      "| |  - ERC721 Token Standard   - Ownable Access Control   - isTicketUsed Boolean Mapping | |\n"
      "| |  - mintTicket()            - verifyTicket()           - isTicketValid()             | |\n"
      "| +-------------------------------------------------------------------------------------+ |\n"
      "|                                            | (State Mutation & Consensus)               |\n"
      "|                                            v                                            |\n"
      "| +-------------------------------------------------------------------------------------+ |\n"
      "| |                EVM Blockchain Network (Hardhat Node / Ethereum Testnet)             | |\n"
      "| +-------------------------------------------------------------------------------------+ |\n"
      "+-----------------------------------------------------------------------------------------+", italic=True)
    body.append(make_p("Fig 3.1: System Architecture Diagram", bold=True, italic=True, size=20, space_after=120, color="555555"))

    subhead("3.3 Use Case / Flow Diagram")
    p("[ Organizer Flow ]:\n"
      "1. Input Attendee Name -> 2. Auto-Generate Wallet Keypair -> 3. Execute mintTicket() -> 4. Ticket Created.\n\n"
      "[ Gatekeeper Verification Flow ]:\n"
      "1. Enter Token ID -> 2. Query isTicketValid() on Blockchain ->\n"
      "   - If FALSE: Display Fake / Duplicate Rejection Alert.\n"
      "   - If TRUE: Execute verifyTicket() -> Mutate isTicketUsed = true -> Emit TicketVerified -> Attendee Admitted.")
    body.append(make_p("Fig 3.2: Use Case / Flow Diagram", bold=True, italic=True, size=20, space_after=120, color="555555"))

    subhead("3.4 Smart Contract Design")
    sc_data = [
        ["Element", "Name / Signature", "Description"],
        ["State Variable", "_nextTokenId (uint256)", "Internal counter tracking auto-incrementing token IDs."],
        ["State Variable", "isTicketUsed (mapping(uint256 => bool))", "Maps token ID to boolean usage status for single-entry enforcement."],
        ["State Variable", "eventName, eventDate (string)", "Public metadata defining event title and date."],
        ["Function", "mintTicket(address attendee) -> uint256", "Mints an ERC-721 token to the attendee. Restricted to contract owner."],
        ["Function", "verifyTicket(uint256 tokenId)", "Verifies token validity and sets isTicketUsed=true. Reverts if duplicate or fake."],
        ["Function", "isTicketValid(uint256 tokenId) -> bool", "Read-only query checking if token exists and remains unused."],
        ["Override", "_update(...) internal override", "Disables standard transfers to enforce soulbound (non-transferable) logic."],
        ["Event", "TicketMinted(uint256 tokenId, address attendee)", "Emitted upon issuance; triggers live DApp registry updates."],
        ["Event", "TicketVerified(uint256 tokenId, address attendee)", "Emitted upon gate verification; updates ticket badge to USED."]
    ]
    body.append(make_table(sc_data, [1800, 3760, 3800], headers=True))
    body.append(make_page_break())

    # ================= PAGE 6: CHAPTER 4: IMPLEMENTATION =================
    chap("4", "IMPLEMENTATION")
    subhead("4.1 Technology Stack Used")
    p("The implementation integrates smart contract security with reactive front-end tooling:\n"
      "• Smart Contract Layer: Solidity v0.8.28 utilizing OpenZeppelin Contracts v5.6.1 (ERC721, Ownable).\n"
      "• Development & Testing Framework: Hardhat v2.22.0 configured with the Cancun EVM target.\n"
      "• Client Blockchain Communication: ethers.js v6.16.0 for JSON-RPC provider calls, contract events, and keypair generation.\n"
      "• Frontend Application: React 19 bootstrapped with Vite 8.3, featuring CSS Grid layout and real-time state synchronization.")

    subhead("4.2 Smart Contract Code (Key Snippets)")
    body.append(make_p("Snippet 1: Organizer-Restricted Ticket Minting", bold=True, size=20, space_after=60, color="1F2438"))
    code_block(
        "function mintTicket(address attendee) public onlyOwner returns (uint256) {\n"
        "    uint256 tokenId = _nextTokenId++;\n"
        "    _mint(attendee, tokenId);\n"
        "    emit TicketMinted(tokenId, attendee);\n"
        "    return tokenId;\n"
        "}"
    )
    p("Explanation: Increments the internal token counter and triggers OpenZeppelin's internal _mint method to assign the unique token ID to the recipient. The onlyOwner modifier guarantees only authorized event organizers can issue tickets, preventing fake tickets.")

    body.append(make_p("Snippet 2: Anti-Duplicate Gate Verification", bold=True, size=20, space_after=60, color="1F2438"))
    code_block(
        "function verifyTicket(uint256 tokenId) public onlyOwner {\n"
        "    require(_ownerOf(tokenId) != address(0), \"Ticket does not exist (fake ticket)\");\n"
        "    require(!isTicketUsed[tokenId], \"Ticket has already been used (duplicate)\");\n"
        "    isTicketUsed[tokenId] = true;\n"
        "    emit TicketVerified(tokenId, ownerOf(tokenId));\n"
        "}"
    )
    p("Explanation: Validates that the requested token ID exists on-chain and has not previously been marked as consumed. Once verified, it permanently sets isTicketUsed[tokenId] to true, making subsequent re-entries with the same token mathematically impossible.")

    body.append(make_p("Snippet 3: Soulbound (Non-Transferable) Enforcement", bold=True, size=20, space_after=60, color="1F2438"))
    code_block(
        "function _update(address to, uint256 tokenId, address auth) internal virtual override returns (address) {\n"
        "    address from = _ownerOf(tokenId);\n"
        "    require(from == address(0) || to == address(0), \"Event tickets are non-transferable\");\n"
        "    return super._update(to, tokenId, auth);\n"
        "}"
    )
    p("Explanation: Overrides OpenZeppelin ERC-721's core _update hook. It allows initial minting (from == 0) and burning (to == 0), but strictly throws an exception if an attendee attempts a secondary market transfer, successfully preventing ticket scalping.")

    subhead("4.3 Frontend / DApp Integration")
    p("The DApp frontend connects directly to the local blockchain via ethers.JsonRpcProvider('http://127.0.0.1:8545/'). To eliminate user friction with browser extensions like MetaMask during local testing, the application connects directly with Hardhat's pre-funded organizer private key. When an organizer enters an attendee's name, the client generates a unique cryptographic keypair via ethers.Wallet.createRandom(), saves the address-name mapping, and executes contract.mintTicket(). Furthermore, the application listens to TicketMinted and TicketVerified events to maintain a real-time reactive table displaying token IDs, holder names, wallet addresses, and dynamic status badges.")

    subhead("4.4 Deployment Details")
    p("The smart contract was deployed to the persistent Hardhat EVM local network via an automated deployment script (scripts/deploy.js):\n"
      "• Network: Hardhat Localhost (Chain ID: 31337, RPC URL: http://127.0.0.1:8545)\n"
      "• Deployed Contract Address: 0x5FbDB2315678afecb367f032d93F642f64180aa3\n"
      "• Deployer / Organizer Address: 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266\n"
      "• Frontend Application URL: http://localhost:5173/")
    body.append(make_page_break())

    # ================= PAGE 7: CHAPTER 5: TESTING & RESULTS =================
    chap("5", "TESTING & RESULTS")
    subhead("5.1 Test Cases")
    test_cases = [
        ["Test ID", "Input / Action", "Expected Output", "Actual Output", "Result"],
        ["TC01", "Deploy contract with event name & date", "Contract deployed; state variables initialized correctly", "Owner, event name, and date verified correctly", "Pass"],
        ["TC02", "Organizer calls mintTicket(attendeeAddress)", "Ticket #1 minted to attendee; TicketMinted emitted", "Ticket #1 owned by attendee; isTicketValid=true", "Pass"],
        ["TC03", "Non-owner account attempts mintTicket()", "Transaction reverts with OwnableUnauthorizedAccount", "Reverted with OwnableUnauthorizedAccount", "Pass"],
        ["TC04", "Organizer calls verifyTicket(1) on valid ticket", "Ticket #1 marked isTicketUsed=true; TicketVerified emitted", "Ticket verified; status changes to USED; emitted event", "Pass"],
        ["TC05", "Organizer calls verifyTicket(1) a second time", "Transaction reverts: 'Ticket has already been used (duplicate)'", "Reverted with exact duplicate error message", "Pass"],
        ["TC06", "Organizer calls verifyTicket(999) for non-existent token", "Transaction reverts: 'Ticket does not exist (fake ticket)'", "Reverted with fake ticket error message", "Pass"],
        ["TC07", "Attendee attempts transferFrom() to another address", "Transaction reverts: 'Event tickets are non-transferable'", "Reverted with non-transferable error message", "Pass"],
        ["TC08", "Call isTicketValid(1) on unused vs used ticket", "Returns true initially; returns false after verification", "Returned true before scan; false after verification", "Pass"]
    ]
    body.append(make_table(test_cases, [1100, 2460, 2500, 2300, 1000], headers=True))

    subhead("5.2 Output & Verification Results")
    p("Hardhat Automated Test Suite Execution Output:\n"
      "---------------------------------------------------------------------------------\n"
      "  EventTicket Verification System\n"
      "    Deployment\n"
      "      √ Should set the right owner (202ms)\n"
      "      √ Should set the correct event name and date\n"
      "    Minting Tickets\n"
      "      √ Should allow the owner to mint a ticket\n"
      "      √ Should fail if a non-owner tries to mint a ticket (prevents fakes) (249ms)\n"
      "    Verifying Tickets\n"
      "      √ Should verify a valid ticket and mark it as used\n"
      "      √ Should fail to verify a ticket that has already been used (prevents duplicates)\n"
      "      √ Should fail to verify a fake/non-existent ticket\n"
      "    Non-transferable (Soulbound) property\n"
      "      √ Should prevent transferring tickets to other addresses\n\n"
      "  8 passing (5s)\n"
      "---------------------------------------------------------------------------------", is_code=True)
    p("DApp Verification Interface Behavior:\n"
      "• Minting Execution: Entering an attendee name (e.g., 'Alice') generates a new keypair and mints Token #1. The record is instantly displayed in the Ticket Database as 'VALID'.\n"
      "• Gate Check-in: Entering Token ID #1 and triggering 'Verify & Mark Used' modifies contract state. The badge immediately updates to 'USED'.\n"
      "• Duplicate Thwarting: Triggering 'Verify & Mark Used' again on Token #1 raises an error alert indicating the ticket has already been used.\n"
      "• Fake Ticket Detection: Inquiring about Token ID #99 displays an alert confirming the ticket does not exist on the blockchain.")
    body.append(make_page_break())

    # ================= PAGE 8: CHAPTER 6: CONCLUSION AND FUTURE SCOPE =================
    chap("6", "CONCLUSION AND FUTURE SCOPE")
    subhead("6.1 Conclusion")
    p("The Decentralized Event Ticket Verification System successfully achieved all core objectives outlined in Chapter 1. By coupling Ethereum ERC-721 token standards with custom state tracking and soulbound access controls, the system guarantees that each ticket is uniquely identifiable, permanently recorded on an immutable ledger, and single-use only. Counterfeit tickets are prevented through cryptographic owner-only minting, while duplicate admissions are entirely eliminated via smart contract state assertions. The resulting prototype delivers a robust, transparent, and user-friendly Web3 platform that eliminates dependence on centralized ticketing gatekeepers.")

    subhead("6.2 Limitations")
    body.append(make_bullet("EVM Gas Costs: Every mint and gate verification transaction incurs computational gas fees on public networks.", "• "))
    body.append(make_bullet("Throughput & Latency: Public blockchain block confirmation times (12-15 seconds on Ethereum Layer 1) can constrain high-volume gate throughput without Layer 2 scaling.", "• "))
    body.append(make_bullet("Environment Constraints: Prototype tested primarily on a local Hardhat EVM development network rather than public mainnet.", "• "))
    body.append(make_bullet("Peripheral Integration: Currently operates via desktop browser interface rather than dedicated mobile optical barcode/NFC hardware scanners.", "• "))

    subhead("6.3 Future Enhancements")
    body.append(make_bullet("Layer 2 Rollup Deployment: Deploying on Arbitrum, Optimism, or Polygon PoS to reduce transaction fees to fractions of a cent and achieve sub-second block finality.", "• "))
    body.append(make_bullet("Dynamic Time-Decaying QR Codes: Integrating cryptographic asymmetric signatures into dynamic QR codes scanned via mobile camera to prevent optical replay attacks.", "• "))
    body.append(make_bullet("IPFS Metadata & NFT Artwork: Storing rich event ticket multimedia and artist memorabilia on InterPlanetary File System (IPFS) or Arweave.", "• "))
    body.append(make_bullet("Account Abstraction (ERC-4337): Implementing sponsored paymasters so non-crypto attendees can interact seamlessly without possessing native cryptocurrency for gas fees.", "• "))
    body.append(make_page_break())

    # ================= PAGE 9: REFERENCES =================
    title("REFERENCES")
    refs = [
        ["[1]", "S. Nakamoto, \"Bitcoin: A Peer-to-Peer Electronic Cash System,\" Decentralized Business Review, 2008."],
        ["[2]", "V. Buterin, \"Ethereum: A Next-Generation Smart Contract and Decentralized Application Platform,\" Ethereum Whitepaper, 2014. [Online]. Available: https://ethereum.org/en/whitepaper/"],
        ["[3]", "W. Entriken, D. Shirley, J. Evans, and N. Sachs, \"ERC-721 Non-Fungible Token Standard,\" Ethereum Improvement Proposals, no. 721, Jan. 2018. [Online]. Available: https://eips.ethereum.org/EIPS/eip-721"],
        ["[4]", "OpenZeppelin, \"OpenZeppelin Contracts: A Library for Secure Smart Contract Development,\" 2024. [Online]. Available: https://docs.openzeppelin.com/contracts/"],
        ["[5]", "Hardhat Documentation, \"Ethereum Development Environment for Professionals,\" Nomic Foundation, 2024. [Online]. Available: https://hardhat.org/docs"],
        ["[6]", "R. Moore and E. Ethers, \"ethers.js: Complete Ethereum Library and Wallet Implementation in JavaScript,\" 2024. [Online]. Available: https://docs.ethers.org/v6/"],
        ["[7]", "Solidity Documentation, \"Solidity Programming Language Specification (v0.8.28),\" Ethereum Foundation, 2024. [Online]. Available: https://docs.soliditylang.org/"],
        ["[8]", "E. Weyl, P. Ohlhaver, and V. Buterin, \"Decentralized Society: Finding Web3's Soul,\" SSRN Electronic Journal, 2022."]
    ]
    for tag, ref_str in refs:
        p_ref = f"""<w:p>
  <w:pPr>
    <w:spacing w:before="60" w:after="120" w:line="260" w:lineRule="auto"/>
    <w:ind w:left="480" w:hanging="480"/>
  </w:pPr>
  <w:r>
    <w:rPr>
      <w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/>
      <w:b/>
      <w:color w:val="1F2438"/>
      <w:sz w:val="22"/>
    </w:rPr>
    <w:t xml:space="preserve">{escape_xml(tag)} </w:t>
  </w:r>
  <w:r>
    <w:rPr>
      <w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/>
      <w:color w:val="333333"/>
      <w:sz w:val="22"/>
    </w:rPr>
    <w:t xml:space="preserve">{escape_xml(ref_str)}</w:t>
  </w:r>
</w:p>"""
        body.append(p_ref)
    body.append(make_page_break())

    # ================= PAGE 10: APPENDIX =================
    title("APPENDIX")
    subhead("A.1 Full Source Code (EventTicket.sol)")
    sol_full = (
        "// SPDX-License-Identifier: MIT\n"
        "pragma solidity ^0.8.20;\n\n"
        "import \"@openzeppelin/contracts/token/ERC721/ERC721.sol\";\n"
        "import \"@openzeppelin/contracts/access/Ownable.sol\";\n\n"
        "contract EventTicket is ERC721, Ownable {\n"
        "    uint256 private _nextTokenId;\n"
        "    mapping(uint256 => bool) public isTicketUsed;\n"
        "    string public eventName;\n"
        "    string public eventDate;\n\n"
        "    event TicketVerified(uint256 indexed tokenId, address attendee);\n"
        "    event TicketMinted(uint256 indexed tokenId, address indexed attendee);\n\n"
        "    constructor(string memory _eventName, string memory _eventDate) \n"
        "        ERC721(\"EventTicket\", \"TKT\") \n"
        "        Ownable(msg.sender)\n"
        "    {\n"
        "        eventName = _eventName;\n"
        "        eventDate = _eventDate;\n"
        "        _nextTokenId = 1;\n"
        "    }\n\n"
        "    function mintTicket(address attendee) public onlyOwner returns (uint256) {\n"
        "        uint256 tokenId = _nextTokenId++;\n"
        "        _mint(attendee, tokenId);\n"
        "        emit TicketMinted(tokenId, attendee);\n"
        "        return tokenId;\n"
        "    }\n\n"
        "    function verifyTicket(uint256 tokenId) public onlyOwner {\n"
        "        require(_ownerOf(tokenId) != address(0), \"Ticket does not exist (fake ticket)\");\n"
        "        require(!isTicketUsed[tokenId], \"Ticket has already been used (duplicate)\");\n"
        "        isTicketUsed[tokenId] = true;\n"
        "        emit TicketVerified(tokenId, ownerOf(tokenId));\n"
        "    }\n\n"
        "    function isTicketValid(uint256 tokenId) public view returns (bool) {\n"
        "        return _ownerOf(tokenId) != address(0) && !isTicketUsed[tokenId];\n"
        "    }\n\n"
        "    function _update(address to, uint256 tokenId, address auth) internal virtual override returns (address) {\n"
        "        address from = _ownerOf(tokenId);\n"
        "        require(from == address(0) || to == address(0), \"Event tickets are non-transferable\");\n"
        "        return super._update(to, tokenId, auth);\n"
        "    }\n"
        "}"
    )
    code_block(sol_full)

    subhead("A.2 Project Architecture & Environment Details")
    p("Project Repository Structure:\n"
      "blockchain/\n"
      "├── contracts/EventTicket.sol\n"
      "├── test/EventTicket.js\n"
      "├── scripts/deploy.js\n"
      "├── hardhat.config.js\n"
      "├── frontend/\n"
      "│   ├── src/App.jsx (Attendee Wallet Generator & Verification Panel)\n"
      "│   ├── src/App.css (UI Layout & Badges)\n"
      "│   └── src/EventTicket.json (ABI Artifact)\n"
      "├── README.md\n"
      "└── Decentralized_Event_Ticket_Verification_Report.docx")

    # Final document XML construction
    doc_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
            xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <w:body>
    {''.join(body)}
    <w:sectPr>
      <w:pgSz w:w="12240" w:h="15840"/>
      <w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" w:header="720" w:footer="720" w:gutter="0"/>
      <w:cols w:space="720"/>
    </w:sectPr>
  </w:body>
</w:document>"""
    return doc_xml

def create_docx(filename):
    content_types = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
</Types>"""

    rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>"""

    doc_rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
</Relationships>"""

    styles = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:docDefaults>
    <w:rPrDefault>
      <w:rPr>
        <w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/>
        <w:sz w:val="22"/>
        <w:color w:val="222222"/>
      </w:rPr>
    </w:rPrDefault>
  </w:docDefaults>
  <w:style w:type="paragraph" w:default="1" w:styleId="Normal">
    <w:name w:val="Normal"/>
  </w:style>
  <w:style w:type="paragraph" w:styleId="ListParagraph">
    <w:name w:val="List Paragraph"/>
    <w:basedOn w:val="Normal"/>
  </w:style>
</w:styles>"""

    document_xml = build_document_xml()

    with zipfile.ZipFile(filename, 'w', zipfile.ZIP_DEFLATED) as docx:
        docx.writestr('[Content_Types].xml', content_types)
        docx.writestr('_rels/.rels', rels)
        docx.writestr('word/_rels/document.xml.rels', doc_rels)
        docx.writestr('word/styles.xml', styles)
        docx.writestr('word/document.xml', document_xml)

    print(f"Generated {filename} successfully!")

if __name__ == '__main__':
    create_docx(r"c:\Users\vaish\Desktop\blockchain\Decentralized_Event_Ticket_Verification_Report.docx")
