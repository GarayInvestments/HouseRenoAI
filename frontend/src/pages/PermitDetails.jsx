import { useEffect, useState } from 'react';
import { 
  ArrowLeft, 
  FileText, 
  Calendar, 
  CheckCircle,
  Clock,
  AlertCircle,
  ExternalLink,
  Download,
  Hash,
  FolderKanban,
  User,
  Loader2
} from 'lucide-react';
import api from '../lib/api';
import { useAppStore } from '../stores/appStore';

export default function PermitDetails() {
  const { currentPermitId, navigateToPermits } = useAppStore();
  const [permit, setPermit] = useState(null);
  const [project, setProject] = useState(null);
  const [client, setClient] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [editedPermit, setEditedPermit] = useState(null);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    const fetchPermitDetails = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // Fetch single permit by ID (not all permits)
        const permitData = await api.getPermit(currentPermitId);
        
        if (permitData) {
          setPermit(permitData);
          
          // Get project ID from permit (handle both old and new field names)
          const projectId = permitData['Project ID'] || permitData.project_id;
          
          if (projectId) {
            // Fetch related project and all clients
            const [projectData, clientsData] = await Promise.all([
              api.getProject(projectId),
              api.getClients()
            ]);
            
            setProject(projectData);
            
            // Find related client through project
            const clientId = projectData?.['Client ID'] || projectData?.client_id;
            if (clientId && Array.isArray(clientsData)) {
              const relatedClient = clientsData.find(c => 
                c['Client ID'] === clientId || 
                c['ID'] === clientId ||
                c.client_id === clientId ||
                c.id === clientId
              );
              setClient(relatedClient);
            }
          }
        } else {
          setError('Permit not found');
        }
      } catch (err) {
        console.error('Failed to load permit details:', err);
        setError('Failed to load permit details');
      } finally {
        setLoading(false);
      }
    };
    
    if (currentPermitId) {
      fetchPermitDetails();
    } else {
      setError('No permit ID provided');
      setLoading(false);
    }
  }, [currentPermitId]);

  // Handle browser back button
  useEffect(() => {
    const handlePopState = () => {
      navigateToPermits();
    };

    // Push a state when component mounts
    window.history.pushState({ page: 'permit-details' }, '');
    
    // Listen for back button
    window.addEventListener('popstate', handlePopState);

    return () => {
      window.removeEventListener('popstate', handlePopState);
    };
  }, [navigateToPermits]);

  const formatDate = (dateString) => {
    if (!dateString) return 'Not set';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' });
  };

  const handleSave = async () => {
    try {
      setIsSaving(true);
      await api.updatePermit(currentPermitId, editedPermit);
      setPermit({ ...permit, ...editedPermit });
      setIsEditing(false);
      setEditedPermit(null);
    } catch (error) {
      console.error('Failed to save permit:', error);
      alert('Failed to save changes. Please try again.');
    } finally {
      setIsSaving(false);
    }
  };

  const handleCancel = () => {
    setIsEditing(false);
    setEditedPermit(null);
  };

  const handleEditChange = (field, value) => {
    setEditedPermit(prev => ({ ...prev, [field]: value }));
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
    if (lowerStatus?.includes('approved')) return <CheckCircle size={20} />;
    if (lowerStatus?.includes('pending') || lowerStatus?.includes('submitted')) return <Clock size={20} />;
    if (lowerStatus?.includes('review')) return <AlertCircle size={20} />;
    return null;
  };

  if (loading) {
    return (
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100vh',
        gap: '16px',
        backgroundColor: '#F8FAFC'
      }}>
        <Loader2 className="animate-spin" size={40} style={{ color: '#2563EB' }} />
        <p style={{ color: '#64748B', fontSize: '14px' }}>Loading permit details...</p>
      </div>
    );
  }

  if (error || !permit) {
    return (
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100vh',
        gap: '16px',
        backgroundColor: '#F8FAFC'
      }}>
        <AlertCircle size={40} style={{ color: '#DC2626' }} />
        <p style={{ color: '#DC2626', fontSize: '14px' }}>{error || 'Permit not found'}</p>
        <button
          onClick={navigateToPermits}
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
          Back to Permits
        </button>
      </div>
    );
  }

  const permitStatus = permit?.['Permit Status'] || permit?.status;
  const permitNumber = permit?.['Permit Number'] || permit?.permit_number || permit?.business_id;
  const permitId = permit?.['Permit ID'] || permit?.permit_id;
  const dateSubmitted = permit?.['Date Submitted'] || permit?.application_date;
  const dateApproved = permit?.['Date Approved'] || permit?.approval_date;
  const statusStyle = getStatusColor(permitStatus);

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
            onClick={navigateToPermits}
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
            Back to Permits
          </button>

          {!isEditing ? (
            <button
              onClick={() => {
                setIsEditing(true);
                setEditedPermit(permit);
              }}
              style={{
                padding: '8px 16px',
                backgroundColor: '#2563EB',
                color: '#FFFFFF',
                border: 'none',
                borderRadius: '8px',
                fontSize: '14px',
                fontWeight: '500',
                cursor: 'pointer'
              }}
            >
              Edit Permit
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
            <div>
              {isEditing ? (
                <input
                  type="text"
                  value={editedPermit?.['Permit Number'] || editedPermit?.permit_number || ''}
                  onChange={(e) => {
                    handleEditChange('Permit Number', e.target.value);
                    handleEditChange('permit_number', e.target.value);
                  }}
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
                  placeholder="Permit Number"
                />
              ) : (
                <h1 style={{
                  fontSize: '32px',
                  fontWeight: '600',
                  color: '#1E293B',
                  marginBottom: '8px'
                }}>
                  Permit {permitNumber || 'Unknown'}
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
                Permit ID: {permitId || business_id || 'N/A'}
              </div>
            </div>
            {isEditing ? (
              <select
                value={editedPermit?.['Permit Status'] || editedPermit?.status || ''}
                onChange={(e) => {
                  handleEditChange('Permit Status', e.target.value);
                  handleEditChange('status', e.target.value);
                }}
                style={{
                  padding: '8px 16px',
                  borderRadius: '8px',
                  fontSize: '14px',
                  fontWeight: '500',
                  border: '2px solid #2563EB',
                  outline: 'none'
                }}
              >
                <option value="Pending">Pending</option>
                <option value="Submitted">Submitted</option>
                <option value="In Review">In Review</option>
                <option value="Approved">Approved</option>
                <option value="Rejected">Rejected</option>
                <option value="Expired">Expired</option>
              </select>
            ) : (
              <span style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '8px',
                padding: '8px 16px',
                borderRadius: '8px',
                backgroundColor: statusStyle.bg,
                color: statusStyle.text,
                fontSize: '14px',
                fontWeight: '500',
                border: `1px solid ${statusStyle.border}`,
                textTransform: 'capitalize'
              }}>
                {getStatusIcon(permitStatus)}
                {permitStatus || 'N/A'}
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
                <Calendar size={20} style={{ color: '#2563EB' }} />
              </div>
              <div style={{ flex: 1 }}>
                <p style={{ fontSize: '12px', color: '#64748B', marginBottom: '2px' }}>Date Submitted</p>
                {isEditing ? (
                  <input
                    type="date"
                    value={editedPermit?.['Date Submitted'] || editedPermit?.application_date || ''}
                    onChange={(e) => handleEditChange('Date Submitted', e.target.value)}
                    style={{
                      width: '100%',
                      padding: '6px 10px',
                      border: '1px solid #D1D5DB',
                      borderRadius: '6px',
                      fontSize: '14px',
                      outline: 'none'
                    }}
                  />
                ) : (
                  <p style={{ fontSize: '14px', color: '#1E293B', fontWeight: '500' }}>
                    {formatDate(dateSubmitted)}
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
                <CheckCircle size={20} style={{ color: '#059669' }} />
              </div>
              <div style={{ flex: 1 }}>
                <p style={{ fontSize: '12px', color: '#64748B', marginBottom: '2px' }}>Date Approved</p>
                {isEditing ? (
                  <input
                    type="date"
                    value={editedPermit?.['Date Approved'] || editedPermit?.approval_date || ''}
                    onChange={(e) => handleEditChange('Date Approved', e.target.value)}
                    style={{
                      width: '100%',
                      padding: '6px 10px',
                      border: '1px solid #D1D5DB',
                      borderRadius: '6px',
                      fontSize: '14px',
                      outline: 'none'
                    }}
                  />
                ) : (
                  <p style={{ fontSize: '14px', color: '#1E293B', fontWeight: '500' }}>
                    {formatDate(dateApproved)}
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
                <FolderKanban size={20} style={{ color: '#D97706' }} />
              </div>
              <div>
                <p style={{ fontSize: '12px', color: '#64748B', marginBottom: '2px' }}>Project</p>
                {project ? (
                  <button
                    onClick={() => useAppStore.getState().navigateToProject(permit['Project ID'])}
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
                    {project['Project Name'] || permit['Project ID']}
                  </button>
                ) : (
                  <p style={{ fontSize: '14px', color: '#1E293B', fontWeight: '500' }}>
                    {permit['Project ID'] || 'N/A'}
                  </p>
                )}
              </div>
            </div>

            {client && (
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
                  <User size={20} style={{ color: '#DC2626' }} />
                </div>
                <div>
                  <p style={{ fontSize: '12px', color: '#64748B', marginBottom: '2px' }}>Client</p>
                  <button
                    onClick={() => useAppStore.getState().navigateToClient(client['Client ID'] || client['ID'])}
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
                    {client['Full Name'] || client['Client Name'] || client['Client ID'] || client['ID']}
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Details Grid */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))',
          gap: '24px'
        }}>
          {/* City Portal Link */}
          {permit['City Portal Link'] && (
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
                <ExternalLink size={20} style={{ color: '#2563EB' }} />
                City Portal
              </h2>
              <a
                href={permit['City Portal Link']}
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
                <ExternalLink size={16} />
                Open City Portal
              </a>
            </div>
          )}

          {/* File Upload */}
          {permit['File Upload'] && (
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
                <FileText size={20} style={{ color: '#2563EB' }} />
                Documents
              </h2>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                padding: '12px',
                backgroundColor: '#F8FAFC',
                borderRadius: '8px',
                border: '1px solid #E2E8F0'
              }}>
                <FileText size={20} style={{ color: '#64748B' }} />
                <div style={{ flex: 1 }}>
                  <p style={{
                    fontSize: '14px',
                    fontWeight: '500',
                    color: '#1E293B',
                    marginBottom: '2px'
                  }}>
                    {permit['File Upload'].split('/').pop()}
                  </p>
                  <p style={{
                    fontSize: '12px',
                    color: '#64748B'
                  }}>
                    Permit Document
                  </p>
                </div>
                <button
                  style={{
                    padding: '6px 12px',
                    backgroundColor: '#FFFFFF',
                    border: '1px solid #E2E8F0',
                    borderRadius: '6px',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px',
                    fontSize: '12px',
                    fontWeight: '500',
                    color: '#64748B',
                    transition: 'all 0.2s ease'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.backgroundColor = '#F8FAFC';
                    e.currentTarget.style.borderColor = '#2563EB';
                    e.currentTarget.style.color = '#2563EB';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.backgroundColor = '#FFFFFF';
                    e.currentTarget.style.borderColor = '#E2E8F0';
                    e.currentTarget.style.color = '#64748B';
                  }}
                >
                  <Download size={14} />
                  Download
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
