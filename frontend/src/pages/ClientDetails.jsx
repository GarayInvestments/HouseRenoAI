import { useState, useEffect } from 'react';
import { ArrowLeft, User, Mail, Phone, MapPin, Calendar, FileText, Loader2 } from 'lucide-react';
import api from '../lib/api';
import useAppStore from '../stores/appStore';

export default function ClientDetails() {
  const [client, setClient] = useState(null);
  const [projects, setProjects] = useState([]);
  const [permits, setPermits] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const currentClientId = useAppStore((state) => state.currentClientId);
  const navigateToClients = useAppStore((state) => state.navigateToClients);

  useEffect(() => {
    // Handle browser back button
    const handlePopState = () => {
      navigateToClients();
    };

    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, [navigateToClients]);

  useEffect(() => {
    // Push state for browser back button support
    window.history.pushState({ view: 'client-details' }, '', '');
    
    const fetchClientDetails = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // Fetch client, projects, and permits in parallel
        const [clientData, projectsData, permitsData] = await Promise.all([
          api.getClient(currentClientId),
          api.getProjects(),
          api.getPermits()
        ]);
        
        setClient(clientData);
        
        // Filter projects for this client
        const clientProjects = Array.isArray(projectsData) 
          ? projectsData.filter(p => p['Client ID'] === currentClientId)
          : [];
        setProjects(clientProjects);
        
        // Filter permits for this client's projects
        const projectIds = clientProjects.map(p => p['Project ID']);
        const clientPermits = Array.isArray(permitsData)
          ? permitsData.filter(permit => projectIds.includes(permit['Project ID']))
          : [];
        setPermits(clientPermits);
        
      } catch {
        setError('Failed to load client details. Please try again.');
      } finally {
        setLoading(false);
      }
    };
    
    if (currentClientId) {
      fetchClientDetails();
    }
  }, [currentClientId]);

  const handleBackClick = () => {
    window.history.back();
  };

  const handleRetry = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [clientData, projectsData, permitsData] = await Promise.all([
        api.getClient(currentClientId),
        api.getProjects(),
        api.getPermits()
      ]);
      
      setClient(clientData);
      
      const clientProjects = Array.isArray(projectsData) 
        ? projectsData.filter(p => p['Client ID'] === currentClientId)
        : [];
      setProjects(clientProjects);
      
      const projectIds = clientProjects.map(p => p['Project ID']);
      const clientPermits = Array.isArray(permitsData)
        ? permitsData.filter(permit => projectIds.includes(permit['Project ID']))
        : [];
      setPermits(clientPermits);
      
    } catch {
      setError('Failed to load client details. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <Loader2 className="h-12 w-12 animate-spin text-blue-500 mx-auto mb-4" />
          <p className="text-gray-600">Loading client details...</p>
        </div>
      </div>
    );
  }

  if (error || !client) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <p className="text-red-600 mb-4">{error || 'Client not found'}</p>
          <button
            onClick={handleRetry}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  const clientName = client['Full Name'] || client['Client Name'] || 'Unnamed Client';
  const clientId = client['Client ID'] || client['ID'] || '';
  const email = client['Email'] || '';
  const phone = client['Phone'] || '';
  const address = client['Address'] || '';
  const city = client['City'] || '';
  const state = client['State'] || '';
  const zip = client['ZIP'] || client['Zip Code'] || '';
  const dateAdded = client['Date Added'] || client['Created Date'] || '';
  const notes = client['Notes'] || client['Client Notes'] || '';
  const preferredContact = client['Preferred Contact Method'] || '';
  const companyName = client['Company Name'] || '';
  
  // Calculate actual counts from fetched data
  const activeProjectsCount = projects.length;
  const activePermitsCount = permits.length;

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      height: '100%',
      backgroundColor: '#F8FAFC'
    }}>
      {/* Back Button */}
      <button
        onClick={handleBackClick}
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          color: '#64748B',
          background: 'none',
          border: 'none',
          padding: '16px 32px',
          fontSize: '14px',
          fontWeight: '500',
          cursor: 'pointer',
          transition: 'color 0.2s ease'
        }}
        onMouseEnter={(e) => e.currentTarget.style.color = '#1E293B'}
        onMouseLeave={(e) => e.currentTarget.style.color = '#64748B'}
      >
        <ArrowLeft size={20} />
        <span>Back to Clients</span>
      </button>

      {/* Content */}
      <div style={{
        flex: 1,
        overflowY: 'auto',
        padding: '0 32px 80px 32px'
      }}>
        <div style={{
          maxWidth: '900px',
          margin: '0 auto'
        }}>
          {/* Client Header */}
          <div style={{
            backgroundColor: '#FFFFFF',
            borderRadius: '12px',
            boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.05)',
            border: '1px solid #E2E8F0',
            padding: '24px',
            marginBottom: '24px'
          }}>
            <div style={{
              display: 'flex',
              alignItems: 'flex-start',
              justifyContent: 'space-between'
            }}>
              <div style={{ flex: 1 }}>
                <h1 style={{
                  fontSize: '28px',
                  fontWeight: '600',
                  color: '#1E293B',
                  marginBottom: '8px'
                }}>{clientName}</h1>
                {companyName && (
                  <p style={{
                    fontSize: '16px',
                    color: '#64748B',
                    marginBottom: '4px'
                  }}>{companyName}</p>
                )}
                <p style={{
                  fontSize: '13px',
                  color: '#94A3B8'
                }}>Client ID: {clientId}</p>
              </div>
              <div style={{
                width: '56px',
                height: '56px',
                borderRadius: '12px',
                background: 'linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexShrink: 0,
                boxShadow: '0 4px 6px -1px rgba(37, 99, 235, 0.3)'
              }}>
                <User size={28} style={{ color: '#FFFFFF' }} />
              </div>
            </div>
          </div>

          {/* Contact Information */}
          <div style={{
            backgroundColor: '#FFFFFF',
            borderRadius: '12px',
            boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.05)',
            border: '1px solid #E2E8F0',
            padding: '24px',
            marginBottom: '24px'
          }}>
            <h2 style={{
              fontSize: '18px',
              fontWeight: '600',
              color: '#1E293B',
              marginBottom: '20px'
            }}>Contact Information</h2>
            <div style={{
              display: 'flex',
              flexDirection: 'column',
              gap: '16px'
            }}>
              {email && (
                <div style={{
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: '12px'
                }}>
                  <Mail size={20} style={{ color: '#94A3B8', flexShrink: 0, marginTop: '2px' }} />
                  <div>
                    <p style={{
                      fontSize: '12px',
                      color: '#94A3B8',
                      marginBottom: '4px'
                    }}>Email</p>
                    <a href={`mailto:${email}`} style={{
                      color: '#2563EB',
                      fontSize: '14px',
                      textDecoration: 'none',
                      wordBreak: 'break-all'
                    }}
                    onMouseEnter={(e) => e.currentTarget.style.textDecoration = 'underline'}
                    onMouseLeave={(e) => e.currentTarget.style.textDecoration = 'none'}
                    >
                      {email}
                    </a>
                  </div>
                </div>
              )}
              {phone && (
                <div style={{
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: '12px'
                }}>
                  <Phone size={20} style={{ color: '#94A3B8', flexShrink: 0, marginTop: '2px' }} />
                  <div>
                    <p style={{
                      fontSize: '12px',
                      color: '#94A3B8',
                      marginBottom: '4px'
                    }}>Phone</p>
                    <a href={`tel:${phone}`} style={{
                      color: '#2563EB',
                      fontSize: '14px',
                      textDecoration: 'none'
                    }}
                    onMouseEnter={(e) => e.currentTarget.style.textDecoration = 'underline'}
                    onMouseLeave={(e) => e.currentTarget.style.textDecoration = 'none'}
                    >
                      {phone}
                    </a>
                  </div>
                </div>
              )}
              {preferredContact && (
                <div style={{
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: '12px'
                }}>
                  <FileText size={20} style={{ color: '#94A3B8', flexShrink: 0, marginTop: '2px' }} />
                  <div>
                    <p style={{
                      fontSize: '12px',
                      color: '#94A3B8',
                      marginBottom: '4px'
                    }}>Preferred Contact Method</p>
                    <p style={{
                      fontSize: '14px',
                      color: '#1E293B'
                    }}>{preferredContact}</p>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Address Information */}
          {(address || city || state || zip) && (
            <div style={{
              backgroundColor: '#FFFFFF',
              borderRadius: '12px',
              boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.05)',
              border: '1px solid #E2E8F0',
              padding: '24px',
              marginBottom: '24px'
            }}>
              <h2 style={{
                fontSize: '18px',
                fontWeight: '600',
                color: '#1E293B',
                marginBottom: '20px'
              }}>Address</h2>
              <div style={{
                display: 'flex',
                alignItems: 'flex-start',
                gap: '12px'
              }}>
                <MapPin size={20} style={{ color: '#94A3B8', flexShrink: 0, marginTop: '2px' }} />
                <div>
                  {address && <p style={{
                    fontSize: '14px',
                    color: '#1E293B',
                    marginBottom: '4px'
                  }}>{address}</p>}
                  {(city || state || zip) && (
                    <p style={{
                      fontSize: '14px',
                      color: '#475569'
                    }}>
                      {city}{city && (state || zip) && ', '}
                      {state} {zip}
                    </p>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Client Details */}
          <div style={{
            backgroundColor: '#FFFFFF',
            borderRadius: '12px',
            boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.05)',
            border: '1px solid #E2E8F0',
            padding: '24px',
            marginBottom: '24px'
          }}>
            <h2 style={{
              fontSize: '18px',
              fontWeight: '600',
              color: '#1E293B',
              marginBottom: '20px'
            }}>Client Details</h2>
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
              gap: '16px'
            }}>
              {dateAdded && (
                <div style={{
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: '12px'
                }}>
                  <Calendar size={20} style={{ color: '#94A3B8', flexShrink: 0, marginTop: '2px' }} />
                  <div>
                    <p style={{
                      fontSize: '12px',
                      color: '#94A3B8',
                      marginBottom: '4px'
                    }}>Date Added</p>
                    <p style={{
                      fontSize: '14px',
                      color: '#1E293B'
                    }}>{dateAdded}</p>
                  </div>
                </div>
              )}
              <div style={{
                display: 'flex',
                alignItems: 'flex-start',
                gap: '12px'
              }}>
                <FileText size={20} style={{ color: '#94A3B8', flexShrink: 0, marginTop: '2px' }} />
                <div>
                  <p style={{
                    fontSize: '12px',
                    color: '#94A3B8',
                    marginBottom: '4px'
                  }}>Active Projects</p>
                  <button
                    onClick={() => useAppStore.getState().navigateToProjectsFiltered(clientId)}
                    style={{
                      fontSize: '16px',
                      fontWeight: '600',
                      color: activeProjectsCount > 0 ? '#2563EB' : '#1E293B',
                      background: 'none',
                      border: 'none',
                      padding: 0,
                      cursor: activeProjectsCount > 0 ? 'pointer' : 'default',
                      textDecoration: activeProjectsCount > 0 ? 'underline' : 'none',
                      textAlign: 'left'
                    }}
                    disabled={activeProjectsCount === 0}
                    onMouseEnter={(e) => {
                      if (activeProjectsCount > 0) {
                        e.currentTarget.style.color = '#1D4ED8';
                      }
                    }}
                    onMouseLeave={(e) => {
                      if (activeProjectsCount > 0) {
                        e.currentTarget.style.color = '#2563EB';
                      }
                    }}
                  >
                    {activeProjectsCount}
                  </button>
                </div>
              </div>
              <div style={{
                display: 'flex',
                alignItems: 'flex-start',
                gap: '12px'
              }}>
                <FileText size={20} style={{ color: '#94A3B8', flexShrink: 0, marginTop: '2px' }} />
                <div>
                  <p style={{
                    fontSize: '12px',
                    color: '#94A3B8',
                    marginBottom: '4px'
                  }}>Active Permits</p>
                  <button
                    onClick={() => useAppStore.getState().navigateToPermitsFiltered(clientId)}
                    style={{
                      fontSize: '16px',
                      fontWeight: '600',
                      color: activePermitsCount > 0 ? '#2563EB' : '#1E293B',
                      background: 'none',
                      border: 'none',
                      padding: 0,
                      cursor: activePermitsCount > 0 ? 'pointer' : 'default',
                      textDecoration: activePermitsCount > 0 ? 'underline' : 'none',
                      textAlign: 'left'
                    }}
                    disabled={activePermitsCount === 0}
                    onMouseEnter={(e) => {
                      if (activePermitsCount > 0) {
                        e.currentTarget.style.color = '#1D4ED8';
                      }
                    }}
                    onMouseLeave={(e) => {
                      if (activePermitsCount > 0) {
                        e.currentTarget.style.color = '#2563EB';
                      }
                    }}
                  >
                    {activePermitsCount}
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Notes */}
          {notes && (
            <div style={{
              backgroundColor: '#FFFFFF',
              borderRadius: '12px',
              boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.05)',
              border: '1px solid #E2E8F0',
              padding: '24px',
              marginBottom: '24px'
            }}>
              <h2 style={{
                fontSize: '18px',
                fontWeight: '600',
                color: '#1E293B',
                marginBottom: '12px'
              }}>Notes</h2>
              <p style={{
                fontSize: '14px',
                color: '#475569',
                lineHeight: '1.6',
                whiteSpace: 'pre-wrap'
              }}>{notes}</p>
            </div>
          )}

          {/* All Fields (Debug/Admin View) */}
          <details style={{
            backgroundColor: '#F8FAFC',
            borderRadius: '12px',
            border: '1px solid #E2E8F0',
            padding: '24px'
          }}>
            <summary style={{
              fontSize: '14px',
              fontWeight: '500',
              color: '#64748B',
              cursor: 'pointer',
              transition: 'color 0.2s ease'
            }}
            onMouseEnter={(e) => e.currentTarget.style.color = '#1E293B'}
            onMouseLeave={(e) => e.currentTarget.style.color = '#64748B'}
            >
              View All Fields
            </summary>
            <div style={{
              marginTop: '16px',
              display: 'flex',
              flexDirection: 'column',
              gap: '8px'
            }}>
              {Object.entries(client).map(([key, value]) => (
                <div key={key} style={{
                  display: 'flex',
                  borderBottom: '1px solid #E2E8F0',
                  paddingBottom: '8px'
                }}>
                  <span style={{
                    fontSize: '13px',
                    fontWeight: '500',
                    color: '#64748B',
                    width: '33.333%',
                    flexShrink: 0
                  }}>{key}:</span>
                  <span style={{
                    fontSize: '13px',
                    color: '#1E293B',
                    width: '66.667%',
                    wordBreak: 'break-all'
                  }}>
                    {typeof value === 'object' && value !== null 
                      ? JSON.stringify(value, null, 2) 
                      : (value || '—')}
                  </span>
                </div>
              ))}
            </div>
          </details>
        </div>
      </div>
    </div>
  );
}
