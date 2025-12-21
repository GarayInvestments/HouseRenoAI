import { useEffect, useState } from 'react';
import { Building2, Calendar, Download, Edit, FileText, Loader2, Mail, Phone, User } from 'lucide-react';

import api from '../lib/api';
import ErrorState from '../components/ErrorState';
import NavigationArrows from '../components/NavigationArrows';
import useDetailsNavigation from '../hooks/useDetailsNavigation';
import { INVOICE_STATUS_OPTIONS, formatEnumLabel } from '../constants/enums';
import { useAppStore } from '../stores/appStore';
import useInvoicesStore from '../stores/invoicesStore';

import { LoadingState, PageHeader, StatusBadge } from '@/components/app';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';

export default function InvoiceDetails() {
  const { currentInvoiceId, navigateToInvoiceDetails, navigateToInvoices } = useAppStore();
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
  const navigation = useDetailsNavigation(invoices, currentInvoiceId, navigateToInvoiceDetails, 'invoice_id');

  const formatDate = (dateString) => {
    if (!dateString) return 'Not set';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  const formatCurrency = (amount) => {
    if (amount === null || amount === undefined) return '$0.00';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
  };

  const toDateInputValue = (value) => {
    if (!value) return '';
    if (typeof value !== 'string') return '';
    return value.includes('T') ? value.slice(0, 10) : value;
  };

  const handleSave = async () => {
    try {
      setIsSaving(true);

      // Map frontend display field names to backend database column names
      const fieldMapping = {
        'Invoice Status': 'status',
        'Invoice Date': 'invoice_date',
        'Due Date': 'due_date',
        Subtotal: 'subtotal',
        'Tax Amount': 'tax_amount',
        'Total Amount': 'total_amount',
      };

      // Convert editedInvoice keys from display names to database column names
      const mappedData = {};
      Object.keys(editedInvoice).forEach((key) => {
        const dbFieldName = fieldMapping[key] || key;
        mappedData[dbFieldName] = editedInvoice[key];
      });

      await api.updateInvoice(currentInvoiceId, mappedData);
      await loadInvoiceDetails();
      setIsEditing(false);
      setEditedInvoice(null);
    } catch (saveError) {
      console.error('Failed to save invoice:', saveError);
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
    setEditedInvoice((prev) => ({ ...prev, [field]: value }));
  };

  if (loading) {
    return <LoadingState message="Loading invoice details..." layout="details" />;
  }

  if (error) {
    return <ErrorState message={error} onRetry={loadInvoiceDetails} />;
  }

  if (!selectedInvoice) {
    return <ErrorState message="Invoice not found" onRetry={() => navigateToInvoices()} />;
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
    } catch (parseError) {
      console.error('Failed to parse line_items:', parseError);
      lineItems = [];
    }
  }

  // Extract project fields
  const projectName =
    project?.project_name ||
    project?.['Project Name'] ||
    project?.data?.project_name ||
    project?.data?.['Project Name'] ||
    'Unknown Project';
  const projectAddress = project?.address || project?.['Address'] || project?.data?.address || project?.data?.['Address'] || '';

  // Extract client fields
  const clientName = client?.full_name || client?.['Full Name'] || 'Unknown Client';
  const clientEmail = client?.email || client?.['Email'] || '';
  const clientPhone = client?.phone || client?.['Phone'] || '';

  const isOverdue = status?.toString().toLowerCase() === 'overdue';

  return (
    <div className="mx-auto max-w-6xl p-6" {...navigation.touchHandlers}>
      <PageHeader
        icon={<FileText size={32} />}
        title={invoiceNumber}
        subtitle={businessId || undefined}
        showBack
        onBack={navigateToInvoices}
        actions={
          <>
            <NavigationArrows
              currentIndex={navigation.currentIndex}
              totalItems={navigation.totalItems}
              hasPrevious={navigation.hasPrevious}
              hasNext={navigation.hasNext}
              onPrevious={navigation.goToPrevious}
              onNext={navigation.goToNext}
              itemLabel="invoice"
            />

            <Button variant="outline" onClick={() => {}}>
              <Download size={16} aria-hidden="true" />
              Download
            </Button>

            {!isEditing ? (
              <Button
                onClick={() => {
                  setIsEditing(true);
                  setEditedInvoice(selectedInvoice);
                }}
              >
                <Edit size={16} aria-hidden="true" />
                Edit
              </Button>
            ) : (
              <>
                <Button variant="outline" onClick={handleCancel} disabled={isSaving}>
                  Cancel
                </Button>
                <Button onClick={handleSave} disabled={isSaving}>
                  {isSaving && <Loader2 className="mr-2 h-4 w-4 animate-spin" aria-hidden="true" />}
                  {isSaving ? 'Saving...' : 'Save Changes'}
                </Button>
              </>
            )}
          </>
        }
      />

      <div className="mt-4">
        {isEditing ? (
          <select
            value={editedInvoice?.status || ''}
            onChange={(e) => handleEditChange('status', e.target.value)}
            className="h-9 w-full max-w-xs rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
          >
            <option value="">Select status...</option>
            {INVOICE_STATUS_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        ) : (
          <StatusBadge status={status} type="invoice" />
        )}
      </div>

      <div className="mt-6 space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>Bill To</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-6 md:grid-cols-3">
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <User size={18} className="text-primary" aria-hidden="true" />
                  <span className="text-base font-semibold text-foreground">{clientName}</span>
                </div>
                {clientEmail && (
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <Mail size={14} aria-hidden="true" />
                    <span className="break-all">{clientEmail}</span>
                  </div>
                )}
                {clientPhone && (
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <Phone size={14} aria-hidden="true" />
                    <span>{clientPhone}</span>
                  </div>
                )}
              </div>

              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <Building2 size={18} className="text-primary" aria-hidden="true" />
                  <span className="text-base font-semibold text-foreground">{projectName}</span>
                </div>
                {projectAddress && <p className="text-sm text-muted-foreground">{projectAddress}</p>}
              </div>

              <div className="space-y-4">
                <div className="space-y-1">
                  <p className="text-xs text-muted-foreground">Invoice Date</p>
                  {isEditing ? (
                    <Input
                      type="date"
                      value={toDateInputValue(editedInvoice?.invoice_date)}
                      onChange={(e) => handleEditChange('invoice_date', e.target.value)}
                      className="max-w-xs"
                    />
                  ) : (
                    <div className="flex items-center gap-2 text-sm text-foreground">
                      <Calendar size={16} className="text-muted-foreground" aria-hidden="true" />
                      <span>{formatDate(invoiceDate)}</span>
                    </div>
                  )}
                </div>

                <div className="space-y-1">
                  <p className="text-xs text-muted-foreground">Due Date</p>
                  {isEditing ? (
                    <Input
                      type="date"
                      value={toDateInputValue(editedInvoice?.due_date)}
                      onChange={(e) => handleEditChange('due_date', e.target.value)}
                      className="max-w-xs"
                    />
                  ) : (
                    <p className={isOverdue ? 'text-sm font-medium text-destructive' : 'text-sm font-medium text-foreground'}>
                      {formatDate(dueDate)}
                    </p>
                  )}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>QuickBooks Details</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-3">
              <div className="space-y-1">
                <p className="text-xs text-muted-foreground">Email Status</p>
                <p className={selectedInvoice.email_status ? 'text-sm font-medium text-foreground' : 'text-sm font-medium text-muted-foreground'}>
                  {selectedInvoice.email_status ? formatEnumLabel(selectedInvoice.email_status) : 'Not synced'}
                </p>
              </div>
              <div className="space-y-1">
                <p className="text-xs text-muted-foreground">Print Status</p>
                <p className={selectedInvoice.print_status ? 'text-sm font-medium text-foreground' : 'text-sm font-medium text-muted-foreground'}>
                  {selectedInvoice.print_status ? formatEnumLabel(selectedInvoice.print_status) : 'Not synced'}
                </p>
              </div>
              <div className="space-y-1">
                <p className="text-xs text-muted-foreground">Billing Email</p>
                <p className={selectedInvoice.bill_email ? 'text-sm font-medium text-foreground' : 'text-sm font-medium text-muted-foreground'}>
                  {selectedInvoice.bill_email || 'Not synced'}
                </p>
              </div>
              <div className="space-y-1">
                <p className="text-xs text-muted-foreground">Payment Terms</p>
                <p className={selectedInvoice.payment_terms ? 'text-sm font-medium text-foreground' : 'text-sm font-medium text-muted-foreground'}>
                  {selectedInvoice.payment_terms || 'Not synced'}
                </p>
              </div>
              <div className="space-y-1">
                <p className="text-xs text-muted-foreground">Currency</p>
                <p className={selectedInvoice.currency_code ? 'text-sm font-medium text-foreground' : 'text-sm font-medium text-muted-foreground'}>
                  {selectedInvoice.currency_code || 'Not synced'}
                </p>
              </div>
            </div>

            {selectedInvoice.customer_memo && (
              <div className="mt-6 border-t pt-4">
                <p className="text-xs text-muted-foreground">Customer Memo</p>
                <p className="mt-1 text-sm text-foreground">{selectedInvoice.customer_memo}</p>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Line Items</CardTitle>
          </CardHeader>
          <CardContent>
            {Array.isArray(lineItems) && lineItems.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full border-collapse">
                  <thead>
                    <tr className="border-b">
                      <th className="px-3 py-3 text-left text-xs font-semibold text-muted-foreground">Description</th>
                      <th className="px-3 py-3 text-right text-xs font-semibold text-muted-foreground">Quantity</th>
                      <th className="px-3 py-3 text-right text-xs font-semibold text-muted-foreground">Rate</th>
                      <th className="px-3 py-3 text-right text-xs font-semibold text-muted-foreground">Amount</th>
                    </tr>
                  </thead>
                  <tbody>
                    {lineItems.map((item, index) => {
                      const qty = item.quantity !== undefined && item.quantity !== null ? item.quantity : (item.Quantity || 0);
                      const displayQty = qty === 0 ? 1 : qty;
                      const unitPrice = item.unit_price || item.rate || item.Rate || item['Unit Price'] || 0;

                      return (
                        <tr key={index} className="border-b last:border-0">
                          <td className="px-3 py-3 text-sm text-foreground">
                            {item.description || item.Description || item.item_name || 'N/A'}
                          </td>
                          <td className="px-3 py-3 text-right text-sm text-muted-foreground">{displayQty}</td>
                          <td className="px-3 py-3 text-right text-sm text-muted-foreground">{formatCurrency(unitPrice)}</td>
                          <td className="px-3 py-3 text-right text-sm font-medium text-foreground">
                            {formatCurrency(item.amount || item.Amount || 0)}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="py-8 text-center text-sm text-muted-foreground">No line items</p>
            )}

            <div className="mt-6 flex flex-col items-end border-t pt-6">
              <div className="w-full max-w-sm space-y-3">
                <div className="flex items-center justify-between gap-4">
                  <span className="text-sm text-muted-foreground">Subtotal</span>
                  {isEditing ? (
                    <Input
                      type="number"
                      value={editedInvoice?.subtotal || ''}
                      onChange={(e) => handleEditChange('subtotal', parseFloat(e.target.value) || 0)}
                      className="max-w-[140px] text-right"
                    />
                  ) : (
                    <span className="text-sm font-medium text-foreground">{formatCurrency(subtotal)}</span>
                  )}
                </div>

                <div className="flex items-center justify-between gap-4">
                  <span className="text-sm text-muted-foreground">Tax</span>
                  {isEditing ? (
                    <Input
                      type="number"
                      value={editedInvoice?.tax_amount || ''}
                      onChange={(e) => handleEditChange('tax_amount', parseFloat(e.target.value) || 0)}
                      className="max-w-[140px] text-right"
                    />
                  ) : (
                    <span className="text-sm font-medium text-foreground">{formatCurrency(taxAmount)}</span>
                  )}
                </div>

                <div className="flex items-center justify-between gap-4 border-t pt-3">
                  <span className="text-sm font-semibold text-foreground">Total</span>
                  {isEditing ? (
                    <Input
                      type="number"
                      value={editedInvoice?.total_amount || ''}
                      onChange={(e) => handleEditChange('total_amount', parseFloat(e.target.value) || 0)}
                      className="max-w-[140px] text-right font-semibold"
                    />
                  ) : (
                    <span className="text-sm font-semibold text-foreground">{formatCurrency(totalAmount)}</span>
                  )}
                </div>

                <div className="flex items-center justify-between gap-4">
                  <span className="text-sm text-muted-foreground">Amount Paid</span>
                  <span className="text-sm font-medium text-foreground">{formatCurrency(amountPaid)}</span>
                </div>

                <div className="flex items-center justify-between gap-4 border-t pt-3">
                  <span className="text-sm font-semibold text-foreground">Balance Due</span>
                  <span className={balanceDue > 0 ? 'text-base font-semibold text-destructive' : 'text-base font-semibold text-foreground'}>
                    {formatCurrency(balanceDue)}
                  </span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {notes && (
          <Card>
            <CardHeader>
              <CardTitle>Notes</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="whitespace-pre-wrap text-sm text-foreground">{notes}</p>
            </CardContent>
          </Card>
        )}

        <Card>
          <CardHeader>
            <CardTitle>Debug Information</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="rounded-md border bg-muted/30 p-3 font-mono text-xs text-muted-foreground">
              <div><span className="font-semibold">Invoice ID:</span> {currentInvoiceId}</div>
              <div><span className="font-semibold">Business ID:</span> {businessId}</div>
              <div><span className="font-semibold">Project ID:</span> {selectedInvoice.project_id || selectedInvoice['Project ID'] || 'N/A'}</div>
              <div><span className="font-semibold">Client ID:</span> {selectedInvoice.client_id || selectedInvoice['Client ID'] || 'N/A'}</div>
              <div><span className="font-semibold">QuickBooks ID:</span> {selectedInvoice.qb_invoice_id || 'Not synced'}</div>
              <div><span className="font-semibold">Last Sync:</span> {selectedInvoice.last_sync_at || 'Never'}</div>
              <div><span className="font-semibold">Line Items Type:</span> {typeof selectedInvoice.line_items}</div>
              <div><span className="font-semibold">Line Items Count:</span> {Array.isArray(lineItems) ? lineItems.length : 'Not array'}</div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
