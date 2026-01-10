/**
 * TagInput Component
 *
 * Autocomplete input for selecting tags with client-side filtering.
 * Fetches all tags from backend, provides suggestions as user types.
 * Max 10 tags limit enforced.
 *
 * Features:
 * - Autocomplete dropdown with fuzzy matching
 * - Prevents duplicate tags (case-insensitive)
 * - Visual tag chips with remove buttons
 * - Max 10 tags limit with visual feedback
 * - Click to select from suggestions
 * - Enter or comma to add tag
 *
 * Used in:
 * - Step2StoryTags (trip creation wizard)
 * - TripEditPage (editing existing trips)
 */

import React, { useState, useEffect, useRef } from 'react';
import { getAllTags } from '../../services/tripService';
import { Tag } from '../../types/trip';
import './TagInput.css';

interface TagInputProps {
  /** Currently selected tags */
  selectedTags: string[];

  /** Callback when tags change */
  onChange: (tags: string[]) => void;

  /** Maximum number of tags allowed (default: 10) */
  maxTags?: number;

  /** Placeholder text */
  placeholder?: string;

  /** Disabled state */
  disabled?: boolean;
}

export const TagInput: React.FC<TagInputProps> = ({
  selectedTags,
  onChange,
  maxTags = 10,
  placeholder = 'Escribe para buscar etiquetas...',
  disabled = false,
}) => {
  const [inputValue, setInputValue] = useState('');
  const [allTags, setAllTags] = useState<Tag[]>([]);
  const [filteredTags, setFilteredTags] = useState<Tag[]>([]);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [highlightedIndex, setHighlightedIndex] = useState(-1);
  const inputRef = useRef<HTMLInputElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Fetch all tags on mount
  useEffect(() => {
    const fetchTags = async () => {
      setIsLoading(true);
      try {
        const tags = await getAllTags();
        setAllTags(tags);
      } catch (error) {
        console.error('Error fetching tags:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchTags();
  }, []);

  // Filter tags based on input value
  useEffect(() => {
    if (!inputValue.trim()) {
      setFilteredTags([]);
      setIsDropdownOpen(false);
      return;
    }

    const searchTerm = inputValue.toLowerCase();
    const filtered = allTags
      .filter((tag) => {
        // Already selected?
        if (selectedTags.some((t) => t.toLowerCase() === tag.name.toLowerCase())) {
          return false;
        }

        // Fuzzy match on name or normalized
        return (
          tag.name.toLowerCase().includes(searchTerm) ||
          tag.normalized.includes(searchTerm)
        );
      })
      .slice(0, 10); // Limit suggestions to 10

    setFilteredTags(filtered);
    setIsDropdownOpen(filtered.length > 0);
    setHighlightedIndex(-1);
  }, [inputValue, allTags, selectedTags]);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(e.target as Node) &&
        inputRef.current &&
        !inputRef.current.contains(e.target as Node)
      ) {
        setIsDropdownOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  /**
   * Add tag to selected list
   */
  const addTag = (tagName: string) => {
    const trimmed = tagName.trim();

    // Validation
    if (!trimmed) return;
    if (selectedTags.length >= maxTags) return;
    if (selectedTags.some((t) => t.toLowerCase() === trimmed.toLowerCase())) return;

    onChange([...selectedTags, trimmed]);
    setInputValue('');
    setIsDropdownOpen(false);
    inputRef.current?.focus();
  };

  /**
   * Remove tag from selected list
   */
  const removeTag = (index: number) => {
    const newTags = selectedTags.filter((_, i) => i !== index);
    onChange(newTags);
    inputRef.current?.focus();
  };

  /**
   * Handle input change
   */
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInputValue(e.target.value);
  };

  /**
   * Handle keyboard navigation
   */
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    // Enter or Comma: Add tag
    if (e.key === 'Enter' || e.key === ',') {
      e.preventDefault();

      if (highlightedIndex >= 0 && filteredTags[highlightedIndex]) {
        // Add highlighted suggestion
        addTag(filteredTags[highlightedIndex].name);
      } else if (inputValue.trim()) {
        // Add custom tag (user typed text)
        addTag(inputValue);
      }
      return;
    }

    // Backspace: Remove last tag if input is empty
    if (e.key === 'Backspace' && !inputValue && selectedTags.length > 0) {
      removeTag(selectedTags.length - 1);
      return;
    }

    // Arrow Down: Highlight next suggestion
    if (e.key === 'ArrowDown' && isDropdownOpen) {
      e.preventDefault();
      setHighlightedIndex((prev) =>
        prev < filteredTags.length - 1 ? prev + 1 : prev
      );
      return;
    }

    // Arrow Up: Highlight previous suggestion
    if (e.key === 'ArrowUp' && isDropdownOpen) {
      e.preventDefault();
      setHighlightedIndex((prev) => (prev > 0 ? prev - 1 : -1));
      return;
    }

    // Escape: Close dropdown
    if (e.key === 'Escape') {
      setIsDropdownOpen(false);
      setHighlightedIndex(-1);
    }
  };

  /**
   * Handle suggestion click
   */
  const handleSuggestionClick = (tag: Tag) => {
    addTag(tag.name);
  };

  const isMaxReached = selectedTags.length >= maxTags;

  return (
    <div className="tag-input">
      {/* Selected Tags */}
      {selectedTags.length > 0 && (
        <div className="tag-input__selected">
          {selectedTags.map((tag, index) => (
            <div key={index} className="tag-input__tag">
              <span className="tag-input__tag-name">{tag}</span>
              <button
                type="button"
                className="tag-input__tag-remove"
                onClick={() => removeTag(index)}
                disabled={disabled}
                aria-label={`Eliminar etiqueta ${tag}`}
              >
                ×
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Input Field */}
      <div className="tag-input__input-wrapper">
        <input
          ref={inputRef}
          type="text"
          className="tag-input__input"
          value={inputValue}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          onFocus={() => inputValue && setIsDropdownOpen(filteredTags.length > 0)}
          placeholder={
            isMaxReached
              ? `Máximo ${maxTags} etiquetas alcanzado`
              : placeholder
          }
          disabled={disabled || isMaxReached}
        />

        {/* Tag Counter */}
        <div className="tag-input__counter">
          <span
            className={`tag-input__counter-text ${
              isMaxReached ? 'tag-input__counter-text--max' : ''
            }`}
          >
            {selectedTags.length}/{maxTags}
          </span>
        </div>
      </div>

      {/* Autocomplete Dropdown */}
      {isDropdownOpen && !disabled && (
        <div ref={dropdownRef} className="tag-input__dropdown">
          {isLoading ? (
            <div className="tag-input__dropdown-item tag-input__dropdown-item--loading">
              Cargando etiquetas...
            </div>
          ) : filteredTags.length > 0 ? (
            filteredTags.map((tag, index) => (
              <div
                key={tag.tag_id}
                className={`tag-input__dropdown-item ${
                  index === highlightedIndex
                    ? 'tag-input__dropdown-item--highlighted'
                    : ''
                }`}
                onClick={() => handleSuggestionClick(tag)}
                onMouseEnter={() => setHighlightedIndex(index)}
              >
                <span className="tag-input__dropdown-name">{tag.name}</span>
                <span className="tag-input__dropdown-count">
                  ({tag.usage_count.toLocaleString()})
                </span>
              </div>
            ))
          ) : (
            <div className="tag-input__dropdown-item tag-input__dropdown-item--empty">
              Presiona Enter para crear "{inputValue}"
            </div>
          )}
        </div>
      )}

      {/* Help Text */}
      <div className="tag-input__help">
        Escribe y presiona Enter o coma (,) para agregar. Usa Backspace para eliminar.
      </div>
    </div>
  );
};
