// Settings Panel Component
import React, { useState } from 'react';
import { X, Palette, Type, Layout, Bell, Shield } from 'lucide-react';

const SettingsPanel = ({ isOpen, onClose }) => {
  const [settings, setSettings] = useState({
    theme: 'dark',
    fontSize: 14,
    fontFamily: 'Fira Code',
    tabSize: 2,
    autoSave: true,
    minimap: true,
    lineNumbers: true,
    wordWrap: true,
    notifications: true
  });

  const handleChange = (key, value) => {
    const newSettings = { ...settings, [key]: value };
    setSettings(newSettings);
    localStorage.setItem('editor-settings', JSON.stringify(newSettings));
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-gray-800 rounded-lg shadow-2xl w-[700px] max-h-[80vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-700">
          <h2 className="text-white text-lg font-semibold">Settings</h2>
          <button onClick={onClose} className="p-1 hover:bg-gray-700 rounded">
            <X className="w-5 h-5 text-gray-400" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {/* Appearance */}
          <div>
            <div className="flex items-center space-x-2 mb-4">
              <Palette className="w-5 h-5 text-blue-400" />
              <h3 className="text-white font-semibold">Appearance</h3>
            </div>
            <div className="space-y-3 pl-7">
              <div>
                <label className="text-gray-400 text-sm block mb-1">Theme</label>
                <select
                  value={settings.theme}
                  onChange={(e) => handleChange('theme', e.target.value)}
                  className="w-full bg-gray-700 text-white rounded px-3 py-2"
                >
                  <option value="dark">Dark</option>
                  <option value="light">Light</option>
                  <option value="high-contrast">High Contrast</option>
                </select>
              </div>
            </div>
          </div>

          {/* Editor */}
          <div>
            <div className="flex items-center space-x-2 mb-4">
              <Type className="w-5 h-5 text-green-400" />
              <h3 className="text-white font-semibold">Editor</h3>
            </div>
            <div className="space-y-3 pl-7">
              <div>
                <label className="text-gray-400 text-sm block mb-1">Font Size</label>
                <input
                  type="number"
                  value={settings.fontSize}
                  onChange={(e) => handleChange('fontSize', parseInt(e.target.value))}
                  className="w-full bg-gray-700 text-white rounded px-3 py-2"
                  min="10"
                  max="24"
                />
              </div>
              <div>
                <label className="text-gray-400 text-sm block mb-1">Font Family</label>
                <select
                  value={settings.fontFamily}
                  onChange={(e) => handleChange('fontFamily', e.target.value)}
                  className="w-full bg-gray-700 text-white rounded px-3 py-2"
                >
                  <option value="Fira Code">Fira Code</option>
                  <option value="Consolas">Consolas</option>
                  <option value="Monaco">Monaco</option>
                  <option value="Courier New">Courier New</option>
                </select>
              </div>
              <div>
                <label className="text-gray-400 text-sm block mb-1">Tab Size</label>
                <input
                  type="number"
                  value={settings.tabSize}
                  onChange={(e) => handleChange('tabSize', parseInt(e.target.value))}
                  className="w-full bg-gray-700 text-white rounded px-3 py-2"
                  min="2"
                  max="8"
                />
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-400 text-sm">Auto Save</span>
                <input
                  type="checkbox"
                  checked={settings.autoSave}
                  onChange={(e) => handleChange('autoSave', e.target.checked)}
                  className="w-4 h-4"
                />
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-400 text-sm">Show Minimap</span>
                <input
                  type="checkbox"
                  checked={settings.minimap}
                  onChange={(e) => handleChange('minimap', e.target.checked)}
                  className="w-4 h-4"
                />
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-400 text-sm">Line Numbers</span>
                <input
                  type="checkbox"
                  checked={settings.lineNumbers}
                  onChange={(e) => handleChange('lineNumbers', e.target.checked)}
                  className="w-4 h-4"
                />
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-400 text-sm">Word Wrap</span>
                <input
                  type="checkbox"
                  checked={settings.wordWrap}
                  onChange={(e) => handleChange('wordWrap', e.target.checked)}
                  className="w-4 h-4"
                />
              </div>
            </div>
          </div>

          {/* Notifications */}
          <div>
            <div className="flex items-center space-x-2 mb-4">
              <Bell className="w-5 h-5 text-yellow-400" />
              <h3 className="text-white font-semibold">Notifications</h3>
            </div>
            <div className="space-y-3 pl-7">
              <div className="flex items-center justify-between">
                <span className="text-gray-400 text-sm">Enable Notifications</span>
                <input
                  type="checkbox"
                  checked={settings.notifications}
                  onChange={(e) => handleChange('notifications', e.target.checked)}
                  className="w-4 h-4"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-gray-700 flex justify-end space-x-2">
          <button
            onClick={() => {
              localStorage.removeItem('editor-settings');
              window.location.reload();
            }}
            className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded"
          >
            Reset to Defaults
          </button>
          <button
            onClick={onClose}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded"
          >
            Save & Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default SettingsPanel;