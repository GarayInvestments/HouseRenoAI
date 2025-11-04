import { Send, Bot, User, AlertCircle, ArrowDown, Paperclip, X, FileText, Image as ImageIcon, CheckCircle2, Loader2 } from 'lucide-react';
import { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import api from '../lib/api';

export default function AIAssistant() {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Hello! I\'m your AI assistant. How can I help you with permits or projects today?' },
  ]);
  const [input, setInput] = useState('');
  const [isHovered, setIsHovered] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState(null);
  const [showScrollButton, setShowScrollButton] = useState(false);
  const [uploadedFile, setUploadedFile] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(null);
  const [showUploadOptions, setShowUploadOptions] = useState(false);
  const [hoveredClientId, setHoveredClientId] = useState(null);
  
  const messagesEndRef = useRef(null);
  const messagesContainerRef = useRef(null);
  const fileInputRef = useRef(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Check backend connection on mount
  useEffect(() => {
    checkConnection();
  }, []);

  // Detect if user has scrolled up
  useEffect(() => {
    const container = messagesContainerRef.current;
    if (!container) return;

    const handleScroll = () => {
      const { scrollTop, scrollHeight, clientHeight } = container;
      const isNearBottom = scrollHeight - scrollTop - clientHeight < 100;
      setShowScrollButton(!isNearBottom);
    };

    container.addEventListener('scroll', handleScroll);
    return () => container.removeEventListener('scroll', handleScroll);
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const checkConnection = async () => {
    try {
      await api.healthCheck();
      setIsConnected(true);
      setError(null);
    } catch {
      setIsConnected(false);
      setError('Backend connection failed. Using demo mode.');
    }
  };

  const handleFileSelect = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const allowedTypes = ['application/pdf', 'image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
      setError('Please upload a PDF or image file (JPG, PNG, WEBP)');
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      setError('File size must be less than 10MB');
      return;
    }

    setUploadedFile(file);
    setShowUploadOptions(true);
    setError(null);
  };

  const handleRemoveFile = () => {
    setUploadedFile(null);
    setShowUploadOptions(false);
    setUploadProgress(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleEditField = (messageIndex, field, value) => {
    setMessages(prev => prev.map((msg, idx) => {
      if (idx === messageIndex && msg.extractedData) {
        return {
          ...msg,
          extractedData: {
            ...msg.extractedData,
            [field]: value
          }
        };
      }
      return msg;
    }));
  };

  const handleConfirmExtractedData = async (messageIndex) => {
    const message = messages[messageIndex];
    if (!message.extractedData) return;

    try {
      setIsLoading(true);
      setMessages(prev => [
        ...prev,
        { role: 'user', content: 'Create the record with this information' },
        { role: 'assistant', content: `Creating ${message.documentType}...` }
      ]);

      await api.createFromExtract(message.documentType, message.extractedData);
      
      setMessages(prev => [...prev.slice(0, -1), {
        role: 'assistant',
        content: `✅ ${message.documentType === 'project' ? 'Project' : 'Permit'} created successfully! You can now view it in the ${message.documentType}s page.`
      }]);
    } catch (err) {
      setError(err.message || `Failed to create ${message.documentType}`);
      setMessages(prev => [...prev.slice(0, -1), {
        role: 'assistant',
        content: `❌ Sorry, there was an error creating the ${message.documentType}. Please try again.`
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleUploadDocument = async (documentType) => {
    if (!uploadedFile) return;

    try {
      setUploadProgress({ status: 'uploading', message: 'Uploading document...' });
      
      const formData = new FormData();
      formData.append('file', uploadedFile);
      formData.append('document_type', documentType);

      const response = await api.uploadDocument(formData);
      
      setUploadProgress({ status: 'extracting', message: 'AI is extracting data...' });
      
      // Auto-lookup Client ID using applicant_info (not shown to user)
      let clientLookupData = null;
      const extractedData = response.extracted_data;
      
      if (documentType === 'project' && response.applicant_info) {
        const applicantName = response.applicant_info['Applicant Name'];
        const applicantEmail = response.applicant_info['Applicant Email'];
        
        if (applicantName || applicantEmail) {
          try {
            setUploadProgress({ status: 'extracting', message: 'Looking up client...' });
            const lookupResult = await api.lookupClient(applicantName, applicantEmail);
            
            if (lookupResult && lookupResult.client_id && lookupResult.confidence > 30) {
              // Auto-fill Client ID
              extractedData['Client ID'] = lookupResult.client_id;
              clientLookupData = lookupResult;
            }
          } catch (lookupErr) {
            console.warn('Client lookup failed:', lookupErr);
            // Continue without client lookup
          }
        }
      }
      
      // Add message showing what was extracted
      setMessages(prev => [
        ...prev,
        { role: 'user', content: `📎 Uploaded: ${uploadedFile.name} (${documentType})` },
        { 
          role: 'assistant', 
          content: `I've analyzed the document and extracted the following information. You can edit any fields before creating the ${documentType}.`,
          extractedData: extractedData,
          clientLookup: clientLookupData,
          documentType,
          isEditable: true
        }
      ]);

      setUploadProgress({ status: 'complete', message: 'Done!' });
      setTimeout(() => {
        handleRemoveFile();
      }, 1500);

    } catch (err) {
      setError(err.message || 'Failed to process document');
      setUploadProgress(null);
    }
  };

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;
    
    const userMessage = input.trim();
    
    setMessages([...messages, { role: 'user', content: userMessage }]);
    setInput('');
    setIsLoading(true);
    setError(null);
    
    try {
      if (isConnected) {
        // Use real backend
        const response = await api.sendChatMessage(userMessage);
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: response.response || 'I received your message but couldn\'t generate a response.'
        }]);
      } else {
        // Fallback to demo mode
        setTimeout(() => {
          setMessages(prev => [...prev, {
            role: 'assistant',
            content: 'I\'m in demo mode. The backend is not connected. In production, I would process your request and provide helpful information about permits and projects.'
          }]);
          setIsLoading(false);
        }, 1000);
        return;
      }
    } catch {
      setError('Failed to send message. Please try again.');
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, I encountered an error processing your message. Please try again.'
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      height: '100%',
      backgroundColor: '#F8FAFC'
    }}>
      {/* Page Header */}
      <div style={{
        backgroundColor: '#FFFFFF',
        borderBottom: '1px solid #E2E8F0',
        padding: '24px 32px',
        boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.05)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div>
            <h1 style={{
              fontSize: '24px',
              fontWeight: '600',
              color: '#1E293B',
              marginBottom: '4px'
            }}>AI Assistant</h1>
            <p style={{
              color: '#64748B',
              fontSize: '14px'
            }}>
              Ask me anything about permits, compliance, or project management.
            </p>
          </div>
          
          {/* Connection Status */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '8px 12px',
            borderRadius: '8px',
            backgroundColor: isConnected ? '#F0FDF4' : '#FEF2F2',
            border: `1px solid ${isConnected ? '#BBF7D0' : '#FECACA'}`
          }}>
            <div style={{
              width: '8px',
              height: '8px',
              borderRadius: '50%',
              backgroundColor: isConnected ? '#22C55E' : '#EF4444'
            }} />
            <span style={{
              fontSize: '12px',
              fontWeight: '500',
              color: isConnected ? '#15803D' : '#DC2626'
            }}>
              {isConnected ? 'Connected' : 'Demo Mode'}
            </span>
          </div>
        </div>
        
        {/* Error Message */}
        {error && (
          <div style={{
            marginTop: '12px',
            padding: '12px',
            backgroundColor: '#FEF2F2',
            border: '1px solid #FECACA',
            borderRadius: '8px',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            <AlertCircle size={16} style={{ color: '#DC2626', flexShrink: 0 }} />
            <span style={{ fontSize: '13px', color: '#DC2626' }}>{error}</span>
          </div>
        )}
      </div>

      {/* Chat Messages */}
      <div 
        ref={messagesContainerRef}
        style={{
          flex: 1,
          overflowY: 'auto',
          padding: '24px 32px',
          position: 'relative'
        }}
      >
        <div style={{
          maxWidth: '900px',
          margin: '0 auto',
          display: 'flex',
          flexDirection: 'column',
          gap: '20px'
        }}>
          {messages.map((message, index) => (
            <div
              key={index}
              style={{
                display: 'flex',
                gap: '12px',
                justifyContent: message.role === 'user' ? 'flex-end' : 'flex-start'
              }}
            >
              {message.role === 'assistant' && (
                <div style={{
                  width: '40px',
                  height: '40px',
                  borderRadius: '10px',
                  background: 'linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexShrink: 0,
                  boxShadow: '0 4px 6px -1px rgba(37, 99, 235, 0.3)'
                }}>
                  <Bot size={20} style={{ color: '#FFFFFF' }} />
                </div>
              )}
              <div
                style={{
                  maxWidth: '600px',
                  padding: '14px 18px',
                  borderRadius: '12px',
                  backgroundColor: message.role === 'user' ? '#2563EB' : '#FFFFFF',
                  color: message.role === 'user' ? '#FFFFFF' : '#1E293B',
                  border: message.role === 'assistant' ? '1px solid #E2E8F0' : 'none',
                  boxShadow: message.role === 'user' 
                    ? '0 4px 6px -1px rgba(37, 99, 235, 0.3)' 
                    : '0 1px 3px 0 rgba(0, 0, 0, 0.05)'
                }}
              >
                {message.role === 'assistant' ? (
                  <>
                    <div style={{
                      fontSize: '14px',
                      lineHeight: '1.6',
                      marginBottom: message.extractedData ? '16px' : 0
                    }} className="markdown-content">
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>
                        {message.content}
                      </ReactMarkdown>
                    </div>
                    
                    {/* Editable Extracted Data Fields */}
                    {message.extractedData && message.isEditable && (
                      <div style={{
                        borderTop: '1px solid #F1F5F9',
                        paddingTop: '16px'
                      }}>
                        <div style={{
                          display: 'flex',
                          flexDirection: 'column',
                          gap: '12px',
                          marginBottom: '16px'
                        }}>
                          {Object.entries(message.extractedData).map(([key, value]) => {
                            const isClientIdField = key === 'Client ID';
                            const hasLookupData = message.clientLookup && message.clientLookup.confidence > 30;
                            const tooltipId = `${index}-clientid`;
                            
                            return (
                              <div key={key} style={{ position: 'relative' }}>
                                <label style={{
                                  display: 'flex',
                                  alignItems: 'center',
                                  gap: '6px',
                                  fontSize: '12px',
                                  fontWeight: '500',
                                  color: '#64748B',
                                  marginBottom: '4px'
                                }}>
                                  {key}
                                  {/* Show badge for auto-matched Client ID */}
                                  {isClientIdField && hasLookupData && (
                                    <span
                                      style={{
                                        display: 'inline-flex',
                                        alignItems: 'center',
                                        gap: '4px',
                                        fontSize: '11px',
                                        fontWeight: '400',
                                        color: '#059669',
                                        backgroundColor: '#D1FAE5',
                                        padding: '2px 6px',
                                        borderRadius: '4px',
                                        cursor: 'help'
                                      }}
                                    >
                                      ✓ Auto-matched ({message.clientLookup.confidence}%)
                                    </span>
                                  )}
                                </label>
                                <div style={{ position: 'relative' }}>
                                  <div
                                    onMouseEnter={() => setHoveredClientId(tooltipId)}
                                    onMouseLeave={() => setHoveredClientId(null)}
                                  >
                                    <input
                                      type="text"
                                      value={value || ''}
                                      onChange={(e) => handleEditField(index, key, e.target.value)}
                                      style={{
                                        width: '100%',
                                        padding: '8px 10px',
                                        border: '1px solid #E2E8F0',
                                        borderRadius: '6px',
                                        fontSize: '13px',
                                        color: '#1E293B',
                                        backgroundColor: '#FFFFFF'
                                      }}
                                      onFocus={(e) => {
                                        e.target.style.borderColor = '#2563EB';
                                        e.target.style.boxShadow = '0 0 0 2px rgba(37, 99, 235, 0.1)';
                                      }}
                                      onBlur={(e) => {
                                        e.target.style.borderColor = '#E2E8F0';
                                        e.target.style.boxShadow = 'none';
                                      }}
                                    />
                                  </div>
                                  
                                  {/* Show client full name below Client ID field */}
                                  {isClientIdField && hasLookupData && (
                                    <div style={{
                                      marginTop: '6px',
                                      padding: '8px 10px',
                                      backgroundColor: '#F0FDF4',
                                      border: '1px solid #BBF7D0',
                                      borderRadius: '6px',
                                      fontSize: '12px',
                                      color: '#166534'
                                    }}>
                                      <div style={{ fontWeight: '600', marginBottom: '2px' }}>
                                        {message.clientLookup.full_name || 'Unknown Client'}
                                      </div>
                                      {message.clientLookup.company && (
                                        <div style={{ fontSize: '11px', color: '#15803D' }}>
                                          {message.clientLookup.company}
                                        </div>
                                      )}
                                      {message.clientLookup.email && (
                                        <div style={{ fontSize: '11px', color: '#15803D', marginTop: '2px' }}>
                                          {message.clientLookup.email}
                                        </div>
                                      )}
                                    </div>
                                  )}
                                  
                                  {/* Enhanced tooltip on hover for Client ID */}
                                  {isClientIdField && hasLookupData && hoveredClientId === tooltipId && (
                                    <div
                                      style={{
                                        position: 'absolute',
                                        bottom: '100%',
                                        left: '0',
                                        marginBottom: '8px',
                                        padding: '10px 12px',
                                        backgroundColor: '#1E293B',
                                        color: '#FFFFFF',
                                        borderRadius: '6px',
                                        fontSize: '12px',
                                        whiteSpace: 'nowrap',
                                        boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.3)',
                                        zIndex: 10
                                      }}
                                    >
                                      <div style={{ fontWeight: '600', marginBottom: '4px' }}>
                                        {message.clientLookup.full_name || 'Unknown Client'}
                                      </div>
                                      {message.clientLookup.company && (
                                        <div style={{ fontSize: '11px', color: '#94A3B8', marginBottom: '2px' }}>
                                          {message.clientLookup.company}
                                        </div>
                                      )}
                                      {message.clientLookup.email && (
                                        <div style={{ fontSize: '11px', color: '#94A3B8', marginBottom: '2px' }}>
                                          {message.clientLookup.email}
                                        </div>
                                      )}
                                      {message.clientLookup.phone && (
                                        <div style={{ fontSize: '11px', color: '#94A3B8', marginBottom: '2px' }}>
                                          {message.clientLookup.phone}
                                        </div>
                                      )}
                                      <div style={{ fontSize: '11px', color: '#10B981', marginTop: '4px', paddingTop: '4px', borderTop: '1px solid #374151' }}>
                                        Match Confidence: {message.clientLookup.confidence}%
                                      </div>
                                    </div>
                                  )}
                                </div>
                              </div>
                            );
                          })}
                        </div>
                        <button
                          onClick={() => handleConfirmExtractedData(index)}
                          disabled={isLoading}
                          style={{
                            width: '100%',
                            padding: '10px',
                            backgroundColor: '#2563EB',
                            color: '#FFFFFF',
                            border: 'none',
                            borderRadius: '8px',
                            fontSize: '14px',
                            fontWeight: '500',
                            cursor: isLoading ? 'not-allowed' : 'pointer',
                            opacity: isLoading ? 0.6 : 1,
                            transition: 'all 0.2s ease'
                          }}
                          onMouseEnter={(e) => {
                            if (!isLoading) {
                              e.currentTarget.style.backgroundColor = '#1D4ED8';
                            }
                          }}
                          onMouseLeave={(e) => {
                            e.currentTarget.style.backgroundColor = '#2563EB';
                          }}
                        >
                          {isLoading ? 'Creating...' : `Create ${message.documentType === 'project' ? 'Project' : 'Permit'}`}
                        </button>
                      </div>
                    )}
                  </>
                ) : (
                  <p style={{
                    fontSize: '14px',
                    lineHeight: '1.6',
                    margin: 0
                  }}>
                    {message.content}
                  </p>
                )}
              </div>
              {message.role === 'user' && (
                <div style={{
                  width: '40px',
                  height: '40px',
                  borderRadius: '10px',
                  backgroundColor: '#E2E8F0',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexShrink: 0
                }}>
                  <User size={20} style={{ color: '#64748B' }} />
                </div>
              )}
            </div>
          ))}
          
          {/* Loading indicator */}
          {isLoading && (
            <div style={{
              display: 'flex',
              gap: '12px',
              justifyContent: 'flex-start'
            }}>
              <div style={{
                width: '40px',
                height: '40px',
                borderRadius: '10px',
                background: 'linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexShrink: 0,
                boxShadow: '0 4px 6px -1px rgba(37, 99, 235, 0.3)'
              }}>
                <Bot size={20} style={{ color: '#FFFFFF' }} />
              </div>
              <div style={{
                maxWidth: '600px',
                padding: '14px 18px',
                borderRadius: '12px',
                backgroundColor: '#FFFFFF',
                border: '1px solid #E2E8F0',
                boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.05)',
                display: 'flex',
                gap: '4px'
              }}>
                <div style={{
                  width: '8px',
                  height: '8px',
                  borderRadius: '50%',
                  backgroundColor: '#94A3B8',
                  animation: 'pulse 1.4s ease-in-out infinite'
                }} />
                <div style={{
                  width: '8px',
                  height: '8px',
                  borderRadius: '50%',
                  backgroundColor: '#94A3B8',
                  animation: 'pulse 1.4s ease-in-out 0.2s infinite'
                }} />
                <div style={{
                  width: '8px',
                  height: '8px',
                  borderRadius: '50%',
                  backgroundColor: '#94A3B8',
                  animation: 'pulse 1.4s ease-in-out 0.4s infinite'
                }} />
              </div>
            </div>
          )}
          
          {/* Invisible element to scroll to */}
          <div ref={messagesEndRef} />
        </div>

        {/* Scroll to Bottom Button */}
        {showScrollButton && (
          <button
            onClick={scrollToBottom}
            style={{
              position: 'absolute',
              bottom: '24px',
              left: '50%',
              transform: 'translateX(-50%)',
              backgroundColor: '#FFFFFF',
              border: '1px solid #E2E8F0',
              borderRadius: '50%',
              width: '44px',
              height: '44px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              cursor: 'pointer',
              boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
              transition: 'all 0.2s ease',
              zIndex: 10
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = '#F8FAFC';
              e.currentTarget.style.transform = 'translateX(-50%) scale(1.05)';
              e.currentTarget.style.boxShadow = '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = '#FFFFFF';
              e.currentTarget.style.transform = 'translateX(-50%) scale(1)';
              e.currentTarget.style.boxShadow = '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)';
            }}
          >
            <ArrowDown size={20} style={{ color: '#64748B' }} />
          </button>
        )}
      </div>

      {/* Input Area */}
      <div style={{
        borderTop: '1px solid #E2E8F0',
        backgroundColor: '#FFFFFF',
        padding: '20px 32px',
        boxShadow: '0 -1px 3px 0 rgba(0, 0, 0, 0.05)'
      }}>
        <div style={{
          maxWidth: '900px',
          margin: '0 auto'
        }}>
          {/* File Upload Preview */}
          {uploadedFile && (
            <div style={{
              marginBottom: '12px',
              padding: '12px',
              backgroundColor: '#F8FAFC',
              borderRadius: '8px',
              border: '1px solid #E2E8F0'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
                <div style={{
                  width: '40px',
                  height: '40px',
                  borderRadius: '8px',
                  backgroundColor: uploadedFile.type === 'application/pdf' ? '#FEF3C7' : '#DBEAFE',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexShrink: 0
                }}>
                  {uploadedFile.type === 'application/pdf' ? (
                    <FileText size={20} style={{ color: '#D97706' }} />
                  ) : (
                    <ImageIcon size={20} style={{ color: '#2563EB' }} />
                  )}
                </div>
                <div style={{ flex: 1 }}>
                  <p style={{ fontSize: '14px', fontWeight: '500', color: '#1E293B', marginBottom: '2px' }}>
                    {uploadedFile.name}
                  </p>
                  <p style={{ fontSize: '12px', color: '#64748B' }}>
                    {(uploadedFile.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>
                <button
                  onClick={handleRemoveFile}
                  style={{
                    padding: '6px',
                    backgroundColor: 'transparent',
                    border: 'none',
                    cursor: 'pointer',
                    color: '#64748B',
                    borderRadius: '4px'
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#F1F5F9'}
                  onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
                >
                  <X size={16} />
                </button>
              </div>

              {/* Upload Progress */}
              {uploadProgress ? (
                <div style={{
                  padding: '12px',
                  backgroundColor: '#FFFFFF',
                  borderRadius: '6px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px'
                }}>
                  {uploadProgress.status === 'complete' ? (
                    <CheckCircle2 size={16} style={{ color: '#059669' }} />
                  ) : (
                    <Loader2 size={16} style={{ color: '#2563EB' }} className="animate-spin" />
                  )}
                  <span style={{ fontSize: '13px', color: '#475569' }}>{uploadProgress.message}</span>
                </div>
              ) : showUploadOptions ? (
                <div>
                  <p style={{ fontSize: '13px', color: '#64748B', marginBottom: '8px' }}>
                    What type of document is this?
                  </p>
                  <div style={{ display: 'flex', gap: '8px' }}>
                    <button
                      onClick={() => handleUploadDocument('project')}
                      style={{
                        flex: 1,
                        padding: '8px 16px',
                        backgroundColor: '#2563EB',
                        color: '#FFFFFF',
                        border: 'none',
                        borderRadius: '6px',
                        fontSize: '13px',
                        fontWeight: '500',
                        cursor: 'pointer'
                      }}
                    >
                      📋 Project
                    </button>
                    <button
                      onClick={() => handleUploadDocument('permit')}
                      style={{
                        flex: 1,
                        padding: '8px 16px',
                        backgroundColor: '#2563EB',
                        color: '#FFFFFF',
                        border: 'none',
                        borderRadius: '6px',
                        fontSize: '13px',
                        fontWeight: '500',
                        cursor: 'pointer'
                      }}
                    >
                      📄 Permit
                    </button>
                  </div>
                </div>
              ) : null}
            </div>
          )}

          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '12px'
          }}>
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.jpg,.jpeg,.png,.webp"
              onChange={handleFileSelect}
              style={{ display: 'none' }}
            />
            <button
              onClick={() => fileInputRef.current?.click()}
              disabled={isLoading || !!uploadedFile}
              style={{
                padding: '12px',
                backgroundColor: '#FFFFFF',
                border: '1px solid #E2E8F0',
                borderRadius: '10px',
                cursor: (isLoading || uploadedFile) ? 'not-allowed' : 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                transition: 'all 0.2s ease',
                opacity: (isLoading || uploadedFile) ? 0.5 : 1
              }}
              onMouseEnter={(e) => {
                if (!isLoading && !uploadedFile) {
                  e.currentTarget.style.backgroundColor = '#F8FAFC';
                  e.currentTarget.style.borderColor = '#2563EB';
                }
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = '#FFFFFF';
                e.currentTarget.style.borderColor = '#E2E8F0';
              }}
            >
              <Paperclip size={18} style={{ color: '#64748B' }} />
            </button>
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Type your message or upload a document..."
              style={{
                flex: 1,
                border: '1px solid #E2E8F0',
                borderRadius: '10px',
                padding: '12px 16px',
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
            <button
              onClick={handleSend}
              disabled={!input.trim() || isLoading}
              onMouseEnter={() => setIsHovered(true)}
              onMouseLeave={() => setIsHovered(false)}
              style={{
                background: (!input.trim() || isLoading)
                  ? '#CBD5E1' 
                  : isHovered 
                    ? 'linear-gradient(135deg, #1D4ED8 0%, #1E40AF 100%)'
                    : 'linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%)',
                color: '#FFFFFF',
                border: 'none',
                padding: '12px 12px',
                borderRadius: '10px',
                cursor: (!input.trim() || isLoading) ? 'not-allowed' : 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                transition: 'all 0.2s ease',
                boxShadow: (!input.trim() || isLoading)
                  ? 'none' 
                  : isHovered 
                    ? '0 6px 12px -2px rgba(37, 99, 235, 0.4)'
                    : '0 4px 6px -1px rgba(37, 99, 235, 0.3)',
                transform: isHovered && input.trim() && !isLoading ? 'translateY(-1px)' : 'translateY(0)'
              }}
            >
              <Send size={18} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
