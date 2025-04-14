import React, { useEffect, useState } from "react";

const API_URL = "http://localhost:8000";

export default function Gallery() {
  const [photos, setPhotos] = useState([]);
  const [error, setError] = useState(null);
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
    // Show a friendlier message if it's a network error
    if (error === "Failed to fetch") {
      return <div style={{color: '#888', margin: '2rem'}}>Couldn’t reach the backend. Is it running?</div>;
    }
    return <div style={{color: 'red'}}>Error: {error}</div>;
  }
  if (!photos.length) return <div style={{color: '#888', margin: '2rem'}}>No photos found.</div>;

  return (
    <div style={{ display: "flex", flexWrap: "wrap", gap: 16 }}>
      {photos.map((photo) => (
        <div key={photo.id} style={{ border: "1px solid #ccc", padding: 8, borderRadius: 8, width: 180 }}>
          <img
            src={`${API_URL}/photos/${photo.id}/image`}
            alt={photo.caption || photo.filename}
            style={{ width: "100%", height: 120, objectFit: "cover", borderRadius: 4 }}
          />
          <div style={{ marginTop: 8, fontWeight: "bold" }}>{photo.caption || <span style={{color:'#888'}}>No caption</span>}</div>
        </div>
      ))}
    </div>
  );
}
