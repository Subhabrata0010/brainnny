/* eslint-disable @typescript-eslint/no-explicit-any */
// ============================================================================
// Second Brain - API Client
// ============================================================================

import type {
  ConversationRequest,
  ConversationResponse,
  RetrieveContextRequest,
  ContextResponse,
  ApiError,
} from './types';

// API Configuration
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const DEFAULT_TIMEOUT = 30000; // 30 seconds

// ----------------------------------------------------------------------------
// Error Handling
// ----------------------------------------------------------------------------

class ApiClientError extends Error {
  constructor(
    message: string,
    public status?: number,
    public details?: any
  ) {
    super(message);
    this.name = 'ApiClientError';
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new ApiClientError(
      errorData.detail || `HTTP Error ${response.status}`,
      response.status,
      errorData
    );
  }

  return response.json();
}

// ----------------------------------------------------------------------------
// API Functions
// ----------------------------------------------------------------------------

/**
 * Store a conversation message
 */
export async function storeMessage(
  request: ConversationRequest
): Promise<ConversationResponse> {
  const response = await fetch(`${API_URL}/conversation`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
    signal: AbortSignal.timeout(DEFAULT_TIMEOUT),
  });

  return handleResponse<ConversationResponse>(response);
}

/**
 * Retrieve memory context
 */
export async function retrieveContext(
  request: RetrieveContextRequest
): Promise<ContextResponse> {
  const response = await fetch(`${API_URL}/retrieve-context`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
    signal: AbortSignal.timeout(DEFAULT_TIMEOUT),
  });

  return handleResponse<ContextResponse>(response);
}

/**
 * Health check
 */
export async function healthCheck(): Promise<{
  status: string;
  service: string;
  architecture: string;
}> {
  const response = await fetch(`${API_URL}/health`, {
    method: 'GET',
  });

  return handleResponse(response);
}

/**
 * Create or get user profile
 */
export async function createOrGetUser(userId: string): Promise<{
  user_id: string;
  communication_style: string | null;
  recurring_topics: string[];
  preferences: Record<string, any>;
}> {
  const response = await fetch(`${API_URL}/user/${userId}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  return handleResponse(response);
}

/**
 * Get API info
 */
export async function getApiInfo(): Promise<any> {
  const response = await fetch(`${API_URL}/`, {
    method: 'GET',
  });

  return handleResponse(response);
}

// ----------------------------------------------------------------------------
// Helper Functions
// ----------------------------------------------------------------------------

/**
 * Test API connection
 */
export async function testConnection(): Promise<boolean> {
  try {
    await healthCheck();
    return true;
  } catch (error) {
    console.error('API connection test failed:', error);
    return false;
  }
}

/**
 * Format API error for display
 */
export function formatApiError(error: unknown): string {
  if (error instanceof ApiClientError) {
    return error.message;
  }

  if (error instanceof Error) {
    return error.message;
  }

  return 'An unknown error occurred';
}

// Export types
export type { ApiError };
export { ApiClientError };