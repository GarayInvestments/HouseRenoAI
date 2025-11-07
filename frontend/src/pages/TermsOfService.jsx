import React from 'react';

export default function TermsOfService() {
  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto bg-white shadow-sm rounded-lg p-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Terms of Service</h1>
        
        <p className="text-sm text-gray-600 mb-8">
          <strong>Effective Date:</strong> November 6, 2025<br />
          <strong>Last Updated:</strong> November 6, 2025
        </p>

        <div className="space-y-6 text-gray-700">
          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">1. Acceptance of Terms</h2>
            <p>
              By accessing or using the House Renovators AI Portal ("Service"), you agree to be 
              bound by these Terms of Service ("Terms"). If you do not agree to these Terms, 
              do not use the Service.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">2. Description of Service</h2>
            <p>
              House Renovators AI Portal is a comprehensive project management platform for 
              construction professionals that provides:
            </p>
            <ul className="list-disc pl-6 space-y-2 mt-3">
              <li>Permit and project tracking</li>
              <li>Client and customer management</li>
              <li>QuickBooks Online integration for invoicing</li>
              <li>AI-powered document analysis and chat assistance</li>
              <li>Real-time data synchronization with Google Sheets</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">3. User Accounts</h2>
            
            <h3 className="text-xl font-semibold text-gray-800 mb-2 mt-4">3.1 Account Creation</h3>
            <p>
              You must provide accurate and complete information when creating an account. 
              You are responsible for maintaining the confidentiality of your account credentials.
            </p>

            <h3 className="text-xl font-semibold text-gray-800 mb-2 mt-4">3.2 Account Security</h3>
            <p>
              You are responsible for all activities that occur under your account. Notify us 
              immediately of any unauthorized access or security breach.
            </p>

            <h3 className="text-xl font-semibold text-gray-800 mb-2 mt-4">3.3 Account Termination</h3>
            <p>
              We reserve the right to suspend or terminate your account if you violate these Terms 
              or engage in fraudulent or illegal activities.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">4. QuickBooks Integration</h2>
            
            <h3 className="text-xl font-semibold text-gray-800 mb-2 mt-4">4.1 Authorization</h3>
            <p>
              By connecting your QuickBooks account, you authorize us to access and manage your 
              QuickBooks data on your behalf, including customers, invoices, estimates, and 
              financial information.
            </p>

            <h3 className="text-xl font-semibold text-gray-800 mb-2 mt-4">4.2 Data Accuracy</h3>
            <p>
              While we strive for accuracy, you are responsible for verifying all financial 
              data and transactions created through the Service. We are not liable for errors 
              in QuickBooks data synchronization.
            </p>

            <h3 className="text-xl font-semibold text-gray-800 mb-2 mt-4">4.3 Disconnection</h3>
            <p>
              You may disconnect your QuickBooks integration at any time. Disconnecting will 
              revoke our access to your QuickBooks data.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">5. AI Services</h2>
            <p>
              Our AI-powered features are provided for convenience and assistance. AI-generated 
              content should be reviewed and verified before use. We do not guarantee the accuracy, 
              completeness, or reliability of AI-generated information.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">6. User Responsibilities</h2>
            <p className="mb-3">You agree to:</p>
            <ul className="list-disc pl-6 space-y-2">
              <li>Use the Service in compliance with all applicable laws and regulations</li>
              <li>Provide accurate and up-to-date information</li>
              <li>Maintain the security of your account</li>
              <li>Not attempt to gain unauthorized access to the Service</li>
              <li>Not use the Service for illegal or fraudulent purposes</li>
              <li>Not interfere with or disrupt the Service</li>
              <li>Respect intellectual property rights</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">7. Intellectual Property</h2>
            <p>
              The Service, including all content, features, and functionality, is owned by 
              House Renovators LLC and is protected by copyright, trademark, and other 
              intellectual property laws. You retain ownership of your data, but grant us 
              a license to use it to provide the Service.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">8. Payment and Fees</h2>
            
            <h3 className="text-xl font-semibold text-gray-800 mb-2 mt-4">8.1 Subscription</h3>
            <p>
              Access to certain features may require a paid subscription. Subscription fees 
              are billed in advance on a recurring basis.
            </p>

            <h3 className="text-xl font-semibold text-gray-800 mb-2 mt-4">8.2 Refunds</h3>
            <p>
              Subscription fees are non-refundable except as required by law or at our sole discretion.
            </p>

            <h3 className="text-xl font-semibold text-gray-800 mb-2 mt-4">8.3 Price Changes</h3>
            <p>
              We reserve the right to modify subscription prices with 30 days' notice.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">9. Data Backup and Loss</h2>
            <p>
              While we implement backup procedures, you are responsible for maintaining your 
              own backups of critical data. We are not liable for data loss or corruption.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">10. Limitation of Liability</h2>
            <p className="mb-3">
              TO THE MAXIMUM EXTENT PERMITTED BY LAW:
            </p>
            <ul className="list-disc pl-6 space-y-2">
              <li>THE SERVICE IS PROVIDED "AS IS" WITHOUT WARRANTIES OF ANY KIND</li>
              <li>WE ARE NOT LIABLE FOR INDIRECT, INCIDENTAL, OR CONSEQUENTIAL DAMAGES</li>
              <li>OUR TOTAL LIABILITY SHALL NOT EXCEED THE AMOUNT YOU PAID IN THE LAST 12 MONTHS</li>
              <li>WE ARE NOT LIABLE FOR THIRD-PARTY SERVICES (QuickBooks, OpenAI, Google)</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">11. Indemnification</h2>
            <p>
              You agree to indemnify and hold harmless House Renovators LLC from any claims, 
              damages, or expenses arising from your use of the Service or violation of these Terms.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">12. Service Availability</h2>
            <p>
              We strive for 99.9% uptime but do not guarantee uninterrupted access. We may 
              perform maintenance, updates, or modifications that temporarily affect Service availability.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">13. Third-Party Services</h2>
            <p>
              The Service integrates with third-party platforms (QuickBooks, OpenAI, Google). 
              Your use of these services is subject to their respective terms and policies. 
              We are not responsible for third-party service interruptions or changes.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">14. Modifications to Service</h2>
            <p>
              We reserve the right to modify, suspend, or discontinue any part of the Service 
              at any time with or without notice.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">15. Governing Law</h2>
            <p>
              These Terms shall be governed by and construed in accordance with the laws of the 
              State of California, United States, without regard to its conflict of law provisions.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">16. Dispute Resolution</h2>
            <p>
              Any disputes arising from these Terms or the Service shall be resolved through 
              binding arbitration in accordance with the American Arbitration Association rules.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">17. Changes to Terms</h2>
            <p>
              We may update these Terms from time to time. We will notify you of material changes 
              by email or through the Service. Continued use of the Service after changes 
              constitutes acceptance of the new Terms.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">18. Contact Information</h2>
            <p className="mb-3">
              For questions about these Terms, contact us:
            </p>
            <div className="bg-gray-50 p-4 rounded-md">
              <p><strong>House Renovators LLC</strong></p>
              <p>Email: <a href="mailto:legal@houserenovatorsllc.com" className="text-blue-600 hover:underline">legal@houserenovatorsllc.com</a></p>
              <p>Website: <a href="https://portal.houserenovatorsllc.com" className="text-blue-600 hover:underline">https://portal.houserenovatorsllc.com</a></p>
            </div>
          </section>

          <section className="mt-8 pt-6 border-t border-gray-200">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">Acceptance</h2>
            <p>
              By using the House Renovators AI Portal, you acknowledge that you have read, 
              understood, and agree to be bound by these Terms of Service and our Privacy Policy.
            </p>
          </section>
        </div>

        <div className="mt-12 pt-6 border-t border-gray-200 text-center space-x-6">
          <a 
            href="/privacy" 
            className="text-blue-600 hover:text-blue-700 font-medium"
          >
            Privacy Policy
          </a>
          <a 
            href="/" 
            className="text-blue-600 hover:text-blue-700 font-medium"
          >
            Back to Home
          </a>
        </div>
      </div>
    </div>
  );
}
