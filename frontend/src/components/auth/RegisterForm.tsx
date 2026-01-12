// src/components/auth/RegisterForm.tsx

import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useDebounce } from '../../hooks/useDebounce';
import { authService } from '../../services/authService';
import { PasswordStrengthMeter } from './PasswordStrengthMeter';
import { TurnstileWidget } from './TurnstileWidget';
import type { RegisterFormData } from '../../types/forms';
import './RegisterForm.css';

// Zod validation schema
const registerSchema = z.object({
  username: z.string()
    .min(3, 'El nombre de usuario debe tener al menos 3 caracteres')
    .max(30, 'El nombre de usuario no puede exceder 30 caracteres')
    .regex(/^[a-zA-Z0-9_]+$/, 'Solo letras, números y guiones bajos'),
  email: z.string()
    .email('Formato de email inválido')
    .max(255, 'El email no puede exceder 255 caracteres'),
  password: z.string()
    .min(8, 'La contraseña debe tener al menos 8 caracteres')
    .max(128, 'La contraseña no puede exceder 128 caracteres'),
  confirmPassword: z.string(),
  turnstileToken: z.string().min(1, 'Verificación CAPTCHA requerida'),
  acceptTerms: z.boolean().refine((val) => val === true, {
    message: 'Debes aceptar los términos y condiciones',
  }),
}).refine(data => data.password === data.confirmPassword, {
  message: 'Las contraseñas no coinciden',
  path: ['confirmPassword'],
});

type RegisterFormValues = z.infer<typeof registerSchema>;

interface RegisterFormProps {
  onSuccess: () => void;
  onError: (error: string) => void;
}

export const RegisterForm: React.FC<RegisterFormProps> = ({ onSuccess, onError }) => {
  const [isSubmitting, setIsSubmitting] = useState(false);
  // Commented out - for future email/username availability checking (T033)
  // const [emailAvailable] = useState<boolean | null>(null);
  // const [usernameAvailable] = useState<boolean | null>(null);
  // const [isCheckingEmail] = useState(false);
  // const [isCheckingUsername] = useState(false);

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
    setError,
    setValue,
    clearErrors,
  } = useForm<RegisterFormValues>({
    resolver: zodResolver(registerSchema),
    mode: 'onTouched',
    defaultValues: {
      turnstileToken: '',
      acceptTerms: false,
    },
  });

  const password = watch('password');
  const email = watch('email');
  const username = watch('username');

  // Debounced email validation (T033)
  // TODO: Enable when backend endpoints are implemented
  const debouncedEmail = useDebounce(email, 500);

  useEffect(() => {
    // Temporarily disabled - backend endpoints /auth/check-email and /auth/check-username not implemented
    // const checkEmail = async () => {
    //   if (!debouncedEmail || errors.email || debouncedEmail.length === 0) {
    //     setEmailAvailable(null);
    //     return;
    //   }

    //   setIsCheckingEmail(true);
    //   try {
    //     const available = await authService.checkEmailAvailability(debouncedEmail);
    //     setEmailAvailable(available);

    //     if (!available) {
    //       setError('email', {
    //         type: 'manual',
    //         message: 'Este email ya está registrado',
    //       });
    //     } else {
    //       clearErrors('email');
    //     }
    //   } catch (error) {
    //     console.error('Error checking email:', error);
    //   } finally {
    //     setIsCheckingEmail(false);
    //   }
    // };

    // checkEmail();
  }, [debouncedEmail, errors.email, setError, clearErrors]);

  // Debounced username validation (T034)
  // TODO: Enable when backend endpoints are implemented
  const debouncedUsername = useDebounce(username, 500);

  useEffect(() => {
    // Temporarily disabled - backend endpoints /auth/check-email and /auth/check-username not implemented
    // const checkUsername = async () => {
    //   if (!debouncedUsername || errors.username || debouncedUsername.length < 3) {
    //     setUsernameAvailable(null);
    //     return;
    //   }

    //   setIsCheckingUsername(true);
    //   try {
    //     const available = await authService.checkUsernameAvailability(debouncedUsername);
    //     setUsernameAvailable(available);

    //     if (!available) {
    //       setError('username', {
    //         type: 'manual',
    //         message: 'Este nombre de usuario no está disponible',
    //       });
    //     } else {
    //       clearErrors('username');
    //     }
    //   } catch (error) {
    //     console.error('Error checking username:', error);
    //   } finally {
    //     setIsCheckingUsername(false);
    //   }
    // };

    // checkUsername();
  }, [debouncedUsername, errors.username, setError, clearErrors]);

  const handleTurnstileVerify = (token: string) => {
    setValue('turnstileToken', token);
    clearErrors('turnstileToken');
  };

  const handleTurnstileError = () => {
    setError('turnstileToken', {
      type: 'manual',
      message: 'Verificación CAPTCHA fallida. Inténtalo de nuevo.',
    });
  };

  const onSubmit = async (data: RegisterFormValues) => {
    setIsSubmitting(true);

    try {
      const registerData: RegisterFormData = {
        username: data.username,
        email: data.email,
        password: data.password,
        confirmPassword: data.confirmPassword,
        turnstileToken: data.turnstileToken,
        acceptTerms: data.acceptTerms,
      };

      await authService.register(registerData);
      onSuccess();
    } catch (error: any) {
      const errorMessage = error.response?.data?.error?.message ||
                          error.message ||
                          'Error al registrar usuario';

      // Handle field-specific errors
      if (error.response?.data?.error?.field) {
        setError(error.response.data.error.field as keyof RegisterFormValues, {
          type: 'manual',
          message: error.response.data.error.message,
        });
      }

      onError(errorMessage);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="register-form">
      {/* Username field */}
      <div className="form-group">
        <label htmlFor="username">Nombre de usuario</label>
        <input
          id="username"
          type="text"
          {...register('username')}
          placeholder="usuario123"
          className={errors.username ? 'error' : usernameAvailable ? 'success' : ''}
          aria-invalid={errors.username ? 'true' : 'false'}
          aria-describedby={errors.username ? 'username-error' : undefined}
        />
        {isCheckingUsername && <span className="checking">Verificando...</span>}
        {errors.username && (
          <span id="username-error" className="error-message" role="alert">
            {errors.username.message}
          </span>
        )}
        {usernameAvailable && !errors.username && (
          <span className="success-message">✓ Nombre de usuario disponible</span>
        )}
      </div>

      {/* Email field */}
      <div className="form-group">
        <label htmlFor="email">Email</label>
        <input
          id="email"
          type="email"
          {...register('email')}
          placeholder="tu@email.com"
          className={errors.email ? 'error' : emailAvailable ? 'success' : ''}
          aria-invalid={errors.email ? 'true' : 'false'}
          aria-describedby={errors.email ? 'email-error' : undefined}
        />
        {isCheckingEmail && <span className="checking">Verificando...</span>}
        {errors.email && (
          <span id="email-error" className="error-message" role="alert">
            {errors.email.message}
          </span>
        )}
        {emailAvailable && !errors.email && (
          <span className="success-message">✓ Email disponible</span>
        )}
      </div>

      {/* Password field with strength meter (T035) */}
      <div className="form-group">
        <label htmlFor="password">Contraseña</label>
        <input
          id="password"
          type="password"
          {...register('password')}
          placeholder="Mínimo 8 caracteres"
          className={errors.password ? 'error' : ''}
          aria-invalid={errors.password ? 'true' : 'false'}
          aria-describedby={errors.password ? 'password-error' : undefined}
        />
        {errors.password && (
          <span id="password-error" className="error-message" role="alert">
            {errors.password.message}
          </span>
        )}
        <PasswordStrengthMeter password={password || ''} />
      </div>

      {/* Confirm password field */}
      <div className="form-group">
        <label htmlFor="confirmPassword">Confirmar contraseña</label>
        <input
          id="confirmPassword"
          type="password"
          {...register('confirmPassword')}
          placeholder="Repite tu contraseña"
          className={errors.confirmPassword ? 'error' : ''}
          aria-invalid={errors.confirmPassword ? 'true' : 'false'}
          aria-describedby={errors.confirmPassword ? 'confirm-password-error' : undefined}
        />
        {errors.confirmPassword && (
          <span id="confirm-password-error" className="error-message" role="alert">
            {errors.confirmPassword.message}
          </span>
        )}
      </div>

      {/* CAPTCHA widget (T036) */}
      <div className="form-group">
        <TurnstileWidget
          onVerify={handleTurnstileVerify}
          onError={handleTurnstileError}
          action="register"
        />
        {errors.turnstileToken && (
          <span className="error-message" role="alert">
            {errors.turnstileToken.message}
          </span>
        )}
      </div>

      {/* Terms acceptance */}
      <div className="form-group checkbox-group">
        <label>
          <input type="checkbox" {...register('acceptTerms')} />
          <span>
            Acepto los <a href="/terms" target="_blank" rel="noopener noreferrer">términos y condiciones</a>
          </span>
        </label>
        {errors.acceptTerms && (
          <span className="error-message" role="alert">
            {errors.acceptTerms.message}
          </span>
        )}
      </div>

      {/* Submit button */}
      <button
        type="submit"
        disabled={isSubmitting}
        aria-busy={isSubmitting}
      >
        {isSubmitting ? 'Registrando...' : 'Crear cuenta'}
      </button>

      {/* Login link */}
      <p className="form-footer">
        ¿Ya tienes cuenta? <a href="/login">Inicia sesión</a>
      </p>
    </form>
  );
};
