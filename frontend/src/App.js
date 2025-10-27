import React, { useState, useEffect, useRef } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Card } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { toast } from 'sonner';
import { Send, Plus, Trash2, Image as ImageIcon, Upload, Menu, X, MessageSquare, Sparkles, LogOut, Edit2, Check } from 'lucide-react';
import '@/App.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function App() {
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [user, setUser] = useState(null);
  const [showAuth, setShowAuth] = useState(!token);
  const [isLogin, setIsLogin] = useState(true);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [conversations, setConversations] = useState([]);
  const [currentConversation, setCurrentConversation] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [showImageDialog, setShowImageDialog] = useState(false);
  const [imagePrompt, setImagePrompt] = useState('');
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [editingConvId, setEditingConvId] = useState(null);
  const [editTitle, setEditTitle] = useState('');
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);

  const axiosConfig = {
    headers: token ? { Authorization: `Bearer ${token}` } : {}
  };

  useEffect(() => {
    if (token) {
      fetchUser();
      fetchConversations();
    }
  }, [token]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const fetchUser = async () => {
    try {
      const res = await axios.get(`${API}/auth/me`, axiosConfig);
      setUser(res.data);
    } catch (error) {
      console.error('Failed to fetch user', error);
      handleLogout();
    }
  };

  const fetchConversations = async () => {
    try {
      const res = await axios.get(`${API}/conversations`, axiosConfig);
      setConversations(res.data);
      if (res.data.length > 0 && !currentConversation) {
        loadConversation(res.data[0].id);
      }
    } catch (error) {
      console.error('Failed to fetch conversations', error);
    }
  };

  const loadConversation = async (convId) => {
    try {
      const res = await axios.get(`${API}/conversations/${convId}`, axiosConfig);
      setCurrentConversation(res.data.conversation);
      setMessages(res.data.messages);
    } catch (error) {
      console.error('Failed to load conversation', error);
    }
  };

  const handleAuth = async (e) => {
    e.preventDefault();
    try {
      const endpoint = isLogin ? '/auth/login' : '/auth/register';
      const res = await axios.post(`${API}${endpoint}`, { username, password });
      localStorage.setItem('token', res.data.access_token);
      setToken(res.data.access_token);
      setUser({ username: res.data.username });
      setShowAuth(false);
      toast.success(isLogin ? 'Welcome back!' : 'Account created!');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Authentication failed');
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
    setShowAuth(true);
    setConversations([]);
    setCurrentConversation(null);
    setMessages([]);
  };

  const createConversation = async () => {
    try {
      const res = await axios.post(`${API}/conversations`, { title: 'New Conversation' }, axiosConfig);
      setConversations([res.data, ...conversations]);
      setCurrentConversation(res.data);
      setMessages([]);
      toast.success('New conversation started');
    } catch (error) {
      toast.error('Failed to create conversation');
    }
  };

  const deleteConversation = async (convId, e) => {
    e.stopPropagation();
    try {
      await axios.delete(`${API}/conversations/${convId}`, axiosConfig);
      setConversations(conversations.filter(c => c.id !== convId));
      if (currentConversation?.id === convId) {
        setCurrentConversation(null);
        setMessages([]);
        if (conversations.length > 1) {
          const nextConv = conversations.find(c => c.id !== convId);
          if (nextConv) loadConversation(nextConv.id);
        }
      }
      toast.success('Conversation deleted');
    } catch (error) {
      toast.error('Failed to delete conversation');
    }
  };

  const updateConversationTitle = async (convId, newTitle) => {
    try {
      await axios.put(`${API}/conversations/${convId}`, { title: newTitle }, axiosConfig);
      setConversations(conversations.map(c => c.id === convId ? { ...c, title: newTitle } : c));
      if (currentConversation?.id === convId) {
        setCurrentConversation({ ...currentConversation, title: newTitle });
      }
      setEditingConvId(null);
    } catch (error) {
      toast.error('Failed to update title');
    }
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || !currentConversation) return;

    const userMsg = inputMessage;
    setInputMessage('');
    setLoading(true);

    // Optimistically add user message
    const tempUserMsg = { role: 'user', content: userMsg, created_at: new Date().toISOString() };
    setMessages([...messages, tempUserMsg]);

    try {
      const res = await axios.post(`${API}/messages`, {
        conversation_id: currentConversation.id,
        content: userMsg
      }, axiosConfig);

      setMessages(prev => [...prev.slice(0, -1), res.data.user_message, res.data.ai_message]);
    } catch (error) {
      toast.error('Failed to send message');
      setMessages(prev => prev.slice(0, -1));
    } finally {
      setLoading(false);
    }
  };

  const generateImage = async () => {
    if (!imagePrompt.trim() || !currentConversation) return;

    setLoading(true);
    setShowImageDialog(false);

    try {
      const res = await axios.post(`${API}/generate-image`, {
        conversation_id: currentConversation.id,
        prompt: imagePrompt
      }, axiosConfig);

      setMessages([...messages, res.data.message]);
      setImagePrompt('');
      toast.success('Image generated!');
    } catch (error) {
      toast.error('Failed to generate image');
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file || !currentConversation) return;

    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await axios.post(`${API}/upload-file?conversation_id=${currentConversation.id}`, formData, {
        ...axiosConfig,
        headers: { ...axiosConfig.headers, 'Content-Type': 'multipart/form-data' }
      });

      await fetchConversations();
      await loadConversation(currentConversation.id);
      toast.success('File analyzed!');
    } catch (error) {
      toast.error('Failed to upload file');
    } finally {
      setLoading(false);
    }
  };

  if (showAuth) {
    return (
      <div className="auth-container" data-testid="auth-page">
        <div className="auth-card">
          <div className="auth-header">
            <Sparkles className="auth-icon" data-testid="sparkles-icon" />
            <h1 data-testid="auth-title">AI Assistant</h1>
            <p data-testid="auth-subtitle">Your intelligent companion</p>
          </div>
          
          <form onSubmit={handleAuth} data-testid="auth-form">
            <Input
              data-testid="username-input"
              type="text"
              placeholder="Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
            <Input
              data-testid="password-input"
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
            <Button data-testid="auth-submit-btn" type="submit" className="w-full">
              {isLogin ? 'Login' : 'Register'}
            </Button>
          </form>
          
          <button
            data-testid="toggle-auth-mode-btn"
            className="auth-toggle"
            onClick={() => setIsLogin(!isLogin)}
          >
            {isLogin ? "Don't have an account? Register" : 'Already have an account? Login'}
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="app-container" data-testid="main-app">
      {/* Sidebar */}
      <div className={`sidebar ${sidebarOpen ? 'open' : 'closed'}`} data-testid="sidebar">
        <div className="sidebar-header">
          <div className="sidebar-title">
            <Sparkles size={24} data-testid="sidebar-sparkles-icon" />
            <span data-testid="sidebar-title-text">AI Assistant</span>
          </div>
          <Button
            data-testid="new-conversation-btn"
            size="sm"
            onClick={createConversation}
            className="new-conv-btn"
          >
            <Plus size={18} />
          </Button>
        </div>

        <ScrollArea className="conversations-list" data-testid="conversations-list">
          {conversations.map((conv) => (
            <div
              key={conv.id}
              data-testid={`conversation-item-${conv.id}`}
              className={`conversation-item ${currentConversation?.id === conv.id ? 'active' : ''}`}
              onClick={() => loadConversation(conv.id)}
            >
              <MessageSquare size={18} data-testid={`conversation-icon-${conv.id}`} />
              {editingConvId === conv.id ? (
                <div className="edit-title-container">
                  <Input
                    data-testid={`edit-title-input-${conv.id}`}
                    value={editTitle}
                    onChange={(e) => setEditTitle(e.target.value)}
                    onClick={(e) => e.stopPropagation()}
                    className="edit-title-input"
                  />
                  <Button
                    data-testid={`save-title-btn-${conv.id}`}
                    size="sm"
                    onClick={(e) => {
                      e.stopPropagation();
                      updateConversationTitle(conv.id, editTitle);
                    }}
                  >
                    <Check size={14} />
                  </Button>
                </div>
              ) : (
                <>
                  <span data-testid={`conversation-title-${conv.id}`} className="conversation-title">{conv.title}</span>
                  <div className="conversation-actions">
                    <Button
                      data-testid={`edit-conversation-btn-${conv.id}`}
                      size="sm"
                      variant="ghost"
                      onClick={(e) => {
                        e.stopPropagation();
                        setEditingConvId(conv.id);
                        setEditTitle(conv.title);
                      }}
                    >
                      <Edit2 size={14} />
                    </Button>
                    <Button
                      data-testid={`delete-conversation-btn-${conv.id}`}
                      size="sm"
                      variant="ghost"
                      onClick={(e) => deleteConversation(conv.id, e)}
                    >
                      <Trash2 size={14} />
                    </Button>
                  </div>
                </>
              )}
            </div>
          ))}
        </ScrollArea>

        <div className="sidebar-footer">
          <div className="user-info" data-testid="user-info">
            <span data-testid="username-display">{user?.username}</span>
          </div>
          <Button
            data-testid="logout-btn"
            size="sm"
            variant="ghost"
            onClick={handleLogout}
          >
            <LogOut size={18} />
          </Button>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="chat-container" data-testid="chat-container">
        <div className="chat-header">
          <Button
            data-testid="toggle-sidebar-btn"
            size="sm"
            variant="ghost"
            onClick={() => setSidebarOpen(!sidebarOpen)}
          >
            {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
          </Button>
          <h2 data-testid="chat-header-title">{currentConversation?.title || 'Select a conversation'}</h2>
        </div>

        <ScrollArea className="messages-area" data-testid="messages-area">
          {messages.map((msg, idx) => (
            <div key={idx} data-testid={`message-${idx}`} className={`message ${msg.role}`}>
              <div className="message-content">
                {msg.image_url ? (
                  <img data-testid={`message-image-${idx}`} src={msg.image_url} alt="Generated" className="generated-image" />
                ) : (
                  <ReactMarkdown
                    data-testid={`message-text-${idx}`}
                    components={{
                      code({ node, inline, className, children, ...props }) {
                        const match = /language-(\w+)/.exec(className || '');
                        return !inline && match ? (
                          <SyntaxHighlighter
                            style={vscDarkPlus}
                            language={match[1]}
                            PreTag="div"
                            {...props}
                          >
                            {String(children).replace(/\n$/, '')}
                          </SyntaxHighlighter>
                        ) : (
                          <code className={className} {...props}>
                            {children}
                          </code>
                        );
                      }
                    }}
                  >
                    {msg.content}
                  </ReactMarkdown>
                )}
              </div>
            </div>
          ))}
          {loading && (
            <div data-testid="loading-indicator" className="message assistant">
              <div className="message-content">
                <div className="typing-indicator">
                  <span></span><span></span><span></span>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </ScrollArea>

        <div className="input-area" data-testid="input-area">
          <input
            data-testid="file-input"
            type="file"
            ref={fileInputRef}
            style={{ display: 'none' }}
            onChange={handleFileUpload}
          />
          <Button
            data-testid="upload-file-btn"
            size="sm"
            variant="ghost"
            onClick={() => fileInputRef.current?.click()}
            disabled={!currentConversation || loading}
          >
            <Upload size={20} />
          </Button>
          <Button
            data-testid="generate-image-btn"
            size="sm"
            variant="ghost"
            onClick={() => setShowImageDialog(true)}
            disabled={!currentConversation || loading}
          >
            <ImageIcon size={20} />
          </Button>
          <Textarea
            data-testid="message-input"
            placeholder="Type your message..."
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
              }
            }}
            disabled={!currentConversation || loading}
            className="message-input"
          />
          <Button
            data-testid="send-message-btn"
            onClick={sendMessage}
            disabled={!currentConversation || loading || !inputMessage.trim()}
          >
            <Send size={20} />
          </Button>
        </div>
      </div>

      {/* Image Generation Dialog */}
      <Dialog open={showImageDialog} onOpenChange={setShowImageDialog}>
        <DialogContent data-testid="image-dialog">
          <DialogHeader>
            <DialogTitle data-testid="image-dialog-title">Generate Image</DialogTitle>
          </DialogHeader>
          <Textarea
            data-testid="image-prompt-input"
            placeholder="Describe the image you want to generate..."
            value={imagePrompt}
            onChange={(e) => setImagePrompt(e.target.value)}
          />
          <Button data-testid="generate-image-submit-btn" onClick={generateImage} disabled={!imagePrompt.trim()}>
            Generate
          </Button>
        </DialogContent>
      </Dialog>
    </div>
  );
}

export default App;