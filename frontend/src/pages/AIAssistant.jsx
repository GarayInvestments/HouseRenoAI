import { Send, Bot, User, AlertCircle, ArrowDown } from 'lucide-react';
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
  
  const messagesEndRef = useRef(null);
  const messagesContainerRef = useRef(null);

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
    } catch (err) {
      setIsConnected(false);
      setError('Backend connection failed. Using demo mode.');
      console.error('Backend connection error:', err);
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
    } catch (err) {
      console.error('Chat error:', err);
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
  );
}
