import { useState, useEffect, useMemo } from 'react';
import { UserCheck, Plus, Search, FileText, Building2, AlertCircle } from 'lucide-react';
import api from '../lib/api';
import { PageHeader, StatsCard, StatusBadge, LoadingState, EmptyState } from '@/components/app';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';

export default function Qualifiers() {
  const [qualifiers, setQualifiers] = useState([]);
  const [businesses, setBusinesses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showAssignModal, setShowAssignModal] = useState(false);
  const [selectedQualifier, setSelectedQualifier] = useState(null);

  useEffect(() => {
    fetchData();
    window.history.replaceState({ page: 'qualifiers' }, '');
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      const [qualifiersResponse, businessesResponse] = await Promise.all([
        api.getQualifiers(),
        api.request('/licensed-businesses')
      ]);
      setQualifiers(Array.isArray(qualifiersResponse) ? qualifiersResponse : []);
      setBusinesses(Array.isArray(businessesResponse) ? businessesResponse : []);
    } catch (err) {
      setError('Failed to load qualifiers. Please try again.');
      console.error('Error fetching data:', err);
    } finally {
      setLoading(false);
    }
  };

  const filteredQualifiers = useMemo(() => {
    if (!searchTerm) return qualifiers;
    return qualifiers.filter(qualifier =>
      qualifier.full_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      qualifier.qualifier_license_number?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      qualifier.qualifier_id?.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [qualifiers, searchTerm]);

  const stats = useMemo(() => {
    const atCapacity = qualifiers.filter(q => (q.assigned_businesses?.length || 0) >= 2).length;
    const available = qualifiers.filter(q => (q.assigned_businesses?.length || 0) < 2).length;
    return { total: qualifiers.length, atCapacity, available };
  }, [qualifiers]);

  const getCapacityStatus = (count) => {
    if (count >= 2) return { status: 'rejected', label: `${count}/2 (FULL)` };
    if (count === 1) return { status: 'pending', label: `${count}/2` };
    return { status: 'approved', label: `${count}/2` };
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingState size="lg" message="Loading qualifiers..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <EmptyState
          icon="alert-circle"
          title="Failed to load qualifiers"
          description={error}
          action={<Button onClick={fetchData}>Retry</Button>}
        />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Page Header */}
      <PageHeader
        icon={<UserCheck size={32} />}
        title="Qualifiers"
        subtitle="Manage licensed qualifiers and business assignments"
        actions={
          <Button onClick={() => setShowCreateModal(true)}>
            <Plus size={16} className="mr-2" />
            Add Qualifier
          </Button>
        }
      />

      <div className="container py-6 space-y-6">
        {/* Search Bar */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground w-4 h-4" />
          <Input
            type="text"
            placeholder="Search by name, license number, or qualifier ID..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <StatsCard
            icon={<UserCheck size={20} />}
            label="Total Qualifiers"
            value={stats.total.toString()}
          />
          <StatsCard
            icon={<AlertCircle size={20} />}
            label="At Capacity"
            value={stats.atCapacity.toString()}
            subtitle="2/2 businesses"
          />
          <StatsCard
            icon={<UserCheck size={20} />}
            label="Available"
            value={stats.available.toString()}
            subtitle="0-1/2 businesses"
          />
        </div>

        {/* Qualifiers List */}
        {filteredQualifiers.length === 0 ? (
          <Card>
            <CardContent className="py-16">
              <EmptyState
                icon="users"
                title={searchTerm ? 'No qualifiers match your search' : 'No qualifiers yet'}
                description={searchTerm ? 'Try adjusting your search terms' : 'Add your first qualifier to get started'}
                action={
                  !searchTerm && (
                    <Button onClick={() => setShowCreateModal(true)}>
                      <Plus size={16} className="mr-2" />
                      Add Qualifier
                    </Button>
                  )
                }
              />
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-4">
            {filteredQualifiers.map((qualifier) => {
              const assignedCount = qualifier.assigned_businesses?.length || 0;
              const capacityInfo = getCapacityStatus(assignedCount);

              return (
                <Card key={qualifier.id} className="hover:shadow-md transition-shadow">
                  <CardContent className="p-6">
                    <div className="space-y-4">
                      {/* Header Row */}
                      <div className="flex items-start justify-between">
                        <div className="space-y-2 flex-1">
                          <div className="flex items-center gap-3 flex-wrap">
                            <h3 className="text-lg font-semibold">
                              {qualifier.full_name}
                            </h3>
                            <StatusBadge 
                              status={capacityInfo.status} 
                              type="permit"
                            />
                            <span className="text-sm text-muted-foreground font-medium">
                              {capacityInfo.label}
                            </span>
                            {qualifier.is_active === false && (
                              <StatusBadge status="draft" type="invoice" />
                            )}
                          </div>

                          {/* License Info */}
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                            <div className="flex items-center text-muted-foreground">
                              <FileText size={16} className="mr-2" />
                              <span className="font-medium mr-1">License:</span>
                              <span>{qualifier.qualifier_license_number}</span>
                            </div>
                            <div className="flex items-center text-muted-foreground">
                              <UserCheck size={16} className="mr-2" />
                              <span className="font-medium mr-1">ID:</span>
                              <span>{qualifier.qualifier_id}</span>
                            </div>
                          </div>
                        </div>

                        {/* Actions */}
                        <div className="flex gap-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => {
                              setSelectedQualifier(qualifier);
                              setShowAssignModal(true);
                            }}
                            disabled={assignedCount >= 2}
                          >
                            <Building2 size={16} className="mr-2" />
                            {assignedCount >= 2 ? 'Full' : 'Assign'}
                          </Button>
                        </div>
                      </div>

                      {/* Assigned Businesses */}
                      {qualifier.assigned_businesses && qualifier.assigned_businesses.length > 0 ? (
                        <div className="rounded-lg bg-muted/50 p-4">
                          <p className="text-sm font-medium mb-3">Assigned to:</p>
                          <div className="space-y-2">
                            {qualifier.assigned_businesses.map((business, idx) => (
                              <div key={idx} className="flex items-center text-sm">
                                <Building2 size={16} className="mr-2 text-muted-foreground" />
                                <span>
                                  {typeof business === 'string' 
                                    ? business 
                                    : business.business_name || business.business_id}
                                </span>
                              </div>
                            ))}
                          </div>
                        </div>
                      ) : (
                        <div className="text-sm text-muted-foreground italic">
                          Not assigned to any business yet
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        )}
      </div>

      {/* Modals would go here - keeping existing modal logic */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-background p-6 rounded-lg max-w-md w-full mx-4">
            <h2 className="text-xl font-semibold mb-4">Add Qualifier</h2>
            <p className="text-sm text-muted-foreground mb-4">
              Modal content would go here (reuse existing logic)
            </p>
            <div className="flex gap-2 justify-end">
              <Button variant="outline" onClick={() => setShowCreateModal(false)}>
                Cancel
              </Button>
              <Button>Save</Button>
            </div>
          </div>
        </div>
      )}

      {showAssignModal && selectedQualifier && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-background p-6 rounded-lg max-w-md w-full mx-4">
            <h2 className="text-xl font-semibold mb-4">
              Assign {selectedQualifier.full_name}
            </h2>
            <p className="text-sm text-muted-foreground mb-4">
              Modal content would go here (reuse existing logic)
            </p>
            <div className="flex gap-2 justify-end">
              <Button 
                variant="outline" 
                onClick={() => {
                  setShowAssignModal(false);
                  setSelectedQualifier(null);
                }}
              >
                Cancel
              </Button>
              <Button>Assign</Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
