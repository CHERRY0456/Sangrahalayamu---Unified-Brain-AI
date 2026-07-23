import { getCookie } from './cookies';
import { SESSION_TOKEN_KEY } from './constants';
import { eraseCookie } from './cookies';

export class ApiClient {
  private baseUrl: string;
  private defaultTimeout: number;
  private isRefreshing: boolean = false;

  constructor() {
    this.baseUrl = process.env.NEXT_PUBLIC_API_URL || '';
    this.defaultTimeout = 10000;
  }

  /**
   * Helper to perform request with timeout, JWT Auth injection, and automatic retry hooks
   */
  private async request<T>(path: string, options: RequestInit = {}, timeoutMs = this.defaultTimeout): Promise<T> {
    const url = `${this.baseUrl}${path}`;
    
    // 1. Setup Abort Controller for Request Timeout
    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), timeoutMs);

    // 2. Resolve JWT access token from localStorage
    const accessToken = typeof window !== 'undefined' ? localStorage.getItem('ib-access-token') : null;
    const authHeaders: Record<string, string> = {};
    if (accessToken) {
      authHeaders['Authorization'] = `Bearer ${accessToken}`;
    }

    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...authHeaders,
      ...(options.headers as Record<string, string> || {}),
    };

    try {
      const response = await fetch(url, {
        ...options,
        headers,
        signal: controller.signal,
      });

      clearTimeout(id);

      // 3. Automatic Token Refresh Handler (JWT 401 fallback)
      if (response.status === 401 && !this.isRefreshing) {
        const refreshed = await this.handleTokenRefresh();
        if (refreshed) {
          // Re-trigger the request once with fresh token
          return this.request<T>(path, options, timeoutMs);
        } else {
          // Refresh failed — clear session and redirect to login
          if (typeof window !== 'undefined') {
            localStorage.removeItem('ib-access-token');
            localStorage.removeItem('ib-refresh-token');
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
   * On success, writes new tokens to localStorage and returns true.
   */
  private async handleTokenRefresh(): Promise<boolean> {
    this.isRefreshing = true;
    try {
      const refreshToken = typeof window !== 'undefined' ? localStorage.getItem('ib-refresh-token') : null;
      if (!refreshToken) return false;

      const res = await fetch(`${this.baseUrl}/api/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });

      if (!res.ok) return false;

      const tokens = await res.json();
      localStorage.setItem('ib-access-token', tokens.access_token);
      localStorage.setItem('ib-refresh-token', tokens.refresh_token);
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
export default apiClient;
