import type {CheckinResult, Habit, HabitInput, UserProfile} from "../types";


export type TokenResponse = {
  access_token: string;
  token_type: string;
  expires_in: number;
};

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

const LOCAL_API_BASE_URL = `http://${window.location.hostname || "localhost"}:8000`;
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? LOCAL_API_BASE_URL;

export function register(username: string, password: string): Promise<TokenResponse> {
  return request("/api/v1/auth/register", null, {
    method: "POST",
    body: JSON.stringify({username, password}),
  });
}

export function login(username: string, password: string): Promise<TokenResponse> {
  return request("/api/v1/auth/login", null, {
    method: "POST",
    body: JSON.stringify({username, password}),
  });
}

export function getProfile(token: string): Promise<UserProfile> {
  return request("/api/v1/user/profile", token);
}

export function listHabits(token: string): Promise<Habit[]> {
  return request("/api/v1/habits", token);
}

export function createHabit(token: string, input: HabitInput): Promise<Habit> {
  return request("/api/v1/habits", token, {method: "POST", body: JSON.stringify(input)});
}

export function updateHabit(token: string, habitId: number, input: HabitInput): Promise<Habit> {
  return request(`/api/v1/habits/${habitId}`, token, {
    method: "PATCH",
    body: JSON.stringify(input),
  });
}

export function archiveHabit(token: string, habitId: number): Promise<void> {
  return request(`/api/v1/habits/${habitId}`, token, {method: "DELETE"});
}

export function checkInHabit(token: string, habitId: number): Promise<CheckinResult> {
  return request(`/api/v1/habits/${habitId}/checkins`, token, {method: "POST"});
}

async function request<T>(path: string, token: string | null, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  headers.set("Accept", "application/json");
  if (init.body) {
    headers.set("Content-Type", "application/json");
  }
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {...init, headers});
  if (!response.ok) {
    throw new ApiError(response.status, await errorMessage(response));
  }
  if (response.status === 204) {
    return undefined as T;
  }
  return response.json() as Promise<T>;
}

async function errorMessage(response: Response): Promise<string> {
  try {
    const body = (await response.json()) as {detail?: string | Array<{msg?: string}>};
    if (typeof body.detail === "string") {
      return body.detail;
    }
    if (Array.isArray(body.detail)) {
      return body.detail.map((item) => item.msg).filter(Boolean).join(" ") || "資料格式不正確。";
    }
  } catch {
    // The status fallback below is more useful than a JSON parsing error.
  }
  return `Request failed with ${response.status}`;
}
