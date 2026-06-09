export * from "./api";

import type { ContactLinkId } from "@/constants/contactMeta";

export interface UserResponse {
  id: string;
  email: string;
  is_verified: boolean;
  permissions: string[];
  display_name: string | null;
  timezone: string;
  preferences: Record<string, unknown>;
  created_at: string;
}

export interface UserPreferences {
  display_currency: string | null;
}

export interface AdminUserSummary {
  id: string;
  email: string;
  display_name: string | null;
  is_verified: boolean;
  is_protected: boolean;
  permissions: string[];
  created_at: string;
}

export interface GitHubStatus {
  linked: boolean;
  github_username: string | null;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface ResumeData {
  name: string;
  title: string;
  tagline?: string;
  location?: string;
  availability?: string;
  bio: string;
  skills: SkillGroup[];
  experience: Experience[];
  projects: Project[];
  education?: Education[];
  links: Partial<Record<ContactLinkId, string>>;
}

export interface SkillGroup {
  category: string;
  items: string[];
}

export interface Experience {
  role: string;
  company: string;
  period: string;
  description: string;
  highlights?: string[];
}

export interface Education {
  degree: string;
  institution: string;
  period: string;
  description?: string;
}

export interface Project {
  name: string;
  description: string;
  tech: string[];
  url: string;
}

export interface DonationsConfig {
  stripe: { enabled: boolean; url: string };
  telegram: { enabled: boolean; url: string };
  crypto: { btc: string; eth: string };
}

export interface SpotifyNowPlaying {
  enabled: boolean;
  is_playing: boolean;
  title?: string;
  artist?: string;
  album?: string;
  album_art_url?: string;
  track_url?: string;
  progress_ms?: number;
  duration_ms?: number;
  error?: string;
}

export interface UrlItem {
  id: number;
  code: string;
  original_url: string;
  title: string | null;
  clicks: number;
  created_at: string;
}

export interface WeatherLocation {
  id: number;
  label: string;
  query: string;
  sort_order: number;
}

export interface WeatherConfig {
  label: string;
  query: string;
}

export interface WeatherData {
  current_condition: Array<{
    temp_C: string;
    weatherDesc: Array<{ value: string }>;
    humidity: string;
    windspeedKmph: string;
    localObsDateTime?: string;
  }>;
  nearest_area: Array<{
    areaName: Array<{ value: string }>;
    country: Array<{ value: string }>;
    latitude?: string;
    longitude?: string;
  }>;
  time_zone?: Array<{
    utcOffset: string;
    timezone?: string;
    datetime?: string;
    utc_datetime?: string;
    unixtime?: number;
    dst?: boolean;
    abbreviation?: string;
  }>;
}

export interface SharedFile {
  id: number;
  code: string;
  original_filename: string;
  file_size: number;
  content_type: string;
  downloads: number;
  expires_at: string;
  created_at: string;
}

export interface Toast {
  id: number;
  message: string;
  type: "success" | "error" | "info";
}

export interface TaskItem {
  id: number;
  telegram_user_id: number;
  title: string;
  description: string | null;
  location: string | null;
  scheduled_at: string;
  status: string;
  google_event_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface TaskReminder {
  id: number;
  task_id: number;
  remind_at: string;
  sent: boolean;
  job_id: string | null;
  created_at: string;
}

export interface TaskStatusChange {
  id: number;
  task_id: number;
  old_status: string;
  new_status: string;
  changed_at: string;
}

export interface TaskDetail extends TaskItem {
  reminders: TaskReminder[];
  status_history: TaskStatusChange[];
}

export interface SyncQueueItem {
  id: number;
  task_id: number;
  action: string;
  attempts: number;
  last_error: string | null;
  next_retry_at: string | null;
  status: string;
  created_at: string;
}

export interface TaskStats {
  pending: number;
  completed: number;
  total: number;
  failed_syncs: number;
}

export interface TaskIntakeItem {
  id: number;
  status: string;
  draft_json: Record<string, unknown> | null;
  confidence_json: Record<string, unknown> | null;
  clarification_turns_json: Array<Record<string, string>> | null;
  clarification_rounds: number;
  task_id: number | null;
  inbound_text: string | null;
  created_at: string;
  updated_at: string;
}

export interface Recipe {
  id: number;
  title: string;
  ingredients: string[];
  steps: string[];
  notes: string | null;
  tags: string[];
  image_url: string | null;
  prep_time: number | null;
  cook_time: number | null;
  servings: number | null;
  created_at: string;
  updated_at: string;
}

export type RecipeSort =
  | "updated_desc"
  | "title_asc"
  | "title_desc"
  | "prep_asc"
  | "total_time_asc";

export interface PaginatedRecipes {
  items: Recipe[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
}

export interface ExpenseCategory {
  id: number;
  name: string;
  sort_order: number;
  monthly_budget: string | null;
  created_at: string;
  updated_at: string;
}

export interface ExpenseParseResult {
  valid: boolean;
  amount?: string;
  currency?: string;
  category?: string;
  tool_name?: string;
  expense_date?: string;
  error?: string;
}

export interface ToolExpense {
  id: number;
  tool_name: string;
  amount: string;
  currency: string;
  expense_date: string;
  category: string | null;
  notes: string | null;
  source: string;
  created_at: string;
  updated_at: string;
}

export interface ToolExpenseMonthTotal {
  period: string;
  total: string;
}

export interface ToolExpenseToolTotal {
  tool_name: string;
  total: string;
}

export interface ToolExpenseCategoryTotal {
  category: string;
  total: string;
}

export interface ToolExpenseSummary {
  total: string;
  currency: string;
  rates_updated_at: string | null;
  by_month: ToolExpenseMonthTotal[];
  by_tool: ToolExpenseToolTotal[];
  by_category: ToolExpenseCategoryTotal[];
}

export interface ExchangeRates {
  base: string;
  rates: Record<string, string>;
  updated_at: string | null;
  provider: string;
}
