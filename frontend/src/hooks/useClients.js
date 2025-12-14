import { useEffect } from 'react';
import { useClientsStore } from '../stores/clientsStore';

/**
 * useClients - Thin adapter around clientsStore
 * Delegates to store for all data and fetch operations
 * Hooks never import api - stores encapsulate all API knowledge
 * 
 * @returns {Object} { clients, loading, error, refetch }
 */
export function useClients() {
  const clients = useClientsStore((state) => state.clients);
  const loading = useClientsStore((state) => state.loading);
  const error = useClientsStore((state) => state.error);
  const fetchClients = useClientsStore((state) => state.fetchClients);

  useEffect(() => {
    fetchClients();
  }, [fetchClients]);

  return { 
    clients, 
    loading, 
    error, 
    refetch: fetchClients 
  };
}

/**
 * useClient - Get single client by ID from store
 * Triggers fetch if client not in store
 * 
 * @param {string} clientId - Client UUID
 * @returns {Object} { client, loading, error, refetch }
 */
export function useClient(clientId) {
  const getClientById = useClientsStore((state) => state.getClientById);
  const loading = useClientsStore((state) => state.loading);
  const error = useClientsStore((state) => state.error);
  const fetchClientById = useClientsStore((state) => state.fetchClientById);

  const client = getClientById(clientId);

  useEffect(() => {
    if (!client && clientId) {
      fetchClientById(clientId);
    }
  }, [clientId, client, fetchClientById]);

  return { 
    client, 
    loading, 
    error, 
    refetch: () => fetchClientById(clientId) 
  };
}
