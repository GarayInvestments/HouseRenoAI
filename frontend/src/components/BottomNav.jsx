import { Home, MessageSquare, FileText, FolderKanban, Settings } from 'lucide-react';
import { useAppStore } from '../stores/appStore';

const navItems = [
  { id: 'dashboard', label: 'Home', icon: Home },
  { id: 'ai-assistant', label: 'AI', icon: MessageSquare },
  { id: 'permits', label: 'Permits', icon: FileText },
  { id: 'projects', label: 'Projects', icon: FolderKanban },
  { id: 'settings', label: 'Settings', icon: Settings },
];

export default function BottomNav() {
  const { currentView, setCurrentView } = useAppStore();

  return (
    <>
      {/* Bottom Navigation - Mobile Only */}
      <nav
        className="md:hidden"
        style={{
          position: 'fixed',
          bottom: 0,
          left: 0,
          right: 0,
          backgroundColor: '#FFFFFF',
          borderTop: '1px solid #E2E8F0',
          boxShadow: '0 -2px 10px rgba(0, 0, 0, 0.05)',
          zIndex: 50,
          paddingBottom: 'env(safe-area-inset-bottom)',
        }}
      >
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-around',
            alignItems: 'center',
            height: '64px',
            maxWidth: '100%',
            margin: '0 auto',
          }}
        >
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentView === item.id || 
                           (item.id === 'projects' && currentView === 'project-details') ||
                           (item.id === 'permits' && currentView === 'permit-details');

            return (
              <button
                key={item.id}
                onClick={() => {
                  if (item.id === 'projects' && currentView === 'project-details') {
                    // If on project details and clicking projects, navigate to projects list
                    setCurrentView('projects');
                  } else if (item.id === 'permits' && currentView === 'permit-details') {
                    // If on permit details and clicking permits, navigate to permits list
                    setCurrentView('permits');
                  } else {
                    setCurrentView(item.id);
                  }
                }}
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flex: 1,
                  height: '100%',
                  border: 'none',
                  background: 'none',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease',
                  padding: '8px 4px',
                  position: 'relative',
                }}
              >
                {/* Active Indicator */}
                {isActive && (
                  <div
                    style={{
                      position: 'absolute',
                      top: 0,
                      left: '50%',
                      transform: 'translateX(-50%)',
                      width: '32px',
                      height: '3px',
                      backgroundColor: '#2563EB',
                      borderRadius: '0 0 3px 3px',
                    }}
                  />
                )}

                {/* Icon Container */}
                <div
                  style={{
                    width: '28px',
                    height: '28px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    marginBottom: '4px',
                    transition: 'transform 0.2s ease',
                    transform: isActive ? 'scale(1.1)' : 'scale(1)',
                  }}
                >
                  <Icon
                    size={22}
                    style={{
                      color: isActive ? '#2563EB' : '#64748B',
                      strokeWidth: isActive ? 2.5 : 2,
                      transition: 'color 0.2s ease',
                    }}
                  />
                </div>

                {/* Label */}
                <span
                  style={{
                    fontSize: '11px',
                    fontWeight: isActive ? '600' : '500',
                    color: isActive ? '#2563EB' : '#64748B',
                    transition: 'all 0.2s ease',
                    letterSpacing: '0.01em',
                  }}
                >
                  {item.label}
                </span>
              </button>
            );
          })}
        </div>
      </nav>

      {/* Spacer to prevent content from being hidden behind bottom nav on mobile */}
      <div className="md:hidden" style={{ height: '64px' }} />
    </>
  );
}
