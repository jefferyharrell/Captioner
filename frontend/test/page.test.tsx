import React from "react";
import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import Home from "../src/app/page";

// Mock fetch globally
const mockPhoto = {
  hash: "abc123",
  filename: "cat.jpg",
  caption: "A cat."
};

global.fetch = jest.fn((url, options) => {
  if (url.endsWith("/photos/random")) {
    return Promise.resolve({
      ok: true,
      json: () => Promise.resolve(mockPhoto)
    });
  }
  if (url.endsWith(`/photos/${mockPhoto.hash}/caption`)) {
    return Promise.resolve({
      ok: true,
      json: () => Promise.resolve({ ...mockPhoto, caption: JSON.parse(options.body).caption })
    });
  }
  return Promise.reject(new Error("not found"));
});

describe("Home page", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("fetches and displays a random photo", async () => {
    render(<Home />);
    expect(screen.getByText(/Loading random photo/i)).toBeInTheDocument();
    await waitFor(() => expect(screen.getByAltText("cat.jpg")).toBeInTheDocument());
    expect(screen.getByDisplayValue("A cat.")).toBeInTheDocument();
    expect(screen.getByText(/Filename: cat.jpg/)).toBeInTheDocument();
  });

  it("lets the user edit and save the caption", async () => {
    render(<Home />);
    await waitFor(() => expect(screen.getByAltText("cat.jpg")).toBeInTheDocument());
    const input = screen.getByPlaceholderText(/Enter a caption/i);
    fireEvent.change(input, { target: { value: "Fluffy kitty" } });
    expect(input).toHaveValue("Fluffy kitty");
    const button = screen.getByRole("button", { name: /Save Caption/i });
    fireEvent.click(button);
    await waitFor(() => expect(screen.getByDisplayValue("Fluffy kitty")).toBeInTheDocument());
  });
});
