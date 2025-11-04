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

function App() {
  const [isLoading, setIsLoading] = useState(true);
  const { currentView, currentProjectId, currentPermitId, currentClientId } = useAppStore();

  useEffect(() => {
    // Simulate initial load
    setTimeout(() => setIsLoading(false), 1500);
  }, []);

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
