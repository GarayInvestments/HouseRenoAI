import { create } from 'zustand';
import api from '../lib/api';

/**
 * Projects Store - Dedicated state management for project data
 * 
 * Benefits:
 * - Isolated re-renders (only components using projects re-render)
 * - Data caching (prevents unnecessary API calls)
 * - Better performance vs global appStore
 * - Encapsulates all API knowledge (hooks don't touch api directly)
 */

const useProjectsStore = create((set, get) => ({
  // State
  projects: [],
  loading: false,
  error: null,
  lastFetched: null,
  filter: 'all', // all, active, completed, pending
  
  // Cache management
  CACHE_DURATION: 5 * 60 * 1000, // 5 minutes
  
  // Actions
  setProjects: (projects) => set({ projects, lastFetched: Date.now(), error: null }),
  
  setLoading: (loading) => set({ loading }),
  
  setError: (error) => set({ error, loading: false }),
  
  setFilter: (filter) => set({ filter }),
  
  clearError: () => set({ error: null }),
  
  // Get filtered projects
  getFilteredProjects: () => {
    const { projects, filter } = get();
    
    if (filter === 'all') return projects;
    
    return projects.filter(project => {
      const status = (project.status || project.Status || '').toLowerCase();
      
      switch (filter) {
        case 'active':
          return status === 'active' || status === 'in progress';
        case 'completed':
          return status === 'completed' || status === 'done';
        case 'pending':
          return status === 'pending' || status === 'planned';
        default:
          return true;
      }
    });
  },
  
  // Get project by ID
  getProjectById: (id) => {
    const { projects } = get();
    return projects.find(p => 
      (p.ID || p['Project ID']) === id || 
      (p.id || p['Project ID']) === id
    );
  },
  
  // Add new project (optimistic update)
  addProject: (project) => set((state) => ({
    projects: [project, ...state.projects]
  })),
  
  // Update project (optimistic update)
  updateProject: (id, updates) => set((state) => ({
    projects: state.projects.map(p => {
      const projectId = p.ID || p['Project ID'] || p.id;
      return projectId === id ? { ...p, ...updates } : p;
    })
  })),
  
  // Delete project (optimistic update)
  deleteProject: (id) => set((state) => ({
    projects: state.projects.filter(p => {
      const projectId = p.ID || p['Project ID'] || p.id;
      return projectId !== id;
    })
  })),
  
  // Check if cache is valid
  isCacheValid: () => {
    const { lastFetched, CACHE_DURATION } = get();
    if (!lastFetched) return false;
    return Date.now() - lastFetched < CACHE_DURATION;
  },
  
  // Fetch all projects (with cache check)
  fetchProjects: async () => {
    const { isCacheValid, setProjects, setLoading, setError } = get();
    if (isCacheValid()) return; // Cache still valid
    
    try {
      setLoading(true);
      const data = await api.getProjects();
      setProjects(data);
    } catch (err) {
      console.error('projectsStore fetch error:', err);
      setError(err.message || 'Failed to fetch projects');
    } finally {
      setLoading(false);
    }
  },
  
  // Fetch single project by ID
  fetchProjectById: async (projectId) => {
    if (!projectId) return;
    
    const { setLoading, setError, addProject } = get();
    
    try {
      setLoading(true);
      const data = await api.getProject(projectId);
      if (data) {
        addProject(data);
      }
    } catch (err) {
      console.error('projectsStore fetchById error:', err);
      setError(err.message || 'Failed to fetch project');
    } finally {
      setLoading(false);
    }
  },
  
  // Clear all data
  clear: () => set({
    projects: [],
    loading: false,
    error: null,
    lastFetched: null,
    filter: 'all'
  })
}));

export { useProjectsStore };
