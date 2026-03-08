'use client';

import { useState, useEffect } from 'react';

interface Session {
  id: string;
  title: string;
  lastActive: Date;
  messageCount: number;
}

interface SessionListProps {
  userId: string;
  currentSessionId: string;
  onSelectSession: (sessionId: string) => void;
  onNewSession: () => void;
}

export function SessionList({ 
  userId, 
  currentSessionId, 
  onSelectSession,
  onNewSession 
}: SessionListProps) {
  const [sessions, setSessions] = useState<Session[]>(() => {
    // Initialize from localStorage on mount
    if (typeof window === 'undefined' || !userId) return [];
    
    const key = `sessions_${userId}`;
    const stored = localStorage.getItem(key);
    
    if (stored) {
      const parsed = JSON.parse(stored) as Session[];
      return parsed.map(s => ({ ...s, lastActive: new Date(s.lastActive) }));
    }
    
    return [];
  });

  // Update current session info
  useEffect(() => {
    if (typeof window === 'undefined' || !userId || !currentSessionId) return;

    const sessionInfo: Session = {
      id: currentSessionId,
      title: `Session ${new Date().toLocaleDateString()}`,
      lastActive: new Date(),
      messageCount: 0
    };

    // Update or add session
    // eslint-disable-next-line react-hooks/exhaustive-deps
    setSessions(prev => {
      const existing = prev.find(s => s.id === currentSessionId);
      if (existing) {
        return prev.map(s => s.id === currentSessionId ? sessionInfo : s);
      }
      return [sessionInfo, ...prev].slice(0, 20); // Keep last 20 sessions
    });
  }, [userId, currentSessionId]);

  // Persist to localStorage
  useEffect(() => {
    if (typeof window === 'undefined' || !userId || sessions.length === 0) return;
    localStorage.setItem(`sessions_${userId}`, JSON.stringify(sessions));
  }, [sessions, userId]);

  return (
    <div className="session-list">
      <div className="session-header">
        <h3>Your Sessions</h3>
        <button onClick={onNewSession} className="new-btn">
          ➕ New
        </button>
      </div>

      <div className="sessions">
        {sessions.map((session) => (
          <div
            key={session.id}
            className={`session-item ${session.id === currentSessionId ? 'active' : ''}`}
            onClick={() => onSelectSession(session.id)}
          >
            <div className="session-title">{session.title}</div>
            <div className="session-meta">
              {session.lastActive.toLocaleDateString()}
            </div>
          </div>
        ))}

        {sessions.length === 0 && (
          <div className="empty-state">
            <p>No sessions yet</p>
            <small>Start a conversation to create your first session</small>
          </div>
        )}
      </div>

      <style jsx>{`
        .session-list {
          width: 280px;
          background: rgba(15, 23, 42, 0.7);
          border-right: 1px solid rgba(148, 163, 184, 0.1);
          display: flex;
          flex-direction: column;
          backdrop-filter: blur(10px);
        }

        .session-header {
          padding: 20px;
          border-bottom: 1px solid rgba(148, 163, 184, 0.1);
          display: flex;
          justify-content: space-between;
          align-items: center;
          background: rgba(15, 23, 42, 0.95);
          backdrop-filter: blur(10px);
        }

        .session-header h3 {
          margin: 0;
          font-size: 16px;
          font-weight: 600;
          color: #e2e8f0;
        }

        .new-btn {
          padding: 6px 12px;
          background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
          color: white;
          border: none;
          border-radius: 6px;
          font-size: 12px;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s;
        }

        .new-btn:hover {
          transform: translateY(-1px);
          box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
        }

        .sessions {
          flex: 1;
          overflow-y: auto;
          padding: 8px;
        }

        .sessions::-webkit-scrollbar {
          width: 6px;
        }

        .sessions::-webkit-scrollbar-track {
          background: rgba(15, 23, 42, 0.3);
        }

        .sessions::-webkit-scrollbar-thumb {
          background: rgba(99, 102, 241, 0.5);
          border-radius: 3px;
        }

        .session-item {
          padding: 12px;
          margin-bottom: 6px;
          background: rgba(30, 41, 59, 0.5);
          border: 1px solid rgba(148, 163, 184, 0.1);
          border-radius: 8px;
          cursor: pointer;
          transition: all 0.2s;
        }

        .session-item:hover {
          background: rgba(30, 41, 59, 0.7);
          border-color: rgba(99, 102, 241, 0.3);
          transform: translateX(4px);
        }

        .session-item.active {
          background: rgba(99, 102, 241, 0.2);
          border-color: rgba(99, 102, 241, 0.4);
        }

        .session-title {
          font-size: 14px;
          font-weight: 500;
          color: #cbd5e1;
          margin-bottom: 4px;
        }

        .session-meta {
          font-size: 11px;
          color: #94a3b8;
        }

        .empty-state {
          text-align: center;
          padding: 40px 20px;
          color: #64748b;
        }

        .empty-state p {
          margin: 0 0 8px 0;
          font-size: 14px;
        }

        .empty-state small {
          font-size: 12px;
          color: #475569;
        }

        @media (max-width: 1024px) {
          .session-list {
            width: 240px;
          }
        }
      `}</style>
    </div>
  );
}
