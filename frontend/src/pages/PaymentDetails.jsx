import { DollarSign, ArrowLeft, Calendar, CreditCard, User, FileText, Building2, Mail, Phone } from 'lucide-react';
import { useState, useEffect } from 'react';
import api from '../lib/api';
import { useAppStore } from '../stores/appStore';
import usePaymentsStore from '../stores/paymentsStore';
import LoadingScreen from '../components/LoadingScreen';
import ErrorState from '../components/ErrorState';
import { formatEnumLabel } from '../constants/enums';

export default function PaymentDetails() {
  const { currentPaymentId, navigateToPayments } = useAppStore();
  const { fetchPayment } = usePaymentsStore();
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [payment, setPayment] = useState(null);
  const [invoice, setInvoice] = useState(null);
  const [client, setClient] = useState(null);

  useEffect(() => {
    if (currentPaymentId) {
      loadPaymentDetails();
    }
  }, [currentPaymentId]);

  const loadPaymentDetails = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Fetch payment details
      const response = await api.request(`/payments/${currentPaymentId}`);
      const paymentData = response.payment || response;
      setPayment(paymentData);
      
      // Load related invoice and client
      const invoiceId = paymentData.invoice_id || paymentData['Invoice ID'];
      const clientId = paymentData.client_id || paymentData['Client ID'];
      
      if (invoiceId) {
        try {
          const invoiceData = await api.request(`/invoices/${invoiceId}`);
          setInvoice(invoiceData);
        } catch (err) {
          console.warn('Could not load invoice:', err);
        }
      }
      
      if (clientId) {
        try {
          const clientData = await api.getClient(clientId);
          setClient(clientData);
        } catch (err) {
          console.warn('Could not load client:', err);
        }
      }
      
      setLoading(false);
    } catch (err) {
      console.error('Failed to load payment details:', err);
      setError(err.message || 'Failed to load payment');
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Not set';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  const formatCurrency = (amount) => {
    if (amount === null || amount === undefined) return '$0.00';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  const getStatusColor = (status) => {
    const statusMap = {
      'completed': { bg: '#D1FAE5', text: '#065F46', border: '#A7F3D0' },
      'pending': { bg: '#FEF3C7', text: '#92400E', border: '#FDE68A' },
      'failed': { bg: '#FEE2E2', text: '#991B1B', border: '#FECACA' },
      'refunded': { bg: '#E0E7FF', text: '#3730A3', border: '#C7D2FE' }
    };
    return statusMap[status?.toLowerCase()] || { bg: '#F3F4F6', text: '#374151', border: '#E5E7EB' };
  };

  const getPaymentMethodIcon = (method) => {
    const iconMap = {
      'Credit Card': <CreditCard size={16} />,
      'Check': <FileText size={16} />,
      'Cash': <DollarSign size={16} />,
      'Wire': <Building2 size={16} />,
      'ACH': <Building2 size={16} />
    };
    return iconMap[method] || <CreditCard size={16} />;
  };

  if (loading) {
    return <LoadingScreen message="Loading payment details..." />;
  }

  if (error) {
    return (
      <ErrorState 
        title="Failed to Load Payment" 
        message={error}
        onRetry={() => loadPaymentDetails()} 
      />
    );
  }

  if (!payment) {
    return (
      <ErrorState 
        title="Payment Not Found" 
        message="The payment you're looking for doesn't exist."
        onRetry={() => navigateToPayments()} 
      />
    );
  }

  const statusColor = getStatusColor(payment.status || payment['Status'] || payment['Payment Status']);

  return (
    <div style={{ padding: '24px', maxWidth: '1200px', margin: '0 auto' }}>
      {/* Header */}
      <div style={{ 
        display: 'flex', 
        alignItems: 'center', 
        gap: '16px', 
        marginBottom: '24px' 
      }}>
        <button
          onClick={navigateToPayments}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '8px 16px',
            backgroundColor: 'white',
            border: '1px solid #E5E7EB',
            borderRadius: '8px',
            cursor: 'pointer',
            fontSize: '14px',
            fontWeight: '500',
            color: '#374151'
          }}
        >
          <ArrowLeft size={16} />
          Back to Payments
        </button>
        
        <h1 style={{ 
          fontSize: '28px', 
          fontWeight: '700', 
          color: '#111827',
          margin: 0 
        }}>
          Payment Details
        </h1>
      </div>

      {/* Payment Info Card */}
      <div style={{
        backgroundColor: 'white',
        padding: '32px',
        borderRadius: '12px',
        border: '1px solid #E5E7EB',
        marginBottom: '24px'
      }}>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
          gap: '24px'
        }}>
          {/* Amount */}
          <div>
            <div style={{ 
              fontSize: '13px', 
              color: '#6B7280', 
              marginBottom: '8px',
              fontWeight: '600'
            }}>
              Amount
            </div>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}>
              <DollarSign size={24} color="#059669" />
              <span style={{ fontSize: '32px', fontWeight: '700', color: '#059669' }}>
                {formatCurrency(payment.amount || payment['Amount'])}
              </span>
            </div>
          </div>

          {/* Business ID */}
          <div>
            <div style={{ fontSize: '13px', color: '#6B7280', marginBottom: '8px', fontWeight: '600' }}>
              Payment ID
            </div>
            <div style={{ fontSize: '16px', fontWeight: '600', color: '#111827' }}>
              {payment.business_id || payment['Business ID'] || payment['Payment ID'] || payment.payment_id || 'N/A'}
            </div>
          </div>

          {/* Status */}
          <div>
            <div style={{ fontSize: '13px', color: '#6B7280', marginBottom: '8px', fontWeight: '600' }}>
              Status
            </div>
            <span style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '6px',
              padding: '8px 12px',
              fontSize: '14px',
              fontWeight: '600',
              backgroundColor: statusColor.bg,
              color: statusColor.text,
              border: `1px solid ${statusColor.border}`,
              borderRadius: '6px'
            }}>
              {formatEnumLabel(payment.status || payment['Payment Status'] || 'pending')}
            </span>
          </div>

          {/* Payment Date */}
          <div>
            <div style={{ fontSize: '13px', color: '#6B7280', marginBottom: '8px', fontWeight: '600' }}>
              Payment Date
            </div>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              fontSize: '15px',
              color: '#374151'
            }}>
              <Calendar size={16} color="#6B7280" />
              {formatDate(payment.payment_date || payment['Payment Date'])}
            </div>
          </div>

          {/* Payment Method */}
          <div>
            <div style={{ fontSize: '13px', color: '#6B7280', marginBottom: '8px', fontWeight: '600' }}>
              Payment Method
            </div>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              fontSize: '15px',
              color: '#374151'
            }}>
              {getPaymentMethodIcon(payment.payment_method || payment['Payment Method'])}
              {payment.payment_method || payment['Payment Method'] || 'N/A'}
            </div>
          </div>

          {/* Reference Number */}
          {(payment.reference_number || payment['Reference Number'] || payment.check_number) && (
            <div>
              <div style={{ fontSize: '13px', color: '#6B7280', marginBottom: '8px', fontWeight: '600' }}>
                Reference Number
              </div>
              <div style={{ fontSize: '15px', color: '#374151' }}>
                {payment.reference_number || payment['Reference Number'] || payment.check_number}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Client Info */}
      {client && (
        <div style={{
          backgroundColor: 'white',
          padding: '24px',
          borderRadius: '12px',
          border: '1px solid #E5E7EB',
          marginBottom: '24px'
        }}>
          <h2 style={{ fontSize: '18px', fontWeight: '700', color: '#111827', marginBottom: '16px' }}>
            Client Information
          </h2>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
            gap: '16px'
          }}>
            <div>
              <div style={{ fontSize: '13px', color: '#6B7280', marginBottom: '4px' }}>
                <User size={14} style={{ display: 'inline', marginRight: '4px' }} />
                Name
              </div>
              <div style={{ fontSize: '15px', color: '#111827' }}>
                {client.full_name || client['Full Name'] || 'N/A'}
              </div>
            </div>
            <div>
              <div style={{ fontSize: '13px', color: '#6B7280', marginBottom: '4px' }}>
                <Mail size={14} style={{ display: 'inline', marginRight: '4px' }} />
                Email
              </div>
              <div style={{ fontSize: '15px', color: '#111827' }}>
                {client.email || client['Email'] || 'N/A'}
              </div>
            </div>
            <div>
              <div style={{ fontSize: '13px', color: '#6B7280', marginBottom: '4px' }}>
                <Phone size={14} style={{ display: 'inline', marginRight: '4px' }} />
                Phone
              </div>
              <div style={{ fontSize: '15px', color: '#111827' }}>
                {client.phone || client['Phone'] || 'N/A'}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Invoice Info */}
      {invoice && (
        <div style={{
          backgroundColor: 'white',
          padding: '24px',
          borderRadius: '12px',
          border: '1px solid #E5E7EB'
        }}>
          <h2 style={{ fontSize: '18px', fontWeight: '700', color: '#111827', marginBottom: '16px' }}>
            Related Invoice
          </h2>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
            gap: '16px'
          }}>
            <div>
              <div style={{ fontSize: '13px', color: '#6B7280', marginBottom: '4px' }}>
                Invoice Number
              </div>
              <div style={{ fontSize: '15px', color: '#111827' }}>
                {invoice.invoice_number || invoice.business_id || invoice['Invoice Number'] || 'N/A'}
              </div>
            </div>
            <div>
              <div style={{ fontSize: '13px', color: '#6B7280', marginBottom: '4px' }}>
                Total Amount
              </div>
              <div style={{ fontSize: '15px', color: '#111827' }}>
                {formatCurrency(invoice.total_amount || invoice['Total Amount'])}
              </div>
            </div>
            <div>
              <div style={{ fontSize: '13px', color: '#6B7280', marginBottom: '4px' }}>
                Balance Due
              </div>
              <div style={{ fontSize: '15px', color: '#111827' }}>
                {formatCurrency(invoice.balance_due || invoice.balance || invoice['Balance Due'])}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Notes */}
      {payment.notes && (
        <div style={{
          backgroundColor: 'white',
          padding: '24px',
          borderRadius: '12px',
          border: '1px solid #E5E7EB',
          marginTop: '24px'
        }}>
          <h2 style={{ fontSize: '18px', fontWeight: '700', color: '#111827', marginBottom: '12px' }}>
            Notes
          </h2>
          <p style={{ fontSize: '15px', color: '#374151', lineHeight: '1.6' }}>
            {payment.notes}
          </p>
        </div>
      )}
    </div>
  );
}
