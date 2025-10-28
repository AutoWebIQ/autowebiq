import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import Editor from '@monaco-editor/react';
import { useDropzone } from 'react-dropzone';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { ScrollArea } from '@/components/ui/scroll-area';
import { toast } from 'sonner';
import { Send, Download, ArrowLeft, Loader2, Code, Eye, ExternalLink, CreditCard, Mic, MicOff, Image as ImageIcon, Edit3, Save } from 'lucide-react';
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
  const [selectedModel, setSelectedModel] = useState('claude-4.5-sonnet-200k');
  const [previewMode, setPreviewMode] = useState('preview');
  const [editMode, setEditMode] = useState(false);
  const [editedCode, setEditedCode] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [uploadingFile, setUploadingFile] = useState(false);
  const [userCredits, setUserCredits] = useState(0);
  const [models, setModels] = useState({});
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
    fetchModels();
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
      setSelectedModel(res.data.model);
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
      const res = await axios.get(`${API}/auth/me`, axiosConfig);
      setUserCredits(res.data.credits);
    } catch (error) {
      console.error('Failed to load credits');
    }
  };

  const fetchModels = async () => {
    try {
      const res = await axios.get(`${API}/models`);
      setModels(res.data);
    } catch (error) {
      console.error('Failed to load models');
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
      }, axiosConfig);
      
      setProject(prev => ({ ...prev, generated_code: editedCode }));
      setEditMode(false);
      toast.success('Code saved successfully!');
    } catch (error) {
      toast.error('Failed to save code');
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg', '.gif', '.webp'],
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
        
        const res = await axios.post(`${API}/upload`, formData, {
          ...axiosConfig,
          headers: {
            ...axiosConfig.headers,
            'Content-Type': 'multipart/form-data'
          }
        });
        
        // Add file info to chat
        setInput(prev => prev + `\n[Uploaded: ${file.name} - ${res.data.url}]`);
        toast.success('File uploaded!');
      } catch (error) {
        toast.error('Upload failed');
      } finally {
        setUploadingFile(false);
      }
    }
  });

  const sendMessage = async () => {
    if (!input.trim() || loading) return;
    
    const modelCost = models[selectedModel]?.cost || 5;
    
    // Check credits
    if (userCredits < modelCost) {
      toast.error(`Insufficient credits! Need ${modelCost} credits. Buy more credits.`);
      navigate('/credits');
      return;
    }
    
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
        message: messageText,
        model: selectedModel
      }, axiosConfig);
      
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: res.data.ai_message.content,
        created_at: res.data.ai_message.created_at
      }]);
      
      if (res.data.code) {
        setProject(prev => ({ ...prev, generated_code: res.data.code }));
      }
      
      // Update credits
      setUserCredits(prev => prev - modelCost);
      
      toast.success(`Generated! Used ${modelCost} credits`);
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

  const downloadProject = async () => {
    try {
      const res = await axios.get(`${API}/projects/${id}/download`, {
        ...axiosConfig,
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${project.name}.zip`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      toast.success('Downloaded!');
    } catch (error) {
      toast.error('Download failed');
    }
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
    <div className="workspace-container" data-testid="workspace">
      <div className="workspace-header">
        <div className="header-left">
          <Button variant="ghost" onClick={() => navigate('/dashboard')} data-testid="back-btn">
            <ArrowLeft className="mr-2" size={18} /> Dashboard
          </Button>
          <div className="project-info">
            <h2 data-testid="project-name">{project.name}</h2>
            <p data-testid="project-desc">{project.description}</p>
          </div>
        </div>
        <div className="header-right">
          <div className="credits-display" data-testid="credits-display">
            <CreditCard size={16} />
            <span>{userCredits} Credits</span>
          </div>
          <Select value={selectedModel} onValueChange={setSelectedModel}>
            <SelectTrigger className="model-selector" data-testid="model-selector">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="claude-4.5-sonnet-200k">
                Claude 4.5 Sonnet (200k) - {models['claude-4.5-sonnet-200k']?.cost || 5} credits
              </SelectItem>
              <SelectItem value="claude-4.5-sonnet-1m">
                Claude 4.5 Sonnet - 1M (PRO) - {models['claude-4.5-sonnet-1m']?.cost || 10} credits
              </SelectItem>
              <SelectItem value="gpt-5">
                GPT-5 (Beta) - {models['gpt-5']?.cost || 8} credits
              </SelectItem>
              <SelectItem value="claude-4-sonnet-20250514">
                Claude 4.0 Sonnet - {models['claude-4-sonnet-20250514']?.cost || 4} credits
              </SelectItem>
            </SelectContent>
          </Select>
          <Button onClick={downloadProject} data-testid="download-btn">
            <Download size={18} className="mr-2" /> Download
          </Button>
        </div>
      </div>

      <div className="workspace-content">
        <div className="workspace-chat" data-testid="chat-panel">
          <ScrollArea className="chat-messages">
            {messages.map((msg, idx) => (
              <div key={idx} className={`chat-message ${msg.role}`} data-testid={`message-${idx}`}>
                <div className="message-avatar">
                  {msg.role === 'user' ? '👤' : '🤖'}
                </div>
                <div className="message-content">
                  <ReactMarkdown>{msg.content}</ReactMarkdown>
                </div>
              </div>
            ))}
            {loading && (
              <div className="chat-message assistant" data-testid="loading-message">
                <div className="message-avatar">🤖</div>
                <div className="message-content">
                  <div className="thinking-animation">
                    <div className="thinking-dots">
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>
                    <p className="thinking-text">AI is thinking and generating your website...</p>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </ScrollArea>
          
          <div className="chat-input-area" data-testid="input-area">
            <div className="input-actions">
              <Button
                data-testid="voice-btn"
                size="sm"
                variant={isRecording ? "destructive" : "ghost"}
                onClick={toggleVoiceRecording}
                disabled={loading}
                title="Voice input"
              >
                {isRecording ? <MicOff size={18} /> : <Mic size={18} />}
              </Button>
              <div {...getRootProps()}>
                <input {...getInputProps()} />
                <Button
                  data-testid="upload-btn"
                  size="sm"
                  variant="ghost"
                  disabled={loading || uploadingFile}
                  title="Upload image/video/file"
                >
                  {uploadingFile ? <Loader2 className="animate-spin" size={18} /> : <ImageIcon size={18} />}
                </Button>
              </div>
            </div>
            <Textarea
              data-testid="message-input"
              placeholder="Describe what you want to build or modify... (Press Enter to send, Shift+Enter for new line)"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  sendMessage();
                }
              }}
              disabled={loading}
            />
            <Button onClick={sendMessage} disabled={loading || !input.trim()} data-testid="send-btn">
              {loading ? <Loader2 className="animate-spin" size={18} /> : <Send size={18} />}
            </Button>
          </div>
        </div>

        <div className="workspace-preview" data-testid="preview-panel">
          <div className="preview-toolbar">
            <div className="preview-tabs">
              <button
                className={previewMode === 'preview' ? 'active' : ''}
                onClick={() => {setPreviewMode('preview'); setEditMode(false);}}
                data-testid="preview-tab"
              >
                <Eye size={16} /> Preview
              </button>
              <button
                className={previewMode === 'code' ? 'active' : ''}
                onClick={() => {setPreviewMode('code'); setEditMode(false);}}
                data-testid="code-tab"
              >
                <Code size={16} /> Code
              </button>
              <button
                className={editMode ? 'active' : ''}
                onClick={() => {setEditMode(!editMode); setPreviewMode('code');}}
                data-testid="edit-tab"
              >
                <Edit3 size={16} /> Edit
              </button>
            </div>
            <div className="preview-actions">
              {editMode && (
                <Button 
                  size="sm" 
                  onClick={saveEditedCode}
                  data-testid="save-code-btn"
                >
                  <Save size={16} className="mr-1" /> Save Changes
                </Button>
              )}
              <Button 
                size="sm" 
                variant="outline" 
                onClick={openInNewTab}
                data-testid="open-new-tab-btn"
                disabled={!project.generated_code}
              >
                <ExternalLink size={16} className="mr-1" /> Open in New Tab
              </Button>
            </div>
          </div>
          
          {editMode ? (
            <div className="code-editor" data-testid="code-editor">
              <Editor
                height="100%"
                defaultLanguage="html"
                value={editedCode}
                onChange={(value) => setEditedCode(value || '')}
                theme="vs-dark"
                options={{
                  minimap: { enabled: false },
                  fontSize: 14,
                  wordWrap: 'on',
                  scrollBeyondLastLine: false,
                }}
              />
            </div>
          ) : previewMode === 'preview' ? (
            <iframe
              ref={iframeRef}
              className="preview-iframe"
              title="Website Preview"
              data-testid="preview-iframe"
            />
          ) : (
            <ScrollArea className="code-view" data-testid="code-view">
              <pre>
                <code>{project.generated_code || '// No code generated yet...'}</code>
              </pre>
            </ScrollArea>
          )}
        </div>
      </div>
    </div>
  );
};

export default Workspace;
