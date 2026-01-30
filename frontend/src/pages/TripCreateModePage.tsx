/**
 * TripCreateModePage Component
 *
 * Modal page for selecting trip creation mode (GPS vs Manual).
 * Displays two options in a centered modal dialog:
 * - "Crear Viaje con GPS": Navigate to GPX wizard (/trips/new/gpx)
 * - "Crear Viaje sin GPS": Navigate to manual form (/trips/new/manual)
 *
 * Features:
 * - Modal overlay with ESC key and click-outside to dismiss
 * - Keyboard navigation support
 * - ARIA accessibility attributes
 * - Responsive design (mobile + desktop)
 *
 * Route: /trips/new
 *
 * Requires: Authentication
 *
 * Feature: 017-gps-trip-wizard
 * Phase: 3 (US1 - Mode Selection Modal)
 * Tasks: T022, T023
 */

import React, { useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import './TripCreateModePage.css';

export const TripCreateModePage: React.FC = () => {
  const navigate = useNavigate();

  // Handle mode selection
  const handleGPSMode = useCallback(() => {
    navigate('/trips/new/gpx');
  }, [navigate]);

  const handleManualMode = useCallback(() => {
    navigate('/trips/new/manual');
  }, [navigate]);

  // Handle modal dismissal (ESC key)
  const handleDismiss = useCallback(() => {
    navigate('/trips');
  }, [navigate]);

  // ESC key listener
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        handleDismiss();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [handleDismiss]);

  // Handle overlay click (dismiss modal)
  const handleOverlayClick = (event: React.MouseEvent<HTMLDivElement>) => {
    // Only dismiss if clicking the overlay itself (not modal content)
    if (event.target === event.currentTarget) {
      handleDismiss();
    }
  };

  // Set page title
  useEffect(() => {
    document.title = '¿Cómo quieres crear tu viaje? - ContraVento';
  }, []);

  return (
    <div className="trip-create-mode-page" onClick={handleOverlayClick}>
      {/* Modal Container */}
      <div
        className="trip-create-mode-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="mode-selection-title"
      >
        {/* Modal Header */}
        <header className="trip-create-mode-modal__header">
          <h1 id="mode-selection-title" className="trip-create-mode-modal__title">
            ¿Cómo quieres crear tu viaje?
          </h1>
          <p className="trip-create-mode-modal__subtitle">
            Elige el método que mejor se adapte a tu aventura
          </p>
        </header>

        {/* Mode Options */}
        <div className="trip-create-mode-modal__options">
          {/* GPS Mode Option */}
          <button
            type="button"
            className="mode-option mode-option--gps"
            onClick={handleGPSMode}
            aria-label="Crear viaje con GPS - Sube un archivo GPX y extrae automáticamente la ruta y telemetría"
          >
            <div className="mode-option__icon-container">
              <svg
                className="mode-option__icon"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                strokeWidth={1.5}
                stroke="currentColor"
                aria-hidden="true"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M9 6.75V15m6-6v8.25m.503 3.498l4.875-2.437c.381-.19.622-.58.622-1.006V4.82c0-.836-.88-1.38-1.628-1.006l-3.869 1.934c-.317.159-.69.159-1.006 0L9.503 3.252a1.125 1.125 0 00-1.006 0L3.622 5.689C3.24 5.88 3 6.27 3 6.695V19.18c0 .836.88 1.38 1.628 1.006l3.869-1.934c.317-.159.69-.159 1.006 0l4.994 2.497c.317.158.69.158 1.006 0z"
                />
              </svg>
            </div>
            <h2 className="mode-option__title">Crear Viaje con GPS</h2>
            <p className="mode-option__description">
              Sube un archivo GPX y extrae automáticamente la ruta, distancia, desnivel y
              dificultad. Añade POIs visualizando la ruta en el mapa.
            </p>
          </button>

          {/* Manual Mode Option */}
          <button
            type="button"
            className="mode-option mode-option--manual"
            onClick={handleManualMode}
            aria-label="Crear viaje sin GPS - Ingresa manualmente los detalles del viaje"
          >
            <div className="mode-option__icon-container">
              <svg
                className="mode-option__icon"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                strokeWidth={1.5}
                stroke="currentColor"
                aria-hidden="true"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L10.582 16.07a4.5 4.5 0 01-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 011.13-1.897l8.932-8.931zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0115.75 21H5.25A2.25 2.25 0 013 18.75V8.25A2.25 2.25 0 015.25 6H10"
                />
              </svg>
            </div>
            <h2 className="mode-option__title">Crear Viaje sin GPS</h2>
            <p className="mode-option__description">
              Ingresa manualmente los detalles del viaje. Ideal si no tienes archivo GPX o prefieres
              añadir solo información básica.
            </p>
          </button>
        </div>

        {/* Help Text */}
        <footer className="trip-create-mode-modal__footer">
          <p className="trip-create-mode-modal__help-text">
            Presiona <kbd>ESC</kbd> para volver a tus viajes
          </p>
        </footer>
      </div>
    </div>
  );
};
