import { FileText, Plus, Search, Filter, Calendar, DollarSign, Building2, User, CheckCircle, Clock, XCircle, RefreshCw, Database } from 'lucide-react';
import { useState, useEffect, useMemo } from 'react';
import api from '../lib/api';
import { useAppStore } from '../stores/appStore';
import useInvoicesStore from '../stores/invoicesStore';
import SyncControlPanel from '../components/SyncControlPanel';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Card, CardContent } from '@/components/ui/Card';
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
  const [hoveredCard, setHoveredCard] = useState(null);
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

  const getStatusColor = (status) => {
    const lowerStatus = status?.toLowerCase();
    if (lowerStatus === 'paid') {
      return { bg: '#ECFDF5', text: '#059669', border: '#A7F3D0' };
    }
    if (lowerStatus === 'sent') {
      return { bg: '#DBEAFE', text: '#2563EB', border: '#93C5FD' };
    }
    if (lowerStatus === 'draft') {
      return { bg: '#F3F4F6', text: '#6B7280', border: '#D1D5DB' };
    }
    if (lowerStatus === 'overdue') {
      return { bg: '#FEE2E2', text: '#DC2626', border: '#FECACA' };
    }
    if (lowerStatus === 'void' || lowerStatus === 'cancelled') {
      return { bg: '#FEF3C7', text: '#D97706', border: '#FCD34D' };
    }
    return { bg: '#F3F4F6', text: '#6B7280', border: '#D1D5DB' };
  };

  const getStatusIcon = (status) => {
    const lowerStatus = status?.toLowerCase();
    if (lowerStatus === 'paid') return <CheckCircle size={16} />;
    if (lowerStatus === 'sent') return <Clock size={16} />;
    if (lowerStatus === 'draft') return <FileText size={16} />;
    if (lowerStatus === 'overdue') return <AlertCircle size={16} />;
    if (lowerStatus === 'void' || lowerStatus === 'cancelled') return <XCircle size={16} />;
    return <FileText size={16} />;
  };

  if (loading && invoices.length === 0) {
    return <LoadingScreen message="Loading invoices..." />;
  }

  if (error && invoices.length === 0) {
    return <ErrorState message={error} onRetry={fetchInvoices} />;
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
          <FileText size={32} color="#2563EB" />
          <h1 style={{ 
            fontSize: '28px', 
            fontWeight: '700',
            color: '#111827',
            margin: 0
          }}>
            Invoices
          </h1>
        </div>
        
        <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
          <button
            onClick={() => {/* TODO: Open create invoice modal */}}
            style={{
              padding: '10px 20px',
              backgroundColor: '#2563EB',
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
            onMouseEnter={(e) => e.target.style.backgroundColor = '#1D4ED8'}
            onMouseLeave={(e) => e.target.style.backgroundColor = '#2563EB'}
          >
            <Plus size={16} />
            New Invoice
          </button>
        </div>
      </div>

      {/* Sync Control Panel - replaces old sync status banner */}
      <div style={{ marginBottom: '20px' }}>
        <SyncControlPanel
          onManualSync={handleSyncQuickBooks}
          syncStatus={qbSyncStatus}
          syncError={qbSyncError}
          lastSyncTime={lastSyncTime}
          nextSyncTime={nextSyncTime}
        />
      </div>

      {/* Stats Cards */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))',
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
            Total Invoices
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
            Paid
          </div>
          <div style={{ fontSize: '28px', fontWeight: '700', color: '#059669' }}>
            {formatCurrency(stats.paidAmount)}
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
            Outstanding
          </div>
          <div style={{ fontSize: '28px', fontWeight: '700', color: '#DC2626' }}>
            {formatCurrency(stats.outstanding)}
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
            placeholder="Search invoices..."
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
          {['all', 'draft', 'sent', 'paid', 'overdue'].map((status) => (
            <button
              key={status}
              onClick={() => setFilter(status)}
              style={{
                padding: '8px 16px',
                backgroundColor: filter === status ? '#2563EB' : 'white',
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

      {/* Invoices List */}
      {filteredInvoices.length === 0 ? (
        <div style={{
          backgroundColor: 'white',
          padding: '60px 20px',
          borderRadius: '12px',
          textAlign: 'center',
          border: '2px dashed #E5E7EB'
        }}>
          <FileText size={48} color="#9CA3AF" style={{ margin: '0 auto 16px' }} />
          <h3 style={{ 
            fontSize: '18px', 
            fontWeight: '600',
            color: '#374151',
            marginBottom: '8px'
          }}>
            No invoices found
          </h3>
          <p style={{ color: '#6B7280', fontSize: '14px', marginBottom: '20px' }}>
            {searchTerm ? 'Try adjusting your search or filters' : 'Get started by creating your first invoice'}
          </p>
          {!searchTerm && (
            <button
              onClick={() => {/* TODO: Open create invoice modal */}}
              style={{
                padding: '10px 20px',
                backgroundColor: '#2563EB',
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
              Create Invoice
            </button>
          )}
        </div>
      ) : (
        <div style={{
          display: 'grid',
          gap: '12px'
        }}>
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
            
            const statusColor = getStatusColor(status);
            const isHovered = hoveredCard === businessId;

            return (
              <div
                key={businessId}
                onClick={() => navigateToInvoiceDetails(invoice.invoice_id || invoice.id)}
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
                  gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))',
                  gap: '20px',
                  alignItems: 'center'
                }}>
                  {/* Invoice Info */}
                  <div>
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px',
                      marginBottom: '8px'
                    }}>
                      <FileText size={18} color="#2563EB" />
                      <span style={{
                        fontSize: '16px',
                        fontWeight: '600',
                        color: '#111827'
                      }}>
                        {invoiceNumber}
                      </span>
                    </div>
                    <div style={{ fontSize: '13px', color: '#6B7280' }}>
                      {businessId}
                    </div>
                  </div>

                  {/* Client & Project */}
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
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '6px',
                      fontSize: '13px',
                      color: '#6B7280'
                    }}>
                      <Building2 size={14} color="#9CA3AF" />
                      {getProjectName(projectId)}
                    </div>
                  </div>

                  {/* Dates */}
                  <div>
                    <div style={{
                      fontSize: '13px',
                      color: '#6B7280',
                      marginBottom: '4px'
                    }}>
                      <Calendar size={14} style={{ display: 'inline', marginRight: '4px' }} />
                      Issued: {formatDate(invoiceDate)}
                    </div>
                    <div style={{
                      fontSize: '13px',
                      color: status.toLowerCase() === 'overdue' ? '#DC2626' : '#6B7280'
                    }}>
                      <Calendar size={14} style={{ display: 'inline', marginRight: '4px' }} />
                      Due: {formatDate(dueDate)}
                    </div>
                  </div>

                  {/* Amounts */}
                  <div>
                    <div style={{
                      fontSize: '20px',
                      fontWeight: '700',
                      color: '#111827',
                      marginBottom: '4px'
                    }}>
                      {formatCurrency(totalAmount)}
                    </div>
                    <div style={{
                      fontSize: '13px',
                      color: balanceDue > 0 ? '#DC2626' : '#059669',
                      fontWeight: '500'
                    }}>
                      Balance: {formatCurrency(balanceDue)}
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
