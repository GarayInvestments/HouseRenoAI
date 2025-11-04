// API service for backend communication
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_VERSION = 'v1';

class ApiService {
  constructor() {
    this.baseUrl = `${API_URL}/${API_VERSION}`;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
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
  async sendChatMessage(message, context = {}) {
    return this.request('/chat', {
      method: 'POST',
      body: JSON.stringify({
        message,
        context,
      }),
    });
  }

  async getChatStatus() {
    return this.request('/chat/status', {
      method: 'GET',
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

  // Health check
  async healthCheck() {
    const url = `${API_URL}/health`;
    const response = await fetch(url);
    return await response.json();
  }
}

export default new ApiService();
