import { create } from 'zustand'

export const useAppStore = create((set) => ({
  currentView: 'dashboard',
  setCurrentView: (view) => set({ currentView: view }),
  isMobileDrawerOpen: false,
  setMobileDrawerOpen: (isOpen) => set({ isMobileDrawerOpen: isOpen }),
  user: { name: 'User', initials: 'U', email: 'user@houserenovators.com' },
  connectionStatus: 'connected',
  setConnectionStatus: (status) => set({ connectionStatus: status }),
}))
