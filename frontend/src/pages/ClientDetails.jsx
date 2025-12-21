import { useState, useEffect } from 'react';
import { User, Mail, Phone, MapPin, Calendar, FileText, Loader2 } from 'lucide-react';
import api from '../lib/api';
import useAppStore from '../stores/appStore';
import ErrorState from '../components/ErrorState';
import { CLIENT_STATUS_OPTIONS } from '../constants/enums';
import { PageHeader, StatusBadge, LoadingState } from '@/components/app';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';

export default function ClientDetails() {
  const [client, setClient] = useState(null);
  const [projects, setProjects] = useState([]);
  const [permits, setPermits] = useState([]);
  const [invoices, setInvoices] = useState([]);
  const [payments, setPayments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [editedClient, setEditedClient] = useState(null);
  const [isSaving, setIsSaving] = useState(false);
  const currentClientId = useAppStore((state) => state.currentClientId);
  const navigateToClients = useAppStore((state) => state.navigateToClients);
  const setCurrentView = useAppStore((state) => state.setCurrentView);

  useEffect(() => {
    // Handle browser back button
    const handlePopState = () => {
      navigateToClients();
    };

    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, [navigateToClients]);

  useEffect(() => {
    // Push state for browser back button support
    window.history.pushState({ view: 'client-details' }, '', '');
    
    const fetchClientDetails = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // Fetch client, projects, permits, invoices, and payments in parallel
        const [clientData, projectsData, permitsData, invoicesData, paymentsData] = await Promise.all([
          api.getClient(currentClientId),
          api.getProjects(),
          api.getPermits(),
          api.getInvoices(),
          api.getPayments()
        ]);
        
        setClient(clientData);
        
        // Filter projects for this client
        const clientProjects = Array.isArray(projectsData) 
          ? projectsData.filter(p => p['Client ID'] === currentClientId)
          : [];
        setProjects(clientProjects);
        
        // Filter permits for this client's projects
        const projectIds = clientProjects.map(p => p['Project ID']);
        const clientPermits = Array.isArray(permitsData)
          ? permitsData.filter(permit => projectIds.includes(permit['Project ID']))
          : [];
        setPermits(clientPermits);
        
        // Filter invoices for this client
        const clientInvoices = Array.isArray(invoicesData)
          ? invoicesData.filter(inv => inv.client_id === currentClientId)
          : [];
        setInvoices(clientInvoices);
        
        // Filter payments for this client
        const clientPayments = Array.isArray(paymentsData)
          ? paymentsData.filter(pmt => pmt.client_id === currentClientId)
          : [];
        setPayments(clientPayments);
        
      } catch {
        setError('Failed to load client details. Please try again.');
      } finally {
        setLoading(false);
      }
    };
    
    if (currentClientId) {
      fetchClientDetails();
    }
  }, [currentClientId]);

  const handleBackClick = () => {
    window.history.back();
  };

  const handleSave = async () => {
    try {
      setIsSaving(true);
      
      // Map frontend display field names to backend database column names
      const fieldMapping = {
        'Client Name': 'full_name',
        'Company Name': 'company_name',
        'Email': 'email',
        'Phone': 'phone',
        'Preferred Contact Method': 'preferred_contact',
        'Address': 'address',
        'City': 'city',
        'State': 'state',
        'ZIP': 'zip_code'
      };
      
      // Convert editedClient keys from display names to database column names
      const mappedData = {};
      Object.keys(editedClient).forEach(key => {
        const dbFieldName = fieldMapping[key] || key;
        mappedData[dbFieldName] = editedClient[key];
      });
      
      await api.updateClient(currentClientId, mappedData);
      setClient({ ...client, ...editedClient });
      setIsEditing(false);
      setEditedClient(null);
    } catch (error) {
      console.error('Failed to save client:', error);
      alert('Failed to save changes. Please try again.');
    } finally {
      setIsSaving(false);
    }
  };

  const handleCancel = () => {
    setIsEditing(false);
    setEditedClient(null);
  };

  const handleEditChange = (field, value) => {
    setEditedClient(prev => ({ ...prev, [field]: value }));
  };

  const handleRetry = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [clientData, projectsData, permitsData] = await Promise.all([
        api.getClient(currentClientId),
        api.getProjects(),
        api.getPermits()
      ]);
      
      setClient(clientData);
      
      const clientProjects = Array.isArray(projectsData) 
        ? projectsData.filter(p => p['Client ID'] === currentClientId)
        : [];
      setProjects(clientProjects);
      
      const projectIds = clientProjects.map(p => p['Project ID']);
      const clientPermits = Array.isArray(permitsData)
        ? permitsData.filter(permit => projectIds.includes(permit['Project ID']))
        : [];
      setPermits(clientPermits);
      
    } catch {
      setError('Failed to load client details. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <LoadingState message="Loading client details..." layout="details" />;
  }

  if (error || !client) {
    return (
      <div className="p-6">
        <ErrorState 
          message={error || 'Client not found'} 
          onRetry={handleRetry} 
          fullScreen 
        />
      </div>
    );
  }

  const clientName = client['Full Name'] || client['Client Name'] || 'Unnamed Client';
  const clientId = client['Client ID'] || client['ID'] || '';
  const email = client['Email'] || '';
  const phone = client['Phone'] || '';
  const address = client['Address'] || '';
  const city = client['City'] || '';
  const state = client['State'] || '';
  const zip = client['ZIP'] || client['Zip Code'] || '';
  const dateAdded = client['Date Added'] || client['Created Date'] || '';
  const notes = client['Notes'] || client['Client Notes'] || '';
  const preferredContact = client['Preferred Contact Method'] || '';
  const companyName = client['Company Name'] || '';
  
  // Calculate actual counts from fetched data
  const activeProjectsCount = projects.length;
  const activePermitsCount = permits.length;

  const outstandingBalance =
    invoices.reduce((sum, inv) => sum + Number(inv.total_amount || 0), 0) -
    payments.reduce((sum, pmt) => sum + Number(pmt.amount || 0), 0);

  return (
    <div className="mx-auto max-w-6xl p-6">
      <PageHeader
        title="Client Details"
        subtitle={clientId ? `Client ID: ${clientId}` : undefined}
        icon={<User size={32} />}
        showBack
        onBack={handleBackClick}
        actions={
          !isEditing ? (
            <Button
              onClick={() => {
                setIsEditing(true);
                setEditedClient(client);
              }}
            >
              Edit Client
            </Button>
          ) : (
            <>
              <Button variant="outline" onClick={handleCancel} disabled={isSaving}>
                Cancel
              </Button>
              <Button onClick={handleSave} disabled={isSaving}>
                {isSaving && <Loader2 className="animate-spin" aria-hidden="true" />}
                {isSaving ? 'Saving...' : 'Save Changes'}
              </Button>
            </>
          )
        }
      />

      <div className="mt-6 space-y-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-start justify-between gap-6">
              <div className="min-w-0 flex-1 space-y-2">
                {isEditing ? (
                  <>
                    <Input
                      type="text"
                      value={editedClient?.['Full Name'] || editedClient?.['Client Name'] || ''}
                      onChange={(e) => {
                        handleEditChange('Full Name', e.target.value);
                        handleEditChange('Client Name', e.target.value);
                      }}
                      placeholder="Client Name"
                      className="h-auto text-2xl font-semibold"
                    />
                    <Input
                      type="text"
                      value={editedClient?.['Company Name'] || ''}
                      onChange={(e) => handleEditChange('Company Name', e.target.value)}
                      placeholder="Company Name (optional)"
                      className="h-auto text-base"
                    />
                  </>
                ) : (
                  <>
                    <h2 className="text-2xl font-semibold tracking-tight text-foreground">{clientName}</h2>
                    {companyName && (
                      <p className="text-base text-muted-foreground">{companyName}</p>
                    )}
                  </>
                )}

                {clientId && (
                  <p className="text-sm text-muted-foreground">Client ID: {clientId}</p>
                )}

                <div>
                  {isEditing ? (
                    <select
                      value={editedClient?.status || client?.status || ''}
                      onChange={(e) => handleEditChange('status', e.target.value)}
                      className="h-9 w-full max-w-xs rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                    >
                      <option value="">Select status...</option>
                      {CLIENT_STATUS_OPTIONS.map((opt) => (
                        <option key={opt.value} value={opt.value}>
                          {opt.label}
                        </option>
                      ))}
                    </select>
                  ) : (
                    client?.status && <StatusBadge status={client.status} type="client" />
                  )}
                </div>
              </div>

              <div className="rounded-xl bg-primary p-4 text-primary-foreground">
                <User size={28} aria-hidden="true" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Contact Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-start gap-3">
              <Mail size={20} className="mt-0.5 text-muted-foreground" aria-hidden="true" />
              <div className="min-w-0 flex-1 space-y-1">
                <p className="text-xs text-muted-foreground">Email</p>
                {isEditing ? (
                  <Input
                    type="email"
                    value={editedClient?.Email || ''}
                    onChange={(e) => handleEditChange('Email', e.target.value)}
                  />
                ) : (
                  <a
                    href={email ? `mailto:${email}` : undefined}
                    className="break-all text-sm text-primary hover:underline"
                  >
                    {email || 'Not set'}
                  </a>
                )}
              </div>
            </div>

            <div className="flex items-start gap-3">
              <Phone size={20} className="mt-0.5 text-muted-foreground" aria-hidden="true" />
              <div className="min-w-0 flex-1 space-y-1">
                <p className="text-xs text-muted-foreground">Phone</p>
                {isEditing ? (
                  <Input
                    type="tel"
                    value={editedClient?.Phone || ''}
                    onChange={(e) => handleEditChange('Phone', e.target.value)}
                  />
                ) : (
                  <a
                    href={phone ? `tel:${phone}` : undefined}
                    className="text-sm text-primary hover:underline"
                  >
                    {phone || 'Not set'}
                  </a>
                )}
              </div>
            </div>

            <div className="flex items-start gap-3">
              <FileText size={20} className="mt-0.5 text-muted-foreground" aria-hidden="true" />
              <div className="min-w-0 flex-1 space-y-1">
                <p className="text-xs text-muted-foreground">Preferred Contact Method</p>
                {isEditing ? (
                  <select
                    value={editedClient?.['Preferred Contact Method'] || ''}
                    onChange={(e) => handleEditChange('Preferred Contact Method', e.target.value)}
                    className="h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                  >
                    <option value="">Select method...</option>
                    <option value="Email">Email</option>
                    <option value="Phone">Phone</option>
                    <option value="Text">Text</option>
                  </select>
                ) : (
                  <p className="text-sm text-foreground">{preferredContact || 'Not set'}</p>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        {(address || city || state || zip || isEditing) && (
          <Card>
            <CardHeader>
              <CardTitle>Address</CardTitle>
            </CardHeader>
            <CardContent>
              {isEditing ? (
                <div className="space-y-3">
                  <Input
                    type="text"
                    value={editedClient?.Address || ''}
                    onChange={(e) => handleEditChange('Address', e.target.value)}
                    placeholder="Street Address"
                  />
                  <div className="grid gap-3 md:grid-cols-3">
                    <Input
                      type="text"
                      value={editedClient?.City || ''}
                      onChange={(e) => handleEditChange('City', e.target.value)}
                      placeholder="City"
                      className="md:col-span-1"
                    />
                    <Input
                      type="text"
                      value={editedClient?.State || ''}
                      onChange={(e) => handleEditChange('State', e.target.value)}
                      placeholder="State"
                      className="md:col-span-1"
                    />
                    <Input
                      type="text"
                      value={editedClient?.ZIP || editedClient?.['Zip Code'] || ''}
                      onChange={(e) => {
                        handleEditChange('ZIP', e.target.value);
                        handleEditChange('Zip Code', e.target.value);
                      }}
                      placeholder="ZIP"
                      className="md:col-span-1"
                    />
                  </div>
                </div>
              ) : (
                <div className="flex items-start gap-3">
                  <MapPin size={20} className="mt-0.5 text-muted-foreground" aria-hidden="true" />
                  <div className="space-y-1">
                    {address && <p className="text-sm text-foreground">{address}</p>}
                    {(city || state || zip) && (
                      <p className="text-sm text-muted-foreground">
                        {city}
                        {city && (state || zip) && ', '}
                        {state} {zip}
                      </p>
                    )}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        )}

        <Card>
          <CardHeader>
            <CardTitle>Client Details</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-3">
              {dateAdded && (
                <div className="flex items-start gap-3">
                  <Calendar size={20} className="mt-0.5 text-muted-foreground" aria-hidden="true" />
                  <div className="space-y-1">
                    <p className="text-xs text-muted-foreground">Date Added</p>
                    <p className="text-sm text-foreground">{dateAdded}</p>
                  </div>
                </div>
              )}

              <div className="flex items-start gap-3">
                <FileText size={20} className="mt-0.5 text-muted-foreground" aria-hidden="true" />
                <div className="space-y-1">
                  <p className="text-xs text-muted-foreground">Active Projects</p>
                  {activeProjectsCount > 0 ? (
                    <Button
                      variant="link"
                      className="h-auto p-0 text-base font-semibold"
                      onClick={() => setCurrentView('projects')}
                    >
                      {activeProjectsCount}
                    </Button>
                  ) : (
                    <p className="text-base font-semibold text-foreground">{activeProjectsCount}</p>
                  )}
                </div>
              </div>

              <div className="flex items-start gap-3">
                <FileText size={20} className="mt-0.5 text-muted-foreground" aria-hidden="true" />
                <div className="space-y-1">
                  <p className="text-xs text-muted-foreground">Active Permits</p>
                  {activePermitsCount > 0 ? (
                    <Button
                      variant="link"
                      className="h-auto p-0 text-base font-semibold"
                      onClick={() => setCurrentView('permits')}
                    >
                      {activePermitsCount}
                    </Button>
                  ) : (
                    <p className="text-base font-semibold text-foreground">{activePermitsCount}</p>
                  )}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {(invoices.length > 0 || payments.length > 0) && (
          <Card>
            <CardHeader>
              <CardTitle>Financial Summary</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid gap-6 lg:grid-cols-2">
                {invoices.length > 0 && (
                  <div className="space-y-3">
                    <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Invoices</p>
                    <div className="space-y-2">
                      {invoices.map((invoice) => (
                        <div
                          key={invoice.invoice_id}
                          className="flex items-center justify-between gap-4 rounded-md border p-3"
                        >
                          <div className="min-w-0">
                            <div className="text-sm font-medium text-foreground">{invoice.invoice_number}</div>
                            <div className="text-xs text-muted-foreground">
                              {invoice.invoice_date ? new Date(invoice.invoice_date).toLocaleDateString() : 'No date'}
                            </div>
                          </div>
                          <div className="flex flex-col items-end gap-2">
                            <div className="text-sm font-semibold text-foreground">
                              ${Number(invoice.total_amount || 0).toFixed(2)}
                            </div>
                            <StatusBadge status={invoice.status || 'draft'} type="invoice" />
                          </div>
                        </div>
                      ))}

                      <div className="flex items-center justify-between rounded-md bg-muted p-3">
                        <span className="text-sm font-semibold text-foreground">Total Invoiced</span>
                        <span className="text-sm font-semibold text-foreground">
                          ${invoices.reduce((sum, inv) => sum + Number(inv.total_amount || 0), 0).toFixed(2)}
                        </span>
                      </div>
                    </div>
                  </div>
                )}

                {payments.length > 0 && (
                  <div className="space-y-3">
                    <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Payments Received</p>
                    <div className="space-y-2">
                      {payments.map((payment) => (
                        <div
                          key={payment.payment_id}
                          className="flex items-center justify-between gap-4 rounded-md border p-3"
                        >
                          <div className="min-w-0">
                            <div className="text-sm font-medium text-foreground">{payment.payment_method || 'Payment'}</div>
                            <div className="text-xs text-muted-foreground">
                              {payment.payment_date ? new Date(payment.payment_date).toLocaleDateString() : 'No date'}
                            </div>
                          </div>
                          <div className="flex flex-col items-end gap-2">
                            <div className="text-sm font-semibold text-foreground">
                              ${Number(payment.amount || 0).toFixed(2)}
                            </div>
                            <StatusBadge status={payment.status || 'pending'} type="payment" />
                          </div>
                        </div>
                      ))}

                      <div className="flex items-center justify-between rounded-md bg-muted p-3">
                        <span className="text-sm font-semibold text-foreground">Total Paid</span>
                        <span className="text-sm font-semibold text-foreground">
                          ${payments.reduce((sum, pmt) => sum + Number(pmt.amount || 0), 0).toFixed(2)}
                        </span>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {invoices.length > 0 && payments.length > 0 && (
                <div className="mt-6 flex items-center justify-between rounded-md border p-4">
                  <span className="text-sm font-semibold text-foreground">Outstanding Balance</span>
                  <span className="text-lg font-semibold text-foreground">${outstandingBalance.toFixed(2)}</span>
                </div>
              )}
            </CardContent>
          </Card>
        )}

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

        <details className="rounded-lg border bg-muted/30 p-6">
          <summary className="cursor-pointer text-sm font-medium text-muted-foreground hover:text-foreground">
            View All Fields
          </summary>
          <div className="mt-4 space-y-2">
            {Object.entries(client).map(([key, value]) => (
              <div key={key} className="flex gap-4 border-b pb-2">
                <span className="w-1/3 shrink-0 text-xs font-medium text-muted-foreground">{key}:</span>
                <span className="w-2/3 break-all text-xs text-foreground">
                  {typeof value === 'object' && value !== null
                    ? JSON.stringify(value, null, 2)
                    : (value || '—')}
                </span>
              </div>
            ))}
          </div>
        </details>
      </div>
    </div>
  );
}
