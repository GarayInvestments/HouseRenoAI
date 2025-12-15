import { Button } from '@/components/ui/button';
import { ArrowLeft } from 'lucide-react';
import { cn } from '@/lib/utils';

/**
 * PageHeader - Consistent page header with icon, title, and actions
 * 
 * Replaces repeated header HTML pattern across all pages.
 * 
 * @example
 * ```jsx
 * <PageHeader
 *   icon={<FileText size={32} />}
 *   title="Invoice Details"
 *   subtitle="#INV-2025-001"
 *   actions={
 *     <>
 *       <Button variant="outline" onClick={handleEdit}>
 *         <Edit size={16} /> Edit
 *       </Button>
 *       <Button onClick={handleDelete}>
 *         <Trash size={16} /> Delete
 *       </Button>
 *     </>
 *   }
 * />
 * ```
 * 
 * @example
 * ```jsx
 * // With back button
 * <PageHeader
 *   icon={<Users size={32} />}
 *   title="Client Details"
 *   showBack={true}
 *   onBack={() => navigate('clients')}
 * />
 * ```
 */
export default function PageHeader({
  icon,
  title,
  subtitle,
  actions,
  showBack = false,
  onBack,
  className,
  ...props
}) {
  return (
    <div
      className={cn('flex items-center justify-between mb-6', className)}
      {...props}
    >
      <div className="flex items-center gap-4">
        {showBack && (
          <Button
            variant="ghost"
            size="icon"
            onClick={onBack}
            aria-label="Go back"
          >
            <ArrowLeft size={20} />
          </Button>
        )}
        
        {icon && (
          <div className="text-blue-600" aria-hidden="true">
            {icon}
          </div>
        )}
        
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{title}</h1>
          {subtitle && (
            <p className="text-sm text-gray-500 mt-1">{subtitle}</p>
          )}
        </div>
      </div>

      {actions && (
        <div className="flex items-center gap-2">
          {actions}
        </div>
      )}
    </div>
  );
}
