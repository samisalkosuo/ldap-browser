import React, { useState, useEffect } from 'react';
import { FaUser, FaUsers, FaFolder, FaGlobe, FaBox, FaQuestion, FaChevronRight, FaChevronDown } from 'react-icons/fa';
import { getChildren } from '../services/api';

const TreeNode = ({ node, connectionId, onSelectNode, selectedDn, level = 0 }) => {
  const [expanded, setExpanded] = useState(false);
  const [children, setChildren] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const isSelected = selectedDn === node.dn;

  const getIcon = (iconType) => {
    switch (iconType) {
      case 'user':
        return <FaUser />;
      case 'group':
        return <FaUsers />;
      case 'ou':
        return <FaFolder />;
      case 'domain':
        return <FaGlobe />;
      case 'container':
        return <FaBox />;
      default:
        return <FaQuestion />;
    }
  };

  const handleToggle = async () => {
    if (!node.has_children) return;

    if (!expanded && children.length === 0) {
      setLoading(true);
      setError('');
      try {
        const childNodes = await getChildren(connectionId, node.dn);
        setChildren(childNodes);
        setExpanded(true);
      } catch (err) {
        setError('Failed to load children');
        console.error(err);
      } finally {
        setLoading(false);
      }
    } else {
      setExpanded(!expanded);
    }
  };

  const handleSelect = () => {
    onSelectNode(node);
  };

  return (
    <div>
      <div
        className={`tree-node ${isSelected ? 'selected' : ''}`}
        style={{ paddingLeft: `${level * 1.5}rem` }}
      >
        <span
          onClick={handleToggle}
          style={{
            cursor: node.has_children ? 'pointer' : 'default',
            marginRight: '0.5rem',
            width: '1rem',
            display: 'inline-block'
          }}
        >
          {node.has_children && (
            expanded ? <FaChevronDown /> : <FaChevronRight />
          )}
        </span>
        <span className="tree-node-icon" onClick={handleSelect}>
          {getIcon(node.icon_type)}
        </span>
        <span className="tree-node-label" onClick={handleSelect}>
          {node.rdn}
        </span>
      </div>

      {loading && (
        <div className="loading" style={{ paddingLeft: `${(level + 1) * 1.5}rem` }}>
          Loading...
        </div>
      )}

      {error && (
        <div style={{ paddingLeft: `${(level + 1) * 1.5}rem`, color: '#e74c3c', fontSize: '0.85rem' }}>
          {error}
        </div>
      )}

      {expanded && children.length > 0 && (
        <div className="tree-children">
          {children.map((child) => (
            <TreeNode
              key={child.dn}
              node={child}
              connectionId={connectionId}
              onSelectNode={onSelectNode}
              selectedDn={selectedDn}
              level={level + 1}
            />
          ))}
        </div>
      )}
    </div>
  );
};

const TreeBrowser = ({ connectionId, baseDn, onSelectNode, selectedDn }) => {
  const [rootNodes, setRootNodes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (connectionId && baseDn) {
      loadRootNodes();
    }
  }, [connectionId, baseDn]);

  const loadRootNodes = async () => {
    setLoading(true);
    setError('');
    try {
      const nodes = await getChildren(connectionId, baseDn);
      
      // If no children, show the base DN itself as root
      if (nodes.length === 0) {
        setRootNodes([{
          dn: baseDn,
          rdn: baseDn,
          object_classes: [],
          has_children: true,
          icon_type: 'domain'
        }]);
      } else {
        setRootNodes(nodes);
      }
    } catch (err) {
      setError('Failed to load LDAP tree');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading LDAP tree...</div>;
  }

  if (error) {
    return (
      <div style={{ padding: '1rem', color: '#e74c3c' }}>
        {error}
        <button onClick={loadRootNodes} className="btn btn-secondary" style={{ marginTop: '1rem' }}>
          Retry
        </button>
      </div>
    );
  }

  if (rootNodes.length === 0) {
    return <div className="loading">No entries found</div>;
  }

  return (
    <div className="tree-container">
      {rootNodes.map((node) => (
        <TreeNode
          key={node.dn}
          node={node}
          connectionId={connectionId}
          onSelectNode={onSelectNode}
          selectedDn={selectedDn}
          level={0}
        />
      ))}
    </div>
  );
};

export default TreeBrowser;

// Made with Bob
