import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import App from "./App";

describe("App foundation", () => {
  it("renders the Habit Life RPG shell", () => {
    render(<App />);

    expect(screen.getByRole("heading", { name: "Habit Life RPG" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Quest Log" })).toBeInTheDocument();
    expect(screen.getByText("晨間 20 分鐘閱讀")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "打卡領獎" })).toBeInTheDocument();
  });
});
