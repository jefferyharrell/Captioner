import { render, screen, waitFor } from '@testing-library/react';
import { vi, Mock } from 'vitest';
import Gallery from './Gallery';

const mockPhotos = [
  { hash: '1', caption: 'A cat', filename: 'cat.jpg' },
  { hash: '2', caption: null, filename: 'dog.jpg' },
];

(global.fetch as Mock) = vi.fn().mockResolvedValue({
  ok: true,
  json: async () => mockPhotos,
});

describe('Gallery', () => {
  it('renders photos and captions', async () => {
    render(<Gallery />);
    await waitFor(() => {
      expect(screen.getByText('A cat')).toBeInTheDocument();
      expect(screen.getByText('No caption')).toBeInTheDocument();
      expect(screen.getAllByRole('img')).toHaveLength(2);
    });
  });

  it('shows loading state and then loads', async () => {
    (fetch as Mock).mockImplementationOnce(() =>
      new Promise(resolve =>
        setTimeout(() => resolve({
          ok: true,
          json: async () => mockPhotos,
        }), 10)
      )
    );
    render(<Gallery />);
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.queryByText(/loading/i)).not.toBeInTheDocument();
    });
  });

  it('removes loading indicator after photos load', async () => {
    render(<Gallery />);
    await waitFor(() => {
      expect(screen.queryByText(/loading/i)).not.toBeInTheDocument();
    });
  });

  it('removes loading indicator after error', async () => {
    (fetch as Mock).mockRejectedValueOnce(new Error('fail'));
    render(<Gallery />);
    await waitFor(() => {
      expect(screen.getByText(/error/i)).toBeInTheDocument();
      expect(screen.queryByText(/loading/i)).not.toBeInTheDocument();
    });
  });

  it('shows error on fetch failure', async () => {
    (fetch as Mock).mockRejectedValueOnce(new Error('fail'));
    render(<Gallery />);
    await waitFor(() => {
      expect(screen.getByText(/error/i)).toBeInTheDocument();
    });
  });

  it('shows error if fetch throws (network error)', async () => {
    (fetch as Mock).mockImplementationOnce(() => { throw new Error('Network fail'); });
    render(<Gallery />);
    await waitFor(() => {
      expect(screen.getByText(/error/i)).toBeInTheDocument();
      expect(screen.getByText(/network fail/i)).toBeInTheDocument();
    });
  });

  it('shows "Unknown error" if fetch throws a non-Error', async () => {
    (fetch as Mock).mockImplementationOnce(() => { throw "not an error object"; });
    render(<Gallery />);
    await waitFor(() => {
      expect(screen.getByText(/unknown error/i)).toBeInTheDocument();
    });
  });

  it('shows error if fetch returns ok: false', async () => {
    (fetch as Mock).mockResolvedValueOnce({ ok: false, json: async () => ({}) });
    render(<Gallery />);
    await waitFor(() => {
      expect(screen.getByText(/failed to fetch/i)).toBeInTheDocument();
    });
  });
});
