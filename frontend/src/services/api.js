import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const chatAPI = {
  sendMessage: async (userId, message, topK = 5) => {
    try {
      const response = await api.post('/chat', {
        user_id: userId,
        message: message,
        retrieve_memories: true,
        top_k: topK,
      });
      return response.data;
    } catch (error) {
      console.error('Error sending message:', error);
      throw error;
    }
  },

  storeMemory: async (userId, memoryText, category = 'general', importance = 0.5) => {
    try {
      const response = await api.post('/chat/store-memory', null, {
        params: {
          user_id: userId,
          memory_text: memoryText,
          category: category,
          importance_score: importance,
        },
      });
      return response.data;
    } catch (error) {
      console.error('Error storing memory:', error);
      throw error;
    }
  },
};

export const memoriesAPI = {
  getMemories: async (userId, limit = 100, category = null) => {
    try {
      const params = { user_id: userId, limit };
      if (category) params.category = category;
      const response = await api.get('/memories', { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching memories:', error);
      throw error;
    }
  },

  getMemory: async (memoryId) => {
    try {
      const response = await api.get(`/memories/${memoryId}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching memory:', error);
      throw error;
    }
  },

  createMemory: async (userId, memoryText, category = 'general', importance = 0.5, tags = []) => {
    try {
      const response = await api.post('/memories', 
        {
          memory_text: memoryText,
          category: category,
          importance_score: importance,
          tags: tags,
        },
        {
          params: { user_id: userId },
        }
      );
      return response.data;
    } catch (error) {
      console.error('Error creating memory:', error);
      throw error;
    }
  },

  updateMemory: async (memoryId, updates) => {
    try {
      const response = await api.put(`/memories/${memoryId}`, updates);
      return response.data;
    } catch (error) {
      console.error('Error updating memory:', error);
      throw error;
    }
  },

  deleteMemory: async (memoryId) => {
    try {
      const response = await api.delete(`/memories/${memoryId}`);
      return response.data;
    } catch (error) {
      console.error('Error deleting memory:', error);
      throw error;
    }
  },

  getMemoryStats: async (userId) => {
    try {
      const response = await api.get(`/memories/stats/${userId}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching memory stats:', error);
      throw error;
    }
  },
};

export const healthAPI = {
  checkHealth: async () => {
    try {
      const response = await api.get('/health');
      return response.data;
    } catch (error) {
      console.error('Error checking health:', error);
      throw error;
    }
  },
};

export default api;
