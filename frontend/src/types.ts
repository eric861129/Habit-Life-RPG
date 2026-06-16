export type UserProfile = {
  id: number;
  username: string;
  level: number;
  exp: number;
  gold: number;
  hp: number;
};

export type Habit = {
  id: number;
  title: string;
  category: string | null;
  last_check_in: string | null;
  checked_in_today: boolean;
};

export type NoticeKind = "success" | "error" | "level";

export type Notice = {
  kind: NoticeKind;
  title: string;
  message: string;
};
