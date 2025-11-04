import { FileText, Plus, Search, Filter, CheckCircle, Clock, AlertCircle } from 'lucide-react';
import { useState } from 'react';

export default function Permits() {
  const [searchTerm, setSearchTerm] = useState('');
  const [hoveredCard, setHoveredCard] = useState(null);
  const [hoveredButton, setHoveredButton] = useState(false);

  const permits = [
    { id: 1, name: 'Building Permit #2024-001', status: 'approved', date: '2024-10-15', location: '123 Main St' },
    { id: 2, name: 'Electrical Permit #2024-042', status: 'pending', date: '2024-10-28', location: '456 Oak Ave' },
    { id: 3, name: 'Plumbing Permit #2024-038', status: 'approved', date: '2024-10-20', location: '789 Pine Rd' },
    { id: 4, name: 'HVAC Permit #2024-055', status: 'review', date: '2024-11-01', location: '321 Elm St' },
  ];

  const getStatusColor = (status) => {
    switch (status) {
      case 'approved': return { bg: '#ECFDF5', text: '#059669', border: '#A7F3D0' };
      case 'pending': return { bg: '#FEF3C7', text: '#D97706', border: '#FCD34D' };
      case 'review': return { bg: '#DBEAFE', text: '#2563EB', border: '#93C5FD' };
      default: return { bg: '#F3F4F6', text: '#6B7280', border: '#D1D5DB' };
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'approved': return <CheckCircle size={16} />;
      case 'pending': return <Clock size={16} />;
      case 'review': return <AlertCircle size={16} />;
      default: return null;
    }
  };

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
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '16px'
        }}>
          <div>
            <h1 style={{
              fontSize: '24px',
              fontWeight: '600',
              color: '#1E293B',
              marginBottom: '4px'
            }}>Permits</h1>
            <p style={{
              color: '#64748B',
              fontSize: '14px'
            }}>
              Manage and track all your building permits
            </p>
          </div>
          <button
            onMouseEnter={() => setHoveredButton(true)}
            onMouseLeave={() => setHoveredButton(false)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              background: hoveredButton 
                ? 'linear-gradient(135deg, #1D4ED8 0%, #1E40AF 100%)'
                : 'linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%)',
              color: '#FFFFFF',
              border: 'none',
              padding: '10px 20px',
              borderRadius: '10px',
              fontSize: '14px',
              fontWeight: '500',
              cursor: 'pointer',
              transition: 'all 0.2s ease',
              boxShadow: hoveredButton 
                ? '0 6px 12px -2px rgba(37, 99, 235, 0.4)'
                : '0 4px 6px -1px rgba(37, 99, 235, 0.3)',
              transform: hoveredButton ? 'translateY(-1px)' : 'translateY(0)'
            }}
          >
            <Plus size={18} />
            New Permit
          </button>
        </div>

        {/* Search and Filter Bar */}
        <div style={{
          display: 'flex',
          gap: '12px',
          marginTop: '16px'
        }}>
          <div style={{
            flex: 1,
            position: 'relative'
          }}>
            <Search size={18} style={{
              position: 'absolute',
              left: '14px',
              top: '50%',
              transform: 'translateY(-50%)',
              color: '#64748B'
            }} />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search permits..."
              style={{
                width: '100%',
                padding: '10px 14px 10px 44px',
                border: '1px solid #E2E8F0',
                borderRadius: '10px',
                fontSize: '14px',
                color: '#1E293B',
                outline: 'none',
                transition: 'all 0.2s ease',
                backgroundColor: '#FFFFFF'
              }}
              onFocus={(e) => {
                e.target.style.borderColor = '#2563EB';
                e.target.style.boxShadow = '0 0 0 3px rgba(37, 99, 235, 0.1)';
              }}
              onBlur={(e) => {
                e.target.style.borderColor = '#E2E8F0';
                e.target.style.boxShadow = 'none';
              }}
            />
          </div>
          <button
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '10px 16px',
              border: '1px solid #E2E8F0',
              borderRadius: '10px',
              backgroundColor: '#FFFFFF',
              color: '#64748B',
              fontSize: '14px',
              fontWeight: '500',
              cursor: 'pointer',
              transition: 'all 0.2s ease'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.borderColor = '#2563EB';
              e.currentTarget.style.color = '#2563EB';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.borderColor = '#E2E8F0';
              e.currentTarget.style.color = '#64748B';
            }}
          >
            <Filter size={18} />
            Filter
          </button>
        </div>
      </div>

      {/* Permits Grid */}
      <div style={{
        flex: 1,
        overflowY: 'auto',
        padding: '32px'
      }}>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))',
          gap: '24px',
          maxWidth: '1400px',
          margin: '0 auto'
        }}>
          {permits.map((permit) => {
            const statusStyle = getStatusColor(permit.status);
            const isHovered = hoveredCard === permit.id;

            return (
              <div
                key={permit.id}
                onMouseEnter={() => setHoveredCard(permit.id)}
                onMouseLeave={() => setHoveredCard(null)}
                style={{
                  backgroundColor: '#FFFFFF',
                  borderRadius: '12px',
                  padding: '20px',
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
                  gap: '12px',
                  marginBottom: '16px'
                }}>
                  <div style={{
                    width: '44px',
                    height: '44px',
                    borderRadius: '10px',
                    background: 'linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    flexShrink: 0,
                    boxShadow: '0 4px 6px -1px rgba(37, 99, 235, 0.3)'
                  }}>
                    <FileText size={22} style={{ color: '#FFFFFF' }} />
                  </div>
                  <div style={{ flex: 1 }}>
                    <h3 style={{
                      fontSize: '16px',
                      fontWeight: '600',
                      color: '#1E293B',
                      marginBottom: '4px'
                    }}>{permit.name}</h3>
                    <p style={{
                      fontSize: '13px',
                      color: '#64748B'
                    }}>{permit.location}</p>
                  </div>
                </div>

                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  paddingTop: '16px',
                  borderTop: '1px solid #F1F5F9'
                }}>
                  <span style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '6px',
                    padding: '6px 12px',
                    borderRadius: '8px',
                    backgroundColor: statusStyle.bg,
                    color: statusStyle.text,
                    fontSize: '13px',
                    fontWeight: '500',
                    border: `1px solid ${statusStyle.border}`
                  }}>
                    {getStatusIcon(permit.status)}
                    {permit.status.charAt(0).toUpperCase() + permit.status.slice(1)}
                  </span>
                  <span style={{
                    fontSize: '13px',
                    color: '#64748B'
                  }}>{permit.date}</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
