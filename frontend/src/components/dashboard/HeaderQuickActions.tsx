import React from 'react';
import { useNavigate } from 'react-router-dom';
import './HeaderQuickActions.css';

/**
 * HeaderQuickActions - Compact icon buttons for header
 * "Brújula de Cabecera" - Always visible, minimal space
 */
const HeaderQuickActions: React.FC = () => {
  const navigate = useNavigate();

  const actions = [
    {
      label: 'Crear Viaje',
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
          <line x1="12" y1="5" x2="12" y2="19" />
          <line x1="5" y1="12" x2="19" y2="12" />
        </svg>
      ),
      onClick: () => navigate('/trips/new'),
      variant: 'primary' as const,
      ariaLabel: 'Crear nuevo viaje',
    },
    {
      label: 'Explorar',
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <circle cx="11" cy="11" r="8" />
          <path d="m21 21-4.35-4.35" />
        </svg>
      ),
      onClick: () => navigate('/explore'),
      variant: 'secondary' as const,
      ariaLabel: 'Explorar viajes de la comunidad',
    },
    {
      label: 'Perfil',
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
          <circle cx="12" cy="7" r="4" />
        </svg>
      ),
      onClick: () => navigate('/profile'),
      variant: 'secondary' as const,
      ariaLabel: 'Ver mi perfil',
    },
    {
      label: 'Configuración',
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <circle cx="12" cy="12" r="3" />
          <path d="M12 1v6m0 6v6M4.22 4.22l4.24 4.24m7.08 7.08l4.24 4.24M1 12h6m6 0h6M4.22 19.78l4.24-4.24m7.08-7.08l4.24-4.24" />
        </svg>
      ),
      onClick: () => navigate('/dashboard'),
      variant: 'secondary' as const,
      ariaLabel: 'Ir al dashboard',
    },
  ];

  return (
    <nav className="header-quick-actions" aria-label="Acciones rápidas">
      {actions.map((action) => (
        <button
          key={action.label}
          className={`header-quick-actions__button header-quick-actions__button--${action.variant}`}
          onClick={action.onClick}
          aria-label={action.ariaLabel}
          title={action.label}
          type="button"
        >
          <span className="header-quick-actions__icon" aria-hidden="true">
            {action.icon}
          </span>
          <span className="header-quick-actions__label">{action.label}</span>
        </button>
      ))}
    </nav>
  );
};

export default HeaderQuickActions;
