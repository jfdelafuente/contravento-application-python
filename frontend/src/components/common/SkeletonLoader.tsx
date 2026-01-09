import React from 'react';
import './SkeletonLoader.css';

interface SkeletonLoaderProps {
  variant?: 'text' | 'card' | 'circle' | 'rect';
  width?: string;
  height?: string;
  count?: number;
  className?: string;
}

/**
 * SkeletonLoader component for loading states
 * Displays animated placeholder while content is loading
 */
const SkeletonLoader: React.FC<SkeletonLoaderProps> = ({
  variant = 'text',
  width = '100%',
  height,
  count = 1,
  className = '',
}) => {
  const getDefaultHeight = () => {
    switch (variant) {
      case 'text':
        return '1rem';
      case 'card':
        return '200px';
      case 'circle':
        return '50px';
      case 'rect':
        return '100px';
      default:
        return '1rem';
    }
  };

  const skeletonHeight = height || getDefaultHeight();

  const skeletonStyle: React.CSSProperties = {
    width,
    height: skeletonHeight,
    borderRadius: variant === 'circle' ? '50%' : variant === 'card' ? '8px' : '4px',
  };

  return (
    <>
      {Array.from({ length: count }).map((_, index) => (
        <div
          key={index}
          className={`skeleton-loader ${className}`}
          style={skeletonStyle}
          aria-busy="true"
          aria-live="polite"
        />
      ))}
    </>
  );
};

export default SkeletonLoader;
