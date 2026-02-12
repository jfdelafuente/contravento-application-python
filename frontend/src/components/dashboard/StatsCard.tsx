import React from 'react';
import SkeletonLoader from '../common/SkeletonLoader';
import './StatsCard.css';

export interface StatsCardProps {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  subtitle?: string;
  loading?: boolean;
  error?: string;
  color?: string;
}

/**
 * StatsCard component - Display individual statistic with icon
 * Supports loading skeleton and error states
 */
const StatsCard: React.FC<StatsCardProps> = ({
  title,
  value,
  icon,
  subtitle,
  loading = false,
  error,
  color = 'var(--color-primary)',
}) => {
  if (loading) {
    return (
      <div className="stats-card stats-card--loading" aria-busy="true">
        <div className="stats-card__icon-wrapper">
          <SkeletonLoader variant="circle" width="48px" height="48px" />
        </div>
        <div className="stats-card__content">
          <SkeletonLoader variant="text" width="60%" height="0.875rem" />
          <SkeletonLoader variant="text" width="80%" height="1.75rem" />
          {subtitle && <SkeletonLoader variant="text" width="50%" height="0.75rem" />}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="stats-card stats-card--error" role="alert">
        <div className="stats-card__icon-wrapper" style={{ color: 'var(--color-error)' }}>
          <svg
            width="48"
            height="48"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
          >
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="8" x2="12" y2="12" />
            <line x1="12" y1="16" x2="12.01" y2="16" />
          </svg>
        </div>
        <div className="stats-card__content">
          <p className="stats-card__title">{title}</p>
          <p className="stats-card__error-message">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="stats-card">
      <div className="stats-card__icon-wrapper" style={{ color }}>
        {icon}
      </div>
      <div className="stats-card__content">
        <p className="stats-card__title">{title}</p>
        <p className="stats-card__value">{value}</p>
        {subtitle && <p className="stats-card__subtitle">{subtitle}</p>}
      </div>
    </div>
  );
};

export default StatsCard;
