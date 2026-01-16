// frontend/src/components/landing/Footer.tsx

import React from 'react';
import { Link } from 'react-router-dom';
import './Footer.css';

/**
 * Footer Component (Feature 014 - User Story 5)
 *
 * Displays footer with branding, social media links, legal links, and contact information.
 * Provides navigation to additional resources and company information.
 *
 * Requirements:
 * - FR-014-022: Display ContraVento branding/logo
 * - FR-014-023: Display social media links (Instagram, Facebook)
 * - FR-014-024: Social links open in new tab with rel="noopener noreferrer"
 * - FR-014-025: Display legal links (Terms of Service, Privacy Policy)
 * - FR-014-026: Legal links navigate to /terms-of-service and /privacy-policy
 * - FR-014-027: Display contact email (hola@contravento.com) as mailto link
 * - SC-014-009: 4-column grid on desktop, stacked on mobile
 * - SC-014-010: Verde bosque background (#1B2621) with crema text (#F9F7F2)
 */
export const Footer: React.FC = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="footer">
      <div className="footer-content">
        {/* Branding Section */}
        <div className="footer-brand">
          <h3 className="footer-logo">ContraVento</h3>
          <p className="footer-tagline">El camino es el destino</p>
          <p className="footer-description">
            Una comunidad de ciclistas que valoran la conexión humana y territorial sobre la
            competencia.
          </p>
        </div>

        {/* Social Media Section */}
        <div className="footer-social">
          <h4 className="footer-section-title">Síguenos</h4>
          <ul className="footer-links">
            <li>
              <a
                href="https://instagram.com/contravento"
                target="_blank"
                rel="noopener noreferrer"
                className="footer-link"
              >
                Instagram
              </a>
            </li>
            <li>
              <a
                href="https://facebook.com/contravento"
                target="_blank"
                rel="noopener noreferrer"
                className="footer-link"
              >
                Facebook
              </a>
            </li>
          </ul>
        </div>

        {/* Legal Section */}
        <div className="footer-legal">
          <h4 className="footer-section-title">Legal</h4>
          <ul className="footer-links">
            <li>
              <Link to="/terms-of-service" className="footer-link">
                Términos de Servicio
              </Link>
            </li>
            <li>
              <Link to="/privacy-policy" className="footer-link">
                Política de Privacidad
              </Link>
            </li>
          </ul>
        </div>

        {/* Contact Section */}
        <div className="footer-contact">
          <h4 className="footer-section-title">Contacto</h4>
          <ul className="footer-links">
            <li>
              <a href="mailto:hola@contravento.com" className="footer-link">
                hola@contravento.com
              </a>
            </li>
          </ul>
        </div>
      </div>

      {/* Copyright */}
      <div className="footer-bottom">
        <p className="footer-copyright">
          © {currentYear} ContraVento. Todos los derechos reservados.
        </p>
      </div>
    </footer>
  );
};
