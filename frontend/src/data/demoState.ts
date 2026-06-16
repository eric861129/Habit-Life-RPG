import type { Habit, Notice, UserProfile } from "../types";

export const demoProfile: UserProfile = {
  id: 1,
  username: "arthur",
  level: 2,
  exp: 120,
  gold: 35,
  hp: 86,
};

export const demoHabits: Habit[] = [
  {
    id: 1,
    title: "晨間 20 分鐘閱讀",
    category: "Mind",
    last_check_in: null,
    checked_in_today: false,
  },
  {
    id: 2,
    title: "喝水 2000 ml",
    category: "Body",
    last_check_in: "2026-06-16T08:10:00+08:00",
    checked_in_today: true,
  },
];

export const demoNotice: Notice = {
  kind: "success",
  title: "Quest reward claimed",
  message: "+40 EXP / +8 gold. Keep the guild ledger shining.",
};
