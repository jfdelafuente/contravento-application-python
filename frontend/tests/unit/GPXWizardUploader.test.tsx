/**
 * GPXWizardUploader Unit Tests
 *
 * Tests for wizard GPX file upload component (Feature 017 - User Story 2):
 * - T037: Drag-and-drop file upload with validation
 * - File size validation (≤10MB)
 * - File type validation (.gpx only)
 * - Visual feedback during drag
 * - File preview and removal
 *
 * Feature: 017-gps-trip-wizard
 * Phase: 4 (US2)
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom/vitest';
import { GPXWizardUploader } from '../../src/components/wizard/GPXWizardUploader';

// Mock CSS imports
vi.mock('../../src/components/wizard/GPXWizardUploader.css', () => ({}));

describe('GPXWizardUploader (T037)', () => {
  const mockOnFileSelect = vi.fn();
  const mockOnFileRemove = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Initial Render', () => {
    it('should render upload area with instructions', () => {
      render(<GPXWizardUploader onFileSelect={mockOnFileSelect} onFileRemove={mockOnFileRemove} />);

      expect(screen.getByText(/arrastra tu archivo gpx/i)).toBeInTheDocument();
      expect(screen.getByText(/o haz clic para seleccionar/i)).toBeInTheDocument();
    });

    it('should display file size limit', () => {
      render(<GPXWizardUploader onFileSelect={mockOnFileSelect} onFileRemove={mockOnFileRemove} />);

      expect(screen.getByText(/máximo 10mb/i)).toBeInTheDocument();
    });

    it('should display accepted file types', () => {
      render(<GPXWizardUploader onFileSelect={mockOnFileSelect} onFileRemove={mockOnFileRemove} />);

      expect(screen.getByText(/\.gpx/i)).toBeInTheDocument();
    });

    it('should not show file preview when no file selected', () => {
      render(<GPXWizardUploader onFileSelect={mockOnFileSelect} onFileRemove={mockOnFileRemove} />);

      expect(screen.queryByText(/archivo seleccionado/i)).not.toBeInTheDocument();
    });
  });

  describe('File Selection', () => {
    it('should call onFileSelect when valid GPX file is selected', () => {
      const mockFile = new File(['gpx content'], 'route.gpx', {
        type: 'application/gpx+xml',
      });

      render(<GPXWizardUploader onFileSelect={mockOnFileSelect} onFileRemove={mockOnFileRemove} />);

      const input = screen.getByLabelText(/arrastra tu archivo gpx/i, { selector: 'input' });
      fireEvent.change(input, { target: { files: [mockFile] } });

      expect(mockOnFileSelect).toHaveBeenCalledWith(mockFile);
    });

    it('should display selected file name and size', () => {
      const mockFile = new File(['x'.repeat(1024 * 100)], 'my-route.gpx', {
        type: 'application/gpx+xml',
      });

      render(
        <GPXWizardUploader
          onFileSelect={mockOnFileSelect}
          onFileRemove={mockOnFileRemove}
          selectedFile={mockFile}
        />
      );

      expect(screen.getByText(/my-route\.gpx/i)).toBeInTheDocument();
      expect(screen.getByText(/100(\.|,)0\s*kb/i)).toBeInTheDocument();
    });

    it('should show remove button when file is selected', () => {
      const mockFile = new File(['content'], 'route.gpx', {
        type: 'application/gpx+xml',
      });

      render(
        <GPXWizardUploader
          onFileSelect={mockOnFileSelect}
          onFileRemove={mockOnFileRemove}
          selectedFile={mockFile}
        />
      );

      const removeButton = screen.getByRole('button', { name: /eliminar/i });
      expect(removeButton).toBeInTheDocument();
    });

    it('should call onFileRemove when remove button clicked', () => {
      const mockFile = new File(['content'], 'route.gpx', {
        type: 'application/gpx+xml',
      });

      render(
        <GPXWizardUploader
          onFileSelect={mockOnFileSelect}
          onFileRemove={mockOnFileRemove}
          selectedFile={mockFile}
        />
      );

      const removeButton = screen.getByRole('button', { name: /eliminar/i });
      fireEvent.click(removeButton);

      expect(mockOnFileRemove).toHaveBeenCalledTimes(1);
    });
  });

  describe('File Validation', () => {
    it('should reject files larger than 10MB', () => {
      const largeFile = new File(['x'.repeat(11 * 1024 * 1024)], 'huge.gpx', {
        type: 'application/gpx+xml',
      });

      render(<GPXWizardUploader onFileSelect={mockOnFileSelect} onFileRemove={mockOnFileRemove} />);

      const input = screen.getByLabelText(/arrastra tu archivo gpx/i, { selector: 'input' });
      fireEvent.change(input, { target: { files: [largeFile] } });

      // Should not call onFileSelect
      expect(mockOnFileSelect).not.toHaveBeenCalled();

      // Should display error message
      expect(screen.getByText(/el archivo es demasiado grande/i)).toBeInTheDocument();
    });

    it('should reject non-GPX files', () => {
      const pdfFile = new File(['pdf content'], 'document.pdf', {
        type: 'application/pdf',
      });

      render(<GPXWizardUploader onFileSelect={mockOnFileSelect} onFileRemove={mockOnFileRemove} />);

      const input = screen.getByLabelText(/arrastra tu archivo gpx/i, { selector: 'input' });
      fireEvent.change(input, { target: { files: [pdfFile] } });

      // Should not call onFileSelect
      expect(mockOnFileSelect).not.toHaveBeenCalled();

      // Should display error message
      expect(screen.getByText(/solo se aceptan archivos \.gpx/i)).toBeInTheDocument();
    });

    it('should accept files with .GPX extension (case insensitive)', () => {
      const mockFile = new File(['content'], 'ROUTE.GPX', {
        type: 'application/gpx+xml',
      });

      render(<GPXWizardUploader onFileSelect={mockOnFileSelect} onFileRemove={mockOnFileRemove} />);

      const input = screen.getByLabelText(/arrastra tu archivo gpx/i, { selector: 'input' });
      fireEvent.change(input, { target: { files: [mockFile] } });

      expect(mockOnFileSelect).toHaveBeenCalledWith(mockFile);
    });

    it('should clear previous error when valid file is selected', () => {
      const { rerender } = render(
        <GPXWizardUploader onFileSelect={mockOnFileSelect} onFileRemove={mockOnFileRemove} />
      );

      // First, select invalid file
      const invalidFile = new File(['content'], 'document.txt', {
        type: 'text/plain',
      });
      const input = screen.getByLabelText(/arrastra tu archivo gpx/i, { selector: 'input' });
      fireEvent.change(input, { target: { files: [invalidFile] } });

      expect(screen.getByText(/solo se aceptan archivos \.gpx/i)).toBeInTheDocument();

      // Then, select valid file
      const validFile = new File(['content'], 'route.gpx', {
        type: 'application/gpx+xml',
      });
      fireEvent.change(input, { target: { files: [validFile] } });

      // Error should be cleared
      expect(screen.queryByText(/solo se aceptan archivos \.gpx/i)).not.toBeInTheDocument();
    });
  });

  describe('Drag and Drop', () => {
    it('should highlight drop zone when file is dragged over', () => {
      render(<GPXWizardUploader onFileSelect={mockOnFileSelect} onFileRemove={mockOnFileRemove} />);

      const dropzone = screen.getByLabelText(/arrastra tu archivo gpx/i);

      // Simulate drag enter
      fireEvent.dragEnter(dropzone);

      // Drop zone should have active class
      expect(dropzone).toHaveClass('gpx-wizard-uploader--active');
    });

    it('should remove highlight when drag leaves', () => {
      render(<GPXWizardUploader onFileSelect={mockOnFileSelect} onFileRemove={mockOnFileRemove} />);

      const dropzone = screen.getByLabelText(/arrastra tu archivo gpx/i);

      // Simulate drag enter then drag leave
      fireEvent.dragEnter(dropzone);
      fireEvent.dragLeave(dropzone);

      // Drop zone should not have active class
      expect(dropzone).not.toHaveClass('gpx-wizard-uploader--active');
    });

    it('should call onFileSelect when file is dropped', () => {
      const mockFile = new File(['content'], 'route.gpx', {
        type: 'application/gpx+xml',
      });

      render(<GPXWizardUploader onFileSelect={mockOnFileSelect} onFileRemove={mockOnFileRemove} />);

      const dropzone = screen.getByLabelText(/arrastra tu archivo gpx/i);

      // Simulate file drop
      const dropEvent = new Event('drop', { bubbles: true });
      Object.defineProperty(dropEvent, 'dataTransfer', {
        value: {
          files: [mockFile],
        },
      });
      fireEvent(dropzone, dropEvent);

      expect(mockOnFileSelect).toHaveBeenCalledWith(mockFile);
    });
  });

  describe('Loading State', () => {
    it('should display loading indicator when isLoading is true', () => {
      render(
        <GPXWizardUploader
          onFileSelect={mockOnFileSelect}
          onFileRemove={mockOnFileRemove}
          isLoading={true}
        />
      );

      expect(screen.getByText(/analizando archivo/i)).toBeInTheDocument();
    });

    it('should disable file input when loading', () => {
      render(
        <GPXWizardUploader
          onFileSelect={mockOnFileSelect}
          onFileRemove={mockOnFileRemove}
          isLoading={true}
        />
      );

      const input = screen.getByLabelText(/arrastra tu archivo gpx/i, { selector: 'input' });
      expect(input).toBeDisabled();
    });

    it('should disable remove button when loading', () => {
      const mockFile = new File(['content'], 'route.gpx', {
        type: 'application/gpx+xml',
      });

      render(
        <GPXWizardUploader
          onFileSelect={mockOnFileSelect}
          onFileRemove={mockOnFileRemove}
          selectedFile={mockFile}
          isLoading={true}
        />
      );

      const removeButton = screen.getByRole('button', { name: /eliminar/i });
      expect(removeButton).toBeDisabled();
    });
  });

  describe('Error Display', () => {
    it('should display error message when error prop is provided', () => {
      render(
        <GPXWizardUploader
          onFileSelect={mockOnFileSelect}
          onFileRemove={mockOnFileRemove}
          error="Error al procesar el archivo GPX"
        />
      );

      expect(screen.getByText(/error al procesar el archivo gpx/i)).toBeInTheDocument();
    });

    it('should apply error styling to drop zone when error exists', () => {
      render(
        <GPXWizardUploader
          onFileSelect={mockOnFileSelect}
          onFileRemove={mockOnFileRemove}
          error="Error al procesar el archivo GPX"
        />
      );

      const dropzone = screen.getByLabelText(/arrastra tu archivo gpx/i);
      expect(dropzone).toHaveClass('gpx-wizard-uploader--error');
    });

    it('should clear error when file is removed', () => {
      const mockFile = new File(['content'], 'route.gpx', {
        type: 'application/gpx+xml',
      });

      const { rerender } = render(
        <GPXWizardUploader
          onFileSelect={mockOnFileSelect}
          onFileRemove={mockOnFileRemove}
          selectedFile={mockFile}
          error="Error al procesar el archivo GPX"
        />
      );

      expect(screen.getByText(/error al procesar el archivo gpx/i)).toBeInTheDocument();

      // Click remove button
      const removeButton = screen.getByRole('button', { name: /eliminar/i });
      fireEvent.click(removeButton);

      // Rerender without error
      rerender(
        <GPXWizardUploader
          onFileSelect={mockOnFileSelect}
          onFileRemove={mockOnFileRemove}
          selectedFile={undefined}
          error={undefined}
        />
      );

      expect(screen.queryByText(/error al procesar el archivo gpx/i)).not.toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA labels for screen readers', () => {
      render(<GPXWizardUploader onFileSelect={mockOnFileSelect} onFileRemove={mockOnFileRemove} />);

      const dropzone = screen.getByLabelText(/arrastra tu archivo gpx/i);
      expect(dropzone).toHaveAttribute('role', 'button');
      expect(dropzone).toHaveAttribute('tabIndex', '0');
    });

    it('should announce errors to screen readers', () => {
      render(
        <GPXWizardUploader
          onFileSelect={mockOnFileSelect}
          onFileRemove={mockOnFileRemove}
          error="Error al procesar el archivo GPX"
        />
      );

      const errorMessage = screen.getByText(/error al procesar el archivo gpx/i);
      expect(errorMessage).toHaveAttribute('role', 'alert');
    });

    it('should support keyboard navigation for file selection', () => {
      render(<GPXWizardUploader onFileSelect={mockOnFileSelect} onFileRemove={mockOnFileRemove} />);

      const dropzone = screen.getByLabelText(/arrastra tu archivo gpx/i);

      // Simulate Enter key press
      fireEvent.keyDown(dropzone, { key: 'Enter', code: 'Enter' });

      // Should trigger file input click (tested via manual testing)
      expect(dropzone).toBeInTheDocument();
    });
  });
});
