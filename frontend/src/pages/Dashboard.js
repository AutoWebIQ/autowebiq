import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './Dashboard.css';

const Dashboard = ({ user, onLogout }) => {
  const navigate = useNavigate();
  const [projects, setProjects] = useState([]);
  const [credits, setCredits] = useState(user.credits);
  const [loading, setLoading] = useState(true);
  const [showNewProject, setShowNewProject] = useState(false);
  const [projectName, setProjectName] = useState('');
  const [projectDesc, setProjectDesc] = useState('');

  useEffect(() => {
    fetchProjects();
    fetchCredits();
  }, []);

  const fetchProjects = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/projects`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setProjects(data.projects || []);
      }
    } catch (error) {
      console.error('Error fetching projects:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchCredits = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/credits/balance`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setCredits(data.credits);
      }
    } catch (error) {
      console.error('Error fetching credits:', error);
    }
  };

  const createProject = async (e) => {
    e.preventDefault();
    
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/projects`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          name: projectName,
          description: projectDesc
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        navigate(`/workspace/${data.project_id}`);
      }
    } catch (error) {
      console.error('Error creating project:', error);
    }
  };

  return (
    <div className="dashboard">
      {/* Header */}
      <header className="dashboard-header">
        <div className="header-left">
          <span className="logo">⚡ AutoWebIQ</span>
        </div>
        <div className="header-right">
          <button className="btn btn-outline" onClick={() => navigate('/subscriptions')}>
            👑 Upgrade
          </button>
          <div className="credits-badge">
            <span className="credits-icon">💎</span>
            <span className="credits-amount">{credits}</span>
            <span className="credits-label">credits</span>
          </div>
          <div className="user-menu">
            <span>{user.name}</span>
            <button className="btn btn-secondary" onClick={onLogout}>Logout</button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="dashboard-content">
        <div className="welcome-section">
          <h1>Welcome back, {user.name}! 👋</h1>
          <p>Build amazing websites with AI in seconds</p>
        </div>

        {/* Quick Actions */}
        <div className="quick-actions">
          <button className="action-card primary" onClick={() => setShowNewProject(true)}>
            <div className="action-icon">✨</div>
            <div className="action-content">
              <h3>New Project</h3>
              <p>Start building with AI</p>
            </div>
          </button>
          
          <div className="action-card">
            <div className="action-icon">📊</div>
            <div className="action-content">
              <h3>Analytics</h3>
              <p>View your stats</p>
            </div>
          </div>
          
          <div className="action-card">
            <div className="action-icon">🎨</div>
            <div className="action-content">
              <h3>Templates</h3>
              <p>Browse templates</p>
            </div>
          </div>
        </div>

        {/* Projects Grid */}
        <div className="projects-section">
          <h2>Your Projects</h2>
          
          {loading ? (
            <div className="loading">Loading projects...</div>
          ) : projects.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">🚀</div>
              <h3>No projects yet</h3>
              <p>Create your first AI-powered website</p>
              <button className="btn btn-primary" onClick={() => setShowNewProject(true)}>
                Create Project
              </button>
            </div>
          ) : (
            <div className="projects-grid">
              {projects.map(project => (
                <div 
                  key={project.id} 
                  className="project-card"
                  onClick={() => navigate(`/workspace/${project.id}`)}
                >
                  <div className="project-header">
                    <h3>{project.name}</h3>
                    <span className={`status-badge ${project.status}`}>
                      {project.status}
                    </span>
                  </div>
                  <p className="project-desc">{project.description}</p>
                  <div className="project-footer">
                    <span className="project-date">
                      {new Date(project.created_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* New Project Modal */}
      {showNewProject && (
        <div className="modal-overlay" onClick={() => setShowNewProject(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <button className="modal-close" onClick={() => setShowNewProject(false)}>×</button>
            
            <h2 className="modal-title">Create New Project</h2>
            <p className="modal-subtitle">Tell us what you want to build</p>

            <form onSubmit={createProject}>
              <input
                type="text"
                className="input"
                placeholder="Project Name (e.g., My Portfolio)"
                value={projectName}
                onChange={(e) => setProjectName(e.target.value)}
                required
              />
              <textarea
                className="input mt-2"
                placeholder="Description (e.g., Create a modern portfolio website with dark theme)"
                value={projectDesc}
                onChange={(e) => setProjectDesc(e.target.value)}
                rows="4"
                required
              />

              <button
                type="submit"
                className="btn btn-primary mt-3"
                style={{ width: '100%' }}
              >
                Create & Start Building →
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
