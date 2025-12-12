import { AlertCircle, RefreshCw } from 'lucide-react'

/**
 * Reusable error state component
 * Shows error message with retry functionality
 */
export default function ErrorState({ 
  message = 'Something went wrong', 
  onRetry,
  fullScreen = false 
}) {
  const containerStyle = fullScreen ? {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: '60vh',
    padding: '20px',
    textAlign: 'center'
  } : {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '40px 20px',
    textAlign: 'center',
    backgroundColor: '#FEF2F2',
    borderRadius: '12px',
    border: '1px solid #FEE2E2',
    margin: '20px 0'
  }

  return (
    <div style={containerStyle}>
      <div style={{
        width: '64px',
        height: '64px',
        borderRadius: '50%',
        backgroundColor: '#FEE2E2',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        marginBottom: '16px'
      }}>
        <AlertCircle size={32} style={{ color: '#DC2626' }} />
      </div>
      
      <h3 style={{
        fontSize: '18px',
        fontWeight: '600',
        color: '#1E293B',
        marginBottom: '8px'
      }}>
        Error Loading Data
      </h3>
      
      <p style={{
        fontSize: '14px',
        color: '#64748B',
        marginBottom: '20px',
        maxWidth: '400px'
      }}>
        {message}
      </p>
      
      {onRetry && (
        <button
          onClick={onRetry}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '10px 20px',
            backgroundColor: '#2563EB',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            fontSize: '14px',
            fontWeight: '500',
            cursor: 'pointer',
            transition: 'background-color 0.2s'
          }}
          onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#1D4ED8'}
          onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#2563EB'}
        >
          <RefreshCw size={16} />
          Try Again
        </button>
      )}
    </div>
  )
}
