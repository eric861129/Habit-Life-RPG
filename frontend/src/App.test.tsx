import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
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
});

describe("App foundation", () => {
  it("loads the Habit Life RPG shell from the API", async () => {
    const fetchMock = mockGameState();

    render(<App />);

    expect(screen.getByText("Connecting to guild server...")).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Habit Life RPG" })).toBeInTheDocument();
    expect(await screen.findByRole("heading", { name: "Quest Log" })).toBeInTheDocument();
    expect(await screen.findByText("晨間 20 分鐘閱讀")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "打卡領獎" })).toBeInTheDocument();

    expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      "http://localhost:8000/api/v1/user/profile",
      expect.objectContaining({
        headers: expect.objectContaining({ Authorization: "Bearer local-dev-token" }),
      }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      2,
      "http://localhost:8000/api/v1/habits",
      expect.objectContaining({
        headers: expect.objectContaining({ Authorization: "Bearer local-dev-token" }),
      }),
    );
  });

  it("renders checked-in habits as done and disabled", async () => {
    mockGameState();

    render(<App />);

    expect(await screen.findByText("喝水 2000 ml")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "已完成" })).toBeDisabled();
  });

  it("checks in a ready habit and updates hero rewards", async () => {
    const user = userEvent.setup();
    const fetchMock = mockGameState();
    const pendingCheckin = deferredResponse();
    fetchMock.mockReturnValueOnce(pendingCheckin.promise);

    render(<App />);

    await user.click(await screen.findByRole("button", { name: "打卡領獎" }));

    expect(screen.getByRole("button", { name: "結算中..." })).toBeDisabled();
    pendingCheckin.resolve(
      jsonResponse({
        habit_id: 1,
        checked_in: true,
        current_exp: 160,
        current_gold: 43,
        current_level: 2,
        leveled_up: false,
      }),
    );

    expect(await screen.findByText("Quest reward claimed")).toBeInTheDocument();
    expect(screen.getByText("+40 EXP / +8 gold. Keep the guild ledger shining.")).toBeInTheDocument();
    expect(screen.getByText("43 G")).toBeInTheDocument();
    expect(screen.getAllByText("160 / 400").length).toBeGreaterThan(0);
    expect(screen.getAllByRole("button", { name: "已完成" })).toHaveLength(2);

    await waitFor(() => {
      expect(fetchMock).toHaveBeenNthCalledWith(
        3,
        "http://localhost:8000/api/v1/habits/1/checkin",
        expect.objectContaining({
          method: "POST",
          headers: expect.objectContaining({ Authorization: "Bearer local-dev-token" }),
        }),
      );
    });
  });

  it("shows a level-up panel when the backend promotes the hero", async () => {
    const user = userEvent.setup();
    const fetchMock = mockGameState({ ...profileResponse, level: 1, exp: 190 });
    fetchMock.mockResolvedValueOnce(
      jsonResponse({
        habit_id: 1,
        checked_in: true,
        current_exp: 230,
        current_gold: 43,
        current_level: 2,
        leveled_up: true,
      }),
    );

    render(<App />);

    await user.click(await screen.findByRole("button", { name: "打卡領獎" }));

    expect(await screen.findByRole("heading", { name: "Level up!" })).toBeInTheDocument();
    expect(screen.getByText("Guild rank updated. The next quest board awaits.")).toBeInTheDocument();
  });

  it("keeps the ready state when duplicate check-in returns an error", async () => {
    const user = userEvent.setup();
    const fetchMock = mockGameState();
    fetchMock.mockResolvedValueOnce(jsonResponse({ detail: "Already checked in today." }, { status: 400 }));

    render(<App />);

    await user.click(await screen.findByRole("button", { name: "打卡領獎" }));

    expect(await screen.findByRole("alert")).toHaveTextContent("Guild error 400");
    expect(screen.getByRole("alert")).toHaveTextContent("Already checked in today.");
    expect(screen.getByRole("button", { name: "打卡領獎" })).toBeEnabled();
    expect(screen.getByText("35 G")).toBeInTheDocument();
    expect(screen.getAllByText("120 / 400").length).toBeGreaterThan(0);
  });

  it("shows an offline error when the backend is unavailable", async () => {
    vi.spyOn(globalThis, "fetch").mockRejectedValue(new TypeError("Failed to fetch"));

    render(<App />);

    expect(await screen.findByRole("alert")).toHaveTextContent("Guild server offline");
    expect(screen.getByText("Start FastAPI on port 8000 to open today's quest board.")).toBeInTheDocument();
  });
});

function mockGameState(profile = profileResponse, habits = habitsResponse) {
  return vi
    .spyOn(globalThis, "fetch")
    .mockResolvedValueOnce(jsonResponse(profile))
    .mockResolvedValueOnce(jsonResponse(habits));
}

function deferredResponse() {
  let resolve!: (response: Response) => void;
  const promise = new Promise<Response>((nextResolve) => {
    resolve = nextResolve;
  });

  return { promise, resolve };
}

function jsonResponse(body: unknown, init: ResponseInit = {}) {
  return new Response(JSON.stringify(body), {
    status: 200,
    headers: { "Content-Type": "application/json" },
    ...init,
  });
}
