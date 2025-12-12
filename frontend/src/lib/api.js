// API service for backend communication
const API_URL = import.meta.env.VITE_API_URL || 'https://houserenovators-api.fly.dev';
const API_VERSION = 'v1';

class ApiService {
  constructor() {
    this.baseUrl = `${API_URL}/${API_VERSION}`;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    
    // Get token from localStorage
    const token = localStorage.getItem('token');
    
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
      
      // Handle 401 Unauthorized - redirect to login
      if (response.status === 401) {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = '/';
        throw new Error('Session expired. Please login again.');
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
    
    try {
      const response = await fetch(url, {
        method: 'POST',
        body: formData, // Don't set Content-Type header - browser will set it with boundary
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
}

export default new ApiService();
