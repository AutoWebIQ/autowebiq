import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { toast } from 'sonner';
import { Download, Eye, Code, ArrowLeft, Sparkles } from 'lucide-react';
import Prism from 'prismjs';
import 'prismjs/components/prism-markup';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ProjectView = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [project, setProject] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('preview');
  const iframeRef = useRef(null);

  const axiosConfig = {
    headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
  };

  useEffect(() => {
    fetchProject();
  }, [id]);

  useEffect(() => {
    if (activeTab === 'code' && project) {
      setTimeout(() => Prism.highlightAll(), 100);
    }
  }, [activeTab, project]);

  const fetchProject = async () => {
    try {
      const res = await axios.get(`${API}/projects/${id}`, axiosConfig);
      setProject(res.data);
    } catch (error) {
      toast.error('Failed to load project');
      navigate('/dashboard');
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
      toast.success('Downloaded successfully!');
    } catch (error) {
      toast.error('Failed to download');
    }
  };

  if (loading) {
    return <div className="loading-screen">Loading project...</div>;
  }

  if (!project) {
    return null;
  }

  return (
    <div className="project-view-container" data-testid="project-view">
      <nav className="project-nav">
        <div className="nav-content">
          <Button
            data-testid="back-btn"
            variant="ghost"
            onClick={() => navigate('/dashboard')}
          >
            <ArrowLeft className="mr-2" /> Back to Dashboard
          </Button>
          <div className="logo">
            <Sparkles className="logo-icon" />
            <span>Optra AI</span>
          </div>
          <div className="project-actions">
            <Button data-testid="download-btn" onClick={downloadProject}>
              <Download className="mr-2" /> Download
            </Button>
          </div>
        </div>
      </nav>

      <div className="project-content">
        <div className="project-header">
          <div>
            <h1 data-testid="project-title">{project.name}</h1>
            <p data-testid="project-description">{project.prompt}</p>
          </div>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="project-tabs">
          <TabsList data-testid="tabs-list">
            <TabsTrigger data-testid="preview-tab" value="preview">
              <Eye className="mr-2" size={16} /> Preview
            </TabsTrigger>
            <TabsTrigger data-testid="code-tab" value="code">
              <Code className="mr-2" size={16} /> Code
            </TabsTrigger>
          </TabsList>

          <TabsContent value="preview" className="preview-content" data-testid="preview-content">
            <Card className="preview-card">
              <iframe
                ref={iframeRef}
                data-testid="preview-iframe"
                srcDoc={project.generated_code.html}
                className="preview-iframe"
                title="Website Preview"
              />
            </Card>
          </TabsContent>

          <TabsContent value="code" className="code-content" data-testid="code-content">
            <Card className="code-card">
              <div className="code-header">
                <h3>index.html</h3>
              </div>
              <pre className="code-block">
                <code data-testid="code-display" className="language-html">
                  {project.generated_code.html}
                </code>
              </pre>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default ProjectView;
