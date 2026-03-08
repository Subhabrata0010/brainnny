// ============================================================================
// EpisodeList Component
// Displays list of episodic memories (past conversations)
// ============================================================================

'use client';

import type { EpisodeListProps } from '../lib/types';

export function EpisodeList({ episodes, onSelectEpisode }: EpisodeListProps) {
  if (!episodes || episodes.length === 0) {
    return (
      <div className="empty-state">
        <p>No past conversations found</p>
      </div>
    );
  }

  return (
    <div className="episode-list">
      {episodes.map((episode, index) => (
        <div
          key={episode.episode_id}
          className="episode-card"
          onClick={() => onSelectEpisode?.(episode.episode_id)}
        >
          <div className="episode-header">
            <span className="episode-number">Episode {index + 1}</span>
            <span className="importance-badge">
              {(episode.importance_score * 100).toFixed(0)}%
            </span>
          </div>
          
          <div className="episode-summary">{episode.summary}</div>
          
          <div className="episode-meta">
            <span className="message-count">
              {episode.message_count} message{episode.message_count !== 1 ? 's' : ''}
            </span>
            <span className="timestamp">
              {new Date(episode.created_at).toLocaleDateString()}
            </span>
          </div>
        </div>
      ))}

      <style jsx>{`
        .episode-list {
          display: flex;
          flex-direction: column;
          gap: 12px;
        }

        .empty-state {
          padding: 40px 20px;
          text-align: center;
          color: #64748b;
        }

        .episode-card {
          padding: 16px;
          background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(5, 150, 105, 0.1) 100%);
          border: 1px solid rgba(16, 185, 129, 0.2);
          border-radius: 10px;
          cursor: pointer;
          transition: all 0.3s;
          backdrop-filter: blur(10px);
        }

        .episode-card:hover {
          background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(5, 150, 105, 0.15) 100%);
          border-color: rgba(16, 185, 129, 0.4);
          transform: translateX(6px);
          box-shadow: 0 4px 12px rgba(16, 185, 129, 0.2);
        }

        .episode-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 8px;
        }

        .episode-number {
          font-size: 12px;
          font-weight: 600;
          color: #6ee7b7;
          text-transform: uppercase;
        }

        .importance-badge {
          padding: 2px 8px;
          background: linear-gradient(135deg, #10b981 0%, #059669 100%);
          color: white;
          border-radius: 12px;
          font-size: 11px;
          font-weight: 600;
          box-shadow: 0 2px 8px rgba(16, 185, 129, 0.3);
        }

        .episode-summary {
          font-size: 14px;
          line-height: 1.5;
          color: #cbd5e1;
          margin-bottom: 10px;
        }

        .episode-meta {
          display: flex;
          justify-content: space-between;
          font-size: 12px;
          color: #94a3b8;
        }

        .message-count {
          font-weight: 500;
        }

        .timestamp {
          font-style: italic;
        }
      `}</style>
    </div>
  );
}