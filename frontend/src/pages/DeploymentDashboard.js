import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Rocket, ExternalLink, Trash2, Clock, CheckCircle, Globe, RefreshCw } from 'lucide-react';
import { toast } from 'sonner';
import './DeploymentDashboard.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const DeploymentDashboard = () => {
  const navigate = useNavigate();
  const { projectId } = useParams();
  const [deployment, setDeployment] = useState(null);
  const [loading, setLoading] = useState(false);
  const [deploying, setDeploying] = useState(false);
  const [project, setProject] = useState(null);

  useEffect(() => {
    if (projectId) {
      fetchProject();
      fetchDeployment();
    }
  }, [projectId]);

  const fetchProject = async () => {
    try {
      const res = await fetch(`${API}/projects/${projectId}`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      if (res.ok) {
        const data = await res.json();
        setProject(data);
      }
    } catch (error) {
      console.error('Error fetching project:', error);
    }
  };

  const fetchDeployment = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API}/deployments/${projectId}`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      const data = await res.json();
      if (data.success && data.deployment) {
        setDeployment(data.deployment);
      }
    } catch (error) {
      console.error('Error fetching deployment:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDeploy = async () => {
    if (!project?.generated_code) {
      toast.error('No code to deploy. Generate a website first.');
      return;
    }

    setDeploying(true);
    try {
      const res = await fetch(`${API}/deployments/deploy`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ project_id: projectId })
      });

      const data = await res.json();
      if (data.success) {
        toast.success('Deployed successfully!');
        setDeployment(data.deployment);
        
        // Open preview in new tab
        setTimeout(() => {
          window.open(data.deployment.preview_url, '_blank');
        }, 1000);
      } else {
        toast.error(data.message || 'Deployment failed');
      }
    } catch (error) {
      console.error('Deploy error:', error);
      toast.error('Deployment failed');
    } finally {
      setDeploying(false);
    }
  };

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete this deployment?')) return;

    try {
      const res = await fetch(`${API}/deployments/${projectId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });

      const data = await res.json();
      if (data.success) {
        toast.success('Deployment deleted');
        setDeployment(null);
      } else {
        toast.error('Failed to delete deployment');
      }
    } catch (error) {
      console.error('Delete error:', error);
      toast.error('Failed to delete deployment');
    }
  };

  return (
    <div className="deployment-dashboard">
      <div className="deployment-header">
        <div>
          <button className="back-button" onClick={() => navigate(`/workspace/${projectId}`)}>← Back to Workspace</button>
          <h1 className="deployment-title">Deployment</h1>
          <p className="deployment-subtitle">{project?.name}</p>
        </div>
      </div>

      <div className="deployment-content">
        {loading ? (
          <Card className="deployment-loading">
            <RefreshCw className="w-8 h-8 animate-spin" />
            <p>Loading deployment status...</p>
          </Card>
        ) : deployment ? (
          <div className="deployment-active">
            <Card className="deployment-card">
              <div className="deployment-status">
                <div className="status-indicator active">
                  <CheckCircle className="w-6 h-6" />
                  <span>Live</span>
                </div>
                <div className="deployment-info">
                  <div className="info-item">
                    <Globe className="w-5 h-5" />
                    <div>
                      <label>Preview URL</label>
                      <a href={deployment.preview_url} target="_blank" rel="noopener noreferrer" className="preview-url">
                        {deployment.preview_url}
                        <ExternalLink className="w-4 h-4" />
                      </a>
                    </div>
                  </div>
                  <div className="info-item">
                    <Rocket className="w-5 h-5" />
                    <div>
                      <label>Subdomain</label>
                      <p>{deployment.subdomain}</p>
                    </div>
                  </div>
                  <div className="info-item">
                    <Clock className="w-5 h-5" />
                    <div>
                      <label>Deployed</label>
                      <p>{deployment.deployed_at ? new Date(deployment.deployed_at).toLocaleString() : 'N/A'}</p>
                    </div>
                  </div>
                </div>
              </div>

              <div className="deployment-actions">
                <Button onClick={handleDeploy} disabled={deploying} className="update-button">
                  <RefreshCw className={`w-4 h-4 ${deploying ? 'animate-spin' : ''}`} />
                  {deploying ? 'Updating...' : 'Update Deployment'}
                </Button>
                <Button variant="outline" onClick={() => window.open(deployment.preview_url, '_blank')}>
                  <ExternalLink className="w-4 h-4" />
                  Open Preview
                </Button>
                <Button variant="destructive" onClick={handleDelete}>
                  <Trash2 className="w-4 h-4" />
                  Delete
                </Button>
              </div>
            </Card>

            <Card className="deployment-preview">
              <h3>Live Preview</h3>
              <iframe src={deployment.preview_url} title="Preview" className="preview-iframe" />
            </Card>
          </div>
        ) : (
          <Card className="deployment-empty">
            <Rocket className="w-16 h-16 text-gray-400" />
            <h3>No Deployment Yet</h3>
            <p>Deploy your project to get an instant preview with a custom subdomain</p>
            <Button onClick={handleDeploy} disabled={deploying || !project?.generated_code} size="lg">
              <Rocket className="w-5 h-5" />
              {deploying ? 'Deploying...' : 'Deploy Now'}
            </Button>
            {!project?.generated_code && (
              <p className="error-text">Generate a website first before deploying</p>
            )}
          </Card>
        )}

        <Card className="deployment-info-card">
          <h3>About Instant Deployment</h3>
          <ul className="info-list">
            <li><CheckCircle className="w-5 h-5 text-green-500" /> Instant preview with custom subdomain</li>
            <li><CheckCircle className="w-5 h-5 text-green-500" /> Free SSL certificate included</li>
            <li><CheckCircle className="w-5 h-5 text-green-500" /> Cloudflare CDN for fast loading</li>
            <li><CheckCircle className="w-5 h-5 text-green-500" /> Update anytime with one click</li>
            <li><CheckCircle className="w-5 h-5 text-green-500" /> No configuration required</li>
          </ul>
        </Card>
      </div>
    </div>
  );
};

export default DeploymentDashboard;