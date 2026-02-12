/**
 * TripCreatePage Component
 *
 * Page for creating new trips using the multi-step wizard.
 * Wraps TripFormWizard with useTripForm hook for state management.
 *
 * Features:
 * - Multi-step form (4 steps)
 * - Form data persistence with localStorage
 * - Draft vs publish workflow
 * - Unsaved changes warning
 * - Success/error handling
 *
 * Route: /trips/new
 *
 * Requires: Authentication
 */

import React, { useEffect } from 'react';
import { TripFormWizard } from '../components/trips/TripForm/TripFormWizard';
import { useTripForm } from '../hooks/useTripForm';
import './TripCreatePage.css';

export const TripCreatePage: React.FC = () => {
  const { handleSubmit, getPersistedData } = useTripForm({
    enablePersistence: true,
  });

  // Get persisted data on mount (if available)
  const persistedData = getPersistedData();

  // Set page title
  useEffect(() => {
    document.title = 'Crear Viaje - ContraVento';
  }, []);

  return (
    <div className="trip-create-page">
      {/* Page Header */}
      <header className="trip-create-page__header">
        <div className="trip-create-page__header-content">
          <h1 className="trip-create-page__title">Crear Nuevo Viaje</h1>
          <p className="trip-create-page__subtitle">
            Comparte tu aventura ciclista con la comunidad. Puedes guardar como borrador y
            publicar más tarde.
          </p>
        </div>
      </header>

      {/* Trip Form Wizard */}
      <main className="trip-create-page__main">
        <TripFormWizard
          initialData={persistedData || undefined}
          onSubmit={handleSubmit}
          isEditMode={false}
        />
      </main>
    </div>
  );
};
