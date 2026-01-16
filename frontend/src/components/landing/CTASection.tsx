// frontend/src/components/landing/CTASection.tsx

import React from 'react';
import { Link } from 'react-router-dom';
import './CTASection.css';

/**
 * CTASection Component (Feature 014 - User Story 4)
 *
 * Displays call-to-action section with registration button and login link.
 * Encourages visitors to join the ContraVento community.
 *
 * Requirements:
 * - FR-014-018: Display prominent CTA button "Formar parte del viaje"
 * - FR-014-019: CTA button links to /register route
 * - FR-014-020: Display "¿Ya tienes cuenta? Inicia sesión" link
 * - FR-014-021: Login link navigates to /login route
 * - SC-014-007: CTA button uses terracota color (#D35400)
 * - SC-014-008: CTA section centered, visible on all viewports
 */
export const CTASection: React.FC = () => {
  return (
    <section className="cta-section" aria-labelledby="cta-title">
      <div className="cta-content">
        <h2 id="cta-title" className="cta-title">
          Únete a la Comunidad
        </h2>
        <p className="cta-subtitle">
          Forma parte de una red de ciclistas que valoran el camino, no solo el destino.
        </p>

        <Link to="/register" className="cta-button">
          Formar parte del viaje
        </Link>

        <p className="cta-login-text">
          ¿Ya tienes cuenta?{' '}
          <Link to="/login" className="cta-login-link">
            Inicia sesión
          </Link>
        </p>
      </div>
    </section>
  );
};
