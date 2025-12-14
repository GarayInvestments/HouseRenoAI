# Frontend Backlog

**Version**: 1.0  
**Last Updated**: December 13, 2025  
**Status**: PLANNING (Deferred Items)

> **Purpose**: Tracking deferred Phase 5+ features and optional optimizations. These are not blocking production deployment but represent future enhancements.

---

## 🚧 Phase 5: New Pages (DEFERRED)

**Status**: Not started (0%)  
**Estimated Effort**: 48-60 hours total (8-10 hours per page)  
**Priority**: Medium (existing pages cover core functionality)  
**Blocking**: None (Phases 1-4 provide full CRUD for Clients, Projects, Permits)

### 5.1 Inspections Page

**Estimated Effort**: 8-10 hours  
**Priority**: Medium  
**Dependencies**: Phase F.2 backend endpoint (COMPLETE ✅)

**Features to Implement**:
- ✅ Backend API: `/v1/inspections` with JSONB photos/deficiencies (COMPLETE)
- ⏳ Frontend Page: `frontend/src/pages/Inspections.jsx`
- ⏳ Inspection List View: DataList component with photos/deficiencies summary
- ⏳ Inspection Details View: Full checklist, photo gallery, deficiency tracking
- ⏳ Photo Upload: Multi-photo upload with preview
- ⏳ Checklist UI: Interactive checklist with pass/fail/na states
- ⏳ Deficiency Form: Add/edit deficiencies with severity levels
- ⏳ Integration: Link to Projects (show inspections for project)

**Architecture Pattern** (Must follow Phase 3):
```javascript
// stores/inspectionsStore.js
const useInspectionsStore = create((set, get) => ({
  inspections: [],
  inspectionsCache: null,
  lastFetchedAt: null,
  fetchInspections: async () => { /* 5-min cache */ },
  createInspection: async (data) => { /* optimistic update */ },
  // ...
}));

// hooks/useInspections.js
export default function useInspections() {
  const { inspections, fetchInspections, loading, error } = useInspectionsStore();
  useEffect(() => { fetchInspections(); }, [fetchInspections]);
  return { inspections, loading, error };
}

// pages/Inspections.jsx
import AppLayout from '../components/layouts/AppLayout';
import DataList from '../components/DataList';
import useInspections from '../hooks/useInspections';

export default function Inspections() {
  const { inspections, loading, error } = useInspections();
  return (
    <AppLayout>
      <h1>Inspections</h1>
      <DataList
        data={inspections}
        loading={loading}
        error={error}
        columns={[
          { key: 'project', label: 'Project', render: (val) => val?.name },
          { key: 'inspector', label: 'Inspector' },
          { key: 'status', label: 'Status' },
          { key: 'photos', label: 'Photos', render: (val) => val?.length || 0 },
        ]}
        onRowClick={(inspection) => navigateToInspection(inspection.id)}
      />
    </AppLayout>
  );
}
```

**UI Components Needed**:
- `InspectionChecklist.jsx` - Interactive checklist with pass/fail toggles
- `PhotoGallery.jsx` - Grid of inspection photos with lightbox
- `DeficiencyList.jsx` - List of deficiencies with severity badges
- `PhotoUpload.jsx` - Multi-photo upload with drag-and-drop

---

### 5.2 Invoices Page

**Estimated Effort**: 10 hours  
**Priority**: High (revenue tracking)  
**Dependencies**: QuickBooks integration (COMPLETE ✅)

**Features to Implement**:
- ✅ Backend API: `/v1/quickbooks/invoices` (COMPLETE)
- ⏳ Frontend Page: `frontend/src/pages/Invoices.jsx`
- ⏳ Invoice List View: DataList with customer, amount, status, due date
- ⏳ Invoice Details View: Line items, payments, PDF export link
- ⏳ Create Invoice Form: Select customer, add line items, set due date
- ⏳ QuickBooks Sync: Real-time sync status, manual refresh button
- ⏳ Payment Tracking: Link to Payments page for invoice payments
- ⏳ PDF Export: Download invoice as PDF (QuickBooks PDF URL)

**Architecture Pattern**:
```javascript
// stores/invoicesStore.js (similar to projectsStore)

// hooks/useInvoices.js (thin adapter)

// pages/Invoices.jsx
<DataList
  data={invoices}
  columns={[
    { key: 'customer', label: 'Customer', render: (val) => val?.DisplayName },
    { key: 'TotalAmt', label: 'Amount', render: (val) => `$${val}` },
    { key: 'Balance', label: 'Balance', render: (val) => `$${val}` },
    { key: 'DueDate', label: 'Due Date', render: (val) => formatDate(val) },
  ]}
/>
```

**UI Components Needed**:
- `InvoiceForm.jsx` - Create/edit invoice with line items
- `LineItemEditor.jsx` - Add/remove/edit line items
- `InvoiceStatus.jsx` - Badge showing paid/unpaid/overdue
- `PDFViewer.jsx` - Embed QuickBooks PDF preview

---

### 5.3 Payments Page

**Estimated Effort**: 8-10 hours  
**Priority**: High (revenue tracking)  
**Dependencies**: Backend `/v1/payments` endpoint (COMPLETE ✅)

**Features to Implement**:
- ✅ Backend API: `/v1/payments` with QB sync (COMPLETE, Nov 10, 2025)
- ⏳ Frontend Page: `frontend/src/pages/Payments.jsx`
- ⏳ Payment List View: DataList with amount, date, invoice, method
- ⏳ Payment Timeline: Visual timeline of payments for a project/client
- ⏳ Payment Details: Linked invoice, receipt, notes
- ⏳ Create Payment Form: Select invoice, enter amount, payment method
- ⏳ QuickBooks Sync: Real-time sync status, manual refresh
- ⏳ Stripe Integration: (Optional) Connect Stripe for online payments

**Architecture Pattern**:
```javascript
// stores/paymentsStore.js

// hooks/usePayments.js

// pages/Payments.jsx
<DataList
  data={payments}
  columns={[
    { key: 'amount', label: 'Amount', render: (val) => `$${val}` },
    { key: 'payment_date', label: 'Date', render: (val) => formatDate(val) },
    { key: 'invoice', label: 'Invoice', render: (val) => val?.DocNumber },
    { key: 'payment_method', label: 'Method' },
  ]}
/>
```

**UI Components Needed**:
- `PaymentTimeline.jsx` - Visual timeline of payments
- `PaymentForm.jsx` - Create/edit payment
- `ReceiptViewer.jsx` - Show receipt (PDF or image)

---

### 5.4 Site Visits Page

**Estimated Effort**: 8 hours  
**Priority**: Medium (scheduling feature)  
**Dependencies**: Backend `/v1/site-visits` endpoint (NOT STARTED)

**Features to Implement**:
- ⏳ Backend API: `/v1/site-visits` (CRUD endpoints)
- ⏳ Frontend Page: `frontend/src/pages/SiteVisits.jsx`
- ⏳ Calendar View: Monthly calendar with site visits
- ⏳ List View: DataList with date, client, project, status
- ⏳ Check-In Feature: GPS location capture on mobile
- ⏳ Notes & Photos: Upload site photos, add visit notes
- ⏳ Integration: Link to Projects (show visits for project)

**Architecture Pattern**:
```javascript
// stores/siteVisitsStore.js

// hooks/useSiteVisits.js

// pages/SiteVisits.jsx
<DataList
  data={siteVisits}
  columns={[
    { key: 'scheduled_date', label: 'Date', render: (val) => formatDate(val) },
    { key: 'project', label: 'Project', render: (val) => val?.name },
    { key: 'status', label: 'Status' },
    { key: 'duration', label: 'Duration', render: (val) => `${val} hrs` },
  ]}
/>
```

**UI Components Needed**:
- `CalendarView.jsx` - Monthly calendar with events
- `CheckInButton.jsx` - GPS location capture
- `VisitNotes.jsx` - Rich text editor for notes
- `SitePhotos.jsx` - Photo upload and gallery

---

### 5.5 Users Page (Admin)

**Estimated Effort**: 8 hours  
**Priority**: Low (single user currently)  
**Dependencies**: Backend user management (NOT STARTED)

**Features to Implement**:
- ⏳ Backend API: `/v1/users` (CRUD endpoints, role management)
- ⏳ Frontend Page: `frontend/src/pages/Users.jsx`
- ⏳ User List View: DataList with name, email, role, last login
- ⏳ Create User Form: Email, role (admin/manager/worker)
- ⏳ Role Management: Assign permissions (view/edit/delete)
- ⏳ Invitations: Send email invite to new users
- ⏳ Integration: User activity logs (who created/edited what)

**Architecture Pattern**:
```javascript
// stores/usersStore.js

// hooks/useUsers.js

// pages/Users.jsx
<DataList
  data={users}
  columns={[
    { key: 'full_name', label: 'Name' },
    { key: 'email', label: 'Email' },
    { key: 'role', label: 'Role' },
    { key: 'last_login', label: 'Last Login', render: (val) => formatDate(val) },
  ]}
/>
```

**UI Components Needed**:
- `UserForm.jsx` - Create/edit user
- `RoleSelector.jsx` - Dropdown with role options
- `InviteModal.jsx` - Send email invitation
- `ActivityLog.jsx` - User activity timeline

---

### 5.6 Chat Page

**Estimated Effort**: 8 hours  
**Priority**: Low (AI chat feature)  
**Dependencies**: Backend `/v1/chat` endpoint (COMPLETE ✅)

**Features to Implement**:
- ✅ Backend API: `/v1/chat` with smart context loading (COMPLETE)
- ⏳ Frontend Page: `frontend/src/pages/Chat.jsx`
- ⏳ Chat Interface: Message list, input field, send button
- ⏳ Message History: Load previous messages from session
- ⏳ Typing Indicator: Show "AI is typing..." while waiting
- ⏳ Code Highlighting: Syntax highlighting for code blocks
- ⏳ Rich Content: Render tables, lists, links in messages
- ⏳ Mobile Support: Responsive chat interface

**Architecture Pattern**:
```javascript
// stores/chatStore.js
const useChatStore = create((set, get) => ({
  messages: [],
  sendMessage: async (message) => {
    // Optimistic update: add user message
    set(state => ({ messages: [...state.messages, { role: 'user', content: message }] }));
    
    // Send to backend
    const response = await apiClient.post('/v1/chat', { message });
    
    // Add AI response
    set(state => ({ messages: [...state.messages, { role: 'assistant', content: response.data.message }] }));
  },
}));

// hooks/useChat.js
export default function useChat() {
  const { messages, sendMessage, loading } = useChatStore();
  return { messages, sendMessage, loading };
}

// pages/Chat.jsx
export default function Chat() {
  const { messages, sendMessage, loading } = useChat();
  const [input, setInput] = useState('');
  
  const handleSend = () => {
    sendMessage(input);
    setInput('');
  };
  
  return (
    <AppLayout>
      <div className="chat-container">
        <div className="messages">
          {messages.map((msg, i) => (
            <div key={i} className={`message ${msg.role}`}>
              <Markdown>{msg.content}</Markdown>
            </div>
          ))}
          {loading && <div className="typing-indicator">AI is typing...</div>}
        </div>
        <div className="input-area">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Ask me anything..."
          />
          <button onClick={handleSend}>Send</button>
        </div>
      </div>
    </AppLayout>
  );
}
```

**UI Components Needed**:
- `MessageList.jsx` - Scrollable message history
- `MessageBubble.jsx` - User/AI message styling
- `TypingIndicator.jsx` - Animated "..." while loading
- `MarkdownRenderer.jsx` - Render markdown with syntax highlighting

---

## 🔧 Phase 6: Optional Optimizations (DEFERRED)

**Status**: Not started  
**Estimated Effort**: 20-30 hours total  
**Priority**: Low (performance is already acceptable)  
**Blocking**: None (Phases 1-4 provide solid performance)

### 6.1 Lazy Loading with React.lazy

**Estimated Effort**: 4-6 hours  
**Priority**: Low (initial bundle is ~500KB, acceptable)

**Implementation**:
```javascript
// App.jsx
import { lazy, Suspense } from 'react';
import LoadingSpinner from './components/LoadingSpinner';

const Clients = lazy(() => import('./pages/Clients'));
const Projects = lazy(() => import('./pages/Projects'));
const Permits = lazy(() => import('./pages/Permits'));

function App() {
  return (
    <Suspense fallback={<LoadingSpinner />}>
      <AppLayout>
        {currentView === 'clients' && <Clients />}
        {currentView === 'projects' && <Projects />}
        {/* ... */}
      </AppLayout>
    </Suspense>
  );
}
```

**Expected Benefits**:
- **Initial Bundle**: ~500KB → ~200KB (60% reduction)
- **Load Time**: 2s → 1s (faster initial load)
- **Trade-off**: Navigation delay (100-200ms per page load)

**Decision**: Deferred until bundle size becomes a problem (>1MB)

---

### 6.2 React Query Adoption

**Estimated Effort**: 8-10 hours  
**Priority**: Low (Zustand + 5-min cache works well)

**Rationale**:
- React Query provides server state management
- Features: automatic refetching, cache invalidation, optimistic updates
- Trade-off: Additional dependency, learning curve

**Current Solution**: Zustand stores with 5-min cache + optimistic updates (90% cache hit rate)

**Decision**: Deferred until caching logic becomes too complex

---

### 6.3 Additional Memoization

**Estimated Effort**: 4-6 hours  
**Priority**: Low (performance is already good)

**Potential Targets**:
- Large lists (1000+ items) with complex filtering
- Expensive computations (nested loops, calculations)
- Derived data that changes infrequently

**Current State**: Memoization applied to filtering operations in Projects and Permits pages

**Decision**: Deferred until profiling shows performance issues

---

### 6.4 DataList Adoption Across All Pages

**Estimated Effort**: 6-8 hours  
**Priority**: Low (most pages already use DataList)

**Remaining Pages** (not using DataList):
- ClientDetails.jsx (custom layout)
- ProjectDetails.jsx (custom layout)
- PermitDetails.jsx (custom layout)

**Decision**: Deferred - detail pages have unique layouts that don't fit DataList pattern

---

## 🎯 Prioritization Recommendations

**High Priority** (Do Next):
1. **Invoices Page** - Revenue tracking is critical
2. **Payments Page** - Complete revenue management
3. **Inspections Page** - Backend already complete

**Medium Priority** (Later):
4. **Site Visits Page** - Scheduling feature (requires backend work)
5. **Chat Page** - Backend complete, nice-to-have UI

**Low Priority** (Optional):
6. **Users Page** - Single user currently, not urgent
7. **Optional Optimizations** - Performance is already acceptable

---

## 📏 Architecture Requirements (CRITICAL)

**All Phase 5+ Pages MUST Follow Phase 3 Patterns**:

1. **Store Separation**: Create dedicated store (e.g., `inspectionsStore.js`)
2. **5-Minute Cache**: Implement cache with TTL
3. **Optimistic Updates**: Update UI immediately, rollback on error
4. **Custom Hook**: Create thin adapter hook (e.g., `useInspections.js`)
5. **Layout Abstraction**: Use `AppLayout` wrapper
6. **DataList Component**: Use for list views (loading/error/empty states)
7. **Error Handling**: Use `ErrorState` component
8. **Accessibility**: ARIA labels, keyboard nav, focus management

**Why This Matters**:
- **Consistency**: All pages behave identically
- **Maintainability**: Proven patterns, no experimentation
- **Performance**: 5-min cache reduces API load
- **UX**: Optimistic updates feel fast

**External Audit Requirement**:
> Phase 3 architecture is **LOCKED 🔒**. All new pages must follow established patterns. Any deviation requires architectural review and approval.

---

## 📊 Estimated Timeline (If Prioritized)

**Phase 5 (New Pages)**: 48-60 hours
- Inspections: 8-10 hours
- Invoices: 10 hours
- Payments: 8-10 hours
- Site Visits: 8 hours
- Users: 8 hours
- Chat: 8 hours

**Phase 6 (Optimizations)**: 20-30 hours
- Lazy Loading: 4-6 hours
- React Query: 8-10 hours
- Additional Memoization: 4-6 hours
- DataList Adoption: 6-8 hours

**Total Deferred Work**: 68-90 hours (~2-3 weeks full-time)

---

## 🔗 Related Documentation

- [`FRONTEND_IMPLEMENTATION_SUMMARY.md`](./FRONTEND_IMPLEMENTATION_SUMMARY.md) - Current status
- [`FRONTEND_ARCHITECTURE.md`](./FRONTEND_ARCHITECTURE.md) - Patterns to follow
- [`FRONTEND_AUDIT_LOG.md`](./FRONTEND_AUDIT_LOG.md) - Historical phases

**Last Updated**: December 13, 2025  
**Status**: PLANNING (Items pending prioritization)
