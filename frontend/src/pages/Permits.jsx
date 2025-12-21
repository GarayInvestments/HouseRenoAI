import { FileText, Plus, Search, Filter, User, FolderKanban } from 'lucide-react';
import { useState, useEffect, useMemo } from 'react';
import api from '../lib/api';
import { useAppStore } from '../stores/appStore';
import { usePermitsStore } from '../stores/permitsStore';
import { StatusBadge, LoadingState, EmptyState, PageHeader } from '@/components/app';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

export default function Permits() {
  const { navigateToPermit } = useAppStore();
  
  // Use permitsStore for data and filtering
  const { 
    permits, 
    loading, 
    error, 
    filter,
    setPermits,
    setLoading,
    setError,
    getFilteredPermits,
    isCacheValid
  } = usePermitsStore();
  
  const [searchTerm, setSearchTerm] = useState('');
  const [hoveredCard, setHoveredCard] = useState(null);
  const [projects, setProjects] = useState([]);
  const [clients, setClients] = useState([]);
  const [clientFilter, setClientFilter] = useState(null); // Local client filter

  useEffect(() => {
    fetchAllData();
    // Set initial history state for permits page
    window.history.replaceState({ page: 'permits' }, '');
  }, []);

  const fetchAllData = async () => {
    // Use cache if valid
    if (isCacheValid() && permits.length > 0) {
      return;
    }
    
    try {
      setLoading(true);
      setError(null);
      
      // Fetch all data in parallel
      const [permitsResponse, projectsData, clientsData] = await Promise.all([
        api.getPermits(),
        api.getProjects(),
        api.getClients()
      ]);
      
      // Handle paginated response from permits endpoint
      const permitsData = permitsResponse?.items || permitsResponse || [];
      setPermits(Array.isArray(permitsData) ? permitsData : []);
      setProjects(Array.isArray(projectsData) ? projectsData : []);
      setClients(Array.isArray(clientsData) ? clientsData : []);
    } catch {
      setError('Failed to load permits. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const getProjectName = (projectId) => {
    const project = projects.find(p => 
      p['Project ID'] === projectId || 
      p.project_id === projectId
    );
    return project?.['Project Name'] || project?.project_name || projectId || 'Unknown Project';
  };

  const getClientNameForPermit = (permit) => {
    // First, find the project for this permit
    const permitProjectId = permit['Project ID'] || permit.project_id;
    const project = projects.find(p => 
      p['Project ID'] === permitProjectId || 
      p.project_id === permitProjectId
    );
    if (!project) return null;
    
    // Then find the client using the project's client ID
    const clientId = project['Client ID'] || project.client_id;
    if (!clientId) return null;
    
    const client = clients.find(c => 
      c['Client ID'] === clientId || 
      c['ID'] === clientId ||
      c.client_id === clientId ||
      c.id === clientId
    );
    return client?.['Full Name'] || client?.['Client Name'] || client?.full_name || clientId;
  };

  // Memoized filtered permits (status filter + client filter + search)
  const filteredPermits = useMemo(() => {
    let result = getFilteredPermits(); // Apply status filter from store
    
    // Apply client filter
    if (clientFilter) {
      // Get all project IDs for this client
      const clientProjectIds = projects
        .filter(p => p['Client ID'] === clientFilter)
        .map(p => p['Project ID']);
      // Filter permits by those project IDs
      result = result.filter(permit => clientProjectIds.includes(permit['Project ID']));
    }
    
    // Apply search filter
    if (searchTerm) {
      result = result.filter(permit => {
        const permitNumber = permit['Permit Number'] || permit.permit_number || permit.business_id || '';
        const permitStatus = permit['Permit Status'] || permit.status || '';
        return permitNumber.toLowerCase().includes(searchTerm.toLowerCase()) ||
               permitStatus.toLowerCase().includes(searchTerm.toLowerCase());
      });
    }
    
    return result;
  }, [permits, filter, clientFilter, searchTerm, projects]);

  // Get client name for filter badge
  const getFilteredClientName = () => {
    if (!clientFilter) return null;
    const client = clients.find(c => c['Client ID'] === clientFilter || c['ID'] === clientFilter);
    return client?.['Full Name'] || client?.['Client Name'] || clientFilter;
  };

  const clearClientFilter = () => {
    setClientFilter(null);
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Not set';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  if (loading) {
    return <LoadingState message="Loading permits..." layout="list" />;
  }

  if (error) {
    return (
      <div className="p-5 bg-slate-50 min-h-screen">
        <EmptyState 
          icon={<FileText size={48} />}
          title="Failed to load permits"
          message={error}
          action={<Button onClick={fetchAllData}>Retry</Button>}
        />
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full bg-slate-50">
      {/* Header */}
      <div className="bg-white border-b border-slate-200 p-6 lg:px-8 shadow-sm">
        <div className="flex justify-between items-center mb-4">
          <div className="flex items-center gap-4">
            <div>
              <h1 className="text-2xl font-semibold text-slate-800 mb-1">Permits</h1>
              <p className="text-slate-500 text-sm">
                {clientFilter 
                  ? `Showing permits for ${getFilteredClientName()}` 
                  : 'Manage and track all your building permits'
                }
              </p>
            </div>
            {clientFilter && (
              <Badge variant="info" className="flex items-center gap-2">
                <span className="font-medium">Client: {getFilteredClientName()}</span>
                <button
                  onClick={clearClientFilter}
                  className="text-blue-900 text-lg font-semibold px-1 hover:text-blue-950 transition-colors"
                >
                  ×
                </button>
              </Badge>
            )}
          </div>
          <Button className="gap-2">
            <Plus size={18} />
            New Permit
          </Button>
        </div>

        {/* Search and Filter Bar */}
        <div className="flex gap-3 mt-4">
          <div className="flex-1 relative">
            <Search size={18} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search permits..."
              className="w-full py-2.5 px-3.5 pl-11 border border-slate-200 rounded-lg text-sm text-slate-800 outline-none transition-all focus:border-blue-600 focus:ring-4 focus:ring-blue-100"
            />
          </div>
          <Button variant="outline" className="gap-2">
            <Filter size={18} />
            Filter
          </Button>
        </div>
      </div>

      {/* Permits Grid */}
      <div className="flex-1 overflow-y-auto p-8">
        {loading ? (
          <LoadingState message="Loading permits..." />
        ) : error ? (
          <EmptyState 
            icon={<FileText size={48} />}
            title="Failed to load permits"
            message={error}
            action={<Button onClick={fetchAllData}>Retry</Button>}
          />
        ) : filteredPermits.length === 0 ? (
          <EmptyState 
            icon={<FileText size={48} />}
            title="No permits found"
            message={searchTerm ? "Try adjusting your search" : "Get started by creating your first permit"}
            action={!searchTerm && <Button><Plus size={16} className="mr-2" />New Permit</Button>}
          />
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-7xl mx-auto">
            {filteredPermits.map((permit) => {
              const permitStatus = permit['Permit Status'] || permit.status;
              const permitId = permit['Permit ID'] || permit.permit_id;
              const isHovered = hoveredCard === permitId;

              return (
                <Card
                  key={permitId}
                  onClick={() => navigateToPermit(permitId)}
                  onMouseEnter={() => setHoveredCard(permitId)}
                  onMouseLeave={() => setHoveredCard(null)}
                  className={`cursor-pointer transition-all duration-200 ${
                    isHovered ? 'shadow-lg -translate-y-0.5' : 'shadow-sm'
                  }`}
                >
                  <CardContent className="p-5">
                    <div className="flex items-start gap-3 mb-4">
                      <div className="w-11 h-11 rounded-lg bg-linear-to-br from-blue-600 to-blue-700 flex items-center justify-center shrink-0 shadow-md shadow-blue-600/30">
                        <FileText size={22} className="text-white" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <h3 className="text-base font-semibold text-slate-800 mb-1 truncate">
                          {permit['Permit Number'] || permit.permit_number || permit.business_id || 'Unknown Permit'}
                        </h3>
                        <div className="flex flex-col gap-0.5">
                          {(permit['Project ID'] || permit.project_id) && (
                            <p className="text-xs text-slate-500 flex items-center gap-1 truncate">
                              <FolderKanban size={12} />
                              {getProjectName(permit['Project ID'] || permit.project_id)}
                            </p>
                          )}
                          {getClientNameForPermit(permit) && (
                            <p className="text-xs text-slate-500 flex items-center gap-1 truncate">
                              <User size={12} />
                              {getClientNameForPermit(permit)}
                            </p>
                          )}
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center justify-between pt-4 border-t border-slate-100">
                      <StatusBadge status={permitStatus?.toLowerCase()} type="permit" />
                      <span className="text-xs text-slate-500">
                        {formatDate(permit['Date Submitted'] || permit.application_date)}
                      </span>
                    </div>
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
