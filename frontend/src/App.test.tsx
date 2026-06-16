import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import App from "./App";

describe("App foundation", () => {
  it("renders the Habit Life RPG frontend shell", () => {
    render(<App />);

    expect(screen.getByRole("heading", { name: "Habit Life RPG" })).toBeInTheDocument();
    expect(screen.getByText(/React \+ Vite \+ TypeScript \+ Tailwind/)).toBeInTheDocument();
  });
});
