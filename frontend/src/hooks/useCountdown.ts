// src/hooks/useCountdown.ts

import { useState, useEffect, useCallback } from 'react';

interface UseCountdownOptions {
  /** Initial seconds for countdown */
  initialSeconds: number;

  /** Callback when countdown completes */
  onComplete?: () => void;

  /** Auto-start countdown on mount */
  autoStart?: boolean;
}

interface UseCountdownReturn {
  /** Seconds remaining */
  secondsRemaining: number;

  /** Formatted time (MM:SS) */
  formattedTime: string;

  /** Whether countdown is running */
  isRunning: boolean;

  /** Start countdown */
  start: () => void;

  /** Pause countdown */
  pause: () => void;

  /** Reset to initial value */
  reset: () => void;
}

/**
 * Countdown timer hook for account blocking and verification resend
 *
 * @example
 * ```tsx
 * const { formattedTime, start } = useCountdown({
 *   initialSeconds: 900, // 15 minutes
 *   onComplete: () => console.log('Block expired'),
 * });
 *
 * useEffect(() => {
 *   start();
 * }, []);
 *
 * return <div>Time remaining: {formattedTime}</div>;
 * ```
 */
export const useCountdown = ({
  initialSeconds,
  onComplete,
  autoStart = false,
}: UseCountdownOptions): UseCountdownReturn => {
  const [secondsRemaining, setSecondsRemaining] = useState(initialSeconds);
  const [isRunning, setIsRunning] = useState(autoStart);

  useEffect(() => {
    if (!isRunning || secondsRemaining <= 0) return;

    const interval = setInterval(() => {
      setSecondsRemaining((prev) => {
        if (prev <= 1) {
          setIsRunning(false);
          onComplete?.();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(interval);
  }, [isRunning, secondsRemaining, onComplete]);

  const start = useCallback(() => {
    if (secondsRemaining > 0) {
      setIsRunning(true);
    }
  }, [secondsRemaining]);

  const pause = useCallback(() => {
    setIsRunning(false);
  }, []);

  const reset = useCallback(() => {
    setSecondsRemaining(initialSeconds);
    setIsRunning(false);
  }, [initialSeconds]);

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  return {
    secondsRemaining,
    formattedTime: formatTime(secondsRemaining),
    isRunning,
    start,
    pause,
    reset,
  };
};
