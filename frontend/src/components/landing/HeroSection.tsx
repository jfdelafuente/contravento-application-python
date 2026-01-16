// frontend/src/components/landing/HeroSection.tsx

import React from 'react';
import { Link } from 'react-router-dom';
import './HeroSection.css';

/**
 * HeroSection Component (Feature 014 - User Story 1)
 *
 * Displays cinematic hero section with "El camino es el destino" headline,
 * subtitle about human/territorial connection, and CTA button to registration.
 *
 * Requirements:
 * - FR-014-001: Hero image with main headline
 * - FR-014-002: Subtitle about connection philosophy
 * - FR-014-003: CTA button to /register
 * - SC-014-001: LCP < 2.5s (eager loading, WebP optimization)
 * - SC-014-002: Responsive (mobile < 768px, tablet 768-1024px, desktop > 1024px)
 */
export const HeroSection: React.FC = () => {
  return (
    <section className="hero-section" aria-label="Hero section - El camino es el destino">
      {/* Responsive Hero Image with WebP optimization */}
      <picture>
        {/* Mobile WebP (< 768px) */}
        <source
          media="(max-width: 768px)"
          srcSet="/src/assets/images/landing/hero-mobile.webp"
          type="image/webp"
        />
        {/* Mobile JPG Fallback (< 768px) */}
        <source
          media="(max-width: 768px)"
          srcSet="/src/assets/images/landing/hero-mobile.jpg"
          type="image/jpeg"
        />
        {/* Desktop WebP */}
        <source
          srcSet="/src/assets/images/landing/hero.webp"
          type="image/webp"
        />
        {/* Desktop JPG Fallback */}
        <img
          src="/src/assets/images/landing/hero.jpg"
          alt="Ciclista en entorno rural durante la hora dorada"
          className="hero-image"
          loading="eager"
        />
      </picture>

      {/* Content Overlay */}
      <div className="hero-content">
        <h1 className="hero-title">El camino es el destino</h1>
        <p className="hero-subtitle">
          Pedalear para conectar, no para competir. Una plataforma para ciclistas que valoran
          la conexión humana y territorial sobre las métricas y el rendimiento.
        </p>
        <Link to="/register" className="hero-cta">
          Únete a la Comunidad
        </Link>
      </div>
    </section>
  );
};
