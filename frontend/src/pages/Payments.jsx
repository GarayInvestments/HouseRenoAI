import { DollarSign, Plus, Search, Calendar, CreditCard, CheckCircle, Clock, XCircle, AlertCircle, RefreshCw, User, FileText, Database } from 'lucide-react';
import { useState, useEffect, useMemo } from 'react';
import api from '../lib/api';
import { useAppStore } from '../stores/appStore';
import usePaymentsStore from '../stores/paymentsStore';
import LoadingScreen from '../components/LoadingScreen';
import ErrorState from '../components/ErrorState';

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
  const [hoveredCard, setHoveredCard] = useState(null);
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

  const getStatusColor = (status) => {
    const lowerStatus = status?.toLowerCase();
    if (lowerStatus === 'cleared') {
      return { bg: '#ECFDF5', text: '#059669', border: '#A7F3D0' };
    }
    if (lowerStatus === 'pending') {
      return { bg: '#FEF3C7', text: '#D97706', border: '#FCD34D' };
    }
    if (lowerStatus === 'failed') {
      return { bg: '#FEE2E2', text: '#DC2626', border: '#FECACA' };
    }
    if (lowerStatus === 'refunded') {
      return { bg: '#F3F4F6', text: '#6B7280', border: '#D1D5DB' };
    }
    return { bg: '#DBEAFE', text: '#2563EB', border: '#93C5FD' };
  };

  const getStatusIcon = (status) => {
    const lowerStatus = status?.toLowerCase();
    if (lowerStatus === 'cleared') return <CheckCircle size={16} />;
    if (lowerStatus === 'pending') return <Clock size={16} />;
    if (lowerStatus === 'failed') return <XCircle size={16} />;
    if (lowerStatus === 'refunded') return <AlertCircle size={16} />;
    return <DollarSign size={16} />;
  };

  const getPaymentMethodIcon = (method) => {
    const lowerMethod = method?.toLowerCase() || '';
    if (lowerMethod.includes('check')) return '📄';
    if (lowerMethod.includes('card') || lowerMethod.includes('credit')) return '💳';
    if (lowerMethod.includes('wire') || lowerMethod.includes('ach')) return '🏦';
    if (lowerMethod.includes('cash')) return '💵';
    return '💰';
  };

  if (loading && payments.length === 0) {
    return <LoadingScreen message="Loading payments..." />;
  }

  if (error && payments.length === 0) {
    return <ErrorState message={error} onRetry={fetchPayments} />;
  }

  return (
    <div style={{ 
      padding: '24px',
      maxWidth: '1400px',
      margin: '0 auto',
      minHeight: '100vh',
      backgroundColor: '#F9FAFB'
    }}>
      {/* Header */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '24px',
        flexWrap: 'wrap',
        gap: '16px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <DollarSign size={32} color="#059669" />
          <h1 style={{ 
            fontSize: '28px', 
            fontWeight: '700',
            color: '#111827',
            margin: 0
          }}>
            Payments
          </h1>
        </div>
        
        <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
          <button
            onClick={handleSyncQuickBooks}
            disabled={qbSyncStatus === 'syncing'}
            style={{
              padding: '10px 16px',
              backgroundColor: qbSyncStatus === 'syncing' ? '#E5E7EB' : 
                             qbSyncStatus === 'success' ? '#10B981' : 
                             qbSyncStatus === 'error' ? '#EF4444' : '#6B7280',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: qbSyncStatus === 'syncing' ? 'not-allowed' : 'pointer',
              fontWeight: '600',
              fontSize: '14px',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              transition: 'all 0.2s ease'
            }}
          >
            <RefreshCw 
              size={16} 
              className={qbSyncStatus === 'syncing' ? 'animate-spin' : ''} 
            />
            {qbSyncStatus === 'syncing' ? 'Syncing...' : 
             qbSyncStatus === 'success' ? 'Synced!' : 
             qbSyncStatus === 'error' ? 'Sync Failed' : 'Sync QuickBooks'}
          </button>
          
          <button
            onClick={() => {/* TODO: Open record payment modal */}}
            style={{
              padding: '10px 20px',
              backgroundColor: '#059669',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              fontWeight: '600',
              fontSize: '14px',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              transition: 'all 0.2s ease'
            }}
            onMouseEnter={(e) => e.target.style.backgroundColor = '#047857'}
            onMouseLeave={(e) => e.target.style.backgroundColor = '#059669'}
          >
            <Plus size={16} />
            Record Payment
          </button>
        </div>
      </div>

      {/* Sync Status Banner */}
      <div style={{
        backgroundColor: 'white',
        borderRadius: '12px',
        padding: '16px 20px',
        marginBottom: '20px',
        border: '1px solid #E5E7EB',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '12px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px', flexWrap: 'wrap' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Database size={18} color={getSyncFreshnessColor()} />
            <span style={{ fontSize: '14px', color: '#6B7280', fontWeight: '500' }}>
              Reading from cache
            </span>
          </div>
          
          {lastSyncTime && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <div style={{
                width: '8px',
                height: '8px',
                borderRadius: '50%',
                backgroundColor: getSyncFreshnessColor()
              }} />
              <span style={{ fontSize: '14px', color: '#374151' }}>
                Last synced: <strong>{getTimeSinceSync()}</strong>
              </span>
            </div>
          )}
          
          {nextSyncTime && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Clock size={16} color='#6B7280' />
              <span style={{ fontSize: '14px', color: '#6B7280' }}>
                Next: {new Date(nextSyncTime).toLocaleTimeString('en-US', { 
                  hour: 'numeric', 
                  minute: '2-digit',
                  hour12: true 
                })}
              </span>
            </div>
          )}
        </div>
        
        {qbSyncError && (
          <span style={{ fontSize: '13px', color: '#EF4444' }}>
            {qbSyncError}
          </span>
        )}
      </div>

      {/* Error banner for QB sync */}
      {qbSyncError && (
        <div style={{
          padding: '12px 16px',
          backgroundColor: '#FEE2E2',
          border: '1px solid #FECACA',
          borderRadius: '8px',
          marginBottom: '16px',
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          color: '#DC2626'
        }}>
          <AlertCircle size={16} />
          <span style={{ fontSize: '14px' }}>{qbSyncError}</span>
        </div>
      )}

      {/* Stats Cards */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: '16px',
        marginBottom: '24px'
      }}>
        <div style={{
          backgroundColor: 'white',
          padding: '20px',
          borderRadius: '12px',
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
          border: '1px solid #E5E7EB'
        }}>
          <div style={{ fontSize: '14px', color: '#6B7280', marginBottom: '8px' }}>
            Total Payments
          </div>
          <div style={{ fontSize: '28px', fontWeight: '700', color: '#111827' }}>
            {stats.total}
          </div>
        </div>

        <div style={{
          backgroundColor: 'white',
          padding: '20px',
          borderRadius: '12px',
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
          border: '1px solid #E5E7EB'
        }}>
          <div style={{ fontSize: '14px', color: '#6B7280', marginBottom: '8px' }}>
            Total Amount
          </div>
          <div style={{ fontSize: '28px', fontWeight: '700', color: '#2563EB' }}>
            {formatCurrency(stats.totalAmount)}
          </div>
        </div>

        <div style={{
          backgroundColor: 'white',
          padding: '20px',
          borderRadius: '12px',
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
          border: '1px solid #E5E7EB'
        }}>
          <div style={{ fontSize: '14px', color: '#6B7280', marginBottom: '8px' }}>
            Cleared
          </div>
          <div style={{ fontSize: '28px', fontWeight: '700', color: '#059669' }}>
            {formatCurrency(stats.clearedAmount)}
          </div>
        </div>

        <div style={{
          backgroundColor: 'white',
          padding: '20px',
          borderRadius: '12px',
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
          border: '1px solid #E5E7EB'
        }}>
          <div style={{ fontSize: '14px', color: '#6B7280', marginBottom: '8px' }}>
            Pending
          </div>
          <div style={{ fontSize: '28px', fontWeight: '700', color: '#D97706' }}>
            {stats.pending}
          </div>
        </div>
      </div>

      {/* Search and Filters */}
      <div style={{
        display: 'flex',
        gap: '12px',
        marginBottom: '20px',
        flexWrap: 'wrap'
      }}>
        {/* Search */}
        <div style={{ 
          position: 'relative', 
          flex: '1 1 300px',
          minWidth: '200px'
        }}>
          <Search 
            size={18} 
            style={{ 
              position: 'absolute', 
              left: '12px', 
              top: '50%', 
              transform: 'translateY(-50%)',
              color: '#9CA3AF'
            }} 
          />
          <input
            type="text"
            placeholder="Search payments..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{
              width: '100%',
              padding: '10px 12px 10px 40px',
              border: '1px solid #E5E7EB',
              borderRadius: '8px',
              fontSize: '14px',
              outline: 'none',
              transition: 'all 0.2s ease'
            }}
            onFocus={(e) => e.target.style.borderColor = '#2563EB'}
            onBlur={(e) => e.target.style.borderColor = '#E5E7EB'}
          />
        </div>

        {/* Status Filters */}
        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
          {['all', 'pending', 'cleared', 'failed'].map((status) => (
            <button
              key={status}
              onClick={() => setFilter(status)}
              style={{
                padding: '8px 16px',
                backgroundColor: filter === status ? '#059669' : 'white',
                color: filter === status ? 'white' : '#374151',
                border: '1px solid #E5E7EB',
                borderRadius: '8px',
                cursor: 'pointer',
                fontSize: '14px',
                fontWeight: '500',
                textTransform: 'capitalize',
                transition: 'all 0.2s ease'
              }}
            >
              {status}
              {status !== 'all' && stats[status] > 0 && (
                <span style={{
                  marginLeft: '6px',
                  padding: '2px 6px',
                  backgroundColor: filter === status ? 'rgba(255,255,255,0.2)' : '#F3F4F6',
                  borderRadius: '10px',
                  fontSize: '12px',
                  fontWeight: '600'
                }}>
                  {stats[status]}
                </span>
              )}
            </button>
          ))}
        </div>
      </div>

      {/* Payments List */}
      {filteredPayments.length === 0 ? (
        <div style={{
          backgroundColor: 'white',
          padding: '60px 20px',
          borderRadius: '12px',
          textAlign: 'center',
          border: '2px dashed #E5E7EB'
        }}>
          <DollarSign size={48} color="#9CA3AF" style={{ margin: '0 auto 16px' }} />
          <h3 style={{ 
            fontSize: '18px', 
            fontWeight: '600',
            color: '#374151',
            marginBottom: '8px'
          }}>
            No payments found
          </h3>
          <p style={{ color: '#6B7280', fontSize: '14px', marginBottom: '20px' }}>
            {searchTerm ? 'Try adjusting your search or filters' : 'Get started by recording your first payment'}
          </p>
          {!searchTerm && (
            <button
              onClick={() => {/* TODO: Open record payment modal */}}
              style={{
                padding: '10px 20px',
                backgroundColor: '#059669',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
                fontWeight: '600',
                fontSize: '14px',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '8px'
              }}
            >
              <Plus size={16} />
              Record Payment
            </button>
          )}
        </div>
      ) : (
        <div style={{
          display: 'grid',
          gap: '12px'
        }}>
          {filteredPayments.map((payment) => {
            const businessId = payment.business_id || payment['Payment ID'] || payment.payment_id;
            const amount = payment.amount || payment['Amount'] || 0;
            const paymentDate = payment.payment_date || payment['Payment Date'];
            const paymentMethod = payment.payment_method || payment['Payment Method'] || 'N/A';
            const referenceNumber = payment.reference_number || payment['Reference Number'] || payment.check_number || '';
            const status = payment.status || payment['Payment Status'] || 'pending';
            const invoiceId = payment.invoice_id || payment['Invoice ID'];
            const clientId = payment.client_id || payment['Client ID'];
            
            const statusColor = getStatusColor(status);
            const isHovered = hoveredCard === businessId;

            return (
              <div
                key={businessId}
                onClick={() => {/* TODO: navigateToPaymentDetails(payment.payment_id || payment.id) */}}
                onMouseEnter={() => setHoveredCard(businessId)}
                onMouseLeave={() => setHoveredCard(null)}
                style={{
                  backgroundColor: 'white',
                  padding: '20px',
                  borderRadius: '12px',
                  border: '1px solid #E5E7EB',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease',
                  transform: isHovered ? 'translateY(-2px)' : 'none',
                  boxShadow: isHovered ? '0 4px 12px rgba(0,0,0,0.1)' : '0 1px 3px rgba(0,0,0,0.05)'
                }}
              >
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
                  gap: '20px',
                  alignItems: 'center'
                }}>
                  {/* Payment Info */}
                  <div>
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px',
                      marginBottom: '8px'
                    }}>
                      <DollarSign size={18} color="#059669" />
                      <span style={{
                        fontSize: '20px',
                        fontWeight: '700',
                        color: '#059669'
                      }}>
                        {formatCurrency(amount)}
                      </span>
                    </div>
                    <div style={{ fontSize: '13px', color: '#6B7280' }}>
                      {businessId}
                    </div>
                  </div>

                  {/* Client & Invoice */}
                  <div>
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '6px',
                      marginBottom: '4px',
                      fontSize: '14px',
                      color: '#374151'
                    }}>
                      <User size={14} color="#6B7280" />
                      {getClientName(clientId)}
                    </div>
                    {invoiceId && (
                      <div style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '6px',
                        fontSize: '13px',
                        color: '#6B7280'
                      }}>
                        <FileText size={14} color="#9CA3AF" />
                        Invoice: {getInvoiceNumber(invoiceId)}
                      </div>
                    )}
                  </div>

                  {/* Payment Method & Date */}
                  <div>
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '6px',
                      marginBottom: '4px',
                      fontSize: '14px',
                      color: '#374151'
                    }}>
                      <span>{getPaymentMethodIcon(paymentMethod)}</span>
                      {paymentMethod}
                    </div>
                    {referenceNumber && (
                      <div style={{
                        fontSize: '13px',
                        color: '#6B7280'
                      }}>
                        Ref: {referenceNumber}
                      </div>
                    )}
                  </div>

                  {/* Date */}
                  <div>
                    <div style={{
                      fontSize: '13px',
                      color: '#6B7280',
                      marginBottom: '4px'
                    }}>
                      <Calendar size={14} style={{ display: 'inline', marginRight: '4px' }} />
                      {formatDate(paymentDate)}
                    </div>
                  </div>

                  {/* Status */}
                  <div style={{ textAlign: 'right' }}>
                    <span style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '6px',
                      padding: '6px 12px',
                      fontSize: '13px',
                      fontWeight: '600',
                      backgroundColor: statusColor.bg,
                      color: statusColor.text,
                      border: `1px solid ${statusColor.border}`,
                      borderRadius: '6px',
                      textTransform: 'capitalize'
                    }}>
                      {getStatusIcon(status)}
                      {status}
                    </span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
