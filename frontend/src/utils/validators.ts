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
