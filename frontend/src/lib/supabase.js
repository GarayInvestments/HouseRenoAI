import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error('Missing Supabase environment variables. Please set VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY')
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: true
  }
})

/**
 * Get current user session
 * @returns {Promise<{user: object|null, session: object|null}>}
 */
export async function getCurrentUser() {
  const { data: { session }, error } = await supabase.auth.getSession()
  if (error) {
    console.error('Error getting session:', error)
    return { user: null, session: null }
  }
  return { user: session?.user ?? null, session }
}

/**
 * Sign in with email and password
 * @param {string} email 
 * @param {string} password 
 * @returns {Promise<{user: object|null, session: object|null, error: object|null}>}
 */
export async function signIn(email, password) {
  const { data, error } = await supabase.auth.signInWithPassword({
    email,
    password,
  })
  
  if (error) {
    console.error('Sign in error:', error)
    return { user: null, session: null, error }
  }
  
  return { user: data.user, session: data.session, error: null }
}

/**
 * Sign out current user
 * @returns {Promise<{error: object|null}>}
 */
export async function signOut() {
  const { error } = await supabase.auth.signOut()
  if (error) {
    console.error('Sign out error:', error)
  }
  return { error }
}

/**
 * Get user profile from backend API
 * @returns {Promise<{profile: object|null, error: object|null}>}
 */
export async function getUserProfile() {
  const { data: { session } } = await supabase.auth.getSession()
  
  if (!session) {
    return { profile: null, error: { message: 'No active session' } }
  }

  try {
    const response = await fetch(`${import.meta.env.VITE_API_URL}/v1/auth/supabase/me`, {
      headers: {
        'Authorization': `Bearer ${session.access_token}`
      }
    })

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }

    const profile = await response.json()
    return { profile, error: null }
  } catch (error) {
    console.error('Error fetching user profile:', error)
    return { profile: null, error }
  }
}

/**
 * Listen to auth state changes
 * @param {Function} callback - Called with (event, session)
 * @returns {object} Subscription object with unsubscribe method
 */
export function onAuthStateChange(callback) {
  return supabase.auth.onAuthStateChange(callback)
}
