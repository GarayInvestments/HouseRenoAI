import { useState, useEffect, useCallback } from 'react';

/**
 * Custom hook for navigating between items in a detail view
 * Provides swipe gestures, keyboard navigation, and prev/next functions
 * 
 * @param {Array} items - Array of items to navigate through
 * @param {string} currentItemId - ID of the currently displayed item
 * @param {Function} onNavigate - Callback function (itemId) => void to navigate to an item
 * @param {string} idField - Name of the ID field in items (default: 'id')
 * @returns {Object} Navigation state and handlers
 */
export default function useDetailsNavigation(items = [], currentItemId, onNavigate, idField = 'id') {
  const [touchStart, setTouchStart] = useState(null);
  const [touchEnd, setTouchEnd] = useState(null);

  // Find current index
  const currentIndex = items.findIndex(item => item[idField] === currentItemId);
  const hasPrevious = currentIndex > 0;
  const hasNext = currentIndex < items.length - 1 && currentIndex !== -1;

  // Minimum swipe distance (in px)
  const minSwipeDistance = 50;

  const goToPrevious = useCallback(() => {
    if (hasPrevious) {
      const prevItem = items[currentIndex - 1];
      onNavigate(prevItem[idField]);
    }
  }, [hasPrevious, items, currentIndex, onNavigate, idField]);

  const goToNext = useCallback(() => {
    if (hasNext) {
      const nextItem = items[currentIndex + 1];
      onNavigate(nextItem[idField]);
    }
  }, [hasNext, items, currentIndex, onNavigate, idField]);

  // Handle touch start
  const onTouchStart = (e) => {
    setTouchEnd(null);
    setTouchStart(e.targetTouches[0].clientX);
  };

  // Handle touch move
  const onTouchMove = (e) => {
    setTouchEnd(e.targetTouches[0].clientX);
  };

  // Handle touch end
  const onTouchEnd = () => {
    if (!touchStart || !touchEnd) return;
    
    const distance = touchStart - touchEnd;
    const isLeftSwipe = distance > minSwipeDistance;
    const isRightSwipe = distance < -minSwipeDistance;

    if (isLeftSwipe && hasNext) {
      goToNext();
    }
    if (isRightSwipe && hasPrevious) {
      goToPrevious();
    }
  };

  // Handle keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'ArrowLeft') {
        e.preventDefault();
        goToPrevious();
      } else if (e.key === 'ArrowRight') {
        e.preventDefault();
        goToNext();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [goToPrevious, goToNext]);

  return {
    currentIndex: currentIndex === -1 ? 0 : currentIndex,
    totalItems: items.length,
    hasPrevious,
    hasNext,
    goToPrevious,
    goToNext,
    // Touch handlers for swipe gestures
    touchHandlers: {
      onTouchStart,
      onTouchMove,
      onTouchEnd
    }
  };
}
