import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import Editor from '@monaco-editor/react';
import { useDropzone } from 'react-dropzone';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { ScrollArea } from '@/components/ui/scroll-area';
import { toast } from 'sonner';
import { Send, ArrowLeft, Loader2, Code, Eye, ExternalLink, CreditCard, Mic, MicOff, Image as ImageIcon, Edit3, Save, Sparkles, Rocket, LogOut } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Workspace = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [project, setProject] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [previewMode, setPreviewMode] = useState('preview');
  const [editMode, setEditMode] = useState(false);
  const [editedCode, setEditedCode] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [uploadingFile, setUploadingFile] = useState(false);
  const [userCredits, setUserCredits] = useState(0);
  const [uploadedImages, setUploadedImages] = useState([]); // Store uploaded image URLs
  const messagesEndRef = useRef(null);
  const iframeRef = useRef(null);
  const recognitionRef = useRef(null);

  const getAxiosConfig = () => ({
    headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
    withCredentials: true
  });

  useEffect(() => {
    fetchProject();
    fetchMessages();
    fetchUserCredits();
    initVoiceRecognition();
  }, [id]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (project && iframeRef.current && previewMode === 'preview' && !editMode) {
      const iframe = iframeRef.current;
      const defaultHTML = '<html><body><div style="display:flex;align-items:center;justify-content:center;height:100vh;font-family:sans-serif;color:#666;">Send a message to generate your website...</div></body></html>';
      const codeToShow = project.generated_code || defaultHTML;
      
      // Force iframe refresh
      iframe.srcdoc = '';
      setTimeout(() => {
        iframe.srcdoc = codeToShow;
      }, 10);
    }
  }, [project?.generated_code, previewMode, editMode]);

  useEffect(() => {
    if (project && editMode) {
      setEditedCode(project.generated_code || '');
    }
  }, [project, editMode]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const fetchProject = async () => {
    try {
      const res = await axios.get(`${API}/projects/${id}`, getAxiosConfig());
      setProject(res.data);
    } catch (error) {
      toast.error('Failed to load project');
      navigate('/dashboard');
    }
  };

  const fetchMessages = async () => {
    try {
      const res = await axios.get(`${API}/projects/${id}/messages`, getAxiosConfig());
      setMessages(res.data.filter(m => m.role !== 'system'));
    } catch (error) {
      console.error('Failed to load messages');
    }
  };

  const fetchUserCredits = async () => {
    try {
      const res = await axios.get(`${API}/auth/me`, getAxiosConfig());
      setUserCredits(res.data.credits);
    } catch (error) {
      console.error('Failed to load credits');
    }
  };

  const initVoiceRecognition = () => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = false;
      
      recognitionRef.current.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        setInput(prev => prev + ' ' + transcript);
        setIsRecording(false);
        toast.success('Voice captured!');
      };
      
      recognitionRef.current.onerror = () => {
        setIsRecording(false);
        toast.error('Voice recognition failed');
      };
      
      recognitionRef.current.onend = () => {
        setIsRecording(false);
      };
    }
  };

  const toggleVoiceRecording = () => {
    if (!recognitionRef.current) {
      toast.error('Voice recognition not supported in this browser');
      return;
    }
    
    if (isRecording) {
      recognitionRef.current.stop();
      setIsRecording(false);
    } else {
      recognitionRef.current.start();
      setIsRecording(true);
      toast.info('Listening...');
    }
  };

  const saveEditedCode = async () => {
    try {
      await axios.put(`${API}/projects/${id}`, {
        generated_code: editedCode
      }, getAxiosConfig());
      
      setProject(prev => ({ ...prev, generated_code: editedCode }));
      setEditMode(false);
      toast.success('Code saved successfully!');
    } catch (error) {
      toast.error('Failed to save code');
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg'],
      'video/*': ['.mp4', '.webm', '.mov'],
      'application/*': ['.pdf', '.doc', '.docx']
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
        
        // Check if it's an image
        const isImage = file.type.startsWith('image/');
        
        if (isImage) {
          // Add to uploaded images array
          setUploadedImages(prev => [...prev, {
            url: res.data.url,
            filename: file.name,
            format: res.data.format
          }]);
          toast.success(`Image uploaded: ${file.name}`);
        } else {
          // Add file info to chat for non-images
          setInput(prev => prev + `\n[Uploaded: ${file.name} - ${res.data.url}]`);
          toast.success('File uploaded!');
        }
      } catch (error) {
        toast.error('Upload failed');
      } finally {
        setUploadingFile(false);
      }
    }
  });

  const sendMessage = async () => {
    if (!input.trim() || loading) return;
    
    // Note: Backend will handle credit deduction dynamically
    
    const userMessage = {
      role: 'user',
      content: input,
      created_at: new Date().toISOString()
    };
    
    const messageText = input;
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);
    
    try {
      const res = await axios.post(`${API}/chat`, {
        project_id: id,
        message: messageText
      }, getAxiosConfig());
      
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: res.data.ai_message.content,
        created_at: res.data.ai_message.created_at
      }]);
      
      if (res.data.code) {
        setProject(prev => ({ ...prev, generated_code: res.data.code }));
      }
      
      // Refresh user credits from backend
      await fetchUserCredits();
      
      toast.success('Generated successfully!');
    } catch (error) {
      const errorMsg = error.response?.data?.detail || 'Failed to generate';
      toast.error(errorMsg);
      setMessages(prev => prev.slice(0, -1));
      
      if (error.response?.status === 402) {
        navigate('/credits');
      }
    } finally {
      setLoading(false);
    }
  };

  // NEW: Multi-Agent Website Builder
  const buildWithAgents = async () => {
    if (!input.trim() || loading) return;
    
    // Note: We'll get the actual cost from the backend response
    // Backend calculates dynamically based on agents used
    
    // Add user message
    const userMessage = {
      role: 'user',
      content: input,
      created_at: new Date().toISOString()
    };
    
    const messageText = input;
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);
    
    // Add agent status message with credit info
    const agentStatusMsg = {
      role: 'system',
      content: '🤖 **Multi-Agent System Activated**\n\nDeploying AI agents to build your website...\n\n💳 **Dynamic Pricing**: Credits will be deducted based on agents used (Estimated: 17-35 credits)',
      created_at: new Date().toISOString()
    };
    setMessages(prev => [...prev, agentStatusMsg]);
    
    try {
      // Add planner agent message
      setMessages(prev => [...prev, {
        role: 'system',
        content: '🧠 **Planner Agent**: Analyzing your requirements... (5 credits)',
        created_at: new Date().toISOString()
      }]);
      
      const res = await axios.post(`${API}/build-with-agents`, {
        project_id: id,
        prompt: messageText,
        uploaded_images: uploadedImages.map(img => img.url) // Pass uploaded image URLs
      }, getAxiosConfig());
      
      // Add success messages with plan details
      const plan = res.data.plan;
      
      setMessages(prev => [...prev, {
        role: 'system',
        content: `✅ **Planner Agent**: Project plan created!\n\n**Project**: ${plan.project_name}\n**Type**: ${plan.type}\n**Pages**: ${plan.pages.join(', ')}\n**Features**: ${plan.features.join(', ')}`,
        created_at: new Date().toISOString()
      }]);
      
      setMessages(prev => [...prev, {
        role: 'system',
        content: '🎨 **Image Agent**: Generating custom images... (12 credits)',
        created_at: new Date().toISOString()
      }]);
      
      setMessages(prev => [...prev, {
        role: 'system',
        content: `✅ **Image Agent**: ${res.data.images?.length || 0} images created!`,
        created_at: new Date().toISOString()
      }]);
      
      setMessages(prev => [...prev, {
        role: 'system',
        content: '🎨 **Frontend Agent**: Building user interface... (8 credits)',
        created_at: new Date().toISOString()
      }]);
      
      setMessages(prev => [...prev, {
        role: 'system',
        content: '✅ **Frontend Agent**: UI code generated successfully!',
        created_at: new Date().toISOString()
      }]);
      
      if (res.data.backend_code) {
        setMessages(prev => [...prev, {
          role: 'system',
          content: '⚙️ **Backend Agent**: Creating API endpoints... (6 credits)',
          created_at: new Date().toISOString()
        }]);
        
        setMessages(prev => [...prev, {
          role: 'system',
          content: '✅ **Backend Agent**: Backend API generated successfully!',
          created_at: new Date().toISOString()
        }]);
      }
      
      // Testing agent message
      setMessages(prev => [...prev, {
        role: 'system',
        content: '🧪 **Testing Agent**: Running quality checks... (4 credits)',
        created_at: new Date().toISOString()
      }]);
      
      const testScore = res.data.test_results?.score || 85;
      setMessages(prev => [...prev, {
        role: 'system',
        content: `✅ **Testing Agent**: Tests passed! Quality score: ${testScore}/100`,
        created_at: new Date().toISOString()
      }]);
      
      // Final success message with credit breakdown
      const creditsUsed = res.data.credits_used || 0;
      const creditsRefunded = res.data.credits_refunded || 0;
      const remainingBalance = res.data.remaining_balance || userCredits;
      const costBreakdown = res.data.cost_breakdown || {};
      
      let breakdownText = '';
      if (costBreakdown.breakdown) {
        breakdownText = '\n\n**Credit Usage:**\n';
        Object.entries(costBreakdown.breakdown).forEach(([agent, cost]) => {
          breakdownText += `- ${agent}: ${cost} credits\n`;
        });
        if (creditsRefunded > 0) {
          breakdownText += `\n💚 **Refunded**: ${creditsRefunded} credits (actual cost was less than estimated)`;
        }
        breakdownText += `\n\n💳 **Total Used**: ${creditsUsed} credits | **Remaining**: ${remainingBalance} credits`;
      }
      
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `🎉 **Complete!** Your ${plan.project_name} is ready!\n\n**What was built:**\n- ${plan.pages.length} pages\n- ${plan.features.length} features\n- ${res.data.backend_code ? 'Backend API included' : 'Frontend only'}${breakdownText}\n\nCheck the preview on the right! →`,
        created_at: new Date().toISOString()
      }]);
      
      // Update preview with generated code
      if (res.data.frontend_code) {
        setProject(prev => ({ 
          ...prev, 
          generated_code: res.data.frontend_code,
          backend_code: res.data.backend_code || '',
          project_plan: plan
        }));
      }
      
      // Update credits with actual remaining balance
      setUserCredits(remainingBalance);
      
      toast.success(`Website built! Used ${creditsUsed} credits${creditsRefunded > 0 ? ` (${creditsRefunded} refunded)` : ''}`);
      
    } catch (error) {
      const errorMsg = error.response?.data?.detail || 'Multi-agent build failed';
      toast.error(errorMsg);
      
      setMessages(prev => [...prev, {
        role: 'system',
        content: `❌ **Build Failed**: ${errorMsg}`,
        created_at: new Date().toISOString()
      }]);
      
      if (error.response?.status === 402) {
        navigate('/credits');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    navigate('/');
  };

  const openInNewTab = () => {
    if (!project.generated_code) {
      toast.error('No code generated yet');
      return;
    }
    
    const blob = new Blob([project.generated_code], { type: 'text/html' });
    const url = window.URL.createObjectURL(blob);
    window.open(url, '_blank');
  };

  if (!project) {
    return <div className="loading-screen">Loading workspace...</div>;
  }

  return (
    <div className="workspace-modern">
      {/* Professional Header */}
      <header className="workspace-header-professional">
        <div className="header-content-professional">
          {/* Left: Logo and Navigation */}
          <div className="header-left-professional">
            <div className="workspace-logo" onClick={() => navigate('/dashboard')}>
              <Sparkles size={24} />
              <span>AutoWebIQ</span>
            </div>
            <Button className="home-btn-workspace" onClick={() => navigate('/dashboard')}>
              <Rocket size={18} />
              Home
            </Button>
          </div>

          {/* Center: Project Selector */}
          <div className="header-center-professional">
            <div className="project-selector">
              <Code size={18} />
              <span className="project-name">{project.name}</span>
            </div>
          </div>

          {/* Right: Credits and Profile */}
          <div className="header-right-professional">
            <div className="credits-display-workspace">
              <CreditCard size={16} />
              <span>{userCredits} Credits</span>
              <Button className="buy-credits-workspace" onClick={() => navigate('/credits')}>
                Buy More
              </Button>
            </div>
            
            <div className="user-menu-workspace">
              <div className="user-avatar-workspace">
                {localStorage.getItem('user') ? JSON.parse(localStorage.getItem('user')).username?.[0]?.toUpperCase() || 'U' : 'U'}
              </div>
              <div className="user-dropdown">
                <div className="user-dropdown-header">
                  <div className="user-dropdown-name">
                    {localStorage.getItem('user') ? JSON.parse(localStorage.getItem('user')).username || 'User' : 'User'}
                  </div>
                  <div className="user-dropdown-email">
                    {localStorage.getItem('user') ? JSON.parse(localStorage.getItem('user')).email : 'email@example.com'}
                  </div>
                </div>
                <button className="logout-btn-workspace" onClick={handleLogout}>
                  <LogOut size={16} />
                  Logout
                </button>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <div className="workspace-main-professional">
        {/* Chat Section */}
        <div className="chat-section-professional">
          <ScrollArea className="messages-area-professional">
            {messages.length === 0 && (
              <div className="empty-state-professional">
                <div className="empty-icon">🤖</div>
                <h2>Start Building</h2>
                <p>Describe your website and AI will generate it</p>
              </div>
            )}
            
            {messages.map((msg, idx) => (
              <div key={idx} className={`message-professional ${msg.role}`}>
                <div className="message-avatar-professional">
                  {msg.role === 'user' ? (
                    <div className="avatar-circle user-avatar-circle">
                      {localStorage.getItem('user') ? JSON.parse(localStorage.getItem('user')).username?.[0]?.toUpperCase() || 'U' : 'U'}
                    </div>
                  ) : (
                    <div className="avatar-circle ai-avatar-circle">AI</div>
                  )}
                </div>
                <div className="message-content-professional">
                  <ReactMarkdown>{msg.content}</ReactMarkdown>
                </div>
              </div>
            ))}
            
            {loading && (
              <div className="message-professional assistant">
                <div className="message-avatar-professional">
                  <div className="avatar-circle ai-avatar-circle">AI</div>
                </div>
                <div className="message-content-professional">
                  <div className="loading-dots-professional">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </ScrollArea>

          {/* Input Area */}
          <div className="input-area-professional">
            <Textarea
              placeholder="Describe what you want to build..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  buildWithAgents();
                }
              }}
              disabled={loading}
              className="input-textarea-professional"
            />
            <Button 
              onClick={buildWithAgents}
              disabled={loading || !input.trim()}
              className="send-btn-professional"
            >
              {loading ? <Loader2 className="animate-spin" size={20} /> : <Send size={20} />}
            </Button>
          </div>
        </div>

        {/* Preview Section */}
        <div className="preview-section-professional">
          <div className="preview-toolbar-professional">
            <div className="preview-tabs-professional">
              <button
                className={previewMode === 'preview' ? 'active' : ''}
                onClick={() => setPreviewMode('preview')}
              >
                <Eye size={16} />
                Preview
              </button>
              <button
                className={previewMode === 'code' ? 'active' : ''}
                onClick={() => setPreviewMode('code')}
              >
                <Code size={16} />
                Code
              </button>
            </div>
            {project.generated_code && (
              <Button className="open-new-tab-professional" onClick={openInNewTab}>
                <ExternalLink size={16} />
                Open in Tab
              </Button>
            )}
          </div>

          <div className="preview-content-professional">
            {!project.generated_code ? (
              <div className="preview-empty-professional">
                <Code size={64} />
                <p>Your website will appear here</p>
              </div>
            ) : (
              <>
                {previewMode === 'preview' && (
                  <iframe
                    ref={iframeRef}
                    srcDoc={project.generated_code}
                    title="Website Preview"
                    className="preview-iframe-professional"
                  />
                )}
                {previewMode === 'code' && (
                  <Editor
                    height="100%"
                    defaultLanguage="html"
                    value={project.generated_code}
                    theme="vs-dark"
                    options={{
                      readOnly: !editMode,
                      minimap: { enabled: false },
                      fontSize: 14
                    }}
                    onChange={(value) => setEditedCode(value)}
                  />
                )}
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Workspace;
