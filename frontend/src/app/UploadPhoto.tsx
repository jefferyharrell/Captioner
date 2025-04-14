"use client";
import React, { useRef, useState } from "react";

const API_URL = "http://localhost:8000";

interface UploadPhotoProps {
  onUpload: (photo: { id: number; filename: string; caption: string | null }) => void;
}

export default function UploadPhoto({ onUpload }: UploadPhotoProps) {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInput = useRef<HTMLInputElement>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (!fileInput.current?.files?.length) {
      setError("Please choose a file.");
      return;
    }
    const file = fileInput.current.files[0];
    const formData = new FormData();
    formData.append("file", file);
    setUploading(true);
    try {
      const res = await fetch(`${API_URL}/photos`, {
        method: "POST",
        body: formData,
      });
      if (!res.ok) throw new Error("Upload failed");
      const photo = await res.json();
      onUpload(photo);
      if (fileInput.current) fileInput.current.value = "";
    } catch (err: any) {
      setError(err.message || "Upload failed");
    } finally {
      setUploading(false);
    }
  };

  return (
    <form
      className="flex flex-col items-center gap-6 mb-10 bg-zinc-900/80 p-8 rounded-xl shadow-lg w-full max-w-md"
      onSubmit={handleSubmit}
    >
      <label htmlFor="photo-upload" className="w-full text-center text-lg font-semibold text-blue-300">
        Choose photo:
      </label>
      <div className="w-full flex flex-col items-center gap-2">
        <input
          ref={fileInput}
          id="photo-upload"
          type="file"
          accept="image/*"
          className="hidden"
          aria-label="Choose photo"
          onChange={() => setError(null)}
        />
        <label
          htmlFor="photo-upload"
          className="cursor-pointer bg-blue-700 text-white px-4 py-2 rounded hover:bg-blue-800 focus:ring-2 focus:ring-blue-400 transition-all duration-150 shadow"
          tabIndex={0}
        >
          {fileInput.current?.files?.[0]?.name || "Select File"}
        </label>
        <span className="text-xs text-gray-400">
          {fileInput.current?.files?.[0]?.name ? "Ready to upload!" : "No file chosen"}
        </span>
      </div>
      <button
        type="submit"
        className="bg-gradient-to-r from-blue-600 to-blue-400 text-white px-6 py-2 rounded-lg font-bold shadow hover:from-blue-700 hover:to-blue-500 focus:ring-2 focus:ring-blue-300 transition-all duration-150 disabled:opacity-60"
        disabled={uploading}
      >
        {uploading ? "Uploading..." : "Upload"}
      </button>
      {error && <div className="text-red-400 font-semibold text-center w-full">{error}</div>}
    </form>
  );
}
