import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Connection Management
export const createConnection = async (connectionData) => {
  const response = await api.post('/connections', connectionData);
  return response.data;
};

export const listConnections = async () => {
  const response = await api.get('/connections');
  return response.data;
};

export const getConnectionStatus = async (connectionId) => {
  const response = await api.get(`/connections/${connectionId}/status`);
  return response.data;
};

export const deleteConnection = async (connectionId) => {
  const response = await api.delete(`/connections/${connectionId}`);
  return response.data;
};

// LDAP Operations
export const getRootDSE = async (connectionId) => {
  const response = await api.get(`/connections/${connectionId}/root-dse`);
  return response.data;
};

export const getChildren = async (connectionId, dn = null) => {
  const params = dn ? { dn } : {};
  const response = await api.get(`/connections/${connectionId}/children`, { params });
  return response.data;
};

export const getEntry = async (connectionId, dn) => {
  const response = await api.get(`/connections/${connectionId}/entry`, {
    params: { dn }
  });
  return response.data;
};

export const searchLDAP = async (connectionId, searchParams) => {
  const response = await api.post(`/connections/${connectionId}/search`, searchParams);
  return response.data;
};

export default api;

// Made with Bob
