/**
 * GPX Wizard Test Page
 *
 * Temporary page for manually testing the GPS Trip Creation Wizard.
 *
 * Feature: 017-gps-trip-wizard
 * Phase: 6 (US6 - Manual Testing)
 *
 * To access: http://localhost:5173/test/gpx-wizard
 */

import React from 'react';
import { useNavigate } from 'react-router-dom';
import { GPXWizard } from '../components/wizard/GPXWizard';
import type { Trip } from '../types/trip';

export const GPXWizardTestPage: React.FC = () => {
  const navigate = useNavigate();

  const handleSuccess = (trip: Trip) => {
    console.log('✅ Trip created successfully:', trip);
    alert(`✅ Viaje creado correctamente!\n\nID: ${trip.trip_id}\nTítulo: ${trip.title}\nDistancia: ${trip.distance_km} km`);

    // Navigate to trip detail page (assuming it exists)
    // navigate(`/trips/${trip.trip_id}`);

    // For now, just navigate to home
    navigate('/');
  };

  const handleError = (error: { code: string; message: string; field?: string }) => {
    console.error('❌ Error creating trip:', error);
    alert(`❌ Error al crear el viaje\n\nCódigo: ${error.code}\nMensaje: ${error.message}${error.field ? `\nCampo: ${error.field}` : ''}`);
  };

  const handleCancel = () => {
    console.log('🚫 Wizard cancelled');
    const confirmCancel = window.confirm('¿Seguro que quieres cancelar? Se perderán todos los datos.');
    if (confirmCancel) {
      navigate('/');
    }
  };

  return (
    <div style={{ padding: '2rem', maxWidth: '1200px', margin: '0 auto' }}>
      <div style={{ marginBottom: '2rem', padding: '1rem', backgroundColor: '#fef3c7', borderRadius: '0.5rem', border: '1px solid #f59e0b' }}>
        <h2 style={{ margin: '0 0 0.5rem 0', color: '#92400e' }}>🧪 Página de Pruebas - GPS Wizard</h2>
        <p style={{ margin: '0', fontSize: '0.875rem', color: '#78350f' }}>
          Esta es una página temporal para pruebas manuales del wizard de creación de viajes GPS.
          <br />
          Verifica la consola del navegador para ver los logs detallados.
        </p>
      </div>

      <GPXWizard
        onSuccess={handleSuccess}
        onError={handleError}
        onCancel={handleCancel}
      />
    </div>
  );
};
