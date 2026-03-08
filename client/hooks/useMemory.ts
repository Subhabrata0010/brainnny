// ============================================================================
// useMemory Hook
// Manages memory retrieval and context state
// ============================================================================

'use client';

import { useState, useCallback } from 'react';
import { retrieveContext } from '../lib/api';
import type { RetrievedContext, UseMemoryReturn } from '../lib/types';

const DEFAULT_USER_ID = 'user_' + Date.now();

export function useMemory(
  userId: string = DEFAULT_USER_ID,
  sessionId?: string
): UseMemoryReturn {
  const [context, setContext] = useState<RetrievedContext | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [stats, setStats] = useState<{
    episodes: number;
    semantic: number;
    recent: number;
  } | null>(null);

  const retrieveMemoryContext = useCallback(
    async (query: string) => {
      if (!query.trim()) return;

      setIsLoading(true);
      setError(null);

      try {
        const response = await retrieveContext({
          user_id: userId,
          query,
          session_id: sessionId,
          max_episodes: 10,
          max_semantic: 5,
          include_recent: 5,
        });

        setContext(response.context);
        setStats({
          episodes: response.retrieval_stats.episodes_retrieved,
          semantic: response.retrieval_stats.semantic_memories,
          recent: response.retrieval_stats.recent_messages,
        });
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to retrieve context');
        throw err;
      } finally {
        setIsLoading(false);
      }
    },
    [userId, sessionId]
  );

  return {
    context,
    retrieveContext: retrieveMemoryContext,
    isLoading,
    error,
    stats,
  };
}