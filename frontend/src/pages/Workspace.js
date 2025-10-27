import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { ScrollArea } from '@/components/ui/scroll-area';
import { toast } from 'sonner';
import { Send, Download, ArrowLeft, Loader2, Code, Eye } from 'lucide-react';
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
  const [selectedModel, setSelectedModel] = useState('gpt-5');
  const [previewMode, setPreviewMode] = useState('preview');
  const messagesEndRef = useRef(null);
  const iframeRef = useRef(null);

  const axiosConfig = {
    headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
  };

  useEffect(() => {
    fetchProject();
    fetchMessages();
  }, [id]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (project && iframeRef.current && previewMode === 'preview') {
      const iframe = iframeRef.current;
      const defaultHTML = '<html><body><div style="display:flex;align-items:center;justify-content:center;height:100vh;font-family:sans-serif;color:#666;">Send a message to generate your website...</div></body></html>';
      iframe.srcdoc = project.generated_code || defaultHTML;
    }
  }, [project, previewMode]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const fetchProject = async () => {
    try {
      const res = await axios.get(`${API}/projects/${id}`, axiosConfig);
      setProject(res.data);
      setSelectedModel(res.data.model);
    } catch (error) {
      toast.error('Failed to load project');
      navigate('/dashboard');
    }
  };

  const fetchMessages = async () => {
    try {
      const res = await axios.get(`${API}/projects/${id}/messages`, axiosConfig);
      setMessages(res.data.filter(m => m.role !== 'system'));
    } catch (error) {
      console.error('Failed to load messages');
    }
  };

  const sendMessage = async () => {
    if (!input.trim() || loading) return;
    
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
      
      toast.success('Generated!');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to generate');
      setMessages(prev => prev.slice(0, -1));
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
          <Select value={selectedModel} onValueChange={setSelectedModel}>
            <SelectTrigger className="model-selector" data-testid="model-selector">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="gpt-5">GPT-5</SelectItem>
              <SelectItem value="claude-4-sonnet-20250514">Claude Sonnet 4</SelectItem>
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
                  <Loader2 className="animate-spin" /> Generating...
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </ScrollArea>
          
          <div className="chat-input-area" data-testid="input-area">
            <Textarea
              data-testid="message-input"
              placeholder="Describe what you want to build or modify..."
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
              <Send size={18} />
            </Button>
          </div>
        </div>

        <div className="workspace-preview" data-testid="preview-panel">
          <div className="preview-toolbar">
            <div className="preview-tabs">
              <button
                className={previewMode === 'preview' ? 'active' : ''}
                onClick={() => setPreviewMode('preview')}
                data-testid="preview-tab"
              >
                <Eye size={16} /> Preview
              </button>
              <button
                className={previewMode === 'code' ? 'active' : ''}
                onClick={() => setPreviewMode('code')}
                data-testid="code-tab"
              >
                <Code size={16} /> Code
              </button>
            </div>
          </div>
          
          {previewMode === 'preview' ? (
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
