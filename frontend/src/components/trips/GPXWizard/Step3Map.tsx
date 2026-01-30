/**
 * Step3Map Component (Feature 017 - Phase 7 - US4)
 *
 * Map visualization step of the GPS Trip Creation Wizard.
 * Displays the GPX route on an interactive map with telemetry metrics.
 *
 * Tasks:
 * - T078: Component implementation
 * - T079: TripMap integration with GPX trackpoints
 * - T080: Telemetry panel with distance, elevation, time metrics
 * - T081: GPX track polyline rendering (handled by TripMap)
 * - T082: Auto-centering (handled by TripMap)
 * - T084: Navigation buttons
 */

import React from 'react';
import type { GPXTelemetry } from '../../../types/gpxWizard';
import './Step3Map.css';

interface Step3MapProps {
  /** GPX telemetry metrics from wizard analysis */
  telemetry: GPXTelemetry;

  /** Callback to go back to previous step */
  onBack: () => void;

  /** Callback to proceed to next step (Step 4: Review) */
  onNext: () => void;
}

export const Step3Map: React.FC<Step3MapProps> = ({
  telemetry,
  onBack,
  onNext,
}) => {

  return (
    <div className="step3-map">
      {/* Step Header */}
      <header className="step3-map__header">
        <h2 className="step3-map__title">Resumen de tu ruta</h2>
        <p className="step3-map__description">
          Revisa los datos de telemetría extraídos de tu archivo GPX.
        </p>
      </header>

      {/* Info Section - Map preview not available in wizard */}
      <section className="step3-map__info-section">
        <div className="step3-map__info-card">
          <div className="step3-map__info-icon">
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
                d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          </div>
          <div className="step3-map__info-content">
            <h3 className="step3-map__info-title">Vista previa del mapa</h3>
            <p className="step3-map__info-text">
              El mapa interactivo con tu ruta completa estará disponible después de publicar el viaje.
              Por ahora, puedes revisar los datos de telemetría extraídos de tu archivo GPX.
            </p>
          </div>
        </div>
      </section>

      {/* Telemetry Panel - Always show */}
      <section className="step3-map__telemetry">
          <h3 className="step3-map__telemetry-title">Datos de telemetría</h3>

          <div className="step3-map__telemetry-grid">
            {/* Distance */}
            <div className="step3-map__telemetry-item">
              <div className="step3-map__telemetry-icon">
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
                    d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"
                  />
                </svg>
              </div>
              <div className="step3-map__telemetry-content">
                <span className="step3-map__telemetry-label">Distancia</span>
                <span className="step3-map__telemetry-value">{telemetry.distance_km.toFixed(1)} km</span>
              </div>
            </div>

            {/* Elevation Gain */}
            {telemetry.elevation_gain !== null && (
              <div className="step3-map__telemetry-item">
                <div className="step3-map__telemetry-icon step3-map__telemetry-icon--success">
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
                      d="M5 10l7-7m0 0l7 7m-7-7v18"
                    />
                  </svg>
                </div>
                <div className="step3-map__telemetry-content">
                  <span className="step3-map__telemetry-label">Desnivel positivo</span>
                  <span className="step3-map__telemetry-value">{Math.round(telemetry.elevation_gain)} m</span>
                </div>
              </div>
            )}

            {/* Elevation Loss */}
            {telemetry.elevation_loss !== null && (
              <div className="step3-map__telemetry-item">
                <div className="step3-map__telemetry-icon step3-map__telemetry-icon--info">
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
                      d="M19 14l-7 7m0 0l-7-7m7 7V3"
                    />
                  </svg>
                </div>
                <div className="step3-map__telemetry-content">
                  <span className="step3-map__telemetry-label">Desnivel negativo</span>
                  <span className="step3-map__telemetry-value">{Math.round(telemetry.elevation_loss)} m</span>
                </div>
              </div>
            )}

            {/* Max Elevation */}
            {telemetry.max_elevation !== null && (
              <div className="step3-map__telemetry-item">
                <div className="step3-map__telemetry-icon step3-map__telemetry-icon--warning">
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
                      d="M5 3l7 18 7-18H5z"
                    />
                  </svg>
                </div>
                <div className="step3-map__telemetry-content">
                  <span className="step3-map__telemetry-label">Altitud máxima</span>
                  <span className="step3-map__telemetry-value">{Math.round(telemetry.max_elevation)} m</span>
                </div>
              </div>
            )}

            {/* Min Elevation */}
            {telemetry.min_elevation !== null && (
              <div className="step3-map__telemetry-item">
                <div className="step3-map__telemetry-icon">
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
                      d="M3 10h18M3 14h18"
                    />
                  </svg>
                </div>
                <div className="step3-map__telemetry-content">
                  <span className="step3-map__telemetry-label">Altitud mínima</span>
                  <span className="step3-map__telemetry-value">{Math.round(telemetry.min_elevation)} m</span>
                </div>
              </div>
            )}
          </div>
        </section>

      {/* Navigation Buttons */}
      <nav className="step3-map__navigation">
        <button
          type="button"
          onClick={onBack}
          className="step3-map__button step3-map__button--secondary"
        >
          Atrás
        </button>

        <button
          type="button"
          onClick={onNext}
          className="step3-map__button step3-map__button--primary"
        >
          Siguiente
        </button>
      </nav>
    </div>
  );
};
