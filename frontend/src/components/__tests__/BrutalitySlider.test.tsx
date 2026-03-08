import { render, screen } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import BrutalitySlider from "../BrutalitySlider";

describe("BrutalitySlider", () => {
  it("displays the correct label for level 1", () => {
    render(<BrutalitySlider value={1} onChange={vi.fn()} />);
    expect(screen.getByText(/Gentle/)).toBeInTheDocument();
  });

  it("displays the correct label for level 3", () => {
    render(<BrutalitySlider value={3} onChange={vi.fn()} />);
    expect(screen.getByText(/Honest/)).toBeInTheDocument();
  });

  it("displays the correct label for level 5", () => {
    render(<BrutalitySlider value={5} onChange={vi.fn()} />);
    expect(screen.getByText(/Savage/)).toBeInTheDocument();
  });

  it("shows Brutality Level label", () => {
    render(<BrutalitySlider value={3} onChange={vi.fn()} />);
    expect(screen.getByText("Brutality Level")).toBeInTheDocument();
  });

  it("renders all 5 emoji indicators at the bottom", () => {
    const { container } = render(<BrutalitySlider value={3} onChange={vi.fn()} />);
    // The bottom emoji row: last child div with text-xs class
    const emojiRow = container.querySelector(".text-xs.text-muted-foreground");
    const spans = emojiRow?.querySelectorAll("span");
    expect(spans).toHaveLength(5);
  });

  it("displays correct label for each brutality level", () => {
    const levels = [
      { value: 1, label: "Gentle" },
      { value: 2, label: "Constructive" },
      { value: 3, label: "Honest" },
      { value: 4, label: "Brutal" },
      { value: 5, label: "Savage" },
    ];

    for (const { value, label } of levels) {
      const { unmount } = render(
        <BrutalitySlider value={value} onChange={vi.fn()} />
      );
      // Match label at end of text to avoid "Brutal" matching "Brutality Level"
      expect(screen.getByText(new RegExp(`${label}$`))).toBeInTheDocument();
      unmount();
    }
  });
});
