// frontend/src/components/landing/HowItWorksSection.tsx

import React from 'react';
import { CameraIcon, ShareIcon, MapIcon, HeartIcon } from '@heroicons/react/24/outline';
import './HowItWorksSection.css';

/**
 * HowItWorksSection Component (Feature 014 - User Story 3)
 *
 * Displays 4-step process flow showing how ContraVento works:
 * 1. Documenta - 2. Comparte - 3. Descubre - 4. Impacta
 *
 * Requirements:
 * - FR-014-014: 4-step process flow
 * - FR-014-015: Numbered steps (1-4) with icons
 * - FR-014-016: Step titles (Documenta, Comparte, Descubre, Impacta)
 * - FR-014-017: Brief descriptions (1-2 sentences)
 * - SC-014-006: Responsive (2x2 grid desktop, stacked mobile)
 */
export const HowItWorksSection: React.FC = () => {
  return (
    <section className="how-it-works-section" aria-labelledby="how-it-works-title">
      <h2 id="how-it-works-title" className="how-it-works-title">
        Cómo Funciona
      </h2>

      <div className="how-it-works-grid">
        {/* Step 1: Documenta */}
        <div className="how-it-works-step">
          <div className="step-number" aria-label="Paso 1">
            1
          </div>
          <div className="step-icon">
            <CameraIcon aria-hidden="true" />
          </div>
          <h3 className="step-title">Documenta</h3>
          <p className="step-description">
            Registra tus viajes en bicicleta con fotos, rutas GPS y notas. Cada pedalada cuenta
            una historia única de conexión con el territorio.
          </p>
        </div>

        {/* Step 2: Comparte */}
        <div className="how-it-works-step">
          <div className="step-number" aria-label="Paso 2">
            2
          </div>
          <div className="step-icon">
            <ShareIcon aria-hidden="true" />
          </div>
          <h3 className="step-title">Comparte</h3>
          <p className="step-description">
            Comparte tus historias con la comunidad ContraVento. Inspira a otros ciclistas y
            descubre experiencias que valoran el camino sobre el destino.
          </p>
        </div>

        {/* Step 3: Descubre */}
        <div className="how-it-works-step">
          <div className="step-number" aria-label="Paso 3">
            3
          </div>
          <div className="step-icon">
            <MapIcon aria-hidden="true" />
          </div>
          <h3 className="step-title">Descubre</h3>
          <p className="step-description">
            Explora rutas y lugares compartidos por otros ciclistas. Encuentra territorios que
            preservan su autenticidad y celebran la cultura local.
          </p>
        </div>

        {/* Step 4: Impacta */}
        <div className="how-it-works-step">
          <div className="step-number" aria-label="Paso 4">
            4
          </div>
          <div className="step-icon">
            <HeartIcon aria-hidden="true" />
          </div>
          <h3 className="step-title">Impacta</h3>
          <p className="step-description">
            Genera un impacto positivo en cada destino. Apoya la economía local, respeta el
            medio ambiente y contribuye a la regeneración de los territorios.
          </p>
        </div>
      </div>
    </section>
  );
};
