import { create } from 'zustand';
import api from '../lib/api';

/**
 * Payments Store
 * Manages payment data, filtering, and CRUD operations
 * Integrates with QuickBooks for payment sync
 */

const usePaymentsStore = create((set, get) => ({
  // State
  payments: [],
  loading: false,
  error: null,
  filter: 'all', // 'all', 'pending', 'cleared', 'failed', 'refunded'
  selectedPayment: null,
  qbSyncStatus: 'idle', // 'idle', 'syncing', 'success', 'error'
  qbSyncError: null,
  lastSyncTime: null,
  nextSyncTime: null,
  syncStatusData: null,

  // Actions
  setFilter: (filter) => set({ filter }),
  
  setSelectedPayment: (payment) => set({ selectedPayment: payment }),

  // Fetch all payments (from cache)
  fetchPayments: async () => {
    set({ loading: true, error: null });
    try {
      const url = '/v1/quickbooks/sync/cache/payments';
      console.log('[DEBUG] Fetching payments from:', url);
      
      // Fetch from cache endpoint
      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('supabase_token')}`
        }
      });
      
      console.log('[DEBUG] Response status:', response.status);
      console.log('[DEBUG] Response content-type:', response.headers.get('content-type'));
      
      if (!response.ok) {
        const text = await response.text();
        console.error('[DEBUG] Error response:', text.substring(0, 200));
        throw new Error(`Failed to fetch payments from cache: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('[DEBUG] Received data:', data);
      const paymentsArray = data?.payments || [];
      
      set({ 
        payments: Array.isArray(paymentsArray) ? paymentsArray : [], 
        loading: false 
      });
      
      // Fetch sync status
      await get().fetchSyncStatus();
      
      return paymentsArray;
    } catch (error) {
      console.error('Failed to fetch payments:', error);
      set({ 
        error: error.message || 'Failed to fetch payments', 
        loading: false,
        payments: []
      });
      return [];
    }
  },
  
  // Fetch sync status
  fetchSyncStatus: async () => {
    try {
      const response = await fetch('/v1/quickbooks/sync/status', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('supabase_token')}`
        }
      });
      
      if (!response.ok) return;
      
      const data = await response.json();
      const paymentStatus = data?.status?.find(s => s.entity_type === 'payments');
      
      if (paymentStatus) {
        set({ 
          lastSyncTime: paymentStatus.last_sync_at,
          syncStatusData: paymentStatus
        });
      }
      
      // Fetch scheduler status for next sync time
      const schedResponse = await fetch('/v1/quickbooks/sync/scheduler', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('supabase_token')}`
        }
      });
      
      if (schedResponse.ok) {
        const schedData = await schedResponse.json();
        set({ nextSyncTime: schedData.next_run_time });
      }
    } catch (error) {
      console.error('Failed to fetch sync status:', error);
    }
  },

  // Create payment
  createPayment: async (paymentData) => {
    set({ loading: true, error: null });
    try {
      const newPayment = await api.createPayment(paymentData);
      set((state) => ({
        payments: [...state.payments, newPayment],
        loading: false,
        selectedPayment: newPayment
      }));
      return newPayment;
    } catch (error) {
      console.error('Failed to create payment:', error);
      set({ 
        error: error.message || 'Failed to create payment', 
        loading: false 
      });
      throw error;
    }
  },

  // Sync with QuickBooks
  syncWithQuickBooks: async () => {
    set({ qbSyncStatus: 'syncing', qbSyncError: null });
    try {
      const response = await fetch('/v1/quickbooks/sync/payments', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('supabase_token')}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) throw new Error('Sync failed');
      
      const { fetchPayments } = get();
      await fetchPayments();
      set({ qbSyncStatus: 'success' });
      
      // Reset status after 3 seconds
      setTimeout(() => {
        set({ qbSyncStatus: 'idle' });
      }, 3000);
    } catch (error) {
      console.error('QuickBooks sync failed:', error);
      set({ 
        qbSyncStatus: 'error',
        qbSyncError: error.message || 'Sync failed'
      });
      
      // Reset status after 5 seconds
      setTimeout(() => {
        set({ qbSyncStatus: 'idle', qbSyncError: null });
      }, 5000);
    }
  },

  // Get filtered payments based on current filter
  getFilteredPayments: () => {
    const { payments, filter } = get();
    
    if (filter === 'all') {
      return payments;
    }
    
    return payments.filter(payment => {
      const status = (payment.status || payment['Payment Status'] || '').toLowerCase();
      return status === filter;
    });
  },

  // Get payment statistics
  getPaymentStats: () => {
    const { payments } = get();
    
    const stats = {
      total: payments.length,
      pending: 0,
      cleared: 0,
      failed: 0,
      totalAmount: 0,
      clearedAmount: 0
    };
    
    payments.forEach(payment => {
      const status = (payment.status || payment['Payment Status'] || '').toLowerCase();
      const amount = parseFloat(payment.amount || payment['Amount'] || 0);
      
      stats.totalAmount += amount;
      
      if (status === 'pending') stats.pending++;
      else if (status === 'cleared') {
        stats.cleared++;
        stats.clearedAmount += amount;
      } else if (status === 'failed') stats.failed++;
    });
    
    return stats;
  },

  // Clear error
  clearError: () => set({ error: null }),

  // Reset store
  reset: () => set({
    payments: [],
    loading: false,
    error: null,
    filter: 'all',
    selectedPayment: null,
    qbSyncStatus: 'idle',
    qbSyncError: null
  })
}));

export default usePaymentsStore;
