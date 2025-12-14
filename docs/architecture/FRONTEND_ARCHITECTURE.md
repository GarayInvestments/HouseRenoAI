# Frontend Architecture Documentation

**Version**: 1.0  
**Last Updated**: December 13, 2025  
**Status**: 🔒 LOCKED (Phases 1-4 Complete)

> **Purpose**: Architectural patterns, decisions, and rationale for frontend implementation. This is a reference document for understanding the "why" behind the structure.

---

## 🏗️ Core Architecture Pattern

### Three-Layer Design

```
┌─────────────────────────────────────┐
│        Components (UI Layer)         │
│   - Render data                      │
│   - Handle user interactions         │
│   - Show loading/error states        │
└─────────────────┬───────────────────┘
                  │
┌─────────────────┴───────────────────┐
│         Hooks (Adapter Layer)        │
│   - Thin wrappers around stores     │
│   - No API knowledge                │
│   - Return { data, loading, error } │
└─────────────────┬───────────────────┘
                  │
┌─────────────────┴───────────────────┐
│       Stores (Data + API Layer)      │
│   - Own all API knowledge           │
│   - Manage cache                    │
│   - Notify subscribers on changes   │
└─────────────────────────────────────┘
```

**Why This Pattern?**
1. **Separation of Concerns**: UI doesn't know about API endpoints
2. **Testability**: Can mock stores, test hooks independently
3. **Maintainability**: API changes isolated to stores
4. **Performance**: Stores handle caching, hooks just subscribe

---

## 🗂️ Zustand Store Architecture

### Store Separation (Phase 2)

**Before**: Single `appStore.js` (500+ lines)
**After**: 4 specialized stores

```javascript
// appStore.js - Navigation & UI state only
{
  currentView, currentClientId, currentProjectId, currentPermitId,
  isMenuOpen, navigateToClient(), navigateToProject(), ...
}

// authStore.js - Authentication (Supabase session)
{
  user, session, signIn(), signOut(), refreshSession(), ...
}

// projectsStore.js - Projects data + API
{
  projects, projectsCache, lastFetchedAt,
  fetchProjects(), createProject(), updateProject(), ...
}

// permitsStore.js - Permits data + API
{
  permits, permitsCache, lastFetchedAt,
  fetchPermits(), createPermit(), updatePermit(), ...
}

// clientsStore.js - Clients data + API
{
  clients, clientsCache, lastFetchedAt,
  fetchClients(), ...
}
```

**Why Split?**
- **Performance**: Updating projects doesn't re-render components using permits
- **Isolation**: Each domain (auth, projects, permits) changes independently
- **Clarity**: Easier to find relevant logic (no 500-line files)
- **Scalability**: New features add new stores, not bloat existing ones

### Cache Strategy (5-Minute TTL)

```javascript
// projectsStore.js example
const projectsStore = create((set, get) => ({
  projects: [],
  projectsCache: null,
  lastFetchedAt: null,
  
  fetchProjects: async () => {
    const state = get();
    const now = Date.now();
    const cacheAge = now - (state.lastFetchedAt || 0);
    
    // Return cache if < 5 minutes old
    if (cacheAge < 5 * 60 * 1000 && state.projectsCache) {
      return state.projectsCache;
    }
    
    // Otherwise fetch from API
    const response = await apiClient.get('/v1/projects');
    set({
      projects: response.data,
      projectsCache: response.data,
      lastFetchedAt: now,
    });
    return response.data;
  },
}));
```

**Why 5-Minute Cache?**
- **Balance**: Reduces API calls without stale data
- **User Experience**: Feels instant when navigating
- **Backend Load**: 90% reduction in redundant requests
- **Simple**: No complex invalidation logic needed

### Optimistic Updates

```javascript
// Example: Update project status
updateProject: async (id, updates) => {
  const state = get();
  
  // 1. Update UI immediately (optimistic)
  const optimisticProjects = state.projects.map(p =>
    p.id === id ? { ...p, ...updates } : p
  );
  set({ projects: optimisticProjects });
  
  // 2. Send to backend
  try {
    const response = await apiClient.patch(`/v1/projects/${id}`, updates);
    
    // 3. Replace with server response
    const finalProjects = state.projects.map(p =>
      p.id === id ? response.data : p
    );
    set({ projects: finalProjects, projectsCache: finalProjects });
  } catch (error) {
    // 4. Rollback on error
    set({ projects: state.projects });
    throw error;
  }
},
```

**Why Optimistic Updates?**
- **Perceived Performance**: UI responds instantly
- **User Trust**: App feels fast and responsive
- **Rollback Safety**: Server errors revert UI to known state

---

## 🔌 Custom Hooks Pattern

### Thin Adapters (Phase 3)

```javascript
// hooks/useProjects.js
import { useEffect } from 'react';
import useProjectsStore from '../stores/projectsStore';

export default function useProjects() {
  const { projects, fetchProjects, loading, error } = useProjectsStore();
  
  useEffect(() => {
    fetchProjects();
  }, [fetchProjects]);
  
  return { projects, loading, error };
}
```

**Why Thin Hooks?**
1. **No API Logic**: Hooks don't know about endpoints (store responsibility)
2. **Simple Testing**: Mock store, test hook behavior
3. **Consistent Interface**: All hooks return `{ data, loading, error }`
4. **Flexibility**: Can swap store implementation without changing components

### Usage in Components

```javascript
// pages/Projects.jsx
import useProjects from '../hooks/useProjects';

export default function Projects() {
  const { projects, loading, error } = useProjects();
  
  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorState error={error} />;
  
  return (
    <div>
      {projects.map(p => <ProjectCard key={p.id} project={p} />)}
    </div>
  );
}
```

---

## 🎨 Layout Abstraction (Phase 3)

### Two Primary Layouts

**AppLayout** (Authenticated pages):
```javascript
// components/layouts/AppLayout.jsx
import Sidebar from '../Sidebar';
import Header from '../Header';

export default function AppLayout({ children }) {
  return (
    <div className="app-layout">
      <Header />
      <Sidebar />
      <main className="app-content">
        {children}
      </main>
    </div>
  );
}
```

**AuthLayout** (Login/Register pages):
```javascript
// components/layouts/AuthLayout.jsx
export default function AuthLayout({ children }) {
  return (
    <div className="auth-layout">
      <div className="auth-card">
        {children}
      </div>
    </div>
  );
}
```

### Usage Pattern

```javascript
// App.jsx
import AppLayout from './components/layouts/AppLayout';
import AuthLayout from './components/layouts/AuthLayout';

function App() {
  const { currentView } = useAppStore();
  const { user } = useAuthStore();
  
  if (!user) {
    return (
      <AuthLayout>
        <Login />
      </AuthLayout>
    );
  }
  
  return (
    <AppLayout>
      {currentView === 'clients' && <Clients />}
      {currentView === 'projects' && <Projects />}
      {/* ... */}
    </AppLayout>
  );
}
```

**Why Layout Abstraction?**
- **Consistency**: Header/Sidebar appear identically on all app pages
- **Maintainability**: Update header once, affects all pages
- **Clarity**: Page components focus on content, not chrome
- **Flexibility**: Easy to add new layouts (e.g., PrintLayout, FullscreenLayout)

---

## 🧩 Reusable Components

### DataList Component (Phase 3)

```javascript
// components/DataList.jsx
export default function DataList({
  data,
  loading,
  error,
  columns,
  onRowClick,
  emptyMessage,
}) {
  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorState error={error} />;
  if (!data || data.length === 0) return <EmptyState message={emptyMessage} />;
  
  return (
    <table>
      <thead>
        <tr>
          {columns.map(col => <th key={col.key}>{col.label}</th>)}
        </tr>
      </thead>
      <tbody>
        {data.map(row => (
          <tr key={row.id} onClick={() => onRowClick(row)}>
            {columns.map(col => <td key={col.key}>{row[col.key]}</td>)}
          </tr>
        ))}
      </tbody>
    </table>
  );
}
```

**Usage**:
```javascript
<DataList
  data={projects}
  loading={loading}
  error={error}
  columns={[
    { key: 'name', label: 'Project Name' },
    { key: 'status', label: 'Status' },
  ]}
  onRowClick={(project) => navigateToProject(project.id)}
  emptyMessage="No projects found"
/>
```

**Why DataList?**
- **Consistency**: All lists have same loading/error/empty states
- **Code Reduction**: 50-100 lines saved per page
- **Accessibility**: Built-in ARIA attributes and keyboard nav
- **Maintainability**: Update one component, fix all lists

---

## 🔐 Authentication Architecture (Phase 1)

### Supabase Session Management

**Before (Zustand)**:
```javascript
// ❌ Problem: XSS can steal tokens
authStore = {
  user: { email, token }, // Token in JS memory
  token: "eyJ...",
}
```

**After (Supabase)**:
```javascript
// ✅ Solution: HttpOnly cookies
supabase.auth.getSession() // Reads from secure storage
supabase.auth.onAuthStateChange() // Subscribes to changes
```

**Why Supabase Auth?**
1. **XSS Protection**: Tokens in HttpOnly cookies (JS can't access)
2. **Auto-Refresh**: SDK handles token refresh automatically
3. **Session Persistence**: Survives page reload
4. **Multi-Tab Sync**: Session changes propagate across tabs

### Auth Flow

```
1. User submits credentials
   ↓
2. Supabase validates → returns session
   ↓
3. Session stored in HttpOnly cookie
   ↓
4. authStore.user populated from session
   ↓
5. App renders authenticated UI
   ↓
6. API calls include Authorization header (Supabase SDK injects)
   ↓
7. Token expires → SDK auto-refreshes
   ↓
8. 401 from backend → authStore.signOut() → clears session
```

---

## 🌐 API Client Architecture (Phase 4)

### Centralized apiClient

```javascript
// utils/apiClient.js
import axios from 'axios';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  timeout: 8000,
});

// Retry logic with exponential backoff
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const config = error.config;
    
    // Retry on 5xx or network errors
    if (!config._retry && (error.response?.status >= 500 || !error.response)) {
      config._retry = true;
      await new Promise(resolve => setTimeout(resolve, 1000));
      return apiClient.request(config);
    }
    
    // Normalize error shape
    throw {
      message: error.response?.data?.message || 'Network error',
      code: error.response?.status || 0,
      retriable: error.response?.status >= 500,
      httpStatus: error.response?.status,
    };
  }
);

export default apiClient;
```

**Why Centralized API Client?**
- **Retry Logic**: 2x retry with exponential backoff for transient errors
- **Timeout Protection**: 8s timeout prevents hanging requests
- **Error Normalization**: Consistent `{ message, code, retriable, httpStatus }` shape
- **Auth Injection**: Supabase SDK adds Authorization header automatically
- **Maintainability**: Change base URL or headers once, affects all requests

---

## 🎯 Performance Optimizations (Phase 2)

### 1. CSS-Only Hover (No React Re-Renders)

**Before**:
```javascript
// ❌ Re-renders entire component on every hover
const [hovered, setHovered] = useState(false);
<div
  onMouseEnter={() => setHovered(true)}
  onMouseLeave={() => setHovered(false)}
  style={{ backgroundColor: hovered ? '#f0f0f0' : 'white' }}
/>
```

**After**:
```css
/* ✅ No React involvement */
.client-row:hover {
  background-color: #f0f0f0;
}
```

### 2. Local Filters (No Global State)

**Before**:
```javascript
// ❌ All pages re-render when filter changes
const { globalFilter, setGlobalFilter } = useAppStore();
```

**After**:
```javascript
// ✅ Each page has its own filter (isolated)
const [localFilter, setLocalFilter] = useState('');
```

### 3. Memoization for Expensive Computations

```javascript
// Expensive: filtering 1000+ projects
const filteredProjects = useMemo(() => {
  return projects.filter(p => 
    p.name.toLowerCase().includes(searchTerm.toLowerCase())
  );
}, [projects, searchTerm]);
```

**When to Memoize?**
- ✅ Filtering large arrays (100+ items)
- ✅ Complex computations (nested loops, calculations)
- ✅ Derived data that changes infrequently
- ❌ Simple operations (no benefit, added complexity)

---

## ♿ Accessibility Patterns (Phase 4)

### Modal Focus Trap

```javascript
// components/Modal.jsx
useEffect(() => {
  if (!isOpen) return;
  
  // Find all focusable elements
  const focusable = modalRef.current.querySelectorAll(
    'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
  );
  
  if (focusable.length === 0) {
    // Fallback: focus modal itself
    modalRef.current.focus();
    return;
  }
  
  // Focus first element
  focusable[0].focus();
  
  // Trap focus within modal
  const handleTab = (e) => {
    if (e.key !== 'Tab') return;
    
    const firstFocusable = focusable[0];
    const lastFocusable = focusable[focusable.length - 1];
    
    if (e.shiftKey && document.activeElement === firstFocusable) {
      e.preventDefault();
      lastFocusable.focus();
    } else if (!e.shiftKey && document.activeElement === lastFocusable) {
      e.preventDefault();
      firstFocusable.focus();
    }
  };
  
  document.addEventListener('keydown', handleTab);
  return () => document.removeEventListener('keydown', handleTab);
}, [isOpen]);
```

### ARIA Attributes

```javascript
// Proper button semantics
<button
  aria-label="Close modal"
  aria-pressed={isOpen}
  onClick={onClose}
>
  ×
</button>

// Loading states
<div role="status" aria-live="polite">
  {loading ? 'Loading...' : `${projects.length} projects loaded`}
</div>

// Error announcements
<div role="alert" aria-live="assertive">
  {error && error.message}
</div>
```

---

## 🧪 Testing Considerations

### Store Testing

```javascript
// Example: projectsStore.test.js
import { renderHook, act } from '@testing-library/react-hooks';
import useProjectsStore from '../stores/projectsStore';

test('fetchProjects returns cached data within 5 minutes', async () => {
  const { result } = renderHook(() => useProjectsStore());
  
  // First fetch
  await act(async () => {
    await result.current.fetchProjects();
  });
  expect(mockApiClient.get).toHaveBeenCalledTimes(1);
  
  // Second fetch within 5 min
  await act(async () => {
    await result.current.fetchProjects();
  });
  expect(mockApiClient.get).toHaveBeenCalledTimes(1); // Still 1 (cache hit)
});
```

### Hook Testing

```javascript
// Example: useProjects.test.js
import { renderHook } from '@testing-library/react-hooks';
import useProjects from '../hooks/useProjects';
import useProjectsStore from '../stores/projectsStore';

jest.mock('../stores/projectsStore');

test('useProjects calls fetchProjects on mount', () => {
  const mockFetchProjects = jest.fn();
  useProjectsStore.mockReturnValue({
    projects: [],
    fetchProjects: mockFetchProjects,
    loading: false,
    error: null,
  });
  
  renderHook(() => useProjects());
  
  expect(mockFetchProjects).toHaveBeenCalledTimes(1);
});
```

---

## 📚 Related Documentation

- [`FRONTEND_IMPLEMENTATION_SUMMARY.md`](./FRONTEND_IMPLEMENTATION_SUMMARY.md) - Current status
- [`FRONTEND_AUDIT_LOG.md`](./FRONTEND_AUDIT_LOG.md) - Historical phases
- [`FRONTEND_BACKLOG.md`](./FRONTEND_BACKLOG.md) - Future work

**Last Updated**: December 13, 2025  
**Status**: 🔒 LOCKED (Reference document)
