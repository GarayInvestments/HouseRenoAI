// API service for backend communication
const API_URL = import.meta.env.VITE_API_URL || 'https://houserenovators-api.fly.dev';
const API_VERSION = 'v1';

console.log('[API Service] Environment:', import.meta.env.VITE_ENV);
console.log('[API Service] API URL:', API_URL);

class ApiService {
  constructor() {
    this.baseUrl = `${API_URL}/${API_VERSION}`;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    console.log('[API Request] Full URL:', url);
    console.log('[API Request] Base URL:', this.baseUrl);
    
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

  async lookupClient(name = null, email = null) {
    const params = new URLSearchParams();
    if (name) params.append('name', name);
    if (email) params.append('email', email);
    
    return this.request(`/clients/lookup?${params.toString()}`, {
      method: 'GET',
    });
  }

  async updateClient(clientId, updates) {
    return this.request(`/clients/${clientId}`, {
      method: 'PUT',
      body: JSON.stringify(updates),
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
