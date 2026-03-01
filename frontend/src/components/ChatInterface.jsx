import React, { useState, useRef, useEffect } from 'react';
import { chatAPI } from '../services/api';
import { FiSend, FiLoader } from 'react-icons/fi';
import '../styles/ChatInterface.css';

const ChatInterface = ({ userId }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [retrievedMemories, setRetrievedMemories] = useState([]);
  const [memoryContext, setMemoryContext] = useState('');
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput('');
    setMessages((prev) => [...prev, { role: 'user', content: userMessage }]);
    setLoading(true);

    try {
      const response = await chatAPI.sendMessage(userId, userMessage);
      
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: response.response },
      ]);
      setRetrievedMemories(response.memories);
      setMemoryContext(response.memory_context);
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: 'Error: Failed to get response. Please try again.',
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chat-interface">
      <div className="chat-container">
        <div className="messages-section">
          <div className="messages">
            {messages.map((msg, idx) => (
              <div key={idx} className={`message message-${msg.role}`}>
                <div className="message-content">{msg.content}</div>
              </div>
            ))}
            {loading && (
              <div className="message message-assistant">
                <div className="message-content loading">
                  <FiLoader className="spinner" /> Thinking...
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <form onSubmit={handleSendMessage} className="input-form">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type your message..."
              disabled={loading}
              className="message-input"
            />
            <button type="submit" disabled={loading} className="send-button">
              <FiSend />
            </button>
          </form>
        </div>

        <div className="memory-panel">
          <div className="memory-section">
            <h3>Memory Context</h3>
            {memoryContext ? (
              <div className="memory-context">
                {memoryContext.split('\n').map((line, idx) => (
                  line && <p key={idx}>{line}</p>
                ))}
              </div>
            ) : (
              <p className="no-memories">No memories retrieved yet</p>
            )}
          </div>

          <div className="memory-section">
            <h3>Retrieved Memories ({retrievedMemories.length})</h3>
            <div className="memories-list">
              {retrievedMemories.length > 0 ? (
                retrievedMemories.map((memory) => (
                  <div key={memory.id} className="memory-item">
                    <div className="memory-text">{memory.memory_text}</div>
                    <div className="memory-meta">
                      <span className="category">{memory.category}</span>
                      <span className="similarity">
                        {(memory.semantic_similarity * 100).toFixed(0)}% match
                      </span>
                    </div>
                  </div>
                ))
              ) : (
                <p className="no-memories">No memories retrieved</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;
