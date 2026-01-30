/**
 * GPXTripCreatePage Component
 *
 * GPS Trip Creation Wizard page with full implementation.
 * Handles file upload, trip details, review, and atomic trip creation.
 *
 * Route: /trips/new/gpx
 *
 * Requires: Authentication
 *
 * Feature: 017-gps-trip-wizard
 * Phase: 6 (US6 - Publish Trip)
 */

import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { GPXWizard } from '../components/wizard/GPXWizard';
import type { Trip } from '../types/trip';

export const GPXTripCreatePage: React.FC = () => {
  const navigate = useNavigate();

  useEffect(() => {
    document.title = 'Crear Viaje desde GPX - ContraVento';
  }, []);

  /**
   * Handle successful trip creation.
   * Shows success toast and navigates to trip detail page.
   */
  const handleSuccess = (trip: Trip) => {
    console.log('✅ Trip created successfully:', trip);

    // Show success toast
    toast.success('¡Viaje creado correctamente!', {
      duration: 4000,
      position: 'top-center',
    });

    // Navigate to trip detail page
    navigate(`/trips/${trip.trip_id}`);
  };

  /**
   * Handle trip creation error.
   * Shows error toast with Spanish message.
   */
  const handleError = (error: { code: string; message: string; field?: string }) => {
    console.error('❌ Error creating trip:', error);

    // Show error toast
    toast.error(error.message, {
      duration: 6000,
      position: 'top-center',
    });
  };

  /**
   * Handle wizard cancellation.
   * Navigates back to trips list.
   */
  const handleCancel = () => {
    console.log('🚫 Wizard cancelled');
    navigate('/trips');
  };

  return (
    <div style={{ padding: '2rem 1rem', maxWidth: '1200px', margin: '0 auto' }}>
      <GPXWizard onSuccess={handleSuccess} onError={handleError} onCancel={handleCancel} />
    </div>
  );
};
