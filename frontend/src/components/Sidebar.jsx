import { LayoutDashboard, MessageSquare, FileText, FolderKanban, Users, FolderOpen, Settings, ClipboardCheck, Receipt, DollarSign, MapPin, Building2, UserCheck, Eye, Boxes } from 'lucide-react';
import { useAppStore } from '../stores/appStore';

const navItems = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { id: 'ai-assistant', label: 'AI Assistant', icon: MessageSquare },
  { id: 'permits', label: 'Permits', icon: FileText },
  { id: 'inspections', label: 'Inspections', icon: ClipboardCheck },
  { id: 'invoices', label: 'Invoices', icon: Receipt },
  { id: 'payments', label: 'Payments', icon: DollarSign },
  { id: 'site-visits', label: 'Site Visits', icon: MapPin },
  { id: 'projects', label: 'Projects', icon: FolderKanban },
  { id: 'clients', label: 'Clients', icon: Users },
  { id: 'licensed-businesses', label: 'Licensed Businesses', icon: Building2 },
  { id: 'qualifiers', label: 'Qualifiers', icon: UserCheck },
  { id: 'oversight-actions', label: 'Oversight Actions', icon: Eye },
  { id: 'documents', label: 'Documents', icon: FolderOpen },
  { id: 'settings', label: 'Settings', icon: Settings },
];

export default function Sidebar() {
  const { currentView, setCurrentView } = useAppStore();

  return (
    <>
      <style>{`
        @media (max-width: 1023px) {
          .desktop-sidebar {
            display: none !important;
          }
        }
        @media (min-width: 1024px) {
          .desktop-sidebar {
            display: flex !important;
          }
        }
      `}</style>
      <aside className="desktop-sidebar" style={{
        flexDirection: 'column',
        width: '260px',
        height: '100vh',
        backgroundColor: '#FFFFFF',
        borderRight: '1px solid #E2E8F0',
        boxShadow: '2px 0 8px rgba(0, 0, 0, 0.04)'
      }}>
      {/* Logo/Brand */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        height: '64px',
        padding: '0 20px',
        borderBottom: '1px solid #E2E8F0'
      }}>
        <div style={{
          width: '36px',
          height: '36px',
          borderRadius: '10px',
          background: 'linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#FFFFFF',
          fontWeight: '700',
          fontSize: '14px',
          marginRight: '12px',
          boxShadow: '0 4px 6px -1px rgba(37, 99, 235, 0.3)'
        }}>
          HR
        </div>
        <h1 style={{
          fontSize: '16px',
          fontWeight: '600',
          color: '#1E293B',
          letterSpacing: '-0.01em'
        }}>
          House Renovators
        </h1>
      </div>

      {/* Navigation */}
      <nav style={{ flex: 1, overflowY: 'auto', padding: '16px 12px' }}>
        <ul style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentView === item.id;
            
            return (
              <li key={item.id}>
                <button
                  onClick={() => setCurrentView(item.id)}
                  style={{
                    width: '100%',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px',
                    padding: '12px 14px',
                    borderRadius: '10px',
                    transition: 'all 0.2s ease',
                    border: 'none',
                    cursor: 'pointer',
                    backgroundColor: isActive ? '#2563EB' : 'transparent',
                    color: isActive ? '#FFFFFF' : '#64748B',
                    fontWeight: isActive ? '600' : '500',
                    fontSize: '14px',
                    boxShadow: isActive ? '0 4px 6px -1px rgba(37, 99, 235, 0.3)' : 'none'
                  }}
                  onMouseEnter={(e) => {
                    if (!isActive) {
                      e.currentTarget.style.backgroundColor = '#F1F5F9';
                      e.currentTarget.style.color = '#1E293B';
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (!isActive) {
                      e.currentTarget.style.backgroundColor = 'transparent';
                      e.currentTarget.style.color = '#64748B';
                    }
                  }}
                >
                  <Icon size={20} style={{ color: isActive ? '#FFFFFF' : '#64748B' }} />
                  <span>{item.label}</span>
                </button>
              </li>
            );
          })}
        </ul>
      </nav>

      {/* Footer Info */}
      <div style={{
        padding: '16px',
        borderTop: '1px solid #F1F5F9'
      }}>
        <p style={{
          fontSize: '11px',
          textAlign: 'center',
          color: '#94A3B8',
          fontWeight: '500'
        }}>
          © 2025 House Renovators
        </p>
      </div>
    </aside>
    </>
  );
}
