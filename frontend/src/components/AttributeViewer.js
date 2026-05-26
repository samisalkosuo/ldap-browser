import React, { useState, useEffect } from 'react';
import { FaCopy } from 'react-icons/fa';
import { getEntry } from '../services/api';

const AttributeViewer = ({ connectionId, dn }) => {
  const [entry, setEntry] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [sortBy, setSortBy] = useState('name-asc');
  const [copiedAttribute, setCopiedAttribute] = useState('');

  useEffect(() => {
    if (connectionId && dn) {
      loadEntry();
    }
  }, [connectionId, dn]);

  const loadEntry = async () => {
    setLoading(true);
    setError('');
    try {
      const entryData = await getEntry(connectionId, dn);
      setEntry(entryData);
    } catch (err) {
      setError('Failed to load entry details');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = (text, attributeName) => {
    navigator.clipboard.writeText(text).then(() => {
      setCopiedAttribute(attributeName);
      setTimeout(() => setCopiedAttribute(''), 2000);
    });
  };

  const sortAttributes = (attributes) => {
    const sorted = [...attributes];
    
    switch (sortBy) {
      case 'name-asc':
        sorted.sort((a, b) => a.name.localeCompare(b.name));
        break;
      case 'name-desc':
        sorted.sort((a, b) => b.name.localeCompare(a.name));
        break;
      case 'type':
        sorted.sort((a, b) => a.type.localeCompare(b.type));
        break;
      case 'size':
        sorted.sort((a, b) => b.size_bytes - a.size_bytes);
        break;
      default:
        break;
    }
    
    return sorted;
  };

  if (loading) {
    return <div className="loading">Loading entry details...</div>;
  }

  if (error) {
    return (
      <div style={{ padding: '2rem', color: '#e74c3c' }}>
        {error}
        <button onClick={loadEntry} className="btn btn-secondary" style={{ marginTop: '1rem' }}>
          Retry
        </button>
      </div>
    );
  }

  if (!entry) {
    return (
      <div className="empty-state">
        <div className="empty-state-icon">📋</div>
        <h3>No Entry Selected</h3>
        <p>Select an entry from the tree to view its attributes</p>
      </div>
    );
  }

  const sortedAttributes = sortAttributes(entry.attributes);

  return (
    <div className="entry-details">
      <div className="entry-header">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
          <div style={{ flex: 1 }}>
            <h2 style={{ fontSize: '1rem', color: '#7f8c8d', marginBottom: '0.5rem' }}>
              Distinguished Name
            </h2>
            <div className="entry-dn">{entry.dn}</div>
          </div>
          <button
            className="copy-btn"
            onClick={() => handleCopy(entry.dn, 'dn')}
            title="Copy DN"
          >
            <FaCopy /> {copiedAttribute === 'dn' ? 'Copied!' : 'Copy DN'}
          </button>
        </div>

        <div style={{ marginTop: '1.5rem' }}>
          <h3 style={{ fontSize: '0.9rem', color: '#7f8c8d', marginBottom: '0.5rem' }}>
            Object Classes
          </h3>
          <div className="entry-classes">
            {entry.object_classes.map((oc, idx) => (
              <span key={idx} className="class-badge">{oc}</span>
            ))}
          </div>
        </div>
      </div>

      <div className="attributes-section">
        <div className="attributes-header">
          <h3>Attributes ({entry.attributes.length})</h3>
          <div className="sort-controls">
            <label style={{ fontSize: '0.85rem', color: '#7f8c8d' }}>Sort by:</label>
            <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
              <option value="name-asc">Name (A-Z)</option>
              <option value="name-desc">Name (Z-A)</option>
              <option value="type">Type</option>
              <option value="size">Size</option>
            </select>
          </div>
        </div>

        <table className="attributes-table">
          <thead>
            <tr>
              <th>Attribute</th>
              <th>Value</th>
              <th>Type</th>
              <th>Size</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {sortedAttributes.map((attr, idx) => (
              <tr key={idx}>
                <td style={{ fontWeight: 500, color: '#2c3e50' }}>
                  {attr.name}
                  {attr.multi_value && (
                    <span style={{ 
                      marginLeft: '0.5rem', 
                      fontSize: '0.75rem', 
                      color: '#7f8c8d' 
                    }}>
                      [{attr.values.length}]
                    </span>
                  )}
                </td>
                <td>
                  {attr.multi_value ? (
                    <div className="attribute-value multi">
                      {attr.values.map((val, vidx) => (
                        <div key={vidx} className="attribute-value-item">
                          {val}
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="attribute-value">
                      {attr.values[0] || '(empty)'}
                    </div>
                  )}
                </td>
                <td>
                  <span className="type-badge">{attr.type}</span>
                </td>
                <td style={{ color: '#7f8c8d', fontSize: '0.85rem' }}>
                  {attr.size_bytes} bytes
                </td>
                <td>
                  <button
                    className="copy-btn"
                    onClick={() => handleCopy(attr.values.join('\n'), attr.name)}
                    title="Copy value"
                  >
                    <FaCopy />
                    {copiedAttribute === attr.name ? ' ✓' : ''}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default AttributeViewer;

// Made with Bob
