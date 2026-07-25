import { getCookie } from './cookies';
import { SESSION_TOKEN_KEY } from './constants';
import { eraseCookie } from './cookies';

export class ApiClient {
  private baseUrl: string;
  private defaultTimeout: number;
  private isRefreshing: boolean = false;

  constructor() {
    this.baseUrl = process.env.NEXT_PUBLIC_API_URL || '';
    this.defaultTimeout = 300000; // 300 seconds (5 minutes) for enterprise file uploads & parsing
  }

  /**
   * Helper to perform request with timeout, JWT Auth injection, and automatic retry hooks
   */
  private async request<T>(path: string, options: RequestInit = {}, timeoutMs = this.defaultTimeout): Promise<T> {
    const url = `${this.baseUrl}${path}`;
    
    // 1. Setup Abort Controller for Request Timeout
    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), timeoutMs);

    const headers: Record<string, string> = {
      ...(options.headers as Record<string, string> || {}),
    };

    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('ib-access-token') || localStorage.getItem('session_token');
      if (token && !headers['Authorization']) {
        headers['Authorization'] = `Bearer ${token}`;
      }
    }

    // Auto-set JSON content type only if body is not FormData
    if (options.body && !(options.body instanceof FormData) && !headers['Content-Type']) {
      headers['Content-Type'] = 'application/json';
    } else if (!options.body && !headers['Content-Type']) {
      headers['Content-Type'] = 'application/json';
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers,
        credentials: 'include',
        signal: controller.signal,
      });

      clearTimeout(id);

      // 3. Automatic Token Refresh Handler (JWT 401 fallback)
      if (response.status === 401 && !this.isRefreshing) {
        const refreshed = await this.handleTokenRefresh();
        if (refreshed) {
          // Re-trigger the request once with fresh cookie
          return this.request<T>(path, options, timeoutMs);
        } else {
          // Refresh failed — clear session and redirect to login
          if (typeof window !== 'undefined') {
            eraseCookie(SESSION_TOKEN_KEY);
            window.location.href = '/login';
          }
          throw new Error('Session expired. Please log in again.');
        }
      }

      // 4. Centralized Error Handler
      if (!response.ok) {
        const errorText = await response.text().catch(() => 'Connection failure');
        throw new Error(`API Error [${response.status}]: ${errorText}`);
      }

      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        return response.json() as Promise<T>;
      }
      return response.text() as unknown as T;

    } catch (error: any) {
      clearTimeout(id);
      if (error.name === 'AbortError') {
        throw new Error(`Request Timeout: Connection exceeded limit of ${timeoutMs}ms.`);
      }
      throw error;
    }
  }

  /**
   * Performs JWT token refresh against POST /api/auth/refresh.
   * On success, backend rotates HttpOnly cookies.
   */
  private async handleTokenRefresh(): Promise<boolean> {
    this.isRefreshing = true;
    try {
      const res = await fetch(`${this.baseUrl}/api/v1/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
      });

      if (!res.ok) return false;
      return true;
    } catch (e) {
      console.error('Token refresh failed:', e);
      return false;
    } finally {
      this.isRefreshing = false;
    }
  }

  public async get<T>(path: string, options?: RequestInit, timeout?: number): Promise<T> {
    return this.request<T>(path, { ...options, method: 'GET' }, timeout);
  }

  public async post<T>(path: string, body: any, options?: RequestInit, timeout?: number): Promise<T> {
    const isFormData = body instanceof FormData;
    return this.request<T>(
      path,
      {
        ...options,
        method: 'POST',
        body: isFormData ? body : JSON.stringify(body),
        headers: isFormData ? { ...options?.headers } : { 'Content-Type': 'application/json', ...options?.headers },
      },
      timeout
    );
  }
}

export const apiClient = new ApiClient();
export const api = apiClient;
export default apiClient;
