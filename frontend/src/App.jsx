import { useState, useEffect } from 'react';
import { useAppStore } from './stores/appStore';
import { useAuthStore } from './stores/authStore';
import LoadingScreen from './components/LoadingScreen';
import Sidebar from './components/Sidebar';
import TopBar from './components/TopBar';
import MobileDrawer from './components/MobileDrawer';
import BottomNav from './components/BottomNav';
import Dashboard from './pages/Dashboard';
import AIAssistant from './pages/AIAssistantNew';
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
import Login from './pages/Login';
import AuthConfirm from './pages/AuthConfirm';
import AuthResetPassword from './pages/AuthResetPassword';

function App() {
  const [isLoading, setIsLoading] = useState(true);
  const { currentView, currentProjectId, currentPermitId, currentClientId, setCurrentView } = useAppStore();
  const { initAuth, isAuthenticated } = useAuthStore();

  useEffect(() => {
    // Check authentication and URL path on initial load
    const initializeApp = async () => {
      const path = window.location.pathname;
      
      // Allow public pages without auth
      if (path === '/privacy') {
        setCurrentView('privacy');
        setIsLoading(false);
        return;
      } else if (path === '/terms') {
        setCurrentView('terms');
        setIsLoading(false);
        return;
      } else if (path === '/auth/confirm') {
        setCurrentView('auth-confirm');
        setIsLoading(false);
        return;
      } else if (path === '/auth/reset-password') {
        setCurrentView('auth-reset-password');
        setIsLoading(false);
        return;
      }
      
      // Initialize auth - validates session and restores user state
      const authenticated = await initAuth();
      
      if (!authenticated) {
        setCurrentView('login');
      }
      
      setIsLoading(false);
    };
    
    initializeApp();
  }, [setCurrentView, initAuth]);

  useEffect(() => {
    // Update URL when view changes (for privacy/terms/auth pages)
    if (currentView === 'privacy') {
      window.history.pushState({}, '', '/privacy');
    } else if (currentView === 'terms') {
      window.history.pushState({}, '', '/terms');
    } else if (currentView === 'auth-confirm') {
      // Keep URL with query params for auth callback
      if (!window.location.pathname.includes('/auth/confirm')) {
        window.history.pushState({}, '', '/auth/confirm' + window.location.search);
      }
    } else if (currentView === 'auth-reset-password') {
      // Keep URL with query params for password reset
      if (!window.location.pathname.includes('/auth/reset-password')) {
        window.history.pushState({}, '', '/auth/reset-password' + window.location.search);
      }
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
      case 'login':
        return <Login />;
      case 'auth-confirm':
        return <AuthConfirm />;
      case 'auth-reset-password':
        return <AuthResetPassword />;
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

  // Public pages (no sidebar/topbar)
  const isPublicPage = ['login', 'privacy', 'terms', 'auth-confirm', 'auth-reset-password'].includes(currentView);

  if (isPublicPage) {
    return renderContent();
  }

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
