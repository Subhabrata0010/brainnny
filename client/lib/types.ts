/* eslint-disable @typescript-eslint/no-explicit-any */
// ============================================================================
// Second Brain - TypeScript Type Definitions
// ============================================================================

// ----------------------------------------------------------------------------
// API Request Types
// ----------------------------------------------------------------------------

export interface ConversationRequest {
  user_id: string;
  session_id: string;
  message: string;
  role: 'user' | 'assistant';
}

export interface RetrieveContextRequest {
  user_id: string;
  query: string;
  session_id?: string;
  max_episodes?: number;
  max_semantic?: number;
  include_recent?: number;
}

// ----------------------------------------------------------------------------
// API Response Types
// ----------------------------------------------------------------------------

export interface ConversationResponse {
  message_id: string;
  episode_id: string;
  stored: boolean;
  message: string;
}

export interface EpisodeResponse {
  episode_id: string;
  user_id: string;
  session_id: string;
  summary: string;
  importance_score: number;
  message_count: number;
  created_at: string;
  updated_at: string;
}

export interface SemanticMemoryResponse {
  memory_id: string;
  user_id: string;
  memory_type: 'preference' | 'fact' | 'topic' | 'skill' | 'goal';
  content: string;
  confidence_score: number;
  created_at: string;
}

export interface ConversationLogResponse {
  message_id: string;
  session_id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export interface UserProfileResponse {
  user_id: string;
  communication_style?: string;
  recurring_topics?: string[];
  preferences?: Record<string, any>;
}

export interface RetrievedContext {
  user_profile: UserProfileResponse | null;
  relevant_episodes: EpisodeResponse[];
  semantic_memory: SemanticMemoryResponse[];
  recent_messages: ConversationLogResponse[];
  context_summary: string;
}

export interface ContextResponse {
  context: RetrievedContext;
  query: string;
  retrieval_stats: {
    episodes_retrieved: number;
    semantic_memories: number;
    recent_messages: number;
  };
}

// ----------------------------------------------------------------------------
// UI State Types
// ----------------------------------------------------------------------------

export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
}

export interface Session {
  id: string;
  title: string;
  created_at: Date;
  message_count: number;
}

export interface MemoryStats {
  total_episodes: number;
  total_messages: number;
  semantic_memories: number;
}

// ----------------------------------------------------------------------------
// Component Props Types
// ----------------------------------------------------------------------------

export interface ChatInputProps {
  onSendMessage: (message: string) => void;
  isLoading: boolean;
}

export interface MemoryPanelProps {
  context: RetrievedContext | null;
  isLoading: boolean;
  onRefresh: () => void;
}

export interface EpisodeListProps {
  episodes: EpisodeResponse[];
  onSelectEpisode?: (episodeId: string) => void;
}

export interface SemanticMemoryProps {
  memories: SemanticMemoryResponse[];
}

// ----------------------------------------------------------------------------
// Hook Return Types
// ----------------------------------------------------------------------------

export interface UseConversationReturn {
  messages: Message[];
  sendMessage: (content: string) => Promise<void>;
  isLoading: boolean;
  error: string | null;
  sessionId: string;
  startNewSession: () => void;
}

export interface UseMemoryReturn {
  context: RetrievedContext | null;
  retrieveContext: (query: string) => Promise<void>;
  isLoading: boolean;
  error: string | null;
  stats: {
    episodes: number;
    semantic: number;
    recent: number;
  } | null;
}

// ----------------------------------------------------------------------------
// API Client Types
// ----------------------------------------------------------------------------

export interface ApiClientConfig {
  baseUrl: string;
  timeout?: number;
}

export interface ApiError {
  message: string;
  status?: number;
  details?: any;
}