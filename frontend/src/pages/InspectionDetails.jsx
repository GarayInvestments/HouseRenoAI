import { useEffect, useState } from 'react';
import { Calendar, Camera, CheckCircle, ClipboardCheck, Loader2, Plus, Trash2, User } from 'lucide-react';

import api from '../lib/api';
import ErrorState from '../components/ErrorState';
import { useAppStore } from '../stores/appStore';
import useInspectionsStore from '../stores/inspectionsStore';

import { LoadingState, PageHeader, StatusBadge } from '@/components/app';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';

export default function InspectionDetails() {
  const { currentInspectionId, navigateToInspections } = useAppStore();
  const { updateInspection, deleteInspection, addPhoto, addDeficiency } = useInspectionsStore();

  const [inspection, setInspection] = useState(null);
  const [project, setProject] = useState(null);
  const [permit, setPermit] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [isEditing, setIsEditing] = useState(false);
  const [editedInspection, setEditedInspection] = useState(null);
  const [isSaving, setIsSaving] = useState(false);

  const [showPhotoModal, setShowPhotoModal] = useState(false);
  const [photoForm, setPhotoForm] = useState({ url: '', description: '' });

  const [showDeficiencyModal, setShowDeficiencyModal] = useState(false);
  const [deficiencyForm, setDeficiencyForm] = useState({
    description: '',
    severity: 'medium',
    status: 'open',
  });

  useEffect(() => {
    if (currentInspectionId) {
      loadInspectionDetails();
    } else {
      setError('No inspection ID provided');
      setLoading(false);
    }
  }, [currentInspectionId]);

  // Handle browser back button
  useEffect(() => {
    const handlePopState = () => {
      navigateToInspections();
    };

    window.history.pushState({ page: 'inspection-details' }, '');
    window.addEventListener('popstate', handlePopState);
    return () => {
      window.removeEventListener('popstate', handlePopState);
    };
  }, [navigateToInspections]);

  const loadInspectionDetails = async () => {
    setLoading(true);
    setError(null);

    try {
      if (!currentInspectionId) {
        setError('No inspection ID provided');
        setLoading(false);
        return;
      }

      const inspectionData = await api.getInspection(currentInspectionId);
      if (!inspectionData) {
        setError('Inspection not found');
        setLoading(false);
        return;
      }

      setInspection(inspectionData);

      const projectId = inspectionData.project_id || inspectionData['Project ID'];
      const permitId = inspectionData.permit_id || inspectionData['Permit ID'];

      if (projectId) {
        try {
          const projectData = await api.getProject(projectId);
          setProject(projectData);
        } catch (projectErr) {
          // Don't fail the whole page for missing related records
          if (projectErr?.message?.startsWith('API error: 404')) {
            setProject(null);
          } else {
            throw projectErr;
          }
        }
      } else {
        setProject(null);
      }

      if (permitId) {
        try {
          const permitData = await api.getPermit(permitId);
          setPermit(permitData);
        } catch (permitErr) {
          // Common in legacy/partial data: inspection points at missing permit
          if (permitErr?.message?.startsWith('API error: 404')) {
            setPermit(null);
          } else {
            throw permitErr;
          }
        }
      } else {
        setPermit(null);
      }

      setLoading(false);
    } catch (err) {
      console.error('Failed to load inspection details:', err);
      setError(err.message || 'Failed to load inspection details');
      setLoading(false);
    }
  };

  const formatDateTime = (dateString) => {
    if (!dateString) return 'Not set';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const toDatetimeLocalInputValue = (value) => {
    if (!value) return '';
    try {
      return new Date(value).toISOString().slice(0, 16);
    } catch {
      return '';
    }
  };

  const handleEdit = () => {
    setIsEditing(true);
    setEditedInspection(inspection);
  };

  const handleCancelEdit = () => {
    setIsEditing(false);
    setEditedInspection(null);
  };

  const handleEditChange = (field, value) => {
    setEditedInspection((prev) => ({ ...(prev || {}), [field]: value }));
  };

  const handleSave = async () => {
    try {
      setIsSaving(true);
      const updated = await updateInspection(currentInspectionId, editedInspection);
      setInspection(updated);
      setIsEditing(false);
      setEditedInspection(null);
    } catch (err) {
      alert('Failed to update inspection: ' + err.message);
    } finally {
      setIsSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete this inspection? This action cannot be undone.')) {
      return;
    }

    try {
      await deleteInspection(currentInspectionId);
      alert('Inspection deleted successfully');
      navigateToInspections();
    } catch (err) {
      alert('Failed to delete inspection: ' + err.message);
    }
  };

  const handleAddPhoto = async () => {
    if (!photoForm.url.trim()) {
      alert('Please provide a photo URL');
      return;
    }

    try {
      const updated = await addPhoto(currentInspectionId, photoForm);
      setInspection(updated);
      setShowPhotoModal(false);
      setPhotoForm({ url: '', description: '' });
    } catch (err) {
      alert('Failed to add photo: ' + err.message);
    }
  };

  const handleAddDeficiency = async () => {
    if (!deficiencyForm.description.trim()) {
      alert('Please provide a deficiency description');
      return;
    }

    try {
      const updated = await addDeficiency(currentInspectionId, deficiencyForm);
      setInspection(updated);
      setShowDeficiencyModal(false);
      setDeficiencyForm({ description: '', severity: 'medium', status: 'open' });
    } catch (err) {
      alert('Failed to add deficiency: ' + err.message);
    }
  };

  const inspectionStatus = inspection?.status || inspection?.['Inspection Status'] || '';
  const inspectionType = inspection?.inspection_type || inspection?.['Inspection Type'] || 'Inspection';
  const businessId = inspection?.business_id || inspection?.['Inspection ID'] || '';
  const scheduledDate = inspection?.scheduled_date || inspection?.['Scheduled Date'];
  const completedDate = inspection?.completed_date || inspection?.['Completed Date'];
  const inspector = inspection?.inspector || 'Not assigned';
  const result = inspection?.result || inspection?.['Result'];
  const notes = inspection?.notes || '';
  const photos = Array.isArray(inspection?.photos) ? inspection.photos : [];
  const deficiencies = Array.isArray(inspection?.deficiencies) ? inspection.deficiencies : [];

  const getSeverityBadge = (severity) => {
    const s = severity?.toString().toLowerCase();
    if (s === 'critical') return { variant: 'destructive', className: '' };
    if (s === 'high') return { variant: 'secondary', className: 'bg-orange-100 text-orange-800 hover:bg-orange-100' };
    if (s === 'medium') return { variant: 'secondary', className: 'bg-yellow-100 text-yellow-800 hover:bg-yellow-100' };
    return { variant: 'secondary', className: 'bg-blue-100 text-blue-800 hover:bg-blue-100' };
  };

  const getDeficiencyStatusBadge = (status) => {
    const s = status?.toString().toLowerCase();
    if (s === 'resolved') return { variant: 'secondary', className: 'bg-green-100 text-green-800 hover:bg-green-100' };
    if (s === 'in-progress') return { variant: 'secondary', className: 'bg-blue-100 text-blue-800 hover:bg-blue-100' };
    return { variant: 'secondary', className: 'bg-yellow-100 text-yellow-800 hover:bg-yellow-100' };
  };

  if (loading) {
    return <LoadingState message="Loading inspection details..." />;
  }

  if (error) {
    return <ErrorState message={error} onRetry={loadInspectionDetails} />;
  }

  if (!inspection) {
    return <ErrorState message="Inspection not found" onRetry={() => navigateToInspections()} />;
  }

  return (
    <div className="mx-auto max-w-6xl p-6">
      <PageHeader
        icon={<ClipboardCheck size={32} />}
        title={inspectionType}
        subtitle={businessId || undefined}
        showBack
        onBack={navigateToInspections}
        actions={
          !isEditing ? (
            <>
              <Button
                onClick={handleEdit}
              >
                Edit
              </Button>
              <Button variant="destructive" onClick={handleDelete}>
                <Trash2 size={16} aria-hidden="true" />
                Delete
              </Button>
            </>
          ) : (
            <>
              <Button variant="outline" onClick={handleCancelEdit} disabled={isSaving}>
                Cancel
              </Button>
              <Button onClick={handleSave} disabled={isSaving}>
                {isSaving && <Loader2 className="mr-2 h-4 w-4 animate-spin" aria-hidden="true" />}
                {isSaving ? 'Saving...' : 'Save Changes'}
              </Button>
            </>
          )
        }
      />

      <div className="mt-6 space-y-6">
        <Card>
          <CardHeader>
            <div className="flex flex-wrap items-start justify-between gap-3">
              <CardTitle>Inspection Details</CardTitle>
              <StatusBadge type="inspection" status={inspectionStatus} />
            </div>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              <div className="space-y-2">
                <div className="text-sm font-medium text-muted-foreground">Status</div>
                {isEditing ? (
                  <select
                    value={editedInspection?.status || ''}
                    onChange={(e) => handleEditChange('status', e.target.value)}
                    className="h-9 w-full max-w-xs rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                  >
                    <option value="scheduled">Scheduled</option>
                    <option value="in-progress">In Progress</option>
                    <option value="completed">Completed</option>
                    <option value="failed">Failed</option>
                    <option value="cancelled">Cancelled</option>
                  </select>
                ) : (
                  <StatusBadge type="inspection" status={inspectionStatus} />
                )}
              </div>

              <div className="space-y-2">
                <div className="text-sm font-medium text-muted-foreground">Type</div>
                {isEditing ? (
                  <Input
                    className="max-w-xs"
                    value={editedInspection?.inspection_type || ''}
                    onChange={(e) => handleEditChange('inspection_type', e.target.value)}
                  />
                ) : (
                  <div className="text-sm font-medium text-foreground">{inspectionType || 'N/A'}</div>
                )}
              </div>

              <div className="space-y-2">
                <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
                  <User size={16} className="text-muted-foreground" />
                  Inspector
                </div>
                {isEditing ? (
                  <Input
                    className="max-w-xs"
                    value={editedInspection?.inspector || ''}
                    onChange={(e) => handleEditChange('inspector', e.target.value)}
                  />
                ) : (
                  <div className="text-sm font-medium text-foreground">{inspector}</div>
                )}
              </div>

              <div className="space-y-2">
                <div className="text-sm font-medium text-muted-foreground">Result</div>
                {isEditing ? (
                  <select
                    value={editedInspection?.result || ''}
                    onChange={(e) => handleEditChange('result', e.target.value)}
                    className="h-9 w-full max-w-xs rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                  >
                    <option value="">Not set</option>
                    <option value="pass">Pass</option>
                    <option value="fail">Fail</option>
                    <option value="partial">Partial</option>
                    <option value="no-access">No Access</option>
                  </select>
                ) : (
                  <div className="text-sm font-medium text-foreground">{result || 'Not set'}</div>
                )}
              </div>

              <div className="space-y-2">
                <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
                  <Calendar size={16} className="text-muted-foreground" />
                  Scheduled Date
                </div>
                {isEditing ? (
                  <Input
                    type="datetime-local"
                    className="max-w-xs"
                    value={toDatetimeLocalInputValue(editedInspection?.scheduled_date)}
                    onChange={(e) => handleEditChange('scheduled_date', e.target.value)}
                  />
                ) : (
                  <div className="text-sm text-foreground">{formatDateTime(scheduledDate)}</div>
                )}
              </div>

              <div className="space-y-2">
                <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
                  <CheckCircle size={16} className="text-muted-foreground" />
                  Completed Date
                </div>
                {isEditing ? (
                  <Input
                    type="datetime-local"
                    className="max-w-xs"
                    value={toDatetimeLocalInputValue(editedInspection?.completed_date)}
                    onChange={(e) => handleEditChange('completed_date', e.target.value)}
                  />
                ) : (
                  <div className="text-sm text-foreground">{formatDateTime(completedDate)}</div>
                )}
              </div>

              <div className="space-y-2">
                <div className="text-sm font-medium text-muted-foreground">Project</div>
                <div className="text-sm text-foreground">{project?.project_name || project?.['Project Name'] || 'Unknown'}</div>
              </div>

              <div className="space-y-2">
                <div className="text-sm font-medium text-muted-foreground">Permit</div>
                <div className="text-sm text-foreground">
                  {permit?.permit_number ||
                    permit?.business_id ||
                    permit?.['Permit Number'] ||
                    inspection?.permit_id ||
                    inspection?.['Permit ID'] ||
                    'Unknown'}
                </div>
              </div>
            </div>

            <div className="space-y-2 border-t pt-6">
              <div className="text-sm font-medium text-muted-foreground">Notes</div>
              {isEditing ? (
                <textarea
                  rows={4}
                  value={editedInspection?.notes || ''}
                  onChange={(e) => handleEditChange('notes', e.target.value)}
                  className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                />
              ) : (
                <div className="whitespace-pre-wrap text-sm text-foreground">{notes || 'No notes'}</div>
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex flex-wrap items-center justify-between gap-3">
              <CardTitle>Photos ({photos.length})</CardTitle>
              <Button onClick={() => setShowPhotoModal(true)}>
                <Plus size={16} aria-hidden="true" />
                Add Photo
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            {photos.length === 0 ? (
              <div className="flex flex-col items-center justify-center gap-2 py-10 text-muted-foreground">
                <Camera size={40} className="opacity-50" aria-hidden="true" />
                <div className="text-sm">No photos yet</div>
              </div>
            ) : (
              <div className="grid grid-cols-[repeat(auto-fill,minmax(160px,1fr))] gap-4">
                {photos.map((photo, idx) => (
                  <div key={idx} className="overflow-hidden rounded-md border">
                    <img
                      src={photo.url}
                      alt={photo.description || 'Inspection photo'}
                      className="h-40 w-full object-cover"
                      loading="lazy"
                    />
                    {photo.description && (
                      <div className="p-2 text-xs text-muted-foreground">{photo.description}</div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex flex-wrap items-center justify-between gap-3">
              <CardTitle>Deficiencies ({deficiencies.length})</CardTitle>
              <Button onClick={() => setShowDeficiencyModal(true)}>
                <Plus size={16} aria-hidden="true" />
                Add Deficiency
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            {deficiencies.length === 0 ? (
              <div className="flex flex-col items-center justify-center gap-2 py-10 text-muted-foreground">
                <CheckCircle size={40} className="opacity-50" aria-hidden="true" />
                <div className="text-sm">No deficiencies found</div>
              </div>
            ) : (
              <div className="space-y-3">
                {deficiencies.map((deficiency, idx) => {
                  const severity = getSeverityBadge(deficiency.severity);
                  const dStatus = getDeficiencyStatusBadge(deficiency.status);
                  return (
                    <div key={idx} className="rounded-md border bg-muted/30 p-4">
                      <div className="flex flex-wrap items-start justify-between gap-3">
                        <div className="text-sm font-medium text-foreground">{deficiency.description}</div>
                        <div className="flex items-center gap-2">
                          <Badge variant={severity.variant} className={severity.className}>
                            {deficiency.severity}
                          </Badge>
                          <Badge variant={dStatus.variant} className={dStatus.className}>
                            {deficiency.status}
                          </Badge>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {showPhotoModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="w-full max-w-md rounded-lg border bg-background p-6 shadow-lg">
            <div className="space-y-1">
              <h3 className="text-lg font-semibold text-foreground">Add Photo</h3>
              <p className="text-sm text-muted-foreground">Add a photo URL and optional description.</p>
            </div>

            <div className="mt-4 space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium text-muted-foreground">Photo URL</label>
                <Input
                  value={photoForm.url}
                  onChange={(e) => setPhotoForm({ ...photoForm, url: e.target.value })}
                  placeholder="https://example.com/photo.jpg"
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-muted-foreground">Description (Optional)</label>
                <Input
                  value={photoForm.description}
                  onChange={(e) => setPhotoForm({ ...photoForm, description: e.target.value })}
                  placeholder="Photo description"
                />
              </div>
            </div>

            <div className="mt-6 flex items-center justify-end gap-2">
              <Button variant="outline" onClick={() => setShowPhotoModal(false)}>
                Cancel
              </Button>
              <Button onClick={handleAddPhoto}>Add Photo</Button>
            </div>
          </div>
        </div>
      )}

      {showDeficiencyModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="w-full max-w-md rounded-lg border bg-background p-6 shadow-lg">
            <div className="space-y-1">
              <h3 className="text-lg font-semibold text-foreground">Add Deficiency</h3>
              <p className="text-sm text-muted-foreground">Log a deficiency found during inspection.</p>
            </div>

            <div className="mt-4 space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium text-muted-foreground">Description</label>
                <textarea
                  rows={3}
                  value={deficiencyForm.description}
                  onChange={(e) => setDeficiencyForm({ ...deficiencyForm, description: e.target.value })}
                  placeholder="Describe the deficiency..."
                  className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-muted-foreground">Severity</label>
                <select
                  value={deficiencyForm.severity}
                  onChange={(e) => setDeficiencyForm({ ...deficiencyForm, severity: e.target.value })}
                  className="h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="critical">Critical</option>
                </select>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-muted-foreground">Status</label>
                <select
                  value={deficiencyForm.status}
                  onChange={(e) => setDeficiencyForm({ ...deficiencyForm, status: e.target.value })}
                  className="h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                >
                  <option value="open">Open</option>
                  <option value="in-progress">In Progress</option>
                  <option value="resolved">Resolved</option>
                </select>
              </div>
            </div>

            <div className="mt-6 flex items-center justify-end gap-2">
              <Button variant="outline" onClick={() => setShowDeficiencyModal(false)}>
                Cancel
              </Button>
              <Button onClick={handleAddDeficiency}>Add Deficiency</Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
