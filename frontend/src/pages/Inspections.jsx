import { ClipboardCheck, Plus, Search, Filter, Calendar, User, Building2, Loader2, CheckCircle, AlertCircle, Clock, XCircle } from 'lucide-react';
import { useState, useEffect, useMemo } from 'react';
import api from '../lib/api';
import { useAppStore } from '../stores/appStore';
import useInspectionsStore from '../stores/inspectionsStore';
import LoadingScreen from '../components/LoadingScreen';
import ErrorState from '../components/ErrorState';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import StatusBadge from '@/components/app/StatusBadge';
import StatsCard from '@/components/app/StatsCard';
import EmptyState from '@/components/app/EmptyState';

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
  const [permits, setPermits] = useState([]);

  useEffect(() => {
    fetchAllData();
    window.history.replaceState({ page: 'inspections' }, '');
  }, []);

  const fetchAllData = async () => {
    try {
      // Fetch all data in parallel
      const [inspectionsData, projectsData, permitsData] = await Promise.all([
        fetchInspections(),
        api.getProjects(),
        api.getPermits()
      ]);
      
      setProjects(Array.isArray(projectsData) ? projectsData : []);
      const permitsArray = permitsData?.items || permitsData || [];
      setPermits(Array.isArray(permitsArray) ? permitsArray : []);
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

  const getPermitNumber = (permitId) => {
    const permit = permits.find(p => 
      p.permit_id === permitId || 
      p['Permit ID'] === permitId
    );
    return permit?.permit_number || permit?.business_id || permit?.['Permit Number'] || 'N/A';
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
  }, [inspections, filter, searchTerm, projects]);

  const getStatusColor = (status) => {
    const lowerStatus = status?.toLowerCase();
    if (lowerStatus === 'completed') {
      return { bg: '#ECFDF5', text: '#059669', border: '#A7F3D0' };
    }
    if (lowerStatus === 'in-progress') {
      return { bg: '#DBEAFE', text: '#2563EB', border: '#93C5FD' };
    }
    if (lowerStatus === 'scheduled') {
      return { bg: '#FEF3C7', text: '#D97706', border: '#FCD34D' };
    }
    if (lowerStatus === 'failed') {
      return { bg: '#FEE2E2', text: '#DC2626', border: '#FECACA' };
    }
    if (lowerStatus === 'cancelled') {
      return { bg: '#F3F4F6', text: '#6B7280', border: '#D1D5DB' };
    }
    return { bg: '#F3F4F6', text: '#6B7280', border: '#D1D5DB' };
  };

  const getStatusIcon = (status) => {
    const lowerStatus = status?.toLowerCase();
    if (lowerStatus === 'completed') return <CheckCircle size={16} />;
    if (lowerStatus === 'in-progress') return <Loader2 size={16} className="animate-spin" />;
    if (lowerStatus === 'scheduled') return <Clock size={16} />;
    if (lowerStatus === 'failed') return <AlertCircle size={16} />;
    if (lowerStatus === 'cancelled') return <XCircle size={16} />;
    return <Clock size={16} />;
  };

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
    return <LoadingScreen message="Loading inspections..." />;
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
                  <CardContent className=\"p-6\">\n                    {/* Header */}\n                    <div className=\"flex justify-between items-start mb-4\">\n                      <div className=\"flex-1\">\n                        <h3 className=\"text-lg font-bold text-gray-800 mb-1\">\n                          {inspectionType}\n                        </h3>\n                        <div className=\"text-sm text-gray-500 font-mono\">\n                          {businessId}\n                        </div>\n                      </div>\n                      <StatusBadge type=\"inspection\" status={inspectionStatus} />\n                    </div>\n\n                    {/* Details */}\n                    <div className=\"flex flex-col gap-3 pt-4 border-t border-gray-100\">\n                      <div className=\"flex items-center gap-2\">\n                        <Building2 size={16} className=\"text-gray-400\" />\n                        <span className=\"text-sm text-gray-500\">\n                          {getProjectName(projectId)}\n                        </span>\n                      </div>\n\n                      <div className=\"flex items-center gap-2\">\n                        <User size={16} className=\"text-gray-400\" />\n                        <span className=\"text-sm text-gray-500\">\n                          {inspector}\n                        </span>\n                      </div>\n\n                      <div className=\"flex items-center gap-2\">\n                        <Calendar size={16} className=\"text-gray-400\" />\n                        <span className=\"text-sm text-gray-500\">\n                          {completedDate ? `Completed: ${formatDate(completedDate)}` : `Scheduled: ${formatDate(scheduledDate)}`}\n                        </span>\n                      </div>\n\n                      {result && (\n                        <div className=\"flex items-center gap-2\">\n                          <span className=\"text-sm text-gray-500 font-semibold\">\n                            Result:\n                          </span>\n                          {getResultBadge(result)}\n                        </div>\n                      )}\n                    </div>\n\n                    {/* Deficiencies count */}\n                    {inspection.deficiencies && Array.isArray(inspection.deficiencies) && inspection.deficiencies.length > 0 && (\n                      <div className=\"mt-3 p-2 px-3 bg-amber-50 rounded-md flex items-center gap-2\">\n                        <AlertCircle size={16} className=\"text-amber-600\" />\n                        <span className=\"text-sm text-amber-600 font-semibold\">\n                          {inspection.deficiencies.length} {inspection.deficiencies.length === 1 ? 'deficiency' : 'deficiencies'}\n                        </span>\n                      </div>\n                    )}\n                  </CardContent>\n                </Card>\n              );\n            })}\n          </div>\n        )}\n      </div>\n    </div>\n  );\n}
