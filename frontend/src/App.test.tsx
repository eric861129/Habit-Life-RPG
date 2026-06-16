import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import App from "./App";

const profileResponse = {
  id: 1,
  username: "arthur",
  level: 2,
  exp: 120,
  gold: 35,
  hp: 86,
};

const habitsResponse = [
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

beforeEach(() => {
  vi.restoreAllMocks();
  vi.spyOn(globalThis, "fetch")
    .mockResolvedValueOnce(jsonResponse(profileResponse))
    .mockResolvedValueOnce(jsonResponse(habitsResponse));
});

describe("App foundation", () => {
  it("loads the Habit Life RPG shell from the API", async () => {
    render(<App />);

    expect(screen.getByRole("heading", { name: "Habit Life RPG" })).toBeInTheDocument();
    expect(await screen.findByRole("heading", { name: "Quest Log" })).toBeInTheDocument();
    expect(await screen.findByText("晨間 20 分鐘閱讀")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "打卡領獎" })).toBeInTheDocument();
  });
});

function jsonResponse(body: unknown, init: ResponseInit = {}) {
  return new Response(JSON.stringify(body), {
    status: 200,
    headers: { "Content-Type": "application/json" },
    ...init,
  });
}
