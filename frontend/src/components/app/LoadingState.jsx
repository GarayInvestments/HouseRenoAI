import { Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';
import Skeleton from '@/components/ui/skeleton';

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
  variant,
  layout = 'default',
  className,
  ...props
}) {
  const sizeConfig = {
    sm: { spinner: 20, text: 'text-xs' },
    md: { spinner: 40, text: 'text-sm' },
    lg: { spinner: 60, text: 'text-base' },
  };

  const config = sizeConfig[size] || sizeConfig.md;

  const resolvedVariant = variant || (fullPage ? 'skeleton' : 'spinner');

  const skeletonContent = (
    <div
      className={cn(
        'w-full',
        fullPage && 'min-h-[400px] flex items-center justify-center',
        className
      )}
      role="status"
      aria-live="polite"
      {...props}
    >
      <div className="w-full max-w-5xl space-y-6 px-6 py-8">
        <div className="space-y-3">
          <Skeleton className="h-8 w-1/3" />
          {showMessage && <Skeleton className="h-4 w-1/2" />}
        </div>

        {layout === 'list' && (
          <div className="space-y-3">
            {Array.from({ length: 8 }).map((_, idx) => (
              <Skeleton key={idx} className="h-12 w-full" />
            ))}
          </div>
        )}

        {layout === 'details' && (
          <>
            <div className="grid gap-4 md:grid-cols-2">
              <Skeleton className="h-28 w-full" />
              <Skeleton className="h-28 w-full" />
            </div>
            <Skeleton className="h-64 w-full" />
          </>
        )}

        {layout === 'default' && (
          <div className="space-y-4">
            <Skeleton className="h-28 w-full" />
            <Skeleton className="h-28 w-full" />
            <Skeleton className="h-28 w-full" />
          </div>
        )}
      </div>
    </div>
  );

  if (resolvedVariant === 'skeleton') {
    return skeletonContent;
  }

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
