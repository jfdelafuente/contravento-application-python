import React, { memo } from 'react';
import './QuickActionButton.css';

export interface QuickActionButtonProps {
  label: string;
  icon: React.ReactNode;
  onClick: () => void;
  variant?: 'primary' | 'secondary';
}

/**
 * QuickActionButton component - Button for quick access to key features
 * Used in dashboard for common user actions
 *
 * Performance optimizations:
 * - rerender-memo: Memoized to prevent unnecessary re-renders when parent re-renders
 */
const QuickActionButton: React.FC<QuickActionButtonProps> = memo(({
  label,
  icon,
  onClick,
  variant = 'secondary',
}) => {
  return (
    <button
      type="button"
      className={`quick-action-button quick-action-button--${variant}`}
      onClick={onClick}
      aria-label={label}
    >
      <div className="quick-action-button__icon">{icon}</div>
      <span className="quick-action-button__label">{label}</span>
    </button>
  );
});

QuickActionButton.displayName = 'QuickActionButton';

export default QuickActionButton;
