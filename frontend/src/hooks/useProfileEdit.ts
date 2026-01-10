/**
 * useProfileEdit Hook
 *
 * Custom hook for managing profile edit form state using React Hook Form
 * with Zod validation.
 */

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { profileEditSchema } from '../utils/validators';
import type { ProfileFormData } from '../types/profile';

/**
 * Initialize profile edit form with validation
 *
 * @param defaultValues - Initial form values from user profile
 * @returns React Hook Form methods and state
 */
export const useProfileEdit = (defaultValues?: Partial<ProfileFormData>) => {
  const {
    register,
    handleSubmit,
    watch,
    formState: { errors, isSubmitting, isDirty },
    reset,
    setValue,
  } = useForm<ProfileFormData>({
    resolver: zodResolver(profileEditSchema),
    defaultValues: {
      bio: defaultValues?.bio || '',
      location: defaultValues?.location || '',
      cycling_type: defaultValues?.cycling_type || '',
      profile_visibility: defaultValues?.profile_visibility || 'public',
      trip_visibility: defaultValues?.trip_visibility || 'public',
    },
    mode: 'onBlur', // Validate on blur for better UX
  });

  // Watch bio field for character counter
  const bio = watch('bio');
  const bioLength = bio?.length || 0;

  return {
    register,
    handleSubmit,
    watch,
    errors,
    isSubmitting,
    isDirty,
    reset,
    setValue,
    bioLength,
  };
};

export default useProfileEdit;
