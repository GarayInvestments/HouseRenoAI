import { create } from 'zustand'
import { supabase, signIn as supabaseSignIn, signOut, getUserProfile } from '../lib/supabase'

const API_URL = import.meta.env.VITE_API_URL || 'https://api.houserenovatorsllc.com'

export const useAppStore = create((set, get) => ({
  // Authentication state
  isAuthenticated: false,
  currentUser: null,
  token: null,
  
  // Auth actions
  login: async (email, password) => {
    try {
      // Sign in with Supabase
      const { user, session, error } = await supabaseSignIn(email, password)
      
      if (error) {
        throw new Error(error.message || 'Login failed')
      }
      
      if (!user || !session) {
        throw new Error('No session returned')
      }
      
      // Get user profile from backend
      const { profile, error: profileError } = await getUserProfile()
      
      if (profileError) {
        throw new Error('Failed to load user profile')
      }
      
      // Store session
      localStorage.setItem('supabase_session', JSON.stringify(session))
      localStorage.setItem('user', JSON.stringify(profile))
      
      set({
        isAuthenticated: true,
        currentUser: profile,
        token: session.access_token,
        user: {
          name: profile.full_name || profile.email,
          initials: (profile.full_name || profile.email).split(' ').map(n => n[0]).join(''),
          email: profile.email,
          role: profile.role
        },
        currentView: 'dashboard'
      })
    } catch (error) {
      console.error('Login error:', error)
      throw error
    }
  },
  
  logout: async () => {
    // Sign out from Supabase
    await signOut()
    
    localStorage.removeItem('supabase_session')
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
    try {
      // Check Supabase session
      const { data: { session }, error } = await supabase.auth.getSession()
      
      if (error || !session) {
        set({ currentView: 'login', isAuthenticated: false })
        return false
      }
      
      // Get user profile from backend
      const { profile, error: profileError } = await getUserProfile()
      
      if (profileError || !profile) {
        get().logout()
        return false
      }
      
      set({
        isAuthenticated: true,
        currentUser: profile,
        token: session.access_token,
        user: {
          name: profile.full_name || profile.email,
          initials: (profile.full_name || profile.email).split(' ').map(n => n[0]).join(''),
          email: profile.email,
          role: profile.role
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
