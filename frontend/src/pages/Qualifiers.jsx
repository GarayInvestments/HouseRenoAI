import { UserCheck, Plus, Search, FileText, Building2, Loader2, AlertCircle, XCircle } from 'lucide-react';
import { useState, useEffect, useMemo } from 'react';
import api from '../lib/api';
import { useAppStore } from '../stores/appStore';
import LoadingScreen from '../components/LoadingScreen';
import ErrorState from '../components/ErrorState';

export default function Qualifiers() {
  const [qualifiers, setQualifiers] = useState([]);
  const [businesses, setBusinesses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showAssignModal, setShowAssignModal] = useState(false);
  const [selectedQualifier, setSelectedQualifier] = useState(null);
  const [isSaving, setIsSaving] = useState(false);
  const [saveError, setSaveError] = useState(null);
  const [endingAssignment, setEndingAssignment] = useState(null);
  const [confirmEndDialog, setConfirmEndDialog] = useState(null); // { qualifierId, businessId, businessName }

  useEffect(() => {
    fetchData();
    window.history.replaceState({ page: 'qualifiers' }, '');
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      const [qualifiersResponse, businessesResponse] = await Promise.all([
        api.getQualifiers(),
        api.request('/licensed-businesses')
      ]);
      setQualifiers(Array.isArray(qualifiersResponse) ? qualifiersResponse : []);
      setBusinesses(Array.isArray(businessesResponse) ? businessesResponse : []);
    } catch (err) {
      setError('Failed to load qualifiers. Please try again.');
      console.error('Error fetching data:', err);
    } finally {
      setLoading(false);
    }
  };

  const filteredQualifiers = useMemo(() => {
    if (!searchTerm) return qualifiers;
    return qualifiers.filter(qualifier =>
      qualifier.full_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      qualifier.qualifier_license_number?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      qualifier.qualifier_id?.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [qualifiers, searchTerm]);

  const handleCreateQualifier = async (formData) => {
    try {
      setIsSaving(true);
      setSaveError(null);
      
      const response = await api.request('/qualifiers', { method: 'POST', body: formData });
      
      setQualifiers([...qualifiers, response]);
      setShowCreateModal(false);
    } catch (err) {
      setSaveError(err.response?.data?.detail || 'Failed to create qualifier. Please try again.');
      console.error('Error creating qualifier:', err);
    } finally {
      setIsSaving(false);
    }
  };

  const handleAssignQualifier = async (businessId) => {
    try {
      setIsSaving(true);
      setSaveError(null);
      
      const requestBody = {
        licensed_business_id: businessId,
        qualifier_id: selectedQualifier.id,
        start_date: new Date().toISOString().split('T')[0],
        is_primary: true
      };
      
      console.log('[ASSIGN] Starting assignment:', {
        url: `/qualifiers/${selectedQualifier.id}/assign`,
        body: requestBody
      });
      
      const result = await api.request(`/qualifiers/${selectedQualifier.id}/assign`, {
        method: 'POST',
        body: requestBody
      });
      
      console.log('[ASSIGN] Assignment successful:', result);
      
      // Refresh data to show updated assignments
      await fetchData();
      setShowAssignModal(false);
      setSelectedQualifier(null);
    } catch (err) {
      setSaveError(err.response?.data?.detail || 'Failed to assign qualifier. Please check capacity limits.');
      console.error('Error assigning qualifier:', err);
    } finally {
      setIsSaving(false);
    }
  };

  const handleEndAssignment = async (qualifierId, businessId, businessName) => {
    setConfirmEndDialog({ qualifierId, businessId, businessName });
  };

  const confirmEndAssignment = async () => {
    const { qualifierId, businessId } = confirmEndDialog;

    try {
      setEndingAssignment(businessId);
      setConfirmEndDialog(null);
      
      await api.request(`/qualifiers/${qualifierId}/assignments/${businessId}/end`, {
        method: 'PUT'
      });
      
      // Refresh data to show updated assignments
      await fetchData();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to end assignment. Please try again.');
      console.error('Error ending assignment:', err);
    } finally {
      setEndingAssignment(null);
    }
  };

  const getCapacityBadge = (qualifier) => {
    const count = qualifier.assigned_businesses?.length || 0;
    const max = 2;
    
    if (count >= max) {
      return (
        <span className="px-3 py-1 text-sm font-bold bg-red-100 text-red-700 rounded-full">
          {count}/{max} (FULL)
        </span>
      );
    } else if (count === 1) {
      return (
        <span className="px-3 py-1 text-sm font-bold bg-yellow-100 text-yellow-700 rounded-full">
          {count}/{max}
        </span>
      );
    } else {
      return (
        <span className="px-3 py-1 text-sm font-bold bg-green-100 text-green-700 rounded-full">
          {count}/{max}
        </span>
      );
    }
  };

  if (loading) return <LoadingScreen />;
  if (error) return <ErrorState message={error} onRetry={fetchData} />;

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Qualifiers</h1>
            <p className="text-gray-600 mt-1">Manage licensed qualifiers and business assignments</p>
          </div>
          <button
            onClick={() => setShowCreateModal(true)}
            className="flex items-center px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
          >
            <Plus className="w-5 h-5 mr-2" />
            Add Qualifier
          </button>
        </div>
      </div>

      {/* Search Bar */}
      <div className="mb-6">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
          <input
            type="text"
            placeholder="Search by name, license number, or qualifier ID..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Qualifiers</p>
              <p className="text-2xl font-bold text-gray-900">{qualifiers.length}</p>
            </div>
            <UserCheck className="w-8 h-8 text-blue-500" />
          </div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">At Capacity (2/2)</p>
              <p className="text-2xl font-bold text-red-600">
                {qualifiers.filter(q => (q.assigned_businesses?.length || 0) >= 2).length}
              </p>
            </div>
            <AlertCircle className="w-8 h-8 text-red-500" />
          </div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Available (0-1/2)</p>
              <p className="text-2xl font-bold text-green-600">
                {qualifiers.filter(q => (q.assigned_businesses?.length || 0) < 2).length}
              </p>
            </div>
            <UserCheck className="w-8 h-8 text-green-500" />
          </div>
        </div>
      </div>

      {/* Qualifiers List */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        {filteredQualifiers.length === 0 ? (
          <div className="p-12 text-center">
            <UserCheck className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">
              {searchTerm ? 'No qualifiers match your search' : 'No qualifiers yet'}
            </p>
            {!searchTerm && (
              <button
                onClick={() => setShowCreateModal(true)}
                className="mt-4 text-blue-500 hover:text-blue-600 font-medium"
              >
                Add your first qualifier
              </button>
            )}
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {filteredQualifiers.map((qualifier) => (
              <div key={qualifier.id} className="p-4 hover:bg-gray-50 transition-colors">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-lg font-semibold text-gray-900">
                        {qualifier.full_name}
                      </h3>
                      {getCapacityBadge(qualifier)}
                      {qualifier.is_active === false && (
                        <span className="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-700 rounded-full">
                          Inactive
                        </span>
                      )}
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm mb-3">
                      <div className="flex items-center text-gray-600">
                        <FileText className="w-4 h-4 mr-2" />
                        <span className="font-medium">License:</span>
                        <span className="ml-2">{qualifier.qualifier_license_number}</span>
                      </div>
                      <div className="flex items-center text-gray-600">
                        <UserCheck className="w-4 h-4 mr-2" />
                        <span className="font-medium">ID:</span>
                        <span className="ml-2">{qualifier.qualifier_id}</span>
                      </div>
                    </div>

                    {/* Assigned Businesses */}
                    {qualifier.assigned_businesses && qualifier.assigned_businesses.length > 0 ? (
                      <div className="mt-3 bg-gray-50 p-3 rounded-lg">
                        <p className="text-sm font-medium text-gray-700 mb-2">Assigned to:</p>
                        <div className="space-y-2">
                          {qualifier.assigned_businesses.map((business, idx) => (
                            <div key={idx} className="flex items-center justify-between text-sm">
                              <div className="flex items-center text-gray-600">
                                <Building2 className="w-4 h-4 mr-2 text-gray-400" />
                                <span>{typeof business === 'string' ? business : business.business_name || business.business_id}</span>
                                {business.start_date && (
                                  <span className="ml-2 text-xs text-gray-400">
                                    (since {new Date(business.start_date).toLocaleDateString()})
                                  </span>
                                )}
                              </div>
                              <button
                                onClick={() => handleEndAssignment(
                                  qualifier.id,
                                  business.business_id,
                                  business.business_name || business.business_id
                                )}
                                disabled={endingAssignment === business.business_id}
                                className="flex items-center px-2 py-1 text-xs text-red-600 hover:bg-red-50 rounded transition-colors disabled:opacity-50"
                                title="End this assignment"
                              >
                                {endingAssignment === business.business_id ? (
                                  <Loader2 className="w-3 h-3 animate-spin" />
                                ) : (
                                  <>
                                    <XCircle className="w-3 h-3 mr-1" />
                                    End
                                  </>
                                )}
                              </button>
                            </div>
                          ))}
                        </div>
                      </div>
                    ) : (
                      <div className="mt-3 text-sm text-gray-500 italic">
                        Not assigned to any business yet
                      </div>
                    )}
                  </div>

                  <div className="ml-4">
                    <button
                      onClick={() => {
                        setSelectedQualifier(qualifier);
                        setShowAssignModal(true);
                        setSaveError(null);
                      }}
                      disabled={(qualifier.assigned_businesses?.length || 0) >= 2}
                      className="px-3 py-1 text-sm bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Assign
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* End Assignment Confirmation Dialog */}
      {confirmEndDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              End assignment for {confirmEndDialog.businessName}?
            </h3>
            <p className="text-sm text-gray-600 mb-6">
              This will set the end date to today and free up capacity.
            </p>
            <div className="flex gap-3 justify-end">
              <button
                onClick={() => setConfirmEndDialog(null)}
                className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={confirmEndAssignment}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
              >
                OK
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Create Modal */}
      {showCreateModal && (
        <CreateQualifierModal
          onClose={() => {
            setShowCreateModal(false);
            setSaveError(null);
          }}
          onSave={handleCreateQualifier}
          isSaving={isSaving}
          error={saveError}
        />
      )}

      {/* Assign Modal */}
      {showAssignModal && selectedQualifier && (
        <AssignQualifierModal
          qualifier={selectedQualifier}
          businesses={businesses}
          onClose={() => {
            setShowAssignModal(false);
            setSelectedQualifier(null);
            setSaveError(null);
          }}
          onAssign={handleAssignQualifier}
          isSaving={isSaving}
          error={saveError}
        />
      )}
    </div>
  );
}

function CreateQualifierModal({ onClose, onSave, isSaving, error }) {
  const [formData, setFormData] = useState({
    full_name: '',
    qualifier_license_number: '',
    license_state: 'NC',
    phone: '',
    email: '',
    is_active: true,
    notes: ''
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    onSave(formData);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Add Qualifier</h2>
          
          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Full Name *
              </label>
              <input
                type="text"
                required
                value={formData.full_name}
                onChange={(e) => setFormData({...formData, full_name: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  License Number *
                </label>
                <input
                  type="text"
                  required
                  value={formData.qualifier_license_number}
                  onChange={(e) => setFormData({...formData, qualifier_license_number: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  License State *
                </label>
                <input
                  type="text"
                  required
                  value={formData.license_state}
                  onChange={(e) => setFormData({...formData, license_state: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Phone</label>
                <input
                  type="tel"
                  value={formData.phone}
                  onChange={(e) => setFormData({...formData, phone: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({...formData, email: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Notes</label>
              <textarea
                value={formData.notes}
                onChange={(e) => setFormData({...formData, notes: e.target.value})}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div className="flex justify-end gap-3 pt-4">
              <button
                type="button"
                onClick={onClose}
                disabled={isSaving}
                className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors disabled:opacity-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={isSaving}
                className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors disabled:opacity-50 flex items-center"
              >
                {isSaving ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Creating...
                  </>
                ) : (
                  'Create Qualifier'
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

function AssignQualifierModal({ qualifier, businesses, onClose, onAssign, isSaving, error }) {
  const [selectedBusinessId, setSelectedBusinessId] = useState('');

  // Filter out already assigned businesses
  const availableBusinesses = businesses.filter(business => {
    const assignedBusinessIds = qualifier.assigned_businesses?.map(b => 
      typeof b === 'string' ? b : b.id
    ) || [];
    return !assignedBusinessIds.includes(business.id);
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    if (selectedBusinessId) {
      onAssign(selectedBusinessId);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg max-w-md w-full">
        <div className="p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Assign Qualifier</h2>
          <p className="text-gray-600 mb-4">{qualifier.full_name}</p>
          
          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Select Business *
              </label>
              <select
                required
                value={selectedBusinessId}
                onChange={(e) => setSelectedBusinessId(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">-- Select a business --</option>
                {availableBusinesses.map((business) => (
                  <option key={business.id} value={business.id}>
                    {business.business_name} ({business.business_id})
                  </option>
                ))}
              </select>
              {availableBusinesses.length === 0 && (
                <p className="mt-2 text-sm text-gray-500">
                  All businesses are already assigned to this qualifier
                </p>
              )}
            </div>

            <div className="flex justify-end gap-3 pt-4">
              <button
                type="button"
                onClick={onClose}
                disabled={isSaving}
                className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors disabled:opacity-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={isSaving || !selectedBusinessId}
                className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors disabled:opacity-50 flex items-center"
              >
                {isSaving ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Assigning...
                  </>
                ) : (
                  'Assign to Business'
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
