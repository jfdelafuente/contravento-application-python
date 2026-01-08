// src/components/auth/AccountBlockedMessage.tsx

import React, { useEffect } from 'react';
import { useCountdown } from '../../hooks/useCountdown';
import './AccountBlockedMessage.css';

interface AccountBlockedMessageProps {
  /** ISO timestamp when block expires */
  blockedUntil: string;
  /** Callback when block expires */
  onUnblock: () => void;
  /** Number of failed attempts (optional) */
  attemptCount?: number;
}

/**
 * Account blocked message with MM:SS countdown timer
 *
 * Shows when user exceeds max login attempts (5 failed = 15min block)
 */
export const AccountBlockedMessage: React.FC<AccountBlockedMessageProps> = ({
  blockedUntil,
  onUnblock,
  attemptCount = 5,
}) => {
  const blockedUntilDate = new Date(blockedUntil);
  const initialSeconds = Math.max(0, Math.floor((blockedUntilDate.getTime() - Date.now()) / 1000));

  const { formattedTime, start, secondsRemaining } = useCountdown({
    initialSeconds,
    onComplete: onUnblock,
  });

  useEffect(() => {
    start(); // Auto-start countdown on mount
  }, [start]);

  if (secondsRemaining === 0) return null;

  return (
    <div className="account-blocked-alert" role="alert">
      <div className="alert-icon">
        <svg
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
          />
        </svg>
      </div>

      <div className="alert-content">
        <h3>Cuenta bloqueada temporalmente</h3>
        <p>
          Has superado el número máximo de intentos de inicio de sesión ({attemptCount} intentos).
        </p>
        <p className="countdown">
          Tiempo restante: <strong className="countdown-timer">{formattedTime}</strong>
        </p>
        <p className="help-text">
          Por tu seguridad, inténtalo de nuevo cuando expire el tiempo o{' '}
          <a href="/forgot-password">recupera tu contraseña</a>.
        </p>
      </div>
    </div>
  );
};
