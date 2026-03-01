import React, { useState, useEffect } from 'react';
import ChatInterface from './components/ChatInterface';
import MemoryPanel from './components/MemoryPanel';
import { healthAPI } from './services/api';
import './App.css';

function App() {
  const [userId, setUserId] = useState('user_' + Math.random().toString(36).substr(2, 9));
  const [activeTab, setActiveTab] = useState('chat');
  const [systemHealth, setSystemHealth] = useState(null);
  const [showUserInput, setShowUserInput] = useState(false);
  const [tempUserId, setTempUserId] = useState(userId);

  useEffect(() => {
    checkSystemHealth();
    const interval = setInterval(checkSystemHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  const checkSystemHealth = async () => {
    try {
      const health = await healthAPI.checkHealth();
      setSystemHealth(health);
    } catch (error) {
      console.error('Error checking system health:', error);
      setSystemHealth({ status: 'error', components: {} });
    }
  };

  const handleUserIdChange = () => {
    setUserId(tempUserId);
    setShowUserInput(false);
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <div className="logo-section">
            <h1>🧠 AI Agent Memory System</h1>
            <p className="subtitle">Persistent Memory for AI Assistants</p>
          </div>
          
          <div className="header-controls">
            <div className="user-section">
              {showUserInput ? (
                <div className="user-input-form">
                  <input
                    type="text"
                    value={tempUserId}
                    onChange={(e) => setTempUserId(e.target.value)}
                    placeholder="Enter user ID"
                    className="user-input"
                  />
                  <button onClick={handleUserIdChange} className="btn-confirm">
                    Set
                  </button>
                  <button
                    onClick={() => setShowUserInput(false)}
                    className="btn-cancel"
                  >
                    Cancel
                  </button>
                </div>
              ) : (
                <div className="user-display">
                  <span className="user-label">User:</span>
                  <span className="user-id">{userId}</span>
                  <button
                    onClick={() => setShowUserInput(true)}
                    className="btn-change"
                  >
                    Change
                  </button>
                </div>
              )}
            </div>

            {systemHealth && (
              <div className={`health-status ${systemHealth.status}`}>
                <span className="status-dot"></span>
                <span className="status-text">{systemHealth.status}</span>
              </div>
            )}
          </div>
        </div>

        <nav className="tab-navigation">
          <button
            className={`tab-btn ${activeTab === 'chat' ? 'active' : ''}`}
            onClick={() => setActiveTab('chat')}
          >
            💬 Chat
          </button>
          <button
            className={`tab-btn ${activeTab === 'memories' ? 'active' : ''}`}
            onClick={() => setActiveTab('memories')}
          >
            📚 Memories
          </button>
        </nav>
      </header>

      <main className="app-main">
        {activeTab === 'chat' && <ChatInterface userId={userId} />}
        {activeTab === 'memories' && <MemoryPanel userId={userId} />}
      </main>

      <footer className="app-footer">
        <p>AI Agent Memory System v1.0.0 | Built with FastAPI & React</p>
      </footer>
    </div>
  );
}

export default App;
