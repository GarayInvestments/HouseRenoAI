import { useState, useEffect } from 'react';
import { useAppStore } from './stores/appStore';
import LoadingScreen from './components/LoadingScreen';
import Sidebar from './components/Sidebar';
import TopBar from './components/TopBar';
import MobileDrawer from './components/MobileDrawer';
import BottomNav from './components/BottomNav';
import Dashboard from './pages/Dashboard';
import AIAssistant from './pages/AIAssistant';
import Permits from './pages/Permits';
import PermitDetails from './pages/PermitDetails';
import Projects from './pages/Projects';
import ProjectDetails from './pages/ProjectDetails';
import Clients from './pages/Clients';
import ClientDetails from './pages/ClientDetails';
import Documents from './pages/Documents';
import Settings from './pages/Settings';
import PrivacyPolicy from './pages/PrivacyPolicy';
import TermsOfService from './pages/TermsOfService';

function App() {
  const [isLoading, setIsLoading] = useState(true);
  const { currentView, currentProjectId, currentPermitId, currentClientId, setCurrentView } = useAppStore();

  useEffect(() => {
    // Check URL path on initial load
    const path = window.location.pathname;
    
    if (path === '/privacy') {
      setCurrentView('privacy');
    } else if (path === '/terms') {
      setCurrentView('terms');
    }
    
    // Simulate initial load
    setTimeout(() => setIsLoading(false), 1500);
  }, [setCurrentView]);

  useEffect(() => {
    // Update URL when view changes (for privacy/terms pages)
    if (currentView === 'privacy') {
      window.history.pushState({}, '', '/privacy');
    } else if (currentView === 'terms') {
      window.history.pushState({}, '', '/terms');
    } else if (window.location.pathname !== '/') {
      // Return to home for other views
      window.history.pushState({}, '', '/');
    }
  }, [currentView]);

  if (isLoading) {
    return <LoadingScreen />;
  }

  const renderContent = () => {
    // If viewing project details
    if (currentView === 'project-details' && currentProjectId) {
      return <ProjectDetails />;
    }

    // If viewing permit details
    if (currentView === 'permit-details' && currentPermitId) {
      return <PermitDetails />;
    }

    // If viewing client details
    if (currentView === 'client-details' && currentClientId) {
      return <ClientDetails />;
    }

    switch (currentView) {
      case 'dashboard':
        return <Dashboard />;
      case 'ai-assistant':
        return <AIAssistant />;
      case 'permits':
        return <Permits />;
      case 'projects':
        return <Projects />;
      case 'clients':
        return <Clients />;
      case 'documents':
        return <Documents />;
      case 'settings':
        return <Settings />;
      case 'privacy':
        return <PrivacyPolicy />;
      case 'terms':
        return <TermsOfService />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Sidebar - Desktop */}
      <Sidebar />

      {/* Mobile Drawer */}
      <MobileDrawer />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col overflow-hidden bg-gray-50">
        {/* Top Bar */}
        <TopBar />

        {/* Page Content */}
        <main className="flex-1 overflow-y-auto">
          {renderContent()}
        </main>

        {/* Bottom Navigation - Mobile Only */}
        <BottomNav />
      </div>
    </div>
  );
}

export default App;
