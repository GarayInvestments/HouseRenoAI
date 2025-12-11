# Supabase Email Templates Setup

## Overview

Custom email templates for House Renovators AI Portal authentication flows. These templates use `{{ .RedirectTo }}` instead of `{{ .SiteURL }}` to properly redirect users back to the frontend after email confirmation.

## 📁 Template Files

All templates are located in `supabase/templates/`:

- **`confirmation.html`** - Email verification after signup
- **`invite.html`** - User invitation emails
- **`recovery.html`** - Password reset requests
- **`magic_link.html`** - Passwordless sign-in links

## 🚀 Deployment Instructions

### For Production (Supabase Dashboard)

1. **Navigate to Email Templates**:
   - Go to: https://supabase.com/dashboard/project/dtfjzjhxtojkgfofrmrr/auth/templates

2. **Update Each Template**:
   - Click on each template (Confirm signup, Invite user, Reset password, Magic Link)
   - Copy content from corresponding HTML file in `supabase/templates/`
   - Paste into the template editor
   - **Important**: Update subject line if desired
   - Click **Save**

3. **Verify Settings**:
   - Ensure **Site URL** is set to: `https://portal.houserenovatorsllc.com`
   - Ensure **Redirect URLs** include all frontend URLs

### For Local Development

If using Supabase CLI locally:

1. **Create config file** (`supabase/config.toml`):
```toml
[auth.email.template.confirmation]
subject = "Confirm Your Email - House Renovators AI"
content_path = "./supabase/templates/confirmation.html"

[auth.email.template.invite]
subject = "You're Invited to House Renovators AI"
content_path = "./supabase/templates/invite.html"

[auth.email.template.recovery]
subject = "Reset Your Password - House Renovators AI"
content_path = "./supabase/templates/recovery.html"

[auth.email.template.magic_link]
subject = "Your Sign-In Link - House Renovators AI"
content_path = "./supabase/templates/magic_link.html"
```

2. **Restart Supabase**:
```bash
supabase stop && supabase start
```

## 🎨 Template Features

### Design Elements
- **Responsive**: Works on mobile and desktop
- **Brand Colors**: Blue gradient for primary actions, red for password reset
- **Clear CTAs**: Large, prominent action buttons
- **Security**: Warning messages for sensitive actions
- **Professional**: Clean, modern design matching portal aesthetic

### Template Variables Used

All templates use these Supabase variables:

- `{{ .RedirectTo }}` - Frontend URL (e.g., https://portal.houserenovatorsllc.com)
- `{{ .TokenHash }}` - Hashed verification token
- `{{ .Email }}` - User's email address
- `{{ .Token }}` - 6-digit OTP (alternative to link)

### URL Structure

Each template redirects to frontend auth callback routes:

```
Confirmation: {{ .RedirectTo }}/auth/confirm?token_hash={{ .TokenHash }}&type=email
Invite:       {{ .RedirectTo }}/auth/confirm?token_hash={{ .TokenHash }}&type=invite
Recovery:     {{ .RedirectTo }}/auth/reset-password?token_hash={{ .TokenHash }}&type=recovery
Magic Link:   {{ .RedirectTo }}/auth/confirm?token_hash={{ .TokenHash }}&type=magiclink
```

## 🔧 Frontend Routes Required

Your React frontend must handle these auth callback routes:

### `/auth/confirm`
Handles email confirmation, invites, and magic links:
```javascript
// Parse query params: token_hash, type
// Call Supabase: supabase.auth.verifyOtp({ token_hash, type })
// Redirect to dashboard on success
```

### `/auth/reset-password`
Handles password reset:
```javascript
// Parse query params: token_hash, type
// Show password reset form
// Call Supabase: supabase.auth.updateUser({ password: newPassword })
// Redirect to login on success
```

## 📝 Customization

### Changing Colors
All templates use inline styles. Update gradient colors:

**Primary (Blue):**
```css
background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
```

**Error (Red):**
```css
background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
```

**Magic Link (Purple):**
```css
background: linear-gradient(135deg, #7c3aed 0%, #5b21b6 100%);
```

### Changing Text
Edit the HTML files directly. Key sections:
- **Header**: Company name and page title
- **Body**: Instructions and security notices
- **Footer**: Company info and copyright

### Adding Logo
Replace the text header with an image:
```html
<img src="https://yourdomain.com/logo.png" alt="House Renovators AI" style="max-width: 200px; height: auto;" />
```

## 🧪 Testing

### Test Email Delivery

1. **Sign Up Test**:
```bash
# Create test user via Supabase dashboard
# Check email for confirmation template
```

2. **Password Reset Test**:
```bash
# Request password reset
# Check email for recovery template
```

3. **Magic Link Test**:
```javascript
// Frontend: supabase.auth.signInWithOtp({ email })
// Check email for magic link template
```

### Verify Redirects

After clicking email links, verify:
- ✅ Redirects to correct frontend URL
- ✅ Token hash is present in URL
- ✅ Type parameter matches action
- ✅ Frontend handles callback correctly

## 🐛 Troubleshooting

### Email Not Received
- Check Supabase dashboard Auth logs
- Verify SMTP settings (if using custom SMTP)
- Check spam folder

### Wrong Redirect URL
- Verify `redirectTo` parameter in frontend auth calls
- Check Supabase **Redirect URLs** allowlist
- Ensure **Site URL** is set correctly

### Template Not Updating
- Clear browser cache
- Wait 2-3 minutes for changes to propagate
- Check Supabase dashboard for save confirmation

### Broken Links
- Verify frontend routes exist (`/auth/confirm`, `/auth/reset-password`)
- Check token_hash and type parameters are parsed correctly
- Test with Supabase CLI in local environment first

## 📚 Additional Resources

- [Supabase Email Templates Docs](https://supabase.com/docs/guides/auth/auth-email-templates)
- [Redirect URLs Configuration](https://supabase.com/docs/guides/auth/redirect-urls)
- [Auth Flows Documentation](https://supabase.com/docs/guides/auth)

---

**Last Updated**: December 11, 2025  
**Status**: Templates created, ready for deployment
