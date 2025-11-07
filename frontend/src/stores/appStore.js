import { create } from 'zustand'

const API_URL = import.meta.env.VITE_API_URL || 'https://api.houserenovatorsllc.com'

export const useAppStore = create((set, get) => ({
  // Authentication state
  isAuthenticated: false,
  currentUser: null,
  token: null,
  
  // Auth actions
  login: async (email, password) => {
    try {
      const response = await fetch(`${API_URL}/v1/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      })
      
      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Login failed')
      }
      
      const data = await response.json()
      
      // Store token and user
      localStorage.setItem('token', data.access_token)
      localStorage.setItem('user', JSON.stringify(data.user))
      
      set({
        isAuthenticated: true,
        currentUser: data.user,
        token: data.access_token,
        user: {
          name: data.user.name,
          initials: data.user.name.split(' ').map(n => n[0]).join(''),
          email: data.user.email,
          role: data.user.role
        },
        currentView: 'dashboard'
      })
    } catch (error) {
      console.error('Login error:', error)
      throw error
    }
  },
  
  logout: () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    set({
      isAuthenticated: false,
      currentUser: null,
      token: null,
      currentView: 'login',
      user: null
    })
  },
  
  checkAuth: async () => {
    const token = localStorage.getItem('token')
    const userStr = localStorage.getItem('user')
    
    if (!token || !userStr) {
      set({ currentView: 'login', isAuthenticated: false })
      return false
    }
    
    try {
      // Verify token with /me endpoint
      const response = await fetch(`${API_URL}/v1/auth/me`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (!response.ok) {
        // Token invalid, logout
        get().logout()
        return false
      }
      
      const userData = JSON.parse(userStr)
      set({
        isAuthenticated: true,
        currentUser: userData,
        token: token,
        user: {
          name: userData.name,
          initials: userData.name.split(' ').map(n => n[0]).join(''),
          email: userData.email,
          role: userData.role
        }
      })
      return true
    } catch (error) {
      console.error('Auth check error:', error)
      get().logout()
      return false
    }
  },
  
  // View state
  currentView: 'dashboard',
  setCurrentView: (view) => set({ currentView: view }),
  currentProjectId: null,
  setCurrentProjectId: (id) => set({ currentProjectId: id }),
  navigateToProject: (id) => set({ currentView: 'project-details', currentProjectId: id }),
  navigateToProjects: () => set({ currentView: 'projects', currentProjectId: null }),
  currentPermitId: null,
  setCurrentPermitId: (id) => set({ currentPermitId: id }),
  navigateToPermit: (id) => set({ currentView: 'permit-details', currentPermitId: id }),
  navigateToPermits: () => set({ currentView: 'permits', currentPermitId: null }),
  currentClientId: null,
  setCurrentClientId: (id) => set({ currentClientId: id }),
  navigateToClient: (id) => set({ currentView: 'client-details', currentClientId: id }),
  navigateToClients: () => set({ currentView: 'clients', currentClientId: null }),
  // Filters for list views
  projectsFilter: null,
  setProjectsFilter: (filter) => set({ projectsFilter: filter }),
  permitsFilter: null,
  setPermitsFilter: (filter) => set({ permitsFilter: filter }),
  navigateToProjectsFiltered: (clientId) => set({ 
    currentView: 'projects', 
    projectsFilter: { clientId },
    currentProjectId: null 
  }),
  navigateToPermitsFiltered: (clientId) => set({ 
    currentView: 'permits', 
    permitsFilter: { clientId },
    currentPermitId: null 
  }),
  isMobileDrawerOpen: false,
  setMobileDrawerOpen: (isOpen) => set({ isMobileDrawerOpen: isOpen }),
  user: { name: 'User', initials: 'U', email: 'user@houserenovators.com' },
  connectionStatus: 'connected',
  setConnectionStatus: (status) => set({ connectionStatus: status }),
}))

export default useAppStore
