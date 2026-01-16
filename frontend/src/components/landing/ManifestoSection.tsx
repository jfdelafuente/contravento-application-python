// frontend/src/components/landing/ManifestoSection.tsx

import React from 'react';
import './ManifestoSection.css';

/**
 * ManifestoSection Component (Feature 014 - User Story 1)
 *
 * Displays 4-pillar manifesto explaining ContraVento's core philosophy:
 * 1. El camino es el destino
 * 2. Pedalear para conectar
 * 3. Regenerar territorios
 * 4. Comunidad sobre competencia
 *
 * Requirements:
 * - FR-014-004: Display 4-pillar manifesto with headings
 * - FR-014-005: Show specific pillar titles
 * - FR-014-006: Include 1-2 sentence descriptions under each pillar
 * - SC-014-003: Manifesto visible above fold on desktop after hero
 */
export const ManifestoSection: React.FC = () => {
  return (
    <section className="manifesto-section" aria-labelledby="manifesto-title">
      <h2 id="manifesto-title" className="manifesto-title">
        Nuestra Filosofía
      </h2>

      <div className="manifesto-grid">
        {/* Pillar 1: El camino es el destino */}
        <div className="manifesto-pillar">
          <h3 className="manifesto-pillar-title">El camino es el destino</h3>
          <p className="manifesto-pillar-description">
            El viaje importa más que el destino. Cada pedalada es una oportunidad para
            descubrir, reflexionar y conectar con el entorno y contigo mismo.
          </p>
        </div>

        {/* Pillar 2: Pedalear para conectar */}
        <div className="manifesto-pillar">
          <h3 className="manifesto-pillar-title">Pedalear para conectar</h3>
          <p className="manifesto-pillar-description">
            La bicicleta es nuestro medio de conexión humana y territorial. Pedaleamos para
            conocer personas, culturas y paisajes que enriquecen nuestra experiencia vital.
          </p>
        </div>

        {/* Pillar 3: Regenerar territorios */}
        <div className="manifesto-pillar">
          <h3 className="manifesto-pillar-title">Regenerar territorios</h3>
          <p className="manifesto-pillar-description">
            Cada viaje es una oportunidad para apoyar economía local, preservar el patrimonio
            natural y cultural, y contribuir a la regeneración de los lugares que visitamos.
          </p>
        </div>

        {/* Pillar 4: Comunidad sobre competencia */}
        <div className="manifesto-pillar">
          <h3 className="manifesto-pillar-title">Comunidad sobre competencia</h3>
          <p className="manifesto-pillar-description">
            No medimos el éxito en kilómetros o velocidad, sino en experiencias compartidas.
            Celebramos el esfuerzo compartido y el apoyo mutuo entre ciclistas.
          </p>
        </div>
      </div>
    </section>
  );
};
