import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import AgentStatusPanel from '../components/AgentStatusPanel';
import './Workspace.css';

const Workspace = () => {
  const { id: projectId } = useParams();
  const navigate = useNavigate();
  const wsRef = useRef(null);
  
  const [project, setProject] = useState(null);
  const [user, setUser] = useState(null);
  const [message, setMessage] = useState('');
  const [credits, setCredits] = useState(0);
  const [agentStatus, setAgentStatus] = useState([]);
  const [generating, setGenerating] = useState(false);
  const [generatedCode, setGeneratedCode] = useState('');
  const [showPreview, setShowPreview] = useState(true);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchUser();
    fetchProject();
    connectWebSocket();
    
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [projectId]);

  const fetchUser = async () => {
    try {
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/auth/me`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        }
      );
      
      if (response.ok) {
        const data = await response.json();
        setUser(data);
        setCredits(data.credits || 0);
      }
    } catch (error) {
      console.error('Error fetching user:', error);
    }
  };

  const fetchProject = async () => {
    try {
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/projects/${projectId}`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        }
      );
      
      if (response.ok) {
        const data = await response.json();
        setProject(data);
        if (data.generated_code) {
          setGeneratedCode(data.generated_code);
        }
      } else {
        console.error('Failed to fetch project');
      }
    } catch (error) {
      console.error('Error fetching project:', error);
    } finally {
      setLoading(false);
    }
  };

  const connectWebSocket = () => {
    const wsUrl = process.env.REACT_APP_BACKEND_URL.replace('http', 'ws');
    const ws = new WebSocket(`${wsUrl}/ws/${projectId}`);
    
    ws.onopen = () => {
      console.log('WebSocket connected');
    };
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.type === 'status') {
        setAgentStatus(prev => [...prev, {
          status: data.status,
          credits: data.credits_used,
          timestamp: new Date(data.timestamp).toLocaleTimeString()
        }]);
      } else if (data.type === 'complete') {
        setGeneratedCode(data.code);
        setGenerating(false);
        setCredits(data.new_balance);
        fetchProject();
      } else if (data.error) {
        setGenerating(false);
        alert(data.error);
      }
    };
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
    
    ws.onclose = () => {
      console.log('WebSocket closed');
    };
    
    wsRef.current = ws;
  };

  const handleGenerate = () => {
    if (!message.trim() || generating) return;
    
    setGenerating(true);
    setAgentStatus([]);
    
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        token: localStorage.getItem('token'),
        message: message
      }));
      setMessage('');
    }
  };

  const downloadCode = () => {
    const blob = new Blob([generatedCode], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${project.name}.html`;
    a.click();
  };

  return (
    <div className="workspace">
      {/* Header */}
      <header className="workspace-header">
        <div className="header-left">
          <button className="back-btn" onClick={() => navigate('/dashboard')}>
            ← Back
          </button>
          <div className="project-info">
            <h1>{project?.name}</h1>
            <span className="project-desc">{project?.description}</span>
          </div>
        </div>
        <div className="header-right">
          <div className="credits-display">
            💎 {credits} credits
          </div>
          {generatedCode && (
            <>
              <button className="btn-icon" onClick={downloadCode} title="Download">
                📥
              </button>
              <button className="btn-icon" onClick={() => navigate(`/deployment/${projectId}`)} title="Deploy">
                🚀
              </button>
              <button 
                className="btn-icon" 
                onClick={() => setShowPreview(!showPreview)}
                title={showPreview ? 'Hide Preview' : 'Show Preview'}
              >
                {showPreview ? '👁️' : '👁️‍🗨️'}
              </button>
            </>
          )}
        </div>
      </header>

      {/* Main Content */}
      <div className="workspace-content">
        {/* Left Panel - Chat & Agent Status */}
        <div className="left-panel">
          {/* Agent Status Panel - Emergent Style */}
          <div className="agent-panel-container">
            <AgentStatusPanel 
              agents={agentStatus}
              isGenerating={generating}
            />
          </div>
          
          <div className="chat-section">\n            <h3>AI Workspace</h3>
            
            {/* Input Area */}
            <div className="chat-input-area">
              <textarea
                className="chat-input"
                placeholder="Describe your website... (e.g., Create a modern portfolio with dark theme)"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                disabled={generating}
                rows="4"
              />
              <button
                className="generate-btn"
                onClick={handleGenerate}
                disabled={generating || !message.trim()}
              >
                {generating ? (
                  <>
                    <span className="spinner-small"></span>
                    Generating...
                  </>
                ) : (
                  <>
                    ✨ Generate Website
                  </>
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Right Panel - Preview */}
        {showPreview && generatedCode && (
          <div className="right-panel">
            <div className="preview-header">
              <h3>Live Preview</h3>
            </div>
            <iframe
              className="preview-iframe"
              srcDoc={generatedCode}
              title="Website Preview"
            />
          </div>
        )}
      </div>
    </div>
  );
};

export default Workspace;
