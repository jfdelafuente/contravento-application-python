// frontend/src/components/landing/Header.tsx

import React from 'react';
import { Link } from 'react-router-dom';
import './Header.css';

/**
 * Header Component (Landing Page)
 *
 * Sticky header for the landing page with logo and navigation links.
 *
 * Layout:
 * - Left: ContraVento logo (links to /)
 * - Right: Navigation links (Rutas, Login)
 *
 * Responsive:
 * - Desktop: Horizontal layout with logo left, nav right
 * - Mobile: Stacked layout, center-aligned
 */
export const Header: React.FC = () => {
  return (
    <header className="landing-header">
      <div className="landing-header-content">
        <div className="landing-header-logo">
          <Link to="/" aria-label="ContraVento - Inicio">
            ContraVento
          </Link>
        </div>

        <nav className="landing-header-nav" aria-label="Navegación principal">
          <Link to="/trips/public" className="landing-header-link">
            Rutas
          </Link>
          <Link to="/login" className="landing-header-link">
            Login
          </Link>
        </nav>
      </div>
    </header>
  );
};
