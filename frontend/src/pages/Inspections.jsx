import { ClipboardCheck, Plus, Search, Filter, Calendar, User, Building2, Loader2, CheckCircle, AlertCircle, Clock, XCircle } from 'lucide-react';
import { useState, useEffect, useMemo } from 'react';
import api from '../lib/api';
import { useAppStore } from '../stores/appStore';
import useInspectionsStore from '../stores/inspectionsStore';
import LoadingScreen from '../components/LoadingScreen';
import ErrorState from '../components/ErrorState';

export default function Inspections() {
  const { navigateToInspectionDetails } = useAppStore();
  
  // Use inspectionsStore for data and filtering
  const { 
    inspections, 
    loading, 
    error, 
    filter,
    setFilter,
    fetchInspections,
    getFilteredInspections
  } = useInspectionsStore();
  
  const [searchTerm, setSearchTerm] = useState('');
  const [hoveredCard, setHoveredCard] = useState(null);
  const [projects, setProjects] = useState([]);
  const [permits, setPermits] = useState([]);

  useEffect(() => {
    fetchAllData();
    window.history.replaceState({ page: 'inspections' }, '');
  }, []);

  const fetchAllData = async () => {
    try {
      // Fetch all data in parallel
      const [inspectionsData, projectsData, permitsData] = await Promise.all([
        fetchInspections(),
        api.getProjects(),
        api.getPermits()
      ]);
      
      setProjects(Array.isArray(projectsData) ? projectsData : []);
      const permitsArray = permitsData?.items || permitsData || [];
      setPermits(Array.isArray(permitsArray) ? permitsArray : []);
    } catch (err) {
      console.error('Failed to load inspections:', err);
    }
  };

  const getProjectName = (projectId) => {
    const project = projects.find(p => 
      p.project_id === projectId || 
      p['Project ID'] === projectId
    );
    return project?.project_name || project?.['Project Name'] || 'Unknown Project';
  };

  const getPermitNumber = (permitId) => {
    const permit = permits.find(p => 
      p.permit_id === permitId || 
      p['Permit ID'] === permitId
    );
    return permit?.permit_number || permit?.business_id || permit?.['Permit Number'] || 'N/A';
  };

  // Format date helper
  const formatDate = (dateString) => {
    if (!dateString) return 'Not set';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  // Memoized filtered inspections (status filter + search)
  const filteredInspections = useMemo(() => {
    let result = getFilteredInspections(); // Apply status filter from store
    
    // Apply search filter
    if (searchTerm) {
      result = result.filter(inspection => {
        const businessId = inspection.business_id || inspection['Inspection ID'] || '';
        const type = inspection.inspection_type || inspection['Inspection Type'] || '';
        const inspector = inspection.inspector || '';
        const projectName = getProjectName(inspection.project_id || inspection['Project ID']);
        
        const searchLower = searchTerm.toLowerCase();
        return businessId.toLowerCase().includes(searchLower) ||
               type.toLowerCase().includes(searchLower) ||
               inspector.toLowerCase().includes(searchLower) ||
               projectName.toLowerCase().includes(searchLower);
      });
    }
    
    return result;
  }, [inspections, filter, searchTerm, projects]);

  const getStatusColor = (status) => {
    const lowerStatus = status?.toLowerCase();
    if (lowerStatus === 'completed') {
      return { bg: '#ECFDF5', text: '#059669', border: '#A7F3D0' };
    }
    if (lowerStatus === 'in-progress') {
      return { bg: '#DBEAFE', text: '#2563EB', border: '#93C5FD' };
    }
    if (lowerStatus === 'scheduled') {
      return { bg: '#FEF3C7', text: '#D97706', border: '#FCD34D' };
    }
    if (lowerStatus === 'failed') {
      return { bg: '#FEE2E2', text: '#DC2626', border: '#FECACA' };
    }
    if (lowerStatus === 'cancelled') {
      return { bg: '#F3F4F6', text: '#6B7280', border: '#D1D5DB' };
    }
    return { bg: '#F3F4F6', text: '#6B7280', border: '#D1D5DB' };
  };

  const getStatusIcon = (status) => {
    const lowerStatus = status?.toLowerCase();
    if (lowerStatus === 'completed') return <CheckCircle size={16} />;
    if (lowerStatus === 'in-progress') return <Loader2 size={16} className="animate-spin" />;
    if (lowerStatus === 'scheduled') return <Clock size={16} />;
    if (lowerStatus === 'failed') return <AlertCircle size={16} />;
    if (lowerStatus === 'cancelled') return <XCircle size={16} />;
    return <Clock size={16} />;
  };

  const getResultBadge = (result) => {
    if (!result) return null;
    
    const lowerResult = result.toLowerCase();
    let color = { bg: '#F3F4F6', text: '#6B7280', border: '#D1D5DB' };
    
    if (lowerResult === 'pass') {
      color = { bg: '#ECFDF5', text: '#059669', border: '#A7F3D0' };
    } else if (lowerResult === 'fail') {
      color = { bg: '#FEE2E2', text: '#DC2626', border: '#FECACA' };
    } else if (lowerResult === 'partial') {
      color = { bg: '#FEF3C7', text: '#D97706', border: '#FCD34D' };
    }
    
    return (
      <span style={{
        display: 'inline-flex',
        alignItems: 'center',
        padding: '2px 8px',
        fontSize: '11px',
        fontWeight: '600',
        backgroundColor: color.bg,
        color: color.text,
        border: `1px solid ${color.border}`,
        borderRadius: '4px',
        marginLeft: '8px'
      }}>
        {result}
      </span>
    );
  };

  if (loading && inspections.length === 0) {
    return <LoadingScreen message="Loading inspections..." />;
  }

  if (error && inspections.length === 0) {
    return <ErrorState message={error} onRetry={fetchAllData} />;
  }

  return (
    <div style={{
      backgroundColor: '#F8FAFC',
      minHeight: '100vh',
      padding: '32px'
    }}>
      <div style={{
        maxWidth: '1400px',
        margin: '0 auto'
      }}>
        {/* Header */}
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'flex-start',
          marginBottom: '32px'
        }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
              <ClipboardCheck size={32} color="#6366F1" strokeWidth={2} />
              <h1 style={{
                fontSize: '32px',
                fontWeight: '700',
                color: '#1E293B',
                margin: 0
              }}>
                Inspections
              </h1>
            </div>
            <p style={{
              fontSize: '16px',
              color: '#64748B',
              margin: 0
            }}>
              Track building inspections and deficiencies
            </p>
          </div>

          <button
            onMouseEnter={() => setHoveredCard('add-button')}
            onMouseLeave={() => setHoveredCard(null)}
            onClick={() => {/* TODO: Open create inspection modal */}}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '12px 24px',
              backgroundColor: hoveredCard === 'add-button' ? '#5B21B6' : '#6366F1',
              color: '#FFFFFF',
              border: 'none',
              borderRadius: '8px',
              fontSize: '15px',
              fontWeight: '600',
              cursor: 'pointer',
              transition: 'all 0.2s',
              boxShadow: '0 2px 4px rgba(99, 102, 241, 0.2)'
            }}
          >
            <Plus size={20} />
            New Inspection
          </button>
        </div>

        {/* Filters and Search */}
        <div style={{
          display: 'flex',
          gap: '16px',
          marginBottom: '24px',
          flexWrap: 'wrap'
        }}>
          {/* Status Filters */}
          <div style={{
            display: 'flex',
            gap: '8px',
            padding: '4px',
            backgroundColor: '#FFFFFF',
            borderRadius: '8px',
            border: '1px solid #E2E8F0'
          }}>
            {['all', 'scheduled', 'in-progress', 'completed', 'failed'].map(status => (
              <button
                key={status}
                onClick={() => setFilter(status)}
                style={{
                  padding: '8px 16px',
                  backgroundColor: filter === status ? '#6366F1' : 'transparent',
                  color: filter === status ? '#FFFFFF' : '#64748B',
                  border: 'none',
                  borderRadius: '6px',
                  fontSize: '14px',
                  fontWeight: '600',
                  cursor: 'pointer',
                  transition: 'all 0.2s',
                  textTransform: 'capitalize'
                }}
              >
                {status === 'all' ? 'All' : status.replace('-', ' ')}
              </button>
            ))}
          </div>

          {/* Search */}
          <div style={{
            flex: 1,
            minWidth: '300px',
            position: 'relative'
          }}>
            <Search size={20} color="#94A3B8" style={{
              position: 'absolute',
              left: '12px',
              top: '50%',
              transform: 'translateY(-50%)'
            }} />
            <input
              type="text"
              placeholder="Search by ID, type, inspector, or project..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              style={{
                width: '100%',
                padding: '12px 12px 12px 44px',
                fontSize: '15px',
                border: '1px solid #E2E8F0',
                borderRadius: '8px',
                backgroundColor: '#FFFFFF'
              }}
            />
          </div>
        </div>

        {/* Stats Summary */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: '16px',
          marginBottom: '24px'
        }}>
          <div style={{
            padding: '20px',
            backgroundColor: '#FFFFFF',
            borderRadius: '8px',
            border: '1px solid #E2E8F0'
          }}>
            <div style={{ fontSize: '14px', color: '#64748B', marginBottom: '4px' }}>Total Inspections</div>
            <div style={{ fontSize: '24px', fontWeight: '700', color: '#1E293B' }}>{inspections.length}</div>
          </div>
          <div style={{
            padding: '20px',
            backgroundColor: '#FFFFFF',
            borderRadius: '8px',
            border: '1px solid #E2E8F0'
          }}>
            <div style={{ fontSize: '14px', color: '#64748B', marginBottom: '4px' }}>Scheduled</div>
            <div style={{ fontSize: '24px', fontWeight: '700', color: '#D97706' }}>
              {inspections.filter(i => (i.status || '').toLowerCase() === 'scheduled').length}
            </div>
          </div>
          <div style={{
            padding: '20px',
            backgroundColor: '#FFFFFF',
            borderRadius: '8px',
            border: '1px solid #E2E8F0'
          }}>
            <div style={{ fontSize: '14px', color: '#64748B', marginBottom: '4px' }}>In Progress</div>
            <div style={{ fontSize: '24px', fontWeight: '700', color: '#2563EB' }}>
              {inspections.filter(i => (i.status || '').toLowerCase() === 'in-progress').length}
            </div>
          </div>
          <div style={{
            padding: '20px',
            backgroundColor: '#FFFFFF',
            borderRadius: '8px',
            border: '1px solid #E2E8F0'
          }}>
            <div style={{ fontSize: '14px', color: '#64748B', marginBottom: '4px' }}>Completed</div>
            <div style={{ fontSize: '24px', fontWeight: '700', color: '#059669' }}>
              {inspections.filter(i => (i.status || '').toLowerCase() === 'completed').length}
            </div>
          </div>
        </div>

        {/* Inspections Grid */}
        {filteredInspections.length === 0 ? (
          <div style={{
            padding: '64px 24px',
            textAlign: 'center',
            backgroundColor: '#FFFFFF',
            borderRadius: '12px',
            border: '2px dashed #E2E8F0'
          }}>
            <ClipboardCheck size={48} color="#CBD5E1" style={{ margin: '0 auto 16px' }} />
            <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#64748B', margin: '0 0 8px 0' }}>
              {searchTerm ? 'No inspections found' : 'No inspections yet'}
            </h3>
            <p style={{ fontSize: '15px', color: '#94A3B8', margin: 0 }}>
              {searchTerm ? 'Try adjusting your search or filters' : 'Create your first inspection to get started'}
            </p>
          </div>
        ) : (
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(380px, 1fr))',
            gap: '20px'
          }}>
            {filteredInspections.map((inspection) => {
              const inspectionStatus = inspection.status || inspection['Inspection Status'] || 'unknown';
              const inspectionId = inspection.inspection_id || inspection['Inspection ID'];
              const businessId = inspection.business_id || inspectionId;
              const inspectionType = inspection.inspection_type || inspection['Inspection Type'] || 'Unknown Type';
              const scheduledDate = inspection.scheduled_date || inspection['Scheduled Date'];
              const completedDate = inspection.completed_date || inspection['Completed Date'];
              const inspector = inspection.inspector || 'Not assigned';
              const result = inspection.result || inspection['Result'];
              const projectId = inspection.project_id || inspection['Project ID'];
              const permitId = inspection.permit_id || inspection['Permit ID'];
              const statusColor = getStatusColor(inspectionStatus);

              return (
                <div
                  key={inspectionId}
                  onMouseEnter={() => setHoveredCard(inspectionId)}
                  onMouseLeave={() => setHoveredCard(null)}
                  onClick={() => navigateToInspectionDetails(inspectionId)}
                  style={{
                    padding: '24px',
                    backgroundColor: '#FFFFFF',
                    borderRadius: '12px',
                    border: `2px solid ${hoveredCard === inspectionId ? '#6366F1' : '#E2E8F0'}`,
                    cursor: 'pointer',
                    transition: 'all 0.2s',
                    transform: hoveredCard === inspectionId ? 'translateY(-2px)' : 'translateY(0)',
                    boxShadow: hoveredCard === inspectionId ? '0 8px 16px rgba(0,0,0,0.08)' : '0 2px 4px rgba(0,0,0,0.04)'
                  }}
                >
                  {/* Header */}
                  <div style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'flex-start',
                    marginBottom: '16px'
                  }}>
                    <div style={{ flex: 1 }}>
                      <h3 style={{
                        fontSize: '18px',
                        fontWeight: '700',
                        color: '#1E293B',
                        margin: '0 0 4px 0'
                      }}>
                        {inspectionType}
                      </h3>
                      <div style={{
                        fontSize: '13px',
                        color: '#64748B',
                        fontFamily: 'monospace'
                      }}>
                        {businessId}
                      </div>
                    </div>
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '4px',
                      padding: '6px 12px',
                      fontSize: '13px',
                      fontWeight: '600',
                      backgroundColor: statusColor.bg,
                      color: statusColor.text,
                      border: `1px solid ${statusColor.border}`,
                      borderRadius: '6px'
                    }}>
                      {getStatusIcon(inspectionStatus)}
                      <span style={{ textTransform: 'capitalize' }}>
                        {inspectionStatus.replace('-', ' ')}
                      </span>
                    </div>
                  </div>

                  {/* Details */}
                  <div style={{
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '12px',
                    paddingTop: '16px',
                    borderTop: '1px solid #F1F5F9'
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <Building2 size={16} color="#94A3B8" />
                      <span style={{ fontSize: '14px', color: '#64748B' }}>
                        {getProjectName(projectId)}
                      </span>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <User size={16} color="#94A3B8" />
                      <span style={{ fontSize: '14px', color: '#64748B' }}>
                        {inspector}
                      </span>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <Calendar size={16} color="#94A3B8" />
                      <span style={{ fontSize: '14px', color: '#64748B' }}>
                        {completedDate ? `Completed: ${formatDate(completedDate)}` : `Scheduled: ${formatDate(scheduledDate)}`}
                      </span>
                    </div>

                    {result && (
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span style={{ fontSize: '14px', color: '#64748B', fontWeight: '600' }}>
                          Result:
                        </span>
                        {getResultBadge(result)}
                      </div>
                    )}
                  </div>

                  {/* Deficiencies count */}
                  {inspection.deficiencies && Array.isArray(inspection.deficiencies) && inspection.deficiencies.length > 0 && (
                    <div style={{
                      marginTop: '12px',
                      padding: '8px 12px',
                      backgroundColor: '#FEF3C7',
                      borderRadius: '6px',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px'
                    }}>
                      <AlertCircle size={16} color="#D97706" />
                      <span style={{ fontSize: '13px', color: '#D97706', fontWeight: '600' }}>
                        {inspection.deficiencies.length} {inspection.deficiencies.length === 1 ? 'deficiency' : 'deficiencies'}
                      </span>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
