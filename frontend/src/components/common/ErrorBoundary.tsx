/**
 * ErrorBoundary Component - React Error Boundary
 *
 * Catches React errors and provides fallback UI with recovery options.
 *
 * Feature: 017-gps-trip-wizard
 * Phase: 9 (Polish)
 * Task: T095
 */

import { Component, type ErrorInfo, type ReactNode } from 'react';
import './ErrorBoundary.css';

interface ErrorBoundaryProps {
  /** Child components to wrap */
  children: ReactNode;

  /** Callback when error occurs (optional) */
  onError?: (error: Error, errorInfo: ErrorInfo) => void;

  /** Custom fallback UI (optional) */
  fallback?: (error: Error, reset: () => void) => ReactNode;
}

interface ErrorBoundaryState {
  /** Whether an error has been caught */
  hasError: boolean;

  /** The caught error */
  error: Error | null;
}

/**
 * React Error Boundary Component
 *
 * Catches unhandled errors in component tree and displays fallback UI.
 * Provides reset functionality to retry rendering.
 *
 * @example
 * ```typescript
 * <ErrorBoundary
 *   onError={(error, errorInfo) => {
 *     console.error('Error caught:', error, errorInfo);
 *   }}
 * >
 *   <GPXWizard />
 * </ErrorBoundary>
 * ```
 */
export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
    };
  }

  /**
   * Update state when error is caught
   */
  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return {
      hasError: true,
      error,
    };
  }

  /**
   * Log error details
   */
  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    // Log to console in development
    if (import.meta.env.MODE === 'development') {
      console.error('🔴 [ErrorBoundary] Caught error:', error);
      console.error('📍 [ErrorBoundary] Component stack:', errorInfo.componentStack);
    }

    // Call optional error handler
    this.props.onError?.(error, errorInfo);
  }

  /**
   * Reset error state and retry rendering
   */
  resetError = (): void => {
    this.setState({
      hasError: false,
      error: null,
    });
  };

  render(): ReactNode {
    if (this.state.hasError && this.state.error) {
      // Use custom fallback if provided
      if (this.props.fallback) {
        return this.props.fallback(this.state.error, this.resetError);
      }

      // Default fallback UI
      return (
        <div className="error-boundary" role="alert" aria-live="assertive">
          <div className="error-boundary__content">
            <div className="error-boundary__icon" aria-hidden="true">
              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                />
              </svg>
            </div>

            <h2 className="error-boundary__title">Algo salió mal</h2>

            <p className="error-boundary__message">
              Ha ocurrido un error inesperado en el asistente de creación de viajes.
            </p>

            {import.meta.env.MODE === 'development' && (
              <details className="error-boundary__details">
                <summary>Detalles técnicos</summary>
                <pre className="error-boundary__error-message">
                  {this.state.error.toString()}
                </pre>
                {this.state.error.stack && (
                  <pre className="error-boundary__stack-trace">
                    {this.state.error.stack}
                  </pre>
                )}
              </details>
            )}

            <div className="error-boundary__actions">
              <button
                onClick={this.resetError}
                className="error-boundary__button error-boundary__button--primary"
                aria-label="Reintentar cargar el asistente"
              >
                Reintentar
              </button>

              <button
                onClick={() => window.location.reload()}
                className="error-boundary__button error-boundary__button--secondary"
                aria-label="Recargar la página completa"
              >
                Recargar página
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
