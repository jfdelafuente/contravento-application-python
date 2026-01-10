/**
 * TripGallery Component
 *
 * Photo gallery for trip detail page with responsive grid and lightbox.
 * Integrates yet-another-react-lightbox for full-screen photo viewing.
 *
 * Used in:
 * - TripDetailPage (main photo gallery section)
 */

import React, { useState } from 'react';
import Lightbox from 'yet-another-react-lightbox';
import Thumbnails from 'yet-another-react-lightbox/plugins/thumbnails';
import Zoom from 'yet-another-react-lightbox/plugins/zoom';
import 'yet-another-react-lightbox/styles.css';
import 'yet-another-react-lightbox/plugins/thumbnails.css';
import { TripPhoto } from '../../types/trip';
import { getPhotoUrl } from '../../utils/tripHelpers';
import './TripGallery.css';

interface TripGalleryProps {
  /** Array of trip photos */
  photos: TripPhoto[];

  /** Trip title (for alt text) */
  tripTitle: string;
}

export const TripGallery: React.FC<TripGalleryProps> = ({ photos, tripTitle }) => {
  const [lightboxOpen, setLightboxOpen] = useState(false);
  const [lightboxIndex, setLightboxIndex] = useState(0);

  // Handle photo click - open lightbox at clicked photo
  const handlePhotoClick = (index: number) => {
    setLightboxIndex(index);
    setLightboxOpen(true);
  };

  // Convert TripPhoto[] to lightbox slides format
  const lightboxSlides = photos.map((photo) => ({
    src: getPhotoUrl(photo.photo_url) || '',
    alt: photo.caption || tripTitle,
    width: photo.width,
    height: photo.height,
  }));

  // Empty state
  if (photos.length === 0) {
    return (
      <div className="trip-gallery trip-gallery--empty">
        <div className="trip-gallery__empty-icon">
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
              d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
            />
          </svg>
        </div>
        <p className="trip-gallery__empty-text">No hay fotos en este viaje</p>
      </div>
    );
  }

  return (
    <>
      <div className="trip-gallery">
        {/* Photo Grid */}
        <div className="trip-gallery__grid">
          {photos.map((photo, index) => (
            <button
              key={photo.photo_id}
              className="trip-gallery__item"
              onClick={() => handlePhotoClick(index)}
              aria-label={`Ver foto ${index + 1} de ${photos.length}${
                photo.caption ? `: ${photo.caption}` : ''
              }`}
            >
              <img
                src={getPhotoUrl(photo.thumbnail_url || photo.photo_url) || ''}
                alt={photo.caption || `${tripTitle} - Foto ${index + 1}`}
                className="trip-gallery__image"
                loading="lazy"
              />

              {/* Caption overlay (only shown if caption exists) */}
              {photo.caption && (
                <div className="trip-gallery__caption-overlay">
                  <p className="trip-gallery__caption-text">{photo.caption}</p>
                </div>
              )}

              {/* Zoom icon overlay */}
              <div className="trip-gallery__zoom-overlay">
                <svg
                  className="trip-gallery__zoom-icon"
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
              </div>
            </button>
          ))}
        </div>

        {/* Photo count */}
        <div className="trip-gallery__count">
          <svg
            className="trip-gallery__count-icon"
            fill="currentColor"
            viewBox="0 0 20 20"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              fillRule="evenodd"
              d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z"
              clipRule="evenodd"
            />
          </svg>
          <span className="trip-gallery__count-text">
            {photos.length} {photos.length === 1 ? 'foto' : 'fotos'}
          </span>
        </div>
      </div>

      {/* Lightbox */}
      <Lightbox
        open={lightboxOpen}
        close={() => setLightboxOpen(false)}
        index={lightboxIndex}
        slides={lightboxSlides}
        plugins={[Thumbnails, Zoom]}
        thumbnails={{
          position: 'bottom',
          width: 120,
          height: 80,
          border: 2,
          borderRadius: 4,
          padding: 4,
          gap: 16,
        }}
        zoom={{
          maxZoomPixelRatio: 3,
          zoomInMultiplier: 2,
          doubleTapDelay: 300,
          doubleClickDelay: 300,
          doubleClickMaxStops: 2,
          keyboardMoveDistance: 50,
          wheelZoomDistanceFactor: 100,
          pinchZoomDistanceFactor: 100,
          scrollToZoom: true,
        }}
        carousel={{
          finite: false,
          preload: 2,
        }}
        animation={{
          fade: 250,
          swipe: 500,
          easing: {
            fade: 'ease',
            swipe: 'ease-out',
            navigation: 'ease-in-out',
          },
        }}
        controller={{
          closeOnBackdropClick: true,
          closeOnPullDown: true,
          closeOnPullUp: true,
        }}
        render={{
          buttonPrev: photos.length <= 1 ? () => null : undefined,
          buttonNext: photos.length <= 1 ? () => null : undefined,
        }}
      />
    </>
  );
};
