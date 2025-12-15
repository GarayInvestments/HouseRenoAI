import { FileText, Plus, Search, Filter, CheckCircle, Clock, AlertCircle, Loader2, User, FolderKanban } from 'lucide-react';
import { useState, useEffect, useMemo } from 'react';
import api from '../lib/api';
import { useAppStore } from '../stores/appStore';
import { usePermitsStore } from '../stores/permitsStore';
import LoadingScreen from '../components/LoadingScreen';
import ErrorState from '../components/ErrorState';

export default function Permits() {
  const { navigateToPermit } = useAppStore();
  
  // Use permitsStore for data and filtering
  const { 
    permits, 
    loading, 
    error, 
    filter,
    setPermits,
    setLoading,
    setError,
    setFilter,
    getFilteredPermits,
    isCacheValid
  } = usePermitsStore();
  
  const [searchTerm, setSearchTerm] = useState('');
  const [hoveredCard, setHoveredCard] = useState(null);
  const [hoveredButton, setHoveredButton] = useState(false);
  const [projects, setProjects] = useState([]);
  const [clients, setClients] = useState([]);
  const [clientFilter, setClientFilter] = useState(null); // Local client filter

  useEffect(() => {
    fetchAllData();
    // Set initial history state for permits page
    window.history.replaceState({ page: 'permits' }, '');
  }, []);

  const fetchAllData = async () => {
    // Use cache if valid
    if (isCacheValid() && permits.length > 0) {
      return;
    }
    
    try {
      setLoading(true);
      setError(null);
      
      // Fetch all data in parallel
      const [permitsResponse, projectsData, clientsData] = await Promise.all([
        api.getPermits(),
        api.getProjects(),
        api.getClients()
      ]);
      
      // Handle paginated response from permits endpoint
      const permitsData = permitsResponse?.items || permitsResponse || [];
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
    const project = projects.find(p => 
      p['Project ID'] === projectId || 
      p.project_id === projectId
    );
    return project?.['Project Name'] || project?.project_name || projectId || 'Unknown Project';
  };

  const getClientNameForPermit = (permit) => {
    // First, find the project for this permit
    const permitProjectId = permit['Project ID'] || permit.project_id;
    const project = projects.find(p => 
      p['Project ID'] === permitProjectId || 
      p.project_id === permitProjectId
    );
    if (!project) return null;
    
    // Then find the client using the project's client ID
    const clientId = project['Client ID'] || project.client_id;
    if (!clientId) return null;
    
    const client = clients.find(c => 
      c['Client ID'] === clientId || 
      c['ID'] === clientId ||
      c.client_id === clientId ||
      c.id === clientId
    );
    return client?.['Full Name'] || client?.['Client Name'] || client?.full_name || clientId;
  };

  // Memoized filtered permits (status filter + client filter + search)
  const filteredPermits = useMemo(() => {
    let result = getFilteredPermits(); // Apply status filter from store
    
    // Apply client filter
    if (clientFilter) {
      // Get all project IDs for this client
      const clientProjectIds = projects
        .filter(p => p['Client ID'] === clientFilter)
        .map(p => p['Project ID']);
      // Filter permits by those project IDs
      result = result.filter(permit => clientProjectIds.includes(permit['Project ID']));
    }
    
    // Apply search filter
    if (searchTerm) {
      result = result.filter(permit => {
        const permitNumber = permit['Permit Number'] || permit.permit_number || permit.business_id || '';
        const permitStatus = permit['Permit Status'] || permit.status || '';
        return permitNumber.toLowerCase().includes(searchTerm.toLowerCase()) ||
               permitStatus.toLowerCase().includes(searchTerm.toLowerCase());
      });
    }
    
    return result;
  }, [permits, filter, clientFilter, searchTerm, projects]);

  // Get client name for filter badge
  const getFilteredClientName = () => {
    if (!clientFilter) return null;
    const client = clients.find(c => c['Client ID'] === clientFilter || c['ID'] === clientFilter);
    return client?.['Full Name'] || client?.['Client Name'] || clientFilter;
  };

  const clearClientFilter = () => {
    setClientFilter(null);
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
                {clientFilter 
                  ? `Showing permits for ${getFilteredClientName()}` 
                  : 'Manage and track all your building permits'
                }
              </p>
            </div>
            {clientFilter && (
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
                  onClick={clearClientFilter}
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
            gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
            gap: '24px',
            maxWidth: '1400px',
            margin: '0 auto'
          }}>
            {filteredPermits.map((permit) => {
              const permitStatus = permit['Permit Status'] || permit.status;
              const permitId = permit['Permit ID'] || permit.permit_id;
              const statusStyle = getStatusColor(permitStatus);
              const isHovered = hoveredCard === permitId;

              return (
                <div
                  key={permitId}
                  onClick={() => navigateToPermit(permitId)}
                  onMouseEnter={() => setHoveredCard(permitId)}
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
                      }}>
                        {permit['Permit Number'] || permit.permit_number || permit.business_id || 'Unknown Permit'}
                      </h3>
                      <div style={{
                        display: 'flex',
                        flexDirection: 'column',
                        gap: '2px'
                      }}>
                        {(permit['Project ID'] || permit.project_id) && (
                          <p style={{
                            fontSize: '12px',
                            color: '#64748B',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '4px'
                          }}>
                            <FolderKanban size={12} />
                            {getProjectName(permit['Project ID'] || permit.project_id)}
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
                      {getStatusIcon(permitStatus)}
                      {permitStatus || 'Unknown'}
                    </span>
                    <span style={{
                      fontSize: '13px',
                      color: '#64748B'
                    }}>{formatDate(permit['Date Submitted'] || permit.application_date)}</span>
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
