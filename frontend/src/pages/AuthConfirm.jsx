import { useEffect, useState } from 'react';
import { supabase } from '../lib/supabase';
import { useAppStore } from '../stores/appStore';

function AuthConfirm() {
  const [status, setStatus] = useState('verifying'); // verifying, success, error
  const [message, setMessage] = useState('Verifying your email...');
  const { setCurrentView } = useAppStore();

  useEffect(() => {
    const confirmEmail = async () => {
      try {
        // Get token_hash and type from URL
        const params = new URLSearchParams(window.location.search);
        const tokenHash = params.get('token_hash');
        const type = params.get('type');

        if (!tokenHash || !type) {
          setStatus('error');
          setMessage('Invalid confirmation link. Please try again or request a new link.');
          return;
        }

        // Verify the OTP token
        const { data, error } = await supabase.auth.verifyOtp({
          token_hash: tokenHash,
          type: type, // 'email', 'invite', 'magiclink', 'email_change'
        });

        if (error) {
          console.error('Verification error:', error);
          setStatus('error');
          
          if (error.message.includes('expired')) {
            setMessage('This verification link has expired. Please request a new one.');
          } else if (error.message.includes('invalid')) {
            setMessage('Invalid verification link. Please check your email for the correct link.');
          } else {
            setMessage(`Verification failed: ${error.message}`);
          }
          return;
        }

        // Success!
        setStatus('success');
        
        // Different messages based on type
        if (type === 'email') {
          setMessage('Email confirmed successfully! Redirecting to login...');
        } else if (type === 'invite') {
          setMessage('Invitation accepted! Redirecting to dashboard...');
        } else if (type === 'magiclink') {
          setMessage('Magic link verified! Redirecting to dashboard...');
        } else if (type === 'email_change') {
          setMessage('Email address changed successfully! Redirecting to dashboard...');
        }

        // Redirect after 2 seconds
        setTimeout(() => {
          if (data.session) {
            // User is logged in, go to dashboard
            setCurrentView('dashboard');
          } else {
            // No session, go to login
            setCurrentView('login');
          }
        }, 2000);

      } catch (err) {
        console.error('Unexpected error:', err);
        setStatus('error');
        setMessage('An unexpected error occurred. Please try again.');
      }
    };

    confirmEmail();
  }, [setCurrentView]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-xl shadow-lg p-8">
        {/* Icon */}
        <div className="flex justify-center mb-6">
          {status === 'verifying' && (
            <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600"></div>
          )}
          {status === 'success' && (
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center">
              <svg className="w-10 h-10 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
          )}
          {status === 'error' && (
            <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center">
              <svg className="w-10 h-10 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
          )}
        </div>

        {/* Title */}
        <h1 className="text-2xl font-bold text-center mb-4 text-gray-900">
          {status === 'verifying' && 'Verifying Email'}
          {status === 'success' && 'Success!'}
          {status === 'error' && 'Verification Failed'}
        </h1>

        {/* Message */}
        <p className="text-center text-gray-600 mb-6">
          {message}
        </p>

        {/* Action Buttons */}
        {status === 'error' && (
          <div className="space-y-3">
            <button
              onClick={() => setCurrentView('login')}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-4 rounded-lg transition-colors"
            >
              Go to Login
            </button>
            <button
              onClick={() => window.location.reload()}
              className="w-full bg-gray-200 hover:bg-gray-300 text-gray-800 font-medium py-3 px-4 rounded-lg transition-colors"
            >
              Try Again
            </button>
          </div>
        )}

        {status === 'success' && (
          <div className="flex justify-center">
            <div className="animate-pulse text-blue-600 font-medium">
              Redirecting...
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default AuthConfirm;
