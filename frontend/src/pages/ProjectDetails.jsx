import { useEffect, useState } from 'react';
import { 
  ArrowLeft, 
  MapPin, 
  Users, 
  Calendar, 
  DollarSign, 
  FileText, 
  Image as ImageIcon,
  Building,
  Loader2,
  AlertCircle,
  Hash
} from 'lucide-react';
import api from '../lib/api';
import { useAppStore } from '../stores/appStore';
import LoadingScreen from '../components/LoadingScreen';
import ErrorState from '../components/ErrorState';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import StatusBadge from '@/components/app/StatusBadge';

export default function ProjectDetails() {
  const { currentProjectId, navigateToProjects } = useAppStore();
  const [project, setProject] = useState(null);
  const [invoices, setInvoices] = useState([]);
  const [payments, setPayments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [editedProject, setEditedProject] = useState(null);
  const [isSaving, setIsSaving] = useState(false);
  const [businesses, setBusinesses] = useState([]);
  const [qualifiers, setQualifiers] = useState([]);

  useEffect(() => {
    fetchProjectDetails();
    fetchComplianceData();
    fetchFinancialData();
  }, [currentProjectId]);

  const fetchFinancialData = async () => {
    try {
      const [invoicesData, paymentsData] = await Promise.all([
        api.getInvoices(),
        api.getPayments()
      ]);
      
      // Filter for this project
      const projectInvoices = Array.isArray(invoicesData)
        ? invoicesData.filter(inv => inv.project_id === currentProjectId)
        : [];
      setInvoices(projectInvoices);
      
      const projectPayments = Array.isArray(paymentsData)
        ? paymentsData.filter(pmt => pmt.project_id === currentProjectId)
        : [];
      setPayments(projectPayments);
    } catch (error) {
      console.error('Failed to load financial data:', error);
    }
  };

  const fetchComplianceData = async () => {
    try {
      const [businessesData, qualifiersData] = await Promise.all([
        api.getLicensedBusinesses(),
        api.getQualifiers()
      ]);
      setBusinesses(businessesData || []);
      setQualifiers(qualifiersData || []);
    } catch (error) {
      console.error('Failed to load compliance data:', error);
    }
  };

  // Handle browser back button
  useEffect(() => {
    const handlePopState = () => {
      navigateToProjects();
    };

    // Push a state when component mounts
    window.history.pushState({ page: 'project-details' }, '');
    
    // Listen for back button
    window.addEventListener('popstate', handlePopState);

    return () => {
      window.removeEventListener('popstate', handlePopState);
    };
  }, [navigateToProjects]);

  const fetchProjectDetails = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getProjects();
      const foundProject = Array.isArray(data) 
        ? data.find(p => p['Project ID'] === currentProjectId)
        : null;
      
      if (foundProject) {
        setProject(foundProject);
      } else {
        setError('Project not found');
      }
    } catch {
      setError('Failed to load project details');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      setIsSaving(true);
      
      // Map frontend display field names to backend database column names
      const fieldMapping = {
        'Project Name': 'project_name',
        'Project Status': 'status',
        'Project Type': 'project_type',
        'Project Address': 'project_address',
        'Start Date': 'start_date',
        'City': 'city',
        'Licensed Business': 'licensed_business_id',
        'Qualifier': 'qualifier_id',
        'Engagement Model': 'engagement_model',
        'Notes': 'notes'
      };
      
      // Convert editedProject keys from display names to database column names
      // Only send fields that exist in the database
      const mappedData = {};
      Object.keys(editedProject).forEach(key => {
        const dbFieldName = fieldMapping[key];
        if (dbFieldName) {
          let value = editedProject[key];
          
          // Convert date strings to ISO datetime format
          if (dbFieldName === 'start_date' && value && value.length === 10) {
            // Input date is YYYY-MM-DD, convert to ISO datetime
            value = `${value}T00:00:00Z`;
          }
          
          // Skip empty strings - send null or omit entirely
          if (value !== '' && value !== null && value !== undefined) {
            mappedData[dbFieldName] = value;
          }
        }
      });
      
      if (Object.keys(mappedData).length === 0) {
        alert('No changes to save');
        setIsSaving(false);
        return;
      }
      
      await api.updateProject(currentProjectId, mappedData, false);
      setProject({ ...project, ...editedProject });
      setIsEditing(false);
      setEditedProject(null);
    } catch (error) {
      console.error('Failed to save project:', error);
      alert('Failed to save changes. Please try again.');
    } finally {
      setIsSaving(false);
    }
  };

  const handleCancel = () => {
    setIsEditing(false);
    setEditedProject(null);
  };

  const handleEditChange = (field, value) => {
    setEditedProject(prev => ({ ...prev, [field]: value }));
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Not set';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' });
  };

  const formatCurrency = (amount) => {
    if (!amount) return 'Not set';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'completed':
      case 'final inspection complete':
        return { bg: '#ECFDF5', text: '#059669', border: '#A7F3D0' };
      case 'permit approved':
      case 'active':
        return { bg: '#DBEAFE', text: '#2563EB', border: '#93C5FD' };
      case 'permit submitted':
      case 'planning':
        return { bg: '#FEF3C7', text: '#D97706', border: '#FCD34D' };
      case 'closed / archived':
        return { bg: '#F3F4F6', text: '#6B7280', border: '#D1D5DB' };
      case 'inquiry received':
        return { bg: '#FEF2F2', text: '#DC2626', border: '#FECACA' };
      default:
        return { bg: '#F3F4F6', text: '#6B7280', border: '#D1D5DB' };
    }
  };

  if (loading) {
    return <LoadingScreen />;
  }

  if (error || !project) {
    return (
      <div style={{ padding: '20px', backgroundColor: '#F8FAFC', minHeight: '100vh' }}>
        <ErrorState 
          message={error || 'Project not found'} 
          onRetry={fetchProjectDetails} 
          fullScreen 
        />
      </div>
    );
  }

  const statusStyle = getStatusColor(project.Status);

  return (
    <div className="bg-gray-50 min-h-screen p-8">
      <div className="max-w-6xl mx-auto">
        {/* Back Button & Edit Controls */}
        <div className="flex justify-between items-center mb-6">
          <Button
            variant="outline"
            onClick={navigateToProjects}
          >
            <ArrowLeft size={16} />
            Back to Projects
          </Button>

          {!isEditing ? (
            <Button
              onClick={() => {
                setIsEditing(true);
                setEditedProject(project);
              }}
            >
              Edit Project
            </Button>
          ) : (
            <div className="flex gap-2">
              <Button
                variant="outline"
                onClick={handleCancel}
                disabled={isSaving}
              >
                Cancel
              </Button>
              <Button
                onClick={handleSave}
                disabled={isSaving}
                className="bg-green-600 hover:bg-green-700"
              >
                {isSaving ? 'Saving...' : 'Save Changes'}
              </Button>
            </div>
          )}
        </div>

        {/* Header Card */}
        <Card className="mb-6">
          <CardContent className="p-8">
            <div className="flex justify-between items-start mb-4">
              <div className="flex-1 mr-4">
                {isEditing ? (
                  <input
                    type="text"
                    value={editedProject?.['Project Name'] || ''}
                    onChange={(e) => handleEditChange('Project Name', e.target.value)}
                    className="text-3xl font-semibold text-gray-800 mb-2 w-full p-2 border-2 border-blue-600 rounded-lg outline-none"
                    placeholder="Project Name"
                  />
                ) : (
                  <h1 className="text-3xl font-semibold text-gray-800 mb-2">
                    {project['Project Name'] || 'Unnamed Project'}
                  </h1>
                )}
                <div className="flex items-center gap-2 text-gray-500 text-sm mb-3">
                  <Hash size={14} />
                  Project ID: {project['Project ID']}
                </div>
              </div>
              {isEditing ? (
                <select
                  value={editedProject?.Status || editedProject?.status || ''}
                  onChange={(e) => handleEditChange('Status', e.target.value)}
                  className="p-2 rounded-lg text-sm font-medium border-2 border-blue-600 outline-none"
                >
                  <option value="">Select status...</option>
                  {PROJECT_STATUS_OPTIONS.map(opt => (
                    <option key={opt.value} value={opt.value}>{opt.label}</option>
                  ))}
                </select>
              ) : (
                <StatusBadge type="project" status={project.Status || 'N/A'} />
              )}
            </div>

            {/* Info Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 pt-4 border-t border-gray-100">
              {/* Location */}
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-blue-100 flex items-center justify-center">
                  <MapPin size={20} className="text-blue-600" />
                </div>
                <div className="flex-1">
                  <p className="text-xs text-gray-500 mb-0.5">Location</p>
                  {isEditing ? (
                    <input
                      type="text"
                      value={editedProject?.['Project Address'] || ''}
                      onChange={(e) => handleEditChange('Project Address', e.target.value)}
                      className="w-full text-sm font-medium px-2.5 py-1.5 border border-gray-300 rounded-md outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      placeholder="Project Address"
                    />
                  ) : (
                    <p className="text-sm text-gray-800 font-medium">
                      {project['Project Address'] || 'No address'}
                    </p>
                  )}
                </div>
              </div>

              {/* Type */}
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-green-100 flex items-center justify-center">
                  <Building size={20} className="text-green-600" />
                </div>
                <div className="flex-1">
                  <p className="text-xs text-gray-500 mb-0.5">Type</p>
                  {isEditing ? (
                    <select
                      value={editedProject?.['Project Type'] || editedProject?.project_type || ''}
                      onChange={(e) => handleEditChange('Project Type', e.target.value)}
                      className="w-full text-sm font-medium px-2.5 py-1.5 border border-gray-300 rounded-md outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    >
                      <option value="">Select type...</option>
                      {PROJECT_TYPE_OPTIONS.map(opt => (
                        <option key={opt.value} value={opt.value}>{opt.label}</option>
                      ))}
                    </select>
                  ) : (
                    <p className="text-sm text-gray-800 font-medium">
                      {formatEnumLabel(project['Project Type'] || project.project_type) || 'N/A'}
                    </p>
                  )}
                </div>
              </div>

              {/* Start Date */}
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-amber-100 flex items-center justify-center">
                  <Calendar size={20} className="text-amber-600" />
                </div>
                <div className="flex-1">
                  <p className="text-xs text-gray-500 mb-0.5">Start Date</p>
                  {isEditing ? (
                    <input
                      type="date"
                      value={editedProject?.['Start Date'] || ''}
                      onChange={(e) => handleEditChange('Start Date', e.target.value)}
                      className="w-full text-sm font-medium px-2.5 py-1.5 border border-gray-300 rounded-md outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  ) : (
                    <p className="text-sm text-gray-800 font-medium">
                      {formatDate(project['Start Date'])}
                    </p>
                  )}
                </div>
              </div>

              {/* Client */}
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-red-100 flex items-center justify-center">
                  <Users size={20} className="text-red-600" />
                </div>
                <div>
                  <p className="text-xs text-gray-500 mb-0.5">Client</p>
                  {project['Client ID'] ? (
                    <button
                      onClick={() => useAppStore.getState().navigateToClient(project['Client ID'])}
                      className="text-sm text-blue-600 font-medium underline hover:text-blue-800 transition-colors bg-transparent border-none p-0 cursor-pointer text-left"
                    >
                      {project['Owner Name (PM\'s Client)'] || project['Client ID']}
                    </button>
                  ) : (
                    <p className="text-sm text-gray-800 font-medium">
                      {project['Owner Name (PM\'s Client)'] || 'Unknown'}
                    </p>
                  )}
                </div>
              </div>
            </div>
        </CardContent>
      </Card>

        {/* Financial Summary - Invoices & Payments */}
        {(invoices.length > 0 || payments.length > 0) && (
          <Card className="mb-6">
            <CardContent className="p-8">
              <h2 className="text-xl font-semibold text-gray-800 mb-6 flex items-center gap-2">
                <DollarSign size={20} className="text-blue-600" />
                Financial Summary
              </h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Invoices */}
                {invoices.length > 0 && (
                  <div>
                    <h3 className="text-sm font-semibold text-gray-500 mb-4 uppercase tracking-wide">Invoices</h3>
                    <div className="flex flex-col gap-3">
                      {invoices.map(invoice => (
                        <div key={invoice.invoice_id} className="p-4 bg-gray-50 rounded-lg border border-gray-200">
                          <div className="flex justify-between items-start">
                            <div>
                              <div className="text-[15px] font-semibold text-gray-800 mb-1">{invoice.invoice_number}</div>
                              <div className="text-[13px] text-gray-500">
                                {invoice.invoice_date ? new Date(invoice.invoice_date).toLocaleDateString() : 'No date'}
                              </div>
                            </div>
                            <div className="text-right">
                              <div className="text-lg font-bold text-gray-800 mb-1">
                                ${Number(invoice.total_amount || 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                              </div>
                              <Badge className={invoice.status === 'PAID' ? 'bg-green-100 text-green-800' : invoice.status === 'SENT' ? 'bg-amber-100 text-amber-800' : 'bg-gray-100 text-gray-600'}>
                                {invoice.status || 'DRAFT'}
                              </Badge>
                            </div>
                          </div>
                        </div>
                      ))}
                      <div className="mt-3 p-4 bg-blue-50 rounded-lg flex justify-between items-center">
                        <span className="text-[15px] font-semibold text-blue-800">Total Invoiced</span>
                        <span className="text-xl font-bold text-blue-800">
                          ${invoices.reduce((sum, inv) => sum + Number(inv.total_amount || 0), 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                        </span>
                      </div>
                    </div>
                  </div>
                )}

                {/* Payments */}
                {payments.length > 0 && (
                  <div>
                    <h3 className="text-sm font-semibold text-gray-500 mb-4 uppercase tracking-wide">Payments Received</h3>
                    <div className="flex flex-col gap-3">
                      {payments.map(payment => (
                        <div key={payment.payment_id} className="p-4 bg-gray-50 rounded-lg border border-gray-200">
                          <div className="flex justify-between items-start">
                            <div>
                              <div className="text-[15px] font-semibold text-gray-800 mb-1">{payment.payment_method || 'Payment'}</div>
                              <div className="text-[13px] text-gray-500">
                                {payment.payment_date ? new Date(payment.payment_date).toLocaleDateString() : 'No date'}
                              </div>
                            </div>
                            <div className="text-right">
                              <div className="text-lg font-bold text-green-600 mb-1">
                                ${Number(payment.amount || 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                              </div>
                              <Badge className={payment.status === 'POSTED' ? 'bg-green-100 text-green-800' : 'bg-amber-100 text-amber-800'}>
                                {payment.status || 'PENDING'}
                              </Badge>
                            </div>
                          </div>
                        </div>
                      ))}
                      <div className="mt-3 p-4 bg-green-100 rounded-lg flex justify-between items-center">
                        <span className="text-[15px] font-semibold text-green-800">Total Paid</span>
                        <span className="text-xl font-bold text-green-800">
                          ${payments.reduce((sum, pmt) => sum + Number(pmt.amount || 0), 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                        </span>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Outstanding Balance */}
              {invoices.length > 0 && payments.length > 0 && (
                <div className="mt-6 p-5 bg-amber-100 rounded-xl border-2 border-amber-500">
                  <div className="flex justify-between items-center">
                    <span className="text-lg font-semibold text-amber-800">
                      Outstanding Balance
                    </span>
                    <span className="text-3xl font-bold text-amber-800">
                      ${(
                        invoices.reduce((sum, inv) => sum + Number(inv.total_amount || 0), 0) -
                        payments.reduce((sum, pmt) => sum + Number(pmt.amount || 0), 0)
                      ).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                    </span>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* Details Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Financial Details */}
          <Card>
            <CardContent className="p-6">
              <h2 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
                <DollarSign size={20} className="text-blue-600" />
                Financial Details
              </h2>
              <div className="flex flex-col gap-3">
                <div>
                  <p className="text-xs text-gray-500 mb-1">Project Cost</p>
                  {isEditing ? (
                    <input
                      type="number"
                      value={editedProject?.['Project Cost (Materials + Labor)'] || ''}
                      onChange={(e) => handleEditChange('Project Cost (Materials + Labor)', parseFloat(e.target.value) || 0)}
                      className="w-full text-xl font-semibold p-2 border border-gray-300 rounded-md outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      placeholder="0"
                    />
                  ) : (
                    <p className="text-xl text-gray-800 font-semibold">
                      {formatCurrency(project['Project Cost (Materials + Labor)'])}
                    </p>
                  )}
                </div>
                <div>
                  <p className="text-xs text-gray-500 mb-1">HR PC Service Fee</p>
                  {isEditing ? (
                    <input
                      type="number"
                      value={editedProject?.['HR PC Service Fee'] || ''}
                      onChange={(e) => handleEditChange('HR PC Service Fee', parseFloat(e.target.value) || 0)}
                      className="w-full text-lg font-medium p-2 border border-gray-300 rounded-md outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      placeholder="0"
                    />
                  ) : (
                    <p className="text-lg text-gray-800 font-medium">
                      {formatCurrency(project['HR PC Service Fee'])}
                    </p>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Location Details */}
          <Card>
            <CardContent className="p-6">
              <h2 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
                <MapPin size={20} className="text-blue-600" />
                Location Details
              </h2>
              <div className="flex flex-col gap-3">
                <div>
                  <p className="text-xs text-gray-500 mb-1">City</p>
                  {isEditing ? (
                    <input
                      type="text"
                      value={editedProject?.City || ''}
                      onChange={(e) => handleEditChange('City', e.target.value)}
                      className="w-full text-sm font-medium px-2.5 py-1.5 border border-gray-300 rounded-md outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  ) : (
                    <p className="text-sm text-gray-800 font-medium">
                      {project.City || 'N/A'}
                    </p>
                  )}
                </div>
                <div>
                  <p className="text-xs text-gray-500 mb-1">County</p>
                  {isEditing ? (
                    <input
                      type="text"
                      value={editedProject?.County || ''}
                      onChange={(e) => handleEditChange('County', e.target.value)}
                      className="w-full text-sm font-medium px-2.5 py-1.5 border border-gray-300 rounded-md outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  ) : (
                    <p className="text-sm text-gray-800 font-medium">
                      {project.County || 'N/A'}
                    </p>
                  )}
                </div>
                <div>
                  <p className="text-xs text-gray-500 mb-1">Jurisdiction ID</p>
                  {isEditing ? (
                    <input
                      type="text"
                      value={editedProject?.Jurisdiction || ''}
                      onChange={(e) => handleEditChange('Jurisdiction', e.target.value)}
                      className="w-full text-sm font-medium px-2.5 py-1.5 border border-gray-300 rounded-md outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  ) : (
                    <p className="text-sm text-gray-800 font-medium">
                      {project.Jurisdiction || 'N/A'}
                    </p>
                  )}
                </div>
                <div>
                  <p className="text-xs text-gray-500 mb-1">Primary Inspector ID</p>
                  {isEditing ? (
                    <input
                      type="text"
                      value={editedProject?.['Primary Inspector'] || ''}
                      onChange={(e) => handleEditChange('Primary Inspector', e.target.value)}
                      className="w-full text-sm font-medium px-2.5 py-1.5 border border-gray-300 rounded-md outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  ) : (
                    <p className="text-sm text-gray-800 font-medium">
                      {project['Primary Inspector'] || 'N/A'}
                    </p>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Scope of Work */}
        {project['Scope of Work'] && (
          <Card className="mt-6">
            <CardContent className="p-6">
              <h2 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
                <FileText size={20} className="text-blue-600" />
                Scope of Work
              </h2>
              <p className="text-sm text-gray-600 leading-relaxed whitespace-pre-wrap">
                {project['Scope of Work']}
              </p>
            </CardContent>
          </Card>
        )}

        {/* Compliance Section (Phase Q) */}
        <Card className="mt-6">
          <CardContent className="p-6">
            <h2 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
              <FileText size={20} className="text-blue-600" />
              Compliance Information
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Licensed Business</label>
                {isEditing ? (
                  <select
                    value={editedProject?.licensed_business_id || ''}
                    onChange={(e) => handleEditChange('licensed_business_id', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="">Select Business...</option>
                    {businesses.map((b) => (
                      <option key={b.id} value={b.id}>
                        {b.business_name} ({b.license_number})
                      </option>
                    ))}
                  </select>
                ) : (
                  <p className="text-sm text-gray-900">
                    {project.licensed_business_id || 'Not assigned'}
                  </p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Qualifier</label>
                {isEditing ? (
                  <select
                    value={editedProject?.qualifier_id || ''}
                    onChange={(e) => handleEditChange('qualifier_id', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="">Select Qualifier...</option>
                    {qualifiers.map((q) => (
                      <option key={q.id} value={q.id}>
                        {q.full_name} ({q.qualifier_id_number})
                      </option>
                    ))}
                  </select>
                ) : (
                  <p className="text-sm text-gray-900">
                    {project.qualifier_id || 'Not assigned'}
                  </p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Engagement Model</label>
                {isEditing ? (
                  <select
                    value={editedProject?.engagement_model || ''}
                    onChange={(e) => handleEditChange('engagement_model', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="">Select Model...</option>
                    <option value="DIRECT_GC">Direct GC</option>
                    <option value="THIRD_PARTY_QUALIFIER">Third-Party Qualifier</option>
                  </select>
                ) : (
                  <p className="text-sm text-gray-900">
                    {project.engagement_model || 'Not set'}
                  </p>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Notes */}
        {(project.Notes || isEditing) && (
          <Card className="mt-6">
            <CardContent className="p-6">
              <h2 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
                <FileText size={20} className="text-amber-600" />
                Notes
              </h2>
              {isEditing ? (
                <textarea
                  value={editedProject?.Notes || ''}
                  onChange={(e) => handleEditChange('Notes', e.target.value)}
                  className="w-full min-h-[100px] p-3 border border-gray-300 rounded-lg text-sm outline-none font-inherit resize-y focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Add project notes..."
                />
              ) : (
                <p className="text-sm text-gray-600 leading-relaxed whitespace-pre-wrap">
                  {project.Notes}
                </p>
              )}
            </CardContent>
          </Card>
        )}

        {/* Photo Album Link */}
        {project['Photo Album'] && (
          <Card className="mt-6">
            <CardContent className="p-6">
              <h2 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
                <ImageIcon size={20} className="text-blue-600" />
                Photo Album
              </h2>
              <Button asChild>
                <a
                  href={project['Photo Album']}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-2"
                >
                  <ImageIcon size={16} />
                  View Photos
                </a>
              </Button>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
