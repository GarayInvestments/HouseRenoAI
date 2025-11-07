import React from 'react';

export default function PrivacyPolicy() {
  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto bg-white shadow-sm rounded-lg p-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Privacy Policy</h1>
        
        <p className="text-sm text-gray-600 mb-8">
          <strong>Effective Date:</strong> November 6, 2025<br />
          <strong>Last Updated:</strong> November 6, 2025
        </p>

        <div className="space-y-6 text-gray-700">
          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">1. Introduction</h2>
            <p>
              House Renovators LLC ("we," "our," or "us") operates the House Renovators AI Portal 
              (the "Service"). This Privacy Policy explains how we collect, use, disclose, and 
              safeguard your information when you use our Service.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">2. Information We Collect</h2>
            
            <h3 className="text-xl font-semibold text-gray-800 mb-2 mt-4">2.1 Information You Provide</h3>
            <ul className="list-disc pl-6 space-y-2">
              <li>Account information (name, email, company details)</li>
              <li>Project and permit information</li>
              <li>Client and customer data</li>
              <li>Financial data from QuickBooks integration</li>
              <li>Communications with our AI assistant</li>
              <li>Documents and files you upload</li>
            </ul>

            <h3 className="text-xl font-semibold text-gray-800 mb-2 mt-4">2.2 Automatically Collected Information</h3>
            <ul className="list-disc pl-6 space-y-2">
              <li>Device information (browser type, operating system)</li>
              <li>Usage data (pages visited, features used)</li>
              <li>IP address and location data</li>
              <li>Cookies and similar tracking technologies</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">3. How We Use Your Information</h2>
            <p className="mb-3">We use the collected information for:</p>
            <ul className="list-disc pl-6 space-y-2">
              <li>Providing and maintaining the Service</li>
              <li>Processing transactions and managing projects</li>
              <li>Syncing data with QuickBooks Online</li>
              <li>Generating AI-powered insights and recommendations</li>
              <li>Improving our Service and developing new features</li>
              <li>Communicating with you about updates and support</li>
              <li>Ensuring security and preventing fraud</li>
              <li>Complying with legal obligations</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">4. Third-Party Services</h2>
            <p className="mb-3">We integrate with the following third-party services:</p>
            <ul className="list-disc pl-6 space-y-2">
              <li><strong>QuickBooks Online (Intuit Inc.):</strong> Financial data management and invoicing</li>
              <li><strong>OpenAI:</strong> AI-powered chat and document analysis</li>
              <li><strong>Google Sheets API:</strong> Data storage and synchronization</li>
              <li><strong>Cloudflare:</strong> Content delivery and security</li>
              <li><strong>Render:</strong> Application hosting</li>
            </ul>
            <p className="mt-3">
              Each third-party service has its own privacy policy governing the use of your data.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">5. Data Security</h2>
            <p>
              We implement industry-standard security measures to protect your information:
            </p>
            <ul className="list-disc pl-6 space-y-2 mt-3">
              <li>End-to-end encryption for data transmission (HTTPS/TLS)</li>
              <li>Secure OAuth 2.0 authentication</li>
              <li>Regular security audits and updates</li>
              <li>Access controls and user authentication</li>
              <li>Encrypted storage of sensitive credentials</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">6. Data Retention</h2>
            <p>
              We retain your information for as long as necessary to provide the Service and 
              comply with legal obligations. You may request deletion of your data at any time 
              by contacting us.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">7. Your Rights</h2>
            <p className="mb-3">You have the right to:</p>
            <ul className="list-disc pl-6 space-y-2">
              <li>Access your personal information</li>
              <li>Correct inaccurate data</li>
              <li>Request deletion of your data</li>
              <li>Export your data</li>
              <li>Opt-out of marketing communications</li>
              <li>Disconnect third-party integrations (e.g., QuickBooks)</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">8. Children's Privacy</h2>
            <p>
              Our Service is not intended for users under 18 years of age. We do not knowingly 
              collect personal information from children.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">9. International Data Transfers</h2>
            <p>
              Your information may be transferred to and processed in countries other than your 
              country of residence. We ensure appropriate safeguards are in place for such transfers.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">10. Changes to This Policy</h2>
            <p>
              We may update this Privacy Policy from time to time. We will notify you of any 
              changes by posting the new Privacy Policy on this page and updating the "Last Updated" date.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">11. Contact Us</h2>
            <p className="mb-3">
              If you have questions about this Privacy Policy, please contact us:
            </p>
            <div className="bg-gray-50 p-4 rounded-md">
              <p><strong>House Renovators LLC</strong></p>
              <p>Email: <a href="mailto:privacy@houserenovatorsllc.com" className="text-blue-600 hover:underline">privacy@houserenovatorsllc.com</a></p>
              <p>Website: <a href="https://portal.houserenovatorsllc.com" className="text-blue-600 hover:underline">https://portal.houserenovatorsllc.com</a></p>
            </div>
          </section>

          <section className="mt-8 pt-6 border-t border-gray-200">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">QuickBooks Integration Privacy Notice</h2>
            <p className="mb-3">
              When you connect your QuickBooks account, we access and store:
            </p>
            <ul className="list-disc pl-6 space-y-2">
              <li>Company information</li>
              <li>Customer and vendor data</li>
              <li>Invoices and estimates</li>
              <li>Items and services</li>
              <li>Financial transaction data</li>
            </ul>
            <p className="mt-3">
              This data is used solely to provide integration features and is not shared with 
              third parties except as necessary to operate the Service. You can disconnect 
              QuickBooks integration at any time from the Settings page.
            </p>
          </section>
        </div>

        <div className="mt-12 pt-6 border-t border-gray-200 text-center">
          <a 
            href="/" 
            className="text-blue-600 hover:text-blue-700 font-medium"
          >
            ← Back to Home
          </a>
        </div>
      </div>
    </div>
  );
}
