import { create } from 'zustand';
import api from '../lib/api';

/**
 * Clients Store - Dedicated state management for client data
 * 
 * Benefits:
 * - Isolated re-renders (only components using clients re-render)
 * - Data caching (prevents unnecessary API calls)
 * - Better performance vs global appStore
 * - Encapsulates all API knowledge (hooks don't touch api directly)
 */

const useClientsStore = create((set, get) => ({
  // State
  clients: [],
  loading: false,
  error: null,
  lastFetched: null,
  
  // Cache management
  CACHE_DURATION: 5 * 60 * 1000, // 5 minutes
  
  // Actions
  setClients: (clients) => set({ clients, lastFetched: Date.now(), error: null }),
  
  setLoading: (loading) => set({ loading }),
  
  setError: (error) => set({ error, loading: false }),
  
  clearError: () => set({ error: null }),
  
  // Get client by ID
  getClientById: (id) => {
    const { clients } = get();
    return clients.find(c => 
      (c.ID || c['Client ID']) === id || 
      (c.id || c['Client ID']) === id
    );
  },
  
  // Add new client (optimistic update)
  addClient: (client) => set((state) => ({
    clients: [client, ...state.clients]
  })),
  
  // Update client (optimistic update)
  updateClient: (id, updates) => set((state) => ({
    clients: state.clients.map(c => {
      const clientId = c.ID || c['Client ID'] || c.id;
      return clientId === id ? { ...c, ...updates } : c;
    })
  })),
  
  // Delete client (optimistic update)
  deleteClient: (id) => set((state) => ({
    clients: state.clients.filter(c => {
      const clientId = c.ID || c['Client ID'] || c.id;
      return clientId !== id;
    })
  })),
  
  // Check if cache is valid
  isCacheValid: () => {
    const { lastFetched, CACHE_DURATION } = get();
    if (!lastFetched) return false;
    return Date.now() - lastFetched < CACHE_DURATION;
  },
  
  // Fetch all clients (with cache check)
  fetchClients: async () => {
    const { isCacheValid, setClients, setLoading, setError } = get();
    if (isCacheValid()) return; // Cache still valid
    
    try {
      setLoading(true);
      const data = await api.getClients();
      setClients(data);
    } catch (err) {
      console.error('clientsStore fetch error:', err);
      setError(err.message || 'Failed to fetch clients');
    } finally {
      setLoading(false);
    }
  },
  
  // Fetch single client by ID
  fetchClientById: async (clientId) => {
    if (!clientId) return;
    
    const { setLoading, setError, addClient } = get();
    
    try {
      setLoading(true);
      const data = await api.getClient(clientId);
      if (data) {
        addClient(data);
      }
    } catch (err) {
      console.error('clientsStore fetchById error:', err);
      setError(err.message || 'Failed to fetch client');
    } finally {
      setLoading(false);
    }
  },
  
  // Clear all data
  clear: () => set({
    clients: [],
    loading: false,
    error: null,
    lastFetched: null
  })
}));

export { useClientsStore };
