/**
 * useUnsavedChanges Hook
 *
 * Custom hook to warn users about unsaved changes when navigating away
 * from a form. Uses browser's beforeunload event to show native confirmation
 * dialog.
 */

import { useEffect } from 'react';

/**
 * Warn user before leaving page if there are unsaved changes
 *
 * @param isDirty - Whether the form has unsaved changes
 * @param message - Optional custom warning message (browser may not show it)
 */
export const useUnsavedChanges = (isDirty: boolean, message?: string): void => {
  useEffect(() => {
    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      if (isDirty) {
        // Modern browsers ignore custom messages for security reasons
        // They show their own generic message instead
        e.preventDefault();
        e.returnValue = message || '';
        return message || '';
      }
    };

    // Add event listener when form is dirty
    if (isDirty) {
      window.addEventListener('beforeunload', handleBeforeUnload);
    }

    // Cleanup: remove event listener
    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
    };
  }, [isDirty, message]);
};

export default useUnsavedChanges;
