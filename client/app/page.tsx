// ============================================================================
// Main Page - Second Brain Chat Interface
// ============================================================================

'use client';

import { useState, useEffect } from 'react';
import { useUser, UserButton } from '@clerk/nextjs';
import { ChatInput } from '../components/ChatInput';
import { MemoryPanel } from '../components/MemoryPanel';
import { SessionList } from '../components/SessionList';
import { useConversation } from '../hooks/useConversation';
import { useMemory } from '../hooks/useMemory';
import { createOrGetUser } from '../lib/api';

export default function ChatPage() {
  const { user, isLoaded, isSignedIn } = useUser();
  const [showMemory, setShowMemory] = useState(false);
  const [showSessions, setShowSessions] = useState(true);
  const [autoRetrieve, setAutoRetrieve] = useState(true);

  // Use Clerk user ID or fallback to guest
  const userId = user?.id || 'guest';

  const conversation = useConversation(userId);
  const memory = useMemory(userId, conversation.sessionId);

  // Create/ensure user exists in backend when signed in
  useEffect(() => {
    if (isSignedIn && user?.id) {
      createOrGetUser(user.id).catch((error) => {
        console.error('Failed to create/get user profile:', error);
      });
    }
  }, [isSignedIn, user?.id]);

  // Auto-retrieve context after sending message
  useEffect(() => {
    if (
      autoRetrieve &&
      conversation.messages.length > 0 &&
      !conversation.isLoading &&
      isSignedIn
    ) {
      const lastMessage = conversation.messages[conversation.messages.length - 1];
      if (lastMessage.role === 'user') {
        memory.retrieveContext(lastMessage.content);
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [conversation.messages.length, autoRetrieve, conversation.isLoading, isSignedIn]);

  const handleSendMessage = async (content: string) => {
    await conversation.sendMessage(content);
  };

  const handleRefreshMemory = () => {
    if (conversation.messages.length > 0) {
      const lastMessage = conversation.messages[conversation.messages.length - 1];
      memory.retrieveContext(lastMessage.content);
    }
  };

  // Show loading state while Clerk is initializing
  if (!isLoaded) {
    return (
      <div className="app-container">
        <div className="loading-container">
          <div className="spinner"></div>
          <p>Loading...</p>
        </div>
        <style jsx>{`
          .app-container {
            display: flex;
            flex-direction: column;
            height: 100vh;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
          }
          .loading-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            gap: 16px;
          }
          .spinner {
            width: 48px;
            height: 48px;
            border: 4px solid rgba(99, 102, 241, 0.2);
            border-top-color: #6366f1;
            border-radius: 50%;
            animation: spin 1s linear infinite;
          }
          @keyframes spin {
            to { transform: rotate(360deg); }
          }
          p {
            color: #94a3b8;
            font-size: 16px;
          }
        `}</style>
      </div>
    );
  }

  return (
    <div className="app-container">
      {/* Header */}
      <header className="app-header">
        <div className="header-content">
          <div className="logo">
            <span className="icon">🧠</span>
            <h1>Second Brain</h1>
            <span className="version">v2.0</span>
          </div>

          <div className="header-controls">
            {isSignedIn && user && (
              <div className="user-info">
                <span className="user-name">{user.firstName || user.username || 'User'}</span>
              </div>
            )}

            <label className="toggle-label">
              <input
                type="checkbox"
                checked={autoRetrieve}
                onChange={(e) => setAutoRetrieve(e.target.checked)}
              />
              <span>Auto-retrieve</span>
            </label>

            <button
              onClick={() => setShowSessions(!showSessions)}
              className="toggle-sessions-btn"
            >
              {showSessions ? '📋 Hide' : '📋 Show'} Sessions
            </button>

            <button
              onClick={() => setShowMemory(!showMemory)}
              className="toggle-memory-btn"
            >
              {showMemory ? '📖 Hide' : '📚 Show'} Memory
            </button>

            <button
              onClick={conversation.startNewSession}
              className="new-session-btn"
            >
              ➕ New Session
            </button>

            {isSignedIn && (
              <div className="user-button-wrapper">
                <UserButton />
              </div>
            )}
          </div>
        </div>

        <div className="session-info">
          <span>Session: {conversation.sessionId}</span>
          {isSignedIn && <span className="user-id">User: {userId}</span>}
          {memory.stats && (
            <span className="stats">
              📚 {memory.stats.episodes} episodes · 
              🧩 {memory.stats.semantic} semantic · 
              💬 {memory.stats.recent} recent
            </span>
          )}
        </div>
      </header>

      {/* Main Content */}
      <main className="main-content">
        {/* Session List */}
        {showSessions && isSignedIn && (
          <SessionList
            userId={userId}
            currentSessionId={conversation.sessionId}
            onSelectSession={(sessionId) => {
              // Switch to selected session (would need to load messages)
              console.log('Switch to session:', sessionId);
            }}
            onNewSession={conversation.startNewSession}
          />
        )}

        {/* Chat Area */}
        <div className={`chat-area ${showMemory ? 'with-memory' : ''} ${showSessions ? 'with-sessions' : ''}`}>
          <div className="messages-container">
            {conversation.messages.length === 0 ? (
              <div className="empty-chat">
                <h2>Welcome to Second Brain</h2>
                <p>Multi-layer memory system for conversations</p>
                <div className="features">
                  <div className="feature">
                    <span>📚</span>
                    <strong>Episodic Memory</strong>
                    <small>Past conversations</small>
                  </div>
                  <div className="feature">
                    <span>🧩</span>
                    <strong>Semantic Memory</strong>
                    <small>Extracted knowledge</small>
                  </div>
                  <div className="feature">
                    <span>💬</span>
                    <strong>Working Memory</strong>
                    <small>Recent messages</small>
                  </div>
                </div>
              </div>
            ) : (
              conversation.messages.map((message) => (
                <div
                  key={message.id}
                  className={`message message-${message.role}`}
                >
                  <div className="message-header">
                    <strong>{message.role.toUpperCase()}</strong>
                    <span className="timestamp">
                      {message.timestamp.toLocaleTimeString()}
                    </span>
                  </div>
                  <div className="message-content">{message.content}</div>
                </div>
              ))
            )}

            {conversation.error && (
              <div className="error-message">
                <strong>Error:</strong> {conversation.error}
              </div>
            )}

            {memory.error && (
              <div className="error-message">
                <strong>Memory Error:</strong> {memory.error}
              </div>
            )}
          </div>

          <ChatInput
            onSendMessage={handleSendMessage}
            isLoading={conversation.isLoading}
          />
        </div>

        {/* Memory Panel */}
        {showMemory && (
          <div className="memory-area">
            <MemoryPanel
              context={memory.context}
              isLoading={memory.isLoading}
              onRefresh={handleRefreshMemory}
            />
          </div>
        )}
      </main>

      <style jsx>{`
        .app-container {
          display: flex;
          flex-direction: column;
          height: 100vh;
          background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        }

        .app-header {
          background: rgba(15, 23, 42, 0.95);
          backdrop-filter: blur(10px);
          border-bottom: 1px solid rgba(148, 163, 184, 0.1);
          padding: 16px 24px;
          box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
        }

        .header-content {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 12px;
        }

        .logo {
          display: flex;
          align-items: center;
          gap: 12px;
        }

        .logo .icon {
          font-size: 32px;
          filter: drop-shadow(0 0 8px rgba(99, 102, 241, 0.5));
        }

        .logo h1 {
          margin: 0;
          font-size: 24px;
          font-weight: 700;
          background: linear-gradient(135deg, #818cf8 0%, #c084fc 100%);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
        }

        .logo .version {
          padding: 4px 8px;
          background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
          color: white;
          border-radius: 6px;
          font-size: 12px;
          font-weight: 600;
          box-shadow: 0 2px 8px rgba(99, 102, 241, 0.4);
        }

        .header-controls {
          display: flex;
          gap: 12px;
          align-items: center;
        }

        .user-info {
          padding: 6px 12px;
          background: rgba(99, 102, 241, 0.1);
          border: 1px solid rgba(99, 102, 241, 0.3);
          border-radius: 8px;
        }

        .user-name {
          font-size: 14px;
          font-weight: 500;
          color: #a5b4fc;
        }

        .user-button-wrapper {
          display: flex;
          align-items: center;
        }

        .toggle-label {
          display: flex;
          align-items: center;
          gap: 6px;
          font-size: 14px;
          cursor: pointer;
          color: #cbd5e1;
          transition: color 0.2s;
        }

        .toggle-label:hover {
          color: #e2e8f0;
        }

        .toggle-label input {
          cursor: pointer;
          accent-color: #6366f1;
        }

        .toggle-memory-btn,
        .toggle-sessions-btn,
        .new-session-btn {
          padding: 8px 16px;
          border: none;
          border-radius: 8px;
          font-size: 14px;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.2s;
        }

        .toggle-sessions-btn {
          background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
          color: white;
          box-shadow: 0 2px 8px rgba(245, 158, 11, 0.3);
        }

        .toggle-sessions-btn:hover {
          transform: translateY(-1px);
          box-shadow: 0 4px 12px rgba(245, 158, 11, 0.4);
        }

        .toggle-memory-btn {
          background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
          color: white;
          box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
        }

        .toggle-memory-btn:hover {
          transform: translateY(-1px);
          box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
        }

        .new-session-btn {
          background: rgba(148, 163, 184, 0.1);
          color: #cbd5e1;
          border: 1px solid rgba(148, 163, 184, 0.2);
        }

        .new-session-btn:hover {
          background: rgba(148, 163, 184, 0.2);
          color: #e2e8f0;
        }

        .session-info {
          display: flex;
          gap: 16px;
          font-size: 12px;
          color: #94a3b8;
          flex-wrap: wrap;
        }

        .user-id {
          padding-left: 16px;
          border-left: 1px solid rgba(148, 163, 184, 0.2);
          color: #a5b4fc;
        }

        .stats {
          padding-left: 16px;
          border-left: 1px solid rgba(148, 163, 184, 0.2);
        }

        .main-content {
          flex: 1;
          display: flex;
          overflow: hidden;
        }

        .chat-area {
          flex: 1;
          display: flex;
          flex-direction: column;
          background: rgba(15, 23, 42, 0.5);
          transition: all 0.3s;
        }

        .chat-area.with-memory {
          flex: 1;
        }

        .chat-area.with-sessions {
          flex: 1;
        }

        .messages-container {
          flex: 1;
          overflow-y: auto;
          padding: 24px;
        }

        .messages-container::-webkit-scrollbar {
          width: 8px;
        }

        .messages-container::-webkit-scrollbar-track {
          background: rgba(15, 23, 42, 0.3);
        }

        .messages-container::-webkit-scrollbar-thumb {
          background: rgba(99, 102, 241, 0.5);
          border-radius: 4px;
        }

        .messages-container::-webkit-scrollbar-thumb:hover {
          background: rgba(99, 102, 241, 0.7);
        }

        .empty-chat {
          text-align: center;
          padding: 60px 20px;
        }

        .empty-chat h2 {
          margin: 0 0 8px 0;
          font-size: 32px;
          background: linear-gradient(135deg, #818cf8 0%, #c084fc 100%);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
        }

        .empty-chat p {
          margin: 0 0 40px 0;
          font-size: 16px;
          color: #94a3b8;
        }

        .features {
          display: flex;
          justify-content: center;
          gap: 40px;
        }

        .feature {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 8px;
          padding: 20px;
          background: rgba(99, 102, 241, 0.05);
          border: 1px solid rgba(99, 102, 241, 0.2);
          border-radius: 12px;
          transition: all 0.3s;
        }

        .feature:hover {
          background: rgba(99, 102, 241, 0.1);
          border-color: rgba(99, 102, 241, 0.3);
          transform: translateY(-2px);
        }

        .feature span {
          font-size: 32px;
          filter: drop-shadow(0 0 8px rgba(99, 102, 241, 0.3));
        }

        .feature strong {
          font-size: 14px;
          color: #e2e8f0;
        }

        .feature small {
          font-size: 12px;
          color: #94a3b8;
        }

        .message {
          margin-bottom: 20px;
          padding: 16px;
          border-radius: 12px;
          max-width: 80%;
          backdrop-filter: blur(10px);
          animation: slideIn 0.3s ease-out;
        }

        @keyframes slideIn {
          from {
            opacity: 0;
            transform: translateY(10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        .message-user {
          background: linear-gradient(135deg, rgba(99, 102, 241, 0.2) 0%, rgba(139, 92, 246, 0.2) 100%);
          border: 1px solid rgba(99, 102, 241, 0.3);
          margin-left: auto;
        }

        .message-assistant {
          background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(5, 150, 105, 0.15) 100%);
          border: 1px solid rgba(16, 185, 129, 0.3);
        }

        .message-system {
          background: linear-gradient(135deg, rgba(245, 158, 11, 0.15) 0%, rgba(217, 119, 6, 0.15) 100%);
          border: 1px solid rgba(245, 158, 11, 0.3);
        }

        .message-header {
          display: flex;
          justify-content: space-between;
          margin-bottom: 8px;
          font-size: 12px;
        }

        .message-header strong {
          color: #e2e8f0;
          font-weight: 600;
        }

        .message-header .timestamp {
          color: #94a3b8;
        }

        .message-content {
          font-size: 14px;
          line-height: 1.6;
          color: #cbd5e1;
        }

        .error-message {
          padding: 12px;
          background: rgba(239, 68, 68, 0.1);
          border-left: 4px solid #ef4444;
          border-radius: 8px;
          margin-bottom: 16px;
          font-size: 14px;
          color: #fca5a5;
          backdrop-filter: blur(10px);
        }

        .memory-area {
          width: 500px;
          background: rgba(15, 23, 42, 0.7);
          border-left: 1px solid rgba(148, 163, 184, 0.1);
          overflow-y: auto;
          backdrop-filter: blur(10px);
        }

        .memory-area::-webkit-scrollbar {
          width: 8px;
        }

        .memory-area::-webkit-scrollbar-track {
          background: rgba(15, 23, 42, 0.3);
        }

        .memory-area::-webkit-scrollbar-thumb {
          background: rgba(99, 102, 241, 0.5);
          border-radius: 4px;
        }

        .memory-area::-webkit-scrollbar-thumb:hover {
          background: rgba(99, 102, 241, 0.7);
        }

        @media (max-width: 1024px) {
          .memory-area {
            width: 400px;
          }
        }

        @media (max-width: 768px) {
          .header-content {
            flex-direction: column;
            gap: 12px;
          }

          .memory-area {
            display: none;
          }

          .message {
            max-width: 90%;
          }
        }
      `}</style>
    </div>
  );
}