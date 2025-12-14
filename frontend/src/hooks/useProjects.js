import { useEffect } from 'react';
import { useProjectsStore } from '../stores/projectsStore';

/**
 * useProjects - Thin adapter around projectsStore
 * Delegates to store for all data and fetch operations
 * Hooks never import api - stores encapsulate all API knowledge
 * 
 * @returns {Object} { projects, loading, error, refetch }
 */
export function useProjects() {
  const projects = useProjectsStore((state) => state.projects);
  const loading = useProjectsStore((state) => state.loading);
  const error = useProjectsStore((state) => state.error);
  const fetchProjects = useProjectsStore((state) => state.fetchProjects);

  useEffect(() => {
    fetchProjects();
  }, [fetchProjects]);

  return { 
    projects, 
    loading, 
    error, 
    refetch: fetchProjects 
  };
}

/**
 * useProject - Get single project by ID from store
 * Triggers fetch if project not in store
 * 
 * @param {string} projectId - Project UUID
 * @returns {Object} { project, loading, error, refetch }
 */
export function useProject(projectId) {
  const getProjectById = useProjectsStore((state) => state.getProjectById);
  const loading = useProjectsStore((state) => state.loading);
  const error = useProjectsStore((state) => state.error);
  const fetchProjectById = useProjectsStore((state) => state.fetchProjectById);

  const project = getProjectById(projectId);

  useEffect(() => {
    if (!project && projectId) {
      fetchProjectById(projectId);
    }
  }, [projectId, project, fetchProjectById]);

  return { 
    project, 
    loading, 
    error, 
    refetch: () => fetchProjectById(projectId) 
  };
}
