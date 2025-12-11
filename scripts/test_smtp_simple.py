#!/usr/bin/env python3
"""
Simple SMTP test - paste credentials when prompted
"""
import smtplib
import ssl
from email.message import EmailMessage
import getpass

def test_smtp():
    print("=== Gmail SMTP Test for noreply@houserenovatorsllc.com ===\n")
    
    # Get credentials
    smtp_user = input("Gmail address (default: steve@garayinvestments.com): ").strip() or "steve@garayinvestments.com"
    smtp_password = getpass.getpass("Gmail App Password (16 chars, no spaces): ").strip()
    
    # Get recipient
    to_email = input("Test recipient email (default: steve@houserenovatorsllc.com): ").strip() or "steve@houserenovatorsllc.com"
    
    print(f"\n📧 Sending test email...")
    print(f"   From: House Renovators <noreply@houserenovatorsllc.com>")
    print(f"   To: {to_email}")
    print(f"   Via: {smtp_user}")
    print()
    
    try:
        # Create message
        msg = EmailMessage()
        msg["From"] = "House Renovators <noreply@houserenovatorsllc.com>"
        msg["To"] = to_email
        msg["Subject"] = "✅ SMTP Test - House Renovators"
        
        html = """
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px; max-width: 600px;">
            <div style="background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%); padding: 30px; border-radius: 12px 12px 0 0; text-align: center;">
                <h1 style="color: white; margin: 0;">✅ SMTP Test Successful!</h1>
            </div>
            <div style="padding: 30px; background: white; border: 1px solid #e5e7eb; border-top: none; border-radius: 0 0 12px 12px;">
                <p>Your Gmail SMTP configuration is working correctly!</p>
                <ul style="line-height: 1.8;">
                    <li><strong>From:</strong> noreply@houserenovatorsllc.com</li>
                    <li><strong>SMTP:</strong> smtp.gmail.com:587</li>
                    <li><strong>Security:</strong> TLS encryption</li>
                </ul>
                <p style="margin-top: 20px; padding: 15px; background: #f0fdf4; border-left: 4px solid #22c55e; border-radius: 4px;">
                    <strong>✨ Next steps:</strong> Configure these settings in Supabase dashboard to enable auth emails.
                </p>
            </div>
            <div style="text-align: center; padding: 20px; color: #6b7280; font-size: 12px;">
                House Renovators LLC © 2025
            </div>
        </body>
        </html>
        """
        
        msg.set_content("SMTP test successful! Your Gmail relay is working.")
        msg.add_alternative(html, subtype='html')
        
        # Send
        context = ssl.create_default_context()
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=10) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        
        print("✅ SUCCESS! Email sent.")
        print(f"\nCheck {to_email} for the test message.")
        print("\n📋 Supabase SMTP Settings:")
        print(f"   Host: smtp.gmail.com")
        print(f"   Port: 587")
        print(f"   Username: {smtp_user}")
        print(f"   Password: (your App Password)")
        print(f"   From: noreply@houserenovatorsllc.com")
        return True
        
    except smtplib.SMTPAuthenticationError:
        print("❌ Authentication failed.")
        print("\n🔧 Troubleshooting:")
        print("   1. Enable 2FA on your Google account")
        print("   2. Generate App Password at: https://myaccount.google.com/apppasswords")
        print("   3. Copy the 16-character password (remove spaces)")
        print("   4. Ensure noreply@houserenovatorsllc.com is added as an alias in Gmail")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_smtp()
