import React from 'react';
import { CheckCircle, Clock, Loader2, XCircle } from 'lucide-react';
import './AgentStatusPanel.css';

/**
 * Agent Status Panel - Emergent Style
 * Shows real-time agent activity during website generation
 */
const AgentStatusPanel = ({ agents = [], isGenerating = false }) => {
  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="status-icon completed" />;
      case 'working':
        return <Loader2 className="status-icon working spin" />;
      case 'pending':
        return <Clock className="status-icon pending" />;
      case 'failed':
        return <XCircle className="status-icon failed" />;
      default:
        return <Clock className="status-icon pending" />;
    }
  };

  const getStatusText = (agent) => {
    switch (agent.status) {
      case 'completed':
        return 'Complete';
      case 'working':
        return agent.progress || 'Working...';
      case 'pending':
        return 'Waiting...';
      case 'failed':
        return 'Failed';
      default:
        return 'Idle';
    }
  };

  const getAgentColor = (name) => {
    const colors = {
      'Planner': '#8b5cf6',
      'Frontend': '#3b82f6',
      'Backend': '#10b981',
      'Image': '#f59e0b',
      'Testing': '#ef4444',
      'Content': '#ec4899'
    };
    return colors[name] || '#6b7280';
  };

  // Default agents if none provided
  const defaultAgents = [
    { name: 'Planner', status: 'idle', cost: 12, progress: null },
    { name: 'Frontend', status: 'idle', cost: 16, progress: null },
    { name: 'Backend', status: 'idle', cost: 12, progress: null },
    { name: 'Image', status: 'idle', cost: 15, progress: null },
    { name: 'Testing', status: 'idle', cost: 10, progress: null }
  ];

  const displayAgents = agents.length > 0 ? agents : defaultAgents;

  return (
    <div className="agent-status-panel">
      <div className="panel-header">
        <h3 className="panel-title">AI Agents</h3>
        {isGenerating && (
          <div className="generating-badge">
            <Loader2 className="w-3 h-3 spin" />
            <span>Generating...</span>
          </div>
        )}
      </div>

      <div className="agents-list">
        {displayAgents.map((agent, index) => (
          <div 
            key={index} 
            className={`agent-item ${agent.status}`}
            style={{ '--agent-color': getAgentColor(agent.name) }}
          >
            <div className="agent-avatar" style={{ background: getAgentColor(agent.name) }}>
              {agent.name.charAt(0)}
            </div>
            
            <div className="agent-info">
              <div className="agent-header">
                <span className="agent-name">{agent.name}</span>
                <span className="agent-cost">{agent.cost} credits</span>
              </div>
              
              <div className="agent-status-row">
                {getStatusIcon(agent.status)}
                <span className="agent-status-text">{getStatusText(agent)}</span>
              </div>
              
              {agent.status === 'working' && (
                <div className="agent-progress-bar">
                  <div 
                    className="progress-fill" 
                    style={{ 
                      width: agent.progressPercent ? `${agent.progressPercent}%` : '50%',
                      background: getAgentColor(agent.name)
                    }}
                  />
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {isGenerating && (
        <div className="total-cost">
          <span>Estimated Cost:</span>
          <span className="cost-amount">
            {displayAgents.reduce((sum, agent) => sum + (agent.status !== 'idle' ? agent.cost : 0), 0)} credits
          </span>
        </div>
      )}
    </div>
  );
};

export default AgentStatusPanel;