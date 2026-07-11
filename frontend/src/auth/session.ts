const SESSION_KEY = "hlr.session.v1";

export const session = {
  getToken(): string | null {
    return window.localStorage.getItem(SESSION_KEY);
  },
  setToken(token: string): void {
    window.localStorage.setItem(SESSION_KEY, token);
  },
  clear(): void {
    window.localStorage.removeItem(SESSION_KEY);
  },
};
