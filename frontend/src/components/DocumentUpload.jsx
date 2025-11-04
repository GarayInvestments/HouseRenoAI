import { useState } from 'react';
import { Upload, FileText, Image as ImageIcon, X, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';
import api from '../lib/api';

export default function DocumentUpload({ documentType, clientId, onSuccess, onCancel }) {
  const [dragActive, setDragActive] = useState(false);
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [extractedData, setExtractedData] = useState(null);
  const [error, setError] = useState(null);
  const [step, setStep] = useState('upload'); // 'upload', 'review', 'success'

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelect(e.dataTransfer.files[0]);
    }
  };

  const handleFileSelect = (selectedFile) => {
    const allowedTypes = ['application/pdf', 'image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
    
    if (!allowedTypes.includes(selectedFile.type)) {
      setError('Please upload a PDF or image file (JPG, PNG, WEBP)');
      return;
    }
    
    if (selectedFile.size > 10 * 1024 * 1024) { // 10MB limit
      setError('File size must be less than 10MB');
      return;
    }
    
    setFile(selectedFile);
    setError(null);
  };

  const handleFileInput = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFileSelect(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    
    try {
      setUploading(true);
      setError(null);
      
      const formData = new FormData();
      formData.append('file', file);
      formData.append('document_type', documentType);
      if (clientId) {
        formData.append('client_id', clientId);
      }
      
      const response = await api.uploadDocument(formData);
      
      setExtractedData(response.extracted_data);
      setStep('review');
    } catch (err) {
      setError(err.message || 'Failed to process document');
    } finally {
      setUploading(false);
    }
  };

  const handleConfirm = async () => {
    try {
      setUploading(true);
      setError(null);
      
      await api.createFromExtract(documentType, extractedData);
      
      setStep('success');
      setTimeout(() => {
        if (onSuccess) onSuccess();
      }, 2000);
    } catch (err) {
      setError(err.message || `Failed to create ${documentType}`);
      setUploading(false);
    }
  };

  const handleEditField = (field, value) => {
    setExtractedData({
      ...extractedData,
      [field]: value
    });
  };

  const handleRemoveFile = () => {
    setFile(null);
    setError(null);
  };

  if (step === 'success') {
    return (
      <div style={{
        textAlign: 'center',
        padding: '48px',
        backgroundColor: '#FFFFFF',
        borderRadius: '12px',
        border: '1px solid #E2E8F0'
      }}>
        <div style={{
          width: '64px',
          height: '64px',
          borderRadius: '50%',
          backgroundColor: '#ECFDF5',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          margin: '0 auto 16px'
        }}>
          <CheckCircle size={32} style={{ color: '#059669' }} />
        </div>
        <h3 style={{
          fontSize: '20px',
          fontWeight: '600',
          color: '#1E293B',
          marginBottom: '8px'
        }}>
          {documentType === 'project' ? 'Project' : 'Permit'} Created Successfully!
        </h3>
        <p style={{ color: '#64748B', fontSize: '14px' }}>
          Redirecting you back...
        </p>
      </div>
    );
  }

  if (step === 'review') {
    return (
      <div style={{
        backgroundColor: '#FFFFFF',
        borderRadius: '12px',
        border: '1px solid #E2E8F0',
        padding: '24px'
      }}>
        <h3 style={{
          fontSize: '18px',
          fontWeight: '600',
          color: '#1E293B',
          marginBottom: '16px'
        }}>
          Review Extracted Data
        </h3>
        <p style={{
          fontSize: '14px',
          color: '#64748B',
          marginBottom: '24px'
        }}>
          Please review and edit the information extracted from your document
        </p>

        <div style={{
          display: 'flex',
          flexDirection: 'column',
          gap: '16px',
          marginBottom: '24px'
        }}>
          {Object.entries(extractedData).map(([key, value]) => (
            <div key={key}>
              <label style={{
                display: 'block',
                fontSize: '13px',
                fontWeight: '500',
                color: '#475569',
                marginBottom: '6px'
              }}>
                {key}
              </label>
              <input
                type="text"
                value={value || ''}
                onChange={(e) => handleEditField(key, e.target.value)}
                style={{
                  width: '100%',
                  padding: '10px 12px',
                  border: '1px solid #E2E8F0',
                  borderRadius: '8px',
                  fontSize: '14px',
                  color: '#1E293B'
                }}
              />
            </div>
          ))}
        </div>

        {error && (
          <div style={{
            padding: '12px',
            backgroundColor: '#FEF2F2',
            border: '1px solid #FECACA',
            borderRadius: '8px',
            marginBottom: '16px',
            display: 'flex',
            gap: '8px',
            alignItems: 'center'
          }}>
            <AlertCircle size={16} style={{ color: '#DC2626' }} />
            <span style={{ color: '#DC2626', fontSize: '14px' }}>{error}</span>
          </div>
        )}

        <div style={{ display: 'flex', gap: '12px' }}>
          <button
            onClick={() => setStep('upload')}
            disabled={uploading}
            style={{
              flex: 1,
              padding: '10px 20px',
              backgroundColor: '#FFFFFF',
              border: '1px solid #E2E8F0',
              borderRadius: '8px',
              fontSize: '14px',
              fontWeight: '500',
              color: '#64748B',
              cursor: 'pointer'
            }}
          >
            Back
          </button>
          <button
            onClick={handleConfirm}
            disabled={uploading}
            style={{
              flex: 1,
              padding: '10px 20px',
              backgroundColor: '#2563EB',
              border: 'none',
              borderRadius: '8px',
              fontSize: '14px',
              fontWeight: '500',
              color: '#FFFFFF',
              cursor: uploading ? 'not-allowed' : 'pointer',
              opacity: uploading ? 0.6 : 1,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px'
            }}
          >
            {uploading ? (
              <>
                <Loader2 size={16} className="animate-spin" />
                Creating...
              </>
            ) : (
              `Create ${documentType === 'project' ? 'Project' : 'Permit'}`
            )}
          </button>
        </div>
      </div>
    );
  }

  return (
    <div style={{
      backgroundColor: '#FFFFFF',
      borderRadius: '12px',
      border: '1px solid #E2E8F0',
      padding: '24px'
    }}>
      <h3 style={{
        fontSize: '18px',
        fontWeight: '600',
        color: '#1E293B',
        marginBottom: '8px'
      }}>
        Upload Document
      </h3>
      <p style={{
        fontSize: '14px',
        color: '#64748B',
        marginBottom: '24px'
      }}>
        Upload a PDF or image of your {documentType === 'project' ? 'project' : 'permit'} document. 
        AI will automatically extract the information.
      </p>

      {!file ? (
        <div
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          style={{
            border: `2px dashed ${dragActive ? '#2563EB' : '#E2E8F0'}`,
            borderRadius: '12px',
            padding: '48px 24px',
            textAlign: 'center',
            backgroundColor: dragActive ? '#F0F9FF' : '#F8FAFC',
            cursor: 'pointer',
            transition: 'all 0.2s ease'
          }}
          onClick={() => document.getElementById('file-input').click()}
        >
          <div style={{
            width: '64px',
            height: '64px',
            borderRadius: '50%',
            backgroundColor: '#DBEAFE',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 16px'
          }}>
            <Upload size={28} style={{ color: '#2563EB' }} />
          </div>
          <p style={{
            fontSize: '16px',
            fontWeight: '500',
            color: '#1E293B',
            marginBottom: '4px'
          }}>
            Drop your file here, or <span style={{ color: '#2563EB' }}>browse</span>
          </p>
          <p style={{
            fontSize: '13px',
            color: '#64748B'
          }}>
            Supports PDF, JPG, PNG, WEBP (max 10MB)
          </p>
          <input
            id="file-input"
            type="file"
            accept=".pdf,.jpg,.jpeg,.png,.webp"
            onChange={handleFileInput}
            style={{ display: 'none' }}
          />
        </div>
      ) : (
        <div>
          <div style={{
            border: '1px solid #E2E8F0',
            borderRadius: '12px',
            padding: '16px',
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            marginBottom: '16px'
          }}>
            <div style={{
              width: '48px',
              height: '48px',
              borderRadius: '8px',
              backgroundColor: file.type === 'application/pdf' ? '#FEF3C7' : '#DBEAFE',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              flexShrink: 0
            }}>
              {file.type === 'application/pdf' ? (
                <FileText size={24} style={{ color: '#D97706' }} />
              ) : (
                <ImageIcon size={24} style={{ color: '#2563EB' }} />
              )}
            </div>
            <div style={{ flex: 1 }}>
              <p style={{
                fontSize: '14px',
                fontWeight: '500',
                color: '#1E293B',
                marginBottom: '2px'
              }}>
                {file.name}
              </p>
              <p style={{
                fontSize: '12px',
                color: '#64748B'
              }}>
                {(file.size / 1024 / 1024).toFixed(2)} MB
              </p>
            </div>
            <button
              onClick={handleRemoveFile}
              style={{
                padding: '8px',
                backgroundColor: 'transparent',
                border: 'none',
                cursor: 'pointer',
                color: '#64748B',
                transition: 'color 0.2s ease'
              }}
              onMouseEnter={(e) => e.target.style.color = '#DC2626'}
              onMouseLeave={(e) => e.target.style.color = '#64748B'}
            >
              <X size={20} />
            </button>
          </div>

          {error && (
            <div style={{
              padding: '12px',
              backgroundColor: '#FEF2F2',
              border: '1px solid #FECACA',
              borderRadius: '8px',
              marginBottom: '16px',
              display: 'flex',
              gap: '8px',
              alignItems: 'center'
            }}>
              <AlertCircle size={16} style={{ color: '#DC2626' }} />
              <span style={{ color: '#DC2626', fontSize: '14px' }}>{error}</span>
            </div>
          )}

          <div style={{ display: 'flex', gap: '12px' }}>
            <button
              onClick={onCancel}
              disabled={uploading}
              style={{
                flex: 1,
                padding: '10px 20px',
                backgroundColor: '#FFFFFF',
                border: '1px solid #E2E8F0',
                borderRadius: '8px',
                fontSize: '14px',
                fontWeight: '500',
                color: '#64748B',
                cursor: 'pointer'
              }}
            >
              Cancel
            </button>
            <button
              onClick={handleUpload}
              disabled={uploading}
              style={{
                flex: 1,
                padding: '10px 20px',
                backgroundColor: '#2563EB',
                border: 'none',
                borderRadius: '8px',
                fontSize: '14px',
                fontWeight: '500',
                color: '#FFFFFF',
                cursor: uploading ? 'not-allowed' : 'pointer',
                opacity: uploading ? 0.6 : 1,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px'
              }}
            >
              {uploading ? (
                <>
                  <Loader2 size={16} className="animate-spin" />
                  Processing...
                </>
              ) : (
                'Process Document'
              )}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
