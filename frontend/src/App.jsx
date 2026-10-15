import { useState, useEffect } from 'react'
import { ethers } from 'ethers'
import EventTicketArtifact from './EventTicket.json'
import './App.css'

// The deployed contract address on localhost
const CONTRACT_ADDRESS = "0x5FbDB2315678afecb367f032d93F642f64180aa3";

// Hardhat default account #0 (Organizer)
const ORGANIZER_PK = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80";

function App() {
  const [account, setAccount] = useState("");
  const [contract, setContract] = useState(null);
  const [eventName, setEventName] = useState("");
  
  // Form states
  const [attendeeName, setAttendeeName] = useState("");
  const [verifyTokenId, setVerifyTokenId] = useState("");
  const [status, setStatus] = useState("");
  
  // Dashboard state
  const [ticketsList, setTicketsList] = useState([]);

  useEffect(() => {
    connectLocalNode();
  }, []);

  const connectLocalNode = async () => {
    try {
      const provider = new ethers.JsonRpcProvider("http://127.0.0.1:8545/");
      const wallet = new ethers.Wallet(ORGANIZER_PK, provider);
      setAccount(wallet.address);
      
      const ticketContract = new ethers.Contract(
        CONTRACT_ADDRESS,
        EventTicketArtifact.abi,
        wallet
      );
      
      setContract(ticketContract);
      
      const name = await ticketContract.eventName();
      setEventName(name);

      // Load all tickets initially
      loadTickets(ticketContract);

    } catch (err) {
      console.error(err);
      setStatus("Error connecting to local Hardhat node. Make sure the node is running.");
    }
  };

  const getAddressBook = () => {
    const data = localStorage.getItem('addressBook');
    return data ? JSON.parse(data) : {};
  };

  const saveToAddressBook = (address, name) => {
    const book = getAddressBook();
    book[address.toLowerCase()] = name;
    localStorage.setItem('addressBook', JSON.stringify(book));
  };

  const loadTickets = async (ticketContract) => {
    try {
      // Fetch all TicketMinted events
      const mintFilter = ticketContract.filters.TicketMinted();
      const mintEvents = await ticketContract.queryFilter(mintFilter);
      
      const ticketsData = [];
      const addressBook = getAddressBook();
      
      // For each mint event, check its current status
      for (const event of mintEvents) {
        const tokenId = event.args.tokenId;
        const attendee = event.args.attendee;
        
        // Check if ticket has been used
        const isUsed = await ticketContract.isTicketUsed(tokenId);
        
        // Find if we generated a name for this address
        const displayName = addressBook[attendee.toLowerCase()] || "Unknown User";
        
        ticketsData.push({
          tokenId: tokenId.toString(),
          owner: attendee,
          displayName: displayName,
          isUsed: isUsed
        });
      }
      
      // Sort by tokenId descending (newest first)
      ticketsData.sort((a, b) => Number(b.tokenId) - Number(a.tokenId));
      setTicketsList(ticketsData);
    } catch (err) {
      console.error("Error loading tickets", err);
    }
  };

  const mintTicket = async (e) => {
    e.preventDefault();
    if (!contract || !attendeeName) return;
    
    try {
      setStatus(`Generating secure wallet for ${attendeeName}...`);
      
      // Generate a totally new, random Ethereum wallet for the attendee
      const newWallet = ethers.Wallet.createRandom();
      const newAddress = newWallet.address;
      
      // Save the mapping so we remember who this wallet belongs to
      saveToAddressBook(newAddress, attendeeName);
      
      setStatus(`Minting ticket to new wallet: ${newAddress}...`);
      
      // Mint to the newly generated address
      const tx = await contract.mintTicket(newAddress);
      await tx.wait();
      
      setStatus(`Success! Ticket minted for ${attendeeName}. Generated Wallet: ${newAddress}`);
      setAttendeeName("");
      
      // Refresh ticket list
      loadTickets(contract);
    } catch (err) {
      console.error(err);
      setStatus("Error minting ticket. Make sure you are the contract owner.");
    }
  };

  const verifyTicket = async (e) => {
    e.preventDefault();
    if (!contract || !verifyTokenId) return;
    
    try {
      setStatus(`Verifying ticket #${verifyTokenId}...`);
      const tx = await contract.verifyTicket(verifyTokenId);
      await tx.wait();
      setStatus(`Success! Ticket #${verifyTokenId} verified and marked as used.`);
      setVerifyTokenId("");
      
      // Refresh ticket list
      loadTickets(contract);
    } catch (err) {
      console.error(err);
      setStatus("Error verifying ticket. It may be a duplicate or fake.");
    }
  };

  const checkValidity = async () => {
    if (!contract || !verifyTokenId) return;
    try {
      const isValid = await contract.isTicketValid(verifyTokenId);
      if (isValid) {
        setStatus(`Ticket #${verifyTokenId} is VALID and unused.`);
      } else {
        setStatus(`Ticket #${verifyTokenId} is INVALID (fake or already used).`);
      }
    } catch(err) {
      console.error(err);
      setStatus("Error checking ticket validity.");
    }
  };

  return (
    <div className="App">
      <header>
        <h1>{eventName || "Decentralized Ticketing System"}</h1>
        {account ? (
          <div>
            <p><strong>Organizer Wallet:</strong> {account}</p>
          </div>
        ) : (
          <p>Connecting to local node...</p>
        )}
      </header>

      <main>
        {status && <div className="status-box" style={{wordBreak: 'break-all'}}>{status}</div>}

        <div className="grid-container">
          <div className="left-column">
            <section className="card">
              <h2>Mint New Ticket</h2>
              <form onSubmit={mintTicket}>
                <label>Attendee Name:</label>
                <input 
                  type="text" 
                  placeholder="e.g. John Doe" 
                  value={attendeeName}
                  onChange={(e) => setAttendeeName(e.target.value)}
                  required
                />
                <button type="submit">Generate Wallet & Mint Ticket</button>
              </form>
            </section>

            <section className="card">
              <h2>Verify Ticket at Gate</h2>
              <form onSubmit={verifyTicket}>
                <label>Token ID to Verify:</label>
                <input 
                  type="number" 
                  placeholder="e.g. 1" 
                  value={verifyTokenId}
                  onChange={(e) => setVerifyTokenId(e.target.value)}
                  required
                />
                <div className="button-group">
                  <button type="button" onClick={checkValidity} className="secondary-btn">Check Validity</button>
                  <button type="submit">Verify & Mark Used</button>
                </div>
              </form>
            </section>
          </div>

          <div className="right-column">
            <section className="card">
              <h2>Ticket Database</h2>
              <p style={{fontSize: '0.9rem', color: '#666', marginBottom: '1rem'}}>
                Real-time view of all tickets on the blockchain.
              </p>
              
              {ticketsList.length === 0 ? (
                <p>No tickets minted yet.</p>
              ) : (
                <table className="ticket-table">
                  <thead>
                    <tr>
                      <th>Token ID</th>
                      <th>Attendee</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {ticketsList.map((ticket) => (
                      <tr key={ticket.tokenId}>
                        <td>#{ticket.tokenId}</td>
                        <td title={ticket.owner}>
                          <strong>{ticket.displayName}</strong>
                          <br />
                          <span style={{fontSize: '0.75rem', color: '#888'}}>
                            Wallet: {ticket.owner.substring(0,6)}...{ticket.owner.substring(38)}
                          </span>
                        </td>
                        <td>
                          {ticket.isUsed ? (
                            <span className="badge used">USED</span>
                          ) : (
                            <span className="badge valid">VALID</span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </section>
          </div>
        </div>
      </main>
    </div>
  )
}

export default App
