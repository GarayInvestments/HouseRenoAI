import { create } from 'zustand';
import api from '../lib/api';

/**
 * Permits Store - Dedicated state management for permit data
 * 
 * Benefits:
 * - Isolated re-renders (only components using permits re-render)
 * - Data caching (prevents unnecessary API calls)
 * - Better performance vs global appStore
 * - Encapsulates all API knowledge (hooks don't touch api directly)
 */

const usePermitsStore = create((set, get) => ({
  // State
  permits: [],
  loading: false,
  error: null,
  lastFetched: null,
  filter: 'all', // all, pending, approved, expired, rejected
  
  // Cache management
  CACHE_DURATION: 5 * 60 * 1000, // 5 minutes
  
  // Actions
  setPermits: (permits) => set({ permits, lastFetched: Date.now(), error: null }),
  
  setLoading: (loading) => set({ loading }),
  
  setError: (error) => set({ error, loading: false }),
  
  setFilter: (filter) => set({ filter }),
  
  clearError: () => set({ error: null }),
  
  // Get filtered permits
  getFilteredPermits: () => {
    const { permits, filter } = get();
    
    if (filter === 'all') return permits;
    
    return permits.filter(permit => {
      // Handle both legacy (Permit Status) and new (status) field names
      const status = (
        permit.status || 
        permit.Status || 
        permit['Permit Status'] || 
        ''
      ).toLowerCase();
      
      switch (filter) {
        case 'pending':
          return status === 'pending' || status === 'submitted' || status === 'in review' || status === 'draft';
        case 'approved':
          return status === 'approved' || status === 'active';
        case 'expired':
          return status === 'expired';
        case 'rejected':
          return status === 'rejected' || status === 'denied' || status === 'cancelled';
        default:
          return true;
      }
    });
  },
  
  // Get permit by ID
  getPermitById: (id) => {
    const { permits } = get();
    return permits.find(p => 
      p.ID === id ||
      p['Permit ID'] === id || 
      p.id === id ||
      p.permit_id === id
    );
  },
  
  // Get permits by project ID
  getPermitsByProject: (projectId) => {
    const { permits } = get();
    return permits.filter(p => {
      const pId = p['Project ID'] || p.project_id || p.projectId;
      return pId === projectId;
    });
  },
  
  // Get permits by client ID
  getPermitsByClient: (clientId) => {
    const { permits } = get();
    return permits.filter(p => {
      const cId = p['Client ID'] || p.client_id || p.clientId;
      return cId === clientId;
    });
  },
  
  // Add new permit (optimistic update)
  addPermit: (permit) => set((state) => ({
    permits: [permit, ...state.permits]
  })),
  
  // Update permit (optimistic update)
  updatePermit: (id, updates) => set((state) => ({
    permits: state.permits.map(p => {
      const permitId = p.ID || p['Permit ID'] || p.id || p.permit_id;
      return permitId === id ? { ...p, ...updates } : p;
    })
  })),
  
  // Delete permit (optimistic update)
  deletePermit: (id) => set((state) => ({
    permits: state.permits.filter(p => {
      const permitId = p.ID || p['Permit ID'] || p.id || p.permit_id;
      return permitId !== id;
    })
  })),
  
  // Check if cache is valid
  isCacheValid: () => {
    const { lastFetched, CACHE_DURATION } = get();
    if (!lastFetched) return false;
    return Date.now() - lastFetched < CACHE_DURATION;
  },
  
  // Fetch all permits (with cache check)
  fetchPermits: async () => {
    const { isCacheValid, setPermits, setLoading, setError } = get();
    if (isCacheValid()) return; // Cache still valid
    
    try {
      setLoading(true);
      const data = await api.getPermits();
      setPermits(data);
    } catch (err) {
      console.error('permitsStore fetch error:', err);
      setError(err.message || 'Failed to fetch permits');
    } finally {
      setLoading(false);
    }
  },
  
  // Fetch single permit by ID
  fetchPermitById: async (permitId) => {
    if (!permitId) return;
    
    const { setLoading, setError, addPermit } = get();
    
    try {
      setLoading(true);
      const data = await api.getPermit(permitId);
      if (data) {
        addPermit(data);
      }
    } catch (err) {
      console.error('permitsStore fetchById error:', err);
      setError(err.message || 'Failed to fetch permit');
    } finally {
      setLoading(false);
    }
  },
  
  // Clear all data
  clear: () => set({
    permits: [],
    loading: false,
    error: null,
    lastFetched: null,
    filter: 'all'
  })
}));

export { usePermitsStore };
