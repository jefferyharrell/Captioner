import React from "react";
import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import Home from "./page";

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
    const textarea = screen.getByLabelText(/edit caption/i);
    fireEvent.change(textarea, { target: { value: "Fluffy kitty" } });
    expect(textarea).toHaveValue("Fluffy kitty");
    // Wait for debounce and save to complete
    await waitFor(() => expect(screen.getByDisplayValue("Fluffy kitty")).toBeInTheDocument());
  });
});
