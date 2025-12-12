import DOMPurify from 'dompurify'

/**
 * Sanitization utilities for preventing XSS attacks
 * 
 * Usage:
 * - sanitizeInput(): For form inputs, removes all HTML tags
 * - sanitizeHtml(): For rich text, allows safe HTML tags
 * - sanitizeUrl(): For URLs, prevents javascript: and data: schemes
 */

/**
 * Sanitize user input by removing all HTML tags and scripts
 * Use for: text inputs, search queries, names, addresses, etc.
 * 
 * @param {string} input - Raw user input
 * @returns {string} - Sanitized plain text
 */
export const sanitizeInput = (input) => {
  if (!input || typeof input !== 'string') {
    return ''
  }
  
  // Remove all HTML tags and scripts
  return DOMPurify.sanitize(input, { 
    ALLOWED_TAGS: [], // No HTML tags allowed
    ALLOWED_ATTR: [] // No attributes allowed
  })
}

/**
 * Sanitize HTML content while allowing safe tags
 * Use for: rich text editors, markdown output, formatted content
 * 
 * @param {string} html - HTML content
 * @returns {string} - Sanitized HTML
 */
export const sanitizeHtml = (html) => {
  if (!html || typeof html !== 'string') {
    return ''
  }
  
  // Allow safe HTML tags and attributes
  return DOMPurify.sanitize(html, {
    ALLOWED_TAGS: [
      'p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
      'ul', 'ol', 'li', 'blockquote', 'code', 'pre', 'a', 'img'
    ],
    ALLOWED_ATTR: ['href', 'src', 'alt', 'title', 'target', 'rel']
  })
}

/**
 * Sanitize URLs to prevent XSS via javascript: or data: schemes
 * Use for: links, redirects, image sources
 * 
 * @param {string} url - URL to sanitize
 * @returns {string} - Sanitized URL or empty string if invalid
 */
export const sanitizeUrl = (url) => {
  if (!url || typeof url !== 'string') {
    return ''
  }
  
  const sanitized = DOMPurify.sanitize(url, { 
    ALLOWED_TAGS: [],
    ALLOWED_ATTR: []
  })
  
  // Check for dangerous protocols
  const dangerousProtocols = ['javascript:', 'data:', 'vbscript:']
  const lowerUrl = sanitized.toLowerCase().trim()
  
  for (const protocol of dangerousProtocols) {
    if (lowerUrl.startsWith(protocol)) {
      console.warn(`Blocked dangerous URL protocol: ${protocol}`)
      return ''
    }
  }
  
  return sanitized
}

/**
 * Sanitize an object's string values recursively
 * Use for: form data objects, API payloads with user input
 * 
 * @param {object} obj - Object with string values to sanitize
 * @returns {object} - Object with sanitized string values
 */
export const sanitizeObject = (obj) => {
  if (!obj || typeof obj !== 'object') {
    return obj
  }
  
  const sanitized = {}
  
  for (const [key, value] of Object.entries(obj)) {
    if (typeof value === 'string') {
      sanitized[key] = sanitizeInput(value)
    } else if (Array.isArray(value)) {
      sanitized[key] = value.map(item => 
        typeof item === 'string' ? sanitizeInput(item) : item
      )
    } else if (typeof value === 'object' && value !== null) {
      sanitized[key] = sanitizeObject(value)
    } else {
      sanitized[key] = value
    }
  }
  
  return sanitized
}

/**
 * Validate and sanitize email addresses
 * Use for: email inputs, contact forms
 * 
 * @param {string} email - Email address
 * @returns {string} - Sanitized email or empty string if invalid
 */
export const sanitizeEmail = (email) => {
  if (!email || typeof email !== 'string') {
    return ''
  }
  
  const sanitized = sanitizeInput(email).toLowerCase().trim()
  
  // Basic email validation
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(sanitized)) {
    return ''
  }
  
  return sanitized
}

/**
 * Validate and sanitize phone numbers
 * Use for: phone inputs, contact forms
 * 
 * @param {string} phone - Phone number
 * @returns {string} - Sanitized phone or empty string if invalid
 */
export const sanitizePhone = (phone) => {
  if (!phone || typeof phone !== 'string') {
    return ''
  }
  
  // Remove all non-numeric characters except + and -
  const sanitized = phone.replace(/[^0-9+\-() ]/g, '').trim()
  
  return sanitized
}

export default {
  sanitizeInput,
  sanitizeHtml,
  sanitizeUrl,
  sanitizeObject,
  sanitizeEmail,
  sanitizePhone
}
