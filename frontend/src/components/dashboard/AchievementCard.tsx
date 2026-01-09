import React from 'react';
import { Achievement } from '../../types/achievement';
import './AchievementCard.css';

export interface AchievementCardProps {
  achievement: Achievement;
}

/**
 * AchievementCard component - Display individual achievement with icon and details
 * Shows earned state with badge icon or locked state with progress
 */
const AchievementCard: React.FC<AchievementCardProps> = ({ achievement }) => {
  const {
    name,
    description,
    badge_icon,
    is_earned,
    earned_at,
    progress,
  } = achievement;

  return (
    <article className={`achievement-card ${is_earned ? 'achievement-card--earned' : 'achievement-card--locked'}`}>
      <div className="achievement-card__icon-wrapper">
        <div className="achievement-card__icon">
          <span className="achievement-card__emoji">{badge_icon}</span>
        </div>
        {is_earned && (
          <div className="achievement-card__badge">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41L9 16.17z" />
            </svg>
          </div>
        )}
      </div>

      <div className="achievement-card__content">
        <h3 className="achievement-card__name">{name}</h3>
        <p className="achievement-card__description">{description}</p>

        {is_earned && earned_at && (
          <span className="achievement-card__date">
            Desbloqueado {new Date(earned_at).toLocaleDateString('es-ES', {
              day: 'numeric',
              month: 'short',
              year: 'numeric'
            })}
          </span>
        )}

        {!is_earned && progress !== undefined && progress > 0 && (
          <div className="achievement-card__progress">
            <div className="achievement-card__progress-bar">
              <div
                className="achievement-card__progress-fill"
                style={{ width: `${progress}%` }}
              />
            </div>
            <span className="achievement-card__progress-text">{progress}%</span>
          </div>
        )}
      </div>
    </article>
  );
};

export default AchievementCard;
