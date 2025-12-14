import { useEffect, useState } from 'react';
import { 
  ArrowLeft, 
  ClipboardCheck, 
  Calendar, 
  CheckCircle,
  Clock,
  AlertCircle,
  User,
  Loader2,
  Building2,
  FileText,
  Camera,
  Edit2,
  Trash2,
  Plus,
  Save,
  X,
  XCircle
} from 'lucide-react';
import api from '../lib/api';
import { useAppStore } from '../stores/appStore';
import useInspectionsStore from '../stores/inspectionsStore';

export default function InspectionDetails() {
  const { currentInspectionId, navigateToInspections } = useAppStore();
  const { updateInspection, deleteInspection, addPhoto, addDeficiency } = useInspectionsStore();
  
  const [inspection, setInspection] = useState(null);
  const [project, setProject] = useState(null);
  const [permit, setPermit] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Edit mode states
  const [isEditing, setIsEditing] = useState(false);
  const [editForm, setEditForm] = useState({});
  const [saveLoading, setSaveLoading] = useState(false);
  
  // Add photo modal
  const [showPhotoModal, setShowPhotoModal] = useState(false);
  const [photoForm, setPhotoForm] = useState({ url: '', description: '' });
  
  // Add deficiency modal
  const [showDeficiencyModal, setShowDeficiencyModal] = useState(false);
  const [deficiencyForm, setDeficiencyForm] = useState({ 
    description: '', 
    severity: 'medium',
    status: 'open'
  });

  useEffect(() => {
    const fetchInspectionDetails = async () => {
      try {
        setLoading(true);
        setError(null);
        
        if (!currentInspectionId) {
          setError('No inspection ID provided');
          return;
        }
        
        // Fetch single inspection by ID
        const inspectionData = await api.getInspection(currentInspectionId);
        
        if (inspectionData) {
          setInspection(inspectionData);
          setEditForm(inspectionData); // Initialize edit form
          
          // Get related data
          const projectId = inspectionData.project_id || inspectionData['Project ID'];
          const permitId = inspectionData.permit_id || inspectionData['Permit ID'];
          
          if (projectId) {
            const projectData = await api.getProject(projectId);
            setProject(projectData);
          }
          
          if (permitId) {
            const permitData = await api.getPermit(permitId);
            setPermit(permitData);
          }
        } else {
          setError('Inspection not found');
        }
      } catch (err) {
        console.error('Failed to load inspection details:', err);
        setError('Failed to load inspection details');
      } finally {
        setLoading(false);
      }
    };
    
    if (currentInspectionId) {
      fetchInspectionDetails();
    } else {
      setError('No inspection ID provided');
      setLoading(false);
    }
  }, [currentInspectionId]);

  // Handle browser back button
  useEffect(() => {
    const handlePopState = () => {
      navigateToInspections();
    };
    window.history.pushState({ page: 'inspection-details' }, '');
    window.addEventListener('popstate', handlePopState);
    return () => {
      window.removeEventListener('popstate', handlePopState);
    };
  }, [navigateToInspections]);

  const formatDate = (dateString) => {
    if (!dateString) return 'Not set';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric', 
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const handleEdit = () => {
    setIsEditing(true);
    setEditForm(inspection);
  };

  const handleCancelEdit = () => {
    setIsEditing(false);
    setEditForm(inspection);
  };

  const handleSaveEdit = async () => {
    try {
      setSaveLoading(true);
      const updated = await updateInspection(currentInspectionId, editForm);
      setInspection(updated);
      setIsEditing(false);
    } catch (err) {
      alert('Failed to update inspection: ' + err.message);
    } finally {
      setSaveLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete this inspection? This action cannot be undone.')) {
      return;
    }
    
    try {
      await deleteInspection(currentInspectionId);
      alert('Inspection deleted successfully');
      navigateToInspections();
    } catch (err) {
      alert('Failed to delete inspection: ' + err.message);
    }
  };

  const handleAddPhoto = async () => {
    if (!photoForm.url.trim()) {
      alert('Please provide a photo URL');
      return;
    }
    
    try {
      const updated = await addPhoto(currentInspectionId, photoForm);
      setInspection(updated);
      setShowPhotoModal(false);
      setPhotoForm({ url: '', description: '' });
    } catch (err) {
      alert('Failed to add photo: ' + err.message);
    }
  };

  const handleAddDeficiency = async () => {
    if (!deficiencyForm.description.trim()) {
      alert('Please provide a deficiency description');
      return;
    }
    
    try {
      const updated = await addDeficiency(currentInspectionId, deficiencyForm);
      setInspection(updated);
      setShowDeficiencyModal(false);
      setDeficiencyForm({ description: '', severity: 'medium', status: 'open' });
    } catch (err) {
      alert('Failed to add deficiency: ' + err.message);
    }
  };

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
    return { bg: '#F3F4F6', text: '#6B7280', border: '#D1D5DB' };
  };

  const getSeverityColor = (severity) => {
    const lower = severity?.toLowerCase();
    if (lower === 'critical') return { bg: '#FEE2E2', text: '#DC2626' };
    if (lower === 'high') return { bg: '#FED7AA', text: '#EA580C' };
    if (lower === 'medium') return { bg: '#FEF3C7', text: '#D97706' };
    return { bg: '#DBEAFE', text: '#2563EB' };
  };

  if (loading) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '100vh',
        backgroundColor: '#F8FAFC'
      }}>
        <Loader2 size={48} className="animate-spin" color="#6366F1" />
      </div>
    );
  }

  if (error) {
    return (
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '100vh',
        backgroundColor: '#F8FAFC',
        padding: '24px'
      }}>
        <AlertCircle size={48} color="#DC2626" style={{ marginBottom: '16px' }} />
        <h2 style={{ fontSize: '24px', fontWeight: '700', color: '#1E293B', margin: '0 0 8px 0' }}>
          {error}
        </h2>
        <button
          onClick={navigateToInspections}
          style={{
            marginTop: '16px',
            padding: '12px 24px',
            backgroundColor: '#6366F1',
            color: '#FFFFFF',
            border: 'none',
            borderRadius: '8px',
            fontSize: '15px',
            fontWeight: '600',
            cursor: 'pointer'
          }}
        >
          Back to Inspections
        </button>
      </div>
    );
  }

  const inspectionStatus = inspection?.status || inspection?.['Inspection Status'];
  const inspectionType = inspection?.inspection_type || inspection?.['Inspection Type'];
  const businessId = inspection?.business_id || inspection?.['Inspection ID'];
  const scheduledDate = inspection?.scheduled_date || inspection?.['Scheduled Date'];
  const completedDate = inspection?.completed_date || inspection?.['Completed Date'];
  const inspector = inspection?.inspector || 'Not assigned';
  const result = inspection?.result || inspection?.['Result'];
  const notes = inspection?.notes || '';
  const statusColor = getStatusColor(inspectionStatus);
  
  const photos = inspection?.photos || [];
  const deficiencies = inspection?.deficiencies || [];

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
        {/* Back Button */}
        <button
          onClick={navigateToInspections}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '8px 16px',
            backgroundColor: '#FFFFFF',
            border: '1px solid #E2E8F0',
            borderRadius: '8px',
            fontSize: '15px',
            fontWeight: '600',
            color: '#64748B',
            cursor: 'pointer',
            marginBottom: '24px',
            transition: 'all 0.2s'
          }}
        >
          <ArrowLeft size={20} />
          Back to Inspections
        </button>

        {/* Header */}
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'flex-start',
          marginBottom: '32px',
          flexWrap: 'wrap',
          gap: '16px'
        }}>
          <div style={{ flex: 1 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
              <ClipboardCheck size={32} color="#6366F1" />
              <h1 style={{
                fontSize: '32px',
                fontWeight: '700',
                color: '#1E293B',
                margin: 0
              }}>
                {inspectionType || 'Inspection'}
              </h1>
            </div>
            <div style={{
              fontSize: '15px',
              color: '#64748B',
              fontFamily: 'monospace'
            }}>
              {businessId}
            </div>
          </div>

          {/* Action Buttons */}
          <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
            {!isEditing ? (
              <>
                <button
                  onClick={handleEdit}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    padding: '10px 20px',
                    backgroundColor: '#6366F1',
                    color: '#FFFFFF',
                    border: 'none',
                    borderRadius: '8px',
                    fontSize: '14px',
                    fontWeight: '600',
                    cursor: 'pointer'
                  }}
                >
                  <Edit2 size={18} />
                  Edit
                </button>
                <button
                  onClick={handleDelete}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    padding: '10px 20px',
                    backgroundColor: '#FEE2E2',
                    color: '#DC2626',
                    border: '1px solid #FECACA',
                    borderRadius: '8px',
                    fontSize: '14px',
                    fontWeight: '600',
                    cursor: 'pointer'
                  }}
                >
                  <Trash2 size={18} />
                  Delete
                </button>
              </>
            ) : (
              <>
                <button
                  onClick={handleSaveEdit}
                  disabled={saveLoading}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    padding: '10px 20px',
                    backgroundColor: '#059669',
                    color: '#FFFFFF',
                    border: 'none',
                    borderRadius: '8px',
                    fontSize: '14px',
                    fontWeight: '600',
                    cursor: saveLoading ? 'not-allowed' : 'pointer',
                    opacity: saveLoading ? 0.6 : 1
                  }}
                >
                  {saveLoading ? <Loader2 size={18} className="animate-spin" /> : <Save size={18} />}
                  Save
                </button>
                <button
                  onClick={handleCancelEdit}
                  disabled={saveLoading}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    padding: '10px 20px',
                    backgroundColor: '#FFFFFF',
                    color: '#64748B',
                    border: '1px solid #E2E8F0',
                    borderRadius: '8px',
                    fontSize: '14px',
                    fontWeight: '600',
                    cursor: saveLoading ? 'not-allowed' : 'pointer'
                  }}
                >
                  <X size={18} />
                  Cancel
                </button>
              </>
            )}
          </div>
        </div>

        {/* Main Content Grid */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: '1fr',
          gap: '24px'
        }}>
          {/* Details Card */}
          <div style={{
            backgroundColor: '#FFFFFF',
            borderRadius: '12px',
            padding: '24px',
            border: '1px solid #E2E8F0'
          }}>
            <h2 style={{
              fontSize: '20px',
              fontWeight: '700',
              color: '#1E293B',
              marginBottom: '20px'
            }}>
              Inspection Details
            </h2>

            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
              gap: '20px'
            }}>
              {/* Status */}
              <div>
                <div style={{ fontSize: '13px', fontWeight: '600', color: '#64748B', marginBottom: '8px' }}>
                  Status
                </div>
                {isEditing ? (
                  <select
                    value={editForm.status || ''}
                    onChange={(e) => setEditForm({...editForm, status: e.target.value})}
                    style={{
                      width: '100%',
                      padding: '10px',
                      border: '1px solid #E2E8F0',
                      borderRadius: '6px',
                      fontSize: '14px'
                    }}
                  >
                    <option value="scheduled">Scheduled</option>
                    <option value="in-progress">In Progress</option>
                    <option value="completed">Completed</option>
                    <option value="failed">Failed</option>
                    <option value="cancelled">Cancelled</option>
                  </select>
                ) : (
                  <div style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '6px',
                    padding: '8px 14px',
                    backgroundColor: statusColor.bg,
                    color: statusColor.text,
                    border: `1px solid ${statusColor.border}`,
                    borderRadius: '6px',
                    fontSize: '14px',
                    fontWeight: '600',
                    textTransform: 'capitalize'
                  }}>
                    {inspectionStatus?.replace('-', ' ')}
                  </div>
                )}
              </div>

              {/* Inspection Type */}
              <div>
                <div style={{ fontSize: '13px', fontWeight: '600', color: '#64748B', marginBottom: '8px' }}>
                  Type
                </div>
                {isEditing ? (
                  <input
                    type="text"
                    value={editForm.inspection_type || ''}
                    onChange={(e) => setEditForm({...editForm, inspection_type: e.target.value})}
                    style={{
                      width: '100%',
                      padding: '10px',
                      border: '1px solid #E2E8F0',
                      borderRadius: '6px',
                      fontSize: '14px'
                    }}
                  />
                ) : (
                  <div style={{ fontSize: '15px', color: '#1E293B' }}>{inspectionType}</div>
                )}
              </div>

              {/* Inspector */}
              <div>
                <div style={{ fontSize: '13px', fontWeight: '600', color: '#64748B', marginBottom: '8px' }}>
                  <User size={14} style={{ display: 'inline', marginRight: '4px' }} />
                  Inspector
                </div>
                {isEditing ? (
                  <input
                    type="text"
                    value={editForm.inspector || ''}
                    onChange={(e) => setEditForm({...editForm, inspector: e.target.value})}
                    style={{
                      width: '100%',
                      padding: '10px',
                      border: '1px solid #E2E8F0',
                      borderRadius: '6px',
                      fontSize: '14px'
                    }}
                  />
                ) : (
                  <div style={{ fontSize: '15px', color: '#1E293B' }}>{inspector}</div>
                )}
              </div>

              {/* Result */}
              <div>
                <div style={{ fontSize: '13px', fontWeight: '600', color: '#64748B', marginBottom: '8px' }}>
                  Result
                </div>
                {isEditing ? (
                  <select
                    value={editForm.result || ''}
                    onChange={(e) => setEditForm({...editForm, result: e.target.value})}
                    style={{
                      width: '100%',
                      padding: '10px',
                      border: '1px solid #E2E8F0',
                      borderRadius: '6px',
                      fontSize: '14px'
                    }}
                  >
                    <option value="">Not set</option>
                    <option value="pass">Pass</option>
                    <option value="fail">Fail</option>
                    <option value="partial">Partial</option>
                    <option value="no-access">No Access</option>
                  </select>
                ) : (
                  <div style={{ fontSize: '15px', color: '#1E293B', textTransform: 'capitalize' }}>
                    {result || 'Not set'}
                  </div>
                )}
              </div>

              {/* Scheduled Date */}
              <div>
                <div style={{ fontSize: '13px', fontWeight: '600', color: '#64748B', marginBottom: '8px' }}>
                  <Calendar size={14} style={{ display: 'inline', marginRight: '4px' }} />
                  Scheduled Date
                </div>
                {isEditing ? (
                  <input
                    type="datetime-local"
                    value={editForm.scheduled_date ? new Date(editForm.scheduled_date).toISOString().slice(0, 16) : ''}
                    onChange={(e) => setEditForm({...editForm, scheduled_date: e.target.value})}
                    style={{
                      width: '100%',
                      padding: '10px',
                      border: '1px solid #E2E8F0',
                      borderRadius: '6px',
                      fontSize: '14px'
                    }}
                  />
                ) : (
                  <div style={{ fontSize: '15px', color: '#1E293B' }}>{formatDate(scheduledDate)}</div>
                )}
              </div>

              {/* Completed Date */}
              <div>
                <div style={{ fontSize: '13px', fontWeight: '600', color: '#64748B', marginBottom: '8px' }}>
                  <CheckCircle size={14} style={{ display: 'inline', marginRight: '4px' }} />
                  Completed Date
                </div>
                {isEditing ? (
                  <input
                    type="datetime-local"
                    value={editForm.completed_date ? new Date(editForm.completed_date).toISOString().slice(0, 16) : ''}
                    onChange={(e) => setEditForm({...editForm, completed_date: e.target.value})}
                    style={{
                      width: '100%',
                      padding: '10px',
                      border: '1px solid #E2E8F0',
                      borderRadius: '6px',
                      fontSize: '14px'
                    }}
                  />
                ) : (
                  <div style={{ fontSize: '15px', color: '#1E293B' }}>{formatDate(completedDate)}</div>
                )}
              </div>

              {/* Project */}
              <div>
                <div style={{ fontSize: '13px', fontWeight: '600', color: '#64748B', marginBottom: '8px' }}>
                  <Building2 size={14} style={{ display: 'inline', marginRight: '4px' }} />
                  Project
                </div>
                <div style={{ fontSize: '15px', color: '#1E293B' }}>
                  {project?.project_name || project?.['Project Name'] || 'Unknown'}
                </div>
              </div>

              {/* Permit */}
              <div>
                <div style={{ fontSize: '13px', fontWeight: '600', color: '#64748B', marginBottom: '8px' }}>
                  <FileText size={14} style={{ display: 'inline', marginRight: '4px' }} />
                  Permit
                </div>
                <div style={{ fontSize: '15px', color: '#1E293B' }}>
                  {permit?.permit_number || permit?.business_id || permit?.['Permit Number'] || 'Unknown'}
                </div>
              </div>
            </div>

            {/* Notes */}
            <div style={{ marginTop: '24px', paddingTop: '24px', borderTop: '1px solid #F1F5F9' }}>
              <div style={{ fontSize: '13px', fontWeight: '600', color: '#64748B', marginBottom: '8px' }}>
                Notes
              </div>
              {isEditing ? (
                <textarea
                  value={editForm.notes || ''}
                  onChange={(e) => setEditForm({...editForm, notes: e.target.value})}
                  rows={4}
                  style={{
                    width: '100%',
                    padding: '10px',
                    border: '1px solid #E2E8F0',
                    borderRadius: '6px',
                    fontSize: '14px',
                    fontFamily: 'inherit',
                    resize: 'vertical'
                  }}
                />
              ) : (
                <div style={{ fontSize: '15px', color: '#1E293B', whiteSpace: 'pre-wrap' }}>
                  {notes || 'No notes'}
                </div>
              )}
            </div>
          </div>

          {/* Photos Section */}
          <div style={{
            backgroundColor: '#FFFFFF',
            borderRadius: '12px',
            padding: '24px',
            border: '1px solid #E2E8F0'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
              <h2 style={{
                fontSize: '20px',
                fontWeight: '700',
                color: '#1E293B',
                margin: 0
              }}>
                Photos ({photos.length})
              </h2>
              <button
                onClick={() => setShowPhotoModal(true)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  padding: '8px 16px',
                  backgroundColor: '#6366F1',
                  color: '#FFFFFF',
                  border: 'none',
                  borderRadius: '6px',
                  fontSize: '13px',
                  fontWeight: '600',
                  cursor: 'pointer'
                }}
              >
                <Plus size={16} />
                Add Photo
              </button>
            </div>

            {photos.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '40px', color: '#94A3B8' }}>
                <Camera size={48} style={{ margin: '0 auto 12px', opacity: 0.5 }} />
                <div>No photos yet</div>
              </div>
            ) : (
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '16px' }}>
                {photos.map((photo, idx) => (
                  <div key={idx} style={{
                    border: '1px solid #E2E8F0',
                    borderRadius: '8px',
                    overflow: 'hidden'
                  }}>
                    <img 
                      src={photo.url} 
                      alt={photo.description || 'Inspection photo'}
                      style={{ width: '100%', height: '150px', objectFit: 'cover' }}
                    />
                    {photo.description && (
                      <div style={{ padding: '8px', fontSize: '13px', color: '#64748B' }}>
                        {photo.description}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Deficiencies Section */}
          <div style={{
            backgroundColor: '#FFFFFF',
            borderRadius: '12px',
            padding: '24px',
            border: '1px solid #E2E8F0'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
              <h2 style={{
                fontSize: '20px',
                fontWeight: '700',
                color: '#1E293B',
                margin: 0
              }}>
                Deficiencies ({deficiencies.length})
              </h2>
              <button
                onClick={() => setShowDeficiencyModal(true)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  padding: '8px 16px',
                  backgroundColor: '#6366F1',
                  color: '#FFFFFF',
                  border: 'none',
                  borderRadius: '6px',
                  fontSize: '13px',
                  fontWeight: '600',
                  cursor: 'pointer'
                }}
              >
                <Plus size={16} />
                Add Deficiency
              </button>
            </div>

            {deficiencies.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '40px', color: '#94A3B8' }}>
                <CheckCircle size={48} style={{ margin: '0 auto 12px', opacity: 0.5 }} />
                <div>No deficiencies found</div>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {deficiencies.map((deficiency, idx) => {
                  const severityColor = getSeverityColor(deficiency.severity);
                  return (
                    <div key={idx} style={{
                      padding: '16px',
                      border: '1px solid #E2E8F0',
                      borderRadius: '8px',
                      backgroundColor: '#F8FAFC'
                    }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
                        <div style={{ flex: 1 }}>
                          <div style={{ fontSize: '15px', fontWeight: '600', color: '#1E293B', marginBottom: '4px' }}>
                            {deficiency.description}
                          </div>
                        </div>
                        <div style={{ display: 'flex', gap: '8px' }}>
                          <span style={{
                            padding: '4px 10px',
                            fontSize: '11px',
                            fontWeight: '600',
                            backgroundColor: severityColor.bg,
                            color: severityColor.text,
                            borderRadius: '4px',
                            textTransform: 'capitalize'
                          }}>
                            {deficiency.severity}
                          </span>
                          <span style={{
                            padding: '4px 10px',
                            fontSize: '11px',
                            fontWeight: '600',
                            backgroundColor: deficiency.status === 'resolved' ? '#ECFDF5' : '#FEF3C7',
                            color: deficiency.status === 'resolved' ? '#059669' : '#D97706',
                            borderRadius: '4px',
                            textTransform: 'capitalize'
                          }}>
                            {deficiency.status}
                          </span>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>

        {/* Add Photo Modal */}
        {showPhotoModal && (
          <div style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0,0,0,0.5)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000
          }}>
            <div style={{
              backgroundColor: '#FFFFFF',
              borderRadius: '12px',
              padding: '24px',
              maxWidth: '500px',
              width: '90%'
            }}>
              <h3 style={{ fontSize: '20px', fontWeight: '700', marginBottom: '20px' }}>Add Photo</h3>
              
              <div style={{ marginBottom: '16px' }}>
                <label style={{ display: 'block', fontSize: '13px', fontWeight: '600', color: '#64748B', marginBottom: '8px' }}>
                  Photo URL
                </label>
                <input
                  type="text"
                  value={photoForm.url}
                  onChange={(e) => setPhotoForm({...photoForm, url: e.target.value})}
                  placeholder="https://example.com/photo.jpg"
                  style={{
                    width: '100%',
                    padding: '10px',
                    border: '1px solid #E2E8F0',
                    borderRadius: '6px',
                    fontSize: '14px'
                  }}
                />
              </div>

              <div style={{ marginBottom: '20px' }}>
                <label style={{ display: 'block', fontSize: '13px', fontWeight: '600', color: '#64748B', marginBottom: '8px' }}>
                  Description (Optional)
                </label>
                <input
                  type="text"
                  value={photoForm.description}
                  onChange={(e) => setPhotoForm({...photoForm, description: e.target.value})}
                  placeholder="Photo description"
                  style={{
                    width: '100%',
                    padding: '10px',
                    border: '1px solid #E2E8F0',
                    borderRadius: '6px',
                    fontSize: '14px'
                  }}
                />
              </div>

              <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
                <button
                  onClick={() => setShowPhotoModal(false)}
                  style={{
                    padding: '10px 20px',
                    backgroundColor: '#FFFFFF',
                    color: '#64748B',
                    border: '1px solid #E2E8F0',
                    borderRadius: '8px',
                    fontSize: '14px',
                    fontWeight: '600',
                    cursor: 'pointer'
                  }}
                >
                  Cancel
                </button>
                <button
                  onClick={handleAddPhoto}
                  style={{
                    padding: '10px 20px',
                    backgroundColor: '#6366F1',
                    color: '#FFFFFF',
                    border: 'none',
                    borderRadius: '8px',
                    fontSize: '14px',
                    fontWeight: '600',
                    cursor: 'pointer'
                  }}
                >
                  Add Photo
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Add Deficiency Modal */}
        {showDeficiencyModal && (
          <div style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0,0,0,0.5)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000
          }}>
            <div style={{
              backgroundColor: '#FFFFFF',
              borderRadius: '12px',
              padding: '24px',
              maxWidth: '500px',
              width: '90%'
            }}>
              <h3 style={{ fontSize: '20px', fontWeight: '700', marginBottom: '20px' }}>Add Deficiency</h3>
              
              <div style={{ marginBottom: '16px' }}>
                <label style={{ display: 'block', fontSize: '13px', fontWeight: '600', color: '#64748B', marginBottom: '8px' }}>
                  Description
                </label>
                <textarea
                  value={deficiencyForm.description}
                  onChange={(e) => setDeficiencyForm({...deficiencyForm, description: e.target.value})}
                  placeholder="Describe the deficiency..."
                  rows={3}
                  style={{
                    width: '100%',
                    padding: '10px',
                    border: '1px solid #E2E8F0',
                    borderRadius: '6px',
                    fontSize: '14px',
                    fontFamily: 'inherit',
                    resize: 'vertical'
                  }}
                />
              </div>

              <div style={{ marginBottom: '16px' }}>
                <label style={{ display: 'block', fontSize: '13px', fontWeight: '600', color: '#64748B', marginBottom: '8px' }}>
                  Severity
                </label>
                <select
                  value={deficiencyForm.severity}
                  onChange={(e) => setDeficiencyForm({...deficiencyForm, severity: e.target.value})}
                  style={{
                    width: '100%',
                    padding: '10px',
                    border: '1px solid #E2E8F0',
                    borderRadius: '6px',
                    fontSize: '14px'
                  }}
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="critical">Critical</option>
                </select>
              </div>

              <div style={{ marginBottom: '20px' }}>
                <label style={{ display: 'block', fontSize: '13px', fontWeight: '600', color: '#64748B', marginBottom: '8px' }}>
                  Status
                </label>
                <select
                  value={deficiencyForm.status}
                  onChange={(e) => setDeficiencyForm({...deficiencyForm, status: e.target.value})}
                  style={{
                    width: '100%',
                    padding: '10px',
                    border: '1px solid #E2E8F0',
                    borderRadius: '6px',
                    fontSize: '14px'
                  }}
                >
                  <option value="open">Open</option>
                  <option value="in-progress">In Progress</option>
                  <option value="resolved">Resolved</option>
                </select>
              </div>

              <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
                <button
                  onClick={() => setShowDeficiencyModal(false)}
                  style={{
                    padding: '10px 20px',
                    backgroundColor: '#FFFFFF',
                    color: '#64748B',
                    border: '1px solid #E2E8F0',
                    borderRadius: '8px',
                    fontSize: '14px',
                    fontWeight: '600',
                    cursor: 'pointer'
                  }}
                >
                  Cancel
                </button>
                <button
                  onClick={handleAddDeficiency}
                  style={{
                    padding: '10px 20px',
                    backgroundColor: '#6366F1',
                    color: '#FFFFFF',
                    border: 'none',
                    borderRadius: '8px',
                    fontSize: '14px',
                    fontWeight: '600',
                    cursor: 'pointer'
                  }}
                >
                  Add Deficiency
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
