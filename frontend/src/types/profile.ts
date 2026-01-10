/**
 * Profile Management Types
 *
 * TypeScript interfaces for profile editing, photo upload, password change,
 * and privacy settings following the backend API contracts.
 */

/**
 * User Profile (from backend API)
 * Complete user profile data including bio, location, cycling preferences,
 * and privacy settings.
 */
export interface UserProfile {
  user_id: string;
  username: string;
  email: string;
  bio?: string;
  location?: string;
  cycling_type?: string;
  photo_url?: string;
  is_verified: boolean;
  profile_visibility: 'public' | 'private';
  trip_visibility: 'public' | 'followers' | 'private';
  created_at: string;
  updated_at: string;
}

/**
 * Profile Update Request
 * Data sent to backend when updating profile information.
 * All fields are optional to allow partial updates.
 */
export interface ProfileUpdateRequest {
  bio?: string;          // Max 500 characters
  location?: string;     // Free text or searchable location
  cycling_type?: string; // One of: bikepacking, road, mountain, touring, gravel
  profile_visibility?: 'public' | 'private';
  trip_visibility?: 'public' | 'followers' | 'private';
}

/**
 * Privacy Settings Update
 * Controls who can see the user's profile and trips.
 */
export interface PrivacySettingsUpdate {
  profile_visibility?: 'public' | 'private';
  trip_visibility?: 'public' | 'followers' | 'private';
}

/**
 * Password Change Request
 * Data sent to backend when changing password.
 * Requires current password verification.
 * Note: confirm_password is validated client-side only, not sent to backend.
 */
export interface PasswordChangeRequest {
  current_password: string;
  new_password: string;
  confirm_password: string;
}

/**
 * Photo Upload Response
 * Response from backend after successful photo upload.
 */
export interface PhotoUploadResponse {
  photo_url: string;
  message: string;
}

/**
 * Profile Form Data
 * Combined data for the profile edit form, including all editable fields.
 */
export interface ProfileFormData {
  bio: string;
  location: string;
  cycling_type: string;
  profile_visibility: 'public' | 'private';
  trip_visibility: 'public' | 'followers' | 'private';
}

/**
 * Password Strength Level
 * Visual indicator for password strength validation.
 */
export type PasswordStrength = 'weak' | 'medium' | 'strong';

/**
 * Cycling Type Options
 * Predefined cycling types for dropdown selection.
 */
export const CYCLING_TYPES = [
  { value: 'bikepacking', label: 'Bikepacking' },
  { value: 'road', label: 'Ciclismo de Ruta' },
  { value: 'mountain', label: 'Mountain Bike' },
  { value: 'touring', label: 'Cicloturismo' },
  { value: 'gravel', label: 'Gravel' },
] as const;
