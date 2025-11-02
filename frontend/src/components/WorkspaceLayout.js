// Workspace Layout Component - Brings everything together
import React, { useState, useEffect } from 'react';
import SplitPane from 'react-split-pane';
import CodeEditor from './CodeEditor';
import FileExplorer from './FileExplorer';
import Terminal from './Terminal';
import LivePreview from './LivePreview';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Play, Square, GitBranch, MessageSquare } from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const WorkspaceLayout = ({ projectId, projectName }) => {
  const [openFiles, setOpenFiles] = useState([]);
  const [activeFile, setActiveFile] = useState(null);
  const [workspaceInfo, setWorkspaceInfo] = useState(null);
  const [terminalVisible, setTerminalVisible] = useState(false);
  const [previewVisible, setPreviewVisible] = useState(true);
  const [chatVisible, setChatVisible] = useState(false);
  const [workspaceStatus, setWorkspaceStatus] = useState('stopped');

  useEffect(() => {
    loadWorkspaceInfo();
  }, [projectId]);

  const loadWorkspaceInfo = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `${BACKEND_URL}/api/workspaces/${projectId}/status`,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      if (response.data.status === 'success') {
        setWorkspaceInfo(response.data);
        setWorkspaceStatus(response.data.container_status);
      }
    } catch (err) {
      console.error('Failed to load workspace info:', err);
    }
  };

  const handleFileSelect = (filePath) => {
    // Add to open files if not already open
    if (!openFiles.find(f => f.path === filePath)) {
      setOpenFiles([...openFiles, { path: filePath, modified: false }]);
    }
    setActiveFile(filePath);
  };

  const handleCloseFile = (filePath) => {
    setOpenFiles(openFiles.filter(f => f.path !== filePath));
    if (activeFile === filePath) {
      setActiveFile(openFiles[0]?.path || null);
    }
  };

  const handleStartWorkspace = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        `${BACKEND_URL}/api/workspaces/create`,
        { project_id: projectId },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      if (response.data.status === 'success') {
        setWorkspaceInfo(response.data);
        setWorkspaceStatus('running');
        setPreviewVisible(true);
        alert('Workspace started successfully!');
      }
    } catch (err) {
      console.error('Failed to start workspace:', err);
      alert('Failed to start workspace: ' + err.message);
    }
  };

  const handleStopWorkspace = async () => {
    try {
      const token = localStorage.getItem('token');
      await axios.post(
        `${BACKEND_URL}/api/workspaces/${projectId}/stop`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setWorkspaceStatus('stopped');
    } catch (err) {
      console.error('Failed to stop workspace:', err);
    }
  };

  return (
    <div className="h-screen flex flex-col bg-gray-900">
      {/* Top Bar */}
      <div className="bg-gray-800 border-b border-gray-700 px-4 py-2 flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <h1 className="text-white font-semibold">{projectName}</h1>
          <div className="flex items-center space-x-2">
            {workspaceStatus === 'running' ? (
              <button
                onClick={handleStopWorkspace}
                className="flex items-center space-x-1 px-3 py-1 bg-red-600 hover:bg-red-700 text-white text-sm rounded"
              >
                <Square className="w-4 h-4" />
                <span>Stop</span>
              </button>
            ) : (
              <button
                onClick={handleStartWorkspace}
                className="flex items-center space-x-1 px-3 py-1 bg-green-600 hover:bg-green-700 text-white text-sm rounded"
              >
                <Play className="w-4 h-4" />
                <span>Start Workspace</span>
              </button>
            )}
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={() => setTerminalVisible(!terminalVisible)}
            className="px-3 py-1 bg-gray-700 hover:bg-gray-600 text-white text-sm rounded"
          >
            Terminal
          </button>
          <button
            onClick={() => setChatVisible(!chatVisible)}
            className="flex items-center space-x-1 px-3 py-1 bg-gray-700 hover:bg-gray-600 text-white text-sm rounded"
          >
            <MessageSquare className="w-4 h-4" />
            <span>Chat</span>
          </button>
          <button
            className="flex items-center space-x-1 px-3 py-1 bg-gray-700 hover:bg-gray-600 text-white text-sm rounded"
          >
            <GitBranch className="w-4 h-4" />
            <span>Git</span>
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-hidden">
        <SplitPane split="vertical" minSize={200} defaultSize={250}>
          {/* Left Sidebar - File Explorer */}
          <FileExplorer
            projectId={projectId}
            onFileSelect={handleFileSelect}
            selectedFile={activeFile}
          />

          {/* Center & Right - Editor and Preview */}
          <SplitPane split="vertical" minSize={400} defaultSize="50%">
            {/* Center - Code Editor */}
            <div className="h-full flex flex-col bg-gray-900">
              {/* File Tabs */}
              {openFiles.length > 0 && (
                <div className="flex bg-gray-800 border-b border-gray-700 overflow-x-auto">
                  {openFiles.map(file => (
                    <div
                      key={file.path}
                      className={`flex items-center space-x-2 px-4 py-2 border-r border-gray-700 cursor-pointer ${
                        activeFile === file.path ? 'bg-gray-700' : 'hover:bg-gray-700'
                      }`}
                      onClick={() => setActiveFile(file.path)}
                    >
                      <span className="text-white text-sm">
                        {file.path.split('/').pop()}
                      </span>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleCloseFile(file.path);
                        }}
                        className="text-gray-400 hover:text-white"
                      >
                        ×
                      </button>
                    </div>
                  ))}
                </div>
              )}

              {/* Editor */}
              <div className="flex-1">
                {activeFile ? (
                  <CodeEditor
                    projectId={projectId}
                    filePath={activeFile}
                    onSave={() => {
                      // Handle save
                    }}
                  />
                ) : (
                  <div className="h-full flex items-center justify-center text-gray-400">
                    Select a file to edit
                  </div>
                )}
              </div>
            </div>

            {/* Right - Live Preview or Chat */}
            <div className="h-full">
              {previewVisible && workspaceInfo?.preview_url ? (
                <LivePreview
                  previewUrl={workspaceInfo.preview_url}
                  projectId={projectId}
                />
              ) : (
                <div className="h-full flex items-center justify-center bg-gray-900 text-gray-400">
                  <div className="text-center">
                    <p>Start workspace to see live preview</p>
                    <button
                      onClick={handleStartWorkspace}
                      className="mt-4 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded"
                    >
                      Start Workspace
                    </button>
                  </div>
                </div>
              )}
            </div>
          </SplitPane>
        </SplitPane>
      </div>

      {/* Bottom Panel - Terminal */}
      {terminalVisible && (
        <div style={{ height: '300px' }} className="border-t border-gray-700">
          <Terminal
            containerId={workspaceInfo?.container_id}
            onClose={() => setTerminalVisible(false)}
          />
        </div>
      )}
    </div>
  );
};

export default WorkspaceLayout;