import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import Gallery from "../Gallery";

// Mock fetch globally
beforeAll(() => {
  global.fetch = jest.fn();
});
afterEach(() => {
  jest.clearAllMocks();
});

describe("Gallery", () => {
  it("shows loading and then photos", async () => {
    (fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => [
        { id: 1, filename: "foo.jpg", caption: "A Foo" },
        { id: 2, filename: "bar.jpg", caption: null },
      ],
    });
    render(<Gallery />);
    await waitFor(() => {
      expect(screen.getByText("A Foo")).toBeInTheDocument();
      expect(screen.getByText("No caption")).toBeInTheDocument();
    });
  });

  it("shows error if fetch fails", async () => {
    (fetch as jest.Mock).mockRejectedValueOnce(new Error("Failed to fetch"));
    render(<Gallery />);
    await waitFor(() => {
      expect(screen.getByText(/couldn’t reach the backend/i)).toBeInTheDocument();
    });
  });

  it("shows no photos found", async () => {
    (fetch as jest.Mock).mockResolvedValueOnce({ ok: true, json: async () => [] });
    render(<Gallery />);
    await waitFor(() => {
      expect(screen.getByText(/no photos found/i)).toBeInTheDocument();
    });
  });
});
