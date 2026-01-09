import React from 'react';
import { useNavigate } from 'react-router-dom';
import QuickActionButton from './QuickActionButton';
import './QuickActionsSection.css';

/**
 * QuickActionsSection component - Quick access buttons for common actions
 * Provides 4 main navigation shortcuts in the dashboard
 */
const QuickActionsSection: React.FC = () => {
  const navigate = useNavigate();

  const quickActions = [
    {
      label: 'Crear Viaje',
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <line x1="12" y1="5" x2="12" y2="19" />
          <line x1="5" y1="12" x2="19" y2="12" />
        </svg>
      ),
      onClick: () => navigate('/trips/new'),
      variant: 'primary' as const,
    },
    {
      label: 'Ver Perfil',
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
          <circle cx="12" cy="7" r="4" />
        </svg>
      ),
      onClick: () => navigate('/profile'),
      variant: 'secondary' as const,
    },
    {
      label: 'Explorar Viajes',
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <circle cx="11" cy="11" r="8" />
          <path d="m21 21-4.35-4.35" />
        </svg>
      ),
      onClick: () => navigate('/explore'),
      variant: 'secondary' as const,
    },
    {
      label: 'Editar Perfil',
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
          <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
        </svg>
      ),
      onClick: () => navigate('/profile/edit'),
      variant: 'secondary' as const,
    },
  ];

  return (
    <section className="quick-actions-section" aria-labelledby="quick-actions-heading">
      <h2 id="quick-actions-heading" className="quick-actions-section__title">
        Acciones Rápidas
      </h2>
      <div className="quick-actions-section__grid">
        {quickActions.map((action, index) => (
          <div
            key={action.label}
            style={{ animationDelay: `${index * 0.1}s` }}
            className="quick-actions-section__grid-item"
          >
            <QuickActionButton
              label={action.label}
              icon={action.icon}
              onClick={action.onClick}
              variant={action.variant}
            />
          </div>
        ))}
      </div>
    </section>
  );
};

export default QuickActionsSection;
