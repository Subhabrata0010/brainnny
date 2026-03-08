// ============================================================================
// MemoryPanel Component
// Main panel displaying all memory layers
// ============================================================================

'use client';

import { EpisodeList } from './EpisodeList';
import { SemanticMemory } from './SemanticMemory';
import type { MemoryPanelProps } from '../lib/types';

export function MemoryPanel({ context, isLoading, onRefresh }: MemoryPanelProps) {
  if (isLoading) {
    return (
      <div className="memory-panel loading">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Retrieving memory...</p>
        </div>

        <style jsx>{`
          .memory-panel.loading {
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 400px;
          }

          .loading-spinner {
            text-align: center;
          }

          .spinner {
            width: 40px;
            height: 40px;
            margin: 0 auto 16px;
            border: 3px solid rgba(99, 102, 241, 0.2);
            border-top-color: #6366f1;
            border-radius: 50%;
            animation: spin 1s linear infinite;
          }

          @keyframes spin {
            to {
              transform: rotate(360deg);
            }
          }

          .loading-spinner p {
            color: #94a3b8;
            font-size: 14px;
          }
        `}</style>
      </div>
    );
  }

  if (!context) {
    return (
      <div className="memory-panel empty">
        <div className="empty-state">
          <h3>No Memory Retrieved</h3>
          <p>Send a message to retrieve relevant memory context</p>
        </div>

        <style jsx>{`
          .memory-panel.empty {
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 400px;
          }

          .empty-state {
            text-align: center;
            color: #64748b;
          }

          .empty-state h3 {
            margin: 0 0 8px 0;
            font-size: 18px;
            font-weight: 600;
            color: #94a3b8;
          }

          .empty-state p {
            margin: 0;
            font-size: 14px;
          }
        `}</style>
      </div>
    );
  }

  return (
    <div className="memory-panel">
      {/* Header */}
      <div className="panel-header">
        <h2>Memory Context</h2>
        <button onClick={onRefresh} className="refresh-button" disabled={isLoading}>
          🔄 Refresh
        </button>
      </div>

      {/* User Profile */}
      {context.user_profile && (
        <div className="memory-section">
          <div className="section-header">
            <span className="icon">👤</span>
            <h3>User Profile</h3>
          </div>
          <div className="profile-content">
            {context.user_profile.communication_style && (
              <div className="profile-item">
                <strong>Style:</strong> {context.user_profile.communication_style}
              </div>
            )}
            {context.user_profile.recurring_topics && (
              <div className="profile-item">
                <strong>Topics:</strong>{' '}
                {context.user_profile.recurring_topics.join(', ')}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Episodic Memory */}
      {context.relevant_episodes.length > 0 && (
        <div className="memory-section">
          <div className="section-header">
            <span className="icon">📚</span>
            <h3>Episodic Memory</h3>
            <span className="count">{context.relevant_episodes.length}</span>
          </div>
          <EpisodeList episodes={context.relevant_episodes} />
        </div>
      )}

      {/* Semantic Memory */}
      {context.semantic_memory.length > 0 && (
        <div className="memory-section">
          <div className="section-header">
            <span className="icon">🧩</span>
            <h3>Semantic Memory</h3>
            <span className="count">{context.semantic_memory.length}</span>
          </div>
          <SemanticMemory memories={context.semantic_memory} />
        </div>
      )}

      {/* Recent Messages (Working Memory) */}
      {context.recent_messages.length > 0 && (
        <div className="memory-section">
          <div className="section-header">
            <span className="icon">💬</span>
            <h3>Working Memory</h3>
            <span className="count">{context.recent_messages.length}</span>
          </div>
          <div className="recent-messages">
            {context.recent_messages.map((msg) => (
              <div key={msg.message_id} className="message-item">
                <div className="message-role">{msg.role.toUpperCase()}</div>
                <div className="message-text">
                  {msg.content.substring(0, 100)}
                  {msg.content.length > 100 ? '...' : ''}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <style jsx>{`
        .memory-panel {
          display: flex;
          flex-direction: column;
          gap: 20px;
          height: 100%;
          overflow-y: auto;
        }

        .panel-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 20px;
          background: rgba(15, 23, 42, 0.95);
          border-bottom: 1px solid rgba(148, 163, 184, 0.1);
          position: sticky;
          top: 0;
          z-index: 10;
          backdrop-filter: blur(10px);
        }

        .panel-header h2 {
          margin: 0;
          font-size: 20px;
          font-weight: 700;
          background: linear-gradient(135deg, #818cf8 0%, #c084fc 100%);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
        }

        .refresh-button {
          padding: 8px 16px;
          background: linear-gradient(135deg, #10b981 0%, #059669 100%);
          color: white;
          border: none;
          border-radius: 8px;
          font-size: 13px;
          cursor: pointer;
          transition: all 0.2s;
          box-shadow: 0 2px 8px rgba(16, 185, 129, 0.3);
        }

        .refresh-button:hover:not(:disabled) {
          transform: translateY(-1px);
          box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
        }

        .refresh-button:disabled {
          background: rgba(100, 116, 139, 0.3);
          cursor: not-allowed;
          box-shadow: none;
        }

        .memory-section {
          padding: 0 20px 20px 20px;
        }

        .section-header {
          display: flex;
          align-items: center;
          gap: 10px;
          margin-bottom: 16px;
        }

        .section-header .icon {
          font-size: 20px;
          filter: drop-shadow(0 0 8px rgba(99, 102, 241, 0.3));
        }

        .section-header h3 {
          flex: 1;
          margin: 0;
          font-size: 16px;
          font-weight: 600;
          color: #e2e8f0;
        }

        .section-header .count {
          padding: 4px 10px;
          background: rgba(99, 102, 241, 0.2);
          border: 1px solid rgba(99, 102, 241, 0.3);
          border-radius: 12px;
          font-size: 12px;
          font-weight: 600;
          color: #a5b4fc;
        }

        .profile-content {
          padding: 16px;
          background: rgba(30, 41, 59, 0.5);
          border: 1px solid rgba(99, 102, 241, 0.2);
          border-radius: 10px;
          backdrop-filter: blur(10px);
        }

        .profile-item {
          font-size: 14px;
          line-height: 1.8;
          color: #cbd5e1;
        }

        .profile-item strong {
          color: #e2e8f0;
        }

        .recent-messages {
          display: flex;
          flex-direction: column;
          gap: 8px;
        }

        .message-item {
          padding: 12px;
          background: rgba(30, 41, 59, 0.5);
          border: 1px solid rgba(148, 163, 184, 0.1);
          border-radius: 8px;
          transition: all 0.2s;
        }

        .message-item:hover {
          background: rgba(30, 41, 59, 0.7);
          border-color: rgba(99, 102, 241, 0.3);
        }

        .message-role {
          font-size: 11px;
          font-weight: 700;
          color: #94a3b8;
          margin-bottom: 4px;
        }

        .message-text {
          font-size: 13px;
          line-height: 1.5;
          color: #cbd5e1;
        }
      `}</style>
    </div>
  );
}