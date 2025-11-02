// Terminal Component for AutoWebIQ
import React, { useEffect, useRef, useState } from 'react';
import { Terminal as XTerm } from 'xterm';
import { FitAddon } from 'xterm-addon-fit';
import { WebLinksAddon } from 'xterm-addon-web-links';
import 'xterm/css/xterm.css';
import { X, Maximize2, Minimize2 } from 'lucide-react';

const BACKEND_WS = process.env.REACT_APP_BACKEND_URL?.replace('http', 'ws') || 'ws://localhost:8001';

const Terminal = ({ containerId, onClose, isFullscreen, onToggleFullscreen }) => {
  const terminalRef = useRef(null);
  const xtermRef = useRef(null);
  const fitAddonRef = useRef(null);
  const wsRef = useRef(null);
  const [connected, setConnected] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!containerId) return;

    // Initialize xterm
    const term = new XTerm({
      cursorBlink: true,
      fontSize: 14,
      fontFamily: "'Fira Code', 'Courier New', monospace",
      theme: {
        background: '#1e1e1e',
        foreground: '#d4d4d4',
        cursor: '#ffffff',
        black: '#000000',
        red: '#cd3131',
        green: '#0dbc79',
        yellow: '#e5e510',
        blue: '#2472c8',
        magenta: '#bc3fbc',
        cyan: '#11a8cd',
        white: '#e5e5e5',
        brightBlack: '#666666',
        brightRed: '#f14c4c',
        brightGreen: '#23d18b',
        brightYellow: '#f5f543',
        brightBlue: '#3b8eea',
        brightMagenta: '#d670d6',
        brightCyan: '#29b8db',
        brightWhite: '#ffffff'
      },
      cols: 80,
      rows: 24
    });

    // Add addons
    const fitAddon = new FitAddon();
    term.loadAddon(fitAddon);
    term.loadAddon(new WebLinksAddon());

    // Mount terminal
    term.open(terminalRef.current);
    fitAddon.fit();

    xtermRef.current = term;
    fitAddonRef.current = fitAddon;

    // Connect WebSocket
    connectWebSocket(term, containerId);

    // Handle resize
    const handleResize = () => {
      fitAddon.fit();
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({
          type: 'resize',
          rows: term.rows,
          cols: term.cols
        }));
      }
    };

    window.addEventListener('resize', handleResize);

    // Cleanup
    return () => {
      window.removeEventListener('resize', handleResize);
      if (wsRef.current) {
        wsRef.current.close();
      }
      term.dispose();
    };
  }, [containerId]);

  // Refit when fullscreen changes
  useEffect(() => {
    if (fitAddonRef.current) {
      setTimeout(() => {
        fitAddonRef.current.fit();
      }, 100);
    }
  }, [isFullscreen]);

  const connectWebSocket = (term, containerId) => {
    const sessionId = `term_${Date.now()}`;
    const ws = new WebSocket(`${BACKEND_WS}/ws/terminal/${sessionId}`);
    
    ws.onopen = () => {
      setConnected(true);
      setError(null);
      
      // Send start message
      ws.send(JSON.stringify({
        type: 'start',
        container_id: containerId
      }));

      // Handle terminal input
      term.onData((data) => {
        if (ws.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify({
            type: 'input',
            data: data
          }));
        }
      });
    };

    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        
        if (message.type === 'output') {
          term.write(message.data);
        } else if (message.type === 'error') {
          setError(message.data);
          term.write(`\r\n\x1b[31mError: ${message.data}\x1b[0m\r\n`);
        }
      } catch (err) {
        console.error('Failed to parse WebSocket message:', err);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setError('Connection error');
      setConnected(false);
    };

    ws.onclose = () => {
      setConnected(false);
      term.write('\r\n\x1b[33mConnection closed\x1b[0m\r\n');
    };

    wsRef.current = ws;
  };

  const handleClear = () => {
    if (xtermRef.current) {
      xtermRef.current.clear();
    }
  };

  return (
    <div className="h-full flex flex-col bg-gray-900">
      {/* Toolbar */}
      <div className="flex items-center justify-between bg-gray-800 px-4 py-2 border-b border-gray-700">
        <div className="flex items-center space-x-3">
          <span className="text-white text-sm font-medium">Terminal</span>
          {connected ? (
            <span className="flex items-center space-x-1 text-green-400 text-xs">
              <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
              <span>Connected</span>
            </span>
          ) : (
            <span className="flex items-center space-x-1 text-red-400 text-xs">
              <span className="w-2 h-2 bg-red-400 rounded-full"></span>
              <span>Disconnected</span>
            </span>
          )}
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={handleClear}
            className="px-3 py-1 text-xs bg-gray-700 hover:bg-gray-600 text-white rounded"
            title="Clear terminal"
          >
            Clear
          </button>
          {onToggleFullscreen && (
            <button
              onClick={onToggleFullscreen}
              className="p-1 hover:bg-gray-700 rounded"
              title={isFullscreen ? 'Minimize' : 'Maximize'}
            >
              {isFullscreen ? (
                <Minimize2 className="w-4 h-4 text-gray-400" />
              ) : (
                <Maximize2 className="w-4 h-4 text-gray-400" />
              )}
            </button>
          )}
          {onClose && (
            <button
              onClick={onClose}
              className="p-1 hover:bg-gray-700 rounded"
              title="Close terminal"
            >
              <X className="w-4 h-4 text-gray-400" />
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

      {/* Terminal */}
      <div className="flex-1 p-2 overflow-hidden">
        <div ref={terminalRef} className="h-full" />
      </div>

      {/* Status Bar */}
      <div className="bg-gray-800 px-4 py-1 text-xs text-gray-400 border-t border-gray-700">
        Container: {containerId ? containerId.substring(0, 12) : 'None'}
      </div>
    </div>
  );
};

export default Terminal;
