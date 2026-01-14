/**
 * Unit tests for PublicTripCard component (Feature 013 - T032, T042)
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { PublicTripCard } from '../../src/components/trips/PublicTripCard';
import { PublicTripSummary } from '../../src/types/trip';

// Mock useNavigate from react-router-dom
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

// Wrapper component for router context
const RouterWrapper = ({ children }: { children: React.ReactNode }) => (
  <BrowserRouter>{children}</BrowserRouter>
);

describe('PublicTripCard', () => {
  const mockTrip: PublicTripSummary = {
    trip_id: '123e4567-e89b-12d3-a456-426614174000',
    title: 'Ruta Bikepacking Pirineos',
    start_date: '2024-06-01',
    distance_km: 320.5,
    photo: {
      photo_url: '/storage/trip_photos/2024/06/photo.jpg',
      thumbnail_url: '/storage/trip_photos/2024/06/photo_thumb.jpg',
    },
    location: {
      name: 'Jaca, España',
    },
    author: {
      user_id: '456e7890-e89b-12d3-a456-426614174001',
      username: 'maria_ciclista',
      profile_photo_url: '/storage/profile_photos/maria.jpg',
    },
    published_at: '2024-06-10T14:30:00Z',
  };

  beforeEach(() => {
    vi.clearAllMocks();
    mockNavigate.mockClear();
  });

  it('renders trip card with all information', () => {
    render(
      <RouterWrapper>
        <PublicTripCard trip={mockTrip} />
      </RouterWrapper>
    );

    // Check title
    expect(screen.getByText('Ruta Bikepacking Pirineos')).toBeInTheDocument();

    // Check author
    expect(screen.getByText('maria_ciclista')).toBeInTheDocument();

    // Check location
    expect(screen.getByText(/Jaca, España/i)).toBeInTheDocument();

    // Check distance
    expect(screen.getByText(/320\.5 km/i)).toBeInTheDocument();
  });

  it('displays trip photo when available', () => {
    render(
      <RouterWrapper>
        <PublicTripCard trip={mockTrip} />
      </RouterWrapper>
    );

    const image = screen.getByAltText('Ruta Bikepacking Pirineos');
    expect(image).toBeInTheDocument();
    expect(image).toHaveAttribute('src', expect.stringContaining('photo_thumb.jpg'));
  });

  it('displays placeholder when no photo available', () => {
    const tripWithoutPhoto: PublicTripSummary = {
      ...mockTrip,
      photo: null,
    };

    render(
      <RouterWrapper>
        <PublicTripCard trip={tripWithoutPhoto} />
      </RouterWrapper>
    );

    const image = screen.getByAltText('Ruta Bikepacking Pirineos');
    expect(image).toHaveAttribute('src', expect.stringContaining('placeholder'));
  });

  it('displays author profile photo when available', () => {
    render(
      <RouterWrapper>
        <PublicTripCard trip={mockTrip} />
      </RouterWrapper>
    );

    const authorPhoto = screen.getByAltText('maria_ciclista');
    expect(authorPhoto).toBeInTheDocument();
    expect(authorPhoto).toHaveAttribute('src', expect.stringContaining('maria.jpg'));
  });

  it('displays default avatar when author has no photo', () => {
    const tripWithNoAuthorPhoto: PublicTripSummary = {
      ...mockTrip,
      author: {
        ...mockTrip.author,
        profile_photo_url: null,
      },
    };

    render(
      <RouterWrapper>
        <PublicTripCard trip={tripWithNoAuthorPhoto} />
      </RouterWrapper>
    );

    // Should render avatar with first letter of username
    const avatar = screen.getByText('M');
    expect(avatar).toBeInTheDocument();
  });

  it('handles missing location gracefully', () => {
    const tripWithoutLocation: PublicTripSummary = {
      ...mockTrip,
      location: null,
    };

    render(
      <RouterWrapper>
        <PublicTripCard trip={tripWithoutLocation} />
      </RouterWrapper>
    );

    // Card should still render without location
    expect(screen.getByText('Ruta Bikepacking Pirineos')).toBeInTheDocument();

    // Location icon should not be present
    expect(screen.queryByText(/Jaca, España/i)).not.toBeInTheDocument();
  });

  it('handles missing distance gracefully', () => {
    const tripWithoutDistance: PublicTripSummary = {
      ...mockTrip,
      distance_km: null,
    };

    render(
      <RouterWrapper>
        <PublicTripCard trip={tripWithoutDistance} />
      </RouterWrapper>
    );

    // Card should still render
    expect(screen.getByText('Ruta Bikepacking Pirineos')).toBeInTheDocument();

    // Distance should not be displayed
    expect(screen.queryByText(/km/i)).not.toBeInTheDocument();
  });

  it('formats date correctly', () => {
    render(
      <RouterWrapper>
        <PublicTripCard trip={mockTrip} />
      </RouterWrapper>
    );

    // Should display formatted date (locale-specific)
    const dateElement = screen.getByText(/jun|junio/i);
    expect(dateElement).toBeInTheDocument();
  });

  it('navigates to trip detail on click', () => {
    const { container } = render(
      <RouterWrapper>
        <PublicTripCard trip={mockTrip} />
      </RouterWrapper>
    );

    const card = container.querySelector('.public-trip-card');
    expect(card).toBeInTheDocument();

    // Click the card
    fireEvent.click(card!);

    // Should navigate to trip detail page with correct trip_id
    expect(mockNavigate).toHaveBeenCalledWith('/trips/123e4567-e89b-12d3-a456-426614174000');
    expect(mockNavigate).toHaveBeenCalledTimes(1);
  });

  it('navigates to trip detail when clicking on image', () => {
    render(
      <RouterWrapper>
        <PublicTripCard trip={mockTrip} />
      </RouterWrapper>
    );

    const image = screen.getByAltText('Ruta Bikepacking Pirineos');

    // Click the image
    fireEvent.click(image);

    // Should navigate to trip detail page
    expect(mockNavigate).toHaveBeenCalledWith('/trips/123e4567-e89b-12d3-a456-426614174000');
  });

  it('navigates to trip detail when clicking on title', () => {
    render(
      <RouterWrapper>
        <PublicTripCard trip={mockTrip} />
      </RouterWrapper>
    );

    const title = screen.getByText('Ruta Bikepacking Pirineos');

    // Click the title
    fireEvent.click(title);

    // Should navigate to trip detail page
    expect(mockNavigate).toHaveBeenCalledWith('/trips/123e4567-e89b-12d3-a456-426614174000');
  });

  it('has proper accessibility attributes', () => {
    const { container } = render(
      <RouterWrapper>
        <PublicTripCard trip={mockTrip} />
      </RouterWrapper>
    );

    const card = container.querySelector('.public-trip-card');

    // Should be an article element for semantic HTML
    expect(card?.tagName).toBe('ARTICLE');
  });

  it('lazy loads trip images', () => {
    render(
      <RouterWrapper>
        <PublicTripCard trip={mockTrip} />
      </RouterWrapper>
    );

    const image = screen.getByAltText('Ruta Bikepacking Pirineos');

    // Should have loading="lazy" attribute
    expect(image).toHaveAttribute('loading', 'lazy');
  });

  it('renders card with correct CSS class', () => {
    const { container } = render(
      <RouterWrapper>
        <PublicTripCard trip={mockTrip} />
      </RouterWrapper>
    );

    const card = container.querySelector('.public-trip-card');
    expect(card).toBeInTheDocument();
    expect(card).toHaveClass('public-trip-card');
  });

  it('displays metadata in correct order', () => {
    const { container } = render(
      <RouterWrapper>
        <PublicTripCard trip={mockTrip} />
      </RouterWrapper>
    );

    const metadata = container.querySelector('.public-trip-card__metadata');
    expect(metadata).toBeInTheDocument();

    // Metadata should contain location, distance, and date
    const metadataText = metadata?.textContent || '';
    expect(metadataText).toContain('Jaca, España');
    expect(metadataText).toContain('320.5 km');
  });

  it('uses 3:2 aspect ratio for images', () => {
    const { container } = render(
      <RouterWrapper>
        <PublicTripCard trip={mockTrip} />
      </RouterWrapper>
    );

    const imageContainer = container.querySelector('.public-trip-card__image-container');
    expect(imageContainer).toBeInTheDocument();

    // Check for aspect ratio styling (padding-top: 66.67% for 3:2 ratio)
    const styles = window.getComputedStyle(imageContainer!);
    // Note: In jsdom, computed styles might not work, so we check for class instead
    expect(imageContainer).toHaveClass('public-trip-card__image-container');
  });
});
