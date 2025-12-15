import React, { useEffect, useState } from 'react';
import { Calendar, MapPin, Users, Camera, AlertTriangle, CheckCircle, Clock, XCircle, Plus, Search } from 'lucide-react';
import useSiteVisitsStore from '../stores/siteVisitsStore';
import useAppStore from '../stores/appStore';

/**
 * Site Visits Page
 * Displays list of site visits with statistics, filtering, and search
 * Shows visit cards with status, location, photos, and deficiencies
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

const SiteVisits = () => {
  const {
    loading,
    error,
    filter,
    setFilter,
    fetchSiteVisits,
    getFilteredSiteVisits,
    getSiteVisitStats
  } = useSiteVisitsStore();

  const navigateToSiteVisitDetails = useAppStore((state) => state.navigateToSiteVisitDetails);
  const navigateToNewSiteVisit = useAppStore((state) => state.navigateToNewSiteVisit);

  const [searchQuery, setSearchQuery] = useState('');
  const [filteredVisits, setFilteredVisits] = useState([]);

  useEffect(() => {
    fetchSiteVisits();
  }, []);

  useEffect(() => {
    const visits = getFilteredSiteVisits();
    
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      const filtered = visits.filter(visit => {
        const businessId = (visit.business_id || '').toLowerCase();
        const visitType = (visit.visit_type || visit['Visit Type'] || '').toLowerCase();
        const location = (visit.gps_location || visit['GPS Location'] || '').toLowerCase();
        const notes = (visit.notes || visit['Notes'] || '').toLowerCase();
        
        return businessId.includes(query) ||
               visitType.includes(query) ||
               location.includes(query) ||
               notes.includes(query);
      });
      setFilteredVisits(filtered);
    } else {
      setFilteredVisits(visits);
    }
  }, [searchQuery, filter, getFilteredSiteVisits]);

  const stats = getSiteVisitStats();

  const formatDate = (dateString) => {
    if (!dateString) return 'Not scheduled';
    try {
      return new Date(dateString).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric'
      });
    } catch {
      return 'Invalid date';
    }
  };

  const formatTime = (timeString) => {
    if (!timeString) return '';
    try {
      // Handle both HH:mm:ss and HH:mm formats
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
        return { 
          style: { backgroundColor: '#DBEAFE', color: '#1E40AF' }, 
          icon: <Clock size={16} />, 
          label: 'Scheduled' 
        };
      case 'in-progress':
        return { 
          style: { backgroundColor: '#FEF3C7', color: '#92400E' }, 
          icon: <Clock size={16} />, 
          label: 'In Progress' 
        };
      case 'completed':
        return { 
          style: { backgroundColor: '#D1FAE5', color: '#065F46' }, 
          icon: <CheckCircle size={16} />, 
          label: 'Completed' 
        };
      case 'cancelled':
        return { 
          style: { backgroundColor: '#FEE2E2', color: '#991B1B' }, 
          icon: <XCircle size={16} />, 
          label: 'Cancelled' 
        };
      default:
        return { 
          style: { backgroundColor: '#F3F4F6', color: '#374151' }, 
          icon: <Clock size={16} />, 
          label: status || 'Unknown' 
        };
    }
  };

  const filterButtons = [
    { value: 'all', label: 'All Visits', count: stats.total },
    { value: 'scheduled', label: 'Scheduled', count: stats.scheduled },
    { value: 'in-progress', label: 'In Progress', count: stats.inProgress },
    { value: 'completed', label: 'Completed', count: stats.completed },
    { value: 'cancelled', label: 'Cancelled', count: stats.cancelled }
  ];

  return (
    <div style={{ 
      padding: '24px',
      maxWidth: '1400px',
      margin: '0 auto',
      minHeight: '100vh',
      backgroundColor: '#F9FAFB'
    }}>
      {/* Header */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '24px',
        flexWrap: 'wrap',
        gap: '16px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <MapPin size={32} color="#2563EB" />
          <h1 style={{ 
            fontSize: '28px', 
            fontWeight: '700',
            color: '#111827',
            margin: 0
          }}>
            Site Visits
          </h1>
        </div>
        
        <button
          onClick={() => navigateToNewSiteVisit && navigateToNewSiteVisit()}
          style={{
            padding: '10px 20px',
            backgroundColor: '#2563EB',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            cursor: 'pointer',
            fontWeight: '600',
            fontSize: '14px',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            transition: 'all 0.2s ease'
          }}
          onMouseEnter={(e) => e.target.style.backgroundColor = '#1D4ED8'}
          onMouseLeave={(e) => e.target.style.backgroundColor = '#2563EB'}
        >
          <Plus size={16} />
          New Site Visit
        </button>
      </div>

      {/* Stats Cards */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))',
        gap: '16px',
        marginBottom: '24px'
      }}>
        <div style={{
          backgroundColor: 'white',
          padding: '20px',
          borderRadius: '12px',
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between'
        }}>
          <div>
            <p style={{ fontSize: '14px', color: '#6B7280', marginBottom: '4px' }}>Total Visits</p>
            <p style={{ fontSize: '28px', fontWeight: '700', color: '#111827' }}>{stats.total}</p>
          </div>
          <Calendar size={32} color="#2563EB" />
        </div>

        <div style={{
          backgroundColor: 'white',
          padding: '20px',
          borderRadius: '12px',
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between'
        }}>
          <div>
            <p style={{ fontSize: '14px', color: '#6B7280', marginBottom: '4px' }}>Completed</p>
            <p style={{ fontSize: '28px', fontWeight: '700', color: '#10B981' }}>{stats.completed}</p>
          </div>
          <CheckCircle size={32} color="#10B981" />
        </div>

        <div style={{
          backgroundColor: 'white',
          padding: '20px',
          borderRadius: '12px',
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between'
        }}>
          <div>
            <p style={{ fontSize: '14px', color: '#6B7280', marginBottom: '4px' }}>With Photos</p>
            <p style={{ fontSize: '28px', fontWeight: '700', color: '#8B5CF6' }}>{stats.withPhotos}</p>
          </div>
          <Camera size={32} color="#8B5CF6" />
        </div>

        <div style={{
          backgroundColor: 'white',
          padding: '20px',
          borderRadius: '12px',
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between'
        }}>
          <div>
            <p style={{ fontSize: '14px', color: '#6B7280', marginBottom: '4px' }}>Deficiencies</p>
            <p style={{ fontSize: '28px', fontWeight: '700', color: '#F59E0B' }}>{stats.withDeficiencies}</p>
          </div>
          <AlertTriangle size={32} color="#F59E0B" />
        </div>
      </div>

      {/* Search and Filters */}
      <div style={{
        backgroundColor: 'white',
        padding: '16px',
        borderRadius: '12px',
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
        marginBottom: '24px'
      }}>
        <div style={{ marginBottom: '16px' }}>
          <div style={{ position: 'relative' }}>
            <Search size={20} style={{
              position: 'absolute',
              left: '12px',
              top: '50%',
              transform: 'translateY(-50%)',
              color: '#9CA3AF'
            }} />
            <input
              type="text"
              placeholder="Search by business ID, type, location, or notes..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{
                width: '100%',
                padding: '10px 10px 10px 40px',
                border: '1px solid #D1D5DB',
                borderRadius: '8px',
                fontSize: '14px',
                outline: 'none'
              }}
              onFocus={(e) => e.target.style.borderColor = '#2563EB'}
              onBlur={(e) => e.target.style.borderColor = '#D1D5DB'}
            />
          </div>
        </div>

        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
          {filterButtons.map((btn) => (
            <button
              key={btn.value}
              onClick={() => setFilter(btn.value)}
              style={{
                padding: '8px 16px',
                backgroundColor: filter === btn.value ? '#2563EB' : '#F3F4F6',
                color: filter === btn.value ? 'white' : '#374151',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
                fontSize: '14px',
                fontWeight: '500',
                transition: 'all 0.2s ease'
              }}
              onMouseEnter={(e) => {
                if (filter !== btn.value) {
                  e.target.style.backgroundColor = '#E5E7EB';
                }
              }}
              onMouseLeave={(e) => {
                if (filter !== btn.value) {
                  e.target.style.backgroundColor = '#F3F4F6';
                }
              }}
            >
              {btn.label} ({btn.count})
            </button>
          ))}
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div style={{
          backgroundColor: '#FEF2F2',
          border: '1px solid #FECACA',
          color: '#991B1B',
          padding: '12px 16px',
          borderRadius: '8px',
          marginBottom: '24px'
        }}>
          {error}
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div style={{ textAlign: 'center', padding: '48px 0' }}>
          <div style={{
            display: 'inline-block',
            width: '32px',
            height: '32px',
            border: '3px solid #E5E7EB',
            borderTopColor: '#2563EB',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite'
          }} />
          <p style={{ marginTop: '8px', color: '#6B7280' }}>Loading site visits...</p>
        </div>
      )}

      {/* Site Visits List */}
      {!loading && filteredVisits.length === 0 && (
        <div style={{
          textAlign: 'center',
          padding: '48px',
          backgroundColor: 'white',
          borderRadius: '12px',
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
        }}>
          <Calendar size={64} color="#9CA3AF" style={{ margin: '0 auto 16px' }} />
          <p style={{ color: '#6B7280', fontSize: '18px' }}>No site visits found</p>
          {searchQuery && (
            <p style={{ color: '#9CA3AF', marginTop: '8px' }}>Try adjusting your search criteria</p>
          )}
        </div>
      )}

      {!loading && filteredVisits.length > 0 && (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))',
          gap: '16px'
        }}>
          {filteredVisits.map((visit) => {
            const statusConfig = getStatusConfig(visit.status || visit['Visit Status']);
            const visitDate = visit.scheduled_date || visit['Scheduled Date'];
            const startTime = visit.start_time || visit['Start Time'];
            const endTime = visit.end_time || visit['End Time'];
            const visitType = visit.visit_type || visit['Visit Type'] || 'Site Visit';
            const location = visit.gps_location || visit['GPS Location'];
            const attendees = visit.attendees || visit['Attendees'] || [];
            const photos = visit.photos || visit['Photos'] || [];
            const deficiencies = visit.deficiencies || visit['Deficiencies'] || [];
            const businessId = visit.business_id || visit['Business ID'] || visit.visit_id;

            return (
              <div
                key={visit.visit_id || visit.id}
                onClick={() => navigateToSiteVisitDetails(visit.visit_id || visit.id)}
                style={{
                  backgroundColor: 'white',
                  padding: '20px',
                  borderRadius: '12px',
                  boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease'
                }}
                onMouseEnter={(e) => e.currentTarget.style.boxShadow = '0 4px 6px rgba(0,0,0,0.15)'}
                onMouseLeave={(e) => e.currentTarget.style.boxShadow = '0 1px 3px rgba(0,0,0,0.1)'}
              >
                <div style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'flex-start',
                  marginBottom: '12px'
                }}>
                  <div>
                    <h3 style={{
                      fontSize: '18px',
                      fontWeight: '600',
                      color: '#111827',
                      margin: 0
                    }}>{businessId}</h3>
                    <p style={{
                      fontSize: '14px',
                      color: '#6B7280',
                      margin: '4px 0 0 0'
                    }}>{visitType}</p>
                  </div>
                  <span style={{
                    padding: '6px 12px',
                    borderRadius: '20px',
                    fontSize: '12px',
                    fontWeight: '500',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px',
                    ...statusConfig.style
                  }}>
                    {statusConfig.icon}
                    {statusConfig.label}
                  </span>
                </div>

                <div style={{ marginBottom: '16px' }}>
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    fontSize: '14px',
                    color: '#6B7280',
                    marginBottom: '8px'
                  }}>
                    <Calendar size={16} />
                    <span>{formatDate(visitDate)}</span>
                    {startTime && (
                      <span style={{ marginLeft: '8px' }}>
                        {formatTime(startTime)}
                        {endTime && ` - ${formatTime(endTime)}`}
                      </span>
                    )}
                  </div>

                  {location && (
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px',
                      fontSize: '14px',
                      color: '#6B7280',
                      marginBottom: '8px',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      whiteSpace: 'nowrap'
                    }}>
                      <MapPin size={16} />
                      <span style={{
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        whiteSpace: 'nowrap'
                      }}>{location}</span>
                    </div>
                  )}

                  {Array.isArray(attendees) && attendees.length > 0 && (
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px',
                      fontSize: '14px',
                      color: '#6B7280'
                    }}>
                      <Users size={16} />
                      <span>{attendees.length} attendee{attendees.length !== 1 ? 's' : ''}</span>
                    </div>
                  )}
                </div>

                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '16px',
                  paddingTop: '12px',
                  borderTop: '1px solid #E5E7EB'
                }}>
                  {Array.isArray(photos) && photos.length > 0 && (
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '4px',
                      fontSize: '14px',
                      color: '#8B5CF6'
                    }}>
                      <Camera size={16} />
                      <span>{photos.length}</span>
                    </div>
                  )}

                  {Array.isArray(deficiencies) && deficiencies.length > 0 && (
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '4px',
                      fontSize: '14px',
                      color: '#F59E0B'
                    }}>
                      <AlertTriangle size={16} />
                      <span>{deficiencies.length}</span>
                    </div>
                  )}

                  {(!photos || photos.length === 0) && (!deficiencies || deficiencies.length === 0) && (
                    <span style={{ fontSize: '14px', color: '#9CA3AF' }}>No photos or deficiencies</span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default SiteVisits;
