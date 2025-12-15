import { ChevronLeft, ChevronRight } from 'lucide-react';

/**
 * Navigation arrows component for detail pages
 * Shows left/right arrows and item counter (e.g., "3 of 12")
 */
export default function NavigationArrows({ 
  currentIndex, 
  totalItems, 
  hasPrevious, 
  hasNext, 
  onPrevious, 
  onNext,
  itemLabel = 'item' // e.g., 'invoice', 'client', 'project'
}) {
  if (totalItems <= 1) return null;

  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      gap: '12px'
    }}>
      {/* Previous button */}
      <button
        onClick={onPrevious}
        disabled={!hasPrevious}
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          width: '36px',
          height: '36px',
          backgroundColor: hasPrevious ? 'white' : '#F3F4F6',
          border: `1px solid ${hasPrevious ? '#D1D5DB' : '#E5E7EB'}`,
          borderRadius: '8px',
          cursor: hasPrevious ? 'pointer' : 'not-allowed',
          transition: 'all 0.2s',
          opacity: hasPrevious ? 1 : 0.5
        }}
        onMouseEnter={(e) => {
          if (hasPrevious) {
            e.currentTarget.style.backgroundColor = '#F9FAFB';
            e.currentTarget.style.borderColor = '#9CA3AF';
          }
        }}
        onMouseLeave={(e) => {
          if (hasPrevious) {
            e.currentTarget.style.backgroundColor = 'white';
            e.currentTarget.style.borderColor = '#D1D5DB';
          }
        }}
      >
        <ChevronLeft size={20} color={hasPrevious ? '#374151' : '#9CA3AF'} />
      </button>

      {/* Counter */}
      <span style={{
        fontSize: '14px',
        color: '#6B7280',
        fontWeight: '500',
        minWidth: '80px',
        textAlign: 'center'
      }}>
        {currentIndex + 1} of {totalItems}
      </span>

      {/* Next button */}
      <button
        onClick={onNext}
        disabled={!hasNext}
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          width: '36px',
          height: '36px',
          backgroundColor: hasNext ? 'white' : '#F3F4F6',
          border: `1px solid ${hasNext ? '#D1D5DB' : '#E5E7EB'}`,
          borderRadius: '8px',
          cursor: hasNext ? 'pointer' : 'not-allowed',
          transition: 'all 0.2s',
          opacity: hasNext ? 1 : 0.5
        }}
        onMouseEnter={(e) => {
          if (hasNext) {
            e.currentTarget.style.backgroundColor = '#F9FAFB';
            e.currentTarget.style.borderColor = '#9CA3AF';
          }
        }}
        onMouseLeave={(e) => {
          if (hasNext) {
            e.currentTarget.style.backgroundColor = 'white';
            e.currentTarget.style.borderColor = '#D1D5DB';
          }
        }}
      >
        <ChevronRight size={20} color={hasNext ? '#374151' : '#9CA3AF'} />
      </button>
    </div>
  );
}
