// ============================================================================
// useConversation Hook
// Manages conversation state and message sending
// ============================================================================

'use client';

import { useState, useCallback, useEffect } from 'react';
import { storeMessage } from '../lib/api';
import type { Message, UseConversationReturn } from '../lib/types';

const DEFAULT_USER_ID = 'user_' + Date.now();

// Get session ID from localStorage, scoped to user
function getStoredSessionId(userId: string): string {
  if (typeof window === 'undefined') return `session_${Date.now()}`;
  
  const key = `session_${userId}`;
  const stored = localStorage.getItem(key);
  
  if (stored) return stored;
  
  const newSession = `session_${Date.now()}`;
  localStorage.setItem(key, newSession);
  return newSession;
}

// Save session ID to localStorage
function saveSessionId(userId: string, sessionId: string) {
  if (typeof window === 'undefined') return;
  localStorage.setItem(`session_${userId}`, sessionId);
}

export function useConversation(userId: string = DEFAULT_USER_ID): UseConversationReturn {
  const [messages, setMessages] = useState<Message[]>([]);
  const [sessionId, setSessionId] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Initialize session ID from localStorage
  useEffect(() => {
    if (userId) {
      const storedSession = getStoredSessionId(userId);
      setSessionId(storedSession);
    }
  }, [userId]);

  const sendMessage = useCallback(
    async (content: string) => {
      if (!content.trim()) return;

      setIsLoading(true);
      setError(null);

      // Optimistically add user message to UI
      const userMessage: Message = {
        id: `msg_${Date.now()}`,
        role: 'user',
        content,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, userMessage]);

      try {
        // Store message in backend
        const response = await storeMessage({
          user_id: userId,
          session_id: sessionId,
          message: content,
          role: 'user',
        });

        // Update message with actual ID
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === userMessage.id
              ? { ...msg, id: response.message_id }
              : msg
          )
        );
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to send message');
        
        // Remove optimistic message on error
        setMessages((prev) => prev.filter((msg) => msg.id !== userMessage.id));
        
        throw err;
      } finally {
        setIsLoading(false);
      }
    },
    [userId, sessionId]
  );

  const startNewSession = useCallback(() => {
    const newSession = `session_${Date.now()}`;
    setSessionId(newSession);
    saveSessionId(userId, newSession);
    setMessages([]);
    setError(null);
  }, [userId]);

  return {
    messages,
    sendMessage,
    isLoading,
    error,
    sessionId,
    startNewSession,
  };
}