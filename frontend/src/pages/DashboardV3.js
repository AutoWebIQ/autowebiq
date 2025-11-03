import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Sparkles, Plus, Eye, Download, Trash2, TrendingUp, Users, Zap, Crown, Globe, Calendar, Clock } from 'lucide-react';
import { toast } from 'sonner';
import './DashboardV3.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const DashboardV3 = ({ user, onLogout }) => {
  const navigate = useNavigate();
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({ totalProjects: 0, websitesGenerated: 0, creditsUsed: 0 });
  const [showNewProject, setShowNewProject] = useState(false);
  const [projectName, setProjectName] = useState('');
  const [projectDesc, setProjectDesc] = useState('');

  useEffect(() => {
    fetchProjects();
    calculateStats();
  }, []);

  const fetchProjects = async () => {
    try {
      const res = await fetch(`${API}/projects`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      if (res.ok) {
        const data = await res.json();
        setProjects(data.projects || []);
      }
    } catch (error) {
      console.error('Error fetching projects:', error);
    } finally {
      setLoading(false);
    }
  };

  const calculateStats = () => {
    const totalProjects = projects.length;
    const websitesGenerated = projects.filter(p => p.generated_code).length;
    const creditsUsed = 1000 - (user?.credits || 0); // Assuming 1000 starting
    setStats({ totalProjects, websitesGenerated, creditsUsed });
  };

  const createProject = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch(`${API}/projects/create`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ name: projectName, description: projectDesc })
      });
      
      if (res.ok) {
        const data = await res.json();
        toast.success('Project created!');
        navigate(`/workspace/${data.id}`);
      }
    } catch (error) {
      console.error('Error creating project:', error);
      toast.error('Failed to create project');
    }
  };

  const deleteProject = async (projectId) => {
    if (!confirm('Are you sure you want to delete this project?')) return;
    
    try {
      const res = await fetch(`${API}/projects/${projectId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      
      if (res.ok) {
        toast.success('Project deleted');
        fetchProjects();
      }
    } catch (error) {
      console.error('Error deleting project:', error);
      toast.error('Failed to delete project');
    }
  };

  return (
    <div className="dashboard-v3">
      {/* Header */}
      <header className="dashboard-header-v3">
        <div className="header-left">
          <div className="logo-v3">
            <Sparkles className="w-8 h-8" />
            <span>AutoWebIQ</span>
          </div>
        </div>
        <div className="header-right">
          <Button variant="outline" onClick={() => navigate('/subscriptions')} className="upgrade-btn">
            <Crown className="w-4 h-4" />
            Upgrade
          </Button>
          <div className="credits-display-v3">
            <Zap className="w-5 h-5" />
            <span className="credits-amount">{user?.credits || 0}</span>
            <span className="credits-label">credits</span>
          </div>
          <div className="user-menu-v3">
            <span>{user?.username || 'User'}</span>
            <Button variant="ghost" size="sm" onClick={onLogout}>Logout</Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="dashboard-content-v3">
        {/* Welcome Section */}
        <div className="welcome-section-v3">
          <h1>Welcome back, {user?.username || 'there'}! 👋</h1>
          <p>Build amazing websites with AI in seconds</p>
        </div>

        {/* Stats Cards */}
        <div className="stats-grid">
          <Card className="stat-card">
            <div className="stat-icon" style={{background: 'linear-gradient(135deg, #667eea, #764ba2)'}}>
              <Globe className="w-6 h-6" />
            </div>
            <div className="stat-content">
              <div className="stat-value">{stats.totalProjects}</div>
              <div className="stat-label">Total Projects</div>
            </div>
          </Card>
          
          <Card className="stat-card">
            <div className="stat-icon" style={{background: 'linear-gradient(135deg, #f093fb, #f5576c)'}}>
              <Sparkles className="w-6 h-6" />
            </div>
            <div className="stat-content">
              <div className="stat-value">{stats.websitesGenerated}</div>
              <div className="stat-label">Websites Generated</div>
            </div>
          </Card>
          
          <Card className="stat-card">
            <div className="stat-icon" style={{background: 'linear-gradient(135deg, #4facfe, #00f2fe)'}}>
              <Zap className="w-6 h-6" />
            </div>
            <div className="stat-content">
              <div className="stat-value">{user?.credits || 0}</div>
              <div className="stat-label">Credits Available</div>
            </div>
          </Card>
          
          <Card className="stat-card">
            <div className="stat-icon" style={{background: 'linear-gradient(135deg, #43e97b, #38f9d7)'}}>
              <TrendingUp className="w-6 h-6" />
            </div>
            <div className="stat-content">
              <div className="stat-value">{stats.creditsUsed}</div>
              <div className="stat-label">Credits Used</div>
            </div>
          </Card>
        </div>

        {/* Quick Actions */}
        <div className="quick-actions-v3">
          <Button size="lg" onClick={() => setShowNewProject(true)} className="new-project-btn">
            <Plus className="w-5 h-5" />
            New Project
          </Button>
        </div>

        {/* Projects Section */}
        <div className="projects-section">
          <div className="section-header">
            <h2>Recent Projects</h2>
            <Button variant="ghost" onClick={fetchProjects}>
              <Clock className="w-4 h-4" />
              Refresh
            </Button>
          </div>

          {loading ? (
            <div className="loading-state">
              <div className="spinner"></div>
              <p>Loading projects...</p>
            </div>
          ) : projects.length === 0 ? (
            <Card className="empty-state">
              <Sparkles className="w-16 h-16 text-gray-400" />
              <h3>No projects yet</h3>
              <p>Create your first AI-powered website</p>
              <Button onClick={() => setShowNewProject(true)}>
                <Plus className="w-4 h-4" />
                Create Project
              </Button>
            </Card>
          ) : (
            <div className="projects-grid">
              {projects.map((project) => (
                <Card key={project.id} className="project-card-v3">
                  <div className="project-preview">
                    {project.generated_code ? (
                      <div className="preview-content">
                        <Globe className="w-12 h-12 text-purple-500" />
                        <div className="status-badge success">Generated</div>
                      </div>
                    ) : (
                      <div className="preview-content empty">
                        <Sparkles className="w-12 h-12 text-gray-400" />
                        <div className="status-badge pending">Pending</div>
                      </div>
                    )}
                  </div>
                  
                  <div className="project-info">
                    <h3>{project.name}</h3>
                    <p>{project.description}</p>
                    <div className="project-meta">
                      <span className="meta-item">
                        <Calendar className="w-4 h-4" />
                        {new Date(project.created_at).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                  
                  <div className="project-actions">
                    <Button variant="outline" size="sm" onClick={() => navigate(`/workspace/${project.id}`)}>
                      <Eye className="w-4 h-4" />
                      Open
                    </Button>
                    {project.generated_code && (
                      <Button variant="outline" size="sm" onClick={() => navigate(`/deployment/${project.id}`)}>
                        <Globe className="w-4 h-4" />
                        Deploy
                      </Button>
                    )}
                    <Button variant="ghost" size="sm" onClick={() => deleteProject(project.id)}>
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </Card>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* New Project Modal */}
      {showNewProject && (
        <div className="modal-overlay" onClick={() => setShowNewProject(false)}>
          <Card className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h2>Create New Project</h2>
            <form onSubmit={createProject}>
              <div className="form-group">
                <label>Project Name</label>
                <input
                  type="text"
                  value={projectName}
                  onChange={(e) => setProjectName(e.target.value)}
                  placeholder="My Awesome Website"
                  required
                />
              </div>
              <div className="form-group">
                <label>Description</label>
                <textarea
                  value={projectDesc}
                  onChange={(e) => setProjectDesc(e.target.value)}
                  placeholder="Describe your website..."
                  rows="3"
                  required
                />
              </div>
              <div className="modal-actions">
                <Button type="button" variant="ghost" onClick={() => setShowNewProject(false)}>Cancel</Button>
                <Button type="submit">Create Project</Button>
              </div>
            </form>
          </Card>
        </div>
      )}
    </div>
  );
};

export default DashboardV3;