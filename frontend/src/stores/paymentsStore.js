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

  // Actions
  setFilter: (filter) => set({ filter }),
  
  setSelectedPayment: (payment) => set({ selectedPayment: payment }),

  // Fetch all payments
  fetchPayments: async () => {
    set({ loading: true, error: null });
    try {
      const data = await api.getPayments();
      const paymentsArray = data?.items || data || [];
      set({ 
        payments: Array.isArray(paymentsArray) ? paymentsArray : [], 
        loading: false 
      });
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
      await api.syncPayments();
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
