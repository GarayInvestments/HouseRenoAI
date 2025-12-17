import { Badge } from '@/components/ui/badge';
import { cva } from 'class-variance-authority';
import { 
  Clock, 
  CheckCircle, 
  XCircle, 
  AlertCircle, 
  PlayCircle,
  PauseCircle,
  Ban
} from 'lucide-react';
import { cn } from '@/lib/utils';

/**
 * StatusBadge - Domain-specific status badge with consistent styling
 * 
 * Replaces inline badge styles for permits, projects, invoices, payments, etc.
 * Automatically maps status values to colors and icons.
 * 
 * @example
 * ```jsx
 * // Permit status
 * <StatusBadge status="pending" type="permit" />
 * // Renders: Yellow badge with clock icon + "Pending"
 * 
 * // Invoice status
 * <StatusBadge status="paid" type="invoice" />
 * // Renders: Green badge with check icon + "Paid"
 * 
 * // Project status
 * <StatusBadge status="active" type="project" />
 * // Renders: Blue badge with play icon + "Active"
 * ```
 * 
 * @param {string} status - Status value (e.g., "pending", "active", "complete")
 * @param {string} type - Entity type (e.g., "permit", "invoice", "project", "payment")
 * @param {boolean} showIcon - Whether to show icon (default: true)
 */

// Status configurations by type
const statusConfig = {
  client: {
    active: { variant: 'success', icon: PlayCircle, label: 'Active' },
    completed: { variant: 'secondary', icon: CheckCircle, label: 'Completed' },
    intake: { variant: 'warning', icon: Clock, label: 'Intake' },
    'on_hold': { variant: 'info', icon: PauseCircle, label: 'On Hold' },
    'on hold': { variant: 'info', icon: PauseCircle, label: 'On Hold' },
    archived: { variant: 'secondary', icon: Ban, label: 'Archived' },
  },
  permit: {
    pending: { variant: 'warning', icon: Clock, label: 'Pending' },
    'under review': { variant: 'info', icon: AlertCircle, label: 'Under Review' },
    approved: { variant: 'success', icon: CheckCircle, label: 'Approved' },
    rejected: { variant: 'destructive', icon: XCircle, label: 'Rejected' },
    expired: { variant: 'secondary', icon: Ban, label: 'Expired' },
  },
  project: {
    active: { variant: 'success', icon: PlayCircle, label: 'Active' },
    pending: { variant: 'warning', icon: Clock, label: 'Pending' },
    complete: { variant: 'secondary', icon: CheckCircle, label: 'Complete' },
    'on hold': { variant: 'info', icon: PauseCircle, label: 'On Hold' },
    cancelled: { variant: 'destructive', icon: XCircle, label: 'Cancelled' },
  },
  invoice: {
    draft: { variant: 'secondary', icon: Clock, label: 'Draft' },
    sent: { variant: 'info', icon: AlertCircle, label: 'Sent' },
    paid: { variant: 'success', icon: CheckCircle, label: 'Paid' },
    overdue: { variant: 'destructive', icon: XCircle, label: 'Overdue' },
    void: { variant: 'secondary', icon: Ban, label: 'Void' },
  },
  payment: {
    pending: { variant: 'warning', icon: Clock, label: 'Pending' },
    completed: { variant: 'success', icon: CheckCircle, label: 'Completed' },
    failed: { variant: 'destructive', icon: XCircle, label: 'Failed' },
    refunded: { variant: 'secondary', icon: AlertCircle, label: 'Refunded' },
  },
  inspection: {
    scheduled: { variant: 'info', icon: Clock, label: 'Scheduled' },
    passed: { variant: 'success', icon: CheckCircle, label: 'Passed' },
    failed: { variant: 'destructive', icon: XCircle, label: 'Failed' },
    'needs review': { variant: 'warning', icon: AlertCircle, label: 'Needs Review' },
  },
};

// Badge variants matching shadcn/ui Badge component
const badgeVariants = cva('', {
  variants: {
    variant: {
      default: '',
      success: 'bg-green-100 text-green-800 hover:bg-green-100',
      warning: 'bg-yellow-100 text-yellow-800 hover:bg-yellow-100',
      destructive: 'bg-red-100 text-red-800 hover:bg-red-100',
      info: 'bg-blue-100 text-blue-800 hover:bg-blue-100',
      secondary: 'bg-gray-100 text-gray-800 hover:bg-gray-100',
    },
  },
  defaultVariants: {
    variant: 'default',
  },
});

export default function StatusBadge({
  status,
  type = 'project',
  showIcon = true,
  className,
  ...props
}) {
  if (!status) return null;

  // Normalize status to lowercase for lookup
  const normalizedStatus = status.toString().toLowerCase();
  
  // Get config for this type and status
  const typeConfig = statusConfig[type] || statusConfig.project;
  const config = typeConfig[normalizedStatus] || {
    variant: 'default',
    icon: AlertCircle,
    label: status,
  };

  const Icon = config.icon;

  return (
    <Badge
      className={cn(
        badgeVariants({ variant: config.variant }),
        'flex items-center gap-1.5 w-fit',
        className
      )}
      {...props}
    >
      {showIcon && <Icon size={14} aria-hidden="true" />}
      <span>{config.label}</span>
    </Badge>
  );
}
