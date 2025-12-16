import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { cn } from '@/lib/utils';

/**
 * StatsCard - Reusable statistics card component
 * 
 * Replaces inline grid + white background + shadow pattern used throughout pages.
 * 
 * @example
 * ```jsx
 * <StatsCard
 *   icon={<DollarSign size={24} />}
 *   label="Total Revenue"
 *   value="$125,430"
 *   trend="+12.5%"
 *   trendUp={true}
 * />
 * ```
 * 
 * @example
 * ```jsx
 * // Without trend
 * <StatsCard
 *   icon={<Users size={24} />}
 *   label="Active Clients"
 *   value="24"
 * />
 * ```
 */
export default function StatsCard({
  icon,
  label,
  value,
  trend,
  trendUp,
  subtitle,
  onClick,
  className,
  ...props
}) {
  const isClickable = !!onClick;

  return (
    <Card
      className={cn(
        'transition-all hover:shadow-md',
        isClickable && 'cursor-pointer hover:border-blue-300',
        className
      )}
      onClick={onClick}
      {...props}
    >
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">
          {label}
        </CardTitle>
        {icon && (
          <div className="text-primary" aria-hidden="true">
            {icon}
          </div>
        )}
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-semibold text-foreground">{value}</div>
        {subtitle && (
          <p className="text-xs text-muted-foreground mt-1">{subtitle}</p>
        )}
        {trend && (
          <p
            className={cn(
              'text-xs font-medium mt-1',
              trendUp ? 'text-green-600' : 'text-red-600'
            )}
          >
            {trend}
          </p>
        )}
      </CardContent>
    </Card>
  );
}
