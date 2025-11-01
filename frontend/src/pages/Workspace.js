// Enhanced Workspace with V2 API and WebSocket Support
// Real-time build updates with async Celery tasks

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'sonner';
import { Send, Loader2, Sparkles, Rocket, ExternalLink, CheckCircle, XCircle, AlertCircle, Paperclip, X } from 'lucide-react';
import { useDropzone } from 'react-dropzone';
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
  const [validating, setValidating] = useState(false);
  const [validationResults, setValidationResults] = useState(null);
  const [showValidationModal, setShowValidationModal] = useState(false);
  const [uploadedImages, setUploadedImages] = useState([]);
  const [uploadingFile, setUploadingFile] = useState(false);
  const messagesEndRef = useRef(null);

  const getAxiosConfig = () => ({
    headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
    withCredentials: true
  });

  // Dropzone for file uploads
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg']
    },
    maxSize: 10485760, // 10MB
    onDrop: async (acceptedFiles) => {
      if (acceptedFiles.length === 0) return;
      
      setUploadingFile(true);
      const file = acceptedFiles[0];
      
      try {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('project_id', id);
        
        const config = getAxiosConfig();
        const res = await axios.post(`${API}/upload`, formData, {
          ...config,
          headers: {
            ...config.headers,
            'Content-Type': 'multipart/form-data'
          }
        });
        
        // Add to uploaded images array
        setUploadedImages(prev => [...prev, {
          url: res.data.url,
          filename: file.name,
          format: res.data.format || 'image'
        }]);
        toast.success(`Image uploaded: ${file.name}`);
      } catch (error) {
        console.error('Upload error:', error);
        toast.error('Upload failed. Please try again.');
      } finally {
        setUploadingFile(false);
      }
    }
  });

  const removeUploadedImage = (index) => {
    setUploadedImages(prev => prev.filter((_, i) => i !== index));
  };

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
    const imagesToSend = uploadedImages.map(img => img.url);
    setInput('');
    setUploadedImages([]); // Clear uploaded images after sending
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

      const buildResponse = await startAsyncBuild(id, messageText, imagesToSend);
      
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
      
      // Use V1 endpoint that works with MongoDB
      const response = await axios.post(
        `${API}/deploy/vercel`,
        {
          project_id: id,
          project_name: project.name || 'autowebiq-project'
        },
        getAxiosConfig()
      );
      
      const result = response.data;
      setDeploymentUrl(result.deployment_url || result.url);
      
      toast.success(
        <div>
          <div>✅ Deployed successfully!</div>
          <a 
            href={result.deployment_url || result.url} 
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
        content: `🚀 **Deployed to Vercel**: Your website is live!`,
        created_at: new Date().toISOString()
      }]);

    } catch (error) {
      console.error('Deployment error:', error);
      toast.error(error.response?.data?.detail || 'Deployment failed. This feature requires Vercel integration.');
      
      setMessages(prev => [...prev, {
        role: 'system',
        content: `❌ **Deployment Failed**: ${error.response?.data?.detail || error.message}. Note: Deployment requires Vercel token configuration.`,
        created_at: new Date().toISOString()
      }]);
    } finally {
      setDeploying(false);
    }
  };

  const handleValidate = async () => {
    if (!project?.generated_code) {
      toast.error('Please build your website first');
      return;
    }

    setValidating(true);
    
    try {
      toast.info('🔍 Running 9-point validation...');
      
      // Use V1 endpoint that works with MongoDB
      const response = await axios.post(
        `${API}/validate`,
        {
          project_id: id,
          html_content: project.generated_code
        },
        getAxiosConfig()
      );
      
      const result = response.data;
      setValidationResults(result);
      setShowValidationModal(true);
      
      const statusEmoji = result.all_passed ? '✅' : result.overall_score >= 75 ? '⚠️' : '❌';
      const statusText = result.overall_score >= 90 ? 'EXCELLENT' : 
                        result.overall_score >= 75 ? 'GOOD' : 
                        result.overall_score >= 60 ? 'NEEDS IMPROVEMENT' : 'POOR';
      
      toast.success(
        <div>
          <div>{statusEmoji} Validation Complete!</div>
          <div>Score: {result.overall_score}/100 ({statusText})</div>
          <div>{result.passed_checks}/{result.total_checks} checks passed</div>
        </div>,
        { duration: 5000 }
      );

      setMessages(prev => [...prev, {
        role: 'system',
        content: `${statusEmoji} **Validation Complete**: ${result.passed_checks}/${result.total_checks} checks passed. Overall Score: ${result.overall_score}/100 (${statusText})`,
        created_at: new Date().toISOString()
      }]);

    } catch (error) {
      console.error('Validation error:', error);
      toast.error(error.response?.data?.detail || 'Validation failed');
      
      setMessages(prev => [...prev, {
        role: 'system',
        content: `❌ **Validation Failed**: ${error.response?.data?.detail || error.message}. Running validation on generated code...`,
        created_at: new Date().toISOString()
      }]);
    } finally {
      setValidating(false);
    }
  };

  const openInNewTab = () => {
    if (!project?.generated_code) {
      toast.error('No website to open. Build your website first!');
      return;
    }

    // Create a blob from the HTML
    const blob = new Blob([project.generated_code], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    
    // Open in new tab
    window.open(url, '_blank');
    
    toast.success('✅ Opened in new tab!');
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
            {/* Uploaded Images Preview */}
            {uploadedImages.length > 0 && (
              <div style={{
                display: 'flex',
                gap: '8px',
                marginBottom: '12px',
                flexWrap: 'wrap'
              }}>
                {uploadedImages.map((img, idx) => (
                  <div
                    key={idx}
                    style={{
                      position: 'relative',
                      width: '80px',
                      height: '80px',
                      borderRadius: '8px',
                      overflow: 'hidden',
                      border: '2px solid #333'
                    }}
                  >
                    <img
                      src={img.url}
                      alt={img.filename}
                      style={{
                        width: '100%',
                        height: '100%',
                        objectFit: 'cover'
                      }}
                    />
                    <button
                      onClick={() => removeUploadedImage(idx)}
                      style={{
                        position: 'absolute',
                        top: '4px',
                        right: '4px',
                        background: 'rgba(0, 0, 0, 0.7)',
                        border: 'none',
                        borderRadius: '50%',
                        width: '24px',
                        height: '24px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        cursor: 'pointer',
                        color: '#fff'
                      }}
                    >
                      <X size={14} />
                    </button>
                  </div>
                ))}
              </div>
            )}
            
            <div style={{ display: 'flex', gap: '12px', alignItems: 'flex-end' }}>
              {/* Clip Icon Button */}
              <div {...getRootProps()} style={{ cursor: 'pointer' }}>
                <input {...getInputProps()} />
                <button
                  type="button"
                  disabled={uploadingFile || loading || buildingAsync}
                  style={{
                    background: '#1a1a1a',
                    border: '1px solid #333',
                    borderRadius: '8px',
                    padding: '12px',
                    color: uploadingFile ? '#666' : '#999',
                    cursor: uploadingFile || loading || buildingAsync ? 'not-allowed' : 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    height: '60px'
                  }}
                >
                  {uploadingFile ? (
                    <Loader2 size={20} style={{ animation: 'spin 1s linear infinite' }} />
                  ) : (
                    <Paperclip size={20} />
                  )}
                </button>
              </div>
              
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
                  gap: '8px',
                  height: '60px'
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
                onClick={handleValidate}
                disabled={validating || !project?.generated_code}
                style={{
                  background: validating ? '#9ca3af' : project?.generated_code ? '#3b82f6' : '#e5e7eb',
                  color: project?.generated_code ? '#fff' : '#9ca3af',
                  padding: '6px 12px',
                  borderRadius: '6px',
                  fontSize: '0.875rem',
                  cursor: project?.generated_code && !validating ? 'pointer' : 'not-allowed',
                  border: 'none',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px'
                }}
              >
                {validating ? (
                  <>
                    <Loader2 size={14} style={{ animation: 'spin 1s linear infinite' }} />
                    Validating...
                  </>
                ) : (
                  <>
                    <CheckCircle size={14} />
                    Validate
                  </>
                )}
              </button>
              
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

      {/* Validation Results Modal */}
      {showValidationModal && validationResults && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0, 0, 0, 0.8)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000,
          padding: '20px'
        }}>
          <div style={{
            background: '#fff',
            borderRadius: '12px',
            maxWidth: '900px',
            width: '100%',
            maxHeight: '90vh',
            overflow: 'auto',
            boxShadow: '0 20px 60px rgba(0, 0, 0, 0.3)'
          }}>
            {/* Modal Header */}
            <div style={{
              padding: '24px',
              borderBottom: '1px solid #e5e7eb',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center'
            }}>
              <div>
                <h2 style={{ fontSize: '1.5rem', fontWeight: '700', color: '#111', marginBottom: '8px' }}>
                  Validation Results
                </h2>
                <p style={{ color: '#6b7280', fontSize: '0.875rem' }}>
                  {validationResults.passed_checks}/{validationResults.total_checks} checks passed • Score: {validationResults.overall_score}/100
                </p>
              </div>
              <button
                onClick={() => setShowValidationModal(false)}
                style={{
                  background: 'transparent',
                  border: 'none',
                  fontSize: '1.5rem',
                  color: '#6b7280',
                  cursor: 'pointer',
                  padding: '4px 8px'
                }}
              >
                ×
              </button>
            </div>

            {/* Overall Score */}
            <div style={{ padding: '24px', background: '#f9fafb' }}>
              <div style={{
                background: '#fff',
                padding: '20px',
                borderRadius: '8px',
                border: '2px solid ' + (validationResults.overall_score >= 90 ? '#10b981' : 
                                        validationResults.overall_score >= 75 ? '#3b82f6' : 
                                        validationResults.overall_score >= 60 ? '#f59e0b' : '#ef4444')
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                  <div style={{
                    fontSize: '3rem',
                    fontWeight: '700',
                    color: validationResults.overall_score >= 90 ? '#10b981' : 
                           validationResults.overall_score >= 75 ? '#3b82f6' : 
                           validationResults.overall_score >= 60 ? '#f59e0b' : '#ef4444'
                  }}>
                    {validationResults.overall_score}
                  </div>
                  <div>
                    <div style={{ fontSize: '1.25rem', fontWeight: '600', color: '#111' }}>
                      {validationResults.overall_score >= 90 ? 'EXCELLENT' : 
                       validationResults.overall_score >= 75 ? 'GOOD' : 
                       validationResults.overall_score >= 60 ? 'NEEDS IMPROVEMENT' : 'POOR'}
                    </div>
                    <div style={{ fontSize: '0.875rem', color: '#6b7280' }}>
                      {validationResults.all_passed ? 'All checks passed! 🎉' : 'Some improvements needed'}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Individual Checks */}
            <div style={{ padding: '24px' }}>
              <h3 style={{ fontSize: '1.125rem', fontWeight: '600', color: '#111', marginBottom: '16px' }}>
                Detailed Results
              </h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {Object.entries(validationResults.results).map(([key, result]) => (
                  <div
                    key={key}
                    style={{
                      border: '1px solid #e5e7eb',
                      borderRadius: '8px',
                      padding: '16px',
                      background: result.passed ? '#f0fdf4' : '#fef2f2'
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                        {result.passed ? (
                          <CheckCircle size={20} style={{ color: '#10b981' }} />
                        ) : (
                          <XCircle size={20} style={{ color: '#ef4444' }} />
                        )}
                        <span style={{ fontWeight: '600', color: '#111' }}>
                          {result.check_name}
                        </span>
                      </div>
                      <span style={{
                        fontWeight: '700',
                        color: result.score >= 90 ? '#10b981' : 
                               result.score >= 75 ? '#3b82f6' : 
                               result.score >= 60 ? '#f59e0b' : '#ef4444'
                      }}>
                        {result.score}/100
                      </span>
                    </div>

                    {result.issues && result.issues.length > 0 && (
                      <div style={{ marginTop: '12px' }}>
                        <div style={{ fontSize: '0.875rem', fontWeight: '600', color: '#6b7280', marginBottom: '8px' }}>
                          Issues Found:
                        </div>
                        <ul style={{ margin: 0, paddingLeft: '20px', fontSize: '0.875rem', color: '#374151' }}>
                          {result.issues.slice(0, 3).map((issue, idx) => (
                            <li key={idx} style={{ marginBottom: '4px' }}>
                              {issue.message}
                            </li>
                          ))}
                          {result.issues.length > 3 && (
                            <li style={{ color: '#6b7280', fontStyle: 'italic' }}>
                              +{result.issues.length - 3} more issues
                            </li>
                          )}
                        </ul>
                      </div>
                    )}

                    {result.recommendations && result.recommendations.length > 0 && (
                      <div style={{ marginTop: '12px', padding: '12px', background: '#fff', borderRadius: '6px', border: '1px solid #e5e7eb' }}>
                        <div style={{ fontSize: '0.875rem', fontWeight: '600', color: '#6b7280', marginBottom: '6px' }}>
                          💡 Recommendations:
                        </div>
                        <ul style={{ margin: 0, paddingLeft: '20px', fontSize: '0.875rem', color: '#374151' }}>
                          {result.recommendations.slice(0, 2).map((rec, idx) => (
                            <li key={idx} style={{ marginBottom: '4px' }}>
                              {rec}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Modal Footer */}
            <div style={{
              padding: '24px',
              borderTop: '1px solid #e5e7eb',
              display: 'flex',
              justifyContent: 'flex-end',
              gap: '12px'
            }}>
              <button
                onClick={() => setShowValidationModal(false)}
                style={{
                  background: '#e5e7eb',
                  color: '#374151',
                  padding: '10px 20px',
                  borderRadius: '6px',
                  border: 'none',
                  cursor: 'pointer',
                  fontWeight: '500'
                }}
              >
                Close
              </button>
              <button
                onClick={() => {
                  setShowValidationModal(false);
                  handleValidate();
                }}
                style={{
                  background: '#7c3aed',
                  color: '#fff',
                  padding: '10px 20px',
                  borderRadius: '6px',
                  border: 'none',
                  cursor: 'pointer',
                  fontWeight: '500'
                }}
              >
                Re-validate
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default WorkspaceV2;
