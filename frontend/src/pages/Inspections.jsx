import { ClipboardCheck, Plus, Search, Filter, Calendar, User, Building2, Loader2, CheckCircle, AlertCircle, Clock, XCircle } from 'lucide-react';
import { useState, useEffect, useMemo } from 'react';
import api from '../lib/api';
import { useAppStore } from '../stores/appStore';
import useInspectionsStore from '../stores/inspectionsStore';
import ErrorState from '../components/ErrorState';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import StatusBadge from '@/components/app/StatusBadge';
import StatsCard from '@/components/app/StatsCard';
import EmptyState from '@/components/app/EmptyState';
import { LoadingState } from '@/components/app';

export default function Inspections() {
  const { navigateToInspectionDetails } = useAppStore();
  
  // Use inspectionsStore for data and filtering
  const { 
    inspections, 
    loading, 
    error, 
    filter,
    setFilter,
    fetchInspections,
    getFilteredInspections
  } = useInspectionsStore();
  
  const [searchTerm, setSearchTerm] = useState('');
  const [projects, setProjects] = useState([]);

  useEffect(() => {
    fetchAllData();
    window.history.replaceState({ page: 'inspections' }, '');
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const fetchAllData = async () => {
    try {
      // Fetch all data in parallel
      const [projectsData] = await Promise.all([
        api.getProjects()
      ]);
      
      await fetchInspections();
      setProjects(Array.isArray(projectsData) ? projectsData : []);
    } catch (err) {
      console.error('Failed to load inspections:', err);
    }
  };

  const getProjectName = (projectId) => {
    const project = projects.find(p => 
      p.project_id === projectId || 
      p['Project ID'] === projectId
    );
    return project?.project_name || project?.['Project Name'] || 'Unknown Project';
  };

  // Format date helper
  const formatDate = (dateString) => {
    if (!dateString) return 'Not set';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  // Memoized filtered inspections (status filter + search)
  const filteredInspections = useMemo(() => {
    let result = getFilteredInspections(); // Apply status filter from store
    
    // Apply search filter
    if (searchTerm) {
      result = result.filter(inspection => {
        const businessId = inspection.business_id || inspection['Inspection ID'] || '';
        const type = inspection.inspection_type || inspection['Inspection Type'] || '';
        const inspector = inspection.inspector || '';
        const projectName = getProjectName(inspection.project_id || inspection['Project ID']);
        
        const searchLower = searchTerm.toLowerCase();
        return businessId.toLowerCase().includes(searchLower) ||
               type.toLowerCase().includes(searchLower) ||
               inspector.toLowerCase().includes(searchLower) ||
               projectName.toLowerCase().includes(searchLower);
      });
    }
    
    return result;
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [inspections, filter, searchTerm, projects, getFilteredInspections, getProjectName]);

  const getResultBadge = (result) => {
    if (!result) return null;
    
    const lowerResult = result.toLowerCase();
    let color = { bg: '#F3F4F6', text: '#6B7280', border: '#D1D5DB' };
    
    if (lowerResult === 'pass') {
      color = { bg: '#ECFDF5', text: '#059669', border: '#A7F3D0' };
    } else if (lowerResult === 'fail') {
      color = { bg: '#FEE2E2', text: '#DC2626', border: '#FECACA' };
    } else if (lowerResult === 'partial') {
      color = { bg: '#FEF3C7', text: '#D97706', border: '#FCD34D' };
    }
    
    return (
      <span style={{
        display: 'inline-flex',
        alignItems: 'center',
        padding: '2px 8px',
        fontSize: '11px',
        fontWeight: '600',
        backgroundColor: color.bg,
        color: color.text,
        border: `1px solid ${color.border}`,
        borderRadius: '4px',
        marginLeft: '8px'
      }}>
        {result}
      </span>
    );
  };

  if (loading && inspections.length === 0) {
    return <LoadingState message="Loading inspections..." layout="list" />;
  }

  if (error && inspections.length === 0) {
    return <ErrorState message={error} onRetry={fetchAllData} />;
  }

  return (
    <div className="bg-gray-50 min-h-screen p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-start mb-8">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <ClipboardCheck size={32} className="text-indigo-600" strokeWidth={2} />
              <h1 className="text-3xl font-bold text-gray-800">
                Inspections
              </h1>
            </div>
            <p className="text-base text-gray-500">
              Track building inspections and deficiencies
            </p>
          </div>

          <Button
            onClick={() => {/* TODO: Open create inspection modal */}}
            className="bg-indigo-600 hover:bg-purple-700"
          >
            <Plus size={20} />
            New Inspection
          </Button>
        </div>

        {/* Filters and Search */}
        <div className="flex gap-4 mb-6 flex-wrap">
          {/* Status Filters */}
          <div className="flex gap-2 p-1 bg-white rounded-lg border border-gray-200">
            {['all', 'scheduled', 'in-progress', 'completed', 'failed'].map(status => (
              <Button
                key={status}
                variant={filter === status ? 'default' : 'ghost'}
                size="sm"
                onClick={() => setFilter(status)}
                className={filter === status ? 'bg-indigo-600 hover:bg-indigo-700' : ''}
              >
                {status === 'all' ? 'All' : status.replace('-', ' ')}
              </Button>
            ))}
          </div>

          {/* Search */}
          <div className="flex-1 min-w-[300px] relative">
            <Search size={20} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder="Search by ID, type, inspector, or project..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-11 pr-3 py-3 text-sm border border-gray-200 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>
        </div>

        {/* Stats Summary */}
        <div className="grid grid-cols-[repeat(auto-fit,minmax(140px,1fr))] gap-4 mb-6">
          <StatsCard 
            label="Total Inspections" 
            value={inspections.length}
          />
          <StatsCard 
            label="Scheduled" 
            value={inspections.filter(i => (i.status || '').toLowerCase() === 'scheduled').length}
            valueClassName="text-amber-600"
          />
          <StatsCard 
            label="In Progress" 
            value={inspections.filter(i => (i.status || '').toLowerCase() === 'in-progress').length}
            valueClassName="text-blue-600"
          />
          <StatsCard 
            label="Completed" 
            value={inspections.filter(i => (i.status || '').toLowerCase() === 'completed').length}
            valueClassName="text-green-600"
          />
        </div>

        {/* Inspections Grid */}
        {filteredInspections.length === 0 ? (
          <EmptyState
            icon={ClipboardCheck}
            title={searchTerm ? 'No inspections found' : 'No inspections yet'}
            description={searchTerm ? 'Try adjusting your search or filters' : 'Create your first inspection to get started'}
          />
        ) : (
          <div className="grid grid-cols-[repeat(auto-fill,minmax(320px,1fr))] gap-5">
            {filteredInspections.map((inspection) => {
              const inspectionStatus = inspection.status || inspection['Inspection Status'] || 'unknown';
              const inspectionId = inspection.inspection_id || inspection['Inspection ID'];
              const businessId = inspection.business_id || inspectionId;
              const inspectionType = inspection.inspection_type || inspection['Inspection Type'] || 'Unknown Type';
              const scheduledDate = inspection.scheduled_date || inspection['Scheduled Date'];
              const completedDate = inspection.completed_date || inspection['Completed Date'];
              const inspector = inspection.inspector || 'Not assigned';
              const result = inspection.result || inspection['Result'];
              const projectId = inspection.project_id || inspection['Project ID'];

              return (
                <Card
                  key={inspectionId}
                  onClick={() => navigateToInspectionDetails(inspectionId)}
                  className="cursor-pointer transition-all hover:-translate-y-0.5 hover:shadow-lg hover:border-indigo-600"
                >
                  <CardContent className="p-6">
                    {/* Header */}
                    <div className="flex justify-between items-start mb-4">
                      <div className="flex-1">
                        <h3 className="text-lg font-bold text-gray-800 mb-1">
                          {inspectionType}
                        </h3>
                        <div className="text-sm text-gray-500 font-mono">
                          {businessId}
                        </div>
                      </div>
                      <StatusBadge type="inspection" status={inspectionStatus} />
                    </div>

                    {/* Details */}
                    <div className="flex flex-col gap-3 pt-4 border-t border-gray-100">
                      <div className="flex items-center gap-2">
                        <Building2 size={16} className="text-gray-400" />
                        <span className="text-sm text-gray-500">
                          {getProjectName(projectId)}
                        </span>
                      </div>

                      <div className="flex items-center gap-2">
                        <User size={16} className="text-gray-400" />
                        <span className="text-sm text-gray-500">
                          {inspector}
                        </span>
                      </div>

                      <div className="flex items-center gap-2">
                        <Calendar size={16} className="text-gray-400" />
                        <span className="text-sm text-gray-500">
                          {completedDate ? `Completed: ${formatDate(completedDate)}` : `Scheduled: ${formatDate(scheduledDate)}`}
                        </span>
                      </div>

                      {result && (
                        <div className="flex items-center gap-2">
                          <span className="text-sm text-gray-500 font-semibold">
                            Result:
                          </span>
                          {getResultBadge(result)}
                        </div>
                      )}
                    </div>

                    {/* Deficiencies count */}
                    {inspection.deficiencies && Array.isArray(inspection.deficiencies) && inspection.deficiencies.length > 0 && (
                      <div className="mt-3 p-2 px-3 bg-amber-50 rounded-md flex items-center gap-2">
                        <AlertCircle size={16} className="text-amber-600" />
                        <span className="text-sm text-amber-600 font-semibold">
                          {inspection.deficiencies.length} {inspection.deficiencies.length === 1 ? 'deficiency' : 'deficiencies'}
                        </span>
                      </div>
                    )}
                  </CardContent>
                </Card>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
