"use client";
import { useEffect, useState } from "react";

interface Photo {
  hash: string;
  filename: string;
  caption: string | null;
}

export default function Home() {
  const [photo, setPhoto] = useState<Photo | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [caption, setCaption] = useState("");
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    fetch("http://localhost:8000/photos/random")
      .then(async (res) => {
        if (!res.ok) throw new Error("No photo found");
        const data = await res.json();
        setPhoto(data);
        setCaption(data.caption ?? "");
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  const handleCaptionChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setCaption(e.target.value);
  };

  const handleCaptionSave = async () => {
    if (!photo) return;
    setSaving(true);
    setSaveError(null);
    try {
      const res = await fetch(`http://localhost:8000/photos/${photo.hash}/caption`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ caption }),
      });
      if (!res.ok) throw new Error("Failed to save caption");
      const updated = await res.json();
      setPhoto(updated);
    } catch (e: any) {
      setSaveError(e.message);
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <div className="flex flex-col items-center justify-center min-h-screen text-lg">Loading random photo…</div>;
  }
  if (error || !photo) {
    return <div className="flex flex-col items-center justify-center min-h-screen text-red-600">{error || "No photo found."}</div>;
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-screen gap-8 p-8">
      <img
        src={`http://localhost:8000/photos/${photo.hash}/image`}
        alt={photo.filename}
        className="max-w-[90vw] max-h-[60vh] rounded shadow"
        style={{ objectFit: "contain" }}
      />
      <div className="flex flex-col gap-2 w-full max-w-md">
        <input
          type="text"
          className="border p-2 rounded text-lg"
          value={caption}
          onChange={handleCaptionChange}
          placeholder="Enter a caption…"
        />
        <button
          onClick={handleCaptionSave}
          className="bg-blue-600 text-white rounded px-4 py-2 disabled:opacity-50"
          disabled={saving}
        >
          {saving ? "Saving…" : "Save Caption"}
        </button>
        {saveError && <div className="text-red-600 text-sm">{saveError}</div>}
      </div>
      <div className="text-gray-500 mt-4">Filename: {photo.filename}</div>    </div>
  );
}
