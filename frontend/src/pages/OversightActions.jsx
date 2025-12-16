import { Eye, Plus, Filter, Calendar, Building2, UserCheck, FolderKanban, Loader2, Clock } from 'lucide-react';
import { useState, useEffect, useMemo } from 'react';
import api from '../lib/api';
import { useAppStore } from '../stores/appStore';
import LoadingScreen from '../components/LoadingScreen';
import ErrorState from '../components/ErrorState';

export default function OversightActions() {
  const [actions, setActions] = useState([]);
  const [projects, setProjects] = useState([]);
  const [qualifiers, setQualifiers] = useState([]);
  const [businesses, setBusinesses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [saveError, setSaveError] = useState(null);

  // Filters
  const [projectFilter, setProjectFilter] = useState('');
  const [qualifierFilter, setQualifierFilter] = useState('');
  const [businessFilter, setBusinessFilter] = useState('');
  const [actionTypeFilter, setActionTypeFilter] = useState('');

  useEffect(() => {
    fetchData();
    window.history.replaceState({ page: 'oversight-actions' }, '');
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [actionsResponse, projectsResponse, qualifiersResponse, businessesResponse] = await Promise.all([
        api.request('/oversight-actions'),
        api.getProjects(),
        api.getQualifiers(),
        api.request('/licensed-businesses')
      ]);
      
      setActions(Array.isArray(actionsResponse) ? actionsResponse : []);
      setProjects(Array.isArray(projectsResponse) ? projectsResponse : []);
      setQualifiers(Array.isArray(qualifiersResponse) ? qualifiersResponse : []);
      setBusinesses(Array.isArray(businessesResponse) ? businessesResponse : []);
    } catch (err) {
      setError('Failed to load oversight actions. Please try again.');
      console.error('Error fetching data:', err);
    } finally {
      setLoading(false);
    }
  };

  const filteredActions = useMemo(() => {
    return actions.filter(action => {
      if (projectFilter && action.project_id !== projectFilter) return false;
      if (qualifierFilter && action.qualifier_id !== qualifierFilter) return false;
      if (businessFilter && action.licensed_business_id !== businessFilter) return false;
      if (actionTypeFilter && action.action_type !== actionTypeFilter) return false;
      return true;
    });
  }, [actions, projectFilter, qualifierFilter, businessFilter, actionTypeFilter]);

  const handleCreateAction = async (formData) => {
    try {
      setIsSaving(true);
      setSaveError(null);
      
      const response = await api.post('/oversight-actions', formData);
      
      setActions([response, ...actions]);
      setShowCreateModal(false);
    } catch (err) {
      setSaveError(err.response?.data?.detail || 'Failed to create oversight action. Please try again.');
      console.error('Error creating action:', err);
    } finally {
      setIsSaving(false);
    }
  };

  const actionTypes = ['SITE_VISIT', 'PLAN_REVIEW', 'PERMIT_REVIEW', 'CLIENT_MEETING', 'INSPECTION_SUPPORT', 'OTHER'];

  if (loading) return <LoadingScreen />;
  if (error) return <ErrorState message={error} onRetry={fetchData} />;

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Oversight Actions</h1>
            <p className="text-gray-600 mt-1">Track qualifier oversight activities per permit</p>
          </div>
          <button
            onClick={() => setShowCreateModal(true)}
            className="flex items-center px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
          >
            <Plus className="w-5 h-5 mr-2" />
            Log Action
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200 mb-6">
        <div className="flex items-center gap-2 mb-3">
          <Filter className="w-5 h-5 text-gray-500" />
          <h3 className="font-medium text-gray-900">Filters</h3>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Project</label>
            <select
              value={projectFilter}
              onChange={(e) => setProjectFilter(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
            >
              {[
                <option key="all" value="">All Projects</option>,
                ...projects.map((project) => (
                  <option key={project.id} value={project.id}>
                    {project['Project Name'] || project.project_name || project['Project ID']}
                  </option>
                ))
              ]}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Qualifier</label>
            <select
              value={qualifierFilter}
              onChange={(e) => setQualifierFilter(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
            >
              {[
                <option key="all" value="">All Qualifiers</option>,
                ...qualifiers.map((qualifier) => (
                  <option key={qualifier.id} value={qualifier.id}>
                    {qualifier.full_name}
                  </option>
                ))
              ]}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Business</label>
            <select
              value={businessFilter}
              onChange={(e) => setBusinessFilter(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
            >
              {[
                <option key="all" value="">All Businesses</option>,
                ...businesses.map((business) => (
                  <option key={business.id} value={business.id}>
                    {business.business_name}
                  </option>
                ))
              ]}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Action Type</label>
            <select
              value={actionTypeFilter}
              onChange={(e) => setActionTypeFilter(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
            >
              {[
                <option key="all" value="">All Types</option>,
                ...actionTypes.map((type) => (
                  <option key={type} value={type}>
                    {type.replace('_', ' ')}
                  </option>
                ))
              ]}
            </select>
          </div>
        </div>

        {(projectFilter || qualifierFilter || businessFilter || actionTypeFilter) && (
          <button
            onClick={() => {
              setProjectFilter('');
              setQualifierFilter('');
              setBusinessFilter('');
              setActionTypeFilter('');
            }}
            className="mt-3 text-sm text-blue-500 hover:text-blue-600"
          >
            Clear all filters
          </button>
        )}
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Actions</p>
              <p className="text-2xl font-bold text-gray-900">{filteredActions.length}</p>
            </div>
            <Eye className="w-8 h-8 text-blue-500" />
          </div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Site Visits</p>
              <p className="text-2xl font-bold text-green-600">
                {filteredActions.filter(a => a.action_type === 'SITE_VISIT').length}
              </p>
            </div>
            <FolderKanban className="w-8 h-8 text-green-500" />
          </div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Plan Reviews</p>
              <p className="text-2xl font-bold text-purple-600">
                {filteredActions.filter(a => a.action_type === 'PLAN_REVIEW').length}
              </p>
            </div>
            <FolderKanban className="w-8 h-8 text-purple-500" />
          </div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">This Month</p>
              <p className="text-2xl font-bold text-blue-600">
                {filteredActions.filter(a => {
                  const actionDate = new Date(a.action_date || a.oversight_date);
                  const now = new Date();
                  return actionDate.getMonth() === now.getMonth() && actionDate.getFullYear() === now.getFullYear();
                }).length}
              </p>
            </div>
            <Calendar className="w-8 h-8 text-blue-500" />
          </div>
        </div>
      </div>

      {/* Actions List */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        {filteredActions.length === 0 ? (
          <div className="p-12 text-center">
            <Eye className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">
              {projectFilter || qualifierFilter || businessFilter || actionTypeFilter
                ? 'No oversight actions match your filters'
                : 'No oversight actions logged yet'}
            </p>
            {!projectFilter && !qualifierFilter && !businessFilter && !actionTypeFilter && (
              <button
                onClick={() => setShowCreateModal(true)}
                className="mt-4 text-blue-500 hover:text-blue-600 font-medium"
              >
                Log your first oversight action
              </button>
            )}
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {filteredActions.map((action) => {
              const project = projects.find(p => p.id === action.project_id);
              const qualifier = qualifiers.find(q => q.id === action.qualifier_id);
              const business = businesses.find(b => b.id === action.licensed_business_id);
              
              return (
                <div key={action.id} className="p-4 hover:bg-gray-50 transition-colors">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <span className="px-3 py-1 text-xs font-medium bg-blue-100 text-blue-700 rounded-full">
                          {action.action_type?.replace('_', ' ')}
                        </span>
                        <div className="flex items-center text-sm text-gray-600">
                          <Calendar className="w-4 h-4 mr-1" />
                          <span className="font-bold">
                            {new Date(action.action_date || action.oversight_date).toLocaleDateString()}
                          </span>
                        </div>
                        {action.recorded_at && action.recorded_at !== action.action_date && (
                          <div className="flex items-center text-xs text-gray-500">
                            <Clock className="w-3 h-3 mr-1" />
                            Recorded: {new Date(action.recorded_at).toLocaleDateString()}
                          </div>
                        )}
                      </div>

                      {action.description && (
                        <p className="text-gray-900 mb-2">{action.description}</p>
                      )}

                      <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-sm">
                        {project && (
                          <div className="flex items-center text-gray-600">
                            <FolderKanban className="w-4 h-4 mr-2" />
                            <span>{project.project_name || project.project_id}</span>
                          </div>
                        )}
                        {qualifier && (
                          <div className="flex items-center text-gray-600">
                            <UserCheck className="w-4 h-4 mr-2" />
                            <span>{qualifier.full_name}</span>
                          </div>
                        )}
                        {business && (
                          <div className="flex items-center text-gray-600">
                            <Building2 className="w-4 h-4 mr-2" />
                            <span>{business.business_name}</span>
                          </div>
                        )}
                      </div>

                      {action.location && (
                        <div className="mt-2 text-sm text-gray-600">
                          <span className="font-medium">Location:</span> {action.location}
                        </div>
                      )}

                      {action.duration_hours && (
                        <div className="mt-1 text-sm text-gray-600">
                          <span className="font-medium">Duration:</span> {action.duration_hours} hours
                        </div>
                      )}

                      {action.notes && (
                        <div className="mt-2 text-sm text-gray-600 bg-gray-50 p-2 rounded">
                          {action.notes}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Create Modal */}
      {showCreateModal && (
        <CreateActionModal
          onClose={() => {
            setShowCreateModal(false);
            setSaveError(null);
          }}
          onSave={handleCreateAction}
          projects={projects}
          qualifiers={qualifiers}
          businesses={businesses}
          isSaving={isSaving}
          error={saveError}
        />
      )}
    </div>
  );
}

function CreateActionModal({ onClose, onSave, projects, qualifiers, businesses, isSaving, error }) {
  const [formData, setFormData] = useState({
    project_id: '',
    action_date: new Date().toISOString().split('T')[0],
    action_type: 'SITE_VISIT',
    description: '',
    location: '',
    duration_hours: '',
    notes: '',
    qualifier_id: '',
    licensed_business_id: ''
  });

  const actionTypes = ['SITE_VISIT', 'PLAN_REVIEW', 'PERMIT_REVIEW', 'CLIENT_MEETING', 'INSPECTION_SUPPORT', 'OTHER'];

  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Clean up data before sending
    const cleanedData = {
      ...formData,
      duration_hours: formData.duration_hours ? parseFloat(formData.duration_hours) : undefined
    };
    
    onSave(cleanedData);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Log Oversight Action</h2>
          
          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Project *
              </label>
              <select
                required
                value={formData.project_id}
                onChange={(e) => setFormData({...formData, project_id: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                {[
                  <option key="" value="">-- Select a project --</option>,
                  ...projects.map((project) => (
                    <option key={project.id} value={project.id}>
                      {project['Project Name'] || project.project_name || project['Project ID']}
                    </option>
                  ))
                ]}
              </select>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Oversight Date *
                </label>
                <input
                  type="date"
                  required
                  value={formData.action_date}
                  onChange={(e) => setFormData({...formData, action_date: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Action Type *
                </label>
                <select
                  required
                  value={formData.action_type}
                  onChange={(e) => setFormData({...formData, action_type: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  {actionTypes.map((type) => (
                    <option key={type} value={type}>
                      {type.replace('_', ' ')}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Qualifier
              </label>
              <select
                value={formData.qualifier_id}
                onChange={(e) => setFormData({...formData, qualifier_id: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                {[
                  <option key="" value="">-- Select qualifier (optional) --</option>,
                  ...qualifiers.map((qualifier) => (
                    <option key={qualifier.id} value={qualifier.id}>
                      {qualifier.full_name}
                    </option>
                  ))
                ]}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Business
              </label>
              <select
                value={formData.licensed_business_id}
                onChange={(e) => setFormData({...formData, licensed_business_id: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                {[
                  <option key="" value="">-- Select business (optional) --</option>,
                  ...businesses.map((business) => (
                    <option key={business.id} value={business.id}>
                      {business.business_name}
                    </option>
                  ))
                ]}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Description
              </label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({...formData, description: e.target.value})}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="What oversight activity was performed?"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Location
                </label>
                <input
                  type="text"
                  value={formData.location}
                  onChange={(e) => setFormData({...formData, location: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Site address or meeting location"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Duration (hours)
                </label>
                <input
                  type="number"
                  step="0.5"
                  min="0"
                  value={formData.duration_hours}
                  onChange={(e) => setFormData({...formData, duration_hours: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Notes
              </label>
              <textarea
                value={formData.notes}
                onChange={(e) => setFormData({...formData, notes: e.target.value})}
                rows={2}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Additional notes or observations"
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
                    Logging...
                  </>
                ) : (
                  'Log Action'
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
