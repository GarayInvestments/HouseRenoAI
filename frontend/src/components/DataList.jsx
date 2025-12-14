import React from 'react';
import LoadingScreen from './LoadingScreen';
import ErrorState from './ErrorState';

/**
 * DataList - Reusable component for rendering lists/tables
 * Handles loading, error, and empty states automatically
 * 
 * @param {Array} data - Array of items to display
 * @param {Array} columns - Column definitions: [{ key, label, render }]
 * @param {Function} onRowClick - Callback when row is clicked
 * @param {Boolean} loading - Loading state
 * @param {String} error - Error message
 * @param {String} emptyMessage - Message when no data
 * @param {Function} onRetry - Retry callback for error state
 * @param {String} itemKey - Unique key property (default: 'id')
 */
export default function DataList({
  data = [],
  columns = [],
  onRowClick,
  loading = false,
  error = null,
  emptyMessage = 'No items found',
  onRetry,
  itemKey = 'id',
}) {
  // Loading state
  if (loading) {
    return <LoadingScreen />;
  }

  // Error state
  if (error) {
    return <ErrorState message={error} onRetry={onRetry} />;
  }

  // Empty state
  if (!data || data.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-gray-500">
        <svg
          className="w-16 h-16 mb-4 text-gray-300"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={1.5}
            d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"
          />
        </svg>
        <p className="text-lg font-medium">{emptyMessage}</p>
      </div>
    );
  }

  // Data list
  return (
    <div className="space-y-2">
      {data.map((item) => (
        <div
          key={item[itemKey]}
          className="bg-white rounded-lg shadow-sm p-4 hover:shadow-md transition-shadow cursor-pointer"
          onClick={() => onRowClick && onRowClick(item)}
        >
          <div className="grid gap-2">
            {columns.map((col) => (
              <div key={col.key} className="flex justify-between items-start">
                <span className="text-sm font-medium text-gray-500">
                  {col.label}:
                </span>
                <span className="text-sm text-gray-900 text-right">
                  {col.render ? col.render(item) : item[col.key]}
                </span>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
