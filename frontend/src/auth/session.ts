const SESSION_KEY = "hlr.session.v2";
const LEGACY_SESSION_KEY = "hlr.session.v1";

export type StoredSession = {
  token: string;
  expiresAt: number;
};

export type RestoredSession = {
  token: string | null;
  expired: boolean;
};

export const session = {
  restore(now = Date.now()): RestoredSession {
    window.localStorage.removeItem(LEGACY_SESSION_KEY);
    const raw = window.sessionStorage.getItem(SESSION_KEY);
    if (raw === null) {
      return {token: null, expired: false};
    }

    try {
      const stored = JSON.parse(raw) as Partial<StoredSession>;
      if (
        typeof stored.token !== "string" ||
        stored.token.length === 0 ||
        typeof stored.expiresAt !== "number" ||
        !Number.isFinite(stored.expiresAt)
      ) {
        this.clear();
        return {token: null, expired: false};
      }
      if (stored.expiresAt <= now) {
        this.clear();
        return {token: null, expired: true};
      }
      return {token: stored.token, expired: false};
    } catch {
      this.clear();
      return {token: null, expired: false};
    }
  },

  set(token: string, expiresInSeconds: number, now = Date.now()): void {
    const stored: StoredSession = {
      token,
      expiresAt: now + expiresInSeconds * 1000,
    };
    window.localStorage.removeItem(LEGACY_SESSION_KEY);
    window.sessionStorage.setItem(SESSION_KEY, JSON.stringify(stored));
  },

  clear(): void {
    window.localStorage.removeItem(LEGACY_SESSION_KEY);
    window.sessionStorage.removeItem(SESSION_KEY);
  },
};
