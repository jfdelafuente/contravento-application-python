/**
 * usePasswordChange Hook
 *
 * Custom hook for managing password change form state using React Hook Form
 * with Zod validation and password strength calculation.
 */

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { passwordChangeSchema } from '../utils/validators';
import type { PasswordChangeRequest } from '../types/profile';

/**
 * Initialize password change form with validation
 *
 * @returns React Hook Form methods and state
 */
export const usePasswordChange = () => {
  const {
    register,
    handleSubmit,
    watch,
    formState: { errors, isSubmitting, isDirty },
    reset,
  } = useForm<PasswordChangeRequest>({
    resolver: zodResolver(passwordChangeSchema),
    defaultValues: {
      current_password: '',
      new_password: '',
      confirm_password: '',
    },
    mode: 'onBlur',
  });

  // Watch new password for strength indicator
  const newPassword = watch('new_password');

  return {
    register,
    handleSubmit,
    errors,
    isSubmitting,
    isDirty,
    reset,
    newPassword,
  };
};

export default usePasswordChange;
