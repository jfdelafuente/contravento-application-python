/**
 * Trip Details Form Validation Schema
 *
 * Zod schema for validating trip details form in wizard Step 2.
 * Includes Spanish error messages and field constraints.
 *
 * Feature: 017-gps-trip-wizard
 * Phase: 5 (US3)
 * Tasks: T058, T059
 */

import { z } from 'zod';

/**
 * Trip Details Form Data Schema
 *
 * Validation rules:
 * - title: Required, max 200 characters
 * - description: Required, min 50 characters
 * - start_date: Required, YYYY-MM-DD format
 * - end_date: Optional, YYYY-MM-DD format
 * - privacy: Required, 'public' or 'private'
 */
export const tripDetailsSchema = z.object({
  title: z
    .string()
    .min(1, 'El título es obligatorio')
    .max(200, 'El título no puede superar 200 caracteres'),

  description: z
    .string()
    .min(50, 'La descripción debe tener al menos 50 caracteres')
    .max(5000, 'La descripción no puede superar 5000 caracteres'),

  start_date: z
    .string()
    .min(1, 'La fecha de inicio es obligatoria')
    .regex(/^\d{4}-\d{2}-\d{2}$/, 'Formato de fecha inválido (debe ser YYYY-MM-DD)'),

  end_date: z
    .string()
    .regex(/^\d{4}-\d{2}-\d{2}$/, 'Formato de fecha inválido (debe ser YYYY-MM-DD)')
    .optional()
    .nullable()
    .or(z.literal('')),

  privacy: z.enum(['public', 'private'], {
    errorMap: () => ({ message: 'La privacidad debe ser "public" o "private"' }),
  }),
});

/**
 * TypeScript type inferred from schema
 */
export type TripDetailsFormData = z.infer<typeof tripDetailsSchema>;
