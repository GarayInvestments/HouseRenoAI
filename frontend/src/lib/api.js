// API service for backend communication
import { supabase } from './supabase'

const API_URL = import.meta.env.VITE_API_URL || 'https://houserenovators-api.fly.dev';
const API_VERSION = 'v1';

class ApiService {
  constructor() {
    this.baseUrl = `${API_URL}/${API_VERSION}`;
    // Auth-critical routes that should trigger logout on 401 after refresh fails
    this.authCriticalRoutes = [
      '/chat',
      '/chat/sessions',
      '/auth',
      '/auth/supabase',
    ];
  }

  async getAuthToken() {
    // Get token from Supabase session (handles refresh automatically)
    const { data: { session }, error } = await supabase.auth.getSession()
    
    if (error || !session) {
      return null
    }
    
    return session.access_token
  }

  isAuthCriticalRoute(endpoint) {
    return this.authCriticalRoutes.some(route => endpoint.startsWith(route));
  }

  async request(endpoint, options = {}, hasRetried = false) {
    const url = `${this.baseUrl}${endpoint}`;
    
    // Get token from Supabase session (not localStorage)
    const token = await this.getAuthToken();
    
    if (!token) {
      console.warn(`[API] No auth token for request to ${endpoint}`);
    } else {
      console.log(`[API] Request to ${endpoint} with token`);
    }
    
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` }),
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      console.log(`[API] Response from ${endpoint}: ${response.status}`);
      
      // Handle 401 Unauthorized - try to refresh session first (but only once per request)
      if (response.status === 401 && !hasRetried) {
        console.warn('[API] 401 Unauthorized - attempting token refresh');
        
        // Try to refresh the session
        const { data: { session }, error } = await supabase.auth.refreshSession();
        
        if (error || !session) {
          // Refresh failed - session is truly expired
          console.error('[API] Token refresh failed');
          
          // Only auto-logout for auth-critical routes
          if (this.isAuthCriticalRoute(endpoint)) {
            console.error('[API] Auth-critical route - redirecting to login');
            await supabase.auth.signOut();
            localStorage.removeItem('user');
            window.location.href = '/';
            throw new Error('Session expired. Please login again.');
          } else {
            // Non-critical route - let the UI handle it
            console.warn('[API] Non-critical route - throwing error for UI to handle');
            throw new Error('Unauthorized. Please check your permissions.');
          }
        }
        
        // Refresh succeeded - retry the request with new token (only once)
        console.log('[API] Token refreshed successfully - retrying request');
        return this.request(endpoint, options, true); // hasRetried = true
      }
      
      // If we already retried and still got 401, don't try again
      if (response.status === 401 && hasRetried) {
        console.error('[API] 401 after refresh - authorization issue');
        
        // Only auto-logout for auth-critical routes
        if (this.isAuthCriticalRoute(endpoint)) {
          await supabase.auth.signOut();
          localStorage.removeItem('user');
          window.location.href = '/';
          throw new Error('Session expired. Please login again.');
        } else {
          // Let UI handle authorization errors
          throw new Error('Unauthorized. Please check your permissions.');
        }
      }
      
      if (!response.ok) {
        throw new Error(`API error: ${response.status} ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // Chat endpoints
  async sendChatMessage(message, sessionId = null, context = {}) {
    return this.request('/chat', {
      method: 'POST',
      body: JSON.stringify({
        message,
        session_id: sessionId,
        context,
      }),
    });
  }

  async getChatStatus() {
    return this.request('/chat/status', {
      method: 'GET',
    });
  }

  // Session management endpoints
  async listSessions() {
    return this.request(`/chat/sessions?t=${Date.now()}`, {
      method: 'GET',
      cache: 'no-cache',
    });
  }

  async createSession(title) {
    // If no title provided, backend will auto-generate EST timestamp
    const body = title ? { title } : {};
    return this.request('/chat/sessions', {
      method: 'POST',
      body: JSON.stringify(body),
    });
  }

  async getSession(sessionId) {
    return this.request(`/chat/sessions/${sessionId}`, {
      method: 'GET',
    });
  }

  async deleteSession(sessionId) {
    return this.request(`/chat/sessions/${sessionId}`, {
      method: 'DELETE',
    });
  }

  async updateSessionMetadata(sessionId, metadata) {
    return this.request(`/chat/sessions/${sessionId}/metadata`, {
      method: 'PUT',
      body: JSON.stringify(metadata),
    });
  }

  // Permits endpoints
  async getPermits() {
    return this.request('/permits', {
      method: 'GET',
    });
  }

  async getPermit(permitId) {
    return this.request(`/permits/${permitId}`, {
      method: 'GET',
    });
  }

  async createPermit(permitData) {
    return this.request('/permits', {
      method: 'POST',
      body: JSON.stringify(permitData),
    });
  }

  async updatePermit(permitId, permitData) {
    return this.request(`/permits/${permitId}`, {
      method: 'PUT',
      body: JSON.stringify(permitData),
    });
  }

  // Projects endpoints
  async getProjects() {
    return this.request('/projects', {
      method: 'GET',
    });
  }

  async getProject(projectId) {
    return this.request(`/projects/${projectId}`, {
      method: 'GET',
    });
  }

  async updateProject(projectId, updates, notifyTeam = true) {
    return this.request(`/projects/${projectId}`, {
      method: 'PUT',
      body: JSON.stringify({
        updates,
        notify_team: notifyTeam,
      }),
    });
  }

  // Clients endpoints
  async getClients() {
    return this.request('/clients', {
      method: 'GET',
    });
  }

  async getClient(clientId) {
    return this.request(`/clients/${clientId}`, {
      method: 'GET',
    });
  }

  async createClient(clientData) {
    return this.request('/clients', {
      method: 'POST',
      body: JSON.stringify(clientData),
    });
  }

  async updateClient(clientId, updates) {
    return this.request(`/clients/${clientId}`, {
      method: 'PUT',
      body: JSON.stringify(updates),
    });
  }

  async deleteClient(clientId) {
    return this.request(`/clients/${clientId}`, {
      method: 'DELETE',
    });
  }

  async lookupClient(name = null, email = null) {
    const params = new URLSearchParams();
    if (name) params.append('name', name);
    if (email) params.append('email', email);
    
    return this.request(`/clients/lookup?${params.toString()}`, {
      method: 'GET',
    });
  }

  // Projects endpoints (extended)
  async createProject(projectData) {
    return this.request('/projects', {
      method: 'POST',
      body: JSON.stringify(projectData),
    });
  }

  async deleteProject(projectId) {
    return this.request(`/projects/${projectId}`, {
      method: 'DELETE',
    });
  }

  // Permits endpoints (extended)
  async deletePermit(permitId) {
    return this.request(`/permits/${permitId}`, {
      method: 'DELETE',
    });
  }

  // Invoices endpoints
  async getInvoices() {
    return this.request('/invoices', {
      method: 'GET',
    });
  }

  async getInvoice(invoiceId) {
    return this.request(`/invoices/${invoiceId}`, {
      method: 'GET',
    });
  }

  async createInvoice(invoiceData) {
    return this.request('/invoices', {
      method: 'POST',
      body: JSON.stringify(invoiceData),
    });
  }

  async updateInvoice(invoiceId, invoiceData) {
    return this.request(`/invoices/${invoiceId}`, {
      method: 'PUT',
      body: JSON.stringify(invoiceData),
    });
  }

  async deleteInvoice(invoiceId) {
    return this.request(`/invoices/${invoiceId}`, {
      method: 'DELETE',
    });
  }

  async getInvoicesByProject(projectId) {
    return this.request(`/invoices/project/${projectId}`, {
      method: 'GET',
    });
  }

  // Payments endpoints
  async getPayments() {
    return this.request('/payments', {
      method: 'GET',
    });
  }

  async createPayment(paymentData) {
    return this.request('/payments', {
      method: 'POST',
      body: JSON.stringify(paymentData),
    });
  }

  async syncPayments() {
    return this.request('/payments/sync', {
      method: 'POST',
    });
  }

  // Inspections endpoints
  async getInspections() {
    return this.request('/inspections', {
      method: 'GET',
    });
  }

  async getInspection(inspectionId) {
    return this.request(`/inspections/${inspectionId}`, {
      method: 'GET',
    });
  }

  async createInspection(inspectionData) {
    return this.request('/inspections', {
      method: 'POST',
      body: JSON.stringify(inspectionData),
    });
  }

  async updateInspection(inspectionId, inspectionData) {
    return this.request(`/inspections/${inspectionId}`, {
      method: 'PUT',
      body: JSON.stringify(inspectionData),
    });
  }

  async deleteInspection(inspectionId) {
    return this.request(`/inspections/${inspectionId}`, {
      method: 'DELETE',
    });
  }

  async addInspectionPhoto(inspectionId, photoData) {
    return this.request(`/inspections/${inspectionId}/photos`, {
      method: 'POST',
      body: JSON.stringify(photoData),
    });
  }

  async addInspectionDeficiency(inspectionId, deficiencyData) {
    return this.request(`/inspections/${inspectionId}/deficiencies`, {
      method: 'POST',
      body: JSON.stringify(deficiencyData),
    });
  }

  // Site Visits endpoints
  async getSiteVisits() {
    return this.request('/site-visits', {
      method: 'GET',
    });
  }

  async getSiteVisit(visitId) {
    return this.request(`/site-visits/${visitId}`, {
      method: 'GET',
    });
  }

  async createSiteVisit(visitData) {
    return this.request('/site-visits', {
      method: 'POST',
      body: JSON.stringify(visitData),
    });
  }

  async updateSiteVisit(visitId, visitData) {
    return this.request(`/site-visits/${visitId}`, {
      method: 'PUT',
      body: JSON.stringify(visitData),
    });
  }

  async deleteSiteVisit(visitId) {
    return this.request(`/site-visits/${visitId}`, {
      method: 'DELETE',
    });
  }

  async getSiteVisitsByProject(projectId) {
    return this.request(`/site-visits/project/${projectId}`, {
      method: 'GET',
    });
  }

  // Jurisdictions endpoints
  async getJurisdictions() {
    return this.request('/jurisdictions', {
      method: 'GET',
    });
  }

  async getJurisdiction(jurisdictionId) {
    return this.request(`/jurisdictions/${jurisdictionId}`, {
      method: 'GET',
    });
  }

  async createJurisdiction(jurisdictionData) {
    return this.request('/jurisdictions', {
      method: 'POST',
      body: JSON.stringify(jurisdictionData),
    });
  }

  async updateJurisdiction(jurisdictionId, jurisdictionData) {
    return this.request(`/jurisdictions/${jurisdictionId}`, {
      method: 'PUT',
      body: JSON.stringify(jurisdictionData),
    });
  }

  async deleteJurisdiction(jurisdictionId) {
    return this.request(`/jurisdictions/${jurisdictionId}`, {
      method: 'DELETE',
    });
  }

  // Users endpoints (admin only)
  async getUsers() {
    return this.request('/users', {
      method: 'GET',
    });
  }

  async getUser(userId) {
    return this.request(`/users/${userId}`, {
      method: 'GET',
    });
  }

  async createUser(userData) {
    return this.request('/users', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  }

  async updateUser(userId, userData) {
    return this.request(`/users/${userId}`, {
      method: 'PUT',
      body: JSON.stringify(userData),
    });
  }

  async deleteUser(userId) {
    return this.request(`/users/${userId}`, {
      method: 'DELETE',
    });
  }

  async updateUserRole(userId, role) {
    return this.request(`/users/${userId}/role`, {
      method: 'PUT',
      body: JSON.stringify({ role }),
    });
  }

  async activateUser(userId) {
    return this.request(`/users/${userId}/activate`, {
      method: 'PUT',
    });
  }

  async deactivateUser(userId) {
    return this.request(`/users/${userId}/deactivate`, {
      method: 'PUT',
    });
  }

  // Document upload endpoints
  async uploadDocument(formData) {
    const url = `${this.baseUrl}/documents/extract`;
    
    // Get auth token from Supabase session
    const token = await this.getAuthToken();
    
    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          // Add Authorization header, but NOT Content-Type (browser sets multipart boundary)
          ...(token && { 'Authorization': `Bearer ${token}` }),
        },
        body: formData,
      });
      
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || `Upload failed: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Document upload failed:', error);
      throw error;
    }
  }

  async createFromExtract(documentType, extractedData) {
    return this.request('/documents/create-from-extract', {
      method: 'POST',
      body: JSON.stringify({
        document_type: documentType,
        extracted_data: extractedData,
      }),
    });
  }

  // Health check
  async healthCheck() {
    const url = `${API_URL}/health`;
    const response = await fetch(url);
    return await response.json();
  }

  // QuickBooks endpoints
  async getQuickBooksStatus() {
    return this.request('/quickbooks/status', {
      method: 'GET',
    });
  }

  // Phase Q Compliance endpoints
  async getLicensedBusinesses() {
    return this.request('/licensed-businesses', {
      method: 'GET',
    });
  }

  async getQualifiers() {
    return this.request('/qualifiers', {
      method: 'GET',
    });
  }
}

export default new ApiService();
