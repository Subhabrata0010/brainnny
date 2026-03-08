// ============================================================================
// SemanticMemory Component
// Displays extracted knowledge and semantic memories
// ============================================================================

'use client';

import type { SemanticMemoryProps } from '../lib/types';

const MEMORY_TYPE_ICONS: Record<string, string> = {
  preference: '❤️',
  fact: '📌',
  topic: '🏷️',
  skill: '⚡',
  goal: '🎯',
};

const MEMORY_TYPE_COLORS: Record<string, string> = {
  preference: 'rgba(236, 72, 153, 0.15)',
  fact: 'rgba(59, 130, 246, 0.15)',
  topic: 'rgba(245, 158, 11, 0.15)',
  skill: 'rgba(168, 85, 247, 0.15)',
  goal: 'rgba(16, 185, 129, 0.15)',
};

export function SemanticMemory({ memories }: SemanticMemoryProps) {
  if (!memories || memories.length === 0) {
    return (
      <div className="empty-state">
        <p>No semantic memories yet</p>
        <small>Knowledge will be extracted as you chat</small>
      </div>
    );
  }

  // Group memories by type
  const groupedMemories = memories.reduce((acc, memory) => {
    if (!acc[memory.memory_type]) {
      acc[memory.memory_type] = [];
    }
    acc[memory.memory_type].push(memory);
    return acc;
  }, {} as Record<string, typeof memories>);

  return (
    <div className="semantic-memory">
      {Object.entries(groupedMemories).map(([type, typeMemories]) => (
        <div key={type} className="memory-group">
          <div className="group-header">
            <span className="icon">{MEMORY_TYPE_ICONS[type] || '📝'}</span>
            <span className="type-label">{type.toUpperCase()}</span>
            <span className="count">{typeMemories.length}</span>
          </div>

          <div className="memories-list">
            {typeMemories.map((memory) => (
              <div
                key={memory.memory_id}
                className="memory-item"
                style={{ backgroundColor: MEMORY_TYPE_COLORS[type] || '#f5f5f5' }}
              >
                <div className="memory-content">{memory.content}</div>
                <div className="memory-meta">
                  <span className="confidence">
                    Confidence: {(memory.confidence_score * 100).toFixed(0)}%
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}

      <style jsx>{`
        .semantic-memory {
          display: flex;
          flex-direction: column;
          gap: 20px;
        }

        .empty-state {
          padding: 40px 20px;
          text-align: center;
          color: #64748b;
        }

        .empty-state small {
          display: block;
          margin-top: 8px;
          font-size: 12px;
          color: #475569;
        }

        .memory-group {
          background: rgba(30, 41, 59, 0.5);
          border: 1px solid rgba(148, 163, 184, 0.1);
          border-radius: 10px;
          padding: 16px;
          backdrop-filter: blur(10px);
        }

        .group-header {
          display: flex;
          align-items: center;
          gap: 8px;
          margin-bottom: 12px;
          padding-bottom: 12px;
          border-bottom: 1px solid rgba(148, 163, 184, 0.1);
        }

        .icon {
          font-size: 18px;
          filter: drop-shadow(0 0 8px rgba(99, 102, 241, 0.3));
        }

        .type-label {
          flex: 1;
          font-size: 13px;
          font-weight: 700;
          color: #e2e8f0;
          letter-spacing: 0.5px;
        }

        .count {
          padding: 2px 8px;
          background: rgba(99, 102, 241, 0.2);
          border: 1px solid rgba(99, 102, 241, 0.3);
          border-radius: 10px;
          font-size: 11px;
          font-weight: 600;
          color: #a5b4fc;
        }

        .memories-list {
          display: flex;
          flex-direction: column;
          gap: 8px;
        }

        .memory-item {
          padding: 12px;
          border-radius: 8px;
          border-left: 3px solid rgba(99, 102, 241, 0.4);
          transition: all 0.2s;
        }

        .memory-item:hover {
          border-left-color: rgba(99, 102, 241, 0.8);
          transform: translateX(4px);
        }

        .memory-content {
          font-size: 13px;
          line-height: 1.5;
          color: #cbd5e1;
          margin-bottom: 6px;
        }

        .memory-meta {
          font-size: 11px;
          color: #94a3b8;
        }

        .confidence {
          font-weight: 500;
        }
      `}</style>
    </div>
  );
}