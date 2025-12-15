import { RefreshCw, AlertCircle, CheckCircle, Clock, Pause, Play, Zap, ShieldAlert, ShieldCheck } from 'lucide-react';
import { useState, useEffect } from 'react';
import { supabase } from '../lib/supabase';

/**
 * QuickBooks Sync Control Panel
 * 
 * Displays:
 * - Circuit breaker status badge
 * - Scheduler status (next sync time)
 * - Manual sync button
 * - Scheduler pause/resume controls (admin)
 */
export default function SyncControlPanel({ 
  onManualSync, 
  syncStatus = 'idle', 
  syncError = null,
  lastSyncTime = null,
  nextSyncTime = null
}) {
  const [circuitBreakerStatus, setCircuitBreakerStatus] = useState(null);
  const [schedulerStatus, setSchedulerStatus] = useState(null);
  const [loadingCircuitBreaker, setLoadingCircuitBreaker] = useState(false);
  const [loadingScheduler, setLoadingScheduler] = useState(false);

  useEffect(() => {
    fetchCircuitBreakerStatus();
    fetchSchedulerStatus();
    
    // Refresh every 30 seconds
    const interval = setInterval(() => {
      fetchCircuitBreakerStatus();
      fetchSchedulerStatus();
    }, 30000);
    
    return () => clearInterval(interval);
  }, []);

  const fetchCircuitBreakerStatus = async () => {
    try {
      const { data: { session } } = await supabase.auth.getSession();
      const token = session?.access_token;
      if (!token) return;

      const apiUrl = import.meta.env.VITE_API_URL || 'https://houserenovators-api.fly.dev';
      const response = await fetch(`${apiUrl}/v1/quickbooks/sync/circuit-breaker`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        const data = await response.json();
        setCircuitBreakerStatus(data);
      }
    } catch (error) {
      console.error('Failed to fetch circuit breaker status:', error);
    }
  };

  const fetchSchedulerStatus = async () => {
    try {
      const { data: { session } } = await supabase.auth.getSession();
      const token = session?.access_token;
      if (!token) return;

      const apiUrl = import.meta.env.VITE_API_URL || 'https://houserenovators-api.fly.dev';
      const response = await fetch(`${apiUrl}/v1/quickbooks/sync/scheduler`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        const data = await response.json();
        setSchedulerStatus(data);
      }
    } catch (error) {
      console.error('Failed to fetch scheduler status:', error);
    }
  };

  const handlePauseScheduler = async () => {
    setLoadingScheduler(true);
    try {
      const { data: { session } } = await supabase.auth.getSession();
      const token = session?.access_token;
      if (!token) return;

      const apiUrl = import.meta.env.VITE_API_URL || 'https://houserenovators-api.fly.dev';
      const response = await fetch(`${apiUrl}/v1/quickbooks/sync/scheduler/pause`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        await fetchSchedulerStatus();
      }
    } catch (error) {
      console.error('Failed to pause scheduler:', error);
    } finally {
      setLoadingScheduler(false);
    }
  };

  const handleResumeScheduler = async () => {
    setLoadingScheduler(true);
    try {
      const { data: { session } } = await supabase.auth.getSession();
      const token = session?.access_token;
      if (!token) return;

      const apiUrl = import.meta.env.VITE_API_URL || 'https://houserenovators-api.fly.dev';
      const response = await fetch(`${apiUrl}/v1/quickbooks/sync/scheduler/resume`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        await fetchSchedulerStatus();
      }
    } catch (error) {
      console.error('Failed to resume scheduler:', error);
    } finally {
      setLoadingScheduler(false);
    }
  };

  const handleResetCircuitBreaker = async () => {
    setLoadingCircuitBreaker(true);
    try {
      const { data: { session } } = await supabase.auth.getSession();
      const token = session?.access_token;
      if (!token) return;

      const apiUrl = import.meta.env.VITE_API_URL || 'https://houserenovators-api.fly.dev';
      const response = await fetch(`${apiUrl}/v1/quickbooks/sync/circuit-breaker/reset`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        await fetchCircuitBreakerStatus();
      }
    } catch (error) {
      console.error('Failed to reset circuit breaker:', error);
    } finally {
      setLoadingCircuitBreaker(false);
    }
  };

  // Circuit breaker badge
  const getCircuitBreakerBadge = () => {
    if (!circuitBreakerStatus) return null;

    // Backend nests data in circuit_breaker object
    const cbData = circuitBreakerStatus.circuit_breaker || circuitBreakerStatus;
    const { state, failure_count, failure_threshold } = cbData;
    
    const stateConfig = {
      'closed': {
        icon: ShieldCheck,
        color: '#059669',
        bg: '#ECFDF5',
        border: '#A7F3D0',
        label: 'Healthy'
      },
      'open': {
        icon: ShieldAlert,
        color: '#DC2626',
        bg: '#FEE2E2',
        border: '#FECACA',
        label: 'Open'
      },
      'half_open': {
        icon: AlertCircle,
        color: '#D97706',
        bg: '#FEF3C7',
        border: '#FDE68A',
        label: 'Testing'
      }
    };

    const config = stateConfig[state] || stateConfig['closed'];
    const Icon = config.icon;

    return (
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        padding: '6px 12px',
        backgroundColor: config.bg,
        border: `1px solid ${config.border}`,
        borderRadius: '6px'
      }}>
        <Icon size={14} color={config.color} />
        <span style={{ fontSize: '13px', fontWeight: '500', color: config.color }}>
          {config.label}
        </span>
        {state !== 'closed' && (
          <span style={{ fontSize: '12px', color: config.color, opacity: 0.8 }}>
            ({failure_count}/{failure_threshold})
          </span>
        )}
      </div>
    );
  };

  // Sync status indicator
  const getSyncStatusBadge = () => {
    const statusConfig = {
      'idle': { icon: Clock, color: '#6B7280', bg: '#F3F4F6', label: 'Ready' },
      'syncing': { icon: RefreshCw, color: '#2563EB', bg: '#DBEAFE', label: 'Syncing' },
      'success': { icon: CheckCircle, color: '#059669', bg: '#ECFDF5', label: 'Success' },
      'error': { icon: AlertCircle, color: '#DC2626', bg: '#FEE2E2', label: 'Error' }
    };

    const config = statusConfig[syncStatus] || statusConfig['idle'];
    const Icon = config.icon;

    return (
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '6px',
        padding: '4px 10px',
        backgroundColor: config.bg,
        borderRadius: '6px'
      }}>
        <Icon size={14} color={config.color} className={syncStatus === 'syncing' ? 'spin' : ''} />
        <span style={{ fontSize: '13px', color: config.color, fontWeight: '500' }}>
          {config.label}
        </span>
      </div>
    );
  };

  const formatTimeSince = (dateString) => {
    if (!dateString) return null;
    const now = new Date();
    const syncDate = new Date(dateString);
    const diffMs = now - syncDate;
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffMins = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));
    
    if (diffHours < 1) return `${diffMins} min ago`;
    return `${diffHours}h ${diffMins}m ago`;
  };

  return (
    <div style={{
      backgroundColor: 'white',
      padding: '16px',
      borderRadius: '12px',
      border: '1px solid #E5E7EB',
      boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
    }}>
      {/* Top row: Circuit breaker + Sync status */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: '12px',
        flexWrap: 'wrap',
        gap: '8px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          {getCircuitBreakerBadge()}
          {getSyncStatusBadge()}
        </div>

        {/* Manual sync button */}
        <button
          onClick={onManualSync}
          disabled={syncStatus === 'syncing'}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            padding: '8px 16px',
            backgroundColor: syncStatus === 'syncing' ? '#F3F4F6' : '#2563EB',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            cursor: syncStatus === 'syncing' ? 'not-allowed' : 'pointer',
            fontSize: '14px',
            fontWeight: '500',
            opacity: syncStatus === 'syncing' ? 0.6 : 1
          }}
        >
          <RefreshCw size={16} className={syncStatus === 'syncing' ? 'spin' : ''} />
          {syncStatus === 'syncing' ? 'Syncing...' : 'Sync Now'}
        </button>
      </div>

      {/* Bottom row: Scheduler info + controls */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        paddingTop: '12px',
        borderTop: '1px solid #F3F4F6',
        flexWrap: 'wrap',
        gap: '8px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          {lastSyncTime && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <CheckCircle size={14} color='#059669' />
              <span style={{ fontSize: '13px', color: '#6B7280' }}>
                Last: {formatTimeSince(lastSyncTime)}
              </span>
            </div>
          )}
          {nextSyncTime && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Clock size={14} color='#6B7280' />
              <span style={{ fontSize: '13px', color: '#6B7280' }}>
                Next: {new Date(nextSyncTime).toLocaleTimeString('en-US', { 
                  hour: 'numeric', 
                  minute: '2-digit',
                  hour12: true 
                })}
              </span>
            </div>
          )}
        </div>

        {/* Scheduler controls */}
        {schedulerStatus && (
          <div style={{ display: 'flex', gap: '8px' }}>
            {schedulerStatus.is_paused ? (
              <button
                onClick={handleResumeScheduler}
                disabled={loadingScheduler}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px',
                  padding: '6px 12px',
                  backgroundColor: '#059669',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: loadingScheduler ? 'not-allowed' : 'pointer',
                  fontSize: '13px',
                  fontWeight: '500'
                }}
              >
                <Play size={14} />
                Resume
              </button>
            ) : (
              <button
                onClick={handlePauseScheduler}
                disabled={loadingScheduler}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px',
                  padding: '6px 12px',
                  backgroundColor: '#D97706',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: loadingScheduler ? 'not-allowed' : 'pointer',
                  fontSize: '13px',
                  fontWeight: '500'
                }}
              >
                <Pause size={14} />
                Pause
              </button>
            )}

            {circuitBreakerStatus?.state === 'OPEN' && (
              <button
                onClick={handleResetCircuitBreaker}
                disabled={loadingCircuitBreaker}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px',
                  padding: '6px 12px',
                  backgroundColor: '#DC2626',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: loadingCircuitBreaker ? 'not-allowed' : 'pointer',
                  fontSize: '13px',
                  fontWeight: '500'
                }}
              >
                <Zap size={14} />
                Reset
              </button>
            )}
          </div>
        )}
      </div>

      {/* Error message */}
      {syncError && (
        <div style={{
          marginTop: '12px',
          padding: '8px 12px',
          backgroundColor: '#FEE2E2',
          border: '1px solid #FECACA',
          borderRadius: '6px',
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}>
          <AlertCircle size={14} color='#DC2626' />
          <span style={{ fontSize: '13px', color: '#DC2626' }}>{syncError}</span>
        </div>
      )}

      {/* Add spinning animation */}
      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
        .spin {
          animation: spin 1s linear infinite;
        }
      `}</style>
    </div>
  );
}
