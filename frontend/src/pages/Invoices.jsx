import { FileText, Plus, Search, Filter, Calendar, DollarSign, Building2, User, CheckCircle, Clock, XCircle, RefreshCw, Database } from 'lucide-react';
import { useState, useEffect, useMemo } from 'react';
import api from '../lib/api';
import { useAppStore } from '../stores/appStore';
import useInvoicesStore from '../stores/invoicesStore';
import SyncControlPanel from '../components/SyncControlPanel';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import StatusBadge from '@/components/app/StatusBadge';
import LoadingState from '@/components/app/LoadingState';
import EmptyState from '@/components/app/EmptyState';
import StatsCard from '@/components/app/StatsCard';

export default function Invoices() {
  const { navigateToInvoiceDetails } = useAppStore();
  
  // Use invoicesStore for data and filtering
  const { 
    invoices, 
    loading, 
    error, 
    filter,
    setFilter,
    fetchInvoices,
    getFilteredInvoices,
    getInvoiceStats,
    syncWithQuickBooks,
    qbSyncStatus,
    qbSyncError,
    lastSyncTime,
    nextSyncTime
  } = useInvoicesStore();
  
  const [searchTerm, setSearchTerm] = useState('');
  const [projects, setProjects] = useState([]);
  const [clients, setClients] = useState([]);

  useEffect(() => {
    fetchAllData();
    window.history.replaceState({ page: 'invoices' }, '');
  }, []);

  const fetchAllData = async () => {
    try {
      // Fetch all data in parallel
      const [invoicesData, projectsData, clientsData] = await Promise.all([
        fetchInvoices(),
        api.getProjects(),
        api.getClients()
      ]);
      
      setProjects(Array.isArray(projectsData) ? projectsData : []);
      setClients(Array.isArray(clientsData) ? clientsData : []);
    } catch (err) {
      console.error('Failed to load invoices:', err);
    }
  };

  const handleSyncQuickBooks = async () => {
    await syncWithQuickBooks();
  };

  const getProjectName = (projectId) => {
    const project = projects.find(p => 
      p.project_id === projectId || 
      p['Project ID'] === projectId
    );
    return project?.project_name || project?.['Project Name'] || 'Unknown Project';
  };

  const getClientName = (clientId) => {
    const client = clients.find(c => 
      c.client_id === clientId || 
      c['Client ID'] === clientId
    );
    return client?.full_name || client?.['Full Name'] || 'Unknown Client';
  };

  // Format date helper
  const formatDate = (dateString) => {
    if (!dateString) return 'Not set';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  // Format currency
  const formatCurrency = (amount) => {
    if (amount === null || amount === undefined) return '$0.00';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
  };
  
  // Calculate time since last sync
  const getTimeSinceSync = () => {
    if (!lastSyncTime) return null;
    const now = new Date();
    const syncDate = new Date(lastSyncTime);
    const diffMs = now - syncDate;
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffMins = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));
    
    if (diffHours < 1) return `${diffMins} min ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    return `${Math.floor(diffHours / 24)}d ago`;
  };
  
  // Get sync freshness color
  const getSyncFreshnessColor = () => {
    if (!lastSyncTime) return '#6B7280'; // Gray
    const now = new Date();
    const syncDate = new Date(lastSyncTime);
    const diffHours = (now - syncDate) / (1000 * 60 * 60);
    
    if (diffHours < 4) return '#10B981'; // Green - fresh
    if (diffHours < 8) return '#F59E0B'; // Yellow - stale
    return '#EF4444'; // Red - very stale
  };

  // Memoized filtered invoices (status filter + search)
  const filteredInvoices = useMemo(() => {
    let result = getFilteredInvoices(); // Apply status filter from store
    
    // Apply search filter
    if (searchTerm) {
      result = result.filter(invoice => {
        const businessId = invoice.business_id || invoice['Invoice ID'] || '';
        const invoiceNumber = invoice.invoice_number || invoice['Invoice Number'] || '';
        const projectName = getProjectName(invoice.project_id || invoice['Project ID']);
        const clientName = getClientName(invoice.client_id || invoice['Client ID']);
        
        const searchLower = searchTerm.toLowerCase();
        return businessId.toLowerCase().includes(searchLower) ||
               invoiceNumber.toLowerCase().includes(searchLower) ||
               projectName.toLowerCase().includes(searchLower) ||
               clientName.toLowerCase().includes(searchLower);
      });
    }
    
    return result;
  }, [invoices, filter, searchTerm, projects, clients]);

  const stats = useMemo(() => getInvoiceStats(), [invoices]);

  if (loading && invoices.length === 0) {
    return <LoadingState message="Loading invoices..." />;
  }

  if (error && invoices.length === 0) {
    return (
      <EmptyState
        title="Failed to load invoices"
        description={error}
        action={<Button onClick={fetchInvoices}>Retry</Button>}
      />
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto min-h-screen bg-gray-50">
      {/* Header */}
      <div className="flex justify-between items-center mb-6 flex-wrap gap-4">
        <div className="flex items-center gap-3">
          <FileText size={32} className="text-blue-600" />
          <h1 className="text-3xl font-bold text-gray-900">
            Invoices
          </h1>
        </div>
        
        <div className="flex gap-3 flex-wrap">
          <Button onClick={() => {/* TODO: Open create invoice modal */}}>
            <Plus size={16} />
            New Invoice
          </Button>
        </div>
      </div>

      {/* Sync Control Panel */}
      <div className="mb-5">
        <SyncControlPanel
          onManualSync={handleSyncQuickBooks}
          syncStatus={qbSyncStatus}
          syncError={qbSyncError}
          lastSyncTime={lastSyncTime}
          nextSyncTime={nextSyncTime}
        />
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-[repeat(auto-fit,minmax(140px,1fr))] gap-4 mb-6">
        <StatsCard 
          label="Total Invoices" 
          value={stats.total} 
        />
        <StatsCard 
          label="Total Amount" 
          value={formatCurrency(stats.totalAmount)}
          valueClassName="text-blue-600"
        />
        <StatsCard 
          label="Paid" 
          value={formatCurrency(stats.paidAmount)}
          valueClassName="text-green-600"
        />
        <StatsCard 
          label="Outstanding" 
          value={formatCurrency(stats.outstanding)}
          valueClassName="text-red-600"
        />
      </div>

      {/* Search and Filters */}
      <div className="flex gap-3 mb-5 flex-wrap">
        {/* Search */}
        <div className="relative flex-1 min-w-[200px]">
          <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input
            type="text"
            placeholder="Search invoices..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-3 py-2.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        {/* Status Filters */}
        <div className="flex gap-2 flex-wrap">
          {['all', 'draft', 'sent', 'paid', 'overdue'].map((status) => (
            <Button
              key={status}
              variant={filter === status ? 'default' : 'outline'}
              size="sm"
              onClick={() => setFilter(status)}
              className="capitalize"
            >
              {status}
              {status !== 'all' && stats[status] > 0 && (
                <Badge variant="secondary" className="ml-2">
                  {stats[status]}
                </Badge>
              )}
            </Button>
          ))}
        </div>
      </div>

      {/* Invoices List */}
      {filteredInvoices.length === 0 ? (
        <EmptyState
          icon={FileText}
          title="No invoices found"
          description={searchTerm ? 'Try adjusting your search or filters' : 'Get started by creating your first invoice'}
          action={!searchTerm && (
            <Button onClick={() => {/* TODO: Open create invoice modal */}}>
              <Plus size={16} />
              Create Invoice
            </Button>
          )}
        />
      ) : (
        <div className="grid gap-3">
          {filteredInvoices.map((invoice) => {
            const businessId = invoice.business_id || invoice['Invoice ID'] || invoice.invoice_id;
            const invoiceNumber = invoice.invoice_number || invoice['Invoice Number'] || 'N/A';
            const invoiceDate = invoice.invoice_date || invoice['Invoice Date'];
            const dueDate = invoice.due_date || invoice['Due Date'];
            const totalAmount = invoice.total_amount || invoice['Total Amount'] || invoice.amount || 0;
            const amountPaid = invoice.amount_paid || invoice['Amount Paid'] || 0;
            const balanceDue = invoice.balance_due || invoice['Balance Due'] || (totalAmount - amountPaid);
            const status = invoice.status || invoice['Invoice Status'] || 'draft';
            const projectId = invoice.project_id || invoice['Project ID'];
            const clientId = invoice.client_id || invoice['Client ID'];

            return (
              <Card
                key={businessId}
                onClick={() => navigateToInvoiceDetails(invoice.invoice_id || invoice.id)}
                className="cursor-pointer transition-all hover:-translate-y-0.5 hover:shadow-lg"
              >
                <CardContent className="p-5">
                  <div className="grid grid-cols-[repeat(auto-fit,minmax(160px,1fr))] gap-5 items-center">
                    {/* Invoice Info */}
                    <div>
                      <div className="flex items-center gap-2 mb-2">
                        <FileText size={18} className="text-blue-600" />
                        <span className="text-base font-semibold text-gray-900">
                          {invoiceNumber}
                        </span>
                      </div>
                      <div className="text-sm text-gray-500">
                        {businessId}
                      </div>
                    </div>

                    {/* Client & Project */}
                    <div>
                      <div className="flex items-center gap-1.5 mb-1 text-sm text-gray-700">
                        <User size={14} className="text-gray-500" />
                        {getClientName(clientId)}
                      </div>
                      <div className="flex items-center gap-1.5 text-sm text-gray-500">
                        <Building2 size={14} className="text-gray-400" />
                        {getProjectName(projectId)}
                      </div>
                    </div>

                    {/* Dates */}
                    <div>
                      <div className="text-sm text-gray-500 mb-1">
                        <Calendar size={14} className="inline mr-1" />
                        Issued: {formatDate(invoiceDate)}
                      </div>
                      <div className={`text-sm ${status.toLowerCase() === 'overdue' ? 'text-red-600' : 'text-gray-500'}`}>
                        <Calendar size={14} className="inline mr-1" />
                        Due: {formatDate(dueDate)}
                      </div>
                    </div>

                    {/* Amounts */}
                    <div>
                      <div className="text-xl font-bold text-gray-900 mb-1">
                        {formatCurrency(totalAmount)}
                      </div>
                      <div className={`text-sm font-medium ${balanceDue > 0 ? 'text-red-600' : 'text-green-600'}`}>
                        Balance: {formatCurrency(balanceDue)}
                      </div>
                    </div>

                    {/* Status */}
                    <div className="text-right">
                      <StatusBadge type="invoice" status={status} />
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
