import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import axios from 'axios';
import Workspace from './pages/Workspace';
import CreditsPage from './pages/CreditsPage';
import TermsOfService from './pages/TermsOfService';
import PrivacyPolicy from './pages/PrivacyPolicy';
import ContactPage from './pages/ContactPage';
import UserMenu from './components/UserMenu';
import EmergentLanding from './components/EmergentLanding';
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
import { loadFirebaseAuthMethods, getFirebaseAuth } from './firebaseAuth';
import { INITIAL_FREE_CREDITS } from './constants';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AuthPage = () => {
  const navigate = useNavigate();
  const [params] = React.useState(new URLSearchParams(window.location.search));
  const [mode, setMode] = useState(params.get('mode') === 'login' ? 'login' : 'register');
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [firebaseAuth, setFirebaseAuth] = useState(null);
  const [authMethods, setAuthMethods] = useState(null);

  // Initialize Firebase Auth
  useEffect(() => {
    const initFirebase = () => {
      try {
        const auth = getFirebaseAuth();
        const methods = loadFirebaseAuthMethods();
        setFirebaseAuth(auth);
        setAuthMethods(methods);
      } catch (error) {
        console.error('Firebase initialization error:', error);
        toast.error('Authentication system failed to load');
      }
    };
    
    initFirebase();
  }, []);

  // Sync Firebase user with backend
  const syncWithBackend = async (firebaseUser) => {
    try {
      const providerData = firebaseUser.providerData[0] || {};
      const payload = {
        firebase_uid: firebaseUser.uid,
        email: firebaseUser.email,
        display_name: firebaseUser.displayName || username || firebaseUser.email.split('@')[0],
        photo_url: firebaseUser.photoURL,
        provider_id: providerData.providerId || 'password'
      };

      const res = await axios.post(`${API}/auth/firebase/sync`, payload);
      
      // Store backend token and user data
      localStorage.setItem('token', res.data.access_token);
      localStorage.setItem('user', JSON.stringify(res.data.user));
      
      return res.data;
    } catch (error) {
      console.error('Backend sync error:', error);
      throw error;
    }
  };

  // Handle Email/Password Auth
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
      // Clear old data before new login
      localStorage.clear();
      
      if (mode === 'register') {
        // Try Firebase first, fallback to JWT
        if (firebaseAuth && authMethods) {
          try {
            // Firebase signup
            const userCredential = await authMethods.createUserWithEmailAndPassword(
              firebaseAuth,
              email,
              password
            );
            const firebaseUser = userCredential.user;
            
            // Sync with backend
            await syncWithBackend(firebaseUser);
            
            toast.success(`🎉 Account created! You got ${INITIAL_FREE_CREDITS} free credits!`);
            navigate('/dashboard');
            return;
          } catch (firebaseError) {
            console.warn('Firebase registration failed, trying direct backend registration:', firebaseError);
            // Fallback to direct backend registration below
          }
        }
        
        // Direct backend registration (JWT)
        const response = await axios.post(`${API}/auth/register`, {
          username: email.split('@')[0], // Use email prefix as username
          email,
          password
        });
        
        localStorage.setItem('token', response.data.access_token);
        localStorage.setItem('user', JSON.stringify(response.data.user));
        
        toast.success(`🎉 Account created! You got ${INITIAL_FREE_CREDITS} free credits!`);
        navigate('/dashboard');
      } else {
        // Try Firebase first, fallback to JWT
        if (firebaseAuth && authMethods) {
          try {
            // Firebase login
            const userCredential = await authMethods.signInWithEmailAndPassword(
              firebaseAuth,
              email,
              password
            );
            const firebaseUser = userCredential.user;
            
            // Sync with backend
            await syncWithBackend(firebaseUser);
            
            toast.success('Welcome back!');
            navigate('/dashboard');
            return;
          } catch (firebaseError) {
            console.warn('Firebase login failed, trying direct backend login:', firebaseError);
            // Fallback to direct backend login below
          }
        }
        
        // Direct backend login (JWT)
        const response = await axios.post(`${API}/auth/login`, {
          email,
          password
        });
        
        localStorage.setItem('token', response.data.access_token);
        localStorage.setItem('user', JSON.stringify(response.data.user));
        
        toast.success('Welcome back!');
        navigate('/dashboard');
      }
    } catch (error) {
      console.error('Auth error:', error);
      
      if (error.response?.data?.detail) {
        toast.error(error.response.data.detail);
      } else if (error.code === 'auth/email-already-in-use') {
        toast.error('This email is already registered. Please login instead.');
        setMode('login');
      } else if (error.code === 'auth/user-not-found') {
        toast.error('No account found with this email');
      } else if (error.code === 'auth/wrong-password') {
        toast.error('Incorrect password');
      } else if (error.code === 'auth/invalid-email') {
        toast.error('Invalid email address');
      } else if (error.code === 'auth/weak-password') {
        toast.error('Password is too weak. Use at least 6 characters.');
      } else {
        toast.error(error.message || 'Authentication failed');
      }
    } finally {
      setLoading(false);
    }
  };

  // Handle Google Sign-In
  const handleGoogleSignIn = async () => {
    if (!firebaseAuth || !authMethods) {
      toast.error('Google Sign-In not available. Please use email/password login.');
      return;
    }

    try {
      // Clear old data before new login
      localStorage.clear();
      
      const provider = new authMethods.GoogleAuthProvider();
      const result = await authMethods.signInWithPopup(firebaseAuth, provider);
      
      // Sync with backend
      await syncWithBackend(result.user);
      
      toast.success('Google login successful!');
      navigate('/dashboard');
    } catch (error) {
      console.error('Google sign-in error:', error);
      
      if (error.code === 'auth/popup-closed-by-user') {
        toast.error('Login cancelled');
      } else if (error.code === 'auth/popup-blocked') {
        toast.error('Popup blocked. Please allow popups and try again.');
      } else if (error.code === 'auth/unauthorized-domain') {
        toast.error('This domain is not authorized. Please contact support.');
      } else {
        toast.error('Google login failed. Please use email/password login.');
      }
    }
  };

  // Handle GitHub Sign-In
  const handleGitHubSignIn = async () => {
    if (!firebaseAuth || !authMethods) {
      toast.error('Authentication not ready. Please refresh.');
      return;
    }

    try {
      // Clear old data before new login
      localStorage.clear();
      
      const provider = new authMethods.GithubAuthProvider();
      const result = await authMethods.signInWithPopup(firebaseAuth, provider);
      
      // Sync with backend
      await syncWithBackend(result.user);
      
      toast.success('GitHub login successful!');
      navigate('/dashboard');
    } catch (error) {
      console.error('GitHub sign-in error:', error);
      
      if (error.code === 'auth/popup-closed-by-user') {
        toast.error('Login cancelled');
      } else if (error.code === 'auth/popup-blocked') {
        toast.error('Popup blocked. Please allow popups and try again.');
      } else if (error.code === 'auth/account-exists-with-different-credential') {
        toast.error('An account already exists with this email using a different login method');
      } else if (error.code === 'auth/unauthorized-domain') {
        toast.error('This domain is not authorized. Please contact support.');
      } else {
        toast.error(error.message || 'GitHub login failed');
      }
    }
  };

  // Handle Forgot Password
  const handleForgotPassword = async () => {
    if (!email) {
      toast.error('Please enter your email address');
      return;
    }

    if (!firebaseAuth || !authMethods) {
      toast.error('Authentication not ready. Please refresh.');
      return;
    }

    try {
      await authMethods.sendPasswordResetEmail(firebaseAuth, email);
      toast.success('Password reset email sent! Check your inbox.');
    } catch (error) {
      console.error('Password reset error:', error);
      
      if (error.code === 'auth/user-not-found') {
        toast.error('No account found with this email');
      } else {
        toast.error(error.message || 'Failed to send reset email');
      }
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
             mode === 'register' ? `Create account and get ${INITIAL_FREE_CREDITS} free credits instantly!` : 
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
                onClick={handleForgotPassword}
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
        
        {(mode === 'login' || mode === 'register') && (
          <>
            <div className="auth-divider">
              <span>OR</span>
            </div>
            
            <Button
              type="button"
              variant="outline"
              className="w-full google-login-btn"
              onClick={handleGoogleSignIn}
              data-testid="google-login-btn"
            >
              <svg className="mr-2" width="18" height="18" viewBox="0 0 18 18">
                <path fill="#4285F4" d="M17.64 9.2c0-.637-.057-1.251-.164-1.84H9v3.481h4.844c-.209 1.125-.843 2.078-1.796 2.717v2.258h2.908c1.702-1.567 2.684-3.874 2.684-6.615z"/>
                <path fill="#34A853" d="M9 18c2.43 0 4.467-.806 5.956-2.184l-2.908-2.258c-.806.54-1.837.86-3.048.86-2.344 0-4.328-1.584-5.036-3.711H.957v2.332C2.438 15.983 5.482 18 9 18z"/>
                <path fill="#FBBC05" d="M3.964 10.707c-.18-.54-.282-1.117-.282-1.707 0-.593.102-1.17.282-1.709V4.958H.957C.347 6.173 0 7.548 0 9c0 1.452.348 2.827.957 4.042l3.007-2.335z"/>
                <path fill="#EA4335" d="M9 3.58c1.321 0 2.508.454 3.44 1.345l2.582-2.58C13.463.891 11.426 0 9 0 5.482 0 2.438 2.017.957 4.958L3.964 7.29C4.672 5.163 6.656 3.58 9 3.58z"/>
              </svg>
              Continue with Google
            </Button>
            
            <Button
              type="button"
              variant="outline"
              className="w-full google-login-btn"
              onClick={handleGitHubSignIn}
              data-testid="github-login-btn"
              style={{ marginTop: '1rem' }}
            >
              <svg className="mr-2" width="18" height="18" viewBox="0 0 24 24" fill="#181717">
                <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/>
              </svg>
              Continue with GitHub
            </Button>
          </>
        )}
        
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
  const [user, setUser] = useState({});  // Start with empty, fetch from API
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [projectName, setProjectName] = useState('');
  const [projectPrompt, setProjectPrompt] = useState('');
  const [creating, setCreating] = useState(false);
  const [processingSession, setProcessingSession] = useState(false);

  // Helper to get current axios config with latest token
  const getAxiosConfig = () => ({
    headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
    withCredentials: true
  });

  // Handle Google OAuth session_id
  useEffect(() => {
    const handleGoogleSession = async () => {
      const hash = window.location.hash;
      if (hash && hash.includes('session_id=')) {
        setProcessingSession(true);
        setLoading(true);
        const sessionId = hash.split('session_id=')[1].split('&')[0];
        
        try {
          const res = await axios.post(`${API}/auth/google/session`, {}, {
            headers: { 'X-Session-ID': sessionId },
            withCredentials: true
          });
          
          // Store session token and user data
          localStorage.setItem('token', res.data.session_token);
          localStorage.setItem('user', JSON.stringify(res.data.user));
          setUser(res.data.user);
          
          // Clean URL
          window.history.replaceState({}, document.title, window.location.pathname);
          
          toast.success(`Welcome ${res.data.user.username || res.data.user.name}! You have ${res.data.user.credits} credits.`);
          
          // Fetch data immediately after successful session
          await fetchData();
        } catch (error) {
          console.error('Google auth error:', error);
          toast.error('Google authentication failed. Please try again.');
          navigate('/auth?mode=login');
        } finally {
          setProcessingSession(false);
        }
      } else {
        // No session_id, check if user is already logged in
        const token = localStorage.getItem('token');
        if (!token) {
          navigate('/auth?mode=login');
        } else {
          fetchData();
        }
      }
    };
    
    handleGoogleSession();
  }, []);

  const fetchData = async () => {
    try {
      const config = getAxiosConfig();
      const [userRes, projectsRes] = await Promise.all([
        axios.get(`${API}/auth/me`, config),
        axios.get(`${API}/projects`, config)
      ]);
      setUser(userRes.data);
      localStorage.setItem('user', JSON.stringify(userRes.data));
      setProjects(projectsRes.data);
    } catch (error) {
      console.error('Failed to load data:', error);
      if (error.response?.status === 401) {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        toast.error('Session expired. Please login again.');
        navigate('/auth?mode=login');
      } else {
        toast.error('Failed to load data');
      }
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
        model: 'gpt-5'
      }, getAxiosConfig());
      
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
      await axios.delete(`${API}/projects/${projectId}`, getAxiosConfig());
      setProjects(projects.filter(p => p.id !== projectId));
      toast.success('Project deleted');
    } catch (error) {
      toast.error('Failed to delete project');
    }
  };

  const handleLogout = async () => {
    try {
      // Call backend logout to clear session
      await axios.post(`${API}/auth/logout`, {}, { withCredentials: true });
    } catch (error) {
      console.error('Logout error:', error);
    }
    
    // Clear ALL localStorage
    localStorage.clear();
    
    // Reset user state
    setUser({});
    setProjects([]);
    
    // Navigate to login
    navigate('/auth?mode=login');
  };

  if (loading) {
    return <div className="loading-screen">Loading...</div>;
  }

  return (
    <div className="dashboard-container" data-testid="dashboard">
      <nav className="dashboard-nav">
        <div className="nav-content">
          <div className="logo" onClick={() => navigate('/dashboard')} style={{cursor: 'pointer'}}>
            <Sparkles className="logo-icon" />
            <span>AutoWebIQ</span>
          </div>
          <div className="nav-buttons">
            <div className="user-info-badge" style={{
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              padding: '8px 16px',
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              borderRadius: '8px',
              color: 'white',
              fontSize: '14px',
              fontWeight: '500'
            }}>
              <div style={{display: 'flex', flexDirection: 'column', alignItems: 'flex-start'}}>
                <span style={{fontSize: '13px', opacity: 0.9}}>👤 {user.username || user.email?.split('@')[0]}</span>
                <span style={{fontSize: '11px', opacity: 0.8}}>{user.email}</span>
              </div>
            </div>
            <div className="credits-badge" data-testid="credits-badge" style={{
              padding: '8px 16px',
              background: '#10b981',
              borderRadius: '8px',
              color: 'white',
              fontWeight: 'bold',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}>
              <CreditCard size={16} />
              <span>{user.credits} Credits</span>
            </div>
            <Button data-testid="buy-credits-btn" onClick={() => navigate('/credits')} style={{background: '#f59e0b'}}>
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
        <Route path="/" element={<EmergentLanding />} />
        <Route path="/auth" element={<AuthPage />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/workspace/:id" element={<Workspace />} />
        <Route path="/credits" element={<CreditsPage />} />
        <Route path="/terms" element={<TermsOfService />} />
        <Route path="/terms-of-service" element={<TermsOfService />} />
        <Route path="/privacy" element={<PrivacyPolicy />} />
        <Route path="/privacy-policy" element={<PrivacyPolicy />} />
        <Route path="/contact" element={<ContactPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;