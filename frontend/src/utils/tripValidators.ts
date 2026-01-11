/**
 * Trip Form Validation Schemas
 *
 * Zod schemas for validating trip forms and publish requirements.
 * Based on backend API contracts from Feature 002 (Travel Diary Backend).
 */

import { z } from 'zod';
import { TripDifficulty } from '../types/trip';

// ============================================================================
// Field Validators
// ============================================================================

/**
 * Title validation
 * - Required
 * - 1-200 characters
 */
const titleSchema = z
  .string()
  .min(1, 'El título es obligatorio')
  .max(200, 'El título no puede exceder 200 caracteres')
  .trim();

/**
 * Description validation (for drafts)
 * - Required
 * - 1-50000 characters
 * - No minimum length for drafts
 */
const descriptionSchema = z
  .string()
  .min(1, 'La descripción es obligatoria')
  .max(50000, 'La descripción no puede exceder 50,000 caracteres');

/**
 * Description validation (for publishing)
 * - Required
 * - 50-50000 characters
 * - Enforces minimum length for published trips
 */
const descriptionPublishSchema = z
  .string()
  .min(50, 'La descripción debe tener al menos 50 caracteres para publicar')
  .max(50000, 'La descripción no puede exceder 50,000 caracteres');

/**
 * Start date validation
 * - Required
 * - ISO 8601 format: YYYY-MM-DD
 * - Cannot be future date
 */
const startDateSchema = z
  .string()
  .min(1, 'La fecha de inicio es obligatoria')
  .refine(
    (date) => {
      const dateObj = new Date(date);
      return !isNaN(dateObj.getTime());
    },
    { message: 'La fecha de inicio no es válida' }
  )
  .refine(
    (date) => {
      const dateObj = new Date(date);
      const today = new Date();
      today.setHours(23, 59, 59, 999); // End of today
      return dateObj <= today;
    },
    { message: 'La fecha de inicio no puede ser futura' }
  );

/**
 * End date validation
 * - Optional (null allowed)
 * - ISO 8601 format: YYYY-MM-DD
 * - Must be >= start_date
 */
const endDateSchema = z
  .string()
  .optional()
  .refine(
    (date) => {
      if (!date || date === '') return true;
      const dateObj = new Date(date);
      return !isNaN(dateObj.getTime());
    },
    { message: 'La fecha de fin no es válida' }
  );

/**
 * Distance validation
 * - Optional (null allowed)
 * - 0.1-10000 km
 * - String in form, parsed to number
 */
const distanceSchema = z
  .string()
  .optional()
  .refine(
    (value) => {
      if (!value || value === '') return true;
      const num = parseFloat(value);
      return !isNaN(num) && num >= 0.1 && num <= 10000;
    },
    { message: 'La distancia debe estar entre 0.1 y 10,000 km' }
  );

/**
 * Difficulty validation
 * - Optional (empty string allowed)
 * - Must be one of: 'easy', 'moderate', 'difficult', 'very_difficult'
 */
const difficultySchema = z
  .enum(['easy', 'moderate', 'difficult', 'very_difficult', ''] as const)
  .optional();

/**
 * Tags validation
 * - Optional (empty array allowed)
 * - Max 10 tags
 * - Max 50 characters per tag
 */
const tagsSchema = z
  .array(z.string().max(50, 'Cada etiqueta no puede exceder 50 caracteres'))
  .max(10, 'Máximo 10 etiquetas permitidas')
  .optional()
  .default([]);

/**
 * Location Input validation schema
 * - name: Required, 1-200 characters
 * - country: Optional, max 100 characters
 * - latitude: Optional, -90 to 90 degrees, max 6 decimals
 * - longitude: Optional, -180 to 180 degrees, max 6 decimals
 */
export const locationInputSchema = z.object({
  name: z
    .string()
    .min(1, 'Nombre de ubicación requerido')
    .max(200, 'Nombre debe tener máximo 200 caracteres'),

  country: z.string().max(100, 'País debe tener máximo 100 caracteres').optional(),

  latitude: z
    .number()
    .min(-90, 'Latitud debe estar entre -90 y 90 grados')
    .max(90, 'Latitud debe estar entre -90 y 90 grados')
    .nullable()
    .optional()
    .refine(
      (val) => {
        if (val === null || val === undefined) return true;
        // Check max 6 decimal places
        const decimals = val.toString().split('.')[1];
        return !decimals || decimals.length <= 6;
      },
      { message: 'Latitud debe tener máximo 6 decimales' }
    ),

  longitude: z
    .number()
    .min(-180, 'Longitud debe estar entre -180 y 180 grados')
    .max(180, 'Longitud debe estar entre -180 y 180 grados')
    .nullable()
    .optional()
    .refine(
      (val) => {
        if (val === null || val === undefined) return true;
        // Check max 6 decimal places
        const decimals = val.toString().split('.')[1];
        return !decimals || decimals.length <= 6;
      },
      { message: 'Longitud debe tener máximo 6 decimales' }
    ),
});

/**
 * Inferred TypeScript type from locationInputSchema
 */
export type LocationInputFormData = z.infer<typeof locationInputSchema>;

// ============================================================================
// Form Schemas
// ============================================================================

/**
 * Trip form validation schema (for drafts and edits)
 *
 * Used in:
 * - TripFormWizard (all 4 steps)
 * - Step 1 (Basic Info) validation
 * - Step 2 (Story & Tags) validation
 *
 * @example
 * ```tsx
 * import { useForm } from 'react-hook-form';
 * import { zodResolver } from '@hookform/resolvers/zod';
 * import { tripFormSchema } from '@/utils/tripValidators';
 *
 * const form = useForm({
 *   resolver: zodResolver(tripFormSchema),
 *   defaultValues: {
 *     title: '',
 *     start_date: '',
 *     end_date: '',
 *     distance_km: '',
 *     difficulty: '',
 *     description: '',
 *     tags: [],
 *   },
 * });
 * ```
 */
export const tripFormSchema = z
  .object({
    // Step 1: Basic Info
    title: titleSchema,
    start_date: startDateSchema,
    end_date: endDateSchema,
    distance_km: distanceSchema,
    difficulty: difficultySchema,

    // Step 2: Story & Tags
    description: descriptionSchema,
    tags: tagsSchema,
  })
  .refine(
    (data) => {
      // Validate end_date >= start_date if both provided
      if (!data.end_date || data.end_date === '') return true;

      const startDate = new Date(data.start_date);
      const endDate = new Date(data.end_date);

      return endDate >= startDate;
    },
    {
      message: 'La fecha de fin debe ser posterior o igual a la fecha de inicio',
      path: ['end_date'],
    }
  );

/**
 * Trip publish validation schema
 *
 * Extends tripFormSchema with stricter requirements for publishing:
 * - Description must be at least 50 characters
 *
 * Used in:
 * - Step 4 (Review & Publish) - before calling publishTrip()
 * - Publish button validation
 *
 * @example
 * ```tsx
 * import { tripPublishSchema } from '@/utils/tripValidators';
 *
 * const handlePublish = async () => {
 *   // Validate form data meets publish requirements
 *   const result = tripPublishSchema.safeParse(formData);
 *
 *   if (!result.success) {
 *     toast.error(result.error.issues[0].message);
 *     return;
 *   }
 *
 *   await publishTrip(tripId);
 * };
 * ```
 */
export const tripPublishSchema = z
  .object({
    // Step 1: Basic Info
    title: titleSchema,
    start_date: startDateSchema,
    end_date: endDateSchema,
    distance_km: distanceSchema,
    difficulty: difficultySchema,

    // Step 2: Story & Tags (stricter validation)
    description: descriptionPublishSchema, // 50-char minimum
    tags: tagsSchema,
  })
  .refine(
    (data) => {
      // Validate end_date >= start_date if both provided
      if (!data.end_date || data.end_date === '') return true;

      const startDate = new Date(data.start_date);
      const endDate = new Date(data.end_date);

      return endDate >= startDate;
    },
    {
      message: 'La fecha de fin debe ser posterior o igual a la fecha de inicio',
      path: ['end_date'],
    }
  );

// ============================================================================
// Type Exports
// ============================================================================

/**
 * Inferred TypeScript type from tripFormSchema
 */
export type TripFormInput = z.infer<typeof tripFormSchema>;

/**
 * Inferred TypeScript type from tripPublishSchema
 */
export type TripPublishInput = z.infer<typeof tripPublishSchema>;
