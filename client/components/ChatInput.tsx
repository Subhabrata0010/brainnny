// ============================================================================
// ChatInput Component
// Input field for sending messages
// ============================================================================

'use client';

import { useState, KeyboardEvent } from 'react';
import type { ChatInputProps } from '../lib/types';

export function ChatInput({ onSendMessage, isLoading }: ChatInputProps) {
  const [message, setMessage] = useState('');

  const handleSubmit = () => {
    if (message.trim() && !isLoading) {
      onSendMessage(message);
      setMessage('');
    }
  };

  const handleKeyPress = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="chat-input-container">
      <input
        type="text"
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        onKeyPress={handleKeyPress}
        placeholder="Type your message..."
        disabled={isLoading}
        className="chat-input"
      />
      <button
        onClick={handleSubmit}
        disabled={isLoading || !message.trim()}
        className="send-button"
      >
        {isLoading ? 'Sending...' : 'Send'}
      </button>

      <style jsx>{`
        .chat-input-container {
          display: flex;
          gap: 10px;
          padding: 15px;
          background: rgba(15, 23, 42, 0.95);
          border-top: 1px solid rgba(148, 163, 184, 0.1);
          backdrop-filter: blur(10px);
        }

        .chat-input {
          flex: 1;
          padding: 12px 16px;
          background: rgba(30, 41, 59, 0.8);
          border: 1px solid rgba(99, 102, 241, 0.3);
          border-radius: 10px;
          font-size: 14px;
          color: #e2e8f0;
          outline: none;
          transition: all 0.2s;
        }

        .chat-input::placeholder {
          color: #64748b;
        }

        .chat-input:focus {
          border-color: #6366f1;
          box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
        }

        .chat-input:disabled {
          background: rgba(30, 41, 59, 0.4);
          cursor: not-allowed;
          opacity: 0.5;
        }

        .send-button {
          padding: 12px 24px;
          background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
          color: white;
          border: none;
          border-radius: 10px;
          font-size: 14px;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s;
          box-shadow: 0 2px 8px rgba(99, 102, 241, 0.3);
        }

        .send-button:hover:not(:disabled) {
          transform: translateY(-2px);
          box-shadow: 0 4px 12px rgba(99, 102, 241, 0.5);
        }

        .send-button:disabled {
          background: rgba(100, 116, 139, 0.3);
          cursor: not-allowed;
          transform: none;
          box-shadow: none;
        }
      `}</style>
    </div>
  );
}