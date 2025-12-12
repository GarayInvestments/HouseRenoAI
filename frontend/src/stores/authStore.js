import { create } from 'zustand'
import { supabase, signIn as supabaseSignIn, signOut, getUserProfile } from '../lib/supabase'

/**
 * Secure Authentication Store
 * 
 * Security improvements:
 * - No token storage in Zustand (XSS protection)
 * - Session managed by Supabase client
 * - Automatic session validation on app load
 * - Refresh token lifecycle handled by Supabase
 */

export const useAuthStore = create((set, get) => ({
  // Auth state
  isAuthenticated: false,
  currentUser: null,
  session: null, // Track session but not token
  loading: true,
  error: null,

  /**
   * Initialize auth - Call on app mount
   * Validates existing session and restores user state
   */
  initAuth: async () => {
    try {
      set({ loading: true, error: null })
      
      // Get session from Supabase (handles refresh automatically)
      const { data: { session }, error: sessionError } = await supabase.auth.getSession()
      
      if (sessionError || !session) {
        set({ 
          isAuthenticated: false, 
          currentUser: null, 
          session: null,
          loading: false 
        })
        return false
      }
      
      // Get user profile from backend
      const { profile, error: profileError } = await getUserProfile()
      
      if (profileError || !profile) {
        await get().logout()
        return false
      }
      
      set({
        isAuthenticated: true,
        currentUser: profile,
        session: session, // Store session object, not just token
        loading: false,
        error: null
      })
      
      return true
    } catch (error) {
      console.error('Auth initialization error:', error)
      set({ 
        loading: false, 
        error: error.message,
        isAuthenticated: false
      })
      return false
    }
  },

  /**
   * Login with email and password
   */
  login: async (email, password) => {
    try {
      set({ loading: true, error: null })
      
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
      
      set({
        isAuthenticated: true,
        currentUser: profile,
        session: session,
        loading: false,
        error: null
      })
      
      return { success: true, profile }
    } catch (error) {
      console.error('Login error:', error)
      set({ 
        loading: false, 
        error: error.message,
        isAuthenticated: false
      })
      throw error
    }
  },

  /**
   * Logout and clear all auth state
   */
  logout: async () => {
    try {
      // Sign out from Supabase
      await signOut()
      
      // Clear local storage (if any custom data stored)
      localStorage.removeItem('user')
      
      set({
        isAuthenticated: false,
        currentUser: null,
        session: null,
        loading: false,
        error: null
      })
    } catch (error) {
      console.error('Logout error:', error)
      // Force clear state even if logout fails
      set({
        isAuthenticated: false,
        currentUser: null,
        session: null,
        loading: false,
        error: null
      })
    }
  },

  /**
   * Check if current session is valid
   * Useful for protected routes
   */
  checkAuth: async () => {
    try {
      // Check Supabase session
      const { data: { session }, error } = await supabase.auth.getSession()
      
      if (error || !session) {
        set({ 
          isAuthenticated: false, 
          currentUser: null,
          session: null
        })
        return false
      }
      
      // Verify user profile still exists
      const { profile, error: profileError } = await getUserProfile()
      
      if (profileError || !profile) {
        await get().logout()
        return false
      }
      
      set({
        isAuthenticated: true,
        currentUser: profile,
        session: session
      })
      
      return true
    } catch (error) {
      console.error('Auth check error:', error)
      await get().logout()
      return false
    }
  },

  /**
   * Get current access token for API calls
   * Automatically refreshes if expired
   */
  getAccessToken: async () => {
    try {
      const { data: { session }, error } = await supabase.auth.getSession()
      
      if (error || !session) {
        return null
      }
      
      return session.access_token
    } catch (error) {
      console.error('Error getting access token:', error)
      return null
    }
  },

  /**
   * Update current user profile
   * Call after profile updates
   */
  updateUserProfile: (profile) => {
    set({ currentUser: profile })
  },

  /**
   * Clear error state
   */
  clearError: () => {
    set({ error: null })
  }
}))

export default useAuthStore
