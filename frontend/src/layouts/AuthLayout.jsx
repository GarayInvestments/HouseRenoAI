import React from 'react';

/**
 * AuthLayout - Layout for authentication pages (Login, Register, etc.)
 * Simple centered layout without app navigation
 */
export default function AuthLayout({ children }) {
  return (
    <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-blue-500 to-blue-700">
      <div className="w-full max-w-md">
        {children}
      </div>
    </div>
  );
}
