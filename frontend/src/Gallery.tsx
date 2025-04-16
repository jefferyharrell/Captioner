import { useEffect, useState } from 'react';

interface Photo {
  hash: string;
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
    <div className="grid gap-4 grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
      {photos.map(photo => (
        <div key={photo.hash} className="flex flex-col items-center p-2">
          <img
            src={`http://localhost:8000/photos/${photo.hash}/thumbnail`}
            alt={photo.caption || photo.filename}
            className="w-full h-48 object-cover"
          />
          <div className="mt-1 text-center w-full min-h-[1.5em]">
            {photo.caption ? photo.caption : <em>No caption</em>}
          </div>
        </div>
      ))}
    </div>
  );
}
