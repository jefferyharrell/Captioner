import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import App from './App';

describe('App', () => {
  it('renders the Photo Gallery heading', () => {
    render(<App />);
    expect(screen.getByText(/Photo Gallery/i)).toBeInTheDocument();
  });
});
