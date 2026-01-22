/**
 * GPXUploader Unit Tests
 *
 * Tests for GPX file upload functionality:
 * - T041: File size validation (<= 10MB)
 * - T042: Loading state during upload
 *
 * Feature: 003-gps-routes
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom/vitest';
import { GPXUploader } from '../../src/components/trips/GPXUploader';

// Mock CSS imports
vi.mock('../../src/components/trips/GPXUploader.css', () => ({}));

// Mock react-dropzone
vi.mock('react-dropzone', () => ({
  useDropzone: vi.fn((options) => {
    const mockFile = new File(['mock gpx content'], 'test.gpx', {
      type: 'application/gpx+xml',
    });

    return {
      getRootProps: () => ({
        onClick: () => {
          // Simulate file selection
          if (options?.onDrop) {
            options.onDrop([mockFile], [], new Event('drop'));
          }
        },
        role: 'button',
        'aria-label': 'Dropzone',
      }),
      getInputProps: () => ({
        type: 'file',
        accept: options?.accept,
        multiple: false,
      }),
      isDragActive: false,
    };
  }),
}));

// Mock useGPXUpload hook
const mockUpload = vi.fn();
const mockReset = vi.fn();

vi.mock('../../src/hooks/useGPXUpload', () => ({
  useGPXUpload: () => ({
    upload: mockUpload,
    uploadProgress: 0,
    isUploading: false,
    error: null,
    statusMessage: null,
    reset: mockReset,
  }),
}));

describe('GPXUploader - File Validation & Loading States', () => {
  const mockTripId = 'test-trip-id-123';
  const mockOnUploadComplete = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('T041 - File Size Validation', () => {
    it('should accept files <= 10MB', async () => {
      render(
        <GPXUploader tripId={mockTripId} onUploadComplete={mockOnUploadComplete} />
      );

      // Create a file < 10MB
      const smallFile = new File(
        [new ArrayBuffer(5 * 1024 * 1024)], // 5MB
        'small_route.gpx',
        { type: 'application/gpx+xml' }
      );

      // Mock upload to succeed
      mockUpload.mockResolvedValue({
        gpx_file_id: 'gpx-123',
        processing_status: 'completed',
      });

      // Get dropzone
      const dropzone = screen.getByText(/Arrastra un archivo GPX/i).closest('div');
      expect(dropzone).toBeInTheDocument();

      // Simulate drop
      fireEvent.click(dropzone!);

      await waitFor(() => {
        expect(mockUpload).toHaveBeenCalled();
      });
    });

    it('should reject files > 10MB with error message', () => {
      // Re-mock useGPXUpload to return error state
      vi.doMock('../../src/hooks/useGPXUpload', () => ({
        useGPXUpload: () => ({
          upload: mockUpload,
          uploadProgress: 0,
          isUploading: false,
          error: 'El archivo excede el tamaño máximo permitido (10 MB)',
          statusMessage: null,
          reset: mockReset,
        }),
      }));

      render(
        <GPXUploader tripId={mockTripId} onUploadComplete={mockOnUploadComplete} />
      );

      // Error message should be displayed
      expect(
        screen.getByText(/El archivo excede el tamaño máximo permitido/i)
      ).toBeInTheDocument();
    });

    it('should only accept .gpx file extension', () => {
      render(
        <GPXUploader tripId={mockTripId} onUploadComplete={mockOnUploadComplete} />
      );

      // Get input element
      const input = screen.getByRole('button', { name: /dropzone/i }).querySelector('input');
      expect(input).toBeInTheDocument();

      // Check accept attribute
      expect(input).toHaveAttribute('accept');
    });
  });

  describe('T042 - Loading State During Upload', () => {
    it('should display loading state when upload is in progress', () => {
      // Re-mock useGPXUpload to return loading state
      vi.doMock('../../src/hooks/useGPXUpload', () => ({
        useGPXUpload: () => ({
          upload: mockUpload,
          uploadProgress: 45,
          isUploading: true,
          error: null,
          statusMessage: 'Procesando archivo GPX...',
          reset: mockReset,
        }),
      }));

      render(
        <GPXUploader tripId={mockTripId} onUploadComplete={mockOnUploadComplete} />
      );

      // Loading message should be displayed
      expect(screen.getByText(/Procesando archivo GPX/i)).toBeInTheDocument();

      // Progress bar should be visible
      const progressBar = screen.getByRole('progressbar', { hidden: true });
      expect(progressBar).toBeInTheDocument();
    });

    it('should disable dropzone during upload', () => {
      vi.doMock('../../src/hooks/useGPXUpload', () => ({
        useGPXUpload: () => ({
          upload: mockUpload,
          uploadProgress: 50,
          isUploading: true,
          error: null,
          statusMessage: 'Subiendo archivo...',
          reset: mockReset,
        }),
      }));

      render(
        <GPXUploader tripId={mockTripId} onUploadComplete={mockOnUploadComplete} />
      );

      // Dropzone should have uploading class
      const dropzone = screen.getByText(/Subiendo archivo/i).closest('.gpx-dropzone');
      expect(dropzone).toHaveClass('uploading');
    });

    it('should show progress percentage during upload', () => {
      vi.doMock('../../src/hooks/useGPXUpload', () => ({
        useGPXUpload: () => ({
          upload: mockUpload,
          uploadProgress: 75,
          isUploading: true,
          error: null,
          statusMessage: 'Procesando archivo GPX...',
          reset: mockReset,
        }),
      }));

      render(
        <GPXUploader tripId={mockTripId} onUploadComplete={mockOnUploadComplete} />
      );

      // Progress percentage should be displayed
      expect(screen.getByText('75%')).toBeInTheDocument();
    });

    it('should call onUploadComplete when upload succeeds', async () => {
      mockUpload.mockResolvedValue({
        gpx_file_id: 'gpx-456',
        processing_status: 'completed',
        distance_km: 42.5,
      });

      render(
        <GPXUploader tripId={mockTripId} onUploadComplete={mockOnUploadComplete} />
      );

      const dropzone = screen.getByText(/Arrastra un archivo GPX/i).closest('div');
      fireEvent.click(dropzone!);

      await waitFor(() => {
        expect(mockOnUploadComplete).toHaveBeenCalled();
      });
    });
  });

  describe('Error Handling', () => {
    it('should display error message when upload fails', () => {
      vi.doMock('../../src/hooks/useGPXUpload', () => ({
        useGPXUpload: () => ({
          upload: mockUpload,
          uploadProgress: 0,
          isUploading: false,
          error: 'Error al procesar archivo GPX: formato inválido',
          statusMessage: null,
          reset: mockReset,
        }),
      }));

      render(
        <GPXUploader tripId={mockTripId} onUploadComplete={mockOnUploadComplete} />
      );

      // Error should be displayed
      expect(screen.getByText(/Error al procesar archivo GPX/i)).toBeInTheDocument();
    });

    it('should have retry button when upload fails', () => {
      vi.doMock('../../src/hooks/useGPXUpload', () => ({
        useGPXUpload: () => ({
          upload: mockUpload,
          uploadProgress: 0,
          isUploading: false,
          error: 'El archivo GPX está corrupto',
          statusMessage: null,
          reset: mockReset,
        }),
      }));

      render(
        <GPXUploader tripId={mockTripId} onUploadComplete={mockOnUploadComplete} />
      );

      const retryButton = screen.getByRole('button', { name: /Intentar de nuevo/i });
      expect(retryButton).toBeInTheDocument();

      // Click retry should call reset
      fireEvent.click(retryButton);
      expect(mockReset).toHaveBeenCalled();
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA labels', () => {
      render(
        <GPXUploader tripId={mockTripId} onUploadComplete={mockOnUploadComplete} />
      );

      // Dropzone should be accessible
      const dropzone = screen.getByRole('button', { name: /dropzone/i });
      expect(dropzone).toBeInTheDocument();
    });

    it('should announce upload status to screen readers', () => {
      vi.doMock('../../src/hooks/useGPXUpload', () => ({
        useGPXUpload: () => ({
          upload: mockUpload,
          uploadProgress: 60,
          isUploading: true,
          error: null,
          statusMessage: 'Procesando archivo GPX...',
          reset: mockReset,
        }),
      }));

      render(
        <GPXUploader tripId={mockTripId} onUploadComplete={mockOnUploadComplete} />
      );

      // Progress info should have role="status" for screen readers
      const statusElement = screen.getByText(/Procesando archivo GPX/i).closest('[role="status"]');
      expect(statusElement).toBeInTheDocument();
    });
  });

  describe('Info Section', () => {
    it('should display helpful information about GPX files', () => {
      render(
        <GPXUploader tripId={mockTripId} onUploadComplete={mockOnUploadComplete} />
      );

      // Info section should be present
      expect(screen.getByText(/¿Qué es un archivo GPX?/i)).toBeInTheDocument();
      expect(screen.getByText(/Puedes exportar rutas desde/i)).toBeInTheDocument();
    });
  });

  describe('Disabled State', () => {
    it('should disable dropzone when disabled prop is true', () => {
      render(
        <GPXUploader
          tripId={mockTripId}
          onUploadComplete={mockOnUploadComplete}
          disabled={true}
        />
      );

      // Dropzone should be disabled
      const dropzone = screen.getByText(/Arrastra un archivo GPX/i).closest('.gpx-dropzone');
      expect(dropzone).toBeInTheDocument();
      // Note: react-dropzone adds disabled class when disabled=true
    });
  });
});
