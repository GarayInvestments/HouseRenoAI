import { X, LayoutDashboard, MessageSquare, FileText, FolderKanban, Users, FolderOpen, Settings } from 'lucide-react';
import { useAppStore } from '../stores/appStore';
import { useEffect } from 'react';

const navItems = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { id: 'ai-assistant', label: 'AI Assistant', icon: MessageSquare },
  { id: 'permits', label: 'Permits', icon: FileText },
  { id: 'projects', label: 'Projects', icon: FolderKanban },
  { id: 'clients', label: 'Clients', icon: Users },
  { id: 'documents', label: 'Documents', icon: FolderOpen },
  { id: 'settings', label: 'Settings', icon: Settings },
];

export default function MobileDrawer() {
  const { drawerOpen, setDrawerOpen, currentView, setCurrentView } = useAppStore();

  // Prevent body scroll when drawer is open
  useEffect(() => {
    if (drawerOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    return () => { document.body.style.overflow = 'unset'; };
  }, [drawerOpen]);

  if (!drawerOpen) return null;

  const handleNavClick = (viewId) => {
    setCurrentView(viewId);
    setDrawerOpen(false);
  };

  return (
    <>
      {/* Backdrop with blur */}
      <div
        style={{
          position: 'fixed',
          inset: 0,
          zIndex: 40,
          backgroundColor: 'rgba(0, 0, 0, 0.5)',
          backdropFilter: 'blur(4px)',
          transition: 'opacity 0.3s ease',
          animation: 'fadeIn 0.3s ease'
        }}
        className="lg:hidden"
        onClick={() => setDrawerOpen(false)}
      />

      {/* Drawer with slide animation */}
      <div 
        style={{
          position: 'fixed',
          top: 0,
          bottom: 0,
          left: 0,
          width: '280px',
          backgroundColor: '#FFFFFF',
          zIndex: 50,
          display: 'flex',
          flexDirection: 'column',
          boxShadow: '4px 0 24px rgba(0, 0, 0, 0.12)',
          transform: 'translateX(0)',
          transition: 'transform 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          animation: 'slideIn 0.3s cubic-bezier(0.4, 0, 0.2, 1)'
        }}
        className="lg:hidden"
      >
        {/* Header */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          height: '64px',
          padding: '0 20px',
          borderBottom: '1px solid #E2E8F0'
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '12px'
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
          <button
            onClick={() => setDrawerOpen(false)}
            style={{
              padding: '10px',
              border: 'none',
              backgroundColor: 'transparent',
              borderRadius: '10px',
              cursor: 'pointer',
              transition: 'background-color 0.2s ease'
            }}
            aria-label="Close menu"
            onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#F1F5F9'}
            onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
          >
            <X size={20} style={{ color: '#475569' }} />
          </button>
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
                    onClick={() => handleNavClick(item.id)}
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

        {/* Footer */}
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
      </div>
      
      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }
        @keyframes slideIn {
          from { transform: translateX(-100%); }
          to { transform: translateX(0); }
        }
      `}</style>
    </>
  );
}
