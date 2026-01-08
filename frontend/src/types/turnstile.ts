// src/types/turnstile.ts

export interface TurnstileOptions {
  /** Turnstile site key */
  siteKey: string;

  /** Theme (light/dark/auto) */
  theme?: 'light' | 'dark' | 'auto';

  /** Widget size */
  size?: 'normal' | 'compact';

  /** Action name (for analytics) */
  action?: string;

  /** Appearance mode */
  appearance?: 'always' | 'execute' | 'interaction-only';

  /** Language code */
  language?: string;
}

export interface TurnstileCallbacks {
  /** Called when verification succeeds */
  onSuccess: (token: string) => void;

  /** Called when verification fails */
  onError?: (error: string) => void;

  /** Called when token expires */
  onExpire?: () => void;

  /** Called when challenge loads */
  onLoad?: () => void;
}

export interface TurnstileWidgetProps extends TurnstileOptions, TurnstileCallbacks {
  /** Optional ref to Turnstile instance */
  ref?: React.Ref<TurnstileInstance>;
}

export interface TurnstileInstance {
  /** Reset the widget */
  reset: () => void;

  /** Remove the widget */
  remove: () => void;

  /** Get current token */
  getResponse: () => string | undefined;
}
