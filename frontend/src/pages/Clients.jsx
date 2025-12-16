import { useState, useEffect, useMemo, useCallback } from 'react';
import { Search, Phone, Mail, MapPin, User, Plus, Edit2, Trash2 } from 'lucide-react';
import api from '../lib/api';
import useAppStore from '../stores/appStore';
import Modal from '../components/Modal';
import FormField from '../components/FormField';
import ConfirmDialog from '../components/ConfirmDialog';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import LoadingState from '@/components/app/LoadingState';
import EmptyState from '@/components/app/EmptyState';

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
    return <LoadingState message="Loading clients..." />;
  }

  if (error) {
    return (
      <EmptyState
        title="Failed to load clients"
        description={error}
        action={
          <Button onClick={fetchClients}>
            Retry
          </Button>
        }
      />
    );
  }

  return (
    <div className="flex flex-col h-full bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-8 py-6">
        <div className="mb-4 flex justify-between items-start">
          <div>
            <h1 className="text-2xl font-semibold text-gray-900 mb-1">Clients</h1>
            <p className="text-gray-600 text-sm">
              {filteredClients.length} {filteredClients.length === 1 ? 'client' : 'clients'}
            </p>
          </div>
          
          <Button onClick={handleOpenCreate}>
            <Plus size={18} />
            New Client
          </Button>
        </div>

        {/* Search Bar */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" size={20} />
          <input
            type="text"
            placeholder="Search by name, email, phone, or address..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-11 pr-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:border-blue-600 focus:ring-4 focus:ring-blue-600/10 transition-all"
          />
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-8">
        {filteredClients.length === 0 ? (
          <EmptyState
            icon={User}
            title={searchQuery ? 'No clients match your search' : 'No clients found'}
            description={searchQuery ? 'Try adjusting your search terms' : 'Create your first client to get started'}
          />
        ) : (
          <div className="grid grid-cols-[repeat(auto-fill,minmax(320px,1fr))] gap-6 max-w-[1400px] mx-auto pb-20">
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
                <Card
                  key={clientId}
                  onClick={() => navigateToClient(clientId)}
                  className="cursor-pointer transition-all hover:shadow-lg hover:-translate-y-0.5"
                >
                  <CardContent className="p-6">
                    {/* Client Header */}
                    <div className="flex items-start justify-between mb-4">
                      <div className="w-12 h-12 rounded-lg bg-linear-to-br from-blue-600 to-blue-700 flex items-center justify-center shrink-0 shadow-md shadow-blue-600/30">
                        <User size={24} className="text-white" />
                      </div>
                      
                      {/* Edit/Delete Buttons */}
                      <div className="flex gap-2">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={(e) => handleOpenEdit(client, e)}
                          className="p-2"
                        >
                          <Edit2 size={16} />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={(e) => handleOpenDelete(client, e)}
                          className="p-2 hover:bg-red-50 hover:text-red-600"
                        >
                          <Trash2 size={16} />
                        </Button>
                      </div>
                    </div>

                    {/* Client Name */}
                    <h3 className="text-[17px] font-semibold text-gray-900 mb-1 leading-snug">
                      {clientName}
                    </h3>
                    <p className="text-xs text-gray-500 mb-4">ID: {clientId}</p>

                    {/* Contact Info */}
                    <div className="flex flex-col gap-2 mb-4">
                      {email && (
                        <div className="flex items-start gap-2">
                          <Mail size={16} className="text-gray-500 shrink-0 mt-0.5" />
                          <span className="text-[13px] text-gray-700 break-all">{email}</span>
                        </div>
                      )}
                      {phone && (
                        <div className="flex items-center gap-2">
                          <Phone size={16} className="text-gray-500 shrink-0" />
                          <span className="text-[13px] text-gray-700">{phone}</span>
                        </div>
                      )}
                      {(address || city || state) && (
                        <div className="flex items-start gap-2">
                          <MapPin size={16} className="text-gray-500 shrink-0 mt-0.5" />
                          <div className="text-[13px] text-gray-700">
                            {address && <div>{address}</div>}
                            {(city || state) && (
                              <div className="text-xs text-gray-500">
                                {city}{city && state && ', '}{state}
                              </div>
                            )}
                          </div>
                        </div>
                      )}
                    </div>

                    {/* Projects Status Breakdown */}
                    <div className="pt-4 border-t border-gray-100">
                      {projectCount === 0 ? (
                        <span className="text-[13px] font-medium text-gray-500">
                          No Projects
                        </span>
                      ) : (
                        <div className="flex flex-wrap gap-2 items-center">
                          {statusCounts.active > 0 && (
                            <Badge variant="info" className="text-xs">
                              {statusCounts.active} Active
                            </Badge>
                          )}
                          {statusCounts.completed > 0 && (
                            <Badge variant="success" className="text-xs">
                              {statusCounts.completed} Completed
                            </Badge>
                          )}
                          {statusCounts.planning > 0 && (
                            <Badge variant="warning" className="text-xs">
                              {statusCounts.planning} Planning
                            </Badge>
                          )}
                          {statusCounts.other > 0 && (
                            <Badge variant="default" className="text-xs">
                              {statusCounts.other} Other
                            </Badge>
                          )}
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
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
