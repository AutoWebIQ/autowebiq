// Monaco Code Editor Component for AutoWebIQ
import React, { useState, useEffect, useRef } from 'react';
import Editor from '@monaco-editor/react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const CodeEditor = ({ projectId, filePath, initialContent, onSave, readOnly = false }) => {
  const [content, setContent] = useState(initialContent || '');
  const [language, setLanguage] = useState('javascript');
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const editorRef = useRef(null);
  const monacoRef = useRef(null);

  // Detect language from file extension
  useEffect(() => {
    if (filePath) {
      const ext = filePath.split('.').pop().toLowerCase();
      const langMap = {
        'js': 'javascript',
        'jsx': 'javascript',
        'ts': 'typescript',
        'tsx': 'typescript',
        'py': 'python',
        'html': 'html',
        'css': 'css',
        'scss': 'scss',
        'json': 'json',
        'md': 'markdown',
        'yaml': 'yaml',
        'yml': 'yaml',
        'sql': 'sql',
        'sh': 'shell'
      };
      setLanguage(langMap[ext] || 'plaintext');
    }
  }, [filePath]);

  // Load file content
  useEffect(() => {
    if (projectId && filePath && !initialContent) {
      loadFileContent();
    }
  }, [projectId, filePath]);

  const loadFileContent = async () => {
    setLoading(true);
    setError(null);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        `${BACKEND_URL}/api/files/read`,
        { project_id: projectId, file_path: filePath },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      if (response.data.status === 'success') {
        setContent(response.data.content);
      } else {
        setError(response.data.message);
      }
    } catch (err) {
      setError('Failed to load file: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleEditorDidMount = (editor, monaco) => {
    editorRef.current = editor;
    monacoRef.current = monaco;

    // Add keyboard shortcuts
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS, () => {
      handleSave();
    });

    // Configure editor options
    editor.updateOptions({
      fontSize: 14,
      lineHeight: 21,
      fontFamily: "'Fira Code', 'Courier New', monospace",
      fontLigatures: true,
      minimap: { enabled: true },
      scrollBeyondLastLine: false,
      wordWrap: 'on',
      automaticLayout: true,
      formatOnPaste: true,
      formatOnType: true,
      suggestOnTriggerCharacters: true,
      quickSuggestions: true,
      tabSize: 2
    });
  };

  const handleEditorChange = (value) => {
    setContent(value);
  };

  const handleSave = async () => {
    if (!projectId || !filePath || readOnly) return;

    setSaving(true);
    setError(null);

    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        `${BACKEND_URL}/api/files/write`,
        {
          project_id: projectId,
          file_path: filePath,
          content: content
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      if (response.data.status === 'success') {
        if (onSave) onSave(content);
        
        // Show success indicator
        const model = editorRef.current?.getModel();
        if (model) {
          monacoRef.current?.editor.setModelMarkers(model, 'save', []);
        }
      } else {
        setError(response.data.message);
      }
    } catch (err) {
      setError('Failed to save file: ' + err.message);
    } finally {
      setSaving(false);
    }
  };

  const formatCode = () => {
    if (editorRef.current) {
      editorRef.current.getAction('editor.action.formatDocument').run();
    }
  };

  const findInFile = () => {
    if (editorRef.current) {
      editorRef.current.getAction('actions.find').run();
    }
  };

  const replaceInFile = () => {
    if (editorRef.current) {
      editorRef.current.getAction('editor.action.startFindReplaceAction').run();
    }
  };

  return (
    <div className="h-full flex flex-col bg-gray-900">
      {/* Toolbar */}
      <div className="flex items-center justify-between bg-gray-800 px-4 py-2 border-b border-gray-700">
        <div className="flex items-center space-x-2">
          <span className="text-white text-sm font-medium truncate max-w-xs">
            {filePath || 'Untitled'}
          </span>
          {saving && (
            <span className="text-blue-400 text-xs">Saving...</span>
          )}
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={findInFile}
            className="px-3 py-1 text-xs bg-gray-700 hover:bg-gray-600 text-white rounded"
            title="Find (Ctrl+F)"
          >
            Find
          </button>
          <button
            onClick={replaceInFile}
            className="px-3 py-1 text-xs bg-gray-700 hover:bg-gray-600 text-white rounded"
            title="Replace (Ctrl+H)"
          >
            Replace
          </button>
          <button
            onClick={formatCode}
            className="px-3 py-1 text-xs bg-gray-700 hover:bg-gray-600 text-white rounded"
            title="Format Code"
          >
            Format
          </button>
          {!readOnly && (
            <button
              onClick={handleSave}
              disabled={saving}
              className="px-3 py-1 text-xs bg-blue-600 hover:bg-blue-700 text-white rounded disabled:opacity-50"
              title="Save (Ctrl+S)"
            >
              {saving ? 'Saving...' : 'Save'}
            </button>
          )}
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-900 text-red-100 px-4 py-2 text-sm">
          {error}
        </div>
      )}

      {/* Editor */}
      <div className="flex-1">
        {loading ? (
          <div className="h-full flex items-center justify-center bg-gray-900">
            <div className="text-white">Loading file...</div>
          </div>
        ) : (
          <Editor
            height="100%"
            language={language}
            value={content}
            onChange={handleEditorChange}
            onMount={handleEditorDidMount}
            theme="vs-dark"
            options={{
              readOnly: readOnly,
              minimap: { enabled: true },
              fontSize: 14,
              lineNumbers: 'on',
              roundedSelection: false,
              scrollBeyondLastLine: false,
              automaticLayout: true
            }}
          />
        )}
      </div>

      {/* Status Bar */}
      <div className="bg-gray-800 px-4 py-1 text-xs text-gray-400 flex justify-between border-t border-gray-700">
        <div>Language: {language}</div>
        <div>
          Lines: {content.split('\n').length} | 
          Characters: {content.length}
        </div>
      </div>
    </div>
  );
};

export default CodeEditor;
