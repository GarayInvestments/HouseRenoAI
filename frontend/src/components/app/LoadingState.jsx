import { Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';

/**
 * LoadingState - Centralized loading indicator
 * 
 * Replaces inline spinner styles scattered across pages.
 * 
 * @example
 * ```jsx
 * // Full page loading
 * <LoadingState message="Loading client data..." />
 * 
 * // Inline loading (smaller)
 * <LoadingState size="sm" message="Syncing..." />
 * 
 * // Minimal (just spinner)
 * <LoadingState showMessage={false} />
 * ```
 * 
 * @param {string} size - Size variant: 'sm', 'md', 'lg' (default: 'md')
 * @param {string} message - Loading message text
 * @param {boolean} showMessage - Whether to show message (default: true)
 * @param {boolean} fullPage - Whether to center in full page (default: true)
 */
export default function LoadingState({
  size = 'md',
  message = 'Loading...',
  showMessage = true,
  fullPage = true,
  className,
  ...props
}) {
  const sizeConfig = {
    sm: { spinner: 20, text: 'text-xs' },
    md: { spinner: 40, text: 'text-sm' },
    lg: { spinner: 60, text: 'text-base' },
  };

  const config = sizeConfig[size] || sizeConfig.md;

  const content = (
    <div
      className={cn(
        'flex flex-col items-center justify-center gap-3',
        fullPage && 'min-h-[400px]',
        className
      )}
      role="status"
      aria-live="polite"
      {...props}
    >
      <Loader2
        className="animate-spin text-blue-600"
        size={config.spinner}
        aria-hidden="true"
      />
      {showMessage && (
        <p className={cn('text-gray-600', config.text)}>
          {message}
        </p>
      )}
    </div>
  );

  return content;
}
