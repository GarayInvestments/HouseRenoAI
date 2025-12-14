import { create } from 'zustand'

/**
 * UI State Store
 * Handles navigation, view state, and UI preferences
 * 
 * Note: Auth state moved to authStore.js for better security
 */

const API_URL = import.meta.env.VITE_API_URL || 'https://api.houserenovatorsllc.com'

export const useAppStore = create((set, get) => ({
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
  
  // Mobile UI
  isMobile: window.innerWidth <= 768,
  drawerOpen: false,
  setIsMobile: (isMobile) => set({ isMobile }),
  setDrawerOpen: (isOpen) => set({ drawerOpen: isOpen }),
  toggleDrawer: () => set((state) => ({ drawerOpen: !state.drawerOpen })),
  // Legacy - kept for compatibility
  isMobileDrawerOpen: false,
  setMobileDrawerOpen: (isOpen) => set({ isMobileDrawerOpen: isOpen }),
  user: { name: 'User', initials: 'U', email: 'user@houserenovators.com' },
  connectionStatus: 'connected',
  setConnectionStatus: (status) => set({ connectionStatus: status }),
}))

export default useAppStore
