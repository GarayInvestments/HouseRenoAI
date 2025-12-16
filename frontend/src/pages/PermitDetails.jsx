import { useEffect, useState } from 'react';
import {
  ArrowLeft,
  FileText,
  Calendar,
  CheckCircle,
  Clock,
  AlertCircle,
  ExternalLink,
  Download,
  Hash,
  FolderKanban,
  User,
  Loader2
} from 'lucide-react';
import api from '../lib/api';
import { useAppStore } from '../stores/appStore';
import { PERMIT_STATUS_OPTIONS, PERMIT_TYPE_OPTIONS, formatEnumLabel } from '../constants/enums';
import { StatusBadge, PageHeader, LoadingState } from '@/components/app';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

export default function PermitDetails() {
  const { currentPermitId, navigateToPermits, navigateToProject, navigateToClient } = useAppStore();
  const [permit, setPermit] = useState(null);
  const [project, setProject] = useState(null);
  const [client, setClient] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [editedPermit, setEditedPermit] = useState(null);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    const fetchPermitDetails = async () => {
      try {
        setLoading(true);
        setError(null);

        // Fetch single permit by ID (not all permits)
        const permitData = await api.getPermit(currentPermitId);

        if (permitData) {
          setPermit(permitData);

          // Get project ID from permit (handle both old and new field names)
          const projectId = permitData['Project ID'] || permitData.project_id;

          if (projectId) {
            // Fetch related project and all clients
            const [projectData, clientsData] = await Promise.all([
              api.getProject(projectId),
              api.getClients()
            ]);

            setProject(projectData);

            // Find related client through project
            const clientId = projectData?.['Client ID'] || projectData?.client_id;
            if (clientId && Array.isArray(clientsData)) {
              const relatedClient = clientsData.find(c =>
                c['Client ID'] === clientId ||
                c['ID'] === clientId ||
                c.client_id === clientId ||
                c.id === clientId
              );
              setClient(relatedClient);
            }
          }
        } else {
          setError('Permit not found');
        }
      } catch (err) {
        console.error('Failed to load permit details:', err);
        setError('Failed to load permit details');
      } finally {
        setLoading(false);
      }
    };

    if (currentPermitId) {
      fetchPermitDetails();
    } else {
      setError('No permit ID provided');
      setLoading(false);
    }
  }, [currentPermitId]);

  // Handle browser back button
  useEffect(() => {
    const handlePopState = () => {
      navigateToPermits();
    };

    // Push a state when component mounts
    window.history.pushState({ page: 'permit-details' }, '');

    // Listen for back button
    window.addEventListener('popstate', handlePopState);

    return () => {
      window.removeEventListener('popstate', handlePopState);
    };
  }, [navigateToPermits]);

  const formatDate = (dateString) => {
    if (!dateString) return 'Not set';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' });
  };

  const toDateInput = (val) =>
    val ? new Date(val).toISOString().split('T')[0] : '';

  const handleSave = async () => {
    try {
      setIsSaving(true);

      // Map frontend display field names to backend database column names
      const fieldMapping = {
        'Permit Number': 'permit_number',
        'Permit Status': 'status',
        'Date Submitted': 'application_date',
        'Date Approved': 'approval_date'
      };

      // Convert editedPermit keys from display names to database column names
      const mappedData = {};
      Object.keys(editedPermit).forEach(key => {
        const dbFieldName = fieldMapping[key] || key;
        mappedData[dbFieldName] = editedPermit[key];
      });

      await api.updatePermit(currentPermitId, mappedData);
      setPermit({ ...permit, ...editedPermit });
      setIsEditing(false);
      setEditedPermit(null);
    } catch (error) {
      console.error('Failed to save permit:', error);
      alert('Failed to save changes. Please try again.');
    } finally {
      setIsSaving(false);
    }
  };

  const handleCancel = () => {
    setIsEditing(false);
    setEditedPermit(null);
  };

  const handleEditChange = (field, value) => {
    setEditedPermit(prev => ({ ...prev, [field]: value }));
  };

  if (loading) {
    return <LoadingState message="Loading permit details..." />;
  }

  if (error || !permit) {
    return (
      <div className="flex flex-col items-center justify-center h-screen gap-4 bg-slate-50">
        <AlertCircle size={40} className="text-red-600" />
        <p className="text-red-600 text-sm">{error || 'Permit not found'}</p>
        <Button onClick={navigateToPermits}>Back to Permits</Button>
      </div>
    );
  }

  const permitStatus = permit?.['Permit Status'] || permit?.status;
  const permitNumber = permit?.['Permit Number'] || permit?.permit_number || permit?.business_id;
  const permitId = permit?.['Permit ID'] || permit?.permit_id;
  const dateSubmitted = permit?.['Date Submitted'] || permit?.application_date;
  const dateApproved = permit?.['Date Approved'] || permit?.approval_date;

  return (
    <div className="bg-slate-50 min-h-screen p-8">
      <div className="max-w-6xl mx-auto">
        {/* Back Button & Edit Controls */}
        <div className="flex justify-between items-center mb-6">
          <Button variant="outline" onClick={navigateToPermits}>
            <ArrowLeft size={16} className="mr-2" />
            Back to Permits
          </Button>

          {!isEditing ? (
            <Button
              onClick={() => {
                setIsEditing(true);
                setEditedPermit({
                  'Permit Number': permit['Permit Number'] ?? permit.permit_number,
                  'Permit Status': permit['Permit Status'] ?? permit.status,
                  'Date Submitted': permit['Date Submitted'] ?? permit.application_date,
                  'Date Approved': permit['Date Approved'] ?? permit.approval_date,
                  'Permit Type': permit['Permit Type'] ?? permit.permit_type
                });
              }}
            >
              Edit Permit
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
          <CardContent className="pt-6">
            <div className="flex justify-between items-start mb-4">
              <div>
                {isEditing ? (
                  <input
                    type="text"
                    value={editedPermit?.['Permit Number'] || editedPermit?.permit_number || ''}
                    onChange={(e) => {
                      handleEditChange('Permit Number', e.target.value);
                      handleEditChange('permit_number', e.target.value);
                    }}
                    className="text-3xl font-semibold text-slate-800 mb-2 w-full px-2 py-1 border-2 border-blue-600 rounded-lg outline-none"
                    placeholder="Permit Number"
                  />
                ) : (
                  <h1 className="text-3xl font-semibold text-slate-800 mb-2">
                    Permit {permitNumber || 'Unknown'}
                  </h1>
                )}
                <div className="flex items-center gap-2 text-slate-500 text-sm mb-3">
                  <Hash size={14} />
                  Permit ID: {permitId || permit?.business_id || 'N/A'}
                </div>
              </div>
              {isEditing ? (
                <select
                  value={editedPermit?.['Permit Status'] || editedPermit?.status || ''}
                  onChange={(e) => {
                    handleEditChange('Permit Status', e.target.value);
                    handleEditChange('status', e.target.value);
                  }}
                  className="px-4 py-2 rounded-lg text-sm font-medium border-2 border-blue-600 outline-none"
                >
                  <option value="">Select status...</option>
                  {PERMIT_STATUS_OPTIONS.map(opt => (
                    <option key={opt.value} value={opt.value}>
                      {opt.label}
                    </option>
                  ))}
                </select>
              ) : (
                <StatusBadge status={permitStatus?.toLowerCase()} type="permit" />
              )}
            </div>

<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 pt-4 border-t border-slate-200">
              {/* Date Submitted */}
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-blue-50 flex items-center justify-center">
                  <Calendar size={20} className="text-blue-600" />
                </div>
                <div className="flex-1">
                  <p className="text-xs text-slate-500 mb-0.5">Date Submitted</p>
                  {isEditing ? (
                    <input
                      type="date"
                      value={toDateInput(editedPermit?.['Date Submitted'] || editedPermit?.application_date)}
                      onChange={(e) => handleEditChange('Date Submitted', e.target.value)}
                      className="w-full px-2.5 py-1.5 border border-slate-300 rounded text-sm outline-none"
                    />
                  ) : (
                    <p className="text-sm text-slate-800 font-medium">
                      {formatDate(dateSubmitted)}
                    </p>
                  )}
                </div>
              </div>

              {/* Date Approved */}
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-green-50 flex items-center justify-center">
                  <CheckCircle size={20} className="text-green-600" />
                </div>
                <div className="flex-1">
                  <p className="text-xs text-slate-500 mb-0.5">Date Approved</p>
                  {isEditing ? (
                    <input
                      type="date"
                      value={toDateInput(editedPermit?.['Date Approved'] || editedPermit?.approval_date)}
                      onChange={(e) => handleEditChange('Date Approved', e.target.value)}
                      className="w-full px-2.5 py-1.5 border border-slate-300 rounded text-sm outline-none"
                    />
                  ) : (
                    <p className="text-sm text-slate-800 font-medium">
                      {formatDate(dateApproved)}
                    </p>
                  )}
                </div>
              </div>

              {/* Permit Type */}
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-sky-50 flex items-center justify-center">
                  <FileText size={20} className="text-sky-600" />
                </div>
                <div className="flex-1">
                  <p className="text-xs text-slate-500 mb-0.5">Permit Type</p>
                  {isEditing ? (
                    <select
                      value={editedPermit?.['Permit Type'] || editedPermit?.permit_type || ''}
                      onChange={(e) => handleEditChange('Permit Type', e.target.value)}
                      className="w-full px-2.5 py-1.5 border border-slate-300 rounded text-sm outline-none"
                    >
                      <option value="">Select type...</option>
                      {PERMIT_TYPE_OPTIONS.map(opt => (
                        <option key={opt.value} value={opt.value}>{opt.label}</option>
                      ))}
                    </select>
                  ) : (
                    <p className="text-sm text-slate-800 font-medium">
                      {formatEnumLabel(permit['Permit Type'] || permit.permit_type) || 'N/A'}
                    </p>
                  )}
                </div>
              </div>

              {/* Project */}
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-amber-50 flex items-center justify-center">
                  <FolderKanban size={20} className="text-amber-600" />
                </div>
                <div>
                  <p className="text-xs text-slate-500 mb-0.5">Project</p>
                  {project ? (
                    <button
                      onClick={() => navigateToProject(permit['Project ID'])}
                      className="text-sm text-blue-600 font-medium underline hover:text-blue-800 text-left"
                    >
                      {project['Project Name'] || permit['Project ID']}
                    </button>
                  ) : (
                    <p className="text-sm text-slate-800 font-medium">
                      {permit['Project ID'] || 'N/A'}
                    </p>
                  )}
                </div>
              </div>

              {/* Client */}
              {client && (
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-red-50 flex items-center justify-center">
                    <User size={20} className="text-red-600" />
                  </div>
                  <div>
                    <p className="text-xs text-slate-500 mb-0.5">Client</p>
                    <button
                      onClick={() => navigateToClient(client['Client ID'] || client['ID'])}
                      className="text-sm text-blue-600 font-medium underline hover:text-blue-800 text-left"
                    >
                      {client['Full Name'] || client['Client Name'] || client['Client ID'] || client['ID']}
                    </button>
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

          {/* Details Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* City Portal Link */}
          {permit['City Portal Link'] && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <ExternalLink size={20} className="text-blue-600" />
                  City Portal
                </CardTitle>
              </CardHeader>
              <CardContent>
                <a
                  href={permit['City Portal Link']}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-2 px-4 py-2.5 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors"
                >
                  <ExternalLink size={16} />
                  Open City Portal
                </a>
              </CardContent>
            </Card>
          )}

          {/* File Upload */}
          {permit['File Upload'] && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileText size={20} className="text-blue-600" />
                  Documents
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-3 p-3 bg-slate-50 rounded-lg border border-slate-200">
                  <FileText size={20} className="text-slate-500" />
                  <div className="flex-1">
                    <p className="text-sm font-medium text-slate-800 mb-0.5">
                      {permit['File Upload'].split('/').pop()}
                    </p>
                    <p className="text-xs text-slate-500">
                      Permit Document
                    </p>
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    className="gap-1"
                  >
                    <Download size={14} />
                    Download
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
