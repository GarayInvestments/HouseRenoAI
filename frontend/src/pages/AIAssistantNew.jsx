import { Send, Bot, User, AlertCircle, ArrowDown, Paperclip, X, FileText, Image as ImageIcon, CheckCircle2, Loader2, MessageSquarePlus, Trash2, Edit2, Check } from 'lucide-react';
import { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import api from '../lib/api';

export default function AIAssistant() {
  // Session state
  const [currentSessionId, setCurrentSessionId] = useState(null);
  const [sessions, setSessions] = useState([]);
  const [sessionMetadata, setSessionMetadata] = useState({});
  
  // Message state
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isHovered, setIsHovered] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState(null);
  const [showScrollButton, setShowScrollButton] = useState(false);
  
  // File upload state
  const [uploadedFile, setUploadedFile] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(null);
  const [showUploadOptions, setShowUploadOptions] = useState(false);
  const [hoveredClientId, setHoveredClientId] = useState(null);
  
  // UI state
  const [showSidebar, setShowSidebar] = useState(true);
  const [editingSessionId, setEditingSessionId] = useState(null);
  const [editingTitle, setEditingTitle] = useState('');
  
  const messagesEndRef = useRef(null);
  const messagesContainerRef = useRef(null);
  const fileInputRef = useRef(null);

  // Initialize: Load or create session
  useEffect(() => {
    initializeSession();
    checkConnection();
  }, []);

  // Auto-scroll when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Scroll detection
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

  // Save current session messages to localStorage whenever they change
  useEffect(() => {
    if (currentSessionId && messages.length > 0) {
      localStorage.setItem(`session_${currentSessionId}_messages`, JSON.stringify(messages));
    }
  }, [messages, currentSessionId]);

  const initializeSession = async () => {
    try {
      // Try to load last session from localStorage
      const lastSessionId = localStorage.getItem('last_session_id');
      
      if (lastSessionId) {
        // Load existing session
        await loadSession(lastSessionId);
      } else {
        // Create new session
        await createNewSession();
      }
      
      // Load all sessions for sidebar
      await loadSessions();
    } catch (err) {
      console.error('Failed to initialize session:', err);
      await createNewSession();
    }
  };

  const createNewSession = async () => {
    try {
      const response = await api.createSession('New Chat');
      const sessionId = response.session_id;
      
      setCurrentSessionId(sessionId);
      setMessages([
        { role: 'assistant', content: 'Hello! I\'m your AI assistant. How can I help you with permits or projects today?' }
      ]);
      setSessionMetadata(response.metadata || {});
      
      localStorage.setItem('last_session_id', sessionId);
      localStorage.setItem(`session_${sessionId}_messages`, JSON.stringify([
        { role: 'assistant', content: 'Hello! I\'m your AI assistant. How can I help you with permits or projects today?' }
      ]));
      
      await loadSessions();
    } catch (err) {
      console.error('Failed to create session:', err);
      setError('Failed to create new chat session');
    }
  };

  const loadSession = async (sessionId) => {
    try {
      // Load messages from localStorage first (instant)
      const storedMessages = localStorage.getItem(`session_${sessionId}_messages`);
      if (storedMessages) {
        setMessages(JSON.parse(storedMessages));
      } else {
        // Fallback to default message
        setMessages([
          { role: 'assistant', content: 'Hello! I\'m your AI assistant. How can I help you with permits or projects today?' }
        ]);
      }
      
      setCurrentSessionId(sessionId);
      localStorage.setItem('last_session_id', sessionId);
      
      // Load session metadata from backend
      try {
        const response = await api.getSession(sessionId);
        setSessionMetadata(response.metadata || {});
      } catch (err) {
        console.warn('Could not load session metadata:', err);
      }
    } catch (err) {
      console.error('Failed to load session:', err);
      setError('Failed to load chat history');
    }
  };

  const loadSessions = async () => {
    try {
      const response = await api.listSessions();
      setSessions(response.sessions || []);
    } catch (err) {
      console.error('Failed to load sessions:', err);
    }
  };

  const deleteSession = async (sessionId) => {
    if (!confirm('Are you sure you want to delete this chat?')) return;
    
    try {
      await api.deleteSession(sessionId);
      localStorage.removeItem(`session_${sessionId}_messages`);
      
      // If deleting current session, create new one
      if (sessionId === currentSessionId) {
        await createNewSession();
      }
      
      await loadSessions();
    } catch (err) {
      console.error('Failed to delete session:', err);
      setError('Failed to delete chat');
    }
  };

  const renameSession = async (sessionId, newTitle) => {
    try {
      await api.updateSessionMetadata(sessionId, { title: newTitle });
      setEditingSessionId(null);
      await loadSessions();
      
      // Update local metadata if it's current session
      if (sessionId === currentSessionId) {
        setSessionMetadata(prev => ({ ...prev, title: newTitle }));
      }
    } catch (err) {
      console.error('Failed to rename session:', err);
      setError('Failed to rename chat');
    }
  };

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
              extractedData['Client ID'] = lookupResult.client_id;
              clientLookupData = lookupResult;
            }
          } catch (lookupErr) {
            console.warn('Client lookup failed:', lookupErr);
          }
        }
      }
      
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
    if (!input.trim() || isLoading || !currentSessionId) return;
    
    const userMessage = input.trim();
    
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setInput('');
    setIsLoading(true);
    setError(null);
    
    try {
      if (isConnected) {
        const response = await api.sendChatMessage(userMessage, currentSessionId);
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: response.response || 'I received your message but couldn\'t generate a response.'
        }]);
        
        // Update session metadata message count
        setSessionMetadata(prev => ({
          ...prev,
          message_count: (prev.message_count || 0) + 2
        }));
      } else {
        setTimeout(() => {
          setMessages(prev => [...prev, {
            role: 'assistant',
            content: 'I\'m in demo mode. The backend is not connected.'
          }]);
          setIsLoading(false);
        }, 1000);
        return;
      }
    } catch (err) {
      setError('Failed to send message. Please try again.');
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, I encountered an error processing your message.'
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{
      display: 'flex',
      height: '100%',
      backgroundColor: '#F8FAFC'
    }}>
      {/* Sidebar */}
      {showSidebar && (
        <div style={{
          width: '280px',
          borderRight: '1px solid #E2E8F0',
          backgroundColor: '#FFFFFF',
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden'
        }}>
          {/* Sidebar Header */}
          <div style={{
            padding: '16px',
            borderBottom: '1px solid #E2E8F0'
          }}>
            <button
              onClick={createNewSession}
              style={{
                width: '100%',
                padding: '10px 14px',
                backgroundColor: '#2563EB',
                color: '#FFFFFF',
                border: 'none',
                borderRadius: '8px',
                fontSize: '14px',
                fontWeight: '500',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
                transition: 'all 0.2s'
              }}
              onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#1D4ED8'}
              onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#2563EB'}
            >
              <MessageSquarePlus size={18} />
              New Chat
            </button>
          </div>
          
          {/* Session List */}
          <div style={{
            flex: 1,
            overflowY: 'auto',
            padding: '8px'
          }}>
            {sessions.length === 0 ? (
              <p style={{
                textAlign: 'center',
                color: '#94A3B8',
                fontSize: '13px',
                padding: '16px'
              }}>
                No chat history yet
              </p>
            ) : (
              sessions.map(session => (
                <div
                  key={session.session_id}
                  style={{
                    padding: '10px 12px',
                    marginBottom: '4px',
                    borderRadius: '6px',
                    backgroundColor: session.session_id === currentSessionId ? '#EFF6FF' : 'transparent',
                    border: session.session_id === currentSessionId ? '1px solid #BFDBFE' : '1px solid transparent',
                    cursor: 'pointer',
                    transition: 'all 0.2s',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px'
                  }}
                  onClick={() => loadSession(session.session_id)}
                  onMouseEnter={(e) => {
                    if (session.session_id !== currentSessionId) {
                      e.currentTarget.style.backgroundColor = '#F8FAFC';
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (session.session_id !== currentSessionId) {
                      e.currentTarget.style.backgroundColor = 'transparent';
                    }
                  }}
                >
                  <div style={{ flex: 1, minWidth: 0 }}>
                    {editingSessionId === session.session_id ? (
                      <input
                        type="text"
                        value={editingTitle}
                        onChange={(e) => setEditingTitle(e.target.value)}
                        onKeyPress={(e) => {
                          if (e.key === 'Enter') {
                            renameSession(session.session_id, editingTitle);
                          }
                        }}
                        onBlur={() => renameSession(session.session_id, editingTitle)}
                        autoFocus
                        style={{
                          width: '100%',
                          padding: '2px 4px',
                          border: '1px solid #2563EB',
                          borderRadius: '4px',
                          fontSize: '13px'
                        }}
                        onClick={(e) => e.stopPropagation()}
                      />
                    ) : (
                      <>
                        <div style={{
                          fontSize: '13px',
                          fontWeight: '500',
                          color: '#1E293B',
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          whiteSpace: 'nowrap'
                        }}>
                          {session.metadata?.title || 'Untitled Chat'}
                        </div>
                        <div style={{
                          fontSize: '11px',
                          color: '#94A3B8',
                          marginTop: '2px'
                        }}>
                          {session.metadata?.message_count || 0} messages
                        </div>
                      </>
                    )}
                  </div>
                  
                  <div style={{ display: 'flex', gap: '4px' }}>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setEditingSessionId(session.session_id);
                        setEditingTitle(session.metadata?.title || 'Untitled Chat');
                      }}
                      style={{
                        padding: '4px',
                        backgroundColor: 'transparent',
                        border: 'none',
                        cursor: 'pointer',
                        color: '#64748B',
                        borderRadius: '4px'
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.backgroundColor = '#F1F5F9';
                        e.currentTarget.style.color = '#2563EB';
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.backgroundColor = 'transparent';
                        e.currentTarget.style.color = '#64748B';
                      }}
                    >
                      <Edit2 size={14} />
                    </button>
                    
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        deleteSession(session.session_id);
                      }}
                      style={{
                        padding: '4px',
                        backgroundColor: 'transparent',
                        border: 'none',
                        cursor: 'pointer',
                        color: '#64748B',
                        borderRadius: '4px'
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.backgroundColor = '#FEF2F2';
                        e.currentTarget.style.color = '#DC2626';
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.backgroundColor = 'transparent';
                        e.currentTarget.style.color = '#64748B';
                      }}
                    >
                      <Trash2 size={14} />
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}
      
      {/* Main Chat Area */}
      <div style={{
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        height: '100%'
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
              }}>
                {sessionMetadata?.title || 'AI Assistant'}
              </h1>
              <p style={{
                color: '#64748B',
                fontSize: '14px'
              }}>
                Session-based chat with memory • {messages.length} messages
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

        {/* Chat Messages - Reuse same structure from original */}
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
                    <div style={{
                      fontSize: '14px',
                      lineHeight: '1.6'
                    }} className="markdown-content">
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>
                        {message.content}
                      </ReactMarkdown>
                    </div>
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
                boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                transition: 'all 0.2s ease',
                zIndex: 10
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = '#F8FAFC';
                e.currentTarget.style.transform = 'translateX(-50%) scale(1.05)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = '#FFFFFF';
                e.currentTarget.style.transform = 'translateX(-50%) scale(1)';
              }}
            >
              <ArrowDown size={20} style={{ color: '#64748B' }} />
            </button>
          )}
        </div>

        {/* Input Area - Simplified, no file upload for now */}
        <div style={{
          borderTop: '1px solid #E2E8F0',
          backgroundColor: '#FFFFFF',
          padding: '20px 32px',
          boxShadow: '0 -1px 3px 0 rgba(0, 0, 0, 0.05)'
        }}>
          <div style={{
            maxWidth: '900px',
            margin: '0 auto',
            display: 'flex',
            alignItems: 'center',
            gap: '12px'
          }}>
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Type your message..."
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
