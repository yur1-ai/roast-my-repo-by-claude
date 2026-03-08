import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { MemoryRouter } from "react-router-dom";
import RoastForm from "../RoastForm";

// Mock the useSubmitRoast hook
const mockSubmit = vi.fn();
vi.mock("@/hooks/useSubmitRoast", () => ({
  useSubmitRoast: () => ({
    submit: mockSubmit,
    isSubmitting: false,
    error: null,
  }),
}));

function renderForm() {
  return render(
    <MemoryRouter>
      <RoastForm />
    </MemoryRouter>
  );
}

describe("RoastForm", () => {
  beforeEach(() => {
    mockSubmit.mockClear();
  });

  it("renders the form with URL input and submit button", () => {
    renderForm();
    expect(screen.getByPlaceholderText("https://github.com/owner/repo")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /roast it/i })).toBeInTheDocument();
  });

  it("renders the brutality slider", () => {
    renderForm();
    expect(screen.getByText("Brutality Level")).toBeInTheDocument();
    // Default value is 3 = "Honest"
    expect(screen.getByText(/Honest/)).toBeInTheDocument();
  });

  it("shows validation error for invalid URL on blur", async () => {
    const user = userEvent.setup();
    renderForm();

    const input = screen.getByPlaceholderText("https://github.com/owner/repo");
    await user.type(input, "not-a-github-url");
    await user.tab(); // trigger blur

    expect(
      screen.getByText(/please enter a valid github url/i)
    ).toBeInTheDocument();
  });

  it("clears validation error for valid URL on blur", async () => {
    const user = userEvent.setup();
    renderForm();

    const input = screen.getByPlaceholderText("https://github.com/owner/repo");

    // First type invalid
    await user.type(input, "bad");
    await user.tab();
    expect(screen.getByText(/please enter a valid github url/i)).toBeInTheDocument();

    // Clear and type valid
    await user.clear(input);
    await user.type(input, "https://github.com/owner/repo");
    await user.tab();
    expect(screen.queryByText(/please enter a valid github url/i)).not.toBeInTheDocument();
  });

  it("shows validation error on submit with invalid URL", async () => {
    const user = userEvent.setup();
    renderForm();

    const input = screen.getByPlaceholderText("https://github.com/owner/repo");
    await user.type(input, "invalid-url");
    await user.click(screen.getByRole("button", { name: /roast it/i }));

    expect(screen.getByText(/please enter a valid github url/i)).toBeInTheDocument();
    expect(mockSubmit).not.toHaveBeenCalled();
  });

  it("calls submit with valid URL and default brutality", async () => {
    const user = userEvent.setup();
    renderForm();

    const input = screen.getByPlaceholderText("https://github.com/owner/repo");
    await user.type(input, "https://github.com/facebook/react");
    await user.click(screen.getByRole("button", { name: /roast it/i }));

    expect(mockSubmit).toHaveBeenCalledWith("https://github.com/facebook/react", 3);
  });

  it("does not show error when URL is empty on blur", async () => {
    const user = userEvent.setup();
    renderForm();

    const input = screen.getByPlaceholderText("https://github.com/owner/repo");
    await user.click(input);
    await user.tab();

    expect(screen.queryByText(/please enter a valid github url/i)).not.toBeInTheDocument();
  });
});
