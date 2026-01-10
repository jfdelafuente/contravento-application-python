// src/utils/validators.ts

/**
 * Validate email format
 */
export const validateEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

/**
 * Validate username format (3-30 alphanumeric + underscore)
 */
export const validateUsername = (username: string): boolean => {
  const usernameRegex = /^[a-zA-Z0-9_]{3,30}$/;
  return usernameRegex.test(username);
};

/**
 * Validate password length (8-128 characters)
 */
export const validatePasswordLength = (password: string): boolean => {
  return password.length >= 8 && password.length <= 128;
};

/**
 * Get email validation error message
 */
export const getEmailError = (email: string): string | null => {
  if (!email) {
    return 'El email es requerido';
  }
  if (!validateEmail(email)) {
    return 'Formato de email inválido';
  }
  return null;
};

/**
 * Get username validation error message
 */
export const getUsernameError = (username: string): string | null => {
  if (!username) {
    return 'El nombre de usuario es requerido';
  }
  if (username.length < 3) {
    return 'El nombre de usuario debe tener al menos 3 caracteres';
  }
  if (username.length > 30) {
    return 'El nombre de usuario no puede exceder 30 caracteres';
  }
  if (!validateUsername(username)) {
    return 'Solo letras, números y guiones bajos permitidos';
  }
  return null;
};

/**
 * Get password validation error message
 */
export const getPasswordError = (password: string): string | null => {
  if (!password) {
    return 'La contraseña es requerida';
  }
  if (password.length < 8) {
    return 'La contraseña debe tener al menos 8 caracteres';
  }
  if (password.length > 128) {
    return 'La contraseña no puede exceder 128 caracteres';
  }
  return null;
};

/**
 * Validate password confirmation matches
 */
export const validatePasswordConfirmation = (
  password: string,
  confirmPassword: string
): string | null => {
  if (!confirmPassword) {
    return 'Confirma tu contraseña';
  }
  if (password !== confirmPassword) {
    return 'Las contraseñas no coinciden';
  }
  return null;
};

/**
 * Sanitize user input to prevent XSS
 */
export const sanitizeInput = (input: string): string => {
  return input
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#x27;')
    .replace(/\//g, '&#x2F;');
};

// ============================================================================
// Zod Schemas for Profile Management
// ============================================================================

import { z } from 'zod';

/**
 * Profile Edit Schema
 * Validates bio, location, and cycling type fields.
 */
export const profileEditSchema = z.object({
  bio: z
    .string()
    .max(500, 'La bio no puede exceder 500 caracteres')
    .optional()
    .or(z.literal('')),
  location: z.string().optional().or(z.literal('')),
  cycling_type: z.string().optional().or(z.literal('')),
});

/**
 * Password Change Schema
 * Validates current password and new password with strength requirements.
 * Also validates password confirmation matches new password.
 */
export const passwordChangeSchema = z
  .object({
    current_password: z.string().min(1, 'Ingresa tu contraseña actual'),
    new_password: z
      .string()
      .min(8, 'Mínimo 8 caracteres')
      .regex(/[A-Z]/, 'Debe incluir al menos una mayúscula')
      .regex(/[a-z]/, 'Debe incluir al menos una minúscula')
      .regex(/\d/, 'Debe incluir al menos un número'),
    confirm_password: z.string().min(1, 'Confirma tu nueva contraseña'),
  })
  .refine((data) => data.new_password === data.confirm_password, {
    message: 'Las contraseñas no coinciden',
    path: ['confirm_password'],
  });

/**
 * Photo Upload Schema
 * Validates file size and MIME type for profile photo uploads.
 */
export const photoUploadSchema = z.object({
  file: z
    .instanceof(File)
    .refine((file) => file.size <= 5 * 1024 * 1024, 'El archivo no puede exceder 5MB')
    .refine(
      (file) => ['image/jpeg', 'image/png'].includes(file.type),
      'Solo se permiten archivos JPG o PNG'
    ),
});

/**
 * Calculate password strength
 * Returns: 'weak' | 'medium' | 'strong'
 */
export const calculatePasswordStrength = (password: string): 'weak' | 'medium' | 'strong' => {
  if (password.length < 8) return 'weak';

  let strength = 0;

  // Check length
  if (password.length >= 12) strength++;

  // Check for uppercase
  if (/[A-Z]/.test(password)) strength++;

  // Check for lowercase
  if (/[a-z]/.test(password)) strength++;

  // Check for numbers
  if (/\d/.test(password)) strength++;

  // Check for special characters
  if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) strength++;

  if (strength <= 2) return 'weak';
  if (strength <= 4) return 'medium';
  return 'strong';
};
