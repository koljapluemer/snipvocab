import type { EnrichedSnippetDetails } from '@/shared/domainTypes'

// API Response Types
export interface AuthUserResponse {
  email: string
}

export interface LoginResponse {
  access: string
  refresh: string
}

export interface RegisterResponse {
  tokens: {
    access: string
    refresh: string
  }
}

export interface SnippetPracticeResponse {
  perceived_difficulty: number | null;
  updated: string;
}

export interface VideoProgressResponse {
  lastPracticed: string | null;
  perceivedDifficulty?: number | null;
  snippetPercentageWatched: number | null;
}

export interface EnrichedSnippetsResponse {
  snippets: EnrichedSnippetDetails[];
  title: string;
  snippetPercentageWatched: number | null;
  perceivedDifficulty: number | null;
}

export interface VideoInfo {
  youtube_id: string;
  youtube_title: string | null;
}

export interface OnboardingVideoInfo extends VideoInfo {
  channel_name: string | null;
  video_views: number;
  video_likes: number;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface UserInfoResponse {
  email: string;
  id: number;
  subscription: {
    status: string | null;
    period_end?: number;
    cancel_at?: number;
    cancel_at_period_end?: boolean;
    error?: string;
  } | null;
}

export interface SubscriptionInfoResponse {
  subscription: {
    status: string | null;
    period_end?: number;
    cancel_at?: number;
    cancel_at_period_end?: boolean;
    error?: string;
  } | null;
} 