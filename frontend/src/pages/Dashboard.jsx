import { TrendingUp, FileCheck, AlertCircle, Clock } from 'lucide-react';

const stats = [
  {
    label: 'Active Projects',
    value: '12',
    change: '+2 this month',
    icon: TrendingUp,
    changeColor: 'text-green-600',
  },
  {
    label: 'Permits Approved',
    value: '34',
    change: '+5 this week',
    icon: FileCheck,
    changeColor: 'text-green-600',
  },
  {
    label: 'Pending Reviews',
    value: '8',
    change: '3 urgent',
    icon: AlertCircle,
    changeColor: 'text-orange-600',
  },
  {
    label: 'Avg. Processing Time',
    value: '4.2 days',
    change: '-0.5 days',
    icon: Clock,
    changeColor: 'text-green-600',
  },
];

export default function Dashboard() {
  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#F8FAFC', padding: '32px' }}>
      <div style={{ maxWidth: '1280px', margin: '0 auto' }}>
        {/* Page Header */}
        <div style={{ marginBottom: '32px' }}>
          <h1 style={{ fontSize: '28px', fontWeight: '600', color: '#1E293B', marginBottom: '8px' }}>
            Dashboard
          </h1>
          <p style={{ fontSize: '15px', color: '#64748B' }}>
            Welcome back! Here's an overview of your projects and permits.
          </p>
        </div>

        {/* Stats Grid */}
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
          gap: '20px',
          marginBottom: '32px'
        }}>
          {stats.map((stat, index) => {
            const Icon = stat.icon;
            return (
              <div
                key={index}
                style={{
                  backgroundColor: '#FFFFFF',
                  borderRadius: '16px',
                  padding: '24px',
                  border: '1px solid #E2E8F0',
                  boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
                  transition: 'all 0.2s ease',
                  cursor: 'pointer'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.boxShadow = '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)';
                  e.currentTarget.style.transform = 'translateY(-2px)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.boxShadow = '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)';
                  e.currentTarget.style.transform = 'translateY(0)';
                }}
              >
                <div style={{ 
                  width: '48px', 
                  height: '48px', 
                  borderRadius: '12px',
                  backgroundColor: '#EFF6FF',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  marginBottom: '16px'
                }}>
                  <Icon size={24} style={{ color: '#2563EB' }} />
                </div>
                <h3 style={{ 
                  fontSize: '32px', 
                  fontWeight: '700', 
                  color: '#1E293B',
                  marginBottom: '4px',
                  lineHeight: '1'
                }}>
                  {stat.value}
                </h3>
                <p style={{ 
                  fontSize: '14px', 
                  color: '#64748B',
                  marginBottom: '12px',
                  fontWeight: '500'
                }}>
                  {stat.label}
                </p>
                <p style={{ 
                  fontSize: '13px', 
                  fontWeight: '600',
                  color: stat.changeColor === 'text-green-600' ? '#059669' : '#EA580C'
                }}>
                  {stat.change}
                </p>
              </div>
            );
          })}
        </div>

        {/* Recent Activity */}
        <div style={{
          backgroundColor: '#FFFFFF',
          borderRadius: '16px',
          padding: '28px',
          border: '1px solid #E2E8F0',
          boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)'
        }}>
          <h2 style={{ 
            fontSize: '20px', 
            fontWeight: '600', 
            color: '#1E293B',
            marginBottom: '20px'
          }}>
            Recent Activity
          </h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {[
              { text: 'Permit #1234 approved', time: '2 hours ago', color: '#2563EB' },
              { text: 'New project "Main St Renovation" created', time: '5 hours ago', color: '#2563EB' },
              { text: 'Document uploaded to Project #456', time: '1 day ago', color: '#2563EB' },
              { text: 'Permit #1230 requires attention', time: '2 days ago', color: '#EA580C' },
            ].map((item, index) => (
              <div 
                key={index}
                style={{
                  borderLeft: `3px solid ${item.color}`,
                  paddingLeft: '16px',
                  paddingTop: '8px',
                  paddingBottom: '8px',
                  transition: 'all 0.2s ease',
                  cursor: 'pointer'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = '#F8FAFC';
                  e.currentTarget.style.paddingLeft = '20px';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = 'transparent';
                  e.currentTarget.style.paddingLeft = '16px';
                }}
              >
                <div style={{ 
                  fontSize: '15px', 
                  fontWeight: '500', 
                  color: '#1E293B',
                  marginBottom: '4px'
                }}>
                  {item.text}
                </div>
                <div style={{ 
                  fontSize: '13px', 
                  color: '#94A3B8'
                }}>
                  {item.time}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
