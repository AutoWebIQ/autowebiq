// API Service V2 - New endpoints with async builds
// Uses PostgreSQL backend and Celery task queue

import axios from 'axios';

const API_V2 = `${process.env.REACT_APP_BACKEND_URL}/api/v2`;

// Get axios config with auth token
const getAxiosConfig = () => {
  const token = localStorage.getItem('token');
  return {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  };
};

// ==================== User Endpoints ====================

export const getUserInfo = async () => {
  const response = await axios.get(`${API_V2}/user/me`, getAxiosConfig());
  return response.data;
};

export const getUserCredits = async () => {
  const response = await axios.get(`${API_V2}/user/credits`, getAxiosConfig());
  return response.data;
};

export const getUserStats = async () => {
  const response = await axios.get(`${API_V2}/stats`, getAxiosConfig());
  return response.data;
};

// ==================== Project Endpoints ====================

export const listProjects = async (limit = 50, offset = 0) => {
  const response = await axios.get(
    `${API_V2}/projects?limit=${limit}&offset=${offset}`,
    getAxiosConfig()
  );
  return response.data;
};

export const getProject = async (projectId) => {
  const response = await axios.get(
    `${API_V2}/projects/${projectId}`,
    getAxiosConfig()
  );
  return response.data;
};

export const startAsyncBuild = async (projectId, prompt, uploadedImages = []) => {
  const response = await axios.post(
    `${API_V2}/projects/${projectId}/build`,
    {
      prompt,
      uploaded_images: uploadedImages
    },
    getAxiosConfig()
  );
  return response.data;
};

export const getBuildStatus = async (projectId, taskId) => {
  const response = await axios.get(
    `${API_V2}/projects/${projectId}/build/status/${taskId}`,
    getAxiosConfig()
  );
  return response.data;
};

// ==================== Credit Endpoints ====================

export const getCreditHistory = async (limit = 50, offset = 0) => {
  const response = await axios.get(
    `${API_V2}/credits/history?limit=${limit}&offset=${offset}`,
    getAxiosConfig()
  );
  return response.data;
};

// ==================== Deployment Endpoints ====================

export const deployToVercel = async (projectId, projectName = null, environment = 'preview') => {
  const response = await axios.post(
    `${API_V2}/deploy/vercel`,
    {
      project_id: projectId,
      project_name: projectName,
      environment: environment
    },
    getAxiosConfig()
  );
  return response.data;
};

export const checkDeploymentStatus = async (deploymentId) => {
  const response = await axios.get(
    `${API_V2}/deploy/vercel/status/${deploymentId}`,
    getAxiosConfig()
  );
  return response.data;
};

// ==================== Helper Functions ====================

export const connectWebSocket = (projectId, onMessage) => {
  const token = localStorage.getItem('token');
  const wsUrl = `${process.env.REACT_APP_BACKEND_URL?.replace('http', 'ws')}/api/v2/ws/build/${projectId}?token=${token}`;
  
  const ws = new WebSocket(wsUrl);
  
  ws.onopen = () => {
    console.log('WebSocket connected');
  };
  
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (onMessage) {
      onMessage(data);
    }
  };
  
  ws.onerror = (error) => {
    console.error('WebSocket error:', error);
  };
  
  ws.onclose = () => {
    console.log('WebSocket disconnected');
  };
  
  return ws;
};

export default {
  getUserInfo,
  getUserCredits,
  getUserStats,
  listProjects,
  getProject,
  startAsyncBuild,
  getBuildStatus,
  getCreditHistory,
  deployToVercel,
  checkDeploymentStatus,
  connectWebSocket
};
