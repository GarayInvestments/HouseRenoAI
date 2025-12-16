import { Building2, Plus, Search, FileText, Calendar, Loader2, CheckCircle2, XCircle } from 'lucide-react';
import { useState, useEffect, useMemo } from 'react';
import api from '../lib/api';
import { useAppStore } from '../stores/appStore';
import LoadingScreen from '../components/LoadingScreen';
import ErrorState from '../components/ErrorState';

export default function LicensedBusinesses() {
  const [businesses, setBusinesses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [saveError, setSaveError] = useState(null);

  useEffect(() => {
    fetchBusinesses();
    window.history.replaceState({ page: 'licensed-businesses' }, '');
  }, []);

  const fetchBusinesses = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await api.request('/licensed-businesses');
      setBusinesses(Array.isArray(response) ? response : []);
    } catch (err) {
      setError('Failed to load licensed businesses. Please try again.');
      console.error('Error fetching businesses:', err);
    } finally {
      setLoading(false);
    }
  };

  const filteredBusinesses = useMemo(() => {
    if (!searchTerm) return businesses;
    return businesses.filter(business =>
      business.business_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      business.license_number?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      business.business_id?.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [businesses, searchTerm]);

  const handleCreateBusiness = async (formData) => {
    try {
      setIsSaving(true);
      setSaveError(null);
      
      const response = await api.post('/licensed-businesses', formData);
      
      // Add new business to list
      setBusinesses([...businesses, response]);
      setShowCreateModal(false);
    } catch (err) {
      setSaveError(err.response?.data?.detail || 'Failed to create business. Please try again.');
      console.error('Error creating business:', err);
    } finally {
      setIsSaving(false);
    }
  };

  if (loading) return <LoadingScreen />;
  if (error) return <ErrorState message={error} onRetry={fetchBusinesses} />;

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Licensed Businesses</h1>
            <p className="text-gray-600 mt-1">Manage NCLBGC-licensed business entities</p>
          </div>
          <button
            onClick={() => setShowCreateModal(true)}
            className="flex items-center px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
          >
            <Plus className="w-5 h-5 mr-2" />
            Add Business
          </button>
        </div>
      </div>

      {/* Search Bar */}
      <div className="mb-6">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
          <input
            type="text"
            placeholder="Search by name, license number, or business ID..."
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
              <p className="text-sm text-gray-600">Total Businesses</p>
              <p className="text-2xl font-bold text-gray-900">{businesses.length}</p>
            </div>
            <Building2 className="w-8 h-8 text-blue-500" />
          </div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Active</p>
              <p className="text-2xl font-bold text-green-600">
                {businesses.filter(b => b.is_active !== false).length}
              </p>
            </div>
            <CheckCircle2 className="w-8 h-8 text-green-500" />
          </div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Owner Companies</p>
              <p className="text-2xl font-bold text-purple-600">
                {businesses.filter(b => b.is_owner_company).length}
              </p>
            </div>
            <Building2 className="w-8 h-8 text-purple-500" />
          </div>
        </div>
      </div>

      {/* Business List */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        {filteredBusinesses.length === 0 ? (
          <div className="p-12 text-center">
            <Building2 className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">
              {searchTerm ? 'No businesses match your search' : 'No licensed businesses yet'}
            </p>
            {!searchTerm && (
              <button
                onClick={() => setShowCreateModal(true)}
                className="mt-4 text-blue-500 hover:text-blue-600 font-medium"
              >
                Add your first business
              </button>
            )}
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {filteredBusinesses.map((business) => (
              <div key={business.id} className="p-4 hover:bg-gray-50 transition-colors">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-lg font-semibold text-gray-900">
                        {business.business_name}
                      </h3>
                      {business.is_owner_company && (
                        <span className="px-2 py-1 text-xs font-medium bg-purple-100 text-purple-700 rounded-full">
                          Owner Company
                        </span>
                      )}
                      {business.is_active === false && (
                        <span className="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-700 rounded-full">
                          Inactive
                        </span>
                      )}
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                      <div className="flex items-center text-gray-600">
                        <FileText className="w-4 h-4 mr-2" />
                        <span className="font-medium">License:</span>
                        <span className="ml-2">{business.license_number}</span>
                      </div>
                      <div className="flex items-center text-gray-600">
                        <Building2 className="w-4 h-4 mr-2" />
                        <span className="font-medium">ID:</span>
                        <span className="ml-2">{business.business_id}</span>
                      </div>
                    </div>

                    {business.business_address && (
                      <div className="mt-2 text-sm text-gray-600">
                        {business.business_address}
                        {business.city && `, ${business.city}`}
                        {business.state && `, ${business.state}`}
                        {business.zip_code && ` ${business.zip_code}`}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Create Modal */}
      {showCreateModal && (
        <CreateBusinessModal
          onClose={() => {
            setShowCreateModal(false);
            setSaveError(null);
          }}
          onSave={handleCreateBusiness}
          isSaving={isSaving}
          error={saveError}
        />
      )}
    </div>
  );
}

function CreateBusinessModal({ onClose, onSave, isSaving, error }) {
  const [formData, setFormData] = useState({
    business_name: '',
    license_number: '',
    license_state: 'NC',
    business_address: '',
    city: '',
    state: 'NC',
    zip_code: '',
    phone: '',
    email: '',
    license_type: 'GENERAL_CONTRACTOR',
    is_active: true,
    is_owner_company: false,
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
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Add Licensed Business</h2>
          
          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Business Name *
              </label>
              <input
                type="text"
                required
                value={formData.business_name}
                onChange={(e) => setFormData({...formData, business_name: e.target.value})}
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
                  value={formData.license_number}
                  onChange={(e) => setFormData({...formData, license_number: e.target.value})}
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

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Address
              </label>
              <input
                type="text"
                value={formData.business_address}
                onChange={(e) => setFormData({...formData, business_address: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">City</label>
                <input
                  type="text"
                  value={formData.city}
                  onChange={(e) => setFormData({...formData, city: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">State</label>
                <input
                  type="text"
                  value={formData.state}
                  onChange={(e) => setFormData({...formData, state: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">ZIP</label>
                <input
                  type="text"
                  value={formData.zip_code}
                  onChange={(e) => setFormData({...formData, zip_code: e.target.value})}
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

            <div className="flex items-center gap-6">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={formData.is_owner_company}
                  onChange={(e) => setFormData({...formData, is_owner_company: e.target.checked})}
                  className="mr-2"
                />
                <span className="text-sm text-gray-700">Owner Company (House Renovators/2States)</span>
              </label>
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
                  'Create Business'
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
