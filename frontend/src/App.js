import React, { useState, useEffect } from 'react';
import { FaLock, FaExclamationTriangle, FaTimes, FaSearch } from 'react-icons/fa';
import './App.css';
import ConnectionForm from './components/ConnectionForm';
import TreeBrowser from './components/TreeBrowser';
import AttributeViewer from './components/AttributeViewer';
import SearchPanel from './components/SearchPanel';
import { listConnections, deleteConnection, getCertificateChain } from './services/api';

function App() {
  const [connections, setConnections] = useState([]);
  const [currentConnection, setCurrentConnection] = useState(null);
  const [showConnectionForm, setShowConnectionForm] = useState(true);
  const [selectedNode, setSelectedNode] = useState(null);
  const [showSearch, setShowSearch] = useState(false);

  useEffect(() => {
    loadConnections();
  }, []);

  const loadConnections = async () => {
    try {
      const conns = await listConnections();
      setConnections(conns);
      
      // If we have a current connection, update it
      if (currentConnection) {
        const updated = conns.find(c => c.connection_id === currentConnection.connection_id);
        if (updated) {
          setCurrentConnection(updated);
        }
      }
    } catch (err) {
      console.error('Failed to load connections:', err);
    }
  };

  const handleConnectionCreated = (connection) => {
    setShowConnectionForm(false);
    setCurrentConnection(connection);
    loadConnections();
  };

  const handleDisconnect = async () => {
    if (currentConnection) {
      try {
        await deleteConnection(currentConnection.connection_id);
        setCurrentConnection(null);
        setSelectedNode(null);
        setShowConnectionForm(true);
        loadConnections();
      } catch (err) {
        console.error('Failed to disconnect:', err);
      }
    }
  };

  const handleSelectNode = (node) => {
    setSelectedNode(node);
    setShowSearch(false);
  };

  const handleViewCertificate = async (connectionId) => {
    try {
      const data = await getCertificateChain(connectionId);
      if (data.certificate_pem) {
        // Open a new window with the certificate
        const certWindow = window.open('', '_blank');
        if (certWindow) {
          certWindow.document.write('<html><head><title>Certificate Chain</title></head><body>');
          certWindow.document.write('<pre style="font-family: monospace; white-space: pre-wrap; word-wrap: break-word;">');
          certWindow.document.write(data.certificate_pem);
          certWindow.document.write('</pre></body></html>');
          certWindow.document.close();
        }
      }
    } catch (err) {
      console.error('Failed to fetch certificate:', err);
      alert('Failed to retrieve certificate chain');
    }
  };

  const getSecurityBadge = (connection) => {
    if (!connection) return null;

    const { security_mode, certificate_status, connection_id } = connection;

    if (security_mode === 'plain') {
      return (
        <span className="security-badge plain">
          <FaExclamationTriangle /> Unencrypted
        </span>
      );
    }

    if (certificate_status === 'self_signed' || certificate_status === 'untrusted') {
      return (
        <button
          className="security-badge self-signed"
          onClick={() => handleViewCertificate(connection_id)}
          style={{ cursor: 'pointer', border: 'none', background: 'transparent', padding: 0 }}
          title="Click to view certificate chain"
        >
          <FaExclamationTriangle /> Self-Signed Cert
        </button>
      );
    }

    return (
      <span className="security-badge secure">
        <FaLock /> Encrypted
      </span>
    );
  };

  return (
    <div className="app">
      <header className="header">
        <h1>LDAP Browser</h1>
        
        <div className="header-info">
          {currentConnection ? (
            <>
              <div className="connection-selector">
                <span style={{ color: '#ecf0f1', fontSize: '0.9rem' }}>
                  {currentConnection.name} ({currentConnection.host}:{currentConnection.port})
                </span>
              </div>
              
              {getSecurityBadge(currentConnection)}
              
              {currentConnection.base_dn && (
                <span style={{ color: '#ecf0f1', fontSize: '0.85rem' }}>
                  Base: {currentConnection.base_dn}
                </span>
              )}
              
              <button className="btn btn-secondary" onClick={() => setShowSearch(!showSearch)}>
                <FaSearch /> Search
              </button>
              
              <button className="btn btn-danger" onClick={handleDisconnect}>
                <FaTimes /> Disconnect
              </button>
            </>
          ) : null}
        </div>
      </header>

      <div className="main-content">
        {showConnectionForm ? (
          <ConnectionForm
            onConnectionCreated={handleConnectionCreated}
            onCancel={() => setShowConnectionForm(false)}
          />
        ) : currentConnection ? (
          <>
            {showSearch ? (
              <div style={{ flex: 1, overflow: 'auto' }}>
                <SearchPanel
                  connectionId={currentConnection.connection_id}
                  baseDn={currentConnection.base_dn}
                  onSelectEntry={handleSelectNode}
                />
              </div>
            ) : (
              <>
                <div className="left-panel">
                  <TreeBrowser
                    connectionId={currentConnection.connection_id}
                    baseDn={currentConnection.base_dn}
                    onSelectNode={handleSelectNode}
                    selectedDn={selectedNode?.dn}
                  />
                </div>
                
                <div className="right-panel">
                  <AttributeViewer
                    connectionId={currentConnection.connection_id}
                    dn={selectedNode?.dn}
                  />
                </div>
              </>
            )}
          </>
        ) : null}
      </div>
    </div>
  );
}

export default App;

// Made with Bob
