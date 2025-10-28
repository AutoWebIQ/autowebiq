import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import axios from 'axios';
import Workspace from './pages/Workspace';
import CreditsPage from './pages/CreditsPage';
import UserMenu from './components/UserMenu';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Card } from '@/components/ui/card';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog';
import { ScrollArea } from '@/components/ui/scroll-area';
import { toast } from 'sonner';
import { Sparkles, Code, Zap, Download, Eye, Trash2, Plus, CreditCard, Rocket, Menu, X, LogOut, CheckCircle, Loader2 } from 'lucide-react';
import Prism from 'prismjs';
import 'prismjs/themes/prism-tomorrow.css';
import '@/App.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const LandingPage = () => {
  const navigate = useNavigate();
  
  return (
    <div className="landing-page" data-testid="landing-page">
      <nav className="landing-nav">
        <div className="nav-content">
          <div className="logo" data-testid="logo">
            <Sparkles className="logo-icon" />
            <span>AutoWebIQ</span>
          </div>
          <div className="nav-buttons">
            <Button data-testid="nav-login-btn" variant="ghost" onClick={() => navigate('/auth?mode=login')}>Login</Button>
            <Button data-testid="nav-signup-btn" onClick={() => navigate('/auth?mode=register')}>Get Started Free</Button>
          </div>
        </div>
      </nav>
      
      <section className="hero-section" data-testid="hero-section">
        <div className="hero-content">
          <h1 data-testid="hero-title">Build Websites with AI in Seconds</h1>
          <p data-testid="hero-subtitle">Transform your ideas into beautiful, functional websites using the power of GPT-5. No coding required.</p>
          <div className="hero-buttons">
            <Button data-testid="hero-cta-btn" size="lg" onClick={() => navigate('/auth?mode=register')}>
              <Rocket className="mr-2" />Start Building - 50 Free Credits
            </Button>
          </div>
          <div className="hero-features">
            <div className="feature-badge" data-testid="feature-1">
              <CheckCircle size={16} /> 50 Free Credits
            </div>
            <div className="feature-badge" data-testid="feature-2">
              <CheckCircle size={16} /> GPT-5 Powered
            </div>
            <div className="feature-badge" data-testid="feature-3">
              <CheckCircle size={16} /> Instant Preview
            </div>
          </div>
        </div>
      </section>
      
      <section className="features-section" data-testid="features-section">
        <h2 data-testid="features-title">Why Choose Optra AI?</h2>
        <div className="features-grid">
          <Card className="feature-card" data-testid="feature-card-1">
            <Sparkles className="feature-icon" />
            <h3>AI-Powered Generation</h3>
            <p>Powered by GPT-5 for intelligent, creative website generation</p>
          </Card>
          <Card className="feature-card" data-testid="feature-card-2">
            <Code className="feature-icon" />
            <h3>Clean Code</h3>
            <p>Production-ready HTML, CSS, and JavaScript code</p>
          </Card>
          <Card className="feature-card" data-testid="feature-card-3">
            <Eye className="feature-icon" />
            <h3>Live Preview</h3>
            <p>See your website instantly with our live preview feature</p>
          </Card>
          <Card className="feature-card" data-testid="feature-card-4">
            <Download className="feature-icon" />
            <h3>Download & Deploy</h3>
            <p>Download your website as a ZIP file and deploy anywhere</p>
          </Card>
        </div>
      </section>
    </div>
  );
};

const AuthPage = () => {
  const navigate = useNavigate();
  const [params] = React.useState(new URLSearchParams(window.location.search));
  const [mode, setMode] = useState(params.get('mode') === 'login' ? 'login' : 'register');
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [resetCode, setResetCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const handleAuth = async (e) => {
    e.preventDefault();
    
    // Validation
    if (mode === 'register') {
      if (password.length < 6) {
        toast.error('Password must be at least 6 characters');
        return;
      }
      if (password !== confirmPassword) {
        toast.error('Passwords do not match');
        return;
      }
    }
    
    setLoading(true);
    
    try {
      if (mode === 'forgot') {
        const res = await axios.post(`${API}/auth/forgot-password`, { email });
        toast.success('Reset code sent! Check the console (dev mode)');
        console.log('Reset code:', res.data.code);
        setMode('reset');
      } else if (mode === 'reset') {
        await axios.post(`${API}/auth/reset-password`, {
          email,
          reset_code: resetCode,
          new_password: password
        });
        toast.success('Password reset successful! Please login');
        setMode('login');
        setPassword('');
        setResetCode('');
      } else {
        const endpoint = mode === 'login' ? '/auth/login' : '/auth/register';
        const payload = mode === 'login' 
          ? { email, password }
          : { username, email, password };
        
        const res = await axios.post(`${API}${endpoint}`, payload);
        localStorage.setItem('token', res.data.access_token);
        localStorage.setItem('user', JSON.stringify(res.data.user));
        toast.success(mode === 'login' ? 'Welcome back!' : '🎉 Account created! You got 50 free credits!');
        navigate('/dashboard');
      }
    } catch (error) {
      const errorMsg = error.response?.data?.detail || 'Something went wrong';
      if (errorMsg.includes('already exists')) {
        toast.error('This email is already registered. Please login instead.');
        setMode('login');
      } else {
        toast.error(errorMsg);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container" data-testid="auth-page">
      <div className="auth-card">
        <div className="auth-header">
          <div className="auth-logo">
            <Sparkles className="auth-icon" />
          </div>
          <h1 data-testid="auth-title">
            {mode === 'login' ? 'Welcome Back!' : mode === 'register' ? 'Get Started' : mode === 'forgot' ? 'Forgot Password?' : 'Reset Password'}
          </h1>
          <p data-testid="auth-subtitle">
            {mode === 'login' ? 'Login to continue building amazing websites' : 
             mode === 'register' ? 'Create account and get 50 free credits instantly!' : 
             mode === 'forgot' ? 'Enter your email to receive a reset code' :
             'Enter the code and your new password'}
          </p>
        </div>
        
        <form onSubmit={handleAuth} data-testid="auth-form">
          {mode === 'register' && (
            <div className="input-group">
              <label>Username</label>
              <Input
                data-testid="username-input"
                type="text"
                placeholder="Choose a username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
              />
            </div>
          )}
          
          {mode !== 'reset' && (
            <div className="input-group">
              <label>Email</label>
              <Input
                data-testid="email-input"
                type="email"
                placeholder="your@email.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>
          )}
          
          {mode === 'reset' && (
            <div className="input-group">
              <label>Reset Code</label>
              <Input
                data-testid="reset-code-input"
                type="text"
                placeholder="Enter 6-digit code"
                value={resetCode}
                onChange={(e) => setResetCode(e.target.value)}
                maxLength={6}
                required
              />
            </div>
          )}
          
          {(mode === 'login' || mode === 'register' || mode === 'reset') && (
            <div className="input-group">
              <label>{mode === 'reset' ? 'New Password' : 'Password'}</label>
              <div className="password-input">
                <Input
                  data-testid="password-input"
                  type={showPassword ? "text" : "password"}
                  placeholder={mode === 'register' ? 'Min. 6 characters' : 'Enter password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
                <button
                  type="button"
                  className="password-toggle"
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? '👁️' : '👁️‍🗨️'}
                </button>
              </div>
            </div>
          )}
          
          {mode === 'register' && (
            <div className="input-group">
              <label>Confirm Password</label>
              <Input
                data-testid="confirm-password-input"
                type={showPassword ? "text" : "password"}
                placeholder="Confirm password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
              />
            </div>
          )}
          
          {mode === 'login' && (
            <div className="auth-options">
              <button
                type="button"
                className="forgot-password-link"
                onClick={() => setMode('forgot')}
              >
                Forgot password?
              </button>
            </div>
          )}
          
          <Button 
            data-testid="auth-submit-btn" 
            type="submit" 
            className="w-full auth-submit-btn" 
            disabled={loading}
          >
            {loading ? (
              <><Loader2 className="animate-spin mr-2" size={18} /> Processing...</>
            ) : (
              mode === 'login' ? 'Login' : 
              mode === 'register' ? '🚀 Create Account' : 
              mode === 'forgot' ? 'Send Reset Code' : 
              'Reset Password'
            )}
          </Button>
        </form>
        
        <div className="auth-footer">
          {mode === 'login' ? (
            <>
              <p>Don't have an account?</p>
              <button
                data-testid="toggle-auth-mode-btn"
                className="auth-toggle"
                onClick={() => setMode('register')}
              >
                Sign up for free
              </button>
            </>
          ) : mode === 'register' ? (
            <>
              <p>Already have an account?</p>
              <button
                data-testid="toggle-auth-mode-btn"
                className="auth-toggle"
                onClick={() => setMode('login')}
              >
                Login here
              </button>
            </>
          ) : (
            <button
              className="auth-toggle"
              onClick={() => setMode('login')}
            >
              ← Back to login
            </button>
          )}
        </div>
        
        {mode === 'register' && (
          <div className="auth-terms">
            <p>By signing up, you agree to our Terms of Service and Privacy Policy</p>
          </div>
        )}
      </div>
    </div>
  );
};

const Dashboard = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState(JSON.parse(localStorage.getItem('user') || '{}'));
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [projectName, setProjectName] = useState('');
  const [projectPrompt, setProjectPrompt] = useState('');
  const [creating, setCreating] = useState(false);

  const axiosConfig = {
    headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [userRes, projectsRes] = await Promise.all([
        axios.get(`${API}/auth/me`, axiosConfig),
        axios.get(`${API}/projects`, axiosConfig)
      ]);
      setUser(userRes.data);
      localStorage.setItem('user', JSON.stringify(userRes.data));
      setProjects(projectsRes.data);
    } catch (error) {
      toast.error('Failed to load data');
      navigate('/auth?mode=login');
    } finally {
      setLoading(false);
    }
  };

  const createProject = async (e) => {
    e.preventDefault();
    if (user.credits < 1) {
      toast.error('Insufficient credits. Please buy more credits.');
      navigate('/credits');
      return;
    }
    
    setCreating(true);
    try {
      const res = await axios.post(`${API}/projects/create`, {
        name: projectName,
        description: projectPrompt,
        model: 'claude-4.5-sonnet-200k'
      }, axiosConfig);
      
      toast.success('Project created! Opening workspace...');
      setShowCreateDialog(false);
      setProjectName('');
      setProjectPrompt('');
      navigate(`/workspace/${res.data.id}`);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to create project');
    } finally {
      setCreating(false);
    }
  };

  const deleteProject = async (projectId) => {
    try {
      await axios.delete(`${API}/projects/${projectId}`, axiosConfig);
      setProjects(projects.filter(p => p.id !== projectId));
      toast.success('Project deleted');
    } catch (error) {
      toast.error('Failed to delete project');
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    navigate('/');
  };

  if (loading) {
    return <div className="loading-screen">Loading...</div>;
  }

  return (
    <div className="dashboard-container" data-testid="dashboard">
      <nav className="dashboard-nav">
        <div className="nav-content">
          <div className="logo" onClick={() => navigate('/dashboard')}>
            <Sparkles className="logo-icon" />
            <span>AutoWebIQ</span>
          </div>
          <div className="nav-buttons">
            <div className="credits-badge" data-testid="credits-badge">
              <CreditCard size={16} />
              <span>{user.credits} Credits</span>
            </div>
            <Button data-testid="buy-credits-btn" onClick={() => navigate('/credits')}>
              Buy Credits
            </Button>
            <UserMenu user={user} onLogout={handleLogout} />
          </div>
        </div>
      </nav>

      <div className="dashboard-content">
        <div className="dashboard-header">
          <div>
            <h1 data-testid="dashboard-title">My Projects</h1>
            <p data-testid="dashboard-subtitle">Create and manage your AI-generated websites</p>
          </div>
          <Button data-testid="create-project-btn" size="lg" onClick={() => setShowCreateDialog(true)}>
            <Plus className="mr-2" /> New Project
          </Button>
        </div>

        <div className="projects-grid" data-testid="projects-grid">
          {projects.map(project => (
            <Card key={project.id} className="project-card" data-testid={`project-card-${project.id}`}>
              <div className="project-card-header">
                <h3 data-testid={`project-name-${project.id}`}>{project.name}</h3>
                <div className="project-card-status" data-testid={`project-status-${project.id}`}>
                  {project.status === 'completed' && <CheckCircle size={16} className="text-green-500" />}
                  {project.status === 'generating' && <div className="spinner" />}
                </div>
              </div>
              <p className="project-prompt" data-testid={`project-prompt-${project.id}`}>{project.prompt}</p>
              <div className="project-card-actions">
                <Button
                  data-testid={`view-project-btn-${project.id}`}
                  size="sm"
                  onClick={() => navigate(`/workspace/${project.id}`)}
                >
                  <Eye size={16} className="mr-1" /> Open
                </Button>
                <Button
                  data-testid={`delete-project-btn-${project.id}`}
                  size="sm"
                  variant="ghost"
                  onClick={() => deleteProject(project.id)}
                >
                  <Trash2 size={16} />
                </Button>
              </div>
            </Card>
          ))}
          
          {projects.length === 0 && (
            <div className="empty-state" data-testid="empty-state">
              <Sparkles size={48} className="empty-icon" />
              <h3>No projects yet</h3>
              <p>Create your first AI-generated website</p>
              <Button onClick={() => setShowCreateDialog(true)}>Create Project</Button>
            </div>
          )}
        </div>
      </div>

      <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
        <DialogContent data-testid="create-project-dialog" aria-describedby="create-project-description">
          <DialogHeader>
            <DialogTitle>Create New Project</DialogTitle>
            <DialogDescription id="create-project-description">
              Describe your website and let AI build it for you (uses credits per message)
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={createProject} className="create-project-form">
            <Input
              data-testid="project-name-input"
              placeholder="Project Name"
              value={projectName}
              onChange={(e) => setProjectName(e.target.value)}
              required
            />
            <Textarea
              data-testid="project-prompt-input"
              placeholder="Describe your website... (e.g., 'A modern landing page for a coffee shop with menu, location, and contact form')"
              value={projectPrompt}
              onChange={(e) => setProjectPrompt(e.target.value)}
              rows={6}
              required
            />
            <Button data-testid="generate-btn" type="submit" disabled={creating} className="w-full">
              {creating ? 'Creating Project...' : 'Create Project (Free)'}
            </Button>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
};

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/auth" element={<AuthPage />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/workspace/:id" element={<Workspace />} />
        <Route path="/credits" element={<CreditsPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;