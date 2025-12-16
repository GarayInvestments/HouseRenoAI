import { DollarSign, Calendar, CreditCard, User, FileText, Building2, Mail, Phone } from 'lucide-react';
import { useState, useEffect } from 'react';
import api from '../lib/api';
import { useAppStore } from '../stores/appStore';
import usePaymentsStore from '../stores/paymentsStore';
import ErrorState from '../components/ErrorState';
import useDetailsNavigation from '../hooks/useDetailsNavigation';
import NavigationArrows from '../components/NavigationArrows';
import { PageHeader, StatusBadge, LoadingState } from '@/components/app';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

function PaymentDetails() {
  const { currentPaymentId, navigateToPayments, navigateToPaymentDetails } = useAppStore();
  const { payments } = usePaymentsStore();
  
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

  // Navigation hook for swipe and arrow navigation
  const navigation = useDetailsNavigation(
    payments,
    currentPaymentId,
    navigateToPaymentDetails,
    'Payment ID'
  );

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
    return <LoadingState message="Loading payment details..." />;
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

  const paymentStatus = payment.status || payment['Status'] || payment['Payment Status'];

  return (
    <div className="mx-auto max-w-6xl p-6" {...navigation.touchHandlers}>
      <PageHeader
        title="Payment Details"
        icon={<DollarSign size={32} />}
        showBack
        onBack={navigateToPayments}
        actions={
          <NavigationArrows
            currentIndex={navigation.currentIndex}
            totalItems={navigation.totalItems}
            hasPrevious={navigation.hasPrevious}
            hasNext={navigation.hasNext}
            onPrevious={navigation.goToPrevious}
            onNext={navigation.goToNext}
            itemLabel="payment"
          />
        }
      />

      <div className="mt-6 space-y-6">
        <Card>
          <CardContent className="p-6">
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              <div className="space-y-2">
                <div className="text-sm font-medium text-muted-foreground">Amount</div>
                <div className="flex items-center gap-2">
                  <DollarSign size={24} className="text-primary" />
                  <div className="text-3xl font-semibold text-foreground">
                    {formatCurrency(payment.amount || payment['Amount'])}
                  </div>
                </div>
              </div>

              <div className="space-y-2">
                <div className="text-sm font-medium text-muted-foreground">Payment ID</div>
                <div className="text-sm font-medium text-foreground">
                  {payment.business_id || payment['Business ID'] || payment['Payment ID'] || payment.payment_id || 'N/A'}
                </div>
              </div>

              <div className="space-y-2">
                <div className="text-sm font-medium text-muted-foreground">Status</div>
                <StatusBadge status={paymentStatus || 'pending'} type="payment" />
              </div>

              <div className="space-y-2">
                <div className="text-sm font-medium text-muted-foreground">Payment Date</div>
                <div className="flex items-center gap-2 text-sm text-foreground">
                  <Calendar size={16} className="text-muted-foreground" />
                  {formatDate(payment.payment_date || payment['Payment Date'])}
                </div>
              </div>

              <div className="space-y-2">
                <div className="text-sm font-medium text-muted-foreground">Payment Method</div>
                <div className="flex items-center gap-2 text-sm text-foreground">
                  {getPaymentMethodIcon(payment.payment_method || payment['Payment Method'])}
                  {payment.payment_method || payment['Payment Method'] || 'N/A'}
                </div>
              </div>

              {(payment.reference_number || payment['Reference Number'] || payment.check_number) && (
                <div className="space-y-2">
                  <div className="text-sm font-medium text-muted-foreground">Reference Number</div>
                  <div className="text-sm text-foreground">
                    {payment.reference_number || payment['Reference Number'] || payment.check_number}
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {client && (
          <Card>
            <CardHeader>
              <CardTitle>Client Information</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                <div className="space-y-1">
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <User size={14} />
                    <span>Name</span>
                  </div>
                  <div className="text-sm text-foreground">{client.full_name || client['Full Name'] || 'N/A'}</div>
                </div>

                <div className="space-y-1">
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <Mail size={14} />
                    <span>Email</span>
                  </div>
                  <div className="text-sm text-foreground">{client.email || client['Email'] || 'N/A'}</div>
                </div>

                <div className="space-y-1">
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <Phone size={14} />
                    <span>Phone</span>
                  </div>
                  <div className="text-sm text-foreground">{client.phone || client['Phone'] || 'N/A'}</div>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {invoice && (
          <Card>
            <CardHeader>
              <CardTitle>Related Invoice</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                <div className="space-y-1">
                  <div className="text-sm text-muted-foreground">Invoice Number</div>
                  <div className="text-sm text-foreground">
                    {invoice.invoice_number || invoice.business_id || invoice['Invoice Number'] || 'N/A'}
                  </div>
                </div>

                <div className="space-y-1">
                  <div className="text-sm text-muted-foreground">Total Amount</div>
                  <div className="text-sm text-foreground">
                    {formatCurrency(invoice.total_amount || invoice['Total Amount'])}
                  </div>
                </div>

                <div className="space-y-1">
                  <div className="text-sm text-muted-foreground">Balance Due</div>
                  <div className="text-sm text-foreground">
                    {formatCurrency(invoice.balance_due || invoice.balance || invoice['Balance Due'])}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {payment.notes && (
          <Card>
            <CardHeader>
              <CardTitle>Notes</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-foreground leading-relaxed">{payment.notes}</p>
            </CardContent>
          </Card>
        )}

        <Card>
          <CardHeader>
            <CardTitle>QuickBooks Details</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              <div className="space-y-1">
                <div className="text-sm text-muted-foreground">Currency</div>
                <div className="text-sm text-foreground">{payment.currency_code || 'Not synced'}</div>
              </div>
              <div className="space-y-1">
                <div className="text-sm text-muted-foreground">Deposit Account</div>
                <div className="text-sm text-foreground">{payment.deposit_account || 'Not synced'}</div>
              </div>
              <div className="space-y-1">
                <div className="text-sm text-muted-foreground">Total Amount</div>
                <div className="text-sm text-foreground">
                  {payment.total_amount ? formatCurrency(payment.total_amount) : 'Not synced'}
                </div>
              </div>
              <div className="space-y-1">
                <div className="text-sm text-muted-foreground">Unapplied Amount</div>
                <div className="text-sm text-foreground">
                  {payment.unapplied_amount !== null && payment.unapplied_amount !== undefined
                    ? formatCurrency(payment.unapplied_amount)
                    : 'Not synced'}
                </div>
              </div>
              <div className="space-y-1">
                <div className="text-sm text-muted-foreground">Payment Type</div>
                <div className="text-sm text-foreground">
                  {payment.process_payment !== null && payment.process_payment !== undefined
                    ? (payment.process_payment ? 'Electronic Processing' : 'Manual/Received')
                    : 'Not synced'}
                </div>
              </div>
            </div>

            {payment.private_note && (
              <div className="mt-4 border-t pt-4">
                <div className="text-sm text-muted-foreground">Private Note</div>
                <div className="mt-1 text-sm text-foreground">{payment.private_note}</div>
              </div>
            )}

            {payment.linked_transactions && (() => {
              try {
                const transactions = typeof payment.linked_transactions === 'string'
                  ? JSON.parse(payment.linked_transactions)
                  : payment.linked_transactions;

                if (Array.isArray(transactions) && transactions.length > 0) {
                  return (
                    <div className="mt-4 border-t pt-4">
                      <div className="text-sm font-medium text-muted-foreground">Linked Transactions</div>
                      <div className="mt-3 space-y-2">
                        {transactions.map((txn, idx) => {
                          const linkedTxns = txn.LinkedTxn || [];
                          return linkedTxns.map((linked, linkIdx) => (
                            <div
                              key={`${idx}-${linkIdx}`}
                              className="rounded-md bg-muted px-3 py-2 text-sm text-foreground"
                            >
                              <span className="font-medium">{linked.TxnType}</span>: {linked.TxnId}
                              {txn.Amount && (
                                <span className="ml-3 text-muted-foreground">({formatCurrency(txn.Amount)})</span>
                              )}
                            </div>
                          ));
                        })}
                      </div>
                    </div>
                  );
                }
              } catch (e) {
                console.error('Error parsing linked_transactions:', e);
              }
              return null;
            })()}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

export default PaymentDetails;
