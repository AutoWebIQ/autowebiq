// Live Preview Component for AutoWebIQ
import React, { useState, useEffect } from 'react';
import { RefreshCw, ExternalLink, Loader } from 'lucide-react';

const LivePreview = ({ previewUrl, projectId }) => {
  const [url, setUrl] = useState(previewUrl);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setUrl(previewUrl);
    setLoading(true);
  }, [previewUrl]);

  const handleLoad = () => {
    setLoading(false);
    setError(null);
  };

  const handleError = () => {
    setLoading(false);
    setError('Failed to load preview');
  };

  const handleRefresh = () => {
    setLoading(true);
    setUrl(previewUrl + '?t=' + Date.now());
  };

  const handleOpenNew = () => {
    window.open(previewUrl, '_blank');
  };

  return (
    <div className="h-full flex flex-col bg-gray-900">
      {/* Toolbar */}
      <div className="flex items-center justify-between bg-gray-800 px-4 py-2 border-b border-gray-700">
        <div className="flex items-center space-x-3">
          <span className="text-white text-sm font-medium">Live Preview</span>
          {loading && (
            <Loader className="w-4 h-4 text-blue-400 animate-spin" />
          )}
        </div>

        <div className="flex items-center space-x-2">
          <input
            type="text"
            value={url}
            readOnly
            className="px-3 py-1 bg-gray-700 text-white text-xs rounded border border-gray-600 w-64"
          />
          <button
            onClick={handleRefresh}
            className="p-1 hover:bg-gray-700 rounded"
            title="Refresh preview"
          >
            <RefreshCw className="w-4 h-4 text-gray-400" />
          </button>
          <button
            onClick={handleOpenNew}
            className="p-1 hover:bg-gray-700 rounded"
            title="Open in new tab"
          >
            <ExternalLink className="w-4 h-4 text-gray-400" />
          </button>
        </div>
      </div>

      {/* Preview Area */}
      <div className="flex-1 bg-white relative">
        {error ? (
          <div className="h-full flex items-center justify-center text-red-500">
            {error}
          </div>
        ) : (
          <iframe
            src={url}
            className="w-full h-full border-0"
            title="Live Preview"
            onLoad={handleLoad}
            onError={handleError}
            sandbox="allow-scripts allow-same-origin allow-forms allow-popups"
          />
        )}
        {loading && (
          <div className="absolute inset-0 flex items-center justify-center bg-gray-900 bg-opacity-50">
            <div className="text-white">Loading preview...</div>
          </div>
        )}
      </div>
    </div>
  );
};

export default LivePreview;