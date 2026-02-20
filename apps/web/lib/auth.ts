import Cookies from 'js-cookie';
import { AuthTokens, User } from '@/types';

type AuthState = {
  isAuthenticated: boolean;
  user: User | null;
};

const ACCESS = 'storyqr_access_token';
const REFRESH = 'storyqr_refresh_token';
const USER = 'storyqr_user';

class AuthManager {
  private listeners = new Set<() => void>();

  login(tokens: AuthTokens, user?: User | null) {
    this.setTokens(tokens);
    if (user) {
      localStorage.setItem(USER, JSON.stringify(user));
    }
    this.notify();
  }

  logout() {
    Cookies.remove(ACCESS);
    Cookies.remove(REFRESH);
    localStorage.removeItem(USER);
    this.notify();
  }

  getAccessToken() {
    return Cookies.get(ACCESS) || null;
  }

  setTokens(tokens: Pick<AuthTokens, 'access_token' | 'refresh_token'>) {
    const cookieOpts = { sameSite: 'lax' as const, secure: typeof window !== 'undefined' && window.location.protocol === 'https:' };
    Cookies.set(ACCESS, tokens.access_token, { ...cookieOpts, expires: 1 / 24 });
    Cookies.set(REFRESH, tokens.refresh_token, { ...cookieOpts, expires: 7 });
  }

  getTokens() {
    const access_token = Cookies.get(ACCESS);
    const refresh_token = Cookies.get(REFRESH);
    if (!access_token || !refresh_token) return null;
    return { access_token, refresh_token };
  }

  getUser(): User | null {
    try {
      const value = localStorage.getItem(USER);
      return value ? (JSON.parse(value) as User) : null;
    } catch {
      return null;
    }
  }

  getAuthState(): AuthState {
    const access = this.getAccessToken();
    return {
      isAuthenticated: Boolean(access),
      user: this.getUser(),
    };
  }

  subscribe(listener: () => void) {
    this.listeners.add(listener);
    return () => {
      this.listeners.delete(listener);
    };
  }

  private notify() {
    this.listeners.forEach((listener) => listener());
  }
}

export const authManager = new AuthManager();
export const auth = authManager;
