export type UserProfile = {
  id: number;
  username: string;
  level: number;
  exp: number;
  gold: number;
};

export type HabitPriority = "high" | "medium" | "low";

export type Habit = {
  id: number;
  title: string;
  description: string | null;
  category: string | null;
  priority: HabitPriority;
  is_archived: boolean;
  streak_count: number;
  last_checkin_date: string | null;
  checked_in_today: boolean;
};

export type HabitInput = {
  title: string;
  description: string | null;
  category: string | null;
  priority: HabitPriority;
};

export type CheckinResult = {
  id: number;
  habit_id: number;
  checkin_date: string;
  checked_in_at: string;
  exp_earned: number;
  gold_earned: number;
  streak_count: number;
  current_exp: number;
  current_gold: number;
  current_level: number;
  leveled_up: boolean;
};

export type Notice = {
  kind: "success" | "error" | "level";
  title: string;
  message: string;
};
