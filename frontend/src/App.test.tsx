import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import App from "./App";


const profile = {id: 1, username: "Reader", level: 1, exp: 0, gold: 0};
const habit = {
  id: 7,
  title: "閱讀 20 分鐘",
  description: "睡前閱讀",
  category: "學習",
  is_archived: false,
  streak_count: 2,
  last_checkin_date: null,
  checked_in_today: false,
};


beforeEach(() => {
  vi.restoreAllMocks();
  window.localStorage.clear();
});


describe("Habit Life RPG reader workflow", () => {
  it("registers a reader and opens an empty dashboard", async () => {
    const user = userEvent.setup();
    const fetchMock = vi
      .spyOn(globalThis, "fetch")
      .mockResolvedValueOnce(jsonResponse({access_token: "reader-token", token_type: "bearer"}, 201))
      .mockResolvedValueOnce(jsonResponse(profile))
      .mockResolvedValueOnce(jsonResponse([]));

    render(<App />);
    await user.click(screen.getByRole("tab", {name: "註冊"}));
    await user.type(screen.getByLabelText("使用者名稱"), "Reader");
    await user.type(screen.getByLabelText("密碼"), "BookDemo!2026");
    await user.click(screen.getByRole("button", {name: "建立冒險者"}));

    expect(await screen.findByRole("heading", {name: "今日進度"})).toBeInTheDocument();
    expect(screen.getByText("建立第一個習慣，開始累積今天的進度。")).toBeInTheDocument();
    expect(window.localStorage.getItem("hlr.session.v1")).toBe("reader-token");
    expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      "http://localhost:8000/api/v1/auth/register",
      expect.objectContaining({method: "POST"}),
    );
  });

  it("loads an existing session and checks in a ready habit", async () => {
    const user = userEvent.setup();
    window.localStorage.setItem("hlr.session.v1", "reader-token");
    const fetchMock = vi
      .spyOn(globalThis, "fetch")
      .mockResolvedValueOnce(jsonResponse(profile))
      .mockResolvedValueOnce(jsonResponse([habit]))
      .mockResolvedValueOnce(
        jsonResponse(
          {
            id: 11,
            habit_id: 7,
            checkin_date: "2026-07-11",
            checked_in_at: "2026-07-11T03:00:00Z",
            exp_earned: 40,
            gold_earned: 8,
            streak_count: 3,
            current_exp: 40,
            current_gold: 8,
            current_level: 1,
            leveled_up: false,
          },
          201,
        ),
      );

    render(<App />);
    await user.click(await screen.findByRole("button", {name: "完成閱讀 20 分鐘"}));

    expect(await screen.findByText("今天的努力已記錄")).toBeInTheDocument();
    expect(screen.getByText("40 EXP")).toBeInTheDocument();
    expect(screen.getByText("8 gold")).toBeInTheDocument();
    expect(screen.getByRole("button", {name: "閱讀 20 分鐘已完成"})).toBeDisabled();
    expect(fetchMock).toHaveBeenLastCalledWith(
      "http://localhost:8000/api/v1/habits/7/checkins",
      expect.objectContaining({method: "POST"}),
    );
  });

  it("creates a habit from the dashboard", async () => {
    const user = userEvent.setup();
    window.localStorage.setItem("hlr.session.v1", "reader-token");
    vi.spyOn(globalThis, "fetch")
      .mockResolvedValueOnce(jsonResponse(profile))
      .mockResolvedValueOnce(jsonResponse([]))
      .mockResolvedValueOnce(jsonResponse(habit, 201));

    render(<App />);
    await user.click(await screen.findByRole("button", {name: "新增習慣"}));
    await user.type(screen.getByLabelText("習慣名稱"), "閱讀 20 分鐘");
    await user.type(screen.getByLabelText("分類"), "學習");
    await user.click(screen.getByRole("button", {name: "儲存習慣"}));

    expect(await screen.findByRole("heading", {name: "閱讀 20 分鐘"})).toBeInTheDocument();
    expect(screen.getByText("習慣已建立")).toBeInTheDocument();
  });

  it("clears an expired session and returns to login", async () => {
    window.localStorage.setItem("hlr.session.v1", "expired-token");
    vi.spyOn(globalThis, "fetch")
      .mockResolvedValueOnce(jsonResponse({detail: "Not authenticated."}, 401))
      .mockResolvedValueOnce(jsonResponse({detail: "Not authenticated."}, 401));

    render(<App />);

    expect(await screen.findByRole("heading", {name: "重新登入"})).toBeInTheDocument();
    expect(window.localStorage.getItem("hlr.session.v1")).toBeNull();
    await waitFor(() => expect(screen.getByRole("button", {name: "登入"})).toBeInTheDocument());
  });
});


function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: {"Content-Type": "application/json"},
  });
}
