import { useState, useEffect } from 'react';
import { ArrowLeft, User, Mail, Phone, MapPin, Calendar, FileText, Loader2 } from 'lucide-react';
import api from '../lib/api';
import useAppStore from '../stores/appStore';
import { useProjectsStore } from '../stores/projectsStore';
import { usePermitsStore } from '../stores/permitsStore';
import LoadingScreen from '../components/LoadingScreen';
import ErrorState from '../components/ErrorState';
import { CLIENT_STATUS_OPTIONS, formatEnumLabel } from '../constants/enums';

export default function ClientDetails() {
  const [client, setClient] = useState(null);
  const [projects, setProjects] = useState([]);
  const [permits, setPermits] = useState([]);
  const [invoices, setInvoices] = useState([]);
  const [payments, setPayments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [editedClient, setEditedClient] = useState(null);
  const [isSaving, setIsSaving] = useState(false);
  const currentClientId = useAppStore((state) => state.currentClientId);
  const navigateToClients = useAppStore((state) => state.navigateToClients);
  const setCurrentView = useAppStore((state) => state.setCurrentView);
  const getProjectsByClient = useProjectsStore((state) => state.getProjectsByClient);
  const getPermitsByClient = usePermitsStore((state) => state.getPermitsByClient);

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
        
        // Fetch client, projects, permits, invoices, and payments in parallel
        const [clientData, projectsData, permitsData, invoicesData, paymentsData] = await Promise.all([
          api.getClient(currentClientId),
          api.getProjects(),
          api.getPermits(),
          api.getInvoices(),
          api.getPayments()
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
        
        // Filter invoices for this client
        const clientInvoices = Array.isArray(invoicesData)
          ? invoicesData.filter(inv => inv.client_id === currentClientId)
          : [];
        setInvoices(clientInvoices);
        
        // Filter payments for this client
        const clientPayments = Array.isArray(paymentsData)
          ? paymentsData.filter(pmt => pmt.client_id === currentClientId)
          : [];
        setPayments(clientPayments);
        
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

  const handleSave = async () => {
    try {
      setIsSaving(true);
      
      // Map frontend display field names to backend database column names
      const fieldMapping = {
        'Client Name': 'full_name',
        'Company Name': 'company_name',
        'Email': 'email',
        'Phone': 'phone',
        'Preferred Contact Method': 'preferred_contact',
        'Address': 'address',
        'City': 'city',
        'State': 'state',
        'ZIP': 'zip_code'
      };
      
      // Convert editedClient keys from display names to database column names
      const mappedData = {};
      Object.keys(editedClient).forEach(key => {
        const dbFieldName = fieldMapping[key] || key;
        mappedData[dbFieldName] = editedClient[key];
      });
      
      await api.updateClient(currentClientId, mappedData);
      setClient({ ...client, ...editedClient });
      setIsEditing(false);
      setEditedClient(null);
    } catch (error) {
      console.error('Failed to save client:', error);
      alert('Failed to save changes. Please try again.');
    } finally {
      setIsSaving(false);
    }
  };

  const handleCancel = () => {
    setIsEditing(false);
    setEditedClient(null);
  };

  const handleEditChange = (field, value) => {
    setEditedClient(prev => ({ ...prev, [field]: value }));
  };

  const getClientStatusColor = (status) => {
    switch (status?.toUpperCase()) {
      case 'ACTIVE':
        return { bg: '#DBEAFE', text: '#2563EB', border: '#93C5FD' };
      case 'COMPLETED':
        return { bg: '#ECFDF5', text: '#059669', border: '#A7F3D0' };
      case 'INTAKE':
        return { bg: '#FEF3C7', text: '#D97706', border: '#FCD34D' };
      case 'ON_HOLD':
        return { bg: '#FEF2F2', text: '#DC2626', border: '#FECACA' };
      case 'ARCHIVED':
        return { bg: '#F3F4F6', text: '#6B7280', border: '#D1D5DB' };
      default:
        return { bg: '#F3F4F6', text: '#6B7280', border: '#D1D5DB' };
    }
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
    return <LoadingScreen />;
  }

  if (error || !client) {
    return (
      <div style={{ padding: '20px', backgroundColor: '#F8FAFC', minHeight: '100vh' }}>
        <ErrorState 
          message={error || 'Client not found'} 
          onRetry={handleRetry} 
          fullScreen 
        />
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
      {/* Back Button & Edit Controls */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '16px 32px' }}>
        <button
          onClick={handleBackClick}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            color: '#64748B',
            background: 'none',
            border: 'none',
            padding: '0',
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

        {!isEditing ? (
          <button
            onClick={() => {
              setIsEditing(true);
              setEditedClient(client);
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
            Edit Client
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
                {isEditing ? (
                  <>
                    <input
                      type="text"
                      value={editedClient?.['Full Name'] || editedClient?.['Client Name'] || ''}
                      onChange={(e) => {
                        handleEditChange('Full Name', e.target.value);
                        handleEditChange('Client Name', e.target.value);
                      }}
                      style={{
                        fontSize: '28px',
                        fontWeight: '600',
                        color: '#1E293B',
                        marginBottom: '8px',
                        width: '100%',
                        padding: '8px',
                        border: '2px solid #2563EB',
                        borderRadius: '8px',
                        outline: 'none'
                      }}
                      placeholder="Client Name"
                    />
                    <input
                      type="text"
                      value={editedClient?.['Company Name'] || ''}
                      onChange={(e) => handleEditChange('Company Name', e.target.value)}
                      style={{
                        fontSize: '16px',
                        color: '#64748B',
                        marginBottom: '4px',
                        width: '100%',
                        padding: '6px',
                        border: '1px solid #D1D5DB',
                        borderRadius: '6px',
                        outline: 'none'
                      }}
                      placeholder="Company Name (optional)"
                    />
                  </>
                ) : (
                  <>
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
                  </>
                )}
                <p style={{
                  fontSize: '13px',
                  color: '#94A3B8',
                  marginBottom: '8px'
                }}>Client ID: {clientId}</p>
                {/* Client Status */}
                {isEditing ? (
                  <select
                    value={editedClient?.status || client?.status || ''}
                    onChange={(e) => handleEditChange('status', e.target.value)}
                    style={{
                      padding: '6px 12px',
                      borderRadius: '6px',
                      fontSize: '13px',
                      fontWeight: '500',
                      border: '2px solid #2563EB',
                      outline: 'none',
                      backgroundColor: 'white'
                    }}
                  >
                    <option value="">Select status...</option>
                    {CLIENT_STATUS_OPTIONS.map(opt => (
                      <option key={opt.value} value={opt.value}>{opt.label}</option>
                    ))}
                  </select>
                ) : (
                  client?.status && (
                    <span style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      padding: '4px 12px',
                      borderRadius: '6px',
                      fontSize: '13px',
                      fontWeight: '500',
                      backgroundColor: getClientStatusColor(client.status).bg,
                      color: getClientStatusColor(client.status).text,
                      border: `1px solid ${getClientStatusColor(client.status).border}`
                    }}>
                      {formatEnumLabel(client.status)}
                    </span>
                  )
                )}
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
              <div style={{
                display: 'flex',
                alignItems: 'flex-start',
                gap: '12px'
              }}>
                <Mail size={20} style={{ color: '#94A3B8', flexShrink: 0, marginTop: '2px' }} />
                <div style={{ flex: 1 }}>
                  <p style={{
                    fontSize: '12px',
                    color: '#94A3B8',
                    marginBottom: '4px'
                  }}>Email</p>
                  {isEditing ? (
                    <input
                      type="email"
                      value={editedClient?.Email || ''}
                      onChange={(e) => handleEditChange('Email', e.target.value)}
                      style={{
                        width: '100%',
                        padding: '8px 12px',
                        border: '1px solid #D1D5DB',
                        borderRadius: '8px',
                        fontSize: '14px',
                        outline: 'none'
                      }}
                    />
                  ) : (
                    <a href={`mailto:${email}`} style={{
                      color: '#2563EB',
                      fontSize: '14px',
                      textDecoration: 'none',
                      wordBreak: 'break-all'
                    }}
                    onMouseEnter={(e) => e.currentTarget.style.textDecoration = 'underline'}
                    onMouseLeave={(e) => e.currentTarget.style.textDecoration = 'none'}
                    >
                      {email || 'Not set'}
                    </a>
                  )}
                </div>
              </div>
              <div style={{
                display: 'flex',
                alignItems: 'flex-start',
                gap: '12px'
              }}>
                <Phone size={20} style={{ color: '#94A3B8', flexShrink: 0, marginTop: '2px' }} />
                <div style={{ flex: 1 }}>
                  <p style={{
                    fontSize: '12px',
                    color: '#94A3B8',
                    marginBottom: '4px'
                  }}>Phone</p>
                  {isEditing ? (
                    <input
                      type="tel"
                      value={editedClient?.Phone || ''}
                      onChange={(e) => handleEditChange('Phone', e.target.value)}
                      style={{
                        width: '100%',
                        padding: '8px 12px',
                        border: '1px solid #D1D5DB',
                        borderRadius: '8px',
                        fontSize: '14px',
                        outline: 'none'
                      }}
                    />
                  ) : (
                    <a href={`tel:${phone}`} style={{
                      color: '#2563EB',
                      fontSize: '14px',
                      textDecoration: 'none'
                    }}
                    onMouseEnter={(e) => e.currentTarget.style.textDecoration = 'underline'}
                    onMouseLeave={(e) => e.currentTarget.style.textDecoration = 'none'}
                    >
                      {phone || 'Not set'}
                    </a>
                  )}
                </div>
              </div>
              <div style={{
                display: 'flex',
                alignItems: 'flex-start',
                gap: '12px'
              }}>
                <FileText size={20} style={{ color: '#94A3B8', flexShrink: 0, marginTop: '2px' }} />
                <div style={{ flex: 1 }}>
                  <p style={{
                    fontSize: '12px',
                    color: '#94A3B8',
                    marginBottom: '4px'
                  }}>Preferred Contact Method</p>
                  {isEditing ? (
                    <select
                      value={editedClient?.['Preferred Contact Method'] || ''}
                      onChange={(e) => handleEditChange('Preferred Contact Method', e.target.value)}
                      style={{
                        width: '100%',
                        padding: '8px 12px',
                        border: '1px solid #D1D5DB',
                        borderRadius: '8px',
                        fontSize: '14px',
                        outline: 'none'
                      }}
                    >
                      <option value="">Select method...</option>
                      <option value="Email">Email</option>
                      <option value="Phone">Phone</option>
                      <option value="Text">Text</option>
                    </select>
                  ) : (
                    <p style={{
                      fontSize: '14px',
                      color: '#1E293B'
                    }}>{preferredContact || 'Not set'}</p>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Address Information */}
          {(address || city || state || zip || isEditing) && (
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
              {isEditing ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  <input
                    type="text"
                    value={editedClient?.Address || ''}
                    onChange={(e) => handleEditChange('Address', e.target.value)}
                    style={{
                      width: '100%',
                      padding: '8px 12px',
                      border: '1px solid #D1D5DB',
                      borderRadius: '8px',
                      fontSize: '14px',
                      outline: 'none'
                    }}
                    placeholder="Street Address"
                  />
                  <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr 1fr', gap: '12px' }}>
                    <input
                      type="text"
                      value={editedClient?.City || ''}
                      onChange={(e) => handleEditChange('City', e.target.value)}
                      style={{
                        padding: '8px 12px',
                        border: '1px solid #D1D5DB',
                        borderRadius: '8px',
                        fontSize: '14px',
                        outline: 'none'
                      }}
                      placeholder="City"
                    />
                    <input
                      type="text"
                      value={editedClient?.State || ''}
                      onChange={(e) => handleEditChange('State', e.target.value)}
                      style={{
                        padding: '8px 12px',
                        border: '1px solid #D1D5DB',
                        borderRadius: '8px',
                        fontSize: '14px',
                        outline: 'none'
                      }}
                      placeholder="State"
                    />
                    <input
                      type="text"
                      value={editedClient?.ZIP || editedClient?.['Zip Code'] || ''}
                      onChange={(e) => {
                        handleEditChange('ZIP', e.target.value);
                        handleEditChange('Zip Code', e.target.value);
                      }}
                      style={{
                        padding: '8px 12px',
                        border: '1px solid #D1D5DB',
                        borderRadius: '8px',
                        fontSize: '14px',
                        outline: 'none'
                      }}
                      placeholder="ZIP"
                    />
                  </div>
                </div>
              ) : (
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
              )}
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
              gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))',
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
                    onClick={() => setCurrentView('projects')}
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
                    onClick={() => setCurrentView('permits')}
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

          {/* Financial Summary */}
          {(invoices.length > 0 || payments.length > 0) && (
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
              }}>Financial Summary</h2>
              
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
                gap: '24px'
              }}>
                {/* Invoices */}
                {invoices.length > 0 && (
                  <div>
                    <h3 style={{
                      fontSize: '14px',
                      fontWeight: '600',
                      color: '#64748B',
                      marginBottom: '12px',
                      textTransform: 'uppercase',
                      letterSpacing: '0.05em'
                    }}>Invoices</h3>
                    <div style={{
                      display: 'flex',
                      flexDirection: 'column',
                      gap: '8px'
                    }}>
                      {invoices.map(invoice => (
                        <div key={invoice.invoice_id} style={{
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center',
                          padding: '12px',
                          backgroundColor: '#F8FAFC',
                          borderRadius: '8px',
                          border: '1px solid #E2E8F0'
                        }}>
                          <div>
                            <div style={{
                              fontSize: '14px',
                              fontWeight: '500',
                              color: '#1E293B',
                              marginBottom: '4px'
                            }}>{invoice.invoice_number}</div>
                            <div style={{
                              fontSize: '12px',
                              color: '#64748B'
                            }}>
                              {invoice.invoice_date ? new Date(invoice.invoice_date).toLocaleDateString() : 'No date'}
                            </div>
                          </div>
                          <div style={{
                            display: 'flex',
                            flexDirection: 'column',
                            alignItems: 'flex-end',
                            gap: '4px'
                          }}>
                            <div style={{
                              fontSize: '16px',
                              fontWeight: '600',
                              color: '#1E293B'
                            }}>
                              ${Number(invoice.total_amount || 0).toFixed(2)}
                            </div>
                            <div style={{
                              fontSize: '11px',
                              padding: '2px 8px',
                              borderRadius: '4px',
                              backgroundColor: invoice.status === 'PAID' ? '#DCFCE7' : invoice.status === 'SENT' ? '#FEF3C7' : '#F1F5F9',
                              color: invoice.status === 'PAID' ? '#166534' : invoice.status === 'SENT' ? '#92400E' : '#475569',
                              fontWeight: '500'
                            }}>
                              {invoice.status || 'DRAFT'}
                            </div>
                          </div>
                        </div>
                      ))}
                      <div style={{
                        marginTop: '8px',
                        padding: '12px',
                        backgroundColor: '#EFF6FF',
                        borderRadius: '8px',
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        fontWeight: '600'
                      }}>
                        <span style={{ color: '#1E40AF' }}>Total Invoiced</span>
                        <span style={{ color: '#1E40AF', fontSize: '18px' }}>
                          ${invoices.reduce((sum, inv) => sum + Number(inv.total_amount || 0), 0).toFixed(2)}
                        </span>
                      </div>
                    </div>
                  </div>
                )}

                {/* Payments */}
                {payments.length > 0 && (
                  <div>
                    <h3 style={{
                      fontSize: '14px',
                      fontWeight: '600',
                      color: '#64748B',
                      marginBottom: '12px',
                      textTransform: 'uppercase',
                      letterSpacing: '0.05em'
                    }}>Payments Received</h3>
                    <div style={{
                      display: 'flex',
                      flexDirection: 'column',
                      gap: '8px'
                    }}>
                      {payments.map(payment => (
                        <div key={payment.payment_id} style={{
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center',
                          padding: '12px',
                          backgroundColor: '#F8FAFC',
                          borderRadius: '8px',
                          border: '1px solid #E2E8F0'
                        }}>
                          <div>
                            <div style={{
                              fontSize: '14px',
                              fontWeight: '500',
                              color: '#1E293B',
                              marginBottom: '4px'
                            }}>{payment.payment_method || 'Payment'}</div>
                            <div style={{
                              fontSize: '12px',
                              color: '#64748B'
                            }}>
                              {payment.payment_date ? new Date(payment.payment_date).toLocaleDateString() : 'No date'}
                            </div>
                          </div>
                          <div style={{
                            display: 'flex',
                            flexDirection: 'column',
                            alignItems: 'flex-end',
                            gap: '4px'
                          }}>
                            <div style={{
                              fontSize: '16px',
                              fontWeight: '600',
                              color: '#059669'
                            }}>
                              ${Number(payment.amount || 0).toFixed(2)}
                            </div>
                            <div style={{
                              fontSize: '11px',
                              padding: '2px 8px',
                              borderRadius: '4px',
                              backgroundColor: payment.status === 'POSTED' ? '#DCFCE7' : '#FEF3C7',
                              color: payment.status === 'POSTED' ? '#166534' : '#92400E',
                              fontWeight: '500'
                            }}>
                              {payment.status || 'PENDING'}
                            </div>
                          </div>
                        </div>
                      ))}
                      <div style={{
                        marginTop: '8px',
                        padding: '12px',
                        backgroundColor: '#DCFCE7',
                        borderRadius: '8px',
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        fontWeight: '600'
                      }}>
                        <span style={{ color: '#166534' }}>Total Paid</span>
                        <span style={{ color: '#166534', fontSize: '18px' }}>
                          ${payments.reduce((sum, pmt) => sum + Number(pmt.amount || 0), 0).toFixed(2)}
                        </span>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Outstanding Balance */}
              {invoices.length > 0 && payments.length > 0 && (
                <div style={{
                  marginTop: '24px',
                  padding: '16px',
                  backgroundColor: '#FEF3C7',
                  borderRadius: '8px',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  border: '2px solid #F59E0B'
                }}>
                  <span style={{ fontSize: '16px', fontWeight: '600', color: '#92400E' }}>
                    Outstanding Balance
                  </span>
                  <span style={{ fontSize: '24px', fontWeight: '700', color: '#92400E' }}>
                    ${
                      (
                        invoices.reduce((sum, inv) => sum + Number(inv.total_amount || 0), 0) -
                        payments.reduce((sum, pmt) => sum + Number(pmt.amount || 0), 0)
                      ).toFixed(2)
                    }
                  </span>
                </div>
              )}
            </div>
          )}

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
