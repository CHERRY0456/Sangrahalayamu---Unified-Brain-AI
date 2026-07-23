import { setCookie, eraseCookie } from '@/lib/cookies';
import { SESSION_TOKEN_KEY } from '@/lib/constants';
import { WorkspaceManifest, EmployeeProfile } from '@/lib/types';

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface LoginResponse {
  profile: EmployeeProfile;
  permissions: string[];
  manifest: WorkspaceManifest;
}

export class AuthService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  }

  /**
   * Authenticates credentials against the FastAPI backend.
   * On success: stores JWT tokens in localStorage, sets session cookie for middleware.
   * Returns the user's full profile, permissions, and workspace manifest.
   */
  public async login(email: string, password: string): Promise<LoginResponse> {
    // Step 1: Authenticate and receive JWT tokens
    const tokenRes = await fetch(`${this.baseUrl}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });

    if (!tokenRes.ok) {
      const err = await tokenRes.json().catch(() => ({ detail: 'Login failed.' }));
      throw new Error(err.detail || `Login failed with status ${tokenRes.status}`);
    }

    const tokens: TokenResponse = await tokenRes.json();

    // Step 2: Store tokens for all subsequent API calls
    localStorage.setItem('ib-access-token', tokens.access_token);
    localStorage.setItem('ib-refresh-token', tokens.refresh_token);

    // Step 3: Set session cookie so Next.js middleware allows access to protected routes
    // We store a marker value (not the raw JWT) as the cookie is only used for route gating
    setCookie(SESSION_TOKEN_KEY, 'authenticated', 7);

    // Step 4: Fetch full user profile + workspace manifest
    const meRes = await fetch(`${this.baseUrl}/api/auth/me`, {
      headers: {
        'Authorization': `Bearer ${tokens.access_token}`,
        'Content-Type': 'application/json',
      },
    });

    if (!meRes.ok) {
      throw new Error('Failed to load user profile after login.');
    }

    const meData = await meRes.json();

    return {
      profile: meData.profile as EmployeeProfile,
      permissions: meData.permissions as string[],
      manifest: meData.manifest as WorkspaceManifest,
    };
  }

  /**
   * Logs out the user by revoking the refresh token on the backend
   * and clearing all local auth state.
   */
  public async logout(): Promise<void> {
    const refreshToken = localStorage.getItem('ib-refresh-token');
    if (refreshToken) {
      try {
        await fetch(`${this.baseUrl}/api/auth/logout`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ refresh_token: refreshToken }),
        });
      } catch {
        // Best-effort logout — clear local state regardless
      }
    }
    localStorage.removeItem('ib-access-token');
    localStorage.removeItem('ib-refresh-token');
    eraseCookie(SESSION_TOKEN_KEY);
  }

  /**
   * Refreshes the current user's profile from the backend (e.g., on page reload).
   */
  public async getMe(): Promise<LoginResponse | null> {
    const accessToken = localStorage.getItem('ib-access-token');
    if (!accessToken) return null;

    const meRes = await fetch(`${this.baseUrl}/api/auth/me`, {
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json',
      },
    });

    if (!meRes.ok) return null;

    const meData = await meRes.json();
    return {
      profile: meData.profile as EmployeeProfile,
      permissions: meData.permissions as string[],
      manifest: meData.manifest as WorkspaceManifest,
    };
  }
}

export const authService = new AuthService();
export default authService;
