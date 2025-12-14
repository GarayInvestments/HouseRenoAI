import { useState, useEffect, useMemo, useCallback } from 'react';
import { Search, Phone, Mail, MapPin, User, Loader2, AlertCircle, Plus, Edit2, Trash2 } from 'lucide-react';
import api from '../lib/api';
import useAppStore from '../stores/appStore';
import Modal from '../components/Modal';
import FormField from '../components/FormField';
import ConfirmDialog from '../components/ConfirmDialog';
import ErrorState from '../components/ErrorState';
import LoadingScreen from '../components/LoadingScreen';

export default function Clients() {
  // Clients page with card layout
  const [clients, setClients] = useState([]);
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const navigateToClient = useAppStore((state) => state.navigateToClient);

  // CRUD state
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingClient, setEditingClient] = useState(null);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [deletingClient, setDeletingClient] = useState(null);
  const [saving, setSaving] = useState(false);
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    phone: '',
    address: '',
    city: '',
    state: '',
    zip_code: '',
    client_type: 'Residential',
    status: 'Active',
  });

  useEffect(() => {
    fetchClients();
  }, []);

  // Stable fetch function - prevents unnecessary re-renders
  const fetchClients = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const [clientsData, projectsData] = await Promise.all([
        api.getClients(),
        api.getProjects()
      ]);
      setClients(Array.isArray(clientsData) ? clientsData : []);
      setProjects(Array.isArray(projectsData) ? projectsData : []);
    } catch {
      setError('Failed to load clients. Please try again.');
    } finally {
      setLoading(false);
    }
  }, []);

  const handleOpenCreate = () => {
    setEditingClient(null);
    setFormData({
      full_name: '',
      email: '',
      phone: '',
      address: '',
      city: '',
      state: '',
      zip_code: '',
      client_type: 'Residential',
      status: 'Active',
    });
    setIsModalOpen(true);
  };

  const handleOpenEdit = useCallback((client, e) => {
    e.stopPropagation(); // Prevent card click
    setEditingClient(client);
    setFormData({
      full_name: client['Full Name'] || client['Client Name'] || '',
      email: client['Email'] || '',
      phone: client['Phone'] || '',
      address: client['Address'] || '',
      city: client['City'] || '',
      state: client['State'] || '',
      zip_code: client['Zip'] || '',
      client_type: client['Client Type'] || 'Residential',
      status: client['Status'] || 'Active',
    });
    setIsModalOpen(true);
  }, []);

  const handleOpenDelete = useCallback((client, e) => {
    e.stopPropagation(); // Prevent card click
    setDeletingClient(client);
    setIsDeleteDialogOpen(true);
  }, []);

  const handleSubmit = useCallback(async (e) => {
    e.preventDefault();
    
    try {
      setSaving(true);
      
      if (editingClient) {
        const clientId = editingClient['Client ID'] || editingClient['ID'];
        await api.updateClient(clientId, formData);
      } else {
        await api.createClient(formData);
      }
      
      await fetchClients();
      setIsModalOpen(false);
      setEditingClient(null);
    } catch (err) {
      console.error('Failed to save client:', err);
      // Show error inline instead of blocking alert
      setError('Failed to save client. Please try again.');
    } finally {
      setSaving(false);
    }
  }, [editingClient, formData, fetchClients]);

  const handleDelete = useCallback(async () => {
    try {
      const clientId = deletingClient['Client ID'] || deletingClient['ID'];
      await api.deleteClient(clientId);
      await fetchClients();
      setIsDeleteDialogOpen(false);
      setDeletingClient(null);
    } catch (err) {
      console.error('Failed to delete client:', err);
      // Show error inline instead of blocking alert
      setError('Failed to delete client. Please try again.');
      setIsDeleteDialogOpen(false);
      setDeletingClient(null);
    }
  }, [deletingClient, fetchClients]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  // Memoize project counts - avoid recalculating on every render
  const projectCountsByClient = useMemo(() => {
    const counts = {};
    projects.forEach(project => {
      const clientId = project['Client ID'];
      if (clientId) {
        counts[clientId] = (counts[clientId] || 0) + 1;
      }
    });
    return counts;
  }, [projects]);

  // Memoize status counts - expensive computation only runs when projects change
  const statusCountsByClient = useMemo(() => {
    const statusMap = {};
    
    projects.forEach(project => {
      const clientId = project['Client ID'];
      if (!clientId) return;
      
      if (!statusMap[clientId]) {
        statusMap[clientId] = { active: 0, completed: 0, planning: 0, other: 0 };
      }
      
      const status = (project.Status || '').toLowerCase().trim();
      
      if (status === 'permit approved' || status === 'active') {
        statusMap[clientId].active++;
      } else if (status === 'completed' || status === 'final inspection complete') {
        statusMap[clientId].completed++;
      } else if (status === 'permit submitted' || status === 'planning') {
        statusMap[clientId].planning++;
      } else if (status === 'closed / archived' || status === 'inquiry received') {
        statusMap[clientId].other++;
      } else if (status) {
        statusMap[clientId].other++;
      }
    });
    
    return statusMap;
  }, [projects]);

  const getProjectCount = (clientId) => {
    return projectCountsByClient[clientId] || 0;
  };

  const getProjectStatusCounts = (clientId) => {
    return statusCountsByClient[clientId] || { active: 0, completed: 0, planning: 0, other: 0 };
  };

  // Memoize filtered clients - normalize search query once, filter only when dependencies change
  const filteredClients = useMemo(() => {
    if (!searchQuery) return clients;
    
    const query = searchQuery.toLowerCase(); // Normalize once
    
    return clients.filter((client) => {
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
  }, [clients, searchQuery]);

  if (loading) {
    return <LoadingScreen />;
  }

  if (error) {
    return (
      <div style={{ padding: '20px', backgroundColor: '#F8FAFC', minHeight: '100vh' }}>
        <ErrorState message={error} onRetry={fetchClients} fullScreen />
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
          marginBottom: '16px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'flex-start'
        }}>
          <div>
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
          
          {/* New Client Button */}
          <button
            onClick={handleOpenCreate}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '10px 16px',
              backgroundColor: '#2563EB',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              fontSize: '14px',
              fontWeight: '500',
              cursor: 'pointer',
              transition: 'all 0.2s'
            }}
            // CSS-only hover - no React state change
            onMouseOver={(e) => { e.currentTarget.style.backgroundColor = '#1D4ED8'; }}
            onMouseOut={(e) => { e.currentTarget.style.backgroundColor = '#2563EB'; }}
          >
            <Plus size={18} />
            New Client
          </button>
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
            // CSS-only focus effects - no state updates
            onFocus={(e) => {
              e.currentTarget.style.borderColor = '#2563EB';
              e.currentTarget.style.boxShadow = '0 0 0 3px rgba(37, 99, 235, 0.1)';
            }}
            onBlur={(e) => {
              e.currentTarget.style.borderColor = '#E2E8F0';
              e.currentTarget.style.boxShadow = 'none';
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
              const projectCount = getProjectCount(clientId);
              const statusCounts = getProjectStatusCounts(clientId);

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
                  // CSS-only hover - no state updates, prevents re-renders
                  onMouseOver={(e) => {
                    e.currentTarget.style.boxShadow = '0 10px 20px -5px rgba(0, 0, 0, 0.1)';
                    e.currentTarget.style.transform = 'translateY(-2px)';
                  }}
                  onMouseOut={(e) => {
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
                    
                    {/* Edit/Delete Buttons */}
                    <div style={{ display: 'flex', gap: '8px' }}>
                      <button
                        onClick={(e) => handleOpenEdit(client, e)}
                        style={{
                          padding: '8px',
                          backgroundColor: '#F1F5F9',
                          border: 'none',
                          borderRadius: '6px',
                          cursor: 'pointer',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          transition: 'all 0.2s'
                        }}
                        // CSS-only hover
                        onMouseOver={(e) => { e.currentTarget.style.backgroundColor = '#E2E8F0'; }}
                        onMouseOut={(e) => { e.currentTarget.style.backgroundColor = '#F1F5F9'; }}
                      >
                        <Edit2 size={16} style={{ color: '#475569' }} />
                      </button>
                      <button
                        onClick={(e) => handleOpenDelete(client, e)}
                        style={{
                          padding: '8px',
                          backgroundColor: '#FEE2E2',
                          border: 'none',
                          borderRadius: '6px',
                          cursor: 'pointer',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          transition: 'all 0.2s'
                        }}
                        // CSS-only hover
                        onMouseOver={(e) => { e.currentTarget.style.backgroundColor = '#FECACA'; }}
                        onMouseOut={(e) => { e.currentTarget.style.backgroundColor = '#FEE2E2'; }}
                      >
                        <Trash2 size={16} style={{ color: '#DC2626' }} />
                      </button>
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

                  {/* Projects Status Breakdown */}
                  <div style={{
                    paddingTop: '16px',
                    borderTop: '1px solid #F1F5F9'
                  }}>
                    {projectCount === 0 ? (
                      <span style={{
                        fontSize: '13px',
                        fontWeight: '500',
                        color: '#94A3B8'
                      }}>
                        No Projects
                      </span>
                    ) : (
                      <div style={{
                        display: 'flex',
                        flexWrap: 'wrap',
                        gap: '8px',
                        alignItems: 'center'
                      }}>
                        {statusCounts.active > 0 && (
                          <span style={{
                            fontSize: '12px',
                            fontWeight: '500',
                            color: '#2563EB',
                            backgroundColor: '#DBEAFE',
                            padding: '4px 10px',
                            borderRadius: '6px'
                          }}>
                            {statusCounts.active} Active
                          </span>
                        )}
                        {statusCounts.completed > 0 && (
                          <span style={{
                            fontSize: '12px',
                            fontWeight: '500',
                            color: '#059669',
                            backgroundColor: '#ECFDF5',
                            padding: '4px 10px',
                            borderRadius: '6px'
                          }}>
                            {statusCounts.completed} Completed
                          </span>
                        )}
                        {statusCounts.planning > 0 && (
                          <span style={{
                            fontSize: '12px',
                            fontWeight: '500',
                            color: '#D97706',
                            backgroundColor: '#FEF3C7',
                            padding: '4px 10px',
                            borderRadius: '6px'
                          }}>
                            {statusCounts.planning} Planning
                          </span>
                        )}
                        {statusCounts.other > 0 && (
                          <span style={{
                            fontSize: '12px',
                            fontWeight: '500',
                            color: '#6B7280',
                            backgroundColor: '#F3F4F6',
                            padding: '4px 10px',
                            borderRadius: '6px'
                          }}>
                            {statusCounts.other} Other
                          </span>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Create/Edit Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => !saving && setIsModalOpen(false)}
        title={editingClient ? 'Edit Client' : 'New Client'}
        size="md"
      >
        <form onSubmit={handleSubmit}>
          <FormField
            label="Full Name"
            name="full_name"
            value={formData.full_name}
            onChange={handleChange}
            required
            placeholder="John Doe"
          />

          <FormField
            label="Email"
            name="email"
            type="email"
            value={formData.email}
            onChange={handleChange}
            required
            placeholder="john@example.com"
          />

          <FormField
            label="Phone"
            name="phone"
            type="tel"
            value={formData.phone}
            onChange={handleChange}
            placeholder="(555) 123-4567"
          />

          <FormField
            label="Address"
            name="address"
            value={formData.address}
            onChange={handleChange}
            placeholder="123 Main St"
          />

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '16px' }}>
            <FormField
              label="City"
              name="city"
              value={formData.city}
              onChange={handleChange}
              placeholder="New York"
            />

            <FormField
              label="State"
              name="state"
              value={formData.state}
              onChange={handleChange}
              placeholder="NY"
            />

            <FormField
              label="Zip Code"
              name="zip_code"
              value={formData.zip_code}
              onChange={handleChange}
              placeholder="10001"
            />
          </div>

          <FormField
            label="Client Type"
            name="client_type"
            type="select"
            value={formData.client_type}
            onChange={handleChange}
            options={['Residential', 'Commercial']}
          />

          <FormField
            label="Status"
            name="status"
            type="select"
            value={formData.status}
            onChange={handleChange}
            options={['Active', 'Inactive', 'Lead']}
          />

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px', marginTop: '24px' }}>
            <button
              type="button"
              onClick={() => setIsModalOpen(false)}
              disabled={saving}
              style={{
                padding: '10px 20px',
                border: '1px solid #E2E8F0',
                borderRadius: '8px',
                backgroundColor: 'white',
                color: '#475569',
                fontSize: '14px',
                fontWeight: '500',
                cursor: 'pointer',
                transition: 'all 0.2s'
              }}
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={saving}
              style={{
                padding: '10px 20px',
                border: 'none',
                borderRadius: '8px',
                backgroundColor: '#2563EB',
                color: 'white',
                fontSize: '14px',
                fontWeight: '500',
                cursor: 'pointer',
                transition: 'all 0.2s',
                opacity: saving ? 0.7 : 1
              }}
            >
              {saving ? 'Saving...' : editingClient ? 'Update Client' : 'Create Client'}
            </button>
          </div>
        </form>
      </Modal>

      {/* Delete Confirmation */}
      <ConfirmDialog
        isOpen={isDeleteDialogOpen}
        onConfirm={handleDelete}
        onCancel={() => setIsDeleteDialogOpen(false)}
        title="Delete Client"
        message={`Are you sure you want to delete ${deletingClient?.['Full Name'] || deletingClient?.['Client Name'] || 'this client'}? This action cannot be undone.`}
        confirmText="Delete"
        cancelText="Cancel"
        type="danger"
      />
    </div>
  );
}
