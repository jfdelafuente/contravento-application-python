import React, { memo, useMemo } from 'react';
import { Achievement } from '../../types/achievement';
import './AchievementCard.css';

export interface AchievementCardProps {
  achievement: Achievement;
}

// rendering-hoist-jsx: Static checkmark icon hoisted outside component
const CheckmarkBadge = () => (
  <div className="achievement-card__badge">
    <svg viewBox="0 0 24 24" fill="currentColor">
      <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41L9 16.17z" />
    </svg>
  </div>
);

/**
 * AchievementCard component - Display individual achievement with icon and status
 * Compact vertical stack: icon → name → earned date or progress
 *
 * Performance optimizations:
 * - rerender-memo: Memoized to prevent re-renders when parent re-renders
 * - rendering-hoist-jsx: Checkmark badge icon hoisted outside component
 * - js-cache-property-access: Cached computed values with useMemo
 * - rendering-conditional-render: Early ternary for className
 */
const AchievementCard: React.FC<AchievementCardProps> = memo(({ achievement }) => {
  const {
    name,
    badge_icon,
    is_earned,
    earned_at,
    progress,
  } = achievement;

  // js-cache-property-access: Cache computed values
  const formattedDate = useMemo(() => {
    if (!is_earned || !earned_at) return null;
    return new Date(earned_at).toLocaleDateString('es-ES', {
      day: 'numeric',
      month: 'short',
    });
  }, [is_earned, earned_at]);

  const hasProgress = useMemo(() =>
    !is_earned && progress !== undefined && progress > 0,
    [is_earned, progress]
  );

  const isLocked = useMemo(() =>
    !is_earned && (progress === undefined || progress === 0),
    [is_earned, progress]
  );

  // rendering-conditional-render: Ternary for className
  const cardClass = is_earned
    ? 'achievement-card achievement-card--earned'
    : 'achievement-card achievement-card--locked';

  return (
    <article className={cardClass}>
      {/* Icon wrapper with checkmark badge for earned achievements */}
      <div className="achievement-card__icon-wrapper">
        <span className="achievement-card__emoji">{badge_icon}</span>
        {is_earned && <CheckmarkBadge />}
      </div>

      {/* Content */}
      <div className="achievement-card__content">
        <h3 className="achievement-card__name">{name}</h3>

        {formattedDate && (
          <p className="achievement-card__date">
            {formattedDate}
          </p>
        )}

        {hasProgress && (
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

        {isLocked && (
          <p className="achievement-card__locked-text">Bloqueado</p>
        )}
      </div>
    </article>
  );
});

AchievementCard.displayName = 'AchievementCard';

export default AchievementCard;
