import { useState, useEffect } from 'react';
import { Search, Phone, Mail, MapPin, User, Loader2 } from 'lucide-react';
import api from '../lib/api';
import useAppStore from '../stores/appStore';

export default function Clients() {
  // Clients page with card layout
  const [clients, setClients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const navigateToClient = useAppStore((state) => state.navigateToClient);

  useEffect(() => {
    fetchClients();
  }, []);

  const fetchClients = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getClients();
      setClients(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error('Error fetching clients:', err);
      setError('Failed to load clients. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const filteredClients = clients.filter((client) => {
    if (!searchQuery) return true;
    
    const query = searchQuery.toLowerCase();
    const clientName = (client['Full Name'] || client['Client Name'] || '').toLowerCase();
    const email = (client['Email'] || '').toLowerCase();
    const phone = (client['Phone'] || '').toLowerCase();
    const address = (client['Address'] || '').toLowerCase();
    
    return (
      clientName.includes(query) ||
      email.includes(query) ||
      phone.includes(query) ||
      address.includes(query)
    );
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <Loader2 className="h-12 w-12 animate-spin text-blue-500 mx-auto mb-4" />
          <p className="text-gray-600">Loading clients...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <p className="text-red-600 mb-4">{error}</p>
          <button
            onClick={fetchClients}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Retry
          </button>
        </div>
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
          marginBottom: '16px'
        }}>
          <h1 style={{
            fontSize: '24px',
            fontWeight: '600',
            color: '#1E293B',
            marginBottom: '4px'
          }}>Clients</h1>
          <p style={{
            color: '#64748B',
            fontSize: '14px'
          }}>
            {filteredClients.length} {filteredClients.length === 1 ? 'client' : 'clients'}
          </p>
        </div>

        {/* Search Bar */}
        <div style={{ position: 'relative' }}>
          <Search style={{
            position: 'absolute',
            left: '12px',
            top: '50%',
            transform: 'translateY(-50%)',
            color: '#94A3B8',
            width: '20px',
            height: '20px'
          }} />
          <input
            type="text"
            placeholder="Search by name, email, phone, or address..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{
              width: '100%',
              paddingLeft: '44px',
              paddingRight: '16px',
              paddingTop: '10px',
              paddingBottom: '10px',
              border: '1px solid #E2E8F0',
              borderRadius: '10px',
              fontSize: '14px',
              outline: 'none',
              transition: 'all 0.2s ease'
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
      </div>

      {/* Content */}
      <div style={{
        flex: 1,
        overflowY: 'auto',
        padding: '32px'
      }}>
        {filteredClients.length === 0 ? (
          <div style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            height: '400px',
            gap: '16px'
          }}>
            <User size={64} style={{ color: '#CBD5E1' }} />
            <p style={{ color: '#64748B', fontSize: '16px' }}>
              {searchQuery ? 'No clients match your search.' : 'No clients found.'}
            </p>
          </div>
        ) : (
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(380px, 1fr))',
            gap: '24px',
            maxWidth: '1400px',
            margin: '0 auto',
            paddingBottom: '80px'
          }}>
            {filteredClients.map((client, index) => {
              const clientId = client['Client ID'] || client['ID'] || index;
              const clientName = client['Full Name'] || client['Client Name'] || 'Unnamed Client';
              const email = client['Email'] || '';
              const phone = client['Phone'] || '';
              const address = client['Address'] || '';
              const city = client['City'] || '';
              const state = client['State'] || '';
              const projectCount = client['Active Projects'] || client['Projects'] || '0';

              return (
                <div
                  key={clientId}
                  onClick={() => navigateToClient(clientId)}
                  style={{
                    backgroundColor: '#FFFFFF',
                    borderRadius: '12px',
                    padding: '24px',
                    border: '1px solid #E2E8F0',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease',
                    boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.05)'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.boxShadow = '0 10px 20px -5px rgba(0, 0, 0, 0.1)';
                    e.currentTarget.style.transform = 'translateY(-2px)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.boxShadow = '0 1px 3px 0 rgba(0, 0, 0, 0.05)';
                    e.currentTarget.style.transform = 'translateY(0)';
                  }}
                >
                  {/* Client Header */}
                  <div style={{
                    display: 'flex',
                    alignItems: 'flex-start',
                    justifyContent: 'space-between',
                    marginBottom: '16px'
                  }}>
                    <div style={{
                      width: '48px',
                      height: '48px',
                      borderRadius: '10px',
                      background: 'linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      flexShrink: 0,
                      boxShadow: '0 4px 6px -1px rgba(37, 99, 235, 0.3)'
                    }}>
                      <User size={24} style={{ color: '#FFFFFF' }} />
                    </div>
                  </div>

                  {/* Client Name */}
                  <h3 style={{
                    fontSize: '17px',
                    fontWeight: '600',
                    color: '#1E293B',
                    marginBottom: '4px',
                    lineHeight: '1.4'
                  }}>{clientName}</h3>
                  <p style={{
                    fontSize: '12px',
                    color: '#94A3B8',
                    marginBottom: '16px'
                  }}>ID: {clientId}</p>

                  {/* Contact Info */}
                  <div style={{
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '8px',
                    marginBottom: '16px'
                  }}>
                    {email && (
                      <div style={{
                        display: 'flex',
                        alignItems: 'flex-start',
                        gap: '8px'
                      }}>
                        <Mail size={16} style={{ color: '#94A3B8', flexShrink: 0, marginTop: '2px' }} />
                        <span style={{
                          fontSize: '13px',
                          color: '#475569',
                          wordBreak: 'break-all'
                        }}>{email}</span>
                      </div>
                    )}
                    {phone && (
                      <div style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px'
                      }}>
                        <Phone size={16} style={{ color: '#94A3B8', flexShrink: 0 }} />
                        <span style={{
                          fontSize: '13px',
                          color: '#475569'
                        }}>{phone}</span>
                      </div>
                    )}
                    {(address || city || state) && (
                      <div style={{
                        display: 'flex',
                        alignItems: 'flex-start',
                        gap: '8px'
                      }}>
                        <MapPin size={16} style={{ color: '#94A3B8', flexShrink: 0, marginTop: '2px' }} />
                        <div style={{ fontSize: '13px', color: '#475569' }}>
                          {address && <div>{address}</div>}
                          {(city || state) && (
                            <div style={{ fontSize: '12px', color: '#94A3B8' }}>
                              {city}{city && state && ', '}{state}
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Projects Count */}
                  <div style={{
                    paddingTop: '16px',
                    borderTop: '1px solid #F1F5F9'
                  }}>
                    <span style={{
                      fontSize: '13px',
                      fontWeight: '500',
                      color: '#475569'
                    }}>
                      {projectCount} Active {projectCount === '1' ? 'Project' : 'Projects'}
                    </span>
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
