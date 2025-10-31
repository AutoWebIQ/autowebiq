// Enhanced Workspace with V2 API and WebSocket Support
// Real-time build updates with async Celery tasks

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'sonner';
import { Send, Loader2, Sparkles, Rocket, ExternalLink, CheckCircle, XCircle, AlertCircle } from 'lucide-react';
import { useBuildWebSocket } from '../hooks/useBuildWebSocket';
import { startAsyncBuild, getBuildStatus, deployToVercel, validateWebsite } from '../services/apiV2';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const WorkspaceV2 = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [project, setProject] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [buildingAsync, setBuildingAsync] = useState(false);
  const [currentTaskId, setCurrentTaskId] = useState(null);
  const [userCredits, setUserCredits] = useState(0);
  const [deploying, setDeploying] = useState(false);
  const [deploymentUrl, setDeploymentUrl] = useState(null);
  const messagesEndRef = useRef(null);

  const getAxiosConfig = () => ({
    headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
    withCredentials: true
  });

  // WebSocket message handler
  const handleWebSocketMessage = useCallback((data) => {
    console.log('WebSocket message:', data);

    if (data.type === 'connection') {
      console.log('WebSocket connection established');
      return;
    }

    if (data.type === 'agent_message') {
      // Add agent message to chat
      const agentEmoji = {
        'planner': '🧠',
        'frontend': '🎨',
        'backend': '⚙️',
        'image': '🖼️',
        'testing': '🧪',
        'initializing': '🚀',
        'building': '🏗️'
      }[data.agent_type] || '💬';

      const statusText = data.status === 'working' ? 'working...' : data.status;
      
      setMessages(prev => [...prev, {
        role: 'system',
        content: `${agentEmoji} **${data.agent_type} Agent** [${data.progress}%]: ${data.message}`,
        created_at: new Date().toISOString()
      }]);
    }

    if (data.type === 'build_progress') {
      console.log('Build progress:', data.data);
    }

    if (data.type === 'build_complete') {
      setBuildingAsync(false);
      setCurrentTaskId(null);
      
      // Update project with generated code
      if (data.result && data.result.generated_code) {
        setProject(prev => ({
          ...prev,
          generated_code: data.result.generated_code
        }));
      }

      setMessages(prev => [...prev, {
        role: 'system',
        content: `✅ **Build Complete!** Website generated successfully in ${data.result.build_time?.toFixed(1) || '?'}s`,
        created_at: new Date().toISOString()
      }]);

      toast.success('Website built successfully!');
      
      // Refresh credits
      fetchUserCredits();
    }

    if (data.type === 'build_error') {
      setBuildingAsync(false);
      setCurrentTaskId(null);
      
      setMessages(prev => [...prev, {
        role: 'system',
        content: `❌ **Build Failed**: ${data.error}`,
        created_at: new Date().toISOString()
      }]);

      toast.error('Build failed. Please try again.');
    }

    if (data.type === 'heartbeat') {
      // Just keep connection alive
      console.log('Heartbeat received');
    }
  }, []);

  // Initialize WebSocket
  const { connectionStatus, sendMessage } = useBuildWebSocket(
    id,
    localStorage.getItem('token'),
    handleWebSocketMessage
  );

  useEffect(() => {
    fetchProject();
    fetchMessages();
    fetchUserCredits();
  }, [id]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const fetchProject = async () => {
    try {
      const res = await axios.get(`${API}/projects/${id}`, getAxiosConfig());
      setProject(res.data);
    } catch (error) {
      console.error('Error fetching project:', error);
      toast.error('Failed to load project');
    }
  };

  const fetchMessages = async () => {
    try {
      const res = await axios.get(`${API}/projects/${id}/messages`, getAxiosConfig());
      setMessages(res.data);
    } catch (error) {
      console.error('Error fetching messages:', error);
    }
  };

  const fetchUserCredits = async () => {
    try {
      const res = await axios.get(`${API}/credits/balance`, getAxiosConfig());
      setUserCredits(res.data.credits);
    } catch (error) {
      console.error('Error fetching credits:', error);
    }
  };

  const handleSendMessage = async () => {
    if (!input.trim() || loading || buildingAsync) return;

    const messageText = input.trim();
    setInput('');
    setLoading(true);

    // Add user message
    const userMsg = {
      role: 'user',
      content: messageText,
      created_at: new Date().toISOString()
    };
    setMessages(prev => [...prev, userMsg]);

    try {
      // Save message to database
      await axios.post(`${API}/projects/${id}/messages`, {
        role: 'user',
        content: messageText
      }, getAxiosConfig());

      // Start async build with V2 API
      setMessages(prev => [...prev, {
        role: 'system',
        content: '🚀 **Starting build...** Connecting to WebSocket for real-time updates...',
        created_at: new Date().toISOString()
      }]);

      setBuildingAsync(true);

      const buildResponse = await startAsyncBuild(id, messageText, []);
      
      console.log('Async build started:', buildResponse);
      
      setCurrentTaskId(buildResponse.task_id);

      setMessages(prev => [...prev, {
        role: 'system',
        content: `✅ **Build Started** (Task: ${buildResponse.task_id.substring(0, 8)}...)\n\nWebSocket Status: ${connectionStatus}\n\nWatch for real-time updates below!`,
        created_at: new Date().toISOString()
      }]);

      toast.success('Build started! Watch for real-time updates.');

    } catch (error) {
      console.error('Error starting build:', error);
      
      if (error.response?.status === 402) {
        setMessages(prev => [...prev, {
          role: 'system',
          content: '⚠️ **Insufficient Credits**: You need more credits to build this project.',
          created_at: new Date().toISOString()
        }]);
        toast.error('Insufficient credits');
      } else {
        setMessages(prev => [...prev, {
          role: 'system',
          content: `❌ **Error**: ${error.response?.data?.detail || error.message}`,
          created_at: new Date().toISOString()
        }]);
        toast.error('Failed to start build');
      }
      
      setBuildingAsync(false);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleDeploy = async () => {
    if (!project?.generated_code) {
      toast.error('Please build your website first');
      return;
    }

    setDeploying(true);
    
    try {
      toast.info('🚀 Deploying to Vercel...');
      
      const result = await deployToVercel(id);
      
      setDeploymentUrl(result.deployment_url);
      
      toast.success(
        <div>
          <div>✅ Deployed successfully!</div>
          <a 
            href={result.deployment_url} 
            target="_blank" 
            rel="noopener noreferrer"
            style={{ color: '#7c3aed', textDecoration: 'underline' }}
          >
            View live site →
          </a>
        </div>,
        { duration: 8000 }
      );

      setMessages(prev => [...prev, {
        role: 'system',
        content: `🚀 **Deployed to Vercel**: Your website is live at [${result.deployment_url}](${result.deployment_url})`,
        created_at: new Date().toISOString()
      }]);

    } catch (error) {
      console.error('Deployment error:', error);
      toast.error(error.response?.data?.detail || 'Deployment failed');
      
      setMessages(prev => [...prev, {
        role: 'system',
        content: `❌ **Deployment Failed**: ${error.response?.data?.detail || error.message}`,
        created_at: new Date().toISOString()
      }]);
    } finally {
      setDeploying(false);
    }
  };

  return (
    <div style={{ height: '100vh', display: 'flex', flexDirection: 'column', background: '#0a0a0a' }}>
      {/* Header */}
      <header style={{
        background: '#111',
        borderBottom: '1px solid #222',
        padding: '16px 24px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <button
            onClick={() => navigate('/dashboard')}
            style={{
              background: 'transparent',
              border: '1px solid #333',
              color: '#fff',
              padding: '8px 16px',
              borderRadius: '6px',
              cursor: 'pointer'
            }}
          >
            ← Back
          </button>
          <h1 style={{ color: '#fff', fontSize: '1.25rem', fontWeight: '600' }}>
            {project?.name || 'Project'}
          </h1>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{
            background: '#1a1a1a',
            padding: '8px 16px',
            borderRadius: '6px',
            border: '1px solid #333'
          }}>
            <span style={{ color: '#888', marginRight: '8px' }}>WebSocket:</span>
            <span style={{
              color: connectionStatus === 'connected' ? '#10b981' : 
                     connectionStatus === 'connecting' ? '#f59e0b' : '#ef4444',
              fontWeight: '600'
            }}>
              {connectionStatus}
            </span>
          </div>

          <div style={{
            background: '#1a1a1a',
            padding: '8px 16px',
            borderRadius: '6px',
            border: '1px solid #333'
          }}>
            <span style={{ color: '#888', marginRight: '8px' }}>Credits:</span>
            <span style={{ color: '#fff', fontWeight: '600' }}>{userCredits}</span>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div style={{ flex: 1, display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 0 }}>
        {/* Chat */}
        <div style={{ 
          background: '#0a0a0a',
          borderRight: '1px solid #222',
          display: 'flex',
          flexDirection: 'column'
        }}>
          {/* Messages */}
          <div style={{
            flex: 1,
            overflowY: 'auto',
            padding: '24px',
            display: 'flex',
            flexDirection: 'column',
            gap: '16px'
          }}>
            {messages.length === 0 && (
              <div style={{ textAlign: 'center', padding: '40px', color: '#666' }}>
                <Sparkles size={48} style={{ margin: '0 auto 16px', opacity: 0.5 }} />
                <p>Start by describing your website idea...</p>
              </div>
            )}

            {messages.map((msg, idx) => (
              <div
                key={idx}
                style={{
                  padding: '16px',
                  borderRadius: '8px',
                  background: msg.role === 'user' ? '#1a1a1a' : '#0f0f0f',
                  border: `1px solid ${msg.role === 'user' ? '#333' : '#222'}`,
                  color: '#fff'
                }}
              >
                {msg.content}
              </div>
            ))}

            {(loading || buildingAsync) && (
              <div style={{
                padding: '16px',
                borderRadius: '8px',
                background: '#0f0f0f',
                border: '1px solid #222',
                color: '#888',
                display: 'flex',
                alignItems: 'center',
                gap: '12px'
              }}>
                <Loader2 size={16} style={{ animation: 'spin 1s linear infinite' }} />
                <span>{buildingAsync ? 'Building (async)...' : 'Processing...'}</span>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div style={{
            padding: '16px 24px',
            borderTop: '1px solid #222',
            background: '#111'
          }}>
            <div style={{ display: 'flex', gap: '12px' }}>
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Describe your website..."
                disabled={loading || buildingAsync}
                style={{
                  flex: 1,
                  background: '#1a1a1a',
                  border: '1px solid #333',
                  borderRadius: '8px',
                  padding: '12px',
                  color: '#fff',
                  resize: 'none',
                  minHeight: '60px',
                  fontFamily: 'inherit'
                }}
              />
              <button
                onClick={handleSendMessage}
                disabled={!input.trim() || loading || buildingAsync}
                style={{
                  background: input.trim() && !loading && !buildingAsync ? '#7c3aed' : '#333',
                  border: 'none',
                  borderRadius: '8px',
                  padding: '12px 24px',
                  color: '#fff',
                  cursor: input.trim() && !loading && !buildingAsync ? 'pointer' : 'not-allowed',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px'
                }}
              >
                <Send size={18} />
              </button>
            </div>
          </div>
        </div>

        {/* Preview */}
        <div style={{
          background: '#fff',
          display: 'flex',
          flexDirection: 'column'
        }}>
          <div style={{
            padding: '16px 24px',
            borderBottom: '1px solid #e5e7eb',
            background: '#f9fafb',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center'
          }}>
            <h3 style={{ fontSize: '0.875rem', fontWeight: '600', color: '#374151' }}>
              Live Preview
            </h3>
            
            <div style={{ display: 'flex', gap: '8px' }}>
              {deploymentUrl && (
                <a
                  href={deploymentUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{
                    background: '#10b981',
                    color: '#fff',
                    padding: '6px 12px',
                    borderRadius: '6px',
                    fontSize: '0.875rem',
                    textDecoration: 'none',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px',
                    border: 'none'
                  }}
                >
                  <ExternalLink size={14} />
                  View Live
                </a>
              )}
              
              <button
                onClick={handleDeploy}
                disabled={deploying || !project?.generated_code}
                style={{
                  background: deploying ? '#9ca3af' : project?.generated_code ? '#7c3aed' : '#e5e7eb',
                  color: project?.generated_code ? '#fff' : '#9ca3af',
                  padding: '6px 12px',
                  borderRadius: '6px',
                  fontSize: '0.875rem',
                  cursor: project?.generated_code && !deploying ? 'pointer' : 'not-allowed',
                  border: 'none',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px'
                }}
              >
                {deploying ? (
                  <>
                    <Loader2 size={14} style={{ animation: 'spin 1s linear infinite' }} />
                    Deploying...
                  </>
                ) : (
                  <>
                    <Rocket size={14} />
                    Deploy to Vercel
                  </>
                )}
              </button>
            </div>
          </div>

          <div style={{ flex: 1, overflow: 'auto' }}>
            {project?.generated_code ? (
              <iframe
                srcDoc={project.generated_code}
                style={{
                  width: '100%',
                  height: '100%',
                  border: 'none'
                }}
                title="preview"
              />
            ) : (
              <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                height: '100%',
                color: '#9ca3af'
              }}>
                <p>No preview available yet</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default WorkspaceV2;
