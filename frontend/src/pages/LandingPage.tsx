// frontend/src/pages/LandingPage.tsx

import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useSEO } from '../hooks/useSEO';
import { Header } from '../components/landing/Header';
import { HeroSection } from '../components/landing/HeroSection';
import { ManifestoSection } from '../components/landing/ManifestoSection';
import { ValuePillarsSection } from '../components/landing/ValuePillarsSection';
import { HowItWorksSection } from '../components/landing/HowItWorksSection';
import { DiscoverTripsSection } from '../components/landing/DiscoverTripsSection';
import { CTASection } from '../components/landing/CTASection';
import { Footer } from '../components/landing/Footer';
import './LandingPage.css';

/**
 * LandingPage Container (Feature 014 - User Story 1)
 *
 * Public landing page displayed at root URL (/) with cinematic hero,
 * 4-pillar manifesto, and authenticated user redirect logic.
 *
 * Requirements:
 * - FR-014-007: Redirect authenticated users to /trips/public (feed)
 * - FR-014-008: Display landing page for unauthenticated visitors
 * - FR-014-009: Compose HeroSection + ManifestoSection + ValuePillarsSection
 * - SC-014-004: Page loads in < 2.5s (LCP)
 *
 * User Flow:
 * - Unauthenticated: See hero + manifesto + value pillars → CTA to /register
 * - Authenticated: Redirect to /trips/public (public feed)
 */
export const LandingPage: React.FC = () => {
  const { user, isLoading } = useAuth();

  // SEO Configuration
  const seoConfig = {
    title: 'ContraVento - Pedalear para Conectar',
    description:
      'Una plataforma para ciclistas que pedalean para conectar, no para competir. Documenta viajes, regenera territorios, y únete a la comunidad que valora el camino sobre el destino.',
    image: '/src/assets/images/landing/hero.jpg',
    url: 'https://contravento.com',
  };

  // Show loading indicator while checking authentication
  if (isLoading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner">Cargando...</div>
      </div>
    );
  }

  // Redirect authenticated users to public trips feed
  if (user) {
    return <Navigate to="/trips/public" replace />;
  }

  // Render landing page for unauthenticated visitors
  return (
    <>
      {useSEO(seoConfig)}
      <Header />
      <main className="landing-page" aria-label="Landing Page - ContraVento">
        <HeroSection />
        <ManifestoSection />
        <ValuePillarsSection />
        <HowItWorksSection />
        <DiscoverTripsSection />
        <CTASection />
      </main>
      <Footer />
    </>
  );
};
