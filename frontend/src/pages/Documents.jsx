import { FolderOpen, Plus, Search, File, Download, Eye } from 'lucide-react';
import { useState } from 'react';

export default function Documents() {
  const [searchTerm, setSearchTerm] = useState('');
  const [hoveredDoc, setHoveredDoc] = useState(null);
  const [hoveredButton, setHoveredButton] = useState(false);

  const documents = [
    { id: 1, name: 'Building Plans - Main Floor.pdf', type: 'PDF', size: '2.4 MB', date: '2024-10-15', category: 'Plans' },
    { id: 2, name: 'Electrical Schematics.dwg', type: 'DWG', size: '5.1 MB', date: '2024-10-20', category: 'Technical' },
    { id: 3, name: 'Project Budget Report.xlsx', type: 'XLSX', size: '342 KB', date: '2024-10-25', category: 'Finance' },
    { id: 4, name: 'Site Photos - Week 3.zip', type: 'ZIP', size: '18.2 MB', date: '2024-10-28', category: 'Photos' },
    { id: 5, name: 'Permit Application Form.pdf', type: 'PDF', size: '1.1 MB', date: '2024-11-01', category: 'Legal' },
    { id: 6, name: 'Material Specifications.docx', type: 'DOCX', size: '856 KB', date: '2024-11-02', category: 'Specs' },
  ];

  const getFileColor = (type) => {
    switch (type.toLowerCase()) {
      case 'pdf': return { bg: '#FEF2F2', text: '#DC2626', border: '#FECACA' };
      case 'dwg': return { bg: '#FEF3C7', text: '#D97706', border: '#FCD34D' };
      case 'xlsx': return { bg: '#ECFDF5', text: '#059669', border: '#A7F3D0' };
      case 'zip': return { bg: '#F3E8FF', text: '#9333EA', border: '#D8B4FE' };
      case 'docx': return { bg: '#DBEAFE', text: '#2563EB', border: '#93C5FD' };
      default: return { bg: '#F3F4F6', text: '#6B7280', border: '#D1D5DB' };
    }
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
            }}>Documents</h1>
            <p style={{
              color: '#64748B',
              fontSize: '14px'
            }}>
              Access and manage all your project documents
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
            Upload Document
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
            placeholder="Search documents..."
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

      {/* Documents List */}
      <div style={{
        flex: 1,
        overflowY: 'auto',
        padding: '32px'
      }}>
        <div style={{
          maxWidth: '1200px',
          margin: '0 auto',
          backgroundColor: '#FFFFFF',
          borderRadius: '12px',
          border: '1px solid #E2E8F0',
          boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.05)',
          overflow: 'hidden'
        }}>
          {documents.map((doc, index) => {
            const fileStyle = getFileColor(doc.type);
            const isHovered = hoveredDoc === doc.id;

            return (
              <div
                key={doc.id}
                onMouseEnter={() => setHoveredDoc(doc.id)}
                onMouseLeave={() => setHoveredDoc(null)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  padding: '16px 24px',
                  borderBottom: index < documents.length - 1 ? '1px solid #F1F5F9' : 'none',
                  transition: 'background-color 0.2s ease',
                  backgroundColor: isHovered ? '#F8FAFC' : '#FFFFFF',
                  cursor: 'pointer'
                }}
              >
                {/* File Icon */}
                <div style={{
                  width: '48px',
                  height: '48px',
                  borderRadius: '10px',
                  backgroundColor: fileStyle.bg,
                  border: `1px solid ${fileStyle.border}`,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  marginRight: '16px',
                  flexShrink: 0
                }}>
                  <File size={24} style={{ color: fileStyle.text }} />
                </div>

                {/* File Info */}
                <div style={{ flex: 1, minWidth: 0 }}>
                  <h3 style={{
                    fontSize: '15px',
                    fontWeight: '600',
                    color: '#1E293B',
                    marginBottom: '4px',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap'
                  }}>{doc.name}</h3>
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px',
                    fontSize: '13px',
                    color: '#64748B'
                  }}>
                    <span style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      padding: '3px 8px',
                      borderRadius: '6px',
                      backgroundColor: fileStyle.bg,
                      color: fileStyle.text,
                      fontSize: '11px',
                      fontWeight: '600',
                      border: `1px solid ${fileStyle.border}`
                    }}>
                      {doc.type}
                    </span>
                    <span>{doc.size}</span>
                    <span>•</span>
                    <span>{doc.category}</span>
                    <span>•</span>
                    <span>{doc.date}</span>
                  </div>
                </div>

                {/* Action Buttons */}
                <div style={{
                  display: 'flex',
                  gap: '8px',
                  marginLeft: '16px',
                  opacity: isHovered ? 1 : 0,
                  transition: 'opacity 0.2s ease'
                }}>
                  <button
                    style={{
                      padding: '8px',
                      border: '1px solid #E2E8F0',
                      borderRadius: '8px',
                      backgroundColor: '#FFFFFF',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      transition: 'all 0.2s ease'
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.borderColor = '#2563EB';
                      e.currentTarget.style.backgroundColor = '#EFF6FF';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.borderColor = '#E2E8F0';
                      e.currentTarget.style.backgroundColor = '#FFFFFF';
                    }}
                    onClick={(e) => e.stopPropagation()}
                  >
                    <Eye size={16} style={{ color: '#2563EB' }} />
                  </button>
                  <button
                    style={{
                      padding: '8px',
                      border: '1px solid #E2E8F0',
                      borderRadius: '8px',
                      backgroundColor: '#FFFFFF',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      transition: 'all 0.2s ease'
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.borderColor = '#2563EB';
                      e.currentTarget.style.backgroundColor = '#EFF6FF';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.borderColor = '#E2E8F0';
                      e.currentTarget.style.backgroundColor = '#FFFFFF';
                    }}
                    onClick={(e) => e.stopPropagation()}
                  >
                    <Download size={16} style={{ color: '#2563EB' }} />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
