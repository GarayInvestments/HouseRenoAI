import { Menu, User, Settings, LogOut, Wifi, WifiOff } from 'lucide-react';
import { useAppStore } from '../stores/appStore';
import { useState, useRef, useEffect } from 'react';

export default function TopBar() {
  const { user, connectionStatus, setMobileDrawerOpen } = useAppStore();
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setDropdownOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <>
      <style>{`
        @media (min-width: 1024px) {
          .mobile-only {
            display: none !important;
          }
        }
      `}</style>
      <div style={{
        position: 'sticky',
        top: 0,
        zIndex: 40,
        backgroundColor: '#FFFFFF',
        borderBottom: '1px solid #E2E8F0',
        boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.05)'
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          height: '64px',
          padding: '0 24px'
        }}>
          {/* Left: Mobile Menu Button */}
          <button
            onClick={() => setMobileDrawerOpen(true)}
            className="mobile-only"
            style={{
              padding: '10px',
              border: 'none',
              backgroundColor: 'transparent',
              borderRadius: '8px',
              cursor: 'pointer',
              transition: 'background-color 0.2s ease'
            }}
            aria-label="Open menu"
            onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#F1F5F9'}
            onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
          >
            <Menu size={20} style={{ color: '#475569' }} />
          </button>

          {/* Center: Logo/Title (visible on mobile) */}
          <div className="mobile-only" style={{
            display: 'flex',
            alignItems: 'center',
            gap: '10px'
          }}>
          <div style={{
            width: '32px',
            height: '32px',
            borderRadius: '8px',
            background: 'linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#FFFFFF',
            fontWeight: '700',
            fontSize: '12px'
          }}>
            HR
          </div>
          <h1 style={{
            fontSize: '15px',
            fontWeight: '600',
            color: '#1E293B'
          }}>
            House Renovators
          </h1>
        </div>

        {/* Right: Connection Status & User Dropdown */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          marginLeft: 'auto'
        }}>
          {/* Connection Indicator */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '8px 14px',
            borderRadius: '10px',
            backgroundColor: '#ECFDF5',
            border: '1px solid #D1FAE5'
          }}>
            {connectionStatus === 'connected' ? (
              <>
                <Wifi size={16} style={{ color: '#059669' }} />
                <span className="hidden sm:inline" style={{
                  fontSize: '13px',
                  fontWeight: '600',
                  color: '#059669'
                }}>Connected</span>
              </>
            ) : (
              <>
                <WifiOff size={16} style={{ color: '#DC2626' }} />
                <span className="hidden sm:inline" style={{
                  fontSize: '13px',
                  fontWeight: '600',
                  color: '#DC2626'
                }}>Disconnected</span>
              </>
            )}
          </div>

          {/* User Dropdown */}
          <div style={{ position: 'relative' }} ref={dropdownRef}>
            <button
              onClick={() => setDropdownOpen(!dropdownOpen)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '10px',
                padding: '6px 12px',
                border: 'none',
                backgroundColor: 'transparent',
                borderRadius: '10px',
                cursor: 'pointer',
                transition: 'background-color 0.2s ease'
              }}
              onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#F1F5F9'}
              onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
            >
              <div style={{
                width: '34px',
                height: '34px',
                borderRadius: '10px',
                background: 'linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#FFFFFF',
                fontWeight: '700',
                fontSize: '13px',
                boxShadow: '0 2px 4px rgba(37, 99, 235, 0.3)'
              }}>
                {user.initials}
              </div>
              <span className="hidden md:block" style={{
                fontWeight: '600',
                fontSize: '14px',
                color: '#1E293B'
              }}>
                {user.name}
              </span>
            </button>

            {/* Dropdown Menu */}
            {dropdownOpen && (
              <div style={{
                position: 'absolute',
                right: 0,
                marginTop: '8px',
                width: '240px',
                backgroundColor: '#FFFFFF',
                borderRadius: '14px',
                boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
                border: '1px solid #E2E8F0',
                overflow: 'hidden'
              }}>
                <div style={{
                  padding: '16px',
                  borderBottom: '1px solid #F1F5F9',
                  backgroundColor: '#F8FAFC'
                }}>
                  <p style={{ fontWeight: '600', fontSize: '14px', color: '#1E293B' }}>{user.name}</p>
                  <p style={{ fontSize: '12px', color: '#64748B', marginTop: '2px' }}>{user.email}</p>
                </div>
                <div style={{ padding: '8px' }}>
                  <button style={{
                    width: '100%',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '10px',
                    padding: '10px 12px',
                    border: 'none',
                    backgroundColor: 'transparent',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    transition: 'background-color 0.2s ease',
                    textAlign: 'left'
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#F1F5F9'}
                  onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}>
                    <User size={18} style={{ color: '#64748B' }} />
                    <span style={{ fontWeight: '500', fontSize: '14px', color: '#1E293B' }}>Profile</span>
                  </button>
                  <button style={{
                    width: '100%',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '10px',
                    padding: '10px 12px',
                    border: 'none',
                    backgroundColor: 'transparent',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    transition: 'background-color 0.2s ease',
                    textAlign: 'left'
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#F1F5F9'}
                  onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}>
                    <Settings size={18} style={{ color: '#64748B' }} />
                    <span style={{ fontWeight: '500', fontSize: '14px', color: '#1E293B' }}>Settings</span>
                  </button>
                  <div style={{ borderTop: '1px solid #F1F5F9', margin: '8px 0' }} />
                  <button 
                    onClick={() => {
                      useAppStore.getState().logout();
                      setDropdownOpen(false);
                    }}
                    style={{
                    width: '100%',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '10px',
                    padding: '10px 12px',
                    border: 'none',
                    backgroundColor: 'transparent',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    transition: 'background-color 0.2s ease',
                    textAlign: 'left'
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#FEF2F2'}
                  onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}>
                    <LogOut size={18} style={{ color: '#DC2626' }} />
                    <span style={{ fontWeight: '600', fontSize: '14px', color: '#DC2626' }}>Log Out</span>
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
    </>
  );
}
