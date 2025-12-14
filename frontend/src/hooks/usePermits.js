import { useEffect } from 'react';
import { usePermitsStore } from '../stores/permitsStore';

/**
 * usePermits - Thin adapter around permitsStore
 * Delegates to store for all data and fetch operations
 * Hooks never import api - stores encapsulate all API knowledge
 * 
 * @returns {Object} { permits, loading, error, refetch }
 */
export function usePermits() {
  const permits = usePermitsStore((state) => state.permits);
  const loading = usePermitsStore((state) => state.loading);
  const error = usePermitsStore((state) => state.error);
  const fetchPermits = usePermitsStore((state) => state.fetchPermits);

  useEffect(() => {
    fetchPermits();
  }, [fetchPermits]);

  return { 
    permits, 
    loading, 
    error, 
    refetch: fetchPermits 
  };
}

/**
 * usePermit - Get single permit by ID from store
 * Triggers fetch if permit not in store
 * 
 * @param {string} permitId - Permit UUID
 * @returns {Object} { permit, loading, error, refetch }
 */
export function usePermit(permitId) {
  const getPermitById = usePermitsStore((state) => state.getPermitById);
  const loading = usePermitsStore((state) => state.loading);
  const error = usePermitsStore((state) => state.error);
  const fetchPermitById = usePermitsStore((state) => state.fetchPermitById);

  const permit = getPermitById(permitId);

  useEffect(() => {
    if (!permit && permitId) {
      fetchPermitById(permitId);
    }
  }, [permitId, permit, fetchPermitById]);

  return { 
    permit, 
    loading, 
    error, 
    refetch: () => fetchPermitById(permitId) 
  };
}
