/**
 * ENUM Options for Dropdowns
 * These match the PostgreSQL ENUMs defined in the backend
 * Last updated: December 14, 2025
 */

// ============================================================================
// STATUS ENUMS (5 total)
// ============================================================================

export const CLIENT_STATUS_OPTIONS = [
  { value: 'INTAKE', label: 'Intake' },
  { value: 'ACTIVE', label: 'Active' },
  { value: 'ON_HOLD', label: 'On Hold' },
  { value: 'COMPLETED', label: 'Completed' },
  { value: 'ARCHIVED', label: 'Archived' }
];

export const PROJECT_STATUS_OPTIONS = [
  { value: 'INTAKE', label: 'Intake' },
  { value: 'PERMIT_UNDER_REVIEW', label: 'Permit Under Review' },
  { value: 'PERMIT_APPROVED', label: 'Permit Approved' },
  { value: 'INSPECTIONS_IN_PROGRESS', label: 'Inspections In Progress' },
  { value: 'PASSED_INSPECTIONS', label: 'Passed Inspections' },
  { value: 'COMPLETED', label: 'Completed' }
];

export const PERMIT_STATUS_OPTIONS = [
  { value: 'UNDER_REVIEW', label: 'Under Review' },
  { value: 'APPROVED', label: 'Approved' },
  { value: 'ISSUED', label: 'Issued' },
  { value: 'INSPECTION_SCHEDULED', label: 'Inspection Scheduled' },
  { value: 'INSPECTION_PASSED', label: 'Inspection Passed' },
  { value: 'CLOSED', label: 'Closed' },
  { value: 'EXPIRED', label: 'Expired' },
  { value: 'REJECTED', label: 'Rejected' },
  { value: 'REVOKED', label: 'Revoked' }
];

export const INVOICE_STATUS_OPTIONS = [
  { value: 'DRAFT', label: 'Draft' },
  { value: 'SENT', label: 'Sent' },
  { value: 'VIEWED', label: 'Viewed' },
  { value: 'PARTIAL', label: 'Partial' },
  { value: 'PAID', label: 'Paid' },
  { value: 'VOID', label: 'Void' }
];

export const PAYMENT_STATUS_OPTIONS = [
  { value: 'PENDING', label: 'Pending' },
  { value: 'POSTED', label: 'Posted' },
  { value: 'FAILED', label: 'Failed' },
  { value: 'REFUNDED', label: 'Refunded' }
];

// ============================================================================
// TYPE ENUMS (5 total)
// ============================================================================

export const PERMIT_TYPE_OPTIONS = [
  { value: 'BUILDING', label: 'Building' },
  { value: 'ELECTRICAL', label: 'Electrical' },
  { value: 'PLUMBING', label: 'Plumbing' },
  { value: 'MECHANICAL', label: 'Mechanical' },
  { value: 'ZONING', label: 'Zoning' },
  { value: 'FIRE', label: 'Fire' },
  { value: 'ENVIRONMENTAL', label: 'Environmental' },
  { value: 'OTHER', label: 'Other' }
];

export const PROJECT_TYPE_OPTIONS = [
  { value: 'NEW_CONSTRUCTION', label: 'New Construction' },
  { value: 'RENOVATION', label: 'Renovation' },
  { value: 'REMODEL', label: 'Remodel' },
  { value: 'ADDITION', label: 'Addition' },
  { value: 'RESIDENTIAL', label: 'Residential' },
  { value: 'COMMERCIAL', label: 'Commercial' },
  { value: 'OTHER', label: 'Other' }
];

export const LICENSE_TYPE_OPTIONS = [
  { value: 'GENERAL_CONTRACTOR', label: 'General Contractor' },
  { value: 'ELECTRICAL', label: 'Electrical' },
  { value: 'PLUMBING', label: 'Plumbing' },
  { value: 'MECHANICAL', label: 'Mechanical' },
  { value: 'SPECIALTY', label: 'Specialty' }
];

export const LICENSE_STATUS_OPTIONS = [
  { value: 'ACTIVE', label: 'Active' },
  { value: 'INACTIVE', label: 'Inactive' },
  { value: 'SUSPENDED', label: 'Suspended' },
  { value: 'REVOKED', label: 'Revoked' }
];

export const ACTION_TYPE_OPTIONS = [
  { value: 'SITE_VISIT', label: 'Site Visit' },
  { value: 'PLAN_REVIEW', label: 'Plan Review' },
  { value: 'PERMIT_REVIEW', label: 'Permit Review' },
  { value: 'CLIENT_MEETING', label: 'Client Meeting' },
  { value: 'INSPECTION_ATTENDANCE', label: 'Inspection Attendance' },
  { value: 'PHONE_CONSULTATION', label: 'Phone Consultation' }
];

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

/**
 * Convert ENUM value to display label
 * Example: "PERMIT_UNDER_REVIEW" -> "Permit Under Review"
 */
export function formatEnumLabel(value) {
  if (!value) return '';
  return value
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ');
}

/**
 * Get label for a specific enum value from options array
 */
export function getEnumLabel(value, options) {
  if (!value) return '';
  const option = options.find(opt => opt.value === value);
  return option ? option.label : formatEnumLabel(value);
}
