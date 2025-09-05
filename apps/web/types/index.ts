// API Response types
export interface ApiResponse<T = any> {
  data: T;
  message?: string;
  success: boolean;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}

// Auth types
export interface User {
  id: string;
  email: string;
  username?: string;
  first_name?: string;
  last_name?: string;
  avatar_url?: string;
  is_verified: boolean;
  created_at: string;
  updated_at: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: 'bearer';
  expires_in: number;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  username?: string;
  first_name?: string;
  last_name?: string;
}

// Album types
export interface Album {
  id: string;
  title: string;
  description?: string;
  is_public: boolean;
  cover_image_url?: string;
  owner_id: string;
  created_at: string;
  updated_at: string;
  pages_count: number;
  views_count: number;
}

export interface CreateAlbumRequest {
  title: string;
  description?: string;
  is_public?: boolean;
}

export interface UpdateAlbumRequest {
  title?: string;
  description?: string;
  is_public?: boolean;
}

// Page types
export interface Page {
  id: string;
  album_id: string;
  title: string;
  page_number: number;
  visibility: 'public' | 'link_only' | 'pin_protected';
  pin?: string;
  description?: string;
  created_at: string;
  updated_at: string;
  media_count: number;
  views_count: number;
}

export interface CreatePageRequest {
  title: string;
  page_number: number;
  visibility: 'public' | 'link_only' | 'pin_protected';
  pin?: string;
  description?: string;
}

export interface UpdatePageRequest {
  title?: string;
  visibility?: 'public' | 'link_only' | 'pin_protected';
  pin?: string;
  description?: string;
}

// Media types
export interface Media {
  id: string;
  page_id: string;
  filename: string;
  original_filename: string;
  file_type: 'image' | 'video' | 'audio';
  mime_type: string;
  file_size: number;
  width?: number;
  height?: number;
  duration?: number;
  url: string;
  thumbnail_url?: string;
  created_at: string;
  updated_at: string;
}

export interface UploadProgress {
  file: File;
  progress: number;
  status: 'uploading' | 'processing' | 'completed' | 'error';
  error?: string;
}

// QR types
export interface QRCode {
  id: string;
  page_id: string;
  album_id: string;
  short_url: string;
  qr_image_url: string;
  custom_url?: string;
  created_at: string;
  updated_at: string;
}

export interface GenerateQRRequest {
  page_id: string;
  album_id: string;
  custom_url?: string;
}

// Print types
export interface PrintJob {
  id: string;
  user_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  template_id: string;
  qr_codes: string[];
  pdf_url?: string;
  error_message?: string;
  created_at: string;
  updated_at: string;
}

export interface CreatePrintJobRequest {
  template_id: string;
  qr_codes: string[];
  label_size: '35mm' | '50mm';
  grid_size: string; // e.g., "5x10", "4x8"
  margin: number;
  bleed: number;
}

export interface PrintTemplate {
  id: string;
  name: string;
  label_size: '35mm' | '50mm';
  grid_size: string;
  margin: number;
  bleed: number;
  is_default: boolean;
}

// Analytics types
export interface AnalyticsOverview {
  total_albums: number;
  total_pages: number;
  total_views: number;
  total_qr_scans: number;
  total_media_uploads: number;
  storage_used: number;
  storage_limit: number;
}

export interface AlbumAnalytics {
  album_id: string;
  views_count: number;
  unique_visitors: number;
  qr_scans: number;
  pages_views: Array<{
    page_id: string;
    views: number;
    unique_visitors: number;
  }>;
  daily_views: Array<{
    date: string;
    views: number;
  }>;
}

export interface AnalyticsPeriod {
  start_date: string;
  end_date: string;
  views_count: number;
  unique_visitors: number;
  qr_scans: number;
  daily_breakdown: Array<{
    date: string;
    views: number;
    unique_visitors: number;
    qr_scans: number;
  }>;
}

// Billing types
export interface BillingPlan {
  id: string;
  name: string;
  description: string;
  price: number;
  currency: 'RUB' | 'USD' | 'EUR';
  interval: 'month' | 'year';
  features: string[];
  limits: {
    albums: number;
    pages_per_album: number;
    media_uploads: number;
    storage_gb: number;
    qr_codes: number;
  };
  is_popular: boolean;
  is_current: boolean;
}

export interface BillingLimits {
  albums: {
    used: number;
    limit: number;
  };
  pages_per_album: {
    used: number;
    limit: number;
  };
  media_uploads: {
    used: number;
    limit: number;
  };
  storage_gb: {
    used: number;
    limit: number;
  };
  qr_codes: {
    used: number;
    limit: number;
  };
}

// Notification types
export interface Notification {
  id: string;
  user_id: string;
  type: 'info' | 'warning' | 'error' | 'success';
  title: string;
  message: string;
  is_read: boolean;
  action_url?: string;
  action_text?: string;
  created_at: string;
}

// Moderation types
export interface ModerationRequest {
  id: string;
  content_type: 'album' | 'page' | 'media';
  content_id: string;
  status: 'pending' | 'approved' | 'rejected';
  reason?: string;
  moderator_notes?: string;
  created_at: string;
  updated_at: string;
}

// Error types
export interface ApiError {
  message: string;
  code?: string;
  details?: Record<string, any>;
  status: number;
}

// Form types
export interface FormState {
  isSubmitting: boolean;
  errors: Record<string, string[]>;
  success?: boolean;
}

// UI types
export interface Toast {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  description?: string;
  duration?: number;
}

export interface Modal {
  id: string;
  component: React.ComponentType<any>;
  props?: Record<string, any>;
  onClose?: () => void;
}

// Theme types
export type Theme = 'light' | 'dark' | 'system';

// Language types
export type Language = 'ru' | 'en';

// File upload types
export interface FileUploadConfig {
  maxSize: number; // in bytes
  allowedTypes: string[];
  multiple: boolean;
}

// Search and filter types
export interface SearchFilters {
  query?: string;
  is_public?: boolean;
  date_from?: string;
  date_to?: string;
  sort_by?: 'created_at' | 'updated_at' | 'title' | 'views_count';
  sort_order?: 'asc' | 'desc';
}

export interface PaginationParams {
  page: number;
  limit: number;
}

// Public page types
export interface PublicPageData {
  page: Page;
  album: Album;
  media: Media[];
  qr_code?: QRCode;
}

export interface PinValidationRequest {
  page_id: string;
  pin: string;
}

export interface PinValidationResponse {
  valid: boolean;
  access_token?: string;
  expires_at?: string;
}
