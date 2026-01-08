// src/hooks/useDebounce.ts

import { useState, useEffect } from 'react';

/**
 * Debounce a value to reduce unnecessary API calls or computations
 *
 * @param value - The value to debounce
 * @param delay - Delay in milliseconds (default: 500ms)
 * @returns Debounced value
 *
 * @example
 * ```tsx
 * const [email, setEmail] = useState('');
 * const debouncedEmail = useDebounce(email, 500);
 *
 * useEffect(() => {
 *   if (debouncedEmail) {
 *     checkEmailAvailability(debouncedEmail);
 *   }
 * }, [debouncedEmail]);
 * ```
 */
export const useDebounce = <T>(value: T, delay: number = 500): T => {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    // Set up timer to update debounced value after delay
    const timer = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    // Clear timer if value changes before delay expires (cleanup)
    return () => {
      clearTimeout(timer);
    };
  }, [value, delay]);

  return debouncedValue;
};
