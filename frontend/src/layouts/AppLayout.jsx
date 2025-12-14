import React from 'react';
import TopBar from '../components/TopBar';
import Sidebar from '../components/Sidebar';
import BottomNav from '../components/BottomNav';
import MobileDrawer from '../components/MobileDrawer';
import { useAppStore } from '../stores/appStore';

/**
 * AppLayout - Main application layout wrapper
 * Provides consistent structure: TopBar + Sidebar + Content + BottomNav
 * Eliminates repeated layout code across pages
 */
export default function AppLayout({ children }) {
  const isMobile = useAppStore((state) => state.isMobile);
  const drawerOpen = useAppStore((state) => state.drawerOpen);

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Top Navigation Bar */}
      <TopBar />

      {/* Main Content Area with Sidebar */}
      <div className="flex flex-1 overflow-hidden">
        {/* Desktop Sidebar - Only shows on screens >= 1024px (handled by Sidebar component) */}
        <Sidebar />

        {/* Main Content - Scrollable */}
        <main className="flex-1 overflow-y-auto bg-gray-50">
          {children}
        </main>
      </div>

      {/* Bottom Navigation - Mobile only */}
      {isMobile && <BottomNav />}

      {/* Mobile Drawer - Shows when opened on mobile/tablet (< 1024px) */}
      {drawerOpen && <MobileDrawer />}
    </div>
  );
}
