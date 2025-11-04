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

export default function ProjectDetails() {
  const { currentProjectId, navigateToProjects } = useAppStore();
  const [project, setProject] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchProjectDetails();
  }, [currentProjectId]);

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
    } catch (err) {
      console.error('Failed to fetch project details:', err);
      setError('Failed to load project details');
    } finally {
      setLoading(false);
    }
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
    return (
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100vh',
        gap: '16px',
        backgroundColor: '#F8FAFC'
      }}>
        <Loader2 className="animate-spin" size={40} style={{ color: '#2563EB' }} />
        <p style={{ color: '#64748B', fontSize: '14px' }}>Loading project details...</p>
      </div>
    );
  }

  if (error || !project) {
    return (
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100vh',
        gap: '16px',
        backgroundColor: '#F8FAFC'
      }}>
        <AlertCircle size={40} style={{ color: '#DC2626' }} />
        <p style={{ color: '#DC2626', fontSize: '14px' }}>{error || 'Project not found'}</p>
        <button
          onClick={navigateToProjects}
          style={{
            padding: '8px 16px',
            backgroundColor: '#2563EB',
            color: '#FFFFFF',
            border: 'none',
            borderRadius: '8px',
            fontSize: '14px',
            cursor: 'pointer'
          }}
        >
          Back to Projects
        </button>
      </div>
    );
  }

  const statusStyle = getStatusColor(project.Status);

  return (
    <div style={{
      backgroundColor: '#F8FAFC',
      minHeight: '100vh',
      padding: '32px'
    }}>
      <div style={{
        maxWidth: '1200px',
        margin: '0 auto'
      }}>
        {/* Back Button */}
        <button
          onClick={navigateToProjects}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '8px 16px',
            backgroundColor: '#FFFFFF',
            border: '1px solid #E2E8F0',
            borderRadius: '8px',
            fontSize: '14px',
            color: '#64748B',
            cursor: 'pointer',
            marginBottom: '24px',
            transition: 'all 0.2s ease'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.backgroundColor = '#F8FAFC';
            e.currentTarget.style.color = '#2563EB';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor = '#FFFFFF';
            e.currentTarget.style.color = '#64748B';
          }}
        >
          <ArrowLeft size={16} />
          Back to Projects
        </button>

        {/* Header Card */}
        <div style={{
          backgroundColor: '#FFFFFF',
          borderRadius: '12px',
          padding: '32px',
          border: '1px solid #E2E8F0',
          marginBottom: '24px',
          boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.05)'
        }}>
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'flex-start',
            marginBottom: '16px'
          }}>
            <div>
              <h1 style={{
                fontSize: '32px',
                fontWeight: '600',
                color: '#1E293B',
                marginBottom: '8px'
              }}>
                {project['Project Name'] || 'Unnamed Project'}
              </h1>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                color: '#64748B',
                fontSize: '14px',
                marginBottom: '12px'
              }}>
                <Hash size={14} />
                Project ID: {project['Project ID']}
              </div>
            </div>
            <span style={{
              display: 'inline-flex',
              alignItems: 'center',
              padding: '8px 16px',
              borderRadius: '8px',
              backgroundColor: statusStyle.bg,
              color: statusStyle.text,
              fontSize: '14px',
              fontWeight: '500',
              border: `1px solid ${statusStyle.border}`,
              textTransform: 'capitalize'
            }}>
              {project.Status || 'N/A'}
            </span>
          </div>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
            gap: '16px',
            paddingTop: '16px',
            borderTop: '1px solid #F1F5F9'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <div style={{
                width: '40px',
                height: '40px',
                borderRadius: '8px',
                backgroundColor: '#DBEAFE',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <MapPin size={20} style={{ color: '#2563EB' }} />
              </div>
              <div>
                <p style={{ fontSize: '12px', color: '#64748B', marginBottom: '2px' }}>Location</p>
                <p style={{ fontSize: '14px', color: '#1E293B', fontWeight: '500' }}>
                  {project['Project Address'] || 'No address'}
                </p>
              </div>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <div style={{
                width: '40px',
                height: '40px',
                borderRadius: '8px',
                backgroundColor: '#ECFDF5',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <Building size={20} style={{ color: '#059669' }} />
              </div>
              <div>
                <p style={{ fontSize: '12px', color: '#64748B', marginBottom: '2px' }}>Type</p>
                <p style={{ fontSize: '14px', color: '#1E293B', fontWeight: '500' }}>
                  {project['Project Type'] || 'N/A'}
                </p>
              </div>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <div style={{
                width: '40px',
                height: '40px',
                borderRadius: '8px',
                backgroundColor: '#FEF3C7',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <Calendar size={20} style={{ color: '#D97706' }} />
              </div>
              <div>
                <p style={{ fontSize: '12px', color: '#64748B', marginBottom: '2px' }}>Start Date</p>
                <p style={{ fontSize: '14px', color: '#1E293B', fontWeight: '500' }}>
                  {formatDate(project['Start Date'])}
                </p>
              </div>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <div style={{
                width: '40px',
                height: '40px',
                borderRadius: '8px',
                backgroundColor: '#FEE2E2',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <Users size={20} style={{ color: '#DC2626' }} />
              </div>
              <div>
                <p style={{ fontSize: '12px', color: '#64748B', marginBottom: '2px' }}>Client</p>
                <p style={{ fontSize: '14px', color: '#1E293B', fontWeight: '500' }}>
                  {project['Owner Name (PM\'s Client)'] || project['Client ID'] || 'Unknown'}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Details Grid */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))',
          gap: '24px'
        }}>
          {/* Financial Details */}
          <div style={{
            backgroundColor: '#FFFFFF',
            borderRadius: '12px',
            padding: '24px',
            border: '1px solid #E2E8F0',
            boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.05)'
          }}>
            <h2 style={{
              fontSize: '18px',
              fontWeight: '600',
              color: '#1E293B',
              marginBottom: '16px',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}>
              <DollarSign size={20} style={{ color: '#2563EB' }} />
              Financial Details
            </h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <div>
                <p style={{ fontSize: '12px', color: '#64748B', marginBottom: '4px' }}>Project Cost</p>
                <p style={{ fontSize: '20px', color: '#1E293B', fontWeight: '600' }}>
                  {formatCurrency(project['Project Cost (Materials + Labor)'])}
                </p>
              </div>
              <div>
                <p style={{ fontSize: '12px', color: '#64748B', marginBottom: '4px' }}>HR PC Service Fee</p>
                <p style={{ fontSize: '18px', color: '#1E293B', fontWeight: '500' }}>
                  {formatCurrency(project['HR PC Service Fee'])}
                </p>
              </div>
            </div>
          </div>

          {/* Location Details */}
          <div style={{
            backgroundColor: '#FFFFFF',
            borderRadius: '12px',
            padding: '24px',
            border: '1px solid #E2E8F0',
            boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.05)'
          }}>
            <h2 style={{
              fontSize: '18px',
              fontWeight: '600',
              color: '#1E293B',
              marginBottom: '16px',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}>
              <MapPin size={20} style={{ color: '#2563EB' }} />
              Location Details
            </h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <div>
                <p style={{ fontSize: '12px', color: '#64748B', marginBottom: '4px' }}>City</p>
                <p style={{ fontSize: '14px', color: '#1E293B', fontWeight: '500' }}>
                  {project.City || 'N/A'}
                </p>
              </div>
              <div>
                <p style={{ fontSize: '12px', color: '#64748B', marginBottom: '4px' }}>County</p>
                <p style={{ fontSize: '14px', color: '#1E293B', fontWeight: '500' }}>
                  {project.County || 'N/A'}
                </p>
              </div>
              <div>
                <p style={{ fontSize: '12px', color: '#64748B', marginBottom: '4px' }}>Jurisdiction ID</p>
                <p style={{ fontSize: '14px', color: '#1E293B', fontWeight: '500' }}>
                  {project.Jurisdiction || 'N/A'}
                </p>
              </div>
              <div>
                <p style={{ fontSize: '12px', color: '#64748B', marginBottom: '4px' }}>Primary Inspector ID</p>
                <p style={{ fontSize: '14px', color: '#1E293B', fontWeight: '500' }}>
                  {project['Primary Inspector'] || 'N/A'}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Scope of Work */}
        {project['Scope of Work'] && (
          <div style={{
            backgroundColor: '#FFFFFF',
            borderRadius: '12px',
            padding: '24px',
            border: '1px solid #E2E8F0',
            marginTop: '24px',
            boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.05)'
          }}>
            <h2 style={{
              fontSize: '18px',
              fontWeight: '600',
              color: '#1E293B',
              marginBottom: '16px',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}>
              <FileText size={20} style={{ color: '#2563EB' }} />
              Scope of Work
            </h2>
            <p style={{
              fontSize: '14px',
              color: '#475569',
              lineHeight: '1.6',
              whiteSpace: 'pre-wrap'
            }}>
              {project['Scope of Work']}
            </p>
          </div>
        )}

        {/* Notes */}
        {project.Notes && (
          <div style={{
            backgroundColor: '#FFFFFF',
            borderRadius: '12px',
            padding: '24px',
            border: '1px solid #E2E8F0',
            marginTop: '24px',
            boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.05)'
          }}>
            <h2 style={{
              fontSize: '18px',
              fontWeight: '600',
              color: '#1E293B',
              marginBottom: '16px',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}>
              <FileText size={20} style={{ color: '#D97706' }} />
              Notes
            </h2>
            <p style={{
              fontSize: '14px',
              color: '#475569',
              lineHeight: '1.6',
              whiteSpace: 'pre-wrap'
            }}>
              {project.Notes}
            </p>
          </div>
        )}

        {/* Photo Album Link */}
        {project['Photo Album'] && (
          <div style={{
            backgroundColor: '#FFFFFF',
            borderRadius: '12px',
            padding: '24px',
            border: '1px solid #E2E8F0',
            marginTop: '24px',
            boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.05)'
          }}>
            <h2 style={{
              fontSize: '18px',
              fontWeight: '600',
              color: '#1E293B',
              marginBottom: '16px',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}>
              <ImageIcon size={20} style={{ color: '#2563EB' }} />
              Photo Album
            </h2>
            <a
              href={project['Photo Album']}
              target="_blank"
              rel="noopener noreferrer"
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '8px',
                padding: '10px 16px',
                backgroundColor: '#2563EB',
                color: '#FFFFFF',
                borderRadius: '8px',
                textDecoration: 'none',
                fontSize: '14px',
                fontWeight: '500',
                transition: 'all 0.2s ease'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = '#1D4ED8';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = '#2563EB';
              }}
            >
              <ImageIcon size={16} />
              View Photos
            </a>
          </div>
        )}
      </div>
    </div>
  );
}
