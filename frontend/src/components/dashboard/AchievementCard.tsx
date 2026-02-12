import React from 'react';
import { Achievement } from '../../types/achievement';
import './AchievementCard.css';

export interface AchievementCardProps {
  achievement: Achievement;
}

/**
 * AchievementCard component - Display individual achievement with icon and status
 * Compact vertical stack: icon → name → earned date or progress
 */
const AchievementCard: React.FC<AchievementCardProps> = ({ achievement }) => {
  const {
    name,
    badge_icon,
    is_earned,
    earned_at,
    progress,
  } = achievement;

  return (
    <article className={`achievement-card ${is_earned ? 'achievement-card--earned' : 'achievement-card--locked'}`}>
      {/* Icon wrapper with checkmark badge for earned achievements */}
      <div className="achievement-card__icon-wrapper">
        <span className="achievement-card__emoji">{badge_icon}</span>
        {is_earned && (
          <div className="achievement-card__badge">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41L9 16.17z" />
            </svg>
          </div>
        )}
      </div>

      {/* Content */}
      <div className="achievement-card__content">
        <h3 className="achievement-card__name">{name}</h3>

        {is_earned && earned_at && (
          <p className="achievement-card__date">
            {new Date(earned_at).toLocaleDateString('es-ES', {
              day: 'numeric',
              month: 'short',
            })}
          </p>
        )}

        {!is_earned && progress !== undefined && progress > 0 && (
          <div className="achievement-card__progress">
            <div className="achievement-card__progress-bar">
              <div
                className="achievement-card__progress-fill"
                style={{ width: `${progress}%` }}
              />
            </div>
            <p className="achievement-card__progress-text">{progress}%</p>
          </div>
        )}

        {!is_earned && (progress === undefined || progress === 0) && (
          <p className="achievement-card__locked-text">Bloqueado</p>
        )}
      </div>
    </article>
  );
};

export default AchievementCard;
