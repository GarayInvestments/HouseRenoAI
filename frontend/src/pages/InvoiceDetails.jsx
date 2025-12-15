import { FileText, ArrowLeft, Calendar, DollarSign, User, Building2, Mail, Phone, Download, Edit, Trash2 } from 'lucide-react';
import { useState, useEffect } from 'react';
import api from '../lib/api';
import { useAppStore } from '../stores/appStore';
import useInvoicesStore from '../stores/invoicesStore';
import LoadingScreen from '../components/LoadingScreen';
import ErrorState from '../components/ErrorState';
import { INVOICE_STATUS_OPTIONS, formatEnumLabel } from '../constants/enums';
import useDetailsNavigation from '../hooks/useDetailsNavigation';
import NavigationArrows from '../components/NavigationArrows';

export default function InvoiceDetails() {
  const { currentInvoiceId, navigateToInvoices, navigateToInvoiceDetails } = useAppStore();
  const { selectedInvoice, fetchInvoice, invoices } = useInvoicesStore();
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [project, setProject] = useState(null);
  const [client, setClient] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [editedInvoice, setEditedInvoice] = useState(null);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    if (currentInvoiceId) {
      loadInvoiceDetails();
    }
  }, [currentInvoiceId]);

  const loadInvoiceDetails = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const invoiceData = await fetchInvoice(currentInvoiceId);
      
      // Load related project and client (check both snake_case and Title Case)
      const projectId = invoiceData.project_id || invoiceData['Project ID'];
      
      if (projectId) {
        const projectData = await api.getProject(projectId);
        setProject(projectData);
      }
      
      const clientId = invoiceData.client_id || invoiceData['Client ID'];
      
      if (clientId) {
        const clientData = await api.getClient(clientId);
        setClient(clientData);
      }
      
      setLoading(false);
    } catch (err) {
      console.error('Failed to load invoice details:', err);
      setError(err.message || 'Failed to load invoice');
      setLoading(false);
    }
  };

  // Navigation hook for swipe and arrow navigation
  const navigation = useDetailsNavigation(
    invoices,
    currentInvoiceId,
    navigateToInvoiceDetails,
    'invoice_id'
  );

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

  const handleSave = async () => {
    try {
      setIsSaving(true);
      
      // Map frontend display field names to backend database column names
      const fieldMapping = {
        'Invoice Status': 'status',
        'Invoice Date': 'invoice_date',
        'Due Date': 'due_date',
        'Subtotal': 'subtotal',
        'Tax Amount': 'tax_amount',
        'Total Amount': 'total_amount'
      };
      
      // Convert editedInvoice keys from display names to database column names
      const mappedData = {};
      Object.keys(editedInvoice).forEach(key => {
        const dbFieldName = fieldMapping[key] || key;
        mappedData[dbFieldName] = editedInvoice[key];
      });
      
      await api.updateInvoice(currentInvoiceId, mappedData);
      await loadInvoiceDetails(); // Reload to get fresh data
      setIsEditing(false);
      setEditedInvoice(null);
    } catch (error) {
      console.error('Failed to save invoice:', error);
      alert('Failed to save changes. Please try again.');
    } finally {
      setIsSaving(false);
    }
  };

  const handleCancel = () => {
    setIsEditing(false);
    setEditedInvoice(null);
  };

  const handleEditChange = (field, value) => {
    setEditedInvoice(prev => ({ ...prev, [field]: value }));
  };

  if (loading) {
    return <LoadingScreen message="Loading invoice details..." />;
  }

  if (error) {
    return <ErrorState message={error} onRetry={loadInvoiceDetails} />;
  }

  if (!selectedInvoice) {
    return (
      <ErrorState 
        message="Invoice not found" 
        onRetry={() => navigateToInvoices()} 
      />
    );
  }

  // Extract invoice fields (support both database and legacy naming)
  const businessId = selectedInvoice.business_id || selectedInvoice['Invoice ID'] || selectedInvoice.invoice_id;
  const invoiceNumber = selectedInvoice.invoice_number || selectedInvoice['Invoice Number'] || 'N/A';
  const invoiceDate = selectedInvoice.invoice_date || selectedInvoice['Invoice Date'];
  const dueDate = selectedInvoice.due_date || selectedInvoice['Due Date'];
  const status = selectedInvoice.status || selectedInvoice['Invoice Status'] || 'draft';
  const subtotal = selectedInvoice.subtotal || selectedInvoice['Subtotal'] || 0;
  const taxAmount = selectedInvoice.tax_amount || selectedInvoice['Tax Amount'] || 0;
  const totalAmount = selectedInvoice.total_amount || selectedInvoice['Total Amount'] || selectedInvoice.amount || 0;
  const amountPaid = selectedInvoice.amount_paid || selectedInvoice['Amount Paid'] || 0;
  const balanceDue = selectedInvoice.balance_due || selectedInvoice['Balance Due'] || (totalAmount - amountPaid);
  const notes = selectedInvoice.notes || selectedInvoice['Notes'] || '';
  
  // Parse line_items - handle double-encoded JSON strings from database
  let lineItems = selectedInvoice.line_items || selectedInvoice['Line Items'] || [];
  if (typeof lineItems === 'string') {
    try {
      // First parse removes outer quotes and unescapes
      const parsed = JSON.parse(lineItems);
      // If still a string, parse again (double-encoded case)
      lineItems = typeof parsed === 'string' ? JSON.parse(parsed) : parsed;
    } catch (e) {
      console.error('Failed to parse line_items:', e);
      lineItems = [];
    }
  }

  // Extract project fields
  const projectName = project?.project_name || project?.['Project Name'] || project?.data?.project_name || project?.data?.['Project Name'] || 'Unknown Project';
  const projectAddress = project?.address || project?.['Address'] || project?.data?.address || project?.data?.['Address'] || '';

  // Extract client fields
  const clientName = client?.full_name || client?.['Full Name'] || 'Unknown Client';
  const clientEmail = client?.email || client?.['Email'] || '';
  const clientPhone = client?.phone || client?.['Phone'] || '';

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
    return { bg: '#F3F4F6', text: '#6B7280', border: '#D1D5DB' };
  };

  const statusColor = getStatusColor(status);

  return (
    <div 
      style={{ 
        padding: '24px',
        maxWidth: '1200px',
        margin: '0 auto',
        minHeight: '100vh',
        backgroundColor: '#F9FAFB'
      }}
      {...navigation.touchHandlers}
    >
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
          <button
            onClick={navigateToInvoices}
            style={{
              padding: '8px',
              backgroundColor: 'white',
              border: '1px solid #E5E7EB',
              borderRadius: '8px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}
          >
            <ArrowLeft size={20} color="#374151" />
          </button>
          
          <div>
            <h1 style={{ 
              fontSize: '28px', 
              fontWeight: '700',
              color: '#111827',
              margin: '0 0 4px 0'
            }}>
              {invoiceNumber}
            </h1>
            <p style={{ 
              fontSize: '14px', 
              color: '#6B7280',
              margin: 0
            }}>
              {businessId}
            </p>
          </div>

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
            {isEditing ? (
              <select
                value={editedInvoice?.status || ''}
                onChange={(e) => handleEditChange('status', e.target.value)}
                style={{
                  padding: '4px 8px',
                  fontSize: '13px',
                  fontWeight: '600',
                  border: '2px solid #2563EB',
                  borderRadius: '6px',
                  outline: 'none',
                  backgroundColor: 'white'
                }}
              >
                <option value="">Select status...</option>
                {INVOICE_STATUS_OPTIONS.map(opt => (
                  <option key={opt.value} value={opt.value}>{opt.label}</option>
                ))}
              </select>
            ) : (
              formatEnumLabel(status)
            )}
          </span>
        </div>
        
        <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap', alignItems: 'center' }}>
          {/* Navigation Arrows */}
          <NavigationArrows
            currentIndex={navigation.currentIndex}
            totalItems={navigation.totalItems}
            hasPrevious={navigation.hasPrevious}
            hasNext={navigation.hasNext}
            onPrevious={navigation.goToPrevious}
            onNext={navigation.goToNext}
            itemLabel="invoice"
          />
          
          <button
            onClick={() => {/* TODO: Download PDF */}}
            style={{
              padding: '10px 16px',
              backgroundColor: 'white',
              color: '#374151',
              border: '1px solid #E5E7EB',
              borderRadius: '8px',
              cursor: 'pointer',
              fontWeight: '600',
              fontSize: '14px',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}
          >
            <Download size={16} />
            Download
          </button>
          
          {!isEditing ? (
            <button
              onClick={() => {
                setIsEditing(true);
                setEditedInvoice(selectedInvoice);
              }}
              style={{
                padding: '10px 16px',
                backgroundColor: '#2563EB',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
                fontWeight: '600',
                fontSize: '14px',
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}
            >
              <Edit size={16} />
              Edit
            </button>
          ) : (
            <div style={{ display: 'flex', gap: '8px' }}>
              <button
                onClick={handleCancel}
                disabled={isSaving}
                style={{
                  padding: '10px 16px',
                  backgroundColor: 'white',
                  color: '#64748B',
                  border: '1px solid #E5E7EB',
                  borderRadius: '8px',
                  cursor: isSaving ? 'not-allowed' : 'pointer',
                  fontWeight: '600',
                  fontSize: '14px',
                  opacity: isSaving ? 0.5 : 1
                }}
              >
                Cancel
              </button>
              <button
                onClick={handleSave}
                disabled={isSaving}
                style={{
                  padding: '10px 16px',
                  backgroundColor: '#059669',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  cursor: isSaving ? 'not-allowed' : 'pointer',
                  fontWeight: '600',
                  fontSize: '14px',
                  opacity: isSaving ? 0.5 : 1
                }}
              >
                {isSaving ? 'Saving...' : 'Save Changes'}
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Invoice Content */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: '1fr',
        gap: '20px'
      }}>
        {/* Client & Project Info */}
        <div style={{
          backgroundColor: 'white',
          padding: '24px',
          borderRadius: '12px',
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
          border: '1px solid #E5E7EB'
        }}>
          <h2 style={{
            fontSize: '18px',
            fontWeight: '600',
            color: '#111827',
            marginBottom: '16px'
          }}>
            Bill To
          </h2>
          
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
            gap: '20px'
          }}>
            <div>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                marginBottom: '8px'
              }}>
                <User size={18} color="#2563EB" />
                <span style={{ fontSize: '16px', fontWeight: '600', color: '#111827' }}>
                  {clientName}
                </span>
              </div>
              {clientEmail && (
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  fontSize: '14px',
                  color: '#6B7280',
                  marginBottom: '4px'
                }}>
                  <Mail size={14} />
                  {clientEmail}
                </div>
              )}
              {clientPhone && (
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  fontSize: '14px',
                  color: '#6B7280'
                }}>
                  <Phone size={14} />
                  {clientPhone}
                </div>
              )}
            </div>

            <div>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                marginBottom: '8px'
              }}>
                <Building2 size={18} color="#2563EB" />
                <span style={{ fontSize: '16px', fontWeight: '600', color: '#111827' }}>
                  {projectName}
                </span>
              </div>
              {projectAddress && (
                <div style={{
                  fontSize: '14px',
                  color: '#6B7280'
                }}>
                  {projectAddress}
                </div>
              )}
            </div>

            <div>
              <div style={{
                marginBottom: '8px'
              }}>
                <span style={{ fontSize: '12px', color: '#6B7280', display: 'block', marginBottom: '4px' }}>
                  Invoice Date
                </span>
                {isEditing ? (
                  <input
                    type="date"
                    value={editedInvoice?.invoice_date || ''}
                    onChange={(e) => handleEditChange('invoice_date', e.target.value)}
                    style={{
                      width: '100%',
                      padding: '6px 10px',
                      border: '1px solid #D1D5DB',
                      borderRadius: '6px',
                      fontSize: '14px',
                      outline: 'none'
                    }}
                  />
                ) : (
                  <span style={{ fontSize: '14px', color: '#111827', fontWeight: '500' }}>
                    {formatDate(invoiceDate)}
                  </span>
                )}
              </div>
              <div>
                <span style={{ fontSize: '12px', color: '#6B7280', display: 'block', marginBottom: '4px' }}>
                  Due Date
                </span>
                {isEditing ? (
                  <input
                    type="date"
                    value={editedInvoice?.due_date || ''}
                    onChange={(e) => handleEditChange('due_date', e.target.value)}
                    style={{
                      width: '100%',
                      padding: '6px 10px',
                      border: '1px solid #D1D5DB',
                      borderRadius: '6px',
                      fontSize: '14px',
                      outline: 'none'
                    }}
                  />
                ) : (
                  <span style={{ 
                    fontSize: '14px', 
                    color: status.toLowerCase() === 'overdue' ? '#DC2626' : '#111827',
                    fontWeight: '500'
                  }}>
                    {formatDate(dueDate)}
                  </span>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* QuickBooks Info */}
        <div style={{
          backgroundColor: 'white',
          padding: '24px',
          borderRadius: '12px',
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
          border: '1px solid #E5E7EB'
        }}>
          <h2 style={{
            fontSize: '18px',
            fontWeight: '600',
            color: '#111827',
            marginBottom: '16px'
          }}>
            QuickBooks Details
          </h2>
          
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))',
            gap: '16px'
          }}>
            <div>
              <span style={{ fontSize: '12px', color: '#6B7280', display: 'block', marginBottom: '4px' }}>
                Email Status
              </span>
              <span style={{ fontSize: '14px', color: selectedInvoice.email_status ? '#111827' : '#9CA3AF', fontWeight: '500' }}>
                {selectedInvoice.email_status ? formatEnumLabel(selectedInvoice.email_status) : 'Not synced'}
              </span>
            </div>
            
            <div>
              <span style={{ fontSize: '12px', color: '#6B7280', display: 'block', marginBottom: '4px' }}>
                Print Status
              </span>
              <span style={{ fontSize: '14px', color: selectedInvoice.print_status ? '#111827' : '#9CA3AF', fontWeight: '500' }}>
                {selectedInvoice.print_status ? formatEnumLabel(selectedInvoice.print_status) : 'Not synced'}
              </span>
            </div>
            
            <div>
              <span style={{ fontSize: '12px', color: '#6B7280', display: 'block', marginBottom: '4px' }}>
                Billing Email
              </span>
              <span style={{ fontSize: '14px', color: selectedInvoice.bill_email ? '#111827' : '#9CA3AF', fontWeight: '500' }}>
                {selectedInvoice.bill_email || 'Not synced'}
              </span>
            </div>
            
            <div>
              <span style={{ fontSize: '12px', color: '#6B7280', display: 'block', marginBottom: '4px' }}>
                Payment Terms
              </span>
              <span style={{ fontSize: '14px', color: selectedInvoice.payment_terms ? '#111827' : '#9CA3AF', fontWeight: '500' }}>
                {selectedInvoice.payment_terms || 'Not synced'}
              </span>
            </div>
            
            <div>
              <span style={{ fontSize: '12px', color: '#6B7280', display: 'block', marginBottom: '4px' }}>
                Currency
              </span>
              <span style={{ fontSize: '14px', color: selectedInvoice.currency_code ? '#111827' : '#9CA3AF', fontWeight: '500' }}>
                {selectedInvoice.currency_code || 'Not synced'}
              </span>
            </div>
          </div>
          
          {selectedInvoice.customer_memo && (
            <div style={{ marginTop: '16px', paddingTop: '16px', borderTop: '1px solid #E5E7EB' }}>
              <span style={{ fontSize: '12px', color: '#6B7280', display: 'block', marginBottom: '4px' }}>
                Customer Memo
              </span>
              <p style={{ fontSize: '14px', color: '#111827', margin: 0 }}>
                {selectedInvoice.customer_memo}
              </p>
            </div>
          )}
        </div>

        {/* Line Items */}
        <div style={{
          backgroundColor: 'white',
          padding: '24px',
          borderRadius: '12px',
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
          border: '1px solid #E5E7EB'
        }}>
          <h2 style={{
            fontSize: '18px',
            fontWeight: '600',
            color: '#111827',
            marginBottom: '16px'
          }}>
            Line Items
          </h2>

          {Array.isArray(lineItems) && lineItems.length > 0 ? (
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr style={{ borderBottom: '2px solid #E5E7EB' }}>
                    <th style={{ textAlign: 'left', padding: '12px', fontSize: '13px', fontWeight: '600', color: '#6B7280' }}>Description</th>
                    <th style={{ textAlign: 'right', padding: '12px', fontSize: '13px', fontWeight: '600', color: '#6B7280' }}>Quantity</th>
                    <th style={{ textAlign: 'right', padding: '12px', fontSize: '13px', fontWeight: '600', color: '#6B7280' }}>Rate</th>
                    <th style={{ textAlign: 'right', padding: '12px', fontSize: '13px', fontWeight: '600', color: '#6B7280' }}>Amount</th>
                  </tr>
                </thead>
                <tbody>
                  {lineItems.map((item, index) => {
                    // Handle flat-fee items (qty=0 means show as qty=1 for display)
                    const qty = item.quantity !== undefined && item.quantity !== null ? item.quantity : (item.Quantity || 0);
                    const displayQty = qty === 0 ? 1 : qty;
                    const unitPrice = item.unit_price || item.rate || item.Rate || item['Unit Price'] || 0;
                    
                    return (
                      <tr key={index} style={{ borderBottom: '1px solid #F3F4F6' }}>
                        <td style={{ padding: '12px', fontSize: '14px', color: '#111827' }}>
                          {item.description || item.Description || item.item_name || 'N/A'}
                        </td>
                        <td style={{ textAlign: 'right', padding: '12px', fontSize: '14px', color: '#6B7280' }}>
                          {displayQty}
                        </td>
                        <td style={{ textAlign: 'right', padding: '12px', fontSize: '14px', color: '#6B7280' }}>
                          {formatCurrency(unitPrice)}
                        </td>
                        <td style={{ textAlign: 'right', padding: '12px', fontSize: '14px', fontWeight: '500', color: '#111827' }}>
                          {formatCurrency(item.amount || item.Amount || 0)}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          ) : (
            <p style={{ fontSize: '14px', color: '#6B7280', textAlign: 'center', padding: '20px' }}>
              No line items
            </p>
          )}

          {/* Totals */}
          <div style={{
            marginTop: '24px',
            paddingTop: '20px',
            borderTop: '2px solid #E5E7EB',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'flex-end'
          }}>
            <div style={{ width: '300px', maxWidth: '100%' }}>
              <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                marginBottom: '8px',
                alignItems: 'center'
              }}>
                <span style={{ fontSize: '14px', color: '#6B7280' }}>Subtotal:</span>
                {isEditing ? (
                  <input
                    type="number"
                    value={editedInvoice?.subtotal || ''}
                    onChange={(e) => handleEditChange('subtotal', parseFloat(e.target.value) || 0)}
                    style={{
                      width: '120px',
                      padding: '4px 8px',
                      fontSize: '14px',
                      fontWeight: '500',
                      border: '1px solid #D1D5DB',
                      borderRadius: '4px',
                      textAlign: 'right',
                      outline: 'none'
                    }}
                  />
                ) : (
                  <span style={{ fontSize: '14px', fontWeight: '500', color: '#111827' }}>
                    {formatCurrency(subtotal)}
                  </span>
                )}
              </div>
              
              <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                marginBottom: '12px',
                alignItems: 'center'
              }}>
                <span style={{ fontSize: '14px', color: '#6B7280' }}>Tax:</span>
                {isEditing ? (
                  <input
                    type="number"
                    value={editedInvoice?.tax_amount || ''}
                    onChange={(e) => handleEditChange('tax_amount', parseFloat(e.target.value) || 0)}
                    style={{
                      width: '120px',
                      padding: '4px 8px',
                      fontSize: '14px',
                      fontWeight: '500',
                      border: '1px solid #D1D5DB',
                      borderRadius: '4px',
                      textAlign: 'right',
                      outline: 'none'
                    }}
                  />
                ) : (
                  <span style={{ fontSize: '14px', fontWeight: '500', color: '#111827' }}>
                    {formatCurrency(taxAmount)}
                  </span>
                )}
              </div>

              <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                paddingTop: '12px',
                borderTop: '1px solid #E5E7EB',
                marginBottom: '8px',
                alignItems: 'center'
              }}>
                <span style={{ fontSize: '16px', fontWeight: '600', color: '#111827' }}>Total:</span>
                {isEditing ? (
                  <input
                    type="number"
                    value={editedInvoice?.total_amount || ''}
                    onChange={(e) => handleEditChange('total_amount', parseFloat(e.target.value) || 0)}
                    style={{
                      width: '120px',
                      padding: '4px 8px',
                      fontSize: '16px',
                      fontWeight: '700',
                      border: '1px solid #D1D5DB',
                      borderRadius: '4px',
                      textAlign: 'right',
                      outline: 'none'
                    }}
                  />
                ) : (
                  <span style={{ fontSize: '16px', fontWeight: '700', color: '#111827' }}>
                    {formatCurrency(totalAmount)}
                  </span>
                )}
              </div>

              <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                marginBottom: '8px'
              }}>
                <span style={{ fontSize: '14px', color: '#6B7280' }}>Amount Paid:</span>
                <span style={{ fontSize: '14px', fontWeight: '500', color: '#059669' }}>
                  {formatCurrency(amountPaid)}
                </span>
              </div>

              <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                paddingTop: '12px',
                borderTop: '2px solid #E5E7EB'
              }}>
                <span style={{ fontSize: '16px', fontWeight: '600', color: '#111827' }}>Balance Due:</span>
                <span style={{ 
                  fontSize: '18px', 
                  fontWeight: '700', 
                  color: balanceDue > 0 ? '#DC2626' : '#059669'
                }}>
                  {formatCurrency(balanceDue)}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Notes */}
        {notes && (
          <div style={{
            backgroundColor: 'white',
            padding: '24px',
            borderRadius: '12px',
            boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
            border: '1px solid #E5E7EB'
          }}>
            <h2 style={{
              fontSize: '18px',
              fontWeight: '600',
              color: '#111827',
              marginBottom: '12px'
            }}>
              Notes
            </h2>
            <p style={{
              fontSize: '14px',
              color: '#6B7280',
              lineHeight: '1.6',
              whiteSpace: 'pre-wrap'
            }}>
              {notes}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
