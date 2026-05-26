import React, { useState } from 'react';
import { createConnection } from '../services/api';

const ConnectionForm = ({ onConnectionCreated, onCancel }) => {
  const [formData, setFormData] = useState({
    name: '',
    protocol: 'ldap',
    host: '',
    port: 389,
    bind_dn: '',
    username: '',
    password: '',
    base_dn: '',
    timeout_seconds: 10
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'port' || name === 'timeout_seconds' ? parseInt(value) || 0 : value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const connection = await createConnection(formData);
      onConnectionCreated(connection);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create connection');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="connection-form">
      <h2>New LDAP Connection</h2>
      
      {error && <div className="error-message">{error}</div>}
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Connection Name *</label>
          <input
            type="text"
            name="name"
            value={formData.name}
            onChange={handleChange}
            required
            placeholder="My LDAP Server"
          />
        </div>

        <div className="form-group">
          <label>Protocol *</label>
          <select
            name="protocol"
            value={formData.protocol}
            onChange={handleChange}
            required
          >
            <option value="ldap">ldap:// (Unencrypted)</option>
            <option value="ldaps">ldaps:// (Encrypted/TLS)</option>
          </select>
          <small style={{ color: '#7f8c8d', fontSize: '0.85rem' }}>
            Select ldaps:// for secure connections
          </small>
        </div>

        <div className="form-group">
          <label>Host *</label>
          <input
            type="text"
            name="host"
            value={formData.host}
            onChange={handleChange}
            required
            placeholder="ldap.example.com"
          />
        </div>

        <div className="form-group">
          <label>Port *</label>
          <input
            type="number"
            name="port"
            value={formData.port}
            onChange={handleChange}
            required
            placeholder="389"
          />
          <small style={{ color: '#7f8c8d', fontSize: '0.85rem' }}>
            Common ports: 389 (LDAP), 636 (LDAPS), 3268 (AD Global Catalog), 3269 (AD GC SSL)
          </small>
        </div>

        <div className="form-group">
          <label>Bind DN</label>
          <input
            type="text"
            name="bind_dn"
            value={formData.bind_dn}
            onChange={handleChange}
            placeholder="cn=admin,dc=example,dc=com"
          />
          <small style={{ color: '#7f8c8d', fontSize: '0.85rem' }}>
            Full distinguished name for binding
          </small>
        </div>

        <div className="form-group">
          <label>Username</label>
          <input
            type="text"
            name="username"
            value={formData.username}
            onChange={handleChange}
            placeholder="admin"
          />
          <small style={{ color: '#7f8c8d', fontSize: '0.85rem' }}>
            Alternative to Bind DN (if supported by server)
          </small>
        </div>

        <div className="form-group">
          <label>Password</label>
          <input
            type="password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            placeholder="••••••••"
          />
        </div>

        <div className="form-group">
          <label>Base DN (optional)</label>
          <input
            type="text"
            name="base_dn"
            value={formData.base_dn}
            onChange={handleChange}
            placeholder="dc=example,dc=com"
          />
          <small style={{ color: '#7f8c8d', fontSize: '0.85rem' }}>
            Leave empty for auto-discovery
          </small>
        </div>

        <div className="form-group">
          <label>Timeout (seconds)</label>
          <input
            type="number"
            name="timeout_seconds"
            value={formData.timeout_seconds}
            onChange={handleChange}
            min="1"
            max="60"
          />
        </div>

        <div className="form-actions">
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? 'Connecting...' : 'Connect'}
          </button>
          {onCancel && (
            <button type="button" className="btn btn-secondary" onClick={onCancel}>
              Cancel
            </button>
          )}
        </div>
      </form>
    </div>
  );
};

export default ConnectionForm;

// Made with Bob
