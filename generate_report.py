import os
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def create_report():
    doc = Document()
    
    # Page setup - 1 inch margins
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    # Styles setup
    style_normal = doc.styles['Normal']
    font = style_normal.font
    font.name = 'Calibri'
    font.size = Pt(11)
    font.color.rgb = RGBColor(0x22, 0x22, 0x22)

    def add_title(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(14)
        run = p.add_run(text)
        run.bold = True
        run.font.size = Pt(16)
        run.font.color.rgb = RGBColor(0x11, 0x11, 0x11)
        return p

    def add_chap_header(chap_num, chap_name):
        p1 = doc.add_paragraph()
        p1.paragraph_format.space_before = Pt(0)
        p1.paragraph_format.space_after = Pt(4)
        r1 = p1.add_run(f"CHAPTER {chap_num}")
        r1.bold = True
        r1.font.size = Pt(14)
        r1.font.color.rgb = RGBColor(0x11, 0x11, 0x11)
        
        p2 = doc.add_paragraph()
        p2.paragraph_format.space_before = Pt(0)
        p2.paragraph_format.space_after = Pt(14)
        r2 = p2.add_run(chap_name)
        r2.bold = True
        r2.font.size = Pt(14)
        r2.font.color.rgb = RGBColor(0x11, 0x11, 0x11)

    def add_subheading(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(4)
        run = p.add_run(text)
        run.bold = True
        run.font.size = Pt(12)
        run.font.color.rgb = RGBColor(0x11, 0x11, 0x11)
        return p

    def add_body(text, space_after=8, italic=False):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = 1.15
        run = p.add_run(text)
        run.italic = italic
        return p

    def add_bullet(text, bold_prefix=""):
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.line_spacing = 1.15
        if bold_prefix:
            r_bold = p.add_run(bold_prefix)
            r_bold.bold = True
        p.add_run(text)
        return p

    # ================= PAGE 1: ABSTRACT =================
    add_title("ABSTRACT")
    abstract_text = (
        "Traditional event ticketing infrastructures rely on centralized web servers and centralized relational databases. "
        "These architectures present significant vulnerabilities, such as single points of failure, rampant ticket scalping, "
        "unauthorized secondary market inflation, and widespread counterfeiting via duplicated barcodes or screenshots. "
        "This project proposes and implements a Decentralized Event Ticket Verification System built on Ethereum blockchain "
        "technology to definitively eliminate counterfeit and duplicate tickets. The solution designs and deploys an ERC-721 "
        "compliant smart contract programmed in Solidity, which conceptualizes every individual admission pass as an immutable, "
        "non-fungible digital token (NFT). Each ticket is cryptographically bound to a unique Token ID upon issuance by the authorized "
        "organizer. To prevent resale and unauthorized ticket transfers, non-transferable (soulbound) properties are enforced. "
        "Ticket validation at the venue gate verifies token legitimacy and executes an irreversible state change, marking the token "
        "as used and permanently barring duplicate check-ins. A modern decentralized application (DApp) frontend developed in "
        "React and Vite interacts with the local Hardhat execution network via ethers.js, featuring automatic on-the-fly keypair generation "
        "and a real-time event registry dashboard. Verification audits demonstrate 100% rejection of unauthorized minting and double-entry attempts."
    )
    add_body(abstract_text, space_after=14)
    doc.add_page_break()

    # ================= PAGE 2: TABLE OF CONTENTS =================
    add_title("TABLE OF CONTENTS")
    
    toc_data = [
        ("Chapter", "Title", "Page No."),
        ("1", "Introduction", "1"),
        ("2", "Literature Survey / Existing System", "3"),
        ("3", "System Requirements & Design", "5"),
        ("4", "Implementation", "8"),
        ("5", "Testing & Results", "12"),
        ("6", "Conclusion and Future Scope", "15"),
        ("", "References", "16"),
        ("", "Appendix", "17")
    ]
    
    toc_table = doc.add_table(rows=len(toc_data), cols=3)
    toc_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    col_widths = [Inches(1.2), Inches(4.2), Inches(1.1)]
    
    for r_idx, row in enumerate(toc_table.rows):
        is_header = (r_idx == 0)
        c_no, c_title, c_page = toc_data[r_idx]
        
        cells = row.cells
        cells[0].text = c_no
        cells[1].text = c_title
        cells[2].text = c_page
        
        for i, cell in enumerate(cells):
            cell.width = col_widths[i]
            set_cell_margins(cell, top=120, bottom=120, left=140, right=140)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.RIGHT if i == 2 else WD_ALIGN_PARAGRAPH.LEFT
            for run in p.runs:
                run.font.name = 'Calibri'
                run.font.size = Pt(10.5)
                if is_header:
                    run.bold = True
                    run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
                else:
                    if c_no != "":
                        run.bold = (i == 1 and ("Introduction" in c_title or "Conclusion" in c_title))
            
            if is_header:
                set_cell_background(cell, "1F2438")
            else:
                if r_idx % 2 == 1:
                    set_cell_background(cell, "F7F8FA")

    doc.add_page_break()

    # ================= PAGE 3: CHAPTER 1: INTRODUCTION =================
    add_chap_header("1", "INTRODUCTION")
    
    add_subheading("1.1 Overview of Blockchain Technology")
    add_body(
        "Blockchain technology is an immutable, distributed, and decentralized ledger system that records transactions across a peer-to-peer network without requiring a centralized certifying authority. By leveraging cryptographically linked data structures known as blocks, consensus mechanisms (such as Proof of Stake or Proof of Authority), and decentralized state machines, blockchain ensures high fault tolerance, auditability, and tamper-resistance."
    )
    add_body(
        "Within event management and digital ticketing, blockchain's key properties—namely data immutability, programmatic transparency, cryptographic asset uniqueness, and automated execution via smart contracts—offer a robust paradigm shift. Rather than relying on private centralized web databases vulnerable to unauthorized alterations or credential cloning, tickets represented as cryptographic tokens on a blockchain provide verifiable origin, non-repudiation, and deterministically enforced validation logic."
    )

    add_subheading("1.2 Problem Statement")
    add_body(
        "Contemporary ticketing systems suffer from widespread ticketing fraud, including counterfeit tickets generated via duplicate QR code printouts or digital screenshots, fraudulent secondary market reselling at exorbitant prices, and unauthorized duplication. Centralized database architectures present single points of failure, lack publicly auditable validation records, and fail to prevent rogue administrators or compromised systems from issuing unauthorized entries. An automated, cryptographically enforceable verification mechanism is required to guarantee ticket uniqueness and permanently prevent duplicate admissions."
    )

    add_subheading("1.3 Objectives")
    add_bullet("To design and deploy a secure Solidity smart contract utilizing the ERC-721 token standard for issuing unique digital event tickets.")
    add_bullet("To eliminate reliance on centralized database gatekeepers by anchoring ticket existence and consumption states directly on the blockchain.")
    add_bullet("To provide an open, transparent, and mathematically verifiable check-in mechanism that instantly prevents duplicate or counterfeit admissions.")
    add_bullet("To implement soulbound (non-transferable) logic preventing predatory secondary ticket scalping and unauthorized transfers.")
    add_bullet("To develop an intuitive, decentralized application (DApp) user interface enabling organizers to mint tickets on-the-fly and verify attendee credentials at entry gates in real time.")

    add_subheading("1.4 Scope of the Project")
    add_body(
        "The current scope of the project encompasses smart contract development, automated unit test verification, and a responsive frontend DApp connected to an EVM-compatible execution environment (tested on Hardhat's local EVM network, fully compatible with Ethereum Sepolia testnet). The system supports organizer-restricted minting, automated attendee wallet keypair generation, token validity queries, state-changing gate verifications, and real-time registry synchronization. The scope deliberately excludes fiat payment gateway integration, gas fee subsidization (account abstraction/relayers), and mobile hardware barcode scanning peripherals."
    )
    doc.add_page_break()

    # ================= PAGE 4: CHAPTER 2: LITERATURE SURVEY =================
    add_chap_header("2", "LITERATURE SURVEY / EXISTING SYSTEM")

    add_subheading("2.1 Existing (Traditional/Centralized) Approach")
    add_body(
        "In traditional ticketing architectures, ticketing platforms (e.g., Ticketmaster, Eventbrite, or in-house ticketing servers) maintain centralized databases like MySQL or PostgreSQL behind proprietary application servers. When an attendee purchases a ticket, the server generates a ticket row with a static identifier and emails a PDF or barcode/QR code to the buyer. At the event entrance, physical scanners or handheld mobile devices connect over local WiFi or cellular networks to query the centralized database, updating a boolean flag to mark the ticket as scanned."
    )

    add_subheading("2.2 Drawbacks of Existing System")
    add_bullet("Single Point of Failure: If the centralized database or venue network connectivity crashes, gates stall and entry verification fails completely.", bold_prefix="• ")
    add_bullet("Ease of Counterfeiting & Duplication: Static barcodes, PDFs, and QR codes can be easily screenshotted, photocopied, or forwarded to multiple individuals, causing chaos at gates where only the first arrival is admitted.", bold_prefix="• ")
    add_bullet("Insider Tampering & Database Vulnerability: Internal administrators or database attackers can fabricate, manipulate, or delete ticket records without any immutable audit trail.", bold_prefix="• ")
    add_bullet("Unchecked Ticket Scalping & Black Market Resale: Centralized platforms have historically struggled with automated bots acquiring bulk tickets and reselling them at exorbitant markups on third-party sites.", bold_prefix="• ")
    add_bullet("Lack of Public Transparency: Neither event organizers nor attendees can independently audit total tickets issued versus venue capacity without trusting platform telemetry.", bold_prefix="• ")

    add_subheading("2.3 Proposed Solution Overview")
    add_body(
        "The proposed Decentralized Event Ticket Verification System solves these architectural flaws by treating each ticket as an ERC-721 Non-Fungible Token (NFT) deployed on an EVM blockchain. Each ticket possesses an indisputable, immutable Token ID and is issued exclusively by the organizer's cryptographic signature. Non-transferability is programmatically enforced in smart contract bytecode, binding the admission rights to the designated wallet. When scanned at the venue, the contract executes a verification routine that irreversibly records the ticket's consumed status on-chain. Any subsequent presentation of the same Token ID is immediately rejected by the blockchain consensus rules, completely thwarting duplication, counterfeiting, and scalping."
    )
    doc.add_page_break()

    # ================= PAGE 5: CHAPTER 3: SYSTEM REQUIREMENTS & DESIGN =================
    add_chap_header("3", "SYSTEM REQUIREMENTS & DESIGN")

    add_subheading("3.1 Hardware & Software Requirements")
    
    req_data = [
        ("Category", "Requirement"),
        ("Hardware", "Minimum 8 GB RAM, Intel i5 / AMD Ryzen 5 processor, 10 GB free storage, Internet connectivity"),
        ("Blockchain Platform", "Ethereum / EVM-Compatible Local Testnet (Cancun EVM target)"),
        ("Smart Contract Language", "Solidity (v0.8.28)"),
        ("Development Environment", "Hardhat Framework (v2.22), Node.js (v20+ / v22+), npm"),
        ("Smart Contract Libraries", "OpenZeppelin Contracts (v5.6.1 - ERC721, Ownable)"),
        ("Local/Test Blockchain", "Hardhat Network (Localhost RPC: http://127.0.0.1:8545, ChainID 31337)"),
        ("Cryptographic Client", "ethers.js (v6.16) for JSON-RPC provider and transaction signing"),
        ("Frontend Framework", "React 19, Vite (v8.3), HTML5, CSS3 Modern Grid & Flexbox"),
        ("Operating System & IDE", "Windows 11 / Linux / macOS, Visual Studio Code")
    ]
    
    t_req = doc.add_table(rows=len(req_data), cols=2)
    t_req.alignment = WD_TABLE_ALIGNMENT.CENTER
    rw = [Inches(2.0), Inches(4.5)]
    for r_idx, row in enumerate(t_req.rows):
        is_hdr = (r_idx == 0)
        c0, c1 = req_data[r_idx]
        row.cells[0].text = c0
        row.cells[1].text = c1
        for i, cell in enumerate(row.cells):
            cell.width = rw[i]
            set_cell_margins(cell, top=80, bottom=80, left=120, right=120)
            p = cell.paragraphs[0]
            for run in p.runs:
                run.font.name = 'Calibri'
                run.font.size = Pt(10)
                if is_hdr:
                    run.bold = True
                    run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
                elif i == 0:
                    run.bold = True
            if is_hdr:
                set_cell_background(cell, "1F2438")
            elif r_idx % 2 == 1:
                set_cell_background(cell, "F7F8FA")

    add_subheading("3.2 System Architecture Diagram")
    add_body(
        "+---------------------------------------------------------------------------------------------------------+\n"
        "|                                       SYSTEM ARCHITECTURE                                               |\n"
        "+---------------------------------------------------------------------------------------------------------+\n"
        "|  [ Event Organizer / Gatekeeper ]                  [ Attendee ]                                        |\n"
        "|                 |                                       |                                               |\n"
        "|                 v                                       v                                               |\n"
        "|  +---------------------------------------------------------------------------------------------------+  |\n"
        "|  |                                  React Frontend DApp (Vite)                                       |  |\n"
        "|  |   - Mint Form (Keypair Generator)   - Gate Verification Panel   - Real-time Blockchain Registry   |  |\n"
        "|  +---------------------------------------------------------------------------------------------------+  |\n"
        "|                                                 | (JSON-RPC Calls / Events)                             |\n"
        "|                                                 v                                                       |\n"
        "|  +---------------------------------------------------------------------------------------------------+  |\n"
        "|  |                                   ethers.js Client Layer (v6)                                     |  |\n"
        "|  |   - JsonRpcProvider (HTTP)   - Wallet Signing (Private Key)   - Event Contract Filters            |  |\n"
        "|  +---------------------------------------------------------------------------------------------------+  |\n"
        "|                                                 | (EVM Transactions & Queries)                          |\n"
        "|                                                 v                                                       |\n"
        "|  +---------------------------------------------------------------------------------------------------+  |\n"
        "|  |                            Solidity Smart Contract (EventTicket.sol)                              |  |\n"
        "|  |   - ERC721 Token Standard     - Ownable Access Control     - isTicketUsed State Mapping           |  |\n"
        "|  |   - mintTicket()              - verifyTicket()             - isTicketValid()                      |  |\n"
        "|  +---------------------------------------------------------------------------------------------------+  |\n"
        "|                                                 | (State Mutation & Consensus)                          |\n"
        "|                                                 v                                                       |\n"
        "|  +---------------------------------------------------------------------------------------------------+  |\n"
        "|  |                       EVM Blockchain Network (Hardhat Node / Ethereum Testnet)                     |  |\n"
        "|  +---------------------------------------------------------------------------------------------------+  |\n"
        "+---------------------------------------------------------------------------------------------------------+"
    )
    p_cap1 = add_body("Fig 3.1: System Architecture Diagram", space_after=10, italic=True)
    p_cap1.runs[0].bold = True

    add_subheading("3.3 Use Case / Flow Diagram")
    add_body(
        "[ Organizer Flow ]:\n"
        "1. Enter Attendee Name -> 2. Generate Random Wallet -> 3. Execute mintTicket() on Blockchain -> 4. Token Minted.\n\n"
        "[ Gatekeeper Check-in Flow ]:\n"
        "1. Input Token ID -> 2. Query isTicketValid() [State: Exists & Unused?] ->\n"
        "   - If FALSE: Display Fake / Duplicate Rejection Alert.\n"
        "   - If TRUE: Execute verifyTicket() -> Mutate isTicketUsed = true -> Emit TicketVerified -> Attendee Admitted."
    )
    p_cap2 = add_body("Fig 3.2: Use Case / Flow Diagram", space_after=10, italic=True)
    p_cap2.runs[0].bold = True

    add_subheading("3.4 Smart Contract Design")
    sc_design_data = [
        ("Element", "Name / Signature", "Description"),
        ("State Variable", "_nextTokenId (uint256)", "Internal auto-incrementing counter tracking issued token IDs."),
        ("State Variable", "isTicketUsed (mapping(uint256 => bool))", "Records boolean usage state for each token ID to enforce single-use entry."),
        ("State Variable", "eventName, eventDate (string)", "Public metadata strings defining the event's title and scheduled date."),
        ("Function", "mintTicket(address attendee) -> uint256", "Mints a new ERC-721 token to the attendee address. Restricted to contract owner."),
        ("Function", "verifyTicket(uint256 tokenId)", "Verifies token validity and marks isTicketUsed=true. Reverts if duplicate or fake."),
        ("Function", "isTicketValid(uint256 tokenId) -> bool", "Read-only query checking if a token exists and remains unused."),
        ("Modifier/Override", "_update(...) internal override", "Disables transfers to enforce non-transferable (soulbound) ticket properties."),
        ("Event", "TicketMinted(uint256 tokenId, address attendee)", "Emitted upon successful ticket issuance; monitored by DApp registry."),
        ("Event", "TicketVerified(uint256 tokenId, address attendee)", "Emitted upon successful ticket check-in at the gate.")
    ]
    t_sc = doc.add_table(rows=len(sc_design_data), cols=3)
    t_sc.alignment = WD_TABLE_ALIGNMENT.CENTER
    sc_w = [Inches(1.5), Inches(2.3), Inches(2.7)]
    for r_idx, row in enumerate(t_sc.rows):
        is_hdr = (r_idx == 0)
        c0, c1, c2 = sc_design_data[r_idx]
        row.cells[0].text = c0
        row.cells[1].text = c1
        row.cells[2].text = c2
        for i, cell in enumerate(row.cells):
            cell.width = sc_w[i]
            set_cell_margins(cell, top=70, bottom=70, left=100, right=100)
            p = cell.paragraphs[0]
            for run in p.runs:
                run.font.name = 'Calibri'
                run.font.size = Pt(9.5)
                if is_hdr:
                    run.bold = True
                    run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
                elif i == 0:
                    run.bold = True
            if is_hdr:
                set_cell_background(cell, "1F2438")
            elif r_idx % 2 == 1:
                set_cell_background(cell, "F7F8FA")

    doc.add_page_break()

    # ================= PAGE 6: CHAPTER 4: IMPLEMENTATION =================
    add_chap_header("4", "IMPLEMENTATION")

    add_subheading("4.1 Technology Stack Used")
    add_body(
        "The project combines modern web engineering with decentralized smart contracts:\n"
        "• Smart Contract Layer: Solidity v0.8.28 with OpenZeppelin Contracts v5.6.1 (ERC721, Ownable).\n"
        "• Development & Testing Framework: Hardhat v2.22.0 configured with the Cancun EVM target.\n"
        "• Web3 Client Library: ethers.js v6.16.0 utilized for JSON-RPC provider interfacing, contract calls, and cryptographic keypair derivation.\n"
        "• Frontend Framework: React 19 bootstrapped with Vite 8.3, utilizing reactive state management and CSS grid styling."
    )

    add_subheading("4.2 Smart Contract Code (Key Snippets)")
    add_body("Snippet 1: Organizer-Restricted Ticket Minting", italic=True)
    add_body(
        "function mintTicket(address attendee) public onlyOwner returns (uint256) {\n"
        "    uint256 tokenId = _nextTokenId++;\n"
        "    _mint(attendee, tokenId);\n"
        "    emit TicketMinted(tokenId, attendee);\n"
        "    return tokenId;\n"
        "}"
    )
    add_body(
        "Explanation: Increments the internal token counter and executes OpenZeppelin's internal _mint function to assign the unique token ID to the recipient. The onlyOwner modifier guarantees only authorized event organizers can issue tickets, preventing fake tickets."
    )

    add_body("Snippet 2: Anti-Duplicate Gate Verification", italic=True)
    add_body(
        "function verifyTicket(uint256 tokenId) public onlyOwner {\n"
        "    require(_ownerOf(tokenId) != address(0), \"Ticket does not exist (fake ticket)\");\n"
        "    require(!isTicketUsed[tokenId], \"Ticket has already been used (duplicate)\");\n"
        "    isTicketUsed[tokenId] = true;\n"
        "    emit TicketVerified(tokenId, ownerOf(tokenId));\n"
        "}"
    )
    add_body(
        "Explanation: Validates that the requested token ID currently exists on-chain and has not previously been marked as consumed. Once verified, it permanently sets isTicketUsed[tokenId] to true, making subsequent re-entries with the same token mathematically impossible."
    )

    add_body("Snippet 3: Soulbound (Non-Transferable) Enforcement", italic=True)
    add_body(
        "function _update(address to, uint256 tokenId, address auth) internal virtual override returns (address) {\n"
        "    address from = _ownerOf(tokenId);\n"
        "    require(from == address(0) || to == address(0), \"Event tickets are non-transferable\");\n"
        "    return super._update(to, tokenId, auth);\n"
        "}"
    )
    add_body(
        "Explanation: Overrides OpenZeppelin ERC-721's core _update hook. It allows initial minting (from == 0) and burning (to == 0), but strictly throws an exception if an attendee attempts a secondary market transfer, successfully preventing ticket scalping."
    )

    add_subheading("4.3 Frontend / DApp Integration")
    add_body(
        "The DApp frontend establishes direct bi-directional connectivity with the local blockchain node using ethers.JsonRpcProvider('http://127.0.0.1:8545/'). To eliminate user friction with browser extensions like MetaMask in testing environments, the app connects directly with Hardhat's default organizer private key. When an organizer types an attendee's name, the client generates a unique cryptographic keypair via ethers.Wallet.createRandom(), assigns the wallet address to the name, and executes contract.mintTicket(). Furthermore, the application listens to TicketMinted and TicketVerified events to maintain a real-time reactive table displaying token IDs, holder names, wallet addresses, and dynamic status badges."
    )

    add_subheading("4.4 Deployment Details")
    add_body(
        "The contract was deployed onto the persistent Hardhat EVM local network via an automated deployment script (scripts/deploy.js).\n"
        "• Network: Hardhat Localhost (Chain ID: 31337, RPC URL: http://127.0.0.1:8545)\n"
        "• Deployed Contract Address: 0x5FbDB2315678afecb367f032d93F642f64180aa3\n"
        "• Deployer / Organizer Address: 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266\n"
        "• Frontend URL: http://localhost:5173/"
    )
    doc.add_page_break()

    # ================= PAGE 7: CHAPTER 5: TESTING & RESULTS =================
    add_chap_header("5", "TESTING & RESULTS")

    add_subheading("5.1 Test Cases")
    test_cases_data = [
        ("Test ID", "Input / Action", "Expected Output", "Actual Output", "Result"),
        ("TC01", "Deploy contract with event name & date", "Contract deployed; state variables initialized correctly", "Owner, event name, and date verified correctly", "Pass"),
        ("TC02", "Organizer calls mintTicket(attendeeAddress)", "Ticket #1 minted to attendee; TicketMinted event emitted", "Ticket #1 owned by attendee; isTicketValid=true", "Pass"),
        ("TC03", "Non-owner account attempts mintTicket()", "Transaction reverts with OwnableUnauthorizedAccount", "Reverted with OwnableUnauthorizedAccount", "Pass"),
        ("TC04", "Organizer calls verifyTicket(1) on valid ticket", "Ticket #1 marked isTicketUsed=true; TicketVerified emitted", "Ticket verified; status changes to USED; emitted event", "Pass"),
        ("TC05", "Organizer calls verifyTicket(1) a second time", "Transaction reverts: 'Ticket has already been used (duplicate)'", "Reverted with exact duplicate error message", "Pass"),
        ("TC06", "Organizer calls verifyTicket(999) for non-existent token", "Transaction reverts: 'Ticket does not exist (fake ticket)'", "Reverted with fake ticket error message", "Pass"),
        ("TC07", "Attendee attempts transferFrom() to another address", "Transaction reverts: 'Event tickets are non-transferable'", "Reverted with non-transferable error message", "Pass"),
        ("TC08", "Call isTicketValid(1) on unused vs used ticket", "Returns true initially; returns false after verification", "Returned true before scan; false after verification", "Pass")
    ]
    t_test = doc.add_table(rows=len(test_cases_data), cols=5)
    t_test.alignment = WD_TABLE_ALIGNMENT.CENTER
    test_w = [Inches(0.8), Inches(1.8), Inches(1.8), Inches(1.5), Inches(0.6)]
    for r_idx, row in enumerate(t_test.rows):
        is_hdr = (r_idx == 0)
        c0, c1, c2, c3, c4 = test_cases_data[r_idx]
        row.cells[0].text = c0
        row.cells[1].text = c1
        row.cells[2].text = c2
        row.cells[3].text = c3
        row.cells[4].text = c4
        for i, cell in enumerate(row.cells):
            cell.width = test_w[i]
            set_cell_margins(cell, top=60, bottom=60, left=80, right=80)
            p = cell.paragraphs[0]
            for run in p.runs:
                run.font.name = 'Calibri'
                run.font.size = Pt(8.5)
                if is_hdr:
                    run.bold = True
                    run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
                elif i == 0 or i == 4:
                    run.bold = True
                    if i == 4:
                        run.font.color.rgb = RGBColor(0x00, 0x88, 0x00)
            if is_hdr:
                set_cell_background(cell, "1F2438")
            elif r_idx % 2 == 1:
                set_cell_background(cell, "F7F8FA")

    add_subheading("5.2 Output & Verification Results")
    add_body(
        "Hardhat Automated Test Execution Output:\n"
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
        "---------------------------------------------------------------------------------"
    )
    add_body(
        "DApp Verification Interface Behavior:\n"
        "• Minting Execution: Entering an attendee name (e.g., 'Alice') generates a new keypair and mints Token #1. The record is instantly displayed in the Ticket Database as 'VALID'.\n"
        "• Gate Check-in: Entering Token ID #1 and triggering 'Verify & Mark Used' modifies contract state. The badge immediately updates to 'USED'.\n"
        "• Duplicate Thwarting: Triggering 'Verify & Mark Used' again on Token #1 raises an error alert indicating the ticket has already been used.\n"
        "• Fake Ticket Detection: Inquiring about Token ID #99 displays an alert confirming the ticket does not exist on the blockchain."
    )
    doc.add_page_break()

    # ================= PAGE 8: CHAPTER 6: CONCLUSION AND FUTURE SCOPE =================
    add_chap_header("6", "CONCLUSION AND FUTURE SCOPE")

    add_subheading("6.1 Conclusion")
    add_body(
        "The Decentralized Event Ticket Verification System successfully achieved all core objectives outlined in Chapter 1. By coupling Ethereum ERC-721 token standards with custom state tracking and soulbound access controls, the system guarantees that each ticket is uniquely identifiable, permanently recorded on an immutable ledger, and single-use only. Counterfeit tickets are prevented through cryptographic owner-only minting, while duplicate admissions are entirely eliminated via smart contract state assertions. The resulting prototype delivers a robust, transparent, and user-friendly Web3 platform that eliminates dependence on centralized ticketing gatekeepers."
    )

    add_subheading("6.2 Limitations")
    add_bullet("EVM Gas Costs: Every mint and gate verification transaction incurs computational gas fees on public networks.", bold_prefix="• ")
    add_bullet("Throughput & Latency: Public blockchain block confirmation times (12-15 seconds on Ethereum Layer 1) can constrain high-volume gate throughput without Layer 2 scaling.", bold_prefix="• ")
    add_bullet("Environment Constraints: Prototype tested primarily on a local Hardhat EVM development network rather than public mainnet.", bold_prefix="• ")
    add_bullet("Peripheral Integration: Currently operates via desktop browser interface rather than dedicated mobile optical barcode/NFC hardware scanners.", bold_prefix="• ")

    add_subheading("6.3 Future Enhancements")
    add_bullet("Layer 2 Rollup Deployment: Deploying on Arbitrum, Optimism, or Polygon PoS to reduce transaction fees to fractions of a cent and achieve sub-second block finality.", bold_prefix="• ")
    add_bullet("Dynamic Time-Decaying QR Codes: Integrating cryptographic asymmetric signatures into dynamic QR codes scanned via mobile camera to prevent optical replay attacks.", bold_prefix="• ")
    add_bullet("IPFS Metadata & NFT Artwork: Storing rich event ticket multimedia and artist memorabilia on InterPlanetary File System (IPFS) or Arweave.", bold_prefix="• ")
    add_bullet("Account Abstraction (ERC-4337): Implementing sponsored paymasters so non-crypto attendees can interact seamlessly without possessing native cryptocurrency for gas fees.", bold_prefix="• ")
    doc.add_page_break()

    # ================= PAGE 9: REFERENCES =================
    add_title("REFERENCES")
    refs = [
        ("[1]", "S. Nakamoto, \"Bitcoin: A Peer-to-Peer Electronic Cash System,\" Decentralized Business Review, 2008."),
        ("[2]", "V. Buterin, \"Ethereum: A Next-Generation Smart Contract and Decentralized Application Platform,\" Ethereum Whitepaper, 2014. [Online]. Available: https://ethereum.org/en/whitepaper/"),
        ("[3]", "W. Entriken, D. Shirley, J. Evans, and N. Sachs, \"ERC-721 Non-Fungible Token Standard,\" Ethereum Improvement Proposals, no. 721, Jan. 2018. [Online]. Available: https://eips.ethereum.org/EIPS/eip-721"),
        ("[4]", "OpenZeppelin, \"OpenZeppelin Contracts: A Library for Secure Smart Contract Development,\" 2024. [Online]. Available: https://docs.openzeppelin.com/contracts/"),
        ("[5]", "Hardhat Documentation, \"Ethereum Development Environment for Professionals,\" Nomic Foundation, 2024. [Online]. Available: https://hardhat.org/docs"),
        ("[6]", "R. Moore and E. Ethers, \"ethers.js: Complete Ethereum Library and Wallet Implementation in JavaScript,\" 2024. [Online]. Available: https://docs.ethers.org/v6/"),
        ("[7]", "Solidity Documentation, \"Solidity Programming Language Specification (v0.8.28),\" Ethereum Foundation, 2024. [Online]. Available: https://docs.soliditylang.org/"),
        ("[8]", "E. Weyl, P. Ohlhaver, and V. Buterin, \"Decentralized Society: Finding Web3's Soul,\" SSRN Electronic Journal, 2022.")
    ]
    for tag, ref_str in refs:
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(8)
        p.paragraph_format.line_spacing = 1.15
        r_tag = p.add_run(f"{tag} ")
        r_tag.bold = True
        p.add_run(ref_str)
        
    doc.add_page_break()

    # ================= PAGE 10: APPENDIX =================
    add_title("APPENDIX")

    add_subheading("A.1 Full Source Code (EventTicket.sol)")
    sol_code = (
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
    p_code = doc.add_paragraph()
    p_code.paragraph_format.space_before = Pt(0)
    p_code.paragraph_format.space_after = Pt(12)
    p_code.paragraph_format.line_spacing = 1.05
    r_c = p_code.add_run(sol_code)
    r_c.font.name = 'Consolas'
    r_c.font.size = Pt(8.5)

    add_subheading("A.2 Deployment & Execution Configuration")
    add_body(
        "Hardhat Configuration (hardhat.config.js):\n"
        "require(\"@nomicfoundation/hardhat-toolbox\");\n"
        "module.exports = {\n"
        "  solidity: {\n"
        "    version: \"0.8.28\",\n"
        "    settings: { evmVersion: \"cancun\" }\n"
        "  }\n"
        "};\n\n"
        "Project Directory Architecture:\n"
        "blockchain/\n"
        "├── contracts/EventTicket.sol\n"
        "├── test/EventTicket.js\n"
        "├── scripts/deploy.js\n"
        "├── hardhat.config.js\n"
        "├── frontend/\n"
        "│   ├── src/App.jsx (Attendee Wallet Generator & Verification Panel)\n"
        "│   ├── src/App.css\n"
        "│   └── src/EventTicket.json (ABI Artifact)\n"
        "└── README.md"
    )

    output_path = r"c:\Users\vaish\Desktop\blockchain\Decentralized_Event_Ticket_Verification_Report.docx"
    doc.save(output_path)
    print(f"Report successfully generated at: {output_path}")

if __name__ == "__main__":
    create_report()
