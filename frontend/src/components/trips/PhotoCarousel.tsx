/**
 * PhotoCarousel Component
 *
 * Horizontal photo carousel for TripDetailPage.
 * Combines trip photos and POI photos into a single navigable gallery.
 *
 * Features:
 * - Navigation buttons (previous/next)
 * - Click to open lightbox (full-screen view)
 * - Badge indicating photo source (Trip/POI)
 * - Caption overlay
 * - Responsive design
 *
 * Feature: MVP - Photo Gallery Enhancement
 */

import React, { useState, useEffect } from 'react';
import Lightbox from 'yet-another-react-lightbox';
import Thumbnails from 'yet-another-react-lightbox/plugins/thumbnails';
import Zoom from 'yet-another-react-lightbox/plugins/zoom';
import 'yet-another-react-lightbox/styles.css';
import 'yet-another-react-lightbox/plugins/thumbnails.css';
import './PhotoCarousel.css';

export interface CombinedPhoto {
  /** Full-size photo URL */
  url: string;

  /** Thumbnail URL (optional, falls back to url) */
  thumbnail?: string;

  /** Photo caption */
  caption: string;

  /** Source of photo (trip or POI) */
  source: 'trip' | 'poi';

  /** Original width (for lightbox aspect ratio) */
  width?: number;

  /** Original height (for lightbox aspect ratio) */
  height?: number;
}

interface PhotoCarouselProps {
  /** Combined array of trip and POI photos */
  photos: CombinedPhoto[];

  /** Trip title (for default alt text) */
  tripTitle?: string;
}

export const PhotoCarousel: React.FC<PhotoCarouselProps> = ({ photos, tripTitle = 'Viaje' }) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [lightboxOpen, setLightboxOpen] = useState(false);

  // Reset currentIndex if it's invalid or out of bounds when photos array changes
  useEffect(() => {
    if (isNaN(currentIndex) || currentIndex < 0 || currentIndex >= photos.length) {
      if (photos.length > 0) {
        setCurrentIndex(0);
      }
    }
  }, [photos.length, currentIndex]);

  // Empty state
  if (photos.length === 0) {
    return null;
  }

  // Safely get current photo with fallback
  const currentPhoto = photos[currentIndex] || photos[0];

  // If still no photo available, return null
  if (!currentPhoto) {
    return null;
  }

  // Navigation handlers
  const handlePrevious = () => {
    setCurrentIndex((prev) => (prev === 0 ? photos.length - 1 : prev - 1));
  };

  const handleNext = () => {
    setCurrentIndex((prev) => (prev === photos.length - 1 ? 0 : prev + 1));
  };

  const handleMainPhotoClick = () => {
    setLightboxOpen(true);
  };

  // Convert photos to lightbox slides format
  const lightboxSlides = photos.map((photo) => ({
    src: photo.url,
    alt: photo.caption || tripTitle,
    width: photo.width,
    height: photo.height,
  }));

  // Source badge label
  const getSourceLabel = (source: 'trip' | 'poi') => {
    return source === 'trip' ? 'Viaje' : 'POI';
  };

  return (
    <div className="photo-carousel" data-testid="photo-carousel">
      {/* Main Photo Display */}
      <div className="photo-carousel__main">
        {/* Photo */}
        <div
          className="photo-carousel__image-container"
          onClick={handleMainPhotoClick}
          role="button"
          tabIndex={0}
          onKeyDown={(e) => {
            if (e.key === 'Enter' || e.key === ' ') {
              e.preventDefault();
              handleMainPhotoClick();
            }
          }}
          aria-label={`Ampliar foto: ${currentPhoto.caption}`}
        >
          <img
            src={currentPhoto.url}
            alt={currentPhoto.caption || tripTitle}
            className="photo-carousel__image"
          />

          {/* Source Badge */}
          <div className={`photo-carousel__badge photo-carousel__badge--${currentPhoto.source}`}>
            {getSourceLabel(currentPhoto.source)}
          </div>

          {/* Caption Overlay */}
          {currentPhoto.caption && (
            <div className="photo-carousel__caption">
              <p>{currentPhoto.caption}</p>
            </div>
          )}

          {/* Click hint */}
          <div className="photo-carousel__click-hint">
            <svg
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7"
              />
            </svg>
            <span>Haz clic para ampliar</span>
          </div>
        </div>

        {/* Navigation Buttons */}
        {photos.length > 1 && (
          <>
            <button
              onClick={handlePrevious}
              className="photo-carousel__nav photo-carousel__nav--prev"
              aria-label="Foto anterior"
            >
              <svg
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </button>

            <button
              onClick={handleNext}
              className="photo-carousel__nav photo-carousel__nav--next"
              aria-label="Foto siguiente"
            >
              <svg
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </button>
          </>
        )}

        {/* Counter */}
        {photos.length > 1 && (
          <div className="photo-carousel__counter">
            {currentIndex + 1} / {photos.length}
          </div>
        )}
      </div>

      {/* Keyboard Navigation Hint (Screen readers) */}
      <div className="sr-only" role="status" aria-live="polite">
        Foto {currentIndex + 1} de {photos.length}: {currentPhoto.caption}
      </div>

      {/* Lightbox */}
      <Lightbox
        open={lightboxOpen}
        close={() => setLightboxOpen(false)}
        slides={lightboxSlides}
        index={currentIndex}
        plugins={[Thumbnails, Zoom]}
        on={{
          view: (index: number) => {
            if (!isNaN(index) && index >= 0 && index < photos.length) {
              setCurrentIndex(index);
            }
          },
        }}
      />
    </div>
  );
};
