import { render, screen, act } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import ScoreBadge from "../ScoreBadge";

describe("ScoreBadge", () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("renders with initial score of 0", () => {
    render(<ScoreBadge score={75} />);
    // Initially starts at 0 before animation
    expect(screen.getByText("0")).toBeInTheDocument();
  });

  it("animates to the target score", () => {
    render(<ScoreBadge score={85} />);

    // Advance through the animation (800ms duration)
    act(() => {
      vi.advanceTimersByTime(900);
    });

    expect(screen.getByText("85")).toBeInTheDocument();
  });

  it("renders at small size", () => {
    const { container } = render(<ScoreBadge score={50} size="sm" />);
    const wrapper = container.firstElementChild as HTMLElement;
    expect(wrapper.style.width).toBe("60px");
    expect(wrapper.style.height).toBe("60px");
  });

  it("renders at large size by default", () => {
    const { container } = render(<ScoreBadge score={50} />);
    const wrapper = container.firstElementChild as HTMLElement;
    expect(wrapper.style.width).toBe("120px");
    expect(wrapper.style.height).toBe("120px");
  });

  it("uses green stroke for high scores (>=80)", () => {
    const { container } = render(<ScoreBadge score={90} />);
    const circles = container.querySelectorAll("circle");
    // Second circle is the progress circle
    expect(circles[1].getAttribute("stroke")).toBe("#4ade80");
  });

  it("uses yellow stroke for medium scores (60-79)", () => {
    const { container } = render(<ScoreBadge score={65} />);
    const circles = container.querySelectorAll("circle");
    expect(circles[1].getAttribute("stroke")).toBe("#facc15");
  });

  it("uses orange stroke for low scores (40-59)", () => {
    const { container } = render(<ScoreBadge score={45} />);
    const circles = container.querySelectorAll("circle");
    expect(circles[1].getAttribute("stroke")).toBe("#fb923c");
  });

  it("uses red stroke for critical scores (<40)", () => {
    const { container } = render(<ScoreBadge score={20} />);
    const circles = container.querySelectorAll("circle");
    expect(circles[1].getAttribute("stroke")).toBe("#f87171");
  });
});
