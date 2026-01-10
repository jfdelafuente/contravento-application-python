/**
 * Step3Photos Component
 *
 * Third step of trip creation wizard - upload and manage trip photos.
 * Integrates PhotoUploader component (to be implemented in T048).
 *
 * Used in:
 * - TripFormWizard (step 3/4)
 */

import React from 'react';
import './Step1BasicInfo.css'; // Shared styles

export const Step3Photos: React.FC = () => {
  return (
    <div className="step3-photos">
      <div className="step3-photos__header">
        <h2 className="step3-photos__title">Fotos del Viaje</h2>
        <p className="step3-photos__description">
          Añade fotos para que otros ciclistas puedan ver tu ruta. Puedes subir hasta 20 fotos (máximo 10MB cada una).
        </p>
      </div>

      <div className="step3-photos__content">
        {/* PhotoUploader will be integrated here in T048 */}
        <div className="step3-photos__placeholder">
          <svg
            className="step3-photos__placeholder-icon"
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
          <h3 className="step3-photos__placeholder-title">
            PhotoUploader Component
          </h3>
          <p className="step3-photos__placeholder-text">
            El componente de carga de fotos con drag & drop se implementará en T048.
            Por ahora, puedes continuar sin fotos y añadirlas más tarde editando el viaje.
          </p>
        </div>

        <p className="step3-photos__note">
          <strong>Nota:</strong> Las fotos son opcionales. Puedes guardar el viaje como borrador
          y añadir fotos más tarde, o continuar directamente a la revisión.
        </p>
      </div>

      <style>{`
        .step3-photos__content {
          display: flex;
          flex-direction: column;
          gap: 24px;
        }

        .step3-photos__placeholder {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          padding: 64px 32px;
          background-color: #f9fafb;
          border: 2px dashed #d1d5db;
          border-radius: 12px;
          text-align: center;
        }

        .step3-photos__placeholder-icon {
          width: 64px;
          height: 64px;
          color: #9ca3af;
          margin-bottom: 16px;
        }

        .step3-photos__placeholder-title {
          font-size: 1.25rem;
          font-weight: 600;
          color: var(--text-primary, #111827);
          margin: 0 0 8px 0;
        }

        .step3-photos__placeholder-text {
          font-size: 0.9375rem;
          color: var(--text-secondary, #6b7280);
          margin: 0;
          max-width: 500px;
        }

        .step3-photos__note {
          padding: 16px;
          background-color: #eff6ff;
          border-left: 4px solid var(--primary-color, #2563eb);
          border-radius: 8px;
          font-size: 0.9375rem;
          color: var(--text-primary, #111827);
          margin: 0;
        }

        .step3-photos__note strong {
          font-weight: 600;
          color: var(--primary-color, #2563eb);
        }

        @media (max-width: 640px) {
          .step3-photos__placeholder {
            padding: 48px 24px;
          }

          .step3-photos__placeholder-icon {
            width: 48px;
            height: 48px;
          }

          .step3-photos__placeholder-title {
            font-size: 1.125rem;
          }

          .step3-photos__placeholder-text {
            font-size: 0.875rem;
          }
        }
      `}</style>
    </div>
  );
};
