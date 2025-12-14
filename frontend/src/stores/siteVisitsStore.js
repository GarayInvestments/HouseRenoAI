import { create } from 'zustand';
import api from '../lib/api';

/**
 * Site Visits Store
 * Manages site visit data, filtering, and CRUD operations
 * Supports photo uploads, deficiency tracking, and follow-up actions
 */

const useSiteVisitsStore = create((set, get) => ({
  // State
  siteVisits: [],
  loading: false,
  error: null,
  filter: 'all', // 'all', 'scheduled', 'in-progress', 'completed', 'cancelled'
  selectedVisit: null,

  // Actions
  setFilter: (filter) => set({ filter }),
  
  setSelectedVisit: (visit) => set({ selectedVisit: visit }),

  // Fetch all site visits
  fetchSiteVisits: async () => {
    set({ loading: true, error: null });
    try {
      const data = await api.getSiteVisits();
      const visitsArray = data?.items || data || [];
      set({ 
        siteVisits: Array.isArray(visitsArray) ? visitsArray : [], 
        loading: false 
      });
      return visitsArray;
    } catch (error) {
      console.error('Failed to fetch site visits:', error);
      set({ 
        error: error.message || 'Failed to fetch site visits', 
        loading: false,
        siteVisits: []
      });
      return [];
    }
  },

  // Fetch single site visit
  fetchSiteVisit: async (visitId) => {
    set({ loading: true, error: null });
    try {
      const visit = await api.getSiteVisit(visitId);
      set({ selectedVisit: visit, loading: false });
      return visit;
    } catch (error) {
      console.error('Failed to fetch site visit:', error);
      set({ 
        error: error.message || 'Failed to fetch site visit', 
        loading: false 
      });
      throw error;
    }
  },

  // Fetch site visits by project
  fetchSiteVisitsByProject: async (projectId) => {
    set({ loading: true, error: null });
    try {
      const data = await api.getSiteVisitsByProject(projectId);
      const visitsArray = data?.items || data || [];
      set({ 
        siteVisits: Array.isArray(visitsArray) ? visitsArray : [], 
        loading: false 
      });
      return visitsArray;
    } catch (error) {
      console.error('Failed to fetch site visits by project:', error);
      set({ 
        error: error.message || 'Failed to fetch site visits', 
        loading: false,
        siteVisits: []
      });
      return [];
    }
  },

  // Create site visit
  createSiteVisit: async (visitData) => {
    set({ loading: true, error: null });
    try {
      const newVisit = await api.createSiteVisit(visitData);
      set((state) => ({
        siteVisits: [...state.siteVisits, newVisit],
        loading: false,
        selectedVisit: newVisit
      }));
      return newVisit;
    } catch (error) {
      console.error('Failed to create site visit:', error);
      set({ 
        error: error.message || 'Failed to create site visit', 
        loading: false 
      });
      throw error;
    }
  },

  // Update site visit
  updateSiteVisit: async (visitId, visitData) => {
    set({ loading: true, error: null });
    try {
      const updatedVisit = await api.updateSiteVisit(visitId, visitData);
      set((state) => ({
        siteVisits: state.siteVisits.map(visit => 
          (visit.visit_id === visitId || visit.id === visitId) 
            ? updatedVisit 
            : visit
        ),
        selectedVisit: updatedVisit,
        loading: false
      }));
      return updatedVisit;
    } catch (error) {
      console.error('Failed to update site visit:', error);
      set({ 
        error: error.message || 'Failed to update site visit', 
        loading: false 
      });
      throw error;
    }
  },

  // Delete site visit
  deleteSiteVisit: async (visitId) => {
    set({ loading: true, error: null });
    try {
      await api.deleteSiteVisit(visitId);
      set((state) => ({
        siteVisits: state.siteVisits.filter(visit => 
          visit.visit_id !== visitId && visit.id !== visitId
        ),
        selectedVisit: null,
        loading: false
      }));
    } catch (error) {
      console.error('Failed to delete site visit:', error);
      set({ 
        error: error.message || 'Failed to delete site visit', 
        loading: false 
      });
      throw error;
    }
  },

  // Get filtered site visits based on current filter
  getFilteredSiteVisits: () => {
    const { siteVisits, filter } = get();
    
    if (filter === 'all') {
      return siteVisits;
    }
    
    return siteVisits.filter(visit => {
      const status = (visit.status || visit['Visit Status'] || '').toLowerCase();
      
      switch(filter) {
        case 'scheduled':
          return status === 'scheduled';
        case 'in-progress':
          return status === 'in-progress';
        case 'completed':
          return status === 'completed';
        case 'cancelled':
          return status === 'cancelled';
        default:
          return true;
      }
    });
  },

  // Get site visit statistics
  getSiteVisitStats: () => {
    const { siteVisits } = get();
    
    const stats = {
      total: siteVisits.length,
      scheduled: 0,
      inProgress: 0,
      completed: 0,
      cancelled: 0,
      withDeficiencies: 0,
      withPhotos: 0
    };
    
    siteVisits.forEach(visit => {
      const status = (visit.status || visit['Visit Status'] || '').toLowerCase();
      const deficiencies = visit.deficiencies || visit['Deficiencies'] || [];
      const photos = visit.photos || visit['Photos'] || [];
      
      if (status === 'scheduled') stats.scheduled++;
      else if (status === 'in-progress') stats.inProgress++;
      else if (status === 'completed') stats.completed++;
      else if (status === 'cancelled') stats.cancelled++;
      
      if (Array.isArray(deficiencies) && deficiencies.length > 0) {
        stats.withDeficiencies++;
      }
      
      if (Array.isArray(photos) && photos.length > 0) {
        stats.withPhotos++;
      }
    });
    
    return stats;
  },

  // Clear error
  clearError: () => set({ error: null }),

  // Reset store
  reset: () => set({
    siteVisits: [],
    loading: false,
    error: null,
    filter: 'all',
    selectedVisit: null
  })
}));

export default useSiteVisitsStore;
