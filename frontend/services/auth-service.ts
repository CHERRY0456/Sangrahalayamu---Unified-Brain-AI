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
    // Step 1: Authenticate and receive HttpOnly cookies
    const tokenRes = await fetch(`${this.baseUrl}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
      credentials: 'include',
    });

    if (!tokenRes.ok) {
      const err = await tokenRes.json().catch(() => ({ detail: 'Login failed.' }));
      throw new Error(err.detail || `Login failed with status ${tokenRes.status}`);
    }

    // Step 2: Fetch full user profile + workspace manifest
    const meRes = await fetch(`${this.baseUrl}/api/auth/me`, {
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
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
    try {
      await fetch(`${this.baseUrl}/api/auth/logout`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
      });
    } catch {
      // Best-effort logout — clear local state regardless
    }
    eraseCookie(SESSION_TOKEN_KEY);
  }

  /**
   * Refreshes the current user's profile from the backend (e.g., on page reload).
   */
  public async getMe(): Promise<LoginResponse | null> {
    const meRes = await fetch(`${this.baseUrl}/api/auth/me`, {
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
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
