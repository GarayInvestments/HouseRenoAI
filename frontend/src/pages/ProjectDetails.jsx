import { useEffect, useState } from 'react';
import { 
  ArrowLeft, 
  MapPin, 
  Users, 
  Calendar, 
  DollarSign, 
  FileText, 
  Image as ImageIcon,
  Building,
  Loader2,
  AlertCircle,
  Hash
} from 'lucide-react';
import api from '../lib/api';
import { useAppStore } from '../stores/appStore';
import LoadingScreen from '../components/LoadingScreen';
import ErrorState from '../components/ErrorState';

export default function ProjectDetails() {
  const { currentProjectId, navigateToProjects } = useAppStore();
  const [project, setProject] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [editedProject, setEditedProject] = useState(null);
  const [isSaving, setIsSaving] = useState(false);
  const [businesses, setBusinesses] = useState([]);
  const [qualifiers, setQualifiers] = useState([]);

  useEffect(() => {
    fetchProjectDetails();
    fetchComplianceData();
  }, [currentProjectId]);

  const fetchComplianceData = async () => {
    try {
      const [businessesData, qualifiersData] = await Promise.all([
        api.getLicensedBusinesses(),
        api.getQualifiers()
      ]);
      setBusinesses(businessesData || []);
      setQualifiers(qualifiersData || []);
    } catch (error) {
      console.error('Failed to load compliance data:', error);
    }
  };

  // Handle browser back button
  useEffect(() => {
    const handlePopState = () => {
      navigateToProjects();
    };

    // Push a state when component mounts
    window.history.pushState({ page: 'project-details' }, '');
    
    // Listen for back button
    window.addEventListener('popstate', handlePopState);

    return () => {
      window.removeEventListener('popstate', handlePopState);
    };
  }, [navigateToProjects]);

  const fetchProjectDetails = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getProjects();
      const foundProject = Array.isArray(data) 
        ? data.find(p => p['Project ID'] === currentProjectId)
        : null;
      
      if (foundProject) {
        setProject(foundProject);
      } else {
        setError('Project not found');
      }
    } catch {
      setError('Failed to load project details');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      setIsSaving(true);
      
      // Map frontend display field names to backend database column names
      const fieldMapping = {
        'Project Name': 'project_name',
        'Project Status': 'status',
        'Project Type': 'project_type',
        'Project Address': 'project_address',
        'Start Date': 'start_date',
        'City': 'city',
        'Licensed Business': 'licensed_business_id',
        'Qualifier': 'qualifier_id',
        'Engagement Model': 'engagement_model',
        'Notes': 'notes'
      };
      
      // Convert editedProject keys from display names to database column names
      // Only send fields that exist in the database
      const mappedData = {};
      Object.keys(editedProject).forEach(key => {
        const dbFieldName = fieldMapping[key];
        if (dbFieldName) {
          mappedData[dbFieldName] = editedProject[key];
        }
      });
      
      console.log('Sending mapped data to API:', mappedData);
      console.log('Original editedProject:', editedProject);
      
      await api.updateProject(currentProjectId, mappedData, false);
      setProject({ ...project, ...editedProject });
      setIsEditing(false);
      setEditedProject(null);
    } catch (error) {
      console.error('Failed to save project:', error);
      alert('Failed to save changes. Please try again.');
    } finally {
      setIsSaving(false);
    }
  };

  const handleCancel = () => {
    setIsEditing(false);
    setEditedProject(null);
  };

  const handleEditChange = (field, value) => {
    setEditedProject(prev => ({ ...prev, [field]: value }));
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Not set';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' });
  };

  const formatCurrency = (amount) => {
    if (!amount) return 'Not set';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'completed':
      case 'final inspection complete':
        return { bg: '#ECFDF5', text: '#059669', border: '#A7F3D0' };
      case 'permit approved':
      case 'active':
        return { bg: '#DBEAFE', text: '#2563EB', border: '#93C5FD' };
      case 'permit submitted':
      case 'planning':
        return { bg: '#FEF3C7', text: '#D97706', border: '#FCD34D' };
      case 'closed / archived':
        return { bg: '#F3F4F6', text: '#6B7280', border: '#D1D5DB' };
      case 'inquiry received':
        return { bg: '#FEF2F2', text: '#DC2626', border: '#FECACA' };
      default:
        return { bg: '#F3F4F6', text: '#6B7280', border: '#D1D5DB' };
    }
  };

  if (loading) {
    return <LoadingScreen />;
  }

  if (error || !project) {
    return (
      <div style={{ padding: '20px', backgroundColor: '#F8FAFC', minHeight: '100vh' }}>
        <ErrorState 
          message={error || 'Project not found'} 
          onRetry={fetchProjectDetails} 
          fullScreen 
        />
      </div>
    );
  }

  const statusStyle = getStatusColor(project.Status);

  return (
    <div style={{
      backgroundColor: '#F8FAFC',
      minHeight: '100vh',
      padding: '32px'
    }}>
      <div style={{
        maxWidth: '1200px',
        margin: '0 auto'
      }}>
        {/* Back Button & Edit Controls */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
          <button
            onClick={navigateToProjects}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '8px 16px',
              backgroundColor: '#FFFFFF',
              border: '1px solid #E2E8F0',
              borderRadius: '8px',
              fontSize: '14px',
              color: '#64748B',
              cursor: 'pointer',
              transition: 'all 0.2s ease'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = '#F8FAFC';
              e.currentTarget.style.color = '#2563EB';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = '#FFFFFF';
              e.currentTarget.style.color = '#64748B';
            }}
          >
            <ArrowLeft size={16} />
            Back to Projects
          </button>

          {!isEditing ? (
            <button
              onClick={() => {
                setIsEditing(true);
                setEditedProject(project);
              }}
              style={{
                padding: '8px 16px',
                backgroundColor: '#2563EB',
                color: '#FFFFFF',
                border: 'none',
                borderRadius: '8px',
                fontSize: '14px',
                fontWeight: '500',
                cursor: 'pointer',
                transition: 'all 0.2s ease'
              }}
              onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#1D4ED8'}
              onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#2563EB'}
            >
              Edit Project
            </button>
          ) : (
            <div style={{ display: 'flex', gap: '8px' }}>
              <button
                onClick={handleCancel}
                disabled={isSaving}
                style={{
                  padding: '8px 16px',
                  backgroundColor: '#FFFFFF',
                  color: '#64748B',
                  border: '1px solid #E2E8F0',
                  borderRadius: '8px',
                  fontSize: '14px',
                  fontWeight: '500',
                  cursor: isSaving ? 'not-allowed' : 'pointer',
                  opacity: isSaving ? 0.5 : 1
                }}
              >
                Cancel
              </button>
              <button
                onClick={handleSave}
                disabled={isSaving}
                style={{
                  padding: '8px 16px',
                  backgroundColor: '#059669',
                  color: '#FFFFFF',
                  border: 'none',
                  borderRadius: '8px',
                  fontSize: '14px',
                  fontWeight: '500',
                  cursor: isSaving ? 'not-allowed' : 'pointer',
                  opacity: isSaving ? 0.5 : 1
                }}
              >
                {isSaving ? 'Saving...' : 'Save Changes'}
              </button>
            </div>
          )}
        </div>

        {/* Header Card */}
        <div style={{
          backgroundColor: '#FFFFFF',
          borderRadius: '12px',
          padding: '32px',
          border: '1px solid #E2E8F0',
          marginBottom: '24px',
          boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.05)'
        }}>
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'flex-start',
            marginBottom: '16px'
          }}>
            <div style={{ flex: 1, marginRight: '16px' }}>
              {isEditing ? (
                <input
                  type="text"
                  value={editedProject?.['Project Name'] || ''}
                  onChange={(e) => handleEditChange('Project Name', e.target.value)}
                  style={{
                    fontSize: '32px',
                    fontWeight: '600',
                    color: '#1E293B',
                    marginBottom: '8px',
                    width: '100%',
                    padding: '8px',
                    border: '2px solid #2563EB',
                    borderRadius: '8px',
                    outline: 'none'
                  }}
                  placeholder="Project Name"
                />
              ) : (
                <h1 style={{
                  fontSize: '32px',
                  fontWeight: '600',
                  color: '#1E293B',
                  marginBottom: '8px'
                }}>
                  {project['Project Name'] || 'Unnamed Project'}
                </h1>
              )}
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                color: '#64748B',
                fontSize: '14px',
                marginBottom: '12px'
              }}>
                <Hash size={14} />
                Project ID: {project['Project ID']}
              </div>
            </div>
            {isEditing ? (
              <select
                value={editedProject?.Status || ''}
                onChange={(e) => handleEditChange('Status', e.target.value)}
                style={{
                  padding: '8px 16px',
                  borderRadius: '8px',
                  fontSize: '14px',
                  fontWeight: '500',
                  border: '2px solid #2563EB',
                  outline: 'none'
                }}
              >
                <option value="Inquiry Received">Inquiry Received</option>
                <option value="Planning">Planning</option>
                <option value="Permit Submitted">Permit Submitted</option>
                <option value="Permit Approved">Permit Approved</option>
                <option value="Active">Active</option>
                <option value="Final Inspection Complete">Final Inspection Complete</option>
                <option value="Completed">Completed</option>
                <option value="Closed / Archived">Closed / Archived</option>
              </select>
            ) : (
              <span style={{
                display: 'inline-flex',
                alignItems: 'center',
                padding: '8px 16px',
                borderRadius: '8px',
                backgroundColor: statusStyle.bg,
                color: statusStyle.text,
                fontSize: '14px',
                fontWeight: '500',
                border: `1px solid ${statusStyle.border}`,
                textTransform: 'capitalize'
              }}>
                {project.Status || 'N/A'}
              </span>
            )}
          </div>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
            gap: '16px',
            paddingTop: '16px',
            borderTop: '1px solid #F1F5F9'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <div style={{
                width: '40px',
                height: '40px',
                borderRadius: '8px',
                backgroundColor: '#DBEAFE',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <MapPin size={20} style={{ color: '#2563EB' }} />
              </div>
              <div style={{ flex: 1 }}>
                <p style={{ fontSize: '12px', color: '#64748B', marginBottom: '2px' }}>Location</p>
                {isEditing ? (
                  <input
                    type="text"
                    value={editedProject?.['Project Address'] || ''}
                    onChange={(e) => handleEditChange('Project Address', e.target.value)}
                    style={{
                      width: '100%',
                      fontSize: '14px',
                      fontWeight: '500',
                      padding: '6px 10px',
                      border: '1px solid #D1D5DB',
                      borderRadius: '6px',
                      outline: 'none'
                    }}
                    placeholder="Project Address"
                  />
                ) : (
                  <p style={{ fontSize: '14px', color: '#1E293B', fontWeight: '500' }}>
                    {project['Project Address'] || 'No address'}
                  </p>
                )}
              </div>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <div style={{
                width: '40px',
                height: '40px',
                borderRadius: '8px',
                backgroundColor: '#ECFDF5',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <Building size={20} style={{ color: '#059669' }} />
              </div>
              <div style={{ flex: 1 }}>
                <p style={{ fontSize: '12px', color: '#64748B', marginBottom: '2px' }}>Type</p>
                {isEditing ? (
                  <input
                    type="text"
                    value={editedProject?.['Project Type'] || ''}
                    onChange={(e) => handleEditChange('Project Type', e.target.value)}
                    style={{
                      width: '100%',
                      fontSize: '14px',
                      fontWeight: '500',
                      padding: '6px 10px',
                      border: '1px solid #D1D5DB',
                      borderRadius: '6px',
                      outline: 'none'
                    }}
                    placeholder="Project Type"
                  />
                ) : (
                  <p style={{ fontSize: '14px', color: '#1E293B', fontWeight: '500' }}>
                    {project['Project Type'] || 'N/A'}
                  </p>
                )}
              </div>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <div style={{
                width: '40px',
                height: '40px',
                borderRadius: '8px',
                backgroundColor: '#FEF3C7',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <Calendar size={20} style={{ color: '#D97706' }} />
              </div>
              <div style={{ flex: 1 }}>
                <p style={{ fontSize: '12px', color: '#64748B', marginBottom: '2px' }}>Start Date</p>
                {isEditing ? (
                  <input
                    type="date"
                    value={editedProject?.['Start Date'] || ''}
                    onChange={(e) => handleEditChange('Start Date', e.target.value)}
                    style={{
                      width: '100%',
                      fontSize: '14px',
                      fontWeight: '500',
                      padding: '6px 10px',
                      border: '1px solid #D1D5DB',
                      borderRadius: '6px',
                      outline: 'none'
                    }}
                  />
                ) : (
                  <p style={{ fontSize: '14px', color: '#1E293B', fontWeight: '500' }}>
                    {formatDate(project['Start Date'])}
                  </p>
                )}
              </div>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <div style={{
                width: '40px',
                height: '40px',
                borderRadius: '8px',
                backgroundColor: '#FEE2E2',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <Users size={20} style={{ color: '#DC2626' }} />
              </div>
              <div>
                <p style={{ fontSize: '12px', color: '#64748B', marginBottom: '2px' }}>Client</p>
                {project['Client ID'] ? (
                  <button
                    onClick={() => useAppStore.getState().navigateToClient(project['Client ID'])}
                    style={{
                      fontSize: '14px',
                      color: '#2563EB',
                      fontWeight: '500',
                      background: 'none',
                      border: 'none',
                      padding: 0,
                      cursor: 'pointer',
                      textDecoration: 'underline',
                      textAlign: 'left'
                    }}
                    onMouseEnter={(e) => e.currentTarget.style.color = '#1D4ED8'}
                    onMouseLeave={(e) => e.currentTarget.style.color = '#2563EB'}
                  >
                    {project['Owner Name (PM\'s Client)'] || project['Client ID']}
                  </button>
                ) : (
                  <p style={{ fontSize: '14px', color: '#1E293B', fontWeight: '500' }}>
                    {project['Owner Name (PM\'s Client)'] || 'Unknown'}
                  </p>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Details Grid */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))',
          gap: '24px'
        }}>
          {/* Financial Details */}
          <div style={{
            backgroundColor: '#FFFFFF',
            borderRadius: '12px',
            padding: '24px',
            border: '1px solid #E2E8F0',
            boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.05)'
          }}>
            <h2 style={{
              fontSize: '18px',
              fontWeight: '600',
              color: '#1E293B',
              marginBottom: '16px',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}>
              <DollarSign size={20} style={{ color: '#2563EB' }} />
              Financial Details
            </h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <div>
                <p style={{ fontSize: '12px', color: '#64748B', marginBottom: '4px' }}>Project Cost</p>
                {isEditing ? (
                  <input
                    type="number"
                    value={editedProject?.['Project Cost (Materials + Labor)'] || ''}
                    onChange={(e) => handleEditChange('Project Cost (Materials + Labor)', parseFloat(e.target.value) || 0)}
                    style={{
                      width: '100%',
                      fontSize: '20px',
                      fontWeight: '600',
                      padding: '8px',
                      border: '1px solid #D1D5DB',
                      borderRadius: '6px',
                      outline: 'none'
                    }}
                    placeholder="0"
                  />
                ) : (
                  <p style={{ fontSize: '20px', color: '#1E293B', fontWeight: '600' }}>
                    {formatCurrency(project['Project Cost (Materials + Labor)'])}
                  </p>
                )}
              </div>
              <div>
                <p style={{ fontSize: '12px', color: '#64748B', marginBottom: '4px' }}>HR PC Service Fee</p>
                {isEditing ? (
                  <input
                    type="number"
                    value={editedProject?.['HR PC Service Fee'] || ''}
                    onChange={(e) => handleEditChange('HR PC Service Fee', parseFloat(e.target.value) || 0)}
                    style={{
                      width: '100%',
                      fontSize: '18px',
                      fontWeight: '500',
                      padding: '8px',
                      border: '1px solid #D1D5DB',
                      borderRadius: '6px',
                      outline: 'none'
                    }}
                    placeholder="0"
                  />
                ) : (
                  <p style={{ fontSize: '18px', color: '#1E293B', fontWeight: '500' }}>
                    {formatCurrency(project['HR PC Service Fee'])}
                  </p>
                )}
              </div>
            </div>
          </div>

          {/* Location Details */}
          <div style={{
            backgroundColor: '#FFFFFF',
            borderRadius: '12px',
            padding: '24px',
            border: '1px solid #E2E8F0',
            boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.05)'
          }}>
            <h2 style={{
              fontSize: '18px',
              fontWeight: '600',
              color: '#1E293B',
              marginBottom: '16px',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}>
              <MapPin size={20} style={{ color: '#2563EB' }} />
              Location Details
            </h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <div>
                <p style={{ fontSize: '12px', color: '#64748B', marginBottom: '4px' }}>City</p>
                {isEditing ? (
                  <input
                    type="text"
                    value={editedProject?.City || ''}
                    onChange={(e) => handleEditChange('City', e.target.value)}
                    style={{
                      width: '100%',
                      fontSize: '14px',
                      fontWeight: '500',
                      padding: '6px 10px',
                      border: '1px solid #D1D5DB',
                      borderRadius: '6px',
                      outline: 'none'
                    }}
                  />
                ) : (
                  <p style={{ fontSize: '14px', color: '#1E293B', fontWeight: '500' }}>
                    {project.City || 'N/A'}
                  </p>
                )}
              </div>
              <div>
                <p style={{ fontSize: '12px', color: '#64748B', marginBottom: '4px' }}>County</p>
                {isEditing ? (
                  <input
                    type="text"
                    value={editedProject?.County || ''}
                    onChange={(e) => handleEditChange('County', e.target.value)}
                    style={{
                      width: '100%',
                      fontSize: '14px',
                      fontWeight: '500',
                      padding: '6px 10px',
                      border: '1px solid #D1D5DB',
                      borderRadius: '6px',
                      outline: 'none'
                    }}
                  />
                ) : (
                  <p style={{ fontSize: '14px', color: '#1E293B', fontWeight: '500' }}>
                    {project.County || 'N/A'}
                  </p>
                )}
              </div>
              <div>
                <p style={{ fontSize: '12px', color: '#64748B', marginBottom: '4px' }}>Jurisdiction ID</p>
                {isEditing ? (
                  <input
                    type="text"
                    value={editedProject?.Jurisdiction || ''}
                    onChange={(e) => handleEditChange('Jurisdiction', e.target.value)}
                    style={{
                      width: '100%',
                      fontSize: '14px',
                      fontWeight: '500',
                      padding: '6px 10px',
                      border: '1px solid #D1D5DB',
                      borderRadius: '6px',
                      outline: 'none'
                    }}
                  />
                ) : (
                  <p style={{ fontSize: '14px', color: '#1E293B', fontWeight: '500' }}>
                    {project.Jurisdiction || 'N/A'}
                  </p>
                )}
              </div>
              <div>
                <p style={{ fontSize: '12px', color: '#64748B', marginBottom: '4px' }}>Primary Inspector ID</p>
                {isEditing ? (
                  <input
                    type="text"
                    value={editedProject?.['Primary Inspector'] || ''}
                    onChange={(e) => handleEditChange('Primary Inspector', e.target.value)}
                    style={{
                      width: '100%',
                      fontSize: '14px',
                      fontWeight: '500',
                      padding: '6px 10px',
                      border: '1px solid #D1D5DB',
                      borderRadius: '6px',
                      outline: 'none'
                    }}
                  />
                ) : (
                  <p style={{ fontSize: '14px', color: '#1E293B', fontWeight: '500' }}>
                    {project['Primary Inspector'] || 'N/A'}
                  </p>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Scope of Work */}
        {project['Scope of Work'] && (
          <div style={{
            backgroundColor: '#FFFFFF',
            borderRadius: '12px',
            padding: '24px',
            border: '1px solid #E2E8F0',
            marginTop: '24px',
            boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.05)'
          }}>
            <h2 style={{
              fontSize: '18px',
              fontWeight: '600',
              color: '#1E293B',
              marginBottom: '16px',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}>
              <FileText size={20} style={{ color: '#2563EB' }} />
              Scope of Work
            </h2>
            <p style={{
              fontSize: '14px',
              color: '#475569',
              lineHeight: '1.6',
              whiteSpace: 'pre-wrap'
            }}>
              {project['Scope of Work']}
            </p>
          </div>
        )}

        {/* Compliance Section (Phase Q) */}
        <div style={{
          backgroundColor: '#FFFFFF',
          borderRadius: '12px',
          padding: '24px',
          border: '1px solid #E2E8F0',
          marginTop: '24px',
          boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.05)'
        }}>
          <h2 style={{
            fontSize: '18px',
            fontWeight: '600',
            color: '#1E293B',
            marginBottom: '16px',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            <FileText size={20} style={{ color: '#2563EB' }} />
            Compliance Information
          </h2>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
            gap: '16px'
          }}>
            <div>
              <label style={{
                display: 'block',
                fontSize: '14px',
                fontWeight: '500',
                color: '#374151',
                marginBottom: '4px'
              }}>Licensed Business</label>
              {isEditing ? (
                <select
                  value={editedProject?.licensed_business_id || ''}
                  onChange={(e) => handleEditChange('licensed_business_id', e.target.value)}
                  style={{
                    width: '100%',
                    padding: '8px 12px',
                    border: '1px solid #D1D5DB',
                    borderRadius: '8px',
                    fontSize: '14px',
                    outline: 'none'
                  }}
                >
                  <option value="">Select Business...</option>
                  {businesses.map((b) => (
                    <option key={b.id} value={b.id}>
                      {b.business_name} ({b.license_number})
                    </option>
                  ))}
                </select>
              ) : (
                <p style={{ color: '#111827', fontSize: '14px' }}>
                  {project.licensed_business_id || 'Not assigned'}
                </p>
              )}
            </div>

            <div>
              <label style={{
                display: 'block',
                fontSize: '14px',
                fontWeight: '500',
                color: '#374151',
                marginBottom: '4px'
              }}>Qualifier</label>
              {isEditing ? (
                <select
                  value={editedProject?.qualifier_id || ''}
                  onChange={(e) => handleEditChange('qualifier_id', e.target.value)}
                  style={{
                    width: '100%',
                    padding: '8px 12px',
                    border: '1px solid #D1D5DB',
                    borderRadius: '8px',
                    fontSize: '14px',
                    outline: 'none'
                  }}
                >
                  <option value="">Select Qualifier...</option>
                  {qualifiers.map((q) => (
                    <option key={q.id} value={q.id}>
                      {q.full_name} ({q.qualifier_id_number})
                    </option>
                  ))}
                </select>
              ) : (
                <p style={{ color: '#111827', fontSize: '14px' }}>
                  {project.qualifier_id || 'Not assigned'}
                </p>
              )}
            </div>

            <div>
              <label style={{
                display: 'block',
                fontSize: '14px',
                fontWeight: '500',
                color: '#374151',
                marginBottom: '4px'
              }}>Engagement Model</label>
              {isEditing ? (
                <select
                  value={editedProject?.engagement_model || ''}
                  onChange={(e) => handleEditChange('engagement_model', e.target.value)}
                  style={{
                    width: '100%',
                    padding: '8px 12px',
                    border: '1px solid #D1D5DB',
                    borderRadius: '8px',
                    fontSize: '14px',
                    outline: 'none'
                  }}
                >
                  <option value="">Select Model...</option>
                  <option value="DIRECT_GC">Direct GC</option>
                  <option value="THIRD_PARTY_QUALIFIER">Third-Party Qualifier</option>
                </select>
              ) : (
                <p style={{ color: '#111827', fontSize: '14px' }}>
                  {project.engagement_model || 'Not set'}
                </p>
              )}
            </div>
          </div>
        </div>

        {/* Notes */}
        {(project.Notes || isEditing) && (
          <div style={{
            backgroundColor: '#FFFFFF',
            borderRadius: '12px',
            padding: '24px',
            border: '1px solid #E2E8F0',
            marginTop: '24px',
            boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.05)'
          }}>
            <h2 style={{
              fontSize: '18px',
              fontWeight: '600',
              color: '#1E293B',
              marginBottom: '16px',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}>
              <FileText size={20} style={{ color: '#D97706' }} />
              Notes
            </h2>
            {isEditing ? (
              <textarea
                value={editedProject?.Notes || ''}
                onChange={(e) => handleEditChange('Notes', e.target.value)}
                style={{
                  width: '100%',
                  minHeight: '100px',
                  padding: '12px',
                  border: '1px solid #D1D5DB',
                  borderRadius: '8px',
                  fontSize: '14px',
                  outline: 'none',
                  fontFamily: 'inherit',
                  resize: 'vertical'
                }}
                placeholder="Add project notes..."
              />
            ) : (
              <p style={{
                fontSize: '14px',
                color: '#475569',
                lineHeight: '1.6',
                whiteSpace: 'pre-wrap'
              }}>
                {project.Notes}
              </p>
            )}
          </div>
        )}

        {/* Photo Album Link */}
        {project['Photo Album'] && (
          <div style={{
            backgroundColor: '#FFFFFF',
            borderRadius: '12px',
            padding: '24px',
            border: '1px solid #E2E8F0',
            marginTop: '24px',
            boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.05)'
          }}>
            <h2 style={{
              fontSize: '18px',
              fontWeight: '600',
              color: '#1E293B',
              marginBottom: '16px',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}>
              <ImageIcon size={20} style={{ color: '#2563EB' }} />
              Photo Album
            </h2>
            <a
              href={project['Photo Album']}
              target="_blank"
              rel="noopener noreferrer"
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '8px',
                padding: '10px 16px',
                backgroundColor: '#2563EB',
                color: '#FFFFFF',
                borderRadius: '8px',
                textDecoration: 'none',
                fontSize: '14px',
                fontWeight: '500',
                transition: 'all 0.2s ease'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = '#1D4ED8';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = '#2563EB';
              }}
            >
              <ImageIcon size={16} />
              View Photos
            </a>
          </div>
        )}
      </div>
    </div>
  );
}
