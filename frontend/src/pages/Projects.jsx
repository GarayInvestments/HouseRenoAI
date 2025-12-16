import { FolderKanban, Plus, Search, MapPin, Users, Calendar } from 'lucide-react';
import { useState, useEffect, useMemo } from 'react';
import api from '../lib/api';
import { useAppStore } from '../stores/appStore';
import { useProjectsStore } from '../stores/projectsStore';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import StatusBadge from '@/components/app/StatusBadge';
import LoadingState from '@/components/app/LoadingState';
import EmptyState from '@/components/app/EmptyState';

export default function Projects() {
  const { navigateToProject } = useAppStore();
  
  // Use projectsStore for data and filtering
  const { 
    projects, 
    loading, 
    error, 
    filter,
    setProjects,
    setLoading,
    setError,
    getFilteredProjects,
    isCacheValid
  } = useProjectsStore();
  
  const [searchTerm, setSearchTerm] = useState('');
  const [clients, setClients] = useState([]);
  const [clientFilter, setClientFilter] = useState(null); // Local client filter

  useEffect(() => {
    fetchProjects();
    // Set initial history state for projects page
    window.history.replaceState({ page: 'projects' }, '');
  }, []);

  const fetchProjects = async () => {
    // Use cache if valid
    if (isCacheValid() && projects.length > 0) {
      return;
    }
    
    try {
      setLoading(true);
      setError(null);
      const [projectsData, clientsData] = await Promise.all([
        api.getProjects(),
        api.getClients()
      ]);
      setProjects(Array.isArray(projectsData) ? projectsData : []);
      setClients(Array.isArray(clientsData) ? clientsData : []);
    } catch {
      setError('Failed to load projects. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Memoized filtered projects (status filter + client filter + search)
  const filteredProjects = useMemo(() => {
    let result = getFilteredProjects(); // Apply status filter from store
    
    // Apply client filter
    if (clientFilter) {
      result = result.filter(project => project['Client ID'] === clientFilter);
    }
    
    // Apply search filter
    if (searchTerm) {
      result = result.filter(project =>
        project['Project Name']?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        project['Project Address']?.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }
    
    return result;
  }, [projects, filter, clientFilter, searchTerm]);

  // Get client name for filter badge
  const getFilteredClientName = () => {
    if (!clientFilter) return null;
    const client = clients.find(c => c['Client ID'] === clientFilter || c['ID'] === clientFilter);
    return client?.['Full Name'] || client?.['Client Name'] || clientFilter;
  };

  const clearClientFilter = () => {
    setClientFilter(null);
  };

  // Get client name for a project card
  const getClientName = (clientId) => {
    if (!clientId) return 'Unknown Client';
    const client = clients.find(c => c['Client ID'] === clientId || c['ID'] === clientId);
    return client?.['Full Name'] || client?.['Client Name'] || clientId;
  };

  const getProgressColor = (progress) => {
    if (progress >= 75) return '#059669';
    if (progress >= 50) return '#2563EB';
    if (progress >= 25) return '#D97706';
    return '#DC2626';
  };

  const calculateProgress = (project) => {
    // Calculate progress based on status or actual progress field
    if (project.Progress !== undefined) return project.Progress;
    
    switch (project.Status?.toLowerCase()) {
      case 'completed':
        return 100;
      case 'in progress':
      case 'active':
        return 60;
      case 'planning':
        return 20;
      default:
        return 0;
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'No deadline';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  if (loading) {
    return <LoadingState message="Loading projects..." />;
  }

  if (error) {
    return (
      <EmptyState
        title="Failed to load projects"
        description={error}
        action={
          <Button onClick={fetchProjects}>
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
        <div className="flex items-center justify-between mb-4">
          <div>
            <div className="flex items-center gap-3 mb-1">
              <h1 className="text-2xl font-semibold text-gray-900">Projects</h1>
              {clientFilter && (
                <Badge variant="info" className="flex items-center gap-2">
                  <span>Client: {getFilteredClientName()}</span>
                  <button
                    onClick={clearClientFilter}
                    className="text-blue-900 hover:text-blue-950 text-lg leading-none px-0.5"
                  >
                    ×
                  </button>
                </Badge>
              )}
            </div>
            <p className="text-gray-600 text-sm">
              {clientFilter 
                ? `Showing projects for ${getFilteredClientName()}`
                : 'Track and manage all your construction projects'}
            </p>
          </div>
          <Button onClick={() => { /* TODO: Add new project modal */ }}>
            <Plus size={18} />
            New Project
          </Button>
        </div>

        {/* Search Bar */}
        <div className="relative mt-4">
          <Search size={18} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-500" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search projects..."
            className="w-full pl-11 pr-3.5 py-2.5 border border-gray-300 rounded-lg text-sm text-gray-900 focus:border-blue-600 focus:ring-4 focus:ring-blue-600/10 transition-all"
          />
        </div>
      </div>

      {/* Projects Grid */}
      <div className="flex-1 overflow-y-auto p-8">
        {filteredProjects.length === 0 ? (
          <EmptyState
            icon={FolderKanban}
            title="No projects found"
            description={searchTerm ? "Try adjusting your search" : "Create your first project to get started"}
          />
        ) : (
          <div className="grid grid-cols-[repeat(auto-fill,minmax(380px,1fr))] gap-6 max-w-[1400px] mx-auto">
            {filteredProjects.map((project) => {
              const progress = calculateProgress(project);
              const progressColor = getProgressColor(progress);

              return (
                <Card
                  key={project['Project ID']}
                  onClick={() => navigateToProject(project['Project ID'])}
                  className="cursor-pointer transition-all hover:shadow-lg hover:-translate-y-0.5"
                >
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between mb-4">
                      <div className="w-12 h-12 rounded-lg bg-linear-to-br from-blue-600 to-blue-700 flex items-center justify-center shrink-0 shadow-md shadow-blue-600/30">
                        <FolderKanban size={24} className="text-white" />
                      </div>
                      <StatusBadge status={project.Status || 'planning'} />
                    </div>

                    <h3 className="text-[17px] font-semibold text-gray-900 mb-3">
                      {project['Project Name'] || 'Unnamed Project'}
                    </h3>

                    <div className="flex flex-col gap-2.5 mb-4">
                      <div className="flex items-center gap-2 text-[13px] text-gray-600">
                        <MapPin size={16} className="text-blue-600" />
                        {project['Project Address'] || 'No address'}
                      </div>
                      <div className="flex items-center gap-2 text-[13px] text-gray-600">
                        <Users size={16} className="text-blue-600" />
                        Client: {getClientName(project['Client ID'])}
                      </div>
                      <div className="flex items-center gap-2 text-[13px] text-gray-600">
                        <Calendar size={16} className="text-blue-600" />
                        {project['Start Date'] ? `Started: ${formatDate(project['Start Date'])}` : 'No start date'}
                      </div>
                    </div>

                    {/* Progress Bar */}
                    <div className="pt-4 border-t border-gray-100">
                      <div className="flex justify-between items-center mb-2">
                        <span className="text-[13px] font-medium text-gray-600">Progress</span>
                        <span 
                          className="text-[13px] font-semibold" 
                          style={{ color: progressColor }}
                        >
                          {progress}%
                        </span>
                      </div>
                      <div className="w-full h-2 bg-gray-100 rounded overflow-hidden">
                        <div 
                          className="h-full rounded transition-all duration-300"
                          style={{ 
                            width: `${progress}%`,
                            backgroundColor: progressColor
                          }}
                        />
                      </div>
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
