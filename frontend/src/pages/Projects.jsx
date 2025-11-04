import { FolderKanban, Plus, Search, MapPin, Users, Calendar, AlertCircle, Loader2 } from 'lucide-react';
import { useState, useEffect } from 'react';
import api from '../lib/api';

export default function Projects() {
  const [searchTerm, setSearchTerm] = useState('');
  const [hoveredCard, setHoveredCard] = useState(null);
  const [hoveredButton, setHoveredButton] = useState(false);
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getProjects();
      setProjects(data.projects || []);
    } catch (err) {
      console.error('Failed to fetch projects:', err);
      setError('Failed to load projects. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const filteredProjects = projects.filter(project =>
    project['Project Name']?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    project['Project Address']?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return { bg: '#DBEAFE', text: '#2563EB', border: '#93C5FD' };
      case 'completed': return { bg: '#ECFDF5', text: '#059669', border: '#A7F3D0' };
      case 'planning': return { bg: '#FEF3C7', text: '#D97706', border: '#FCD34D' };
      default: return { bg: '#F3F4F6', text: '#6B7280', border: '#D1D5DB' };
    }
  };

  const getProgressColor = (progress) => {
    if (progress >= 75) return '#059669';
    if (progress >= 50) return '#2563EB';
    if (progress >= 25) return '#D97706';
    return '#DC2626';
  };

  const calculateProgress = (project) => {
    // Calculate progress based on status or actual progress field
    if (project.Progress !== undefined) return project.Progress;
    
    switch (project.Status?.toLowerCase()) {
      case 'completed':
        return 100;
      case 'in progress':
      case 'active':
        return 60;
      case 'planning':
        return 20;
      default:
        return 0;
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'No deadline';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      height: '100%',
      backgroundColor: '#F8FAFC'
    }}>
      {/* Header */}
      <div style={{
        backgroundColor: '#FFFFFF',
        borderBottom: '1px solid #E2E8F0',
        padding: '24px 32px',
        boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.05)'
      }}>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '16px'
        }}>
          <div>
            <h1 style={{
              fontSize: '24px',
              fontWeight: '600',
              color: '#1E293B',
              marginBottom: '4px'
            }}>Projects</h1>
            <p style={{
              color: '#64748B',
              fontSize: '14px'
            }}>
              Track and manage all your construction projects
            </p>
          </div>
          <button
            onMouseEnter={() => setHoveredButton(true)}
            onMouseLeave={() => setHoveredButton(false)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              background: hoveredButton 
                ? 'linear-gradient(135deg, #1D4ED8 0%, #1E40AF 100%)'
                : 'linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%)',
              color: '#FFFFFF',
              border: 'none',
              padding: '10px 20px',
              borderRadius: '10px',
              fontSize: '14px',
              fontWeight: '500',
              cursor: 'pointer',
              transition: 'all 0.2s ease',
              boxShadow: hoveredButton 
                ? '0 6px 12px -2px rgba(37, 99, 235, 0.4)'
                : '0 4px 6px -1px rgba(37, 99, 235, 0.3)',
              transform: hoveredButton ? 'translateY(-1px)' : 'translateY(0)'
            }}
          >
            <Plus size={18} />
            New Project
          </button>
        </div>

        {/* Search Bar */}
        <div style={{
          position: 'relative',
          marginTop: '16px'
        }}>
          <Search size={18} style={{
            position: 'absolute',
            left: '14px',
            top: '50%',
            transform: 'translateY(-50%)',
            color: '#64748B'
          }} />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search projects..."
            style={{
              width: '100%',
              padding: '10px 14px 10px 44px',
              border: '1px solid #E2E8F0',
              borderRadius: '10px',
              fontSize: '14px',
              color: '#1E293B',
              outline: 'none',
              transition: 'all 0.2s ease',
              backgroundColor: '#FFFFFF'
            }}
            onFocus={(e) => {
              e.target.style.borderColor = '#2563EB';
              e.target.style.boxShadow = '0 0 0 3px rgba(37, 99, 235, 0.1)';
            }}
            onBlur={(e) => {
              e.target.style.borderColor = '#E2E8F0';
              e.target.style.boxShadow = 'none';
            }}
          />
        </div>
      </div>

      {/* Projects Grid */}
      <div style={{
        flex: 1,
        overflowY: 'auto',
        padding: '32px'
      }}>
        {loading ? (
          <div style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            height: '400px',
            gap: '16px'
          }}>
            <Loader2 className="animate-spin" size={40} style={{ color: '#2563EB' }} />
            <p style={{ color: '#64748B', fontSize: '14px' }}>Loading projects...</p>
          </div>
        ) : error ? (
          <div style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            height: '400px',
            gap: '16px'
          }}>
            <AlertCircle size={40} style={{ color: '#DC2626' }} />
            <p style={{ color: '#DC2626', fontSize: '14px' }}>{error}</p>
            <button
              onClick={fetchProjects}
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
              Retry
            </button>
          </div>
        ) : (
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(380px, 1fr))',
            gap: '24px',
            maxWidth: '1400px',
            margin: '0 auto'
          }}>
            {filteredProjects.map((project) => {
              const statusStyle = getStatusColor(project.Status || 'planning');
              const isHovered = hoveredCard === project['Project ID'];
              // Calculate progress based on available data (you can adjust this logic)
              const progress = calculateProgress(project);
              const progressColor = getProgressColor(progress);

              return (
                <div
                  key={project['Project ID']}
                  onMouseEnter={() => setHoveredCard(project['Project ID'])}
                  onMouseLeave={() => setHoveredCard(null)}
                  style={{
                    backgroundColor: '#FFFFFF',
                    borderRadius: '12px',
                    padding: '24px',
                    border: '1px solid #E2E8F0',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease',
                    boxShadow: isHovered 
                      ? '0 10px 20px -5px rgba(0, 0, 0, 0.1)'
                      : '0 1px 3px 0 rgba(0, 0, 0, 0.05)',
                    transform: isHovered ? 'translateY(-2px)' : 'translateY(0)'
                  }}
                >
                  <div style={{
                    display: 'flex',
                    alignItems: 'flex-start',
                    justifyContent: 'space-between',
                    marginBottom: '16px'
                  }}>
                    <div style={{
                      width: '48px',
                      height: '48px',
                      borderRadius: '10px',
                      background: 'linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      flexShrink: 0,
                      boxShadow: '0 4px 6px -1px rgba(37, 99, 235, 0.3)'
                    }}>
                      <FolderKanban size={24} style={{ color: '#FFFFFF' }} />
                    </div>
                    <span style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      padding: '6px 12px',
                      borderRadius: '8px',
                      backgroundColor: statusStyle.bg,
                      color: statusStyle.text,
                      fontSize: '12px',
                      fontWeight: '500',
                      border: `1px solid ${statusStyle.border}`,
                      textTransform: 'capitalize'
                    }}>
                      {project.Status || 'N/A'}
                    </span>
                  </div>

                  <h3 style={{
                    fontSize: '17px',
                    fontWeight: '600',
                    color: '#1E293B',
                    marginBottom: '12px'
                  }}>{project['Project Name'] || 'Unnamed Project'}</h3>

                  <div style={{
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '10px',
                    marginBottom: '16px'
                  }}>
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px',
                      fontSize: '13px',
                      color: '#64748B'
                    }}>
                      <MapPin size={16} style={{ color: '#2563EB' }} />
                      {project['Project Address'] || 'No address'}
                    </div>
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px',
                      fontSize: '13px',
                      color: '#64748B'
                    }}>
                      <Users size={16} style={{ color: '#2563EB' }} />
                      Client: {project['Owner Name (PM\'s Client)'] || project['Client ID'] || 'Unknown'}
                    </div>
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px',
                      fontSize: '13px',
                      color: '#64748B'
                    }}>
                      <Calendar size={16} style={{ color: '#2563EB' }} />
                      {project['Start Date'] ? `Started: ${formatDate(project['Start Date'])}` : 'No start date'}
                    </div>
                  </div>

                  {/* Progress Bar */}
                  <div style={{
                    paddingTop: '16px',
                    borderTop: '1px solid #F1F5F9'
                  }}>
                    <div style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      marginBottom: '8px'
                    }}>
                      <span style={{
                        fontSize: '13px',
                        fontWeight: '500',
                        color: '#64748B'
                      }}>Progress</span>
                      <span style={{
                        fontSize: '13px',
                        fontWeight: '600',
                        color: progressColor
                      }}>{progress}%</span>
                    </div>
                    <div style={{
                      width: '100%',
                      height: '8px',
                      backgroundColor: '#F1F5F9',
                      borderRadius: '4px',
                      overflow: 'hidden'
                    }}>
                      <div style={{
                        width: `${progress}%`,
                        height: '100%',
                        backgroundColor: progressColor,
                        borderRadius: '4px',
                        transition: 'width 0.3s ease'
                      }} />
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
