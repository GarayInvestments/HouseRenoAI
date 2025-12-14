import { useState, useEffect } from 'react';
import { useAppStore } from './stores/appStore';
import { useAuthStore } from './stores/authStore';
import LoadingScreen from './components/LoadingScreen';
import AppLayout from './layouts/AppLayout';
import AuthLayout from './layouts/AuthLayout';
import Dashboard from './pages/Dashboard';
import AIAssistant from './pages/AIAssistantNew';
import Permits from './pages/Permits';
import PermitDetails from './pages/PermitDetails';
import Inspections from './pages/Inspections';
import InspectionDetails from './pages/InspectionDetails';
import Invoices from './pages/Invoices';
import InvoiceDetails from './pages/InvoiceDetails';
import Payments from './pages/Payments';
import SiteVisits from './pages/SiteVisits';
import SiteVisitDetails from './pages/SiteVisitDetails';
import Projects from './pages/Projects';
import ProjectDetails from './pages/ProjectDetails';
import Clients from './pages/Clients';
import ClientDetails from './pages/ClientDetails';
import LicensedBusinesses from './pages/LicensedBusinesses';
import Qualifiers from './pages/Qualifiers';
import OversightActions from './pages/OversightActions';
import Documents from './pages/Documents';
import Settings from './pages/Settings';
import PrivacyPolicy from './pages/PrivacyPolicy';
import TermsOfService from './pages/TermsOfService';
import Login from './pages/Login';
import AuthConfirm from './pages/AuthConfirm';
import AuthResetPassword from './pages/AuthResetPassword';

function App() {
  const [isLoading, setIsLoading] = useState(true);
  const { 
    currentView, 
    currentProjectId, 
    currentPermitId, 
    currentInspectionId, 
    currentInvoiceId, 
    currentSiteVisitId, 
    currentClientId,
    currentLicensedBusinessId,
    currentQualifierId,
    setCurrentView, 
    setIsMobile 
  } = useAppStore();
  const { initAuth, isAuthenticated } = useAuthStore();

  // Handle window resize for mobile detection
  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth <= 768);
    };
    
    // Set initial value
    handleResize();
    
    // Add listener
    window.addEventListener('resize', handleResize);
    
    // Cleanup
    return () => window.removeEventListener('resize', handleResize);
  }, [setIsMobile]);

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

    // If viewing inspection details
    if (currentView === 'inspection-details' && currentInspectionId) {
      return <InspectionDetails />;
    }

    // If viewing invoice details
    if (currentView === 'invoice-details' && currentInvoiceId) {
      return <InvoiceDetails />;
    }

    // If viewing site visit details
    if (currentView === 'site-visit-details' && currentSiteVisitId) {
      return <SiteVisitDetails />;
    }

    // If viewing client details
    if (currentView === 'client-details' && currentClientId) {
      return <ClientDetails />;
    }

    // Phase Q - Qualifier Compliance views
    if (currentView === 'licensed-business-details' && currentLicensedBusinessId) {
      // Detail view placeholder - for now just show list
      return <LicensedBusinesses />;
    }

    if (currentView === 'qualifier-details' && currentQualifierId) {
      // Detail view placeholder - for now just show list
      return <Qualifiers />;
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
      case 'inspections':
        return <Inspections />;
      case 'invoices':
        return <Invoices />;
      case 'payments':
        return <Payments />;
      case 'site-visits':
        return <SiteVisits />;
      case 'projects':
        return <Projects />;
      case 'clients':
        return <Clients />;
      case 'licensed-businesses':
        return <LicensedBusinesses />;
      case 'qualifiers':
        return <Qualifiers />;
      case 'oversight-actions':
        return <OversightActions />;
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

  // Public pages (no sidebar/topbar) - Use AuthLayout
  const isPublicPage = ['login', 'privacy', 'terms', 'auth-confirm', 'auth-reset-password'].includes(currentView);

  if (isPublicPage) {
    // Use AuthLayout for login/auth pages
    if (currentView === 'login' || currentView === 'auth-confirm' || currentView === 'auth-reset-password') {
      return <AuthLayout>{renderContent()}</AuthLayout>;
    }
    // No layout for privacy/terms (keep existing simple structure)
    return renderContent();
  }

  // Authenticated pages - Use AppLayout
  return <AppLayout>{renderContent()}</AppLayout>;
}

export default App;
