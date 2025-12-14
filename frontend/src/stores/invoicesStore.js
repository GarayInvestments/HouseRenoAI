import { create } from 'zustand';
import api from '../lib/api';

/**
 * Invoices Store
 * Manages invoice data, filtering, and CRUD operations
 * Integrates with QuickBooks for invoice sync
 */

const useInvoicesStore = create((set, get) => ({
  // State
  invoices: [],
  loading: false,
  error: null,
  filter: 'all', // 'all', 'draft', 'sent', 'paid', 'overdue', 'void'
  selectedInvoice: null,
  qbSyncStatus: 'idle', // 'idle', 'syncing', 'success', 'error'
  qbSyncError: null,
  lastSyncTime: null,
  nextSyncTime: null,
  syncStatusData: null,

  // Actions
  setFilter: (filter) => set({ filter }),
  
  setSelectedInvoice: (invoice) => set({ selectedInvoice: invoice }),

  // Fetch all invoices (from cache)
  fetchInvoices: async () => {
    set({ loading: true, error: null });
    try {
      // Fetch from cache endpoint
      const response = await fetch('/v1/quickbooks/sync/cache/invoices', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('supabase_token')}`
        }
      });
      
      if (!response.ok) throw new Error('Failed to fetch invoices from cache');
      
      const data = await response.json();
      const invoicesArray = data?.invoices || [];
      
      set({ 
        invoices: Array.isArray(invoicesArray) ? invoicesArray : [], 
        loading: false 
      });
      
      // Fetch sync status
      await get().fetchSyncStatus();
      
      return invoicesArray;
    } catch (error) {
      console.error('Failed to fetch invoices:', error);
      set({ 
        error: error.message || 'Failed to fetch invoices', 
        loading: false,
        invoices: []
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
      const invoiceStatus = data?.status?.find(s => s.entity_type === 'invoices');
      
      if (invoiceStatus) {
        set({ 
          lastSyncTime: invoiceStatus.last_sync_at,
          syncStatusData: invoiceStatus
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

  // Fetch single invoice
  fetchInvoice: async (invoiceId) => {
    set({ loading: true, error: null });
    try {
      const invoice = await api.getInvoice(invoiceId);
      set({ selectedInvoice: invoice, loading: false });
      return invoice;
    } catch (error) {
      console.error('Failed to fetch invoice:', error);
      set({ 
        error: error.message || 'Failed to fetch invoice', 
        loading: false 
      });
      throw error;
    }
  },

  // Fetch invoices by project
  fetchInvoicesByProject: async (projectId) => {
    set({ loading: true, error: null });
    try {
      const data = await api.getInvoicesByProject(projectId);
      const invoicesArray = data?.items || data || [];
      set({ 
        invoices: Array.isArray(invoicesArray) ? invoicesArray : [], 
        loading: false 
      });
      return invoicesArray;
    } catch (error) {
      console.error('Failed to fetch invoices by project:', error);
      set({ 
        error: error.message || 'Failed to fetch invoices', 
        loading: false,
        invoices: []
      });
      return [];
    }
  },

  // Create invoice
  createInvoice: async (invoiceData) => {
    set({ loading: true, error: null });
    try {
      const newInvoice = await api.createInvoice(invoiceData);
      set((state) => ({
        invoices: [...state.invoices, newInvoice],
        loading: false,
        selectedInvoice: newInvoice
      }));
      return newInvoice;
    } catch (error) {
      console.error('Failed to create invoice:', error);
      set({ 
        error: error.message || 'Failed to create invoice', 
        loading: false 
      });
      throw error;
    }
  },

  // Update invoice
  updateInvoice: async (invoiceId, invoiceData) => {
    set({ loading: true, error: null });
    try {
      const updatedInvoice = await api.updateInvoice(invoiceId, invoiceData);
      set((state) => ({
        invoices: state.invoices.map(inv => 
          (inv.id === invoiceId || inv.invoice_id === invoiceId) 
            ? updatedInvoice 
            : inv
        ),
        selectedInvoice: updatedInvoice,
        loading: false
      }));
      return updatedInvoice;
    } catch (error) {
      console.error('Failed to update invoice:', error);
      set({ 
        error: error.message || 'Failed to update invoice', 
        loading: false 
      });
      throw error;
    }
  },

  // Delete invoice
  deleteInvoice: async (invoiceId) => {
    set({ loading: true, error: null });
    try {
      await api.deleteInvoice(invoiceId);
      set((state) => ({
        invoices: state.invoices.filter(inv => 
          inv.id !== invoiceId && inv.invoice_id !== invoiceId
        ),
        selectedInvoice: null,
        loading: false
      }));
    } catch (error) {
      console.error('Failed to delete invoice:', error);
      set({ 
        error: error.message || 'Failed to delete invoice', 
        loading: false 
      });
      throw error;
    }
  },

  // Sync with QuickBooks
  syncWithQuickBooks: async () => {
    set({ qbSyncStatus: 'syncing', qbSyncError: null });
    try {
      const response = await fetch('/v1/quickbooks/sync/invoices', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('supabase_token')}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) throw new Error('Sync failed');
      
      const { fetchInvoices } = get();
      await fetchInvoices();
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

  // Get filtered invoices based on current filter
  getFilteredInvoices: () => {
    const { invoices, filter } = get();
    
    if (filter === 'all') {
      return invoices;
    }
    
    return invoices.filter(invoice => {
      const status = (invoice.status || invoice['Invoice Status'] || '').toLowerCase();
      
      switch(filter) {
        case 'draft':
          return status === 'draft';
        case 'sent':
          return status === 'sent';
        case 'paid':
          return status === 'paid';
        case 'overdue':
          return status === 'overdue';
        case 'void':
          return status === 'void';
        default:
          return true;
      }
    });
  },

  // Get invoice statistics
  getInvoiceStats: () => {
    const { invoices } = get();
    
    const stats = {
      total: invoices.length,
      draft: 0,
      sent: 0,
      paid: 0,
      overdue: 0,
      totalAmount: 0,
      paidAmount: 0,
      outstanding: 0
    };
    
    invoices.forEach(invoice => {
      const status = (invoice.status || invoice['Invoice Status'] || '').toLowerCase();
      const amount = parseFloat(invoice.amount || invoice['Amount'] || 0);
      
      stats.totalAmount += amount;
      
      if (status === 'draft') stats.draft++;
      else if (status === 'sent') stats.sent++;
      else if (status === 'paid') {
        stats.paid++;
        stats.paidAmount += amount;
      } else if (status === 'overdue') {
        stats.overdue++;
        stats.outstanding += amount;
      }
    });
    
    stats.outstanding = stats.totalAmount - stats.paidAmount;
    
    return stats;
  },

  // Clear error
  clearError: () => set({ error: null }),

  // Reset store
  reset: () => set({
    invoices: [],
    loading: false,
    error: null,
    filter: 'all',
    selectedInvoice: null,
    qbSyncStatus: 'idle',
    qbSyncError: null
  })
}));

export default useInvoicesStore;
