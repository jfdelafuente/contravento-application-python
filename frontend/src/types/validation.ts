// src/types/validation.ts

export type ValidationStatus = 'idle' | 'validating' | 'valid' | 'invalid';

export interface FieldValidationState {
  /** Current validation status */
  status: ValidationStatus;

  /** Error message (if invalid) */
  message?: string;

  /** Success message (if valid and explicitly shown) */
  successMessage?: string;

  /** Whether field has been touched/blurred */
  touched: boolean;

  /** Whether field is currently being validated (async) */
  isValidating: boolean;
}

export interface FormValidationState {
  /** Map of field names to validation state */
  fields: Record<string, FieldValidationState>;

  /** Overall form validity */
  isValid: boolean;

  /** Whether form has been submitted */
  isSubmitted: boolean;
}
