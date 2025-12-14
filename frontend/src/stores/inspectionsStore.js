import { create } from 'zustand';
import api from '../lib/api';

/**
 * Inspections Store - Dedicated state management for inspection data
 * 
 * Features:
 * - Data caching (5-minute TTL)
 * - Filter by status, inspector, project, date range
 * - Full CRUD operations
 * - Deficiencies and photos management
 */

const useInspectionsStore = create((set, get) => ({
  // State
  inspections: [],
  loading: false,
  error: null,
  lastFetched: null,
  filter: 'all', // all, scheduled, in-progress, completed, failed, cancelled
  
  // Cache management
  CACHE_DURATION: 5 * 60 * 1000, // 5 minutes
  
  // Actions
  setInspections: (inspections) => set({ inspections, lastFetched: Date.now(), error: null }),
  
  setLoading: (loading) => set({ loading }),
  
  setError: (error) => set({ error, loading: false }),
  
  setFilter: (filter) => set({ filter }),
  
  clearError: () => set({ error: null }),
  
  // Get filtered inspections
  getFilteredInspections: () => {
    const { inspections, filter } = get();
    
    if (filter === 'all') return inspections;
    
    return inspections.filter(inspection => {
      const status = (
        inspection.status || 
        inspection['Inspection Status'] || 
        ''
      ).toLowerCase();
      
      if (filter === 'scheduled') return status === 'scheduled';
      if (filter === 'in-progress') return status === 'in-progress';
      if (filter === 'completed') return status === 'completed';
      if (filter === 'failed') return status === 'failed';
      if (filter === 'cancelled') return status === 'cancelled';
      
      return true;
    });
  },
  
  // Get inspection by ID
  getInspectionById: (id) => {
    const { inspections } = get();
    return inspections.find(i => 
      i.inspection_id === id || 
      i['Inspection ID'] === id ||
      i.business_id === id
    );
  },
  
  // Get inspections by permit
  getInspectionsByPermit: (permitId) => {
    const { inspections } = get();
    return inspections.filter(i => 
      i.permit_id === permitId || 
      i['Permit ID'] === permitId
    );
  },
  
  // Get inspections by project
  getInspectionsByProject: (projectId) => {
    const { inspections } = get();
    return inspections.filter(i => 
      i.project_id === projectId || 
      i['Project ID'] === projectId
    );
  },
  
  // Check if cache is fresh
  isCacheFresh: () => {
    const { lastFetched, CACHE_DURATION } = get();
    if (!lastFetched) return false;
    return Date.now() - lastFetched < CACHE_DURATION;
  },
  
  // Fetch all inspections (with optional params)
  fetchInspections: async (params = {}) => {
    const { isCacheFresh, setLoading, setInspections, setError } = get();
    
    // Use cache if fresh and no params
    if (Object.keys(params).length === 0 && isCacheFresh()) {
      return get().inspections;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await api.getInspections(params);
      const inspectionsData = response?.items || response || [];
      setInspections(inspectionsData);
      return inspectionsData;
    } catch (err) {
      console.error('inspectionsStore fetch error:', err);
      setError(err.message || 'Failed to load inspections');
      return [];
    } finally {
      setLoading(false);
    }
  },
  
  // Fetch single inspection by ID
  fetchInspectionById: async (id) => {
    const { setLoading, setError } = get();
    
    setLoading(true);
    setError(null);
    
    try {
      const inspection = await api.getInspection(id);
      
      // Update cache with this inspection
      const { inspections } = get();
      const updated = inspections.map(i => 
        (i.inspection_id === id || i.business_id === id) ? inspection : i
      );
      
      // If not found in cache, add it
      if (!updated.find(i => i.inspection_id === inspection.inspection_id)) {
        updated.push(inspection);
      }
      
      set({ inspections: updated, lastFetched: Date.now() });
      return inspection;
    } catch (err) {
      console.error('inspectionsStore fetchById error:', err);
      setError(err.message || 'Failed to load inspection');
      return null;
    } finally {
      setLoading(false);
    }
  },
  
  // Create new inspection
  createInspection: async (inspectionData) => {
    const { setLoading, setError, inspections } = get();
    
    setLoading(true);
    setError(null);
    
    try {
      const newInspection = await api.createInspection(inspectionData);
      
      // Add to cache
      set({ 
        inspections: [newInspection, ...inspections],
        lastFetched: Date.now()
      });
      
      return newInspection;
    } catch (err) {
      console.error('inspectionsStore create error:', err);
      setError(err.message || 'Failed to create inspection');
      throw err;
    } finally {
      setLoading(false);
    }
  },
  
  // Update inspection
  updateInspection: async (id, updates) => {
    const { setLoading, setError, inspections } = get();
    
    setLoading(true);
    setError(null);
    
    try {
      const updated = await api.updateInspection(id, updates);
      
      // Update cache
      const newInspections = inspections.map(i =>
        (i.inspection_id === id || i.business_id === id) ? updated : i
      );
      
      set({ inspections: newInspections, lastFetched: Date.now() });
      return updated;
    } catch (err) {
      console.error('inspectionsStore update error:', err);
      setError(err.message || 'Failed to update inspection');
      throw err;
    } finally {
      setLoading(false);
    }
  },
  
  // Delete inspection
  deleteInspection: async (id) => {
    const { setLoading, setError, inspections } = get();
    
    setLoading(true);
    setError(null);
    
    try {
      await api.deleteInspection(id);
      
      // Remove from cache
      const newInspections = inspections.filter(i =>
        i.inspection_id !== id && i.business_id !== id
      );
      
      set({ inspections: newInspections, lastFetched: Date.now() });
      return true;
    } catch (err) {
      console.error('inspectionsStore delete error:', err);
      setError(err.message || 'Failed to delete inspection');
      throw err;
    } finally {
      setLoading(false);
    }
  },
  
  // Add photo to inspection
  addPhoto: async (inspectionId, photoData) => {
    const { setLoading, setError } = get();
    
    setLoading(true);
    setError(null);
    
    try {
      const updated = await api.addInspectionPhoto(inspectionId, photoData);
      
      // Update cache
      const { inspections } = get();
      const newInspections = inspections.map(i =>
        (i.inspection_id === inspectionId || i.business_id === inspectionId) ? updated : i
      );
      
      set({ inspections: newInspections, lastFetched: Date.now() });
      return updated;
    } catch (err) {
      console.error('inspectionsStore addPhoto error:', err);
      setError(err.message || 'Failed to add photo');
      throw err;
    } finally {
      setLoading(false);
    }
  },
  
  // Add deficiency to inspection
  addDeficiency: async (inspectionId, deficiencyData) => {
    const { setLoading, setError } = get();
    
    setLoading(true);
    setError(null);
    
    try {
      const updated = await api.addInspectionDeficiency(inspectionId, deficiencyData);
      
      // Update cache
      const { inspections } = get();
      const newInspections = inspections.map(i =>
        (i.inspection_id === inspectionId || i.business_id === inspectionId) ? updated : i
      );
      
      set({ inspections: newInspections, lastFetched: Date.now() });
      return updated;
    } catch (err) {
      console.error('inspectionsStore addDeficiency error:', err);
      setError(err.message || 'Failed to add deficiency');
      throw err;
    } finally {
      setLoading(false);
    }
  },
  
  // Clear cache (force refresh on next fetch)
  clearCache: () => set({ lastFetched: null }),
  
  // Reset store
  reset: () => set({
    inspections: [],
    loading: false,
    error: null,
    lastFetched: null,
    filter: 'all'
  })
}));

export default useInspectionsStore;
