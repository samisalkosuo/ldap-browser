import React, { useState } from 'react';
import { FaSearch } from 'react-icons/fa';
import { searchLDAP } from '../services/api';

const SearchPanel = ({ connectionId, baseDn, onSelectEntry }) => {
  const [searchParams, setSearchParams] = useState({
    base_dn: baseDn || '',
    filter: '(objectClass=*)',
    scope: 'sub',
    size_limit: 100,
    time_limit: 10
  });
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [searched, setSearched] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setSearchParams(prev => ({
      ...prev,
      [name]: name === 'size_limit' || name === 'time_limit' ? parseInt(value) || 0 : value
    }));
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSearched(true);

    try {
      const searchResults = await searchLDAP(connectionId, searchParams);
      setResults(searchResults);
    } catch (err) {
      setError(err.response?.data?.detail || 'Search failed');
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const handleResultClick = (result) => {
    onSelectEntry({ dn: result.dn });
  };

  return (
    <div>
      <div className="search-panel">
        <form onSubmit={handleSearch} className="search-form">
          <div className="search-row">
            <input
              type="text"
              name="base_dn"
              value={searchParams.base_dn}
              onChange={handleChange}
              placeholder="Base DN"
              required
            />
          </div>
          
          <div className="search-row">
            <input
              type="text"
              name="filter"
              value={searchParams.filter}
              onChange={handleChange}
              placeholder="LDAP Filter"
              required
              style={{ flex: 2 }}
            />
            <select name="scope" value={searchParams.scope} onChange={handleChange}>
              <option value="base">Base</option>
              <option value="one">One Level</option>
              <option value="sub">Subtree</option>
            </select>
          </div>

          <div className="search-row">
            <input
              type="number"
              name="size_limit"
              value={searchParams.size_limit}
              onChange={handleChange}
              placeholder="Size Limit"
              min="1"
              max="1000"
              style={{ width: '120px' }}
            />
            <input
              type="number"
              name="time_limit"
              value={searchParams.time_limit}
              onChange={handleChange}
              placeholder="Time Limit (s)"
              min="1"
              max="60"
              style={{ width: '120px' }}
            />
            <button type="submit" className="btn btn-primary" disabled={loading}>
              <FaSearch /> {loading ? 'Searching...' : 'Search'}
            </button>
          </div>
        </form>
      </div>

      {error && (
        <div style={{ padding: '1rem', backgroundColor: '#fee', color: '#c00', margin: '1rem' }}>
          {error}
        </div>
      )}

      {searched && !loading && (
        <div className="search-results">
          <h3 style={{ marginBottom: '1rem', color: '#2c3e50' }}>
            Results: {results.length}
          </h3>
          
          {results.length === 0 ? (
            <div style={{ padding: '2rem', textAlign: 'center', color: '#7f8c8d' }}>
              No results found
            </div>
          ) : (
            results.map((result, idx) => (
              <div
                key={idx}
                className="search-result-item"
                onClick={() => handleResultClick(result)}
              >
                <div className="search-result-dn">{result.dn}</div>
                <div className="search-result-classes">
                  {result.objectClasses.join(', ')}
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
};

export default SearchPanel;

// Made with Bob
