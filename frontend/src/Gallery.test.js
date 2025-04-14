import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import Gallery from "./Gallery";

beforeAll(() => {
  global.fetch = jest.fn();
});
afterAll(() => {
  global.fetch.mockRestore();
});

test("renders photo thumbnails from API", async () => {
  const fakePhotos = [
    { id: "1", filename: "a.jpg", hash: "abc", caption: "First" },
    { id: "2", filename: "b.jpg", hash: "def", caption: "" }
  ];
  fetch.mockResolvedValueOnce({
    ok: true,
    json: async () => fakePhotos
  });

  render(<Gallery />);
  // You may see loading briefly, but we care about the loaded state
  await waitFor(() => {
    expect(screen.getByText("First")).toBeInTheDocument();
    expect(screen.getByText("No caption")).toBeInTheDocument();
  });
});

test("shows a friendly message when there are no photos", async () => {
  fetch.mockResolvedValueOnce({
    ok: true,
    json: async () => []
  });
  render(<Gallery />);
  await waitFor(() => {
    expect(screen.getByText(/no photos yet/i)).toBeInTheDocument();
  });
});
