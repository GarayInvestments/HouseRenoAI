import { Building2, Plus, Search, FileText } from 'lucide-react';
import { useState, useEffect, useMemo } from 'react';
import api from '@/lib/api';
import { PageHeader, StatsCard, StatusBadge, LoadingState, EmptyState } from '@/components/app';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent } from '@/components/ui/card';

export default function LicensedBusinesses() {
  const [businesses, setBusinesses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);

  useEffect(() => {
    fetchBusinesses();
    window.history.replaceState({ page: 'licensed-businesses' }, '');
  }, []);

  const fetchBusinesses = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await api.request('/licensed-businesses');
      setBusinesses(Array.isArray(response) ? response : []);
    } catch (err) {
      setError('Failed to load licensed businesses');
      console.error('Error fetching businesses:', err);
    } finally {
      setLoading(false);
    }
  };

  const filteredBusinesses = useMemo(() => {
    if (!searchTerm) return businesses;
    return businesses.filter(business =>
      business.business_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      business.license_number?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      business.business_id?.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [businesses, searchTerm]);

  const stats = useMemo(() => ({
    total: businesses.length,
    active: businesses.filter(b => b.is_active !== false).length,
    ownerCompanies: businesses.filter(b => b.is_owner_company).length
  }), [businesses]);

  if (loading) return <LoadingState />;
  if (error) return <EmptyState icon="alert" title="Error loading businesses" description={error} />;

  return (
    <div className="min-h-screen bg-background">
      <div className="mx-auto max-w-6xl px-6 py-8 space-y-8">
      <PageHeader
        icon={<Building2 className="h-8 w-8" />}
        title="Licensed Businesses"
        subtitle="Manage NCLBGC-licensed business entities"
        actions={
          <Button onClick={() => setShowCreateModal(true)} size="default">
            <Plus className="h-4 w-4 mr-2" />
            Add Business
          </Button>
        }
      />

      {/* Search */}
      <Card className="shadow-sm border-border/60">
        <CardContent className="p-4 md:p-5">
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div className="relative w-full md:max-w-xl">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search by name, license number, or business ID..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 h-11 border-border/70"
              />
            </div>
            <div className="flex items-center gap-2">
              <Button onClick={() => setShowCreateModal(true)}>
                <Plus className="h-4 w-4 mr-2" />
                Add Business
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-3">
        <StatsCard
          label="Total Businesses"
          value={stats.total}
          icon={<Building2 className="h-4 w-4" />}
          className="shadow-sm"
        />
        <StatsCard
          label="Active"
          value={stats.active}
          icon={<Building2 className="h-4 w-4" />}
          className="shadow-sm"
        />
        <StatsCard
          label="Owner Companies"
          value={stats.ownerCompanies}
          icon={<Building2 className="h-4 w-4" />}
          className="shadow-sm"
        />
      </div>

      {/* Business List */}
      {filteredBusinesses.length === 0 ? (
        <EmptyState
          icon="inbox"
          title={searchTerm ? "No businesses found" : "No licensed businesses"}
          description={searchTerm ? "Try adjusting your search" : "Add your first business to get started"}
          action={!searchTerm && (
            <Button onClick={() => setShowCreateModal(true)}>
              <Plus className="w-4 h-4 mr-2" />
              Add Business
            </Button>
          )}
        />
      ) : (
        <Card className="border-border/60 shadow-sm">
          <CardContent className="p-0">
            <div className="divide-y divide-border/70">
              {filteredBusinesses.map((business) => (
                <div key={business.id} className="p-5 md:p-6 hover:bg-muted/50 transition-colors">
                  <div className="flex flex-col gap-3">
                    <div className="flex flex-wrap items-start justify-between gap-2">
                      <div className="space-y-1">
                        <h3 className="text-lg font-semibold text-foreground leading-tight">{business.business_name}</h3>
                        <div className="flex items-center gap-2 flex-wrap">
                          {business.is_owner_company && (
                            <StatusBadge status="approved" text="Owner Company" />
                          )}
                          {business.is_active === false && (
                            <StatusBadge status="rejected" text="Inactive" />
                          )}
                        </div>
                      </div>
                    </div>

                    <div className="grid gap-3 sm:grid-cols-2 text-sm">
                      <div className="flex items-center gap-2 text-muted-foreground">
                        <FileText className="h-4 w-4 flex-shrink-0" />
                        <span className="font-medium text-foreground">License:</span>
                        <span className="text-foreground">{business.license_number}</span>
                      </div>
                      <div className="flex items-center gap-2 text-muted-foreground">
                        <Building2 className="h-4 w-4 flex-shrink-0" />
                        <span className="font-medium text-foreground">ID:</span>
                        <span className="text-foreground">{business.business_id}</span>
                      </div>
                    </div>

                    {business.business_address && (
                      <div className="text-sm text-muted-foreground border-t border-border pt-3">
                        {business.business_address}
                        {business.city && `, ${business.city}`}
                        {business.state && `, ${business.state}`}
                        {business.zip_code && ` ${business.zip_code}`}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Create Modal - Placeholder */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <Card className="max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <CardContent className="p-6">
              <h2 className="text-2xl font-bold mb-4">Add Licensed Business</h2>
              <p className="text-muted-foreground mb-4">Modal form will be wired up next</p>
              <Button onClick={() => setShowCreateModal(false)}>Close</Button>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
    </div>
  );
}
