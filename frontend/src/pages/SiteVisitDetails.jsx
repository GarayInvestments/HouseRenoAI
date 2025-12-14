import React, { useEffect, useState } from 'react';
import { ArrowLeft, Calendar, MapPin, Users, Camera, AlertTriangle, CheckCircle, Clock, XCircle, Edit, Trash2, Save, X } from 'lucide-react';
import useSiteVisitsStore from '../stores/siteVisitsStore';
import useAppStore from '../stores/appStore';

/**
 * Site Visit Details Page
 * Displays comprehensive view of a single site visit
 * Shows visit info, attendees, photos, deficiencies, follow-up actions
 * Supports inline editing and deletion
 */

// Add spinner animation via style tag
const spinnerStyle = document.createElement('style');
spinnerStyle.textContent = `
  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }
`;
if (!document.head.querySelector('style[data-spinner]')) {
  spinnerStyle.setAttribute('data-spinner', 'true');
  document.head.appendChild(spinnerStyle);
}

const SiteVisitDetails = () => {
  const currentVisitId = useAppStore((state) => state.currentSiteVisitId);
  const navigateToSiteVisits = useAppStore((state) => state.navigateToSiteVisits);

  const {
    selectedVisit,
    loading,
    error,
    fetchSiteVisit,
    updateSiteVisit,
    deleteSiteVisit
  } = useSiteVisitsStore();

  const [isEditing, setIsEditing] = useState(false);
  const [editedVisit, setEditedVisit] = useState(null);
  const [isSaving, setIsSaving] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    if (currentVisitId) {
      fetchSiteVisit(currentVisitId);
    }
  }, [currentVisitId]);

  useEffect(() => {
    if (selectedVisit) {
      setEditedVisit({ ...selectedVisit });
    }
  }, [selectedVisit]);

  const handleSave = async () => {
    if (!editedVisit) return;
    
    setIsSaving(true);
    try {
      await updateSiteVisit(currentVisitId, editedVisit);
      setIsEditing(false);
    } catch (err) {
      console.error('Failed to save site visit:', err);
    } finally {
      setIsSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to delete this site visit?')) return;
    
    setIsDeleting(true);
    try {
      await deleteSiteVisit(currentVisitId);
      navigateToSiteVisits();
    } catch (err) {
      console.error('Failed to delete site visit:', err);
      setIsDeleting(false);
    }
  };

  const handleCancel = () => {
    setEditedVisit({ ...selectedVisit });
    setIsEditing(false);
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Not scheduled';
    try {
      return new Date(dateString).toLocaleDateString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      });
    } catch {
      return 'Invalid date';
    }
  };

  const formatTime = (timeString) => {
    if (!timeString) return 'Not set';
    try {
      const [hours, minutes] = timeString.split(':');
      const hour = parseInt(hours);
      const ampm = hour >= 12 ? 'PM' : 'AM';
      const displayHour = hour % 12 || 12;
      return `${displayHour}:${minutes} ${ampm}`;
    } catch {
      return timeString;
    }
  };

  const getStatusConfig = (status) => {
    const statusLower = (status || '').toLowerCase();
    switch(statusLower) {
      case 'scheduled':
        return { style: { backgroundColor: '#DBEAFE', color: '#1E40AF' }, icon: <Clock size={20} />, label: 'Scheduled' };
      case 'in-progress':
        return { style: { backgroundColor: '#FEF3C7', color: '#92400E' }, icon: <Clock size={20} />, label: 'In Progress' };
      case 'completed':
        return { style: { backgroundColor: '#D1FAE5', color: '#065F46' }, icon: <CheckCircle size={20} />, label: 'Completed' };
      case 'cancelled':
        return { style: { backgroundColor: '#FEE2E2', color: '#991B1B' }, icon: <XCircle size={20} />, label: 'Cancelled' };
      default:
        return { style: { backgroundColor: '#F3F4F6', color: '#374151' }, icon: <Clock size={20} />, label: status || 'Unknown' };
    }
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '256px' }}>
        <div style={{
          display: 'inline-block',
          width: '32px',
          height: '32px',
          border: '3px solid #E5E7EB',
          borderTopColor: '#2563EB',
          borderRadius: '50%',
          animation: 'spin 1s linear infinite'
        }} />
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: '16px' }}>
        <div style={{
          backgroundColor: '#FEF2F2',
          border: '1px solid #FECACA',
          color: '#991B1B',
          padding: '12px 16px',
          borderRadius: '8px'
        }}>
          {error}
        </div>
      </div>
    );
  }

  if (!selectedVisit || !editedVisit) {
    return (
      <div style={{ padding: '16px' }}>
        <div style={{
          backgroundColor: '#FEFCE8',
          border: '1px solid #FEF08A',
          color: '#854D0E',
          padding: '12px 16px',
          borderRadius: '8px'
        }}>
          Site visit not found
        </div>
      </div>
    );
  }

  const visit = isEditing ? editedVisit : selectedVisit;
  const statusConfig = getStatusConfig(visit.status);
  const attendees = visit.attendees || [];
  const photos = visit.photos || [];
  const deficiencies = visit.deficiencies || [];
  const followUpActions = visit.follow_up_actions || [];

  return (
    <div style={{ padding: '24px', maxWidth: '1200px', margin: '0 auto', backgroundColor: '#F9FAFB', minHeight: '100vh' }}>
      {/* Header */}
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
        alignItems: 'flex-start',
        gap: '16px',
        marginBottom: '24px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <button
            onClick={navigateToSiteVisits}
            style={{
              padding: '8px',
              backgroundColor: 'transparent',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              transition: 'all 0.2s ease'
            }}
            onMouseEnter={(e) => e.target.style.backgroundColor = '#F3F4F6'}
            onMouseLeave={(e) => e.target.style.backgroundColor = 'transparent'}
          >
            <ArrowLeft size={20} />
          </button>
          <div>
            <h1 style={{
              fontSize: '28px',
              fontWeight: '700',
              color: '#111827',
              margin: 0
            }}>
              {visit.business_id || visit.visit_id}
            </h1>
            <p style={{ fontSize: '14px', color: '#6B7280', margin: '4px 0 0 0' }}>{visit.visit_type || 'Site Visit'}</p>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          {!isEditing ? (
            <>
              <button
                onClick={() => setIsEditing(true)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  padding: '10px 20px',
                  backgroundColor: '#2563EB',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  fontWeight: '600',
                  fontSize: '14px',
                  transition: 'all 0.2s ease'
                }}
                onMouseEnter={(e) => e.target.style.backgroundColor = '#1D4ED8'}
                onMouseLeave={(e) => e.target.style.backgroundColor = '#2563EB'}
              >
                <Edit size={16} />
                Edit
              </button>
              <button
                onClick={handleDelete}
                disabled={isDeleting}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  padding: '10px 20px',
                  backgroundColor: '#DC2626',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  cursor: isDeleting ? 'not-allowed' : 'pointer',
                  fontWeight: '600',
                  fontSize: '14px',
                  opacity: isDeleting ? 0.5 : 1,
                  transition: 'all 0.2s ease'
                }}
                onMouseEnter={(e) => { if (!isDeleting) e.target.style.backgroundColor = '#B91C1C'; }}
                onMouseLeave={(e) => { if (!isDeleting) e.target.style.backgroundColor = '#DC2626'; }}
              >
                <Trash2 size={16} />
                {isDeleting ? 'Deleting...' : 'Delete'}
              </button>
            </>
          ) : (
            <>
              <button
                onClick={handleSave}
                disabled={isSaving}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  padding: '10px 20px',
                  backgroundColor: '#10B981',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  cursor: isSaving ? 'not-allowed' : 'pointer',
                  fontWeight: '600',
                  fontSize: '14px',
                  opacity: isSaving ? 0.5 : 1,
                  transition: 'all 0.2s ease'
                }}
                onMouseEnter={(e) => { if (!isSaving) e.target.style.backgroundColor = '#059669'; }}
                onMouseLeave={(e) => { if (!isSaving) e.target.style.backgroundColor = '#10B981'; }}
              >
                <Save size={16} />
                {isSaving ? 'Saving...' : 'Save'}
              </button>
              <button
                onClick={handleCancel}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  padding: '10px 20px',
                  backgroundColor: '#6B7280',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  fontWeight: '600',
                  fontSize: '14px',
                  transition: 'all 0.2s ease'
                }}
                onMouseEnter={(e) => e.target.style.backgroundColor = '#4B5563'}
                onMouseLeave={(e) => e.target.style.backgroundColor = '#6B7280'}
              >
                <X size={16} />
                Cancel
              </button>
            </>
          )}
        </div>
      </div>

      {/* Status Badge */}
      <div style={{ marginBottom: '24px' }}>
        <span style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '8px',
          padding: '8px 16px',
          borderRadius: '20px',
          fontSize: '14px',
          fontWeight: '500',
          ...statusConfig.style
        }}>
          {statusConfig.icon}
          {statusConfig.label}
        </span>
      </div>

      {/* Visit Information */}
      <div style={{
        backgroundColor: 'white',
        borderRadius: '12px',
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
        padding: '24px',
        marginBottom: '24px'
      }}>
        <h2 style={{
          fontSize: '18px',
          fontWeight: '600',
          color: '#111827',
          marginBottom: '16px'
        }}>Visit Information</h2>
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
            }}>Scheduled Date</label>
            {isEditing ? (
              <input
                type="date"
                value={visit.scheduled_date || ''}
                onChange={(e) => setEditedVisit({ ...editedVisit, scheduled_date: e.target.value })}
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  border: '1px solid #D1D5DB',
                  borderRadius: '8px',
                  fontSize: '14px',
                  outline: 'none'
                }}
                onFocus={(e) => e.target.style.borderColor = '#2563EB'}
                onBlur={(e) => e.target.style.borderColor = '#D1D5DB'}
              />
            ) : (
              <p style={{ color: '#111827', fontSize: '14px' }}>{formatDate(visit.scheduled_date)}</p>
            )}
          </div>

          <div>
            <label style={{
              display: 'block',
              fontSize: '14px',
              fontWeight: '500',
              color: '#374151',
              marginBottom: '4px'
            }}>Status</label>
            {isEditing ? (
              <select
                value={visit.status || ''}
                onChange={(e) => setEditedVisit({ ...editedVisit, status: e.target.value })}
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  border: '1px solid #D1D5DB',
                  borderRadius: '8px',
                  fontSize: '14px',
                  outline: 'none'
                }}
                onFocus={(e) => e.target.style.borderColor = '#2563EB'}
                onBlur={(e) => e.target.style.borderColor = '#D1D5DB'}
              >
                <option value="scheduled">Scheduled</option>
                <option value="in-progress">In Progress</option>
                <option value="completed">Completed</option>
                <option value="cancelled">Cancelled</option>
              </select>
            ) : (
              <p style={{ color: '#111827', fontSize: '14px' }}>{visit.status || 'Not set'}</p>
            )}
          </div>

          <div>
            <label style={{
              display: 'block',
              fontSize: '14px',
              fontWeight: '500',
              color: '#374151',
              marginBottom: '4px'
            }}>Start Time</label>
            {isEditing ? (
              <input
                type="time"
                value={visit.start_time || ''}
                onChange={(e) => setEditedVisit({ ...editedVisit, start_time: e.target.value })}
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  border: '1px solid #D1D5DB',
                  borderRadius: '8px',
                  fontSize: '14px',
                  outline: 'none'
                }}
                onFocus={(e) => e.target.style.borderColor = '#2563EB'}
                onBlur={(e) => e.target.style.borderColor = '#D1D5DB'}
              />
            ) : (
              <p style={{ color: '#111827', fontSize: '14px' }}>{formatTime(visit.start_time)}</p>
            )}
          </div>

          <div>
            <label style={{
              display: 'block',
              fontSize: '14px',
              fontWeight: '500',
              color: '#374151',
              marginBottom: '4px'
            }}>End Time</label>
            {isEditing ? (
              <input
                type="time"
                value={visit.end_time || ''}
                onChange={(e) => setEditedVisit({ ...editedVisit, end_time: e.target.value })}
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  border: '1px solid #D1D5DB',
                  borderRadius: '8px',
                  fontSize: '14px',
                  outline: 'none'
                }}
                onFocus={(e) => e.target.style.borderColor = '#2563EB'}
                onBlur={(e) => e.target.style.borderColor = '#D1D5DB'}
              />
            ) : (
              <p style={{ color: '#111827', fontSize: '14px' }}>{formatTime(visit.end_time)}</p>
            )}
          </div>

          <div style={{ gridColumn: '1 / -1' }}>
            <label style={{
              display: 'block',
              fontSize: '14px',
              fontWeight: '500',
              color: '#374151',
              marginBottom: '4px'
            }}>
              <MapPin size={16} style={{ display: 'inline', marginRight: '4px', verticalAlign: 'middle' }} />
              GPS Location
            </label>
            {isEditing ? (
              <input
                type="text"
                value={visit.gps_location || ''}
                onChange={(e) => setEditedVisit({ ...editedVisit, gps_location: e.target.value })}
                placeholder="Enter GPS coordinates or address"
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  border: '1px solid #D1D5DB',
                  borderRadius: '8px',
                  fontSize: '14px',
                  outline: 'none'
                }}
                onFocus={(e) => e.target.style.borderColor = '#2563EB'}
                onBlur={(e) => e.target.style.borderColor = '#D1D5DB'}
              />
            ) : (
              <p style={{ color: '#111827', fontSize: '14px' }}>{visit.gps_location || 'Not set'}</p>
            )}
          </div>

          <div>
            <label style={{
              display: 'block',
              fontSize: '14px',
              fontWeight: '500',
              color: '#374151',
              marginBottom: '4px'
            }}>Weather</label>
            {isEditing ? (
              <input
                type="text"
                value={visit.weather || ''}
                onChange={(e) => setEditedVisit({ ...editedVisit, weather: e.target.value })}
                placeholder="e.g., Sunny, 75°F"
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  border: '1px solid #D1D5DB',
                  borderRadius: '8px',
                  fontSize: '14px',
                  outline: 'none'
                }}
                onFocus={(e) => e.target.style.borderColor = '#2563EB'}
                onBlur={(e) => e.target.style.borderColor = '#D1D5DB'}
              />
            ) : (
              <p style={{ color: '#111827', fontSize: '14px' }}>{visit.weather || 'Not recorded'}</p>
            )}
          </div>

          <div>
            <label style={{
              display: 'block',
              fontSize: '14px',
              fontWeight: '500',
              color: '#374151',
              marginBottom: '4px'
            }}>Visit Type</label>
            {isEditing ? (
              <input
                type="text"
                value={visit.visit_type || ''}
                onChange={(e) => setEditedVisit({ ...editedVisit, visit_type: e.target.value })}
                placeholder="e.g., Pre-Construction, Progress Check"
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  border: '1px solid #D1D5DB',
                  borderRadius: '8px',
                  fontSize: '14px',
                  outline: 'none'
                }}
                onFocus={(e) => e.target.style.borderColor = '#2563EB'}
                onBlur={(e) => e.target.style.borderColor = '#D1D5DB'}
              />
            ) : (
              <p style={{ color: '#111827', fontSize: '14px' }}>{visit.visit_type || 'Not specified'}</p>
            )}
          </div>

          <div style={{ gridColumn: '1 / -1' }}>
            <label style={{
              display: 'block',
              fontSize: '14px',
              fontWeight: '500',
              color: '#374151',
              marginBottom: '4px'
            }}>Notes</label>
            {isEditing ? (
              <textarea
                value={visit.notes || ''}
                onChange={(e) => setEditedVisit({ ...editedVisit, notes: e.target.value })}
                rows={4}
                placeholder="Enter visit notes..."
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  border: '1px solid #D1D5DB',
                  borderRadius: '8px',
                  fontSize: '14px',
                  outline: 'none',
                  fontFamily: 'inherit'
                }}
                onFocus={(e) => e.target.style.borderColor = '#2563EB'}
                onBlur={(e) => e.target.style.borderColor = '#D1D5DB'}
              />
            ) : (
              <p style={{ color: '#111827', fontSize: '14px', whiteSpace: 'pre-wrap' }}>{visit.notes || 'No notes'}</p>
            )}
          </div>
        </div>
      </div>

      {/* Attendees */}
      <div style={{
        backgroundColor: 'white',
        borderRadius: '12px',
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
        padding: '24px',
        marginBottom: '24px'
      }}>
        <h2 style={{
          fontSize: '18px',
          fontWeight: '600',
          color: '#111827',
          marginBottom: '16px',
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}>
          <Users size={20} />
          Attendees ({Array.isArray(attendees) ? attendees.length : 0})
        </h2>
        {Array.isArray(attendees) && attendees.length > 0 ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {attendees.map((attendee, index) => (
              <div key={index} style={{
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                padding: '12px',
                backgroundColor: '#F9FAFB',
                borderRadius: '8px'
              }}>
                <div style={{
                  width: '40px',
                  height: '40px',
                  backgroundColor: '#2563EB',
                  color: 'white',
                  borderRadius: '50%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontWeight: '600',
                  fontSize: '16px'
                }}>
                  {typeof attendee === 'string' 
                    ? attendee.charAt(0).toUpperCase()
                    : attendee.name ? attendee.name.charAt(0).toUpperCase() : '?'}
                </div>
                <div>
                  <p style={{ fontWeight: '500', color: '#111827', margin: 0 }}>
                    {typeof attendee === 'string' ? attendee : attendee.name || 'Unknown'}
                  </p>
                  {typeof attendee === 'object' && attendee.role && (
                    <p style={{ fontSize: '14px', color: '#6B7280', margin: 0 }}>{attendee.role}</p>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p style={{ color: '#9CA3AF' }}>No attendees recorded</p>
        )}
      </div>

      {/* Photos */}
      <div style={{
        backgroundColor: 'white',
        borderRadius: '12px',
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
        padding: '24px',
        marginBottom: '24px'
      }}>
        <h2 style={{
          fontSize: '18px',
          fontWeight: '600',
          color: '#111827',
          marginBottom: '16px',
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}>
          <Camera size={20} />
          Photos ({Array.isArray(photos) ? photos.length : 0})
        </h2>
        {Array.isArray(photos) && photos.length > 0 ? (
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(150px, 1fr))',
            gap: '16px'
          }}>
            {photos.map((photo, index) => (
              <div key={index} style={{ position: 'relative' }}>
                <img
                  src={typeof photo === 'string' ? photo : photo.url}
                  alt={`Site photo ${index + 1}`}
                  style={{
                    width: '100%',
                    height: '160px',
                    objectFit: 'cover',
                    borderRadius: '8px'
                  }}
                />
                {typeof photo === 'object' && photo.timestamp && (
                  <div style={{
                    position: 'absolute',
                    bottom: 0,
                    left: 0,
                    right: 0,
                    backgroundColor: 'rgba(0, 0, 0, 0.5)',
                    color: 'white',
                    fontSize: '12px',
                    padding: '8px',
                    borderBottomLeftRadius: '8px',
                    borderBottomRightRadius: '8px'
                  }}>
                    {new Date(photo.timestamp).toLocaleString()}
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <p style={{ color: '#9CA3AF' }}>No photos uploaded</p>
        )}
      </div>

      {/* Deficiencies */}
      <div style={{
        backgroundColor: 'white',
        borderRadius: '12px',
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
        padding: '24px',
        marginBottom: '24px'
      }}>
        <h2 style={{
          fontSize: '18px',
          fontWeight: '600',
          color: '#111827',
          marginBottom: '16px',
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}>
          <AlertTriangle size={20} />
          Deficiencies ({Array.isArray(deficiencies) ? deficiencies.length : 0})
        </h2>
        {Array.isArray(deficiencies) && deficiencies.length > 0 ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {deficiencies.map((deficiency, index) => (
              <div key={index} style={{
                padding: '16px',
                backgroundColor: '#FEF3C7',
                borderLeft: '4px solid #F59E0B',
                borderRadius: '8px'
              }}>
                <p style={{ fontWeight: '500', color: '#111827', margin: 0 }}>
                  {typeof deficiency === 'string' ? deficiency : deficiency.description || 'Deficiency noted'}
                </p>
                {typeof deficiency === 'object' && deficiency.severity && (
                  <p style={{ fontSize: '14px', color: '#92400E', marginTop: '4px' }}>Severity: {deficiency.severity}</p>
                )}
                {typeof deficiency === 'object' && deficiency.location && (
                  <p style={{ fontSize: '14px', color: '#6B7280', marginTop: '4px' }}>Location: {deficiency.location}</p>
                )}
              </div>
            ))}
          </div>
        ) : (
          <p style={{ color: '#9CA3AF' }}>No deficiencies found</p>
        )}
      </div>

      {/* Follow-Up Actions */}
      <div style={{
        backgroundColor: 'white',
        borderRadius: '12px',
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
        padding: '24px'
      }}>
        <h2 style={{
          fontSize: '18px',
          fontWeight: '600',
          color: '#111827',
          marginBottom: '16px',
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}>
          <CheckCircle size={20} />
          Follow-Up Actions ({Array.isArray(followUpActions) ? followUpActions.length : 0})
        </h2>
        {Array.isArray(followUpActions) && followUpActions.length > 0 ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {followUpActions.map((action, index) => (
              <div key={index} style={{
                display: 'flex',
                alignItems: 'flex-start',
                gap: '12px',
                padding: '12px',
                backgroundColor: '#EFF6FF',
                borderRadius: '8px'
              }}>
                <div style={{ marginTop: '2px' }}>
                  <CheckCircle size={20} color="#2563EB" />
                </div>
                <div style={{ flex: 1 }}>
                  <p style={{ color: '#111827', margin: 0 }}>
                    {typeof action === 'string' ? action : action.description || 'Action required'}
                  </p>
                  {typeof action === 'object' && action.due_date && (
                    <p style={{ fontSize: '14px', color: '#6B7280', marginTop: '4px' }}>Due: {formatDate(action.due_date)}</p>
                  )}
                  {typeof action === 'object' && action.assigned_to && (
                    <p style={{ fontSize: '14px', color: '#6B7280', marginTop: '2px' }}>Assigned: {action.assigned_to}</p>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p style={{ color: '#9CA3AF' }}>No follow-up actions</p>
        )}
      </div>
    </div>
  );
};

export default SiteVisitDetails;
