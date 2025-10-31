// WebSocket Hook for Real-time Build Updates
// Connects to backend WebSocket and handles real-time messages

import { useEffect, useRef, useCallback, useState } from 'react';

const WS_URL = process.env.REACT_APP_BACKEND_URL?.replace('http', 'ws') || 'ws://localhost:8001';

export const useBuildWebSocket = (projectId, token, onMessage) => {
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const [connectionStatus, setConnectionStatus] = useState('disconnected'); // disconnected, connecting, connected, error
  const [lastMessage, setLastMessage] = useState(null);

  const connect = useCallback(() => {
    if (!projectId || !token) {
      console.log('WebSocket: Missing projectId or token');
      return;
    }

    // Clean up existing connection
    if (wsRef.current) {
      wsRef.current.close();
    }

    setConnectionStatus('connecting');
    
    const wsUrl = `${WS_URL}/api/v2/ws/build/${projectId}?token=${token}`;
    console.log('WebSocket: Connecting to', wsUrl);

    try {
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('WebSocket: Connected');
        setConnectionStatus('connected');
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log('WebSocket: Message received', data);
          setLastMessage(data);

          // Call the callback with the message
          if (onMessage) {
            onMessage(data);
          }
        } catch (error) {
          console.error('WebSocket: Error parsing message', error);
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket: Error', error);
        setConnectionStatus('error');
      };

      ws.onclose = (event) => {
        console.log('WebSocket: Closed', event.code, event.reason);
        setConnectionStatus('disconnected');
        wsRef.current = null;

        // Attempt to reconnect after 3 seconds if not a normal closure
        if (event.code !== 1000) {
          console.log('WebSocket: Will attempt to reconnect in 3s...');
          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, 3000);
        }
      };
    } catch (error) {
      console.error('WebSocket: Connection error', error);
      setConnectionStatus('error');
    }
  }, [projectId, token, onMessage]);

  const disconnect = useCallback(() => {
    console.log('WebSocket: Manual disconnect');
    
    // Clear reconnect timeout
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    // Close WebSocket
    if (wsRef.current) {
      wsRef.current.close(1000, 'Manual disconnect');
      wsRef.current = null;
    }

    setConnectionStatus('disconnected');
  }, []);

  const sendMessage = useCallback((message) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(typeof message === 'string' ? message : JSON.stringify(message));
      return true;
    }
    console.warn('WebSocket: Cannot send message, not connected');
    return false;
  }, []);

  const sendPing = useCallback(() => {
    return sendMessage('ping');
  }, [sendMessage]);

  // Connect on mount
  useEffect(() => {
    connect();

    // Cleanup on unmount
    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  // Ping every 30 seconds to keep connection alive
  useEffect(() => {
    if (connectionStatus === 'connected') {
      const pingInterval = setInterval(() => {
        sendPing();
      }, 30000);

      return () => clearInterval(pingInterval);
    }
  }, [connectionStatus, sendPing]);

  return {
    connectionStatus,
    lastMessage,
    sendMessage,
    disconnect,
    reconnect: connect
  };
};

export default useBuildWebSocket;
