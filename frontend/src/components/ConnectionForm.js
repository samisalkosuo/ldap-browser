import React, { useState, useEffect } from 'react';
import { createConnection, getConnectionDefaults } from '../services/api';

const defaultFormData = {
  protocol: 'ldap',
  host: '',
  port: 389,
  bind_dn: '',
  username: '',
  password: '',
  base_dn: '',
  timeout_seconds: 10
};

const ConnectionForm = ({ onConnectionCreated, onCancel }) => {
  const [formData, setFormData] = useState(defaultFormData);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  // Fetch connection defaults from environment variables on mount
  useEffect(() => {
    const fetchDefaults = async () => {
      try {
        const defaults = await getConnectionDefaults();
        if (Object.keys(defaults).length > 0) {
          setFormData(prev => ({
            ...prev,
            ...defaults
          }));
        }
      } catch (err) {
        // Silently fail - defaults are optional
        console.log('No connection defaults available');
      }
    };
    
    fetchDefaults();
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'port' || name === 'timeout_seconds' ? parseInt(value) || 0 : value
    }));
  };

  const handleClear = () => {
    setFormData(defaultFormData);
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    const payload = {
      ...formData,
      name: `${formData.host || 'LDAP'}:${formData.port}`
    };

    try {
      const connection = await createConnection(payload);
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
        <div className="form-row">
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
              Common: 389, 636, 3268, 3269
            </small>
          </div>
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
          <button type="button" className="btn btn-secondary" onClick={handleClear} disabled={loading}>
            Clear
          </button>
        </div>
      </form>
    </div>
  );
};

export default ConnectionForm;

// Made with Bob
