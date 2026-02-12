// src/components/auth/TurnstileWidget.tsx

import React, { useRef } from 'react';
import { Turnstile, TurnstileInstance } from '@marsidev/react-turnstile';

interface TurnstileWidgetProps {
  onVerify: (token: string) => void;
  onError?: () => void;
  action?: string; // 'register' | 'login' | 'forgot-password'
}

/**
 * Cloudflare Turnstile CAPTCHA widget for bot protection
 *
 * Uses testing key by default for local development.
 * Replace with production key in .env.local for production.
 */
export const TurnstileWidget: React.FC<TurnstileWidgetProps> = ({
  onVerify,
  onError,
  action = 'register',
}) => {
  const turnstileRef = useRef<TurnstileInstance>(null);

  const handleError = () => {
    console.error('Turnstile verification failed');
    onError?.();
  };

  return (
    <div className="turnstile-widget">
      <Turnstile
        ref={turnstileRef}
        siteKey={import.meta.env.VITE_TURNSTILE_SITE_KEY}
        onSuccess={onVerify}
        onError={handleError}
        options={{
          theme: 'dark',
          size: 'normal',
          action: action,
          appearance: 'always',
        }}
      />
    </div>
  );
};
