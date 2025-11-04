import { create } from 'zustand'

export const useAppStore = create((set) => ({
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
