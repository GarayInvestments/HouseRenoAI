import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import {
  Inbox,
  FileX,
  Users,
  FolderOpen,
  Search,
  AlertCircle,
} from 'lucide-react';

/**
 * EmptyState - Consistent empty data display
 * 
 * Replaces inline centered text + icon patterns for empty lists/tables.
 * 
 * @example
 * ```jsx
 * // Basic empty state
 * <EmptyState
 *   icon="inbox"
 *   title="No invoices found"
 *   description="Create your first invoice to get started."
 *   action={
 *     <Button onClick={handleCreate}>
 *       <Plus size={16} /> Create Invoice
 *     </Button>
 *   }
 * />
 * ```
 * 
 * @example
 * ```jsx
 * // Search results empty
 * <EmptyState
 *   icon="search"
 *   title="No results found"
 *   description="Try adjusting your search terms."
 * />
 * ```
 * 
 * @param {string} icon - Icon name: 'inbox', 'search', 'users', 'files', 'folder', 'alert'
 * @param {string} title - Main heading text
 * @param {string} description - Supporting description text
 * @param {ReactNode} action - Optional action button(s)
 */

const iconMap = {
  inbox: Inbox,
  search: Search,
  users: Users,
  files: FileX,
  folder: FolderOpen,
  alert: AlertCircle,
};

export default function EmptyState({
  icon = 'inbox',
  title = 'No data found',
  description,
  action,
  className,
  ...props
}) {
  const Icon = iconMap[icon] || iconMap.inbox;

  return (
    <div
      className={cn(
        'flex flex-col items-center justify-center py-12 px-4 text-center',
        className
      )}
      role="status"
      aria-live="polite"
      {...props}
    >
      <div
        className="mb-4 rounded-full bg-gray-100 p-6"
        aria-hidden="true"
      >
        <Icon size={48} className="text-gray-400" />
      </div>

      <h3 className="text-lg font-semibold text-gray-900 mb-2">
        {title}
      </h3>

      {description && (
        <p className="text-sm text-gray-600 max-w-md mb-6">
          {description}
        </p>
      )}

      {action && <div className="flex gap-2">{action}</div>}
    </div>
  );
}
