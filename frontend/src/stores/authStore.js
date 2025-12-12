import { create } from 'zustand'

const API_URL = import.meta.env.VITE_API_URL || 'https://houserenovators-api.fly.dev'

export const useAuthStore = create((set, get) => ({
  // State
  isAuthenticated: false,
  user: null,
  accessToken: null,
  refreshToken: null,
  loading: false,
  error: null,

  // Auto-refresh timer
  refreshTimer: null,

  // Initialize from localStorage
  initialize: () => {
    const refreshToken = localStorage.getItem('refresh_token')
    const userStr = localStorage.getItem('user')
    
    if (refreshToken && userStr) {
      try {
        const user = JSON.parse(userStr)
        set({ 
          refreshToken,
          user,
          isAuthenticated: true 
        })
        // Attempt to get a fresh access token (don't clear auth on failure during init)
        get().refreshAccessToken(false).catch(() => {
          // Silent fail on init - this is expected if refresh token is expired or invalid
          // The user will be prompted to login on first API call
        })
      } catch (error) {
        console.error('Failed to parse stored user:', error)
        get().clearAuth()
      }
    }
  },

  // Login
  login: async (email, password) => {
    set({ loading: true, error: null })
    
    try {
      const response = await fetch(`${API_URL}/v1/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Login failed')
      }

      const data = await response.json()
      
      // Store tokens
      localStorage.setItem('refresh_token', data.refresh_token)
      localStorage.setItem('user', JSON.stringify(data.user))
      
      set({
        isAuthenticated: true,
        user: data.user,
        accessToken: data.access_token,
        refreshToken: data.refresh_token,
        loading: false,
        error: null
      })

      // Schedule token refresh (13 minutes - before 15 min expiry)
      get().scheduleTokenRefresh(13 * 60 * 1000)

      return { success: true }
    } catch (error) {
      set({ loading: false, error: error.message })
      return { success: false, error: error.message }
    }
  },

  // Register
  register: async (email, password, fullName, phone = null) => {
    set({ loading: true, error: null })
    
    try {
      const response = await fetch(`${API_URL}/v1/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          email, 
          password, 
          full_name: fullName,
          phone
        })
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Registration failed')
      }

      const data = await response.json()
      
      // Store tokens
      localStorage.setItem('refresh_token', data.refresh_token)
      localStorage.setItem('user', JSON.stringify(data.user))
      
      set({
        isAuthenticated: true,
        user: data.user,
        accessToken: data.access_token,
        refreshToken: data.refresh_token,
        loading: false,
        error: null
      })

      // Schedule token refresh
      get().scheduleTokenRefresh(13 * 60 * 1000)

      return { success: true }
    } catch (error) {
      set({ loading: false, error: error.message })
      return { success: false, error: error.message }
    }
  },

  // Refresh access token
  refreshAccessToken: async (clearOnFailure = true) => {
    const { refreshToken } = get()
    
    if (!refreshToken) {
      if (clearOnFailure) get().clearAuth()
      return { success: false, error: 'No refresh token' }
    }

    try {
      const response = await fetch(`${API_URL}/v1/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: refreshToken })
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || 'Token refresh failed')
      }

      const data = await response.json()
      
      // Update tokens
      localStorage.setItem('refresh_token', data.refresh_token)
      
      set({
        accessToken: data.access_token,
        refreshToken: data.refresh_token
      })

      // Schedule next refresh
      get().scheduleTokenRefresh(13 * 60 * 1000)

      return { success: true }
    } catch (error) {
      console.error('Token refresh failed:', error)
      if (clearOnFailure) {
        get().clearAuth()
      }
      return { success: false, error: error.message }
    }
  },

  // Schedule automatic token refresh
  scheduleTokenRefresh: (delayMs) => {
    const { refreshTimer } = get()
    
    // Clear existing timer
    if (refreshTimer) {
      clearTimeout(refreshTimer)
    }

    // Schedule new refresh
    const timer = setTimeout(() => {
      get().refreshAccessToken()
    }, delayMs)

    set({ refreshTimer: timer })
  },

  // Logout
  logout: async () => {
    const { accessToken, refreshTimer } = get()
    
    // Clear refresh timer
    if (refreshTimer) {
      clearTimeout(refreshTimer)
    }

    // Call backend logout if we have a token
    if (accessToken) {
      try {
        await fetch(`${API_URL}/v1/auth/logout`, {
          method: 'POST',
          headers: { 
            'Authorization': `Bearer ${accessToken}`,
            'Content-Type': 'application/json'
          }
        })
      } catch (error) {
        console.error('Logout request failed:', error)
        // Continue with local cleanup even if backend call fails
      }
    }

    get().clearAuth()
  },

  // Clear authentication state
  clearAuth: () => {
    const { refreshTimer } = get()
    
    if (refreshTimer) {
      clearTimeout(refreshTimer)
    }

    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
    
    set({
      isAuthenticated: false,
      user: null,
      accessToken: null,
      refreshToken: null,
      refreshTimer: null,
      error: null
    })
  },

  // Get current user
  getCurrentUser: async () => {
    const { accessToken } = get()
    
    if (!accessToken) {
      return { success: false, error: 'Not authenticated' }
    }

    try {
      const response = await fetch(`${API_URL}/v1/auth/me`, {
        method: 'GET',
        headers: { 
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json'
        }
      })

      if (!response.ok) {
        throw new Error('Failed to get user info')
      }

      const user = await response.json()
      
      set({ user })
      localStorage.setItem('user', JSON.stringify(user))

      return { success: true, user }
    } catch (error) {
      console.error('Get current user failed:', error)
      return { success: false, error: error.message }
    }
  }
}))

export default useAuthStore
