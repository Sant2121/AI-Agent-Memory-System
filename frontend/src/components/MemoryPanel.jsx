import React, { useState, useEffect } from 'react';
import { memoriesAPI } from '../services/api';
import { FiTrash2, FiEdit2, FiPlus } from 'react-icons/fi';
import '../styles/MemoryPanel.css';

const MemoryPanel = ({ userId }) => {
  const [memories, setMemories] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [stats, setStats] = useState(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newMemory, setNewMemory] = useState({
    memory_text: '',
    category: 'general',
    importance_score: 0.5,
    tags: [],
  });

  useEffect(() => {
    fetchMemories();
    fetchStats();
  }, [userId, selectedCategory]);

  const fetchMemories = async () => {
    setLoading(true);
    try {
      const data = await memoriesAPI.getMemories(userId, 100, selectedCategory);
      setMemories(data.memories);
    } catch (error) {
      console.error('Error fetching memories:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const data = await memoriesAPI.getMemoryStats(userId);
      setStats(data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const handleDeleteMemory = async (memoryId) => {
    if (window.confirm('Are you sure you want to delete this memory?')) {
      try {
        await memoriesAPI.deleteMemory(memoryId);
        setMemories((prev) => prev.filter((m) => m.id !== memoryId));
      } catch (error) {
        console.error('Error deleting memory:', error);
      }
    }
  };

  const handleCreateMemory = async (e) => {
    e.preventDefault();
    if (!newMemory.memory_text.trim()) return;

    try {
      const created = await memoriesAPI.createMemory(
        userId,
        newMemory.memory_text,
        newMemory.category,
        newMemory.importance_score,
        newMemory.tags
      );
      setMemories((prev) => [created, ...prev]);
      setNewMemory({
        memory_text: '',
        category: 'general',
        importance_score: 0.5,
        tags: [],
      });
      setShowCreateForm(false);
    } catch (error) {
      console.error('Error creating memory:', error);
    }
  };

  return (
    <div className="memory-panel">
      <div className="panel-header">
        <h2>Memory Management</h2>
        <button
          className="create-btn"
          onClick={() => setShowCreateForm(!showCreateForm)}
        >
          <FiPlus /> New Memory
        </button>
      </div>

      {stats && (
        <div className="stats-section">
          <div className="stat-card">
            <div className="stat-value">{stats.total_memories}</div>
            <div className="stat-label">Total Memories</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{stats.categories.length}</div>
            <div className="stat-label">Categories</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{(stats.average_importance * 100).toFixed(0)}%</div>
            <div className="stat-label">Avg Importance</div>
          </div>
        </div>
      )}

      {showCreateForm && (
        <form onSubmit={handleCreateMemory} className="create-form">
          <textarea
            value={newMemory.memory_text}
            onChange={(e) =>
              setNewMemory({ ...newMemory, memory_text: e.target.value })
            }
            placeholder="Enter memory text..."
            className="memory-textarea"
          />
          <div className="form-row">
            <select
              value={newMemory.category}
              onChange={(e) =>
                setNewMemory({ ...newMemory, category: e.target.value })
              }
              className="form-select"
            >
              <option value="general">General</option>
              <option value="project">Project</option>
              <option value="preference">Preference</option>
              <option value="fact">Fact</option>
            </select>
            <input
              type="range"
              min="0"
              max="1"
              step="0.1"
              value={newMemory.importance_score}
              onChange={(e) =>
                setNewMemory({
                  ...newMemory,
                  importance_score: parseFloat(e.target.value),
                })
              }
              className="form-range"
            />
            <span className="importance-label">
              Importance: {(newMemory.importance_score * 100).toFixed(0)}%
            </span>
          </div>
          <div className="form-buttons">
            <button type="submit" className="btn-primary">
              Save Memory
            </button>
            <button
              type="button"
              onClick={() => setShowCreateForm(false)}
              className="btn-secondary"
            >
              Cancel
            </button>
          </div>
        </form>
      )}

      <div className="categories-filter">
        <button
          className={`category-btn ${!selectedCategory ? 'active' : ''}`}
          onClick={() => setSelectedCategory(null)}
        >
          All
        </button>
        {stats?.categories.map((cat) => (
          <button
            key={cat}
            className={`category-btn ${selectedCategory === cat ? 'active' : ''}`}
            onClick={() => setSelectedCategory(cat)}
          >
            {cat}
          </button>
        ))}
      </div>

      <div className="memories-container">
        {loading ? (
          <p className="loading">Loading memories...</p>
        ) : memories.length > 0 ? (
          <div className="memories-grid">
            {memories.map((memory) => (
              <div key={memory.id} className="memory-card">
                <div className="memory-card-header">
                  <span className="category-badge">{memory.category}</span>
                  <span className="importance-badge">
                    {(memory.importance_score * 100).toFixed(0)}%
                  </span>
                </div>
                <div className="memory-card-body">
                  <p className="memory-text">{memory.memory_text}</p>
                </div>
                <div className="memory-card-footer">
                  <small className="timestamp">
                    {new Date(memory.created_at).toLocaleDateString()}
                  </small>
                  <div className="memory-actions">
                    <button className="action-btn edit">
                      <FiEdit2 />
                    </button>
                    <button
                      className="action-btn delete"
                      onClick={() => handleDeleteMemory(memory.id)}
                    >
                      <FiTrash2 />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="no-memories">No memories stored yet</p>
        )}
      </div>
    </div>
  );
};

export default MemoryPanel;
