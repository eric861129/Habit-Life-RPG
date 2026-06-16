import type { Habit, UserProfile } from "../types";

export type HabitCheckinResponse = {
  habit_id: number;
  checked_in: boolean;
  current_exp: number;
  current_gold: number;
  current_level: number;
  leveled_up: boolean;
};

export class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";
const DEV_AUTH_TOKEN = import.meta.env.VITE_DEV_AUTH_TOKEN ?? "local-dev-token";

export async function getUserProfile(): Promise<UserProfile> {
  return request<UserProfile>("/api/v1/user/profile");
}

export async function getHabits(): Promise<Habit[]> {
  return request<Habit[]>("/api/v1/habits");
}

export async function checkInHabit(habitId: number): Promise<HabitCheckinResponse> {
  return request<HabitCheckinResponse>(`/api/v1/habits/${habitId}/checkin`, {
    method: "POST",
  });
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      Accept: "application/json",
      Authorization: `Bearer ${DEV_AUTH_TOKEN}`,
      ...init.headers,
    },
  });

  if (!response.ok) {
    throw new ApiError(response.status, await readErrorMessage(response));
  }

  return response.json() as Promise<T>;
}

async function readErrorMessage(response: Response): Promise<string> {
  try {
    const body = (await response.json()) as { detail?: string };
    return body.detail ?? `Request failed with ${response.status}`;
  } catch {
    return `Request failed with ${response.status}`;
  }
}
