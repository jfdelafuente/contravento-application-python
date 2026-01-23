/**
 * ProcessingTimer Component
 *
 * Displays elapsed time during GPX processing with visual feedback.
 * Shows warning when approaching timeout threshold.
 *
 * Feature 003 - GPS Routes Interactive (Layer 2 - Visual Feedback)
 */

import React, { useState, useEffect } from 'react';
import './ProcessingTimer.css';

export interface ProcessingTimerProps {
  /** Timestamp when processing started (Date.now()) */
  startTime: number;

  /** Maximum expected processing time in seconds */
  maxSeconds: number;

  /** Processing status (for color coding) */
  status?: 'processing' | 'warning' | 'error';
}

/**
 * ProcessingTimer Component
 *
 * Shows a live countdown/countup timer for GPX processing.
 * Provides visual feedback and warnings.
 */
export const ProcessingTimer: React.FC<ProcessingTimerProps> = ({
  startTime,
  maxSeconds,
  status = 'processing',
}) => {
  const [elapsed, setElapsed] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      const now = Date.now();
      const elapsedSeconds = Math.floor((now - startTime) / 1000);
      setElapsed(elapsedSeconds);
    }, 1000);

    return () => clearInterval(interval);
  }, [startTime]);

  // Calculate progress percentage
  const progressPercent = Math.min((elapsed / maxSeconds) * 100, 100);

  // Determine status
  const isWarning = elapsed > maxSeconds * 0.7; // >70% of max time
  const isNearTimeout = elapsed > maxSeconds * 0.9; // >90% of max time

  return (
    <div className={`processing-timer processing-timer--${status}`}>
      <div className="processing-timer-header">
        <span className="processing-timer-label">Tiempo de procesamiento</span>
        <span className="processing-timer-time">
          {elapsed}s / ~{maxSeconds}s
        </span>
      </div>

      <div className="processing-timer-bar">
        <div
          className={`processing-timer-progress ${
            isNearTimeout ? 'processing-timer-progress--danger' : ''
          } ${isWarning && !isNearTimeout ? 'processing-timer-progress--warning' : ''}`}
          style={{ width: `${progressPercent}%` }}
        />
      </div>

      {isWarning && (
        <div className="processing-timer-message">
          {isNearTimeout ? (
            <span className="processing-timer-message--danger">
              ⚠️ El archivo es muy grande, procesamiento puede tardar más de lo esperado...
            </span>
          ) : (
            <span className="processing-timer-message--warning">
              El archivo es grande, puede tardar unos segundos más...
            </span>
          )}
        </div>
      )}
    </div>
  );
};
