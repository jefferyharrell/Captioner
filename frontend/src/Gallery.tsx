import { useEffect, useState } from 'react';

interface Photo {
  id: string;
  caption: string | null;
  filename: string;
}

export default function Gallery() {
  const [photos, setPhotos] = useState<Photo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchPhotos() {
      try {
        const res = await fetch('http://localhost:8000/photos');
        if (!res.ok) throw new Error('Failed to fetch photos');
        const data = await res.json();
        setPhotos(data);
      } catch (err: unknown) {
        if (err instanceof Error) {
          setError(err.message);
        } else {
          setError('Unknown error');
        }
      } finally {
        setLoading(false);
      }
    }
    fetchPhotos();
  }, []);

  if (loading) return <div>Loading gallery…</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 24 }}>
      {photos.map(photo => (
        <div key={photo.id} style={{ border: '1px solid #ddd', borderRadius: 8, padding: 12 }}>
          <img
            src={`http://localhost:8000/photos/${photo.id}/image`}
            alt={photo.caption || photo.filename}
            style={{ width: '100%', height: 200, objectFit: 'cover', borderRadius: 4 }}
          />
          <div style={{ marginTop: 8, color: '#444' }}>
            {photo.caption ? photo.caption : <em>No caption</em>}
          </div>
        </div>
      ))}
    </div>
  );
}
