import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import UploadPhoto from "../UploadPhoto";

// Mock fetch globally
beforeAll(() => {
  global.fetch = jest.fn();
});
afterEach(() => {
  jest.clearAllMocks();
});

describe("UploadPhoto", () => {
  it("uploads a photo and calls onUpload callback", async () => {
    const onUpload = jest.fn();
    // Mock fetch to resolve with a new photo object
    (fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ id: 42, filename: "test.jpg", caption: null }),
    });

    render(<UploadPhoto onUpload={onUpload} />);

    // Simulate file selection
    const file = new File(["dummy"], "test.jpg", { type: "image/jpeg" });
    const input = screen.getByLabelText(/choose photo/i);
    fireEvent.change(input, { target: { files: [file] } });

    // Submit the form
    fireEvent.click(screen.getByRole("button", { name: /upload/i }));

    // Wait for upload and callback
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining("/photos"),
        expect.objectContaining({
          method: "POST",
          body: expect.any(FormData),
        })
      );
      expect(onUpload).toHaveBeenCalledWith({ id: 42, filename: "test.jpg", caption: null });
    });
  });
});
