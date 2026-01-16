// frontend/src/components/landing/ValuePillarsSection.tsx

import React from 'react';
import { ShoppingBagIcon, UsersIcon, SparklesIcon } from '@heroicons/react/24/outline';
import './ValuePillarsSection.css';

/**
 * ValuePillarsSection Component (Feature 014 - User Story 2)
 *
 * Displays 3-column grid showing ContraVento's value pillars:
 * Territorio, Comunidad, and Ética with icons and descriptions.
 *
 * Requirements:
 * - FR-014-010: 3-column grid with value pillars
 * - FR-014-011: Heroicons for each pillar
 * - FR-014-012: Pillar names (Territorio, Comunidad, Ética)
 * - FR-014-013: Brief descriptions (1-2 sentences)
 * - SC-014-005: Responsive (3 columns desktop, stacked mobile)
 */
export const ValuePillarsSection: React.FC = () => {
  return (
    <section className="value-pillars-section" aria-labelledby="value-pillars-title">
      <h2 id="value-pillars-title" className="value-pillars-title">
        Pilares de Valor
      </h2>

      <div className="value-pillars-grid">
        {/* Pillar 1: Territorio */}
        <div className="value-pillar">
          <div className="value-pillar-icon">
            <ShoppingBagIcon aria-hidden="true" />
          </div>
          <h3 className="value-pillar-title">Territorio</h3>
          <p className="value-pillar-description">
            Cada viaje apoya la economía local. Consumimos en negocios del territorio,
            preservamos el patrimonio y contribuimos a la regeneración de los lugares que visitamos.
          </p>
        </div>

        {/* Pillar 2: Comunidad */}
        <div className="value-pillar">
          <div className="value-pillar-icon">
            <UsersIcon aria-hidden="true" />
          </div>
          <h3 className="value-pillar-title">Comunidad</h3>
          <p className="value-pillar-description">
            Formamos parte de una red de ciclistas que comparten experiencias, se apoyan mutuamente
            y celebran el esfuerzo compartido por encima de la competencia individual.
          </p>
        </div>

        {/* Pillar 3: Ética */}
        <div className="value-pillar">
          <div className="value-pillar-icon">
            <SparklesIcon aria-hidden="true" />
          </div>
          <h3 className="value-pillar-title">Ética</h3>
          <p className="value-pillar-description">
            Pedaleamos con respeto por el medio ambiente, las culturas locales y las personas.
            Nuestro impacto debe ser positivo y regenerativo, nunca extractivo.
          </p>
        </div>
      </div>
    </section>
  );
};
