/**
 * API Client Wrapper
 * Provides retry logic, timeout handling, and error normalization
 * 
 * Features:
 * - Automatic retries with exponential backoff
 * - Request timeout (configurable, default 8s)
 * - Normalized error responses
 * - AbortController support for cancellation
 */

/**
 * Wraps API requests with retry, timeout, and error handling
 * 
 * @param {Function} request - Function that returns a Promise (e.g., fetch call)
 * @param {Object} options - Configuration options
 * @param {number} options.retries - Number of retry attempts (default: 2)
 * @param {number} options.timeout - Timeout in milliseconds (default: 8000)
 * @returns {Object} { data, error, status, httpStatus }
 */
export async function apiClient(request, options = {}) {
  const { retries = 2, timeout = 8000 } = options;
  
  let lastError;
  let lastHttpStatus = null;
  
  for (let i = 0; i <= retries; i++) {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), timeout);
      
      // Execute request with abort signal
      const response = await request({ signal: controller.signal });
      clearTimeout(timeoutId);
      
      return { 
        data: response.data || response, 
        error: null, 
        status: 'success',
        httpStatus: response.httpStatus || 200
      };
    } catch (err) {
      lastError = err;
      lastHttpStatus = err.httpStatus || null;
      
      // Don't retry on abort (user cancelled or timeout)
      if (err.name === 'AbortError') {
        break;
      }
      
      // Don't retry on client errors (4xx)
      if (lastHttpStatus >= 400 && lastHttpStatus < 500) {
        break;
      }
      
      // Exponential backoff before retry (1s, 2s, 3s...)
      if (i < retries) {
        await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)));
      }
    }
  }
  
  // All retries failed - return standardized error shape
  const isRetriable = lastHttpStatus >= 500 || lastHttpStatus === null;
  return { 
    data: null, 
    error: {
      message: lastError?.message || 'Request failed',
      code: lastHttpStatus || 'NETWORK_ERROR',
      retriable: isRetriable
    },
    status: 'error',
    httpStatus: lastHttpStatus
  };
}

/**
 * Wraps a fetch call for use with apiClient
 * Automatically parses JSON and handles HTTP errors
 * 
 * @param {string} url - API endpoint URL
 * @param {Object} options - fetch options (method, headers, body, etc.)
 * @returns {Promise} Resolved JSON data with httpStatus or throws error with httpStatus
 */
export async function fetchJSON(url, options = {}) {
  return async ({ signal } = {}) => {
    const response = await fetch(url, { ...options, signal });
    
    // Handle HTTP errors
    if (!response.ok) {
      const errorText = await response.text().catch(() => 'Unknown error');
      const error = new Error(`HTTP ${response.status}: ${errorText}`);
      error.httpStatus = response.status;
      throw error;
    }
    
    // Parse JSON response and attach httpStatus
    const data = await response.json();
    return { data, httpStatus: response.status };
  };
}

/**
 * Example usage:
 * 
 * const { data, error, httpStatus } = await apiClient(
 *   fetchJSON(`${API_URL}/projects`, { 
 *     headers: { Authorization: `Bearer ${token}` } 
 *   }),
 *   { retries: 3, timeout: 10000 }
 * );
 * 
 * if (error) {
 *   console.error('Failed to fetch projects:', error.message);
 *   
 *   // Handle different error types
 *   if (httpStatus === 401) {
 *     // Auth error - redirect to login
 *   } else if (httpStatus === 422) {
 *     // Validation error - show to user
 *   } else if (error.retriable) {
 *     // Network/server error - show retry option
 *   }
 *   return;
 * }
 * 
 * setProjects(data);
 */
