import { Settings as SettingsIcon, User, Bell, Lock, Palette, Globe, Shield } from 'lucide-react';
import { useState } from 'react';

export default function Settings() {
  const [hoveredItem, setHoveredItem] = useState(null);

  const settingSections = [
    {
      id: 'profile',
      title: 'Profile Settings',
      description: 'Manage your personal information and preferences',
      icon: User,
      color: '#2563EB'
    },
    {
      id: 'notifications',
      title: 'Notifications',
      description: 'Configure how you receive updates and alerts',
      icon: Bell,
      color: '#059669'
    },
    {
      id: 'security',
      title: 'Security & Privacy',
      description: 'Manage your password and security settings',
      icon: Lock,
      color: '#DC2626'
    },
    {
      id: 'appearance',
      title: 'Appearance',
      description: 'Customize the look and feel of your workspace',
      icon: Palette,
      color: '#9333EA'
    },
    {
      id: 'language',
      title: 'Language & Region',
      description: 'Set your preferred language and regional settings',
      icon: Globe,
      color: '#D97706'
    },
    {
      id: 'permissions',
      title: 'Permissions',
      description: 'Control access and sharing settings',
      icon: Shield,
      color: '#0891B2'
    }
  ];

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      height: '100%',
      backgroundColor: '#F8FAFC'
    }}>
      {/* Header */}
      <div style={{
        backgroundColor: '#FFFFFF',
        borderBottom: '1px solid #E2E8F0',
        padding: '24px 32px',
        boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.05)'
      }}>
        <h1 style={{
          fontSize: '24px',
          fontWeight: '600',
          color: '#1E293B',
          marginBottom: '4px'
        }}>Settings</h1>
        <p style={{
          color: '#64748B',
          fontSize: '14px'
        }}>
          Manage your account settings and preferences
        </p>
      </div>

      {/* Settings Grid */}
      <div style={{
        flex: 1,
        overflowY: 'auto',
        padding: '32px'
      }}>
        <div style={{
          maxWidth: '1200px',
          margin: '0 auto'
        }}>
          {/* Account Info Card */}
          <div style={{
            backgroundColor: '#FFFFFF',
            borderRadius: '12px',
            padding: '24px',
            border: '1px solid #E2E8F0',
            boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.05)',
            marginBottom: '32px'
          }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '20px'
            }}>
              <div style={{
                width: '80px',
                height: '80px',
                borderRadius: '12px',
                background: 'linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#FFFFFF',
                fontSize: '32px',
                fontWeight: '700',
                boxShadow: '0 4px 6px -1px rgba(37, 99, 235, 0.3)'
              }}>
                SG
              </div>
              <div style={{ flex: 1 }}>
                <h2 style={{
                  fontSize: '20px',
                  fontWeight: '600',
                  color: '#1E293B',
                  marginBottom: '4px'
                }}>Steve Garay</h2>
                <p style={{
                  fontSize: '14px',
                  color: '#64748B',
                  marginBottom: '8px'
                }}>steve@houserenovators.com</p>
                <div style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '6px',
                  padding: '6px 12px',
                  borderRadius: '8px',
                  backgroundColor: '#ECFDF5',
                  border: '1px solid #A7F3D0',
                  fontSize: '13px',
                  fontWeight: '500',
                  color: '#059669'
                }}>
                  <div style={{
                    width: '8px',
                    height: '8px',
                    borderRadius: '50%',
                    backgroundColor: '#059669'
                  }} />
                  Premium Account
                </div>
              </div>
              <button
                style={{
                  padding: '10px 20px',
                  border: '1px solid #E2E8F0',
                  borderRadius: '10px',
                  backgroundColor: '#FFFFFF',
                  color: '#2563EB',
                  fontSize: '14px',
                  fontWeight: '500',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.borderColor = '#2563EB';
                  e.currentTarget.style.backgroundColor = '#EFF6FF';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.borderColor = '#E2E8F0';
                  e.currentTarget.style.backgroundColor = '#FFFFFF';
                }}
              >
                Edit Profile
              </button>
            </div>
          </div>

          {/* Settings Sections Grid */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))',
            gap: '20px'
          }}>
            {settingSections.map((section) => {
              const Icon = section.icon;
              const isHovered = hoveredItem === section.id;

              return (
                <div
                  key={section.id}
                  onMouseEnter={() => setHoveredItem(section.id)}
                  onMouseLeave={() => setHoveredItem(null)}
                  style={{
                    backgroundColor: '#FFFFFF',
                    borderRadius: '12px',
                    padding: '24px',
                    border: '1px solid #E2E8F0',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease',
                    boxShadow: isHovered 
                      ? '0 10px 20px -5px rgba(0, 0, 0, 0.1)'
                      : '0 1px 3px 0 rgba(0, 0, 0, 0.05)',
                    transform: isHovered ? 'translateY(-2px)' : 'translateY(0)'
                  }}
                >
                  <div style={{
                    display: 'flex',
                    alignItems: 'flex-start',
                    gap: '16px'
                  }}>
                    <div style={{
                      width: '48px',
                      height: '48px',
                      borderRadius: '10px',
                      backgroundColor: `${section.color}15`,
                      border: `1px solid ${section.color}30`,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      flexShrink: 0
                    }}>
                      <Icon size={24} style={{ color: section.color }} />
                    </div>
                    <div style={{ flex: 1 }}>
                      <h3 style={{
                        fontSize: '16px',
                        fontWeight: '600',
                        color: '#1E293B',
                        marginBottom: '6px'
                      }}>{section.title}</h3>
                      <p style={{
                        fontSize: '13px',
                        color: '#64748B',
                        lineHeight: '1.5'
                      }}>{section.description}</p>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Danger Zone */}
          <div style={{
            backgroundColor: '#FFFFFF',
            borderRadius: '12px',
            padding: '24px',
            border: '1px solid #FECACA',
            boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.05)',
            marginTop: '32px'
          }}>
            <h3 style={{
              fontSize: '16px',
              fontWeight: '600',
              color: '#DC2626',
              marginBottom: '8px'
            }}>Danger Zone</h3>
            <p style={{
              fontSize: '14px',
              color: '#64748B',
              marginBottom: '16px'
            }}>
              Permanently delete your account and all associated data. This action cannot be undone.
            </p>
            <button
              style={{
                padding: '10px 20px',
                border: '1px solid #DC2626',
                borderRadius: '10px',
                backgroundColor: '#FFFFFF',
                color: '#DC2626',
                fontSize: '14px',
                fontWeight: '500',
                cursor: 'pointer',
                transition: 'all 0.2s ease'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = '#FEF2F2';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = '#FFFFFF';
              }}
            >
              Delete Account
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
