// Command Palette Component (Ctrl+P / Cmd+P)
import React, { useState, useEffect, useRef } from 'react';
import { Search, File, GitBranch, Terminal, Settings, Zap } from 'lucide-react';

const CommandPalette = ({ isOpen, onClose, onCommand, files = [] }) => {
  const [query, setQuery] = useState('');
  const [selected, setSelected] = useState(0);
  const inputRef = useRef(null);

  const commands = [
    { id: 'open-file', label: 'Open File...', icon: File, category: 'Files' },
    { id: 'open-terminal', label: 'Open Terminal', icon: Terminal, category: 'View' },
    { id: 'open-git', label: 'Open Git Panel', icon: GitBranch, category: 'View' },
    { id: 'open-settings', label: 'Open Settings', icon: Settings, category: 'View' },
    { id: 'format-code', label: 'Format Code', icon: Zap, category: 'Edit' },
    { id: 'save-all', label: 'Save All Files', icon: File, category: 'File' },
  ];

  // Add files to commands
  const allCommands = [
    ...commands,
    ...files.map(file => ({
      id: `file:${file}`,
      label: file,
      icon: File,
      category: 'Files'
    }))
  ];

  const filtered = allCommands.filter(cmd =>
    cmd.label.toLowerCase().includes(query.toLowerCase())
  );

  useEffect(() => {
    if (isOpen) {
      inputRef.current?.focus();
      setQuery('');
      setSelected(0);
    }
  }, [isOpen]);

  useEffect(() => {
    const handleKeyDown = (e) => {
      if (!isOpen) return;

      if (e.key === 'Escape') {
        onClose();
      } else if (e.key === 'ArrowDown') {
        e.preventDefault();
        setSelected(prev => Math.min(prev + 1, filtered.length - 1));
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        setSelected(prev => Math.max(prev - 1, 0));
      } else if (e.key === 'Enter') {
        e.preventDefault();
        if (filtered[selected]) {
          handleSelect(filtered[selected]);
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, selected, filtered]);

  const handleSelect = (command) => {
    onCommand(command);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-start justify-center pt-20 z-50">
      <div className="bg-gray-800 rounded-lg shadow-2xl w-[600px] overflow-hidden">
        {/* Search Input */}
        <div className="p-4 border-b border-gray-700">
          <div className="flex items-center space-x-3">
            <Search className="w-5 h-5 text-gray-400" />
            <input
              ref={inputRef}
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Type a command or search..."
              className="flex-1 bg-transparent text-white outline-none placeholder-gray-500"
            />
          </div>
        </div>

        {/* Results */}
        <div className="max-h-[400px] overflow-y-auto">
          {filtered.length === 0 ? (
            <div className="p-8 text-center text-gray-400">
              No results found
            </div>
          ) : (
            filtered.map((cmd, index) => {
              const Icon = cmd.icon;
              return (
                <div
                  key={cmd.id}
                  className={`flex items-center space-x-3 px-4 py-3 cursor-pointer ${
                    index === selected ? 'bg-blue-600' : 'hover:bg-gray-700'
                  }`}
                  onClick={() => handleSelect(cmd)}
                >
                  <Icon className="w-4 h-4 text-gray-400" />
                  <div className="flex-1">
                    <div className="text-white text-sm">{cmd.label}</div>
                    <div className="text-gray-400 text-xs">{cmd.category}</div>
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Footer */}
        <div className="px-4 py-2 border-t border-gray-700 flex items-center justify-between text-xs text-gray-400">
          <div>↑↓ Navigate • ↵ Select • ESC Close</div>
        </div>
      </div>
    </div>
  );
};

export default CommandPalette;