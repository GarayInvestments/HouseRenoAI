import { TrendingUp, FileCheck, AlertCircle, Clock, LayoutDashboard } from 'lucide-react';
import { useAppStore } from '../stores/appStore';
import { StatsCard, PageHeader } from '@/components/app';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';

const stats = [
  {
    label: 'Active Projects',
    value: '12',
    trend: '+2 this month',
    trendUp: true,
    icon: TrendingUp,
    action: 'projects',
  },
  {
    label: 'Permits Approved',
    value: '34',
    trend: '+5 this week',
    trendUp: true,
    icon: FileCheck,
  },
  {
    label: 'Pending Reviews',
    value: '8',
    trend: '3 urgent',
    trendUp: false,
    icon: AlertCircle,
  },
  {
    label: 'Avg. Processing Time',
    value: '4.2 days',
    trend: '-0.5 days',
    trendUp: true,
    icon: Clock,
  },
];

const recentActivities = [
  { text: 'Permit #1234 approved', time: '2 hours ago', type: 'success' },
  { text: 'New project "Main St Renovation" created', time: '5 hours ago', type: 'info' },
  { text: 'Document uploaded to Project #456', time: '1 day ago', type: 'info' },
  { text: 'Permit #1230 requires attention', time: '2 days ago', type: 'warning' },
];

export default function Dashboard() {
  const { setCurrentView } = useAppStore();

  const handleStatClick = (action) => {
    if (action) {
      setCurrentView(action);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 p-8">
      <div className="max-w-7xl mx-auto">
        <PageHeader
          icon={<LayoutDashboard size={32} />}
          title="Dashboard"
          subtitle="Welcome back! Here's an overview of your projects and permits."
        />

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
          {stats.map((stat, index) => (
            <StatsCard
              key={index}
              icon={<stat.icon size={24} />}
              label={stat.label}
              value={stat.value}
              trend={stat.trend}
              trendUp={stat.trendUp}
              onClick={stat.action ? () => handleStatClick(stat.action) : undefined}
            />
          ))}
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentActivities.map((item, index) => (
                <div
                  key={index}
                  className={`border-l-3 pl-4 py-2 transition-all cursor-pointer hover:bg-slate-50 hover:pl-5 ${
                    item.type === 'success' ? 'border-l-blue-600' :
                    item.type === 'warning' ? 'border-l-orange-600' :
                    'border-l-blue-600'
                  }`}
                >
                  <div className="text-[15px] font-medium text-slate-800 mb-1">
                    {item.text}
                  </div>
                  <div className="text-[13px] text-slate-400">
                    {item.time}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
