/**
 * PhotoCropModal
 *
 * Modal component for cropping profile photos using react-easy-crop.
 * Features zoom control, rotation, and preview of cropped area.
 */

import React, { useState, useCallback } from 'react';
import Cropper from 'react-easy-crop';
import type { Area, Point } from 'react-easy-crop';
import './PhotoCropModal.css';

export interface PhotoCropModalProps {
  /** Photo URL or blob URL to crop */
  photoUrl: string;
  /** Callback when user saves the crop */
  onSave: (croppedArea: Area) => void;
  /** Callback when user cancels */
  onCancel: () => void;
  /** Whether the save action is loading */
  isSaving?: boolean;
}

export const PhotoCropModal: React.FC<PhotoCropModalProps> = ({
  photoUrl,
  onSave,
  onCancel,
  isSaving = false,
}) => {
  const [crop, setCrop] = useState<Point>({ x: 0, y: 0 });
  const [zoom, setZoom] = useState(1);
  const [rotation, setRotation] = useState(0);
  const [croppedAreaPixels, setCroppedAreaPixels] = useState<Area | null>(null);

  const onCropComplete = useCallback((croppedArea: Area, croppedAreaPixels: Area) => {
    setCroppedAreaPixels(croppedAreaPixels);
  }, []);

  const handleSave = () => {
    if (croppedAreaPixels) {
      onSave(croppedAreaPixels);
    }
  };

  const handleZoomChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setZoom(Number(e.target.value));
  };

  const handleRotationChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setRotation(Number(e.target.value));
  };

  return (
    <div className="photo-crop-modal-overlay" onClick={onCancel}>
      <div className="photo-crop-modal" onClick={(e) => e.stopPropagation()}>
        <div className="photo-crop-header">
          <h2 className="photo-crop-title">Recortar Foto</h2>
          <button
            type="button"
            className="photo-crop-close"
            onClick={onCancel}
            disabled={isSaving}
            aria-label="Cerrar modal"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        </div>

        {/* Crop Area */}
        <div className="photo-crop-container">
          <Cropper
            image={photoUrl}
            crop={crop}
            zoom={zoom}
            rotation={rotation}
            aspect={1}
            cropShape="round"
            showGrid={false}
            onCropChange={setCrop}
            onZoomChange={setZoom}
            onRotationChange={setRotation}
            onCropComplete={onCropComplete}
          />
        </div>

        {/* Controls */}
        <div className="photo-crop-controls">
          {/* Zoom Control */}
          <div className="control-group">
            <label htmlFor="zoom-slider" className="control-label">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                className="control-icon"
              >
                <circle cx="11" cy="11" r="8" />
                <line x1="21" y1="21" x2="16.65" y2="16.65" />
                <line x1="11" y1="8" x2="11" y2="14" />
                <line x1="8" y1="11" x2="14" y2="11" />
              </svg>
              Zoom
            </label>
            <input
              id="zoom-slider"
              type="range"
              min="1"
              max="3"
              step="0.1"
              value={zoom}
              onChange={handleZoomChange}
              className="control-slider"
              disabled={isSaving}
            />
            <span className="control-value">{zoom.toFixed(1)}x</span>
          </div>

          {/* Rotation Control */}
          <div className="control-group">
            <label htmlFor="rotation-slider" className="control-label">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                className="control-icon"
              >
                <polyline points="23 4 23 10 17 10" />
                <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10" />
              </svg>
              Rotación
            </label>
            <input
              id="rotation-slider"
              type="range"
              min="0"
              max="360"
              step="1"
              value={rotation}
              onChange={handleRotationChange}
              className="control-slider"
              disabled={isSaving}
            />
            <span className="control-value">{rotation}°</span>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="photo-crop-actions">
          <button
            type="button"
            className="btn-crop-cancel"
            onClick={onCancel}
            disabled={isSaving}
          >
            Cancelar
          </button>
          <button
            type="button"
            className="btn-crop-save"
            onClick={handleSave}
            disabled={isSaving || !croppedAreaPixels}
          >
            {isSaving ? (
              <>
                <span className="spinner"></span>
                Guardando...
              </>
            ) : (
              'Guardar'
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default PhotoCropModal;
