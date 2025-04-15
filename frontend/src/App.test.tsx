import { render, screen } from '@testing-library/react';
import App from './App';

describe('App', () => {
  it('renders the Vite + React heading', () => {
    render(<App />);
    expect(screen.getByText(/Vite \+ React/i)).toBeInTheDocument();
  });
});
