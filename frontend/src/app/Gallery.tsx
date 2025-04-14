"use client";
import React, { useEffect, useState } from "react";

const API_URL = "http://localhost:8000";

interface Photo {
  id: number;
  filename: string;
  caption: string | null;
}

export default function Gallery() {
  const [photos, setPhotos] = useState<Photo[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch(`${API_URL}/photos`)
      .then((res) => {
        if (!res.ok) throw new Error("Failed to fetch photos");
        return res.json();
      })
      .then(setPhotos)
      .catch((e) => setError(e.message));
  }, []);

  if (error) {
    if (error === "Failed to fetch") {
      return <div className="text-gray-500 mt-8 text-center">Couldn’t reach the backend. Is it running?</div>;
    }
    return <div className="text-red-600 mt-8 text-center font-semibold">Error: {error}</div>;
  }
  if (!photos.length) return <div className="text-gray-500 mt-8 text-center">No photos found.</div>;

  return (
    <div className="flex flex-wrap justify-center gap-6 mt-8">
      {photos.map((photo) => (
        <div
          key={photo.id}
          className="border border-gray-200 bg-white p-4 rounded-lg shadow hover:shadow-lg transition w-44 flex flex-col items-center"
        >
          <img
            src={`${API_URL}/photos/${photo.id}/image`}
            alt={photo.caption || photo.filename}
            className="w-full h-32 object-cover rounded mb-2"
          />
          <div className="mt-1 font-semibold text-center text-gray-800 text-sm min-h-5">
            {photo.caption || ""}
          </div>
        </div>
      ))}
    </div>
  );
}
