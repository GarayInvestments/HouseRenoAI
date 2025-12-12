import { FileText, Plus, Search, Filter, CheckCircle, Clock, AlertCircle, Loader2, User, FolderKanban } from 'lucide-react';
import { useState, useEffect } from 'react';
import api from '../lib/api';
import { useAppStore } from '../stores/appStore';
import LoadingScreen from '../components/LoadingScreen';
import ErrorState from '../components/ErrorState';

export default function Permits() {
  const { navigateToPermit, permitsFilter, setPermitsFilter } = useAppStore();
  const [searchTerm, setSearchTerm] = useState('');
  const [hoveredCard, setHoveredCard] = useState(null);
  const [hoveredButton, setHoveredButton] = useState(false);
  const [permits, setPermits] = useState([]);
  const [projects, setProjects] = useState([]);
  const [clients, setClients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchAllData();
    // Set initial history state for permits page
    window.history.replaceState({ page: 'permits' }, '');
  }, []);

  const fetchAllData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Fetch all data in parallel
      const [permitsData, projectsData, clientsData] = await Promise.all([
        api.getPermits(),
        api.getProjects(),
        api.getClients()
      ]);
      
      setPermits(Array.isArray(permitsData) ? permitsData : []);
      setProjects(Array.isArray(projectsData) ? projectsData : []);
      setClients(Array.isArray(clientsData) ? clientsData : []);
    } catch {
      setError('Failed to load permits. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const getProjectName = (projectId) => {
    const project = projects.find(p => p['Project ID'] === projectId);
    return project?.['Project Name'] || projectId || 'Unknown Project';
  };

  const getClientNameForPermit = (permit) => {
    // First, find the project for this permit
    const project = projects.find(p => p['Project ID'] === permit['Project ID']);
    if (!project) return null;
    
    // Then find the client using the project's client ID
    const clientId = project['Client ID'];
    if (!clientId) return null;
    
    const client = clients.find(c => c['Client ID'] === clientId || c['ID'] === clientId);
    return client?.['Full Name'] || client?.['Client Name'] || clientId;
  };

  // Apply client filter first if present
  let baseFilteredPermits = permits;
  if (permitsFilter?.clientId) {
    // Get all project IDs for this client
    const clientProjectIds = projects
      .filter(p => p['Client ID'] === permitsFilter.clientId)
      .map(p => p['Project ID']);
    // Filter permits by those project IDs
    baseFilteredPermits = permits.filter(permit => clientProjectIds.includes(permit['Project ID']));
  }

  // Then apply search filter
  const filteredPermits = baseFilteredPermits.filter(permit =>
    permit['Permit Number']?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    permit['Permit Status']?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Get client name for filter badge
  const getFilteredClientName = () => {
    if (!permitsFilter?.clientId) return null;
    const client = clients.find(c => c['Client ID'] === permitsFilter.clientId || c['ID'] === permitsFilter.clientId);
    return client?.['Full Name'] || client?.['Client Name'] || permitsFilter.clientId;
  };

  const clearFilter = () => {
    setPermitsFilter(null);
  };

  const getStatusColor = (status) => {
    const lowerStatus = status?.toLowerCase();
    if (lowerStatus?.includes('approved')) {
      return { bg: '#ECFDF5', text: '#059669', border: '#A7F3D0' };
    }
    if (lowerStatus?.includes('pending') || lowerStatus?.includes('submitted')) {
      return { bg: '#FEF3C7', text: '#D97706', border: '#FCD34D' };
    }
    if (lowerStatus?.includes('review')) {
      return { bg: '#DBEAFE', text: '#2563EB', border: '#93C5FD' };
    }
    return { bg: '#F3F4F6', text: '#6B7280', border: '#D1D5DB' };
  };

  const getStatusIcon = (status) => {
    const lowerStatus = status?.toLowerCase();
    if (lowerStatus?.includes('approved')) return <CheckCircle size={16} />;
    if (lowerStatus?.includes('pending') || lowerStatus?.includes('submitted')) return <Clock size={16} />;
    if (lowerStatus?.includes('review')) return <AlertCircle size={16} />;
    return null;
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Not set';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  if (loading) {
    return <LoadingScreen />;
  }

  if (error) {
    return (
      <div style={{ padding: '20px', backgroundColor: '#F8FAFC', minHeight: '100vh' }}>
        <ErrorState message={error} onRetry={fetchAllData} fullScreen />
      </div>
    );
  }

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
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
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
                {permitsFilter?.clientId 
                  ? `Showing permits for ${getFilteredClientName()}` 
                  : 'Manage and track all your building permits'
                }
              </p>
            </div>
            {permitsFilter?.clientId && (
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '4px 12px',
                backgroundColor: '#DBEAFE',
                borderRadius: '6px',
                fontSize: '14px',
                color: '#1E40AF'
              }}>
                <span style={{ fontWeight: '500' }}>Client: {getFilteredClientName()}</span>
                <button
                  onClick={clearFilter}
                  style={{
                    background: 'none',
                    border: 'none',
                    color: '#1E40AF',
                    fontSize: '18px',
                    fontWeight: '600',
                    cursor: 'pointer',
                    padding: '0 4px',
                    lineHeight: 1,
                    transition: 'color 0.2s ease'
                  }}
                  onMouseEnter={(e) => e.target.style.color = '#1E3A8A'}
                  onMouseLeave={(e) => e.target.style.color = '#1E40AF'}
                >
                  ×
                </button>
              </div>
            )}
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
        {loading ? (
          <div style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            height: '400px',
            gap: '16px'
          }}>
            <Loader2 className="animate-spin" size={40} style={{ color: '#2563EB' }} />
            <p style={{ color: '#64748B', fontSize: '14px' }}>Loading permits...</p>
          </div>
        ) : error ? (
          <div style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            height: '400px',
            gap: '16px'
          }}>
            <AlertCircle size={40} style={{ color: '#DC2626' }} />
            <p style={{ color: '#DC2626', fontSize: '14px' }}>{error}</p>
            <button
              onClick={fetchAllData}
              style={{
                padding: '8px 16px',
                backgroundColor: '#2563EB',
                color: '#FFFFFF',
                border: 'none',
                borderRadius: '8px',
                fontSize: '14px',
                cursor: 'pointer'
              }}
            >
              Retry
            </button>
          </div>
        ) : (
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))',
            gap: '24px',
            maxWidth: '1400px',
            margin: '0 auto'
          }}>
            {filteredPermits.map((permit) => {
              const statusStyle = getStatusColor(permit['Permit Status']);
              const isHovered = hoveredCard === permit['Permit ID'];

              return (
                <div
                  key={permit['Permit ID']}
                  onClick={() => navigateToPermit(permit['Permit ID'])}
                  onMouseEnter={() => setHoveredCard(permit['Permit ID'])}
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
                      }}>{permit['Permit Number'] || 'Unknown Permit'}</h3>
                      <div style={{
                        display: 'flex',
                        flexDirection: 'column',
                        gap: '2px'
                      }}>
                        {permit['Project ID'] && (
                          <p style={{
                            fontSize: '12px',
                            color: '#64748B',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '4px'
                          }}>
                            <FolderKanban size={12} />
                            {getProjectName(permit['Project ID'])}
                          </p>
                        )}
                        {getClientNameForPermit(permit) && (
                          <p style={{
                            fontSize: '12px',
                            color: '#64748B',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '4px'
                          }}>
                            <User size={12} />
                            {getClientNameForPermit(permit)}
                          </p>
                        )}
                      </div>
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
                      {getStatusIcon(permit['Permit Status'])}
                      {permit['Permit Status'] || 'Unknown'}
                    </span>
                    <span style={{
                      fontSize: '13px',
                      color: '#64748B'
                    }}>{formatDate(permit['Date Submitted'])}</span>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
