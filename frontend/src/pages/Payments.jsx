import { DollarSign, Plus, Search, Calendar, CreditCard, CheckCircle, Clock, XCircle, RefreshCw, User, FileText, Database } from 'lucide-react';
import { useState, useEffect, useMemo } from 'react';
import api from '../lib/api';
import { useAppStore } from '../stores/appStore';
import usePaymentsStore from '../stores/paymentsStore';
import { PAYMENT_STATUS_OPTIONS, formatEnumLabel } from '../constants/enums';
import SyncControlPanel from '../components/SyncControlPanel';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import StatusBadge from '@/components/app/StatusBadge';
import LoadingState from '@/components/app/LoadingState';
import EmptyState from '@/components/app/EmptyState';
import StatsCard from '@/components/app/StatsCard';

export default function Payments() {
  const { navigateToPaymentDetails } = useAppStore();
  
  // Use paymentsStore for data and filtering
  const { 
    payments, 
    loading, 
    error, 
    filter,
    setFilter,
    fetchPayments,
    getFilteredPayments,
    getPaymentStats,
    syncWithQuickBooks,
    qbSyncStatus,
    qbSyncError,
    lastSyncTime,
    nextSyncTime
  } = usePaymentsStore();
  
  const [searchTerm, setSearchTerm] = useState('');
  const [clients, setClients] = useState([]);
  const [invoices, setInvoices] = useState([]);

  useEffect(() => {
    fetchAllData();
    window.history.replaceState({ page: 'payments' }, '');
  }, []);

  const fetchAllData = async () => {
    try {
      // Fetch all data in parallel
      const [paymentsData, clientsData, invoicesData] = await Promise.all([
        fetchPayments(),
        api.getClients(),
        api.getInvoices()
      ]);
      
      setClients(Array.isArray(clientsData) ? clientsData : []);
      const invoicesArray = invoicesData?.items || invoicesData || [];
      setInvoices(Array.isArray(invoicesArray) ? invoicesArray : []);
    } catch (err) {
      console.error('Failed to load payments:', err);
    }
  };

  const handleSyncQuickBooks = async () => {
    await syncWithQuickBooks();
  };

  const getClientName = (clientId) => {
    const client = clients.find(c => 
      c.client_id === clientId || 
      c['Client ID'] === clientId
    );
    return client?.full_name || client?.['Full Name'] || 'Unknown Client';
  };

  const getInvoiceNumber = (invoiceId) => {
    const invoice = invoices.find(i => 
      i.invoice_id === invoiceId || 
      i['Invoice ID'] === invoiceId
    );
    return invoice?.invoice_number || invoice?.business_id || invoice?.['Invoice Number'] || 'N/A';
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

  // Memoized filtered payments (status filter + search)
  const filteredPayments = useMemo(() => {
    let result = getFilteredPayments(); // Apply status filter from store
    
    // Apply search filter
    if (searchTerm) {
      result = result.filter(payment => {
        const businessId = payment.business_id || payment['Payment ID'] || '';
        const referenceNumber = payment.reference_number || payment['Reference Number'] || '';
        const clientName = getClientName(payment.client_id || payment['Client ID']);
        const invoiceNumber = getInvoiceNumber(payment.invoice_id || payment['Invoice ID']);
        
        const searchLower = searchTerm.toLowerCase();
        return businessId.toLowerCase().includes(searchLower) ||
               referenceNumber.toLowerCase().includes(searchLower) ||
               clientName.toLowerCase().includes(searchLower) ||
               invoiceNumber.toLowerCase().includes(searchLower);
      });
    }
    
    return result;
  }, [payments, filter, searchTerm, clients, invoices]);

  const stats = useMemo(() => getPaymentStats(), [payments]);

  const getPaymentMethodIcon = (method) => {
    const lowerMethod = method?.toLowerCase() || '';
    if (lowerMethod.includes('check')) return '📄';
    if (lowerMethod.includes('card') || lowerMethod.includes('credit')) return '💳';
    if (lowerMethod.includes('wire') || lowerMethod.includes('ach')) return '🏦';
    if (lowerMethod.includes('cash')) return '💵';
    return '💰';
  };

  if (loading && payments.length === 0) {
    return <LoadingState message="Loading payments..." layout="list" />;
  }

  if (error && payments.length === 0) {
    return (
      <EmptyState
        title="Failed to load payments"
        description={error}
        action={<Button onClick={fetchPayments}>Retry</Button>}
      />
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto min-h-screen bg-gray-50">
      {/* Header */}
      <div className="flex justify-between items-center mb-6 flex-wrap gap-4">
        <div className="flex items-center gap-3">
          <DollarSign size={32} className="text-green-600" />
          <h1 className="text-3xl font-bold text-gray-900">
            Payments
          </h1>
        </div>
        
        <Button onClick={() => {/* TODO: Open record payment modal */}}>
          <Plus size={16} />
          Record Payment
        </Button>
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
          label="Total Payments" 
          value={stats.total}
        />
        <StatsCard 
          label="Total Amount" 
          value={formatCurrency(stats.totalAmount)}
          valueClassName="text-blue-600"
        />
        <StatsCard 
          label="Cleared" 
          value={formatCurrency(stats.clearedAmount)}
          valueClassName="text-green-600"
        />
        <StatsCard 
          label="Pending" 
          value={stats.pending}
          valueClassName="text-amber-600"
        />
      </div>

      {/* Search and Filters */}
      <div className="flex gap-3 mb-5 flex-wrap">
        {/* Search */}
        <div className="relative flex-1 min-w-[200px]">
          <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input
            type="text"
            placeholder="Search payments..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-3 py-2.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        {/* Status Filters */}
        <div className="flex gap-2 flex-wrap">
          {['all', 'PENDING', 'POSTED', 'FAILED', 'REFUNDED'].map((status) => (
            <Button
              key={status}
              variant={filter === status ? 'default' : 'outline'}
              size="sm"
              onClick={() => setFilter(status)}
              className="capitalize"
            >
              {status === 'all' ? 'All' : formatEnumLabel(status)}
              {status !== 'all' && stats[status.toLowerCase()] > 0 && (
                <Badge variant="secondary" className="ml-2">
                  {stats[status.toLowerCase()]}
                </Badge>
              )}
            </Button>
          ))}
        </div>
      </div>

      {/* Payments List */}
      {filteredPayments.length === 0 ? (
        <EmptyState
          icon={DollarSign}
          title="No payments found"
          description={searchTerm ? 'Try adjusting your search or filters' : 'Get started by recording your first payment'}
          action={!searchTerm && (
            <Button onClick={() => {/* TODO: Open record payment modal */}}>
              <Plus size={16} />
              Record Payment
            </Button>
          )}
        />
      ) : (
        <div className="grid gap-3">
          {filteredPayments.map((payment, index) => {
            const paymentId = payment.payment_id || payment['Payment ID'] || payment.id;
            const businessId = payment.business_id || payment['Business ID'] || payment['Payment ID'] || paymentId;
            const amount = payment.amount || payment['Amount'] || 0;
            const paymentDate = payment.payment_date || payment['Payment Date'];
            const paymentMethod = payment.payment_method || payment['Payment Method'] || 'N/A';
            const referenceNumber = payment.reference_number || payment['Reference Number'] || payment['Check Number'] || payment.check_number || '';
            const status = payment.status || payment['Status'] || payment['Payment Status'] || 'pending';
            const invoiceId = payment.invoice_id || payment['Invoice ID'];
            const clientId = payment.client_id || payment['Client ID'];

            return (
              <Card
                key={`payment-${paymentId || index}`}
                onClick={() => navigateToPaymentDetails(paymentId)}
                className="cursor-pointer transition-all hover:-translate-y-0.5 hover:shadow-lg"
              >
                <CardContent className="p-5">
                  <div className="grid grid-cols-[repeat(auto-fit,minmax(180px,1fr))] gap-5 items-center">
                    {/* Payment Info */}
                    <div>
                      <div className="flex items-center gap-2 mb-2">
                        <DollarSign size={18} className="text-green-600" />
                        <span className="text-xl font-bold text-green-600">
                          {formatCurrency(amount)}
                        </span>
                      </div>
                      <div className="text-sm text-gray-500">
                        {businessId}
                      </div>
                    </div>

                    {/* Client & Invoice */}
                    <div>
                      <div className="flex items-center gap-1.5 mb-1 text-sm text-gray-700">
                        <User size={14} className="text-gray-500" />
                        {getClientName(clientId)}
                      </div>
                      {invoiceId && (
                        <div className="flex items-center gap-1.5 text-sm text-gray-500">
                          <FileText size={14} className="text-gray-400" />
                          Invoice: {getInvoiceNumber(invoiceId)}
                        </div>
                      )}
                    </div>

                    {/* Payment Method & Date */}
                    <div>
                      <div className="flex items-center gap-1.5 mb-1 text-sm text-gray-700">
                        <span>{getPaymentMethodIcon(paymentMethod)}</span>
                        {paymentMethod}
                      </div>
                      {referenceNumber && (
                        <div className="text-sm text-gray-500">
                          Ref: {referenceNumber}
                        </div>
                      )}
                    </div>

                    {/* Date */}
                    <div>
                      <div className="text-sm text-gray-500 mb-1">
                        <Calendar size={14} className="inline mr-1" />
                        {formatDate(paymentDate)}
                      </div>
                    </div>

                    {/* Status */}
                    <div className="text-right">
                      <StatusBadge type="payment" status={status} />
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
