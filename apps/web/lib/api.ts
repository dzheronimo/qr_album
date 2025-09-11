import { endpoints } from './endpoints';
import { auth } from './auth';
import { ApiError, ApiResponse } from '@/types';

// Функция для получения сообщений об ошибках по умолчанию
function getDefaultErrorMessage(status: number): string {
  switch (status) {
    case 400:
      return 'Некорректный запрос';
    case 401:
      return 'Неверные данные авторизации';
    case 403:
      return 'Доступ запрещен';
    case 404:
      return 'Ресурс не найден';
    case 409:
      return 'Конфликт данных';
    case 422:
      return 'Ошибка валидации';
    case 429:
      return 'Слишком много запросов';
    case 500:
      return 'Внутренняя ошибка сервера';
    case 502:
      return 'Сервис временно недоступен';
    case 503:
      return 'Сервис временно недоступен';
    case 504:
      return 'Превышено время ожидания';
    default:
      return 'Произошла ошибка';
  }
}

// HTTP client configuration
const DEFAULT_TIMEOUT = 7000; // 7 seconds as per requirements
const MAX_RETRIES = 3;
const RETRY_DELAY = 1000; // 1 second

// Request configuration
interface RequestConfig extends RequestInit {
  timeout?: number;
  retries?: number;
  skipAuth?: boolean;
}

// API client class
class ApiClient {
  private baseURL: string;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
  }

  // Main request method
  private async request<T>(
    url: string,
    config: RequestConfig = {}
  ): Promise<ApiResponse<T>> {
    const {
      timeout = DEFAULT_TIMEOUT,
      retries = MAX_RETRIES,
      skipAuth = false,
      ...fetchConfig
    } = config;

    // Add authentication header if not skipped
    if (!skipAuth) {
      const token = auth.getAccessToken();
      if (token) {
        fetchConfig.headers = {
          ...fetchConfig.headers,
          Authorization: `Bearer ${token}`,
        };
      }
    }

    // Add default headers
    fetchConfig.headers = {
      'Content-Type': 'application/json',
      ...fetchConfig.headers,
    };

    // Create abort controller for timeout
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);

    try {
      const response = await fetch(url, {
        ...fetchConfig,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      // Handle different response statuses
      if (response.status === 401 && !skipAuth) {
        // Token expired, try to refresh (только если аутентификация обязательна)
        if (retries > 0) {
          const refreshed = await this.refreshToken();
          if (refreshed) {
            return this.request<T>(url, { ...config, retries: retries - 1 });
          }
        }
        // Если не удалось обновить токен — выходим из аккаунта и редиректим на логин
        auth.logout();
        if (typeof window !== 'undefined') {
          window.location.href = '/auth/login';
        }
        throw new ApiError('Unauthorized', 401);
      }

      if (response.status === 429) {
        // Rate limited, wait and retry
        if (retries > 0) {
          await this.delay(RETRY_DELAY * (MAX_RETRIES - retries + 1));
          return this.request<T>(url, { ...config, retries: retries - 1 });
        }
        throw new ApiError('Too many requests', 429);
      }

      if (response.status >= 500) {
        // Server error, retry if possible
        if (retries > 0) {
          await this.delay(RETRY_DELAY);
          return this.request<T>(url, { ...config, retries: retries - 1 });
        }
        throw new ApiError('Server error', response.status);
      }

      if (!response.ok) {
        let errorData: any = {};
        try {
          const text = await response.text();
          if (text) {
            errorData = JSON.parse(text);
          }
        } catch {
          // Если не удалось распарсить JSON, используем пустой объект
        }
        
        // Извлекаем сообщение об ошибке из стандартной структуры API
        const message = errorData?.error?.message || 
                       errorData?.message || 
                       errorData?.detail ||
                       getDefaultErrorMessage(response.status);
        
        throw new ApiError(
          message,
          response.status,
          errorData?.error?.code || errorData?.code
        );
      }

      // Приводим ответ к унифицированному виду ApiResponse<T>
      let parsed: any = null;
      try {
        parsed = await response.json();
      } catch {
        parsed = null;
      }

      if (parsed && typeof parsed === 'object' && 'success' in parsed && 'data' in parsed) {
        return parsed as ApiResponse<T>;
      }

      // Если бэкенд вернул «сырой» объект без success/data — оборачиваем
      return {
        success: true,
        data: parsed as T,
      } as ApiResponse<T>;
    } catch (error) {
      clearTimeout(timeoutId);
      
      if (error instanceof ApiError) {
        throw error;
      }

      if ((error as any).name === 'AbortError') {
        throw new ApiError('Request timeout', 408);
      }

      throw new ApiError(
        (error as any).message || 'Network error',
        0
      );
    }
  }

  // Refresh token
  private async refreshToken(): Promise<boolean> {
    try {
      const tokens = auth.getTokens();
      if (!tokens?.refresh_token) {
        return false;
      }

      const response = await fetch(endpoints.auth.refresh(), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          refresh_token: tokens.refresh_token,
        }),
      });

      if (response.ok) {
        const newTokens = await response.json();
        auth.setTokens(newTokens.data);
        return true;
      }

      return false;
    } catch {
      return false;
    }
  }

  // Utility method for delays
  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  // HTTP methods
  async get<T>(url: string, config?: RequestConfig): Promise<ApiResponse<T>> {
    return this.request<T>(url, { ...config, method: 'GET' });
  }

  async post<T>(
    url: string,
    data?: any,
    config?: RequestConfig
  ): Promise<ApiResponse<T>> {
    return this.request<T>(url, {
      ...config,
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async put<T>(
    url: string,
    data?: any,
    config?: RequestConfig
  ): Promise<ApiResponse<T>> {
    return this.request<T>(url, {
      ...config,
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async patch<T>(
    url: string,
    data?: any,
    config?: RequestConfig
  ): Promise<ApiResponse<T>> {
    return this.request<T>(url, {
      ...config,
      method: 'PATCH',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async delete<T>(url: string, config?: RequestConfig): Promise<ApiResponse<T>> {
    return this.request<T>(url, { ...config, method: 'DELETE' });
  }

  // File upload method
  async upload<T>(
    url: string,
    file: File,
    config?: RequestConfig
  ): Promise<ApiResponse<T>> {
    const formData = new FormData();
    formData.append('file', file);

    return this.request<T>(url, {
      ...config,
      method: 'POST',
      body: formData,
      headers: {
        // Don't set Content-Type for FormData, let browser set it with boundary
        ...config?.headers,
        ...(config?.skipAuth ? {} : { Authorization: `Bearer ${auth.getAccessToken()}` }),
      },
    });
  }

  // Multipart upload with progress
  async uploadWithProgress<T>(
    url: string,
    file: File,
    onProgress?: (progress: number) => void,
    config?: RequestConfig
  ): Promise<ApiResponse<T>> {
    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();
      
      // Track upload progress
      xhr.upload.addEventListener('progress', (event) => {
        if (event.lengthComputable && onProgress) {
          const progress = (event.loaded / event.total) * 100;
          onProgress(progress);
        }
      });

      // Handle response
      xhr.addEventListener('load', () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          try {
            const data = JSON.parse(xhr.responseText);
            resolve(data);
          } catch (error) {
            reject(new ApiError('Invalid response format', xhr.status));
          }
        } else {
          reject(new ApiError('Upload failed', xhr.status));
        }
      });

      xhr.addEventListener('error', () => {
        reject(new ApiError('Network error', 0));
      });

      xhr.addEventListener('abort', () => {
        reject(new ApiError('Upload cancelled', 0));
      });

      // Setup request
      xhr.open('POST', url);
      
      // Add auth header
      const token = auth.getAccessToken();
      if (token && !config?.skipAuth) {
        xhr.setRequestHeader('Authorization', `Bearer ${token}`);
      }

      // Add other headers
      if (config?.headers) {
        Object.entries(config.headers).forEach(([key, value]) => {
          xhr.setRequestHeader(key, value as string);
        });
      }

      // Send file
      const formData = new FormData();
      formData.append('file', file);
      xhr.send(formData);
    });
  }
}

// Normalize base URL to avoid accidental 8000 port and trailing slashes in runtime
function normalizeBaseUrl(rawBaseUrl: string | undefined): string {
  const fallback = 'http://localhost:8080';
  if (!rawBaseUrl) {
    return fallback;
  }
  try {
    const parsed = new URL(rawBaseUrl);
    // Only change port for localhost, not for Docker internal URLs
    if (parsed.hostname === 'localhost' && parsed.port === '8000') {
      parsed.port = '8080';
    }
    const normalized = parsed.toString().replace(/\/$/, '');
    return normalized;
  } catch {
    // Only replace localhost:8000 with localhost:8080, not Docker URLs
    if (rawBaseUrl.includes('localhost:8000')) {
      return rawBaseUrl.replace('localhost:8000', 'localhost:8080').replace(/\/$/, '') || fallback;
    }
    return rawBaseUrl.replace(/\/$/, '') || fallback;
  }
}

// Create API client instance with debug logging
const rawBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL;
const normalizedBaseUrl = normalizeBaseUrl(rawBaseUrl);
const finalBaseUrl = normalizedBaseUrl + '/api/v1';

console.log('DEBUG: NEXT_PUBLIC_API_BASE_URL (raw):', rawBaseUrl);
console.log('DEBUG: Normalized Base URL:', normalizedBaseUrl);
console.log('DEBUG: Final API Client Base URL:', finalBaseUrl);

export const apiClient = new ApiClient(finalBaseUrl);

// Export endpoints for convenience
export { endpoints };

// Health check
export const healthCheck = async (): Promise<boolean> => {
  try {
    const response = await apiClient.get(endpoints.health(), { skipAuth: true });
    return response.success;
  } catch {
    return false;
  }
};
