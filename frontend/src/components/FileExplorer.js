// File Explorer Component for AutoWebIQ
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  ChevronRight, 
  ChevronDown, 
  File, 
  Folder, 
  FolderOpen,
  Plus,
  Trash2,
  RefreshCw 
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const FileExplorer = ({ projectId, onFileSelect, selectedFile }) => {
  const [fileTree, setFileTree] = useState(null);
  const [loading, setLoading] = useState(false);
  const [expandedFolders, setExpandedFolders] = useState(new Set());
  const [contextMenu, setContextMenu] = useState(null);

  useEffect(() => {
    if (projectId) {
      loadFileTree();
    }
  }, [projectId]);

  const loadFileTree = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        `${BACKEND_URL}/api/files/tree`,
        projectId,
        { 
          headers: { 
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      if (response.data.status === 'success') {
        setFileTree(response.data.tree);
        // Auto-expand root
        setExpandedFolders(new Set(['']));
      }
    } catch (err) {
      console.error('Failed to load file tree:', err);
    } finally {
      setLoading(false);
    }
  };

  const toggleFolder = (path) => {
    const newExpanded = new Set(expandedFolders);
    if (newExpanded.has(path)) {
      newExpanded.delete(path);
    } else {
      newExpanded.add(path);
    }
    setExpandedFolders(newExpanded);
  };

  const handleFileClick = (file) => {
    if (file.type === 'file') {
      onFileSelect(file.path);
    } else {
      toggleFolder(file.path);
    }
  };

  const handleContextMenu = (e, file) => {
    e.preventDefault();
    setContextMenu({
      x: e.clientX,
      y: e.clientY,
      file: file
    });
  };

  const closeContextMenu = () => {
    setContextMenu(null);
  };

  const handleDeleteFile = async (filePath) => {
    if (!window.confirm(`Delete ${filePath}?`)) return;

    try {
      const token = localStorage.getItem('token');
      await axios.post(
        `${BACKEND_URL}/api/files/delete`,
        { project_id: projectId, file_path: filePath },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      loadFileTree(); // Reload tree
    } catch (err) {
      console.error('Failed to delete file:', err);
      alert('Failed to delete file');
    }
    closeContextMenu();
  };

  const getFileIcon = (file) => {
    if (file.type === 'directory') {
      return expandedFolders.has(file.path) ? (
        <FolderOpen className="w-4 h-4 text-blue-400" />
      ) : (
        <Folder className="w-4 h-4 text-blue-400" />
      );
    }

    // File type icons
    const ext = file.name.split('.').pop().toLowerCase();
    const colors = {
      'js': 'text-yellow-400',
      'jsx': 'text-blue-400',
      'ts': 'text-blue-500',
      'tsx': 'text-blue-500',
      'py': 'text-green-400',
      'html': 'text-orange-400',
      'css': 'text-purple-400',
      'json': 'text-yellow-300',
      'md': 'text-gray-400'
    };

    return <File className={`w-4 h-4 ${colors[ext] || 'text-gray-400'}`} />;
  };

  const renderTreeNode = (node, depth = 0) => {
    if (!node) return null;

    const isExpanded = expandedFolders.has(node.path);
    const isSelected = selectedFile === node.path;

    return (
      <div key={node.path}>
        <div
          className={`flex items-center space-x-2 px-2 py-1 hover:bg-gray-700 cursor-pointer ${
            isSelected ? 'bg-gray-700' : ''
          }`}
          style={{ paddingLeft: `${depth * 16 + 8}px` }}
          onClick={() => handleFileClick(node)}
          onContextMenu={(e) => handleContextMenu(e, node)}
        >
          {node.type === 'directory' && (
            <span>
              {isExpanded ? (
                <ChevronDown className="w-4 h-4 text-gray-400" />
              ) : (
                <ChevronRight className="w-4 h-4 text-gray-400" />
              )}
            </span>
          )}
          
          {getFileIcon(node)}
          
          <span className="text-sm text-gray-200 truncate flex-1">
            {node.name}
          </span>

          {node.type === 'file' && node.size && (
            <span className="text-xs text-gray-500">
              {formatFileSize(node.size)}
            </span>
          )}
        </div>

        {node.type === 'directory' && isExpanded && node.children && (
          <div>
            {node.children.map(child => renderTreeNode(child, depth + 1))}
          </div>
        )}
      </div>
    );
  };

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  return (
    <div className="h-full bg-gray-800 flex flex-col" onClick={closeContextMenu}>
      {/* Header */}
      <div className="flex items-center justify-between bg-gray-900 px-3 py-2 border-b border-gray-700">
        <span className="text-white text-sm font-medium">Files</span>
        <div className="flex items-center space-x-1">
          <button
            onClick={loadFileTree}
            className="p-1 hover:bg-gray-700 rounded"
            title="Refresh"
          >
            <RefreshCw className="w-4 h-4 text-gray-400" />
          </button>
        </div>
      </div>

      {/* File Tree */}
      <div className="flex-1 overflow-y-auto">
        {loading ? (
          <div className="p-4 text-gray-400 text-sm">Loading files...</div>
        ) : fileTree ? (
          renderTreeNode(fileTree)
        ) : (
          <div className="p-4 text-gray-400 text-sm">No files</div>
        )}
      </div>

      {/* Context Menu */}
      {contextMenu && (
        <div
          className="fixed bg-gray-700 border border-gray-600 rounded shadow-lg py-1 z-50"
          style={{ left: contextMenu.x, top: contextMenu.y }}
        >
          <button
            onClick={() => handleDeleteFile(contextMenu.file.path)}
            className="w-full px-4 py-2 text-left text-sm text-red-400 hover:bg-gray-600 flex items-center space-x-2"
          >
            <Trash2 className="w-4 h-4" />
            <span>Delete</span>
          </button>
        </div>
      )}
    </div>
  );
};

export default FileExplorer;
