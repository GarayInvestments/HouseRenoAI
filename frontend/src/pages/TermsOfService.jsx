import React from 'react';

export default function TermsOfService() {
  return (
    <div style={{ 
      minHeight: '100vh', 
      background: 'linear-gradient(to bottom, #F8FAFC, #F1F5F9)',
      padding: '48px 16px'
    }}>
      <div style={{
        maxWidth: '900px',
        margin: '0 auto',
        background: 'white',
        borderRadius: '16px',
        boxShadow: '0 4px 6px rgba(0, 0, 0, 0.05), 0 10px 20px rgba(0, 0, 0, 0.08)',
        padding: '48px',
        border: '1px solid #E2E8F0'
      }}>
        {/* Header */}
        <div style={{ 
          borderBottom: '3px solid #2563EB',
          paddingBottom: '24px',
          marginBottom: '32px'
        }}>
          <h1 style={{ 
            fontSize: '36px', 
            fontWeight: '700', 
            color: '#1E293B',
            marginBottom: '16px',
            lineHeight: '1.2'
          }}>
            Terms of Service
          </h1>
          
          <div style={{
            display: 'flex',
            gap: '24px',
            fontSize: '14px',
            color: '#64748B',
            flexWrap: 'wrap'
          }}>
            <div>
              <strong style={{ color: '#475569' }}>Effective Date:</strong> November 6, 2025
            </div>
            <div>
              <strong style={{ color: '#475569' }}>Last Updated:</strong> November 6, 2025
            </div>
          </div>
        </div>

        <div style={{ 
          fontSize: '16px',
          lineHeight: '1.7',
          color: '#334155'
        }}>
          {/* Section 1 */}
          <section style={{ 
            marginBottom: '40px',
            padding: '32px',
            background: '#F8FAFC',
            borderRadius: '12px',
            border: '1px solid #E2E8F0'
          }}>
            <h2 style={{ 
              fontSize: '28px', 
              fontWeight: '700', 
              color: '#1E293B',
              marginBottom: '16px',
              display: 'flex',
              alignItems: 'center',
              gap: '12px'
            }}>
              <span style={{
                width: '32px',
                height: '32px',
                borderRadius: '8px',
                background: 'linear-gradient(135deg, #2563EB, #1D4ED8)',
                color: 'white',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '16px',
                fontWeight: '700'
              }}>1</span>
              Acceptance of Terms
            </h2>
            <p style={{ marginBottom: '0' }}>
              By accessing or using the House Renovators AI Portal ("Service"), you agree to be 
              bound by these Terms of Service ("Terms"). If you do not agree to these Terms, 
              do not use the Service.
            </p>
          </section>

          {/* Section 2 */}
          <section style={{ 
            marginBottom: '40px',
            padding: '32px',
            background: 'white',
            borderRadius: '12px',
            border: '1px solid #E2E8F0'
          }}>
            <h2 style={{ 
              fontSize: '28px', 
              fontWeight: '700', 
              color: '#1E293B',
              marginBottom: '16px',
              display: 'flex',
              alignItems: 'center',
              gap: '12px'
            }}>
              <span style={{
                width: '32px',
                height: '32px',
                borderRadius: '8px',
                background: 'linear-gradient(135deg, #2563EB, #1D4ED8)',
                color: 'white',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '16px',
                fontWeight: '700'
              }}>2</span>
              Description of Service
            </h2>
            <p style={{ marginBottom: '12px' }}>
              House Renovators AI Portal is a comprehensive project management platform for 
              construction professionals that provides:
            </p>
            <ul style={{
              paddingLeft: '24px',
              margin: '12px 0',
              listStyleType: 'none'
            }}>
              <li style={{ marginBottom: '8px', position: 'relative', paddingLeft: '20px' }}>
                <span style={{ 
                  position: 'absolute', 
                  left: '0', 
                  color: '#2563EB',
                  fontWeight: '700'
                }}>•</span>
                Permit and project tracking
              </li>
              <li style={{ marginBottom: '8px', position: 'relative', paddingLeft: '20px' }}>
                <span style={{ 
                  position: 'absolute', 
                  left: '0', 
                  color: '#2563EB',
                  fontWeight: '700'
                }}>•</span>
                Client and customer management
              </li>
              <li style={{ marginBottom: '8px', position: 'relative', paddingLeft: '20px' }}>
                <span style={{ 
                  position: 'absolute', 
                  left: '0', 
                  color: '#2563EB',
                  fontWeight: '700'
                }}>•</span>
                QuickBooks Online integration for invoicing
              </li>
              <li style={{ marginBottom: '8px', position: 'relative', paddingLeft: '20px' }}>
                <span style={{ 
                  position: 'absolute', 
                  left: '0', 
                  color: '#2563EB',
                  fontWeight: '700'
                }}>•</span>
                AI-powered document analysis and chat assistance
              </li>
              <li style={{ marginBottom: '8px', position: 'relative', paddingLeft: '20px' }}>
                <span style={{ 
                  position: 'absolute', 
                  left: '0', 
                  color: '#2563EB',
                  fontWeight: '700'
                }}>•</span>
                Real-time data synchronization with Google Sheets
              </li>
            </ul>
          </section>

          {/* Section 3 */}
          <section style={{ 
            marginBottom: '40px',
            padding: '32px',
            background: '#F8FAFC',
            borderRadius: '12px',
            border: '1px solid #E2E8F0'
          }}>
            <h2 style={{ 
              fontSize: '28px', 
              fontWeight: '700', 
              color: '#1E293B',
              marginBottom: '24px',
              display: 'flex',
              alignItems: 'center',
              gap: '12px'
            }}>
              <span style={{
                width: '32px',
                height: '32px',
                borderRadius: '8px',
                background: 'linear-gradient(135deg, #2563EB, #1D4ED8)',
                color: 'white',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '16px',
                fontWeight: '700'
              }}>3</span>
              User Accounts
            </h2>
            
            <h3 style={{ 
              fontSize: '20px', 
              fontWeight: '600', 
              color: '#334155',
              marginBottom: '12px',
              marginTop: '20px'
            }}>
              3.1 Account Creation
            </h3>
            <p style={{ marginBottom: '16px' }}>
              You must provide accurate and complete information when creating an account. 
              You are responsible for maintaining the confidentiality of your account credentials.
            </p>

            <h3 style={{ 
              fontSize: '20px', 
              fontWeight: '600', 
              color: '#334155',
              marginBottom: '12px',
              marginTop: '20px'
            }}>
              3.2 Account Security
            </h3>
            <p style={{ marginBottom: '16px' }}>
              You are responsible for all activities that occur under your account. Notify us 
              immediately of any unauthorized access or security breach.
            </p>

            <h3 style={{ 
              fontSize: '20px', 
              fontWeight: '600', 
              color: '#334155',
              marginBottom: '12px',
              marginTop: '20px'
            }}>
              3.3 Account Termination
            </h3>
            <p style={{ marginBottom: '0' }}>
              We reserve the right to suspend or terminate your account if you violate these Terms 
              or engage in fraudulent or illegal activities.
            </p>
          </section>

          {/* Section 4 */}
          <section style={{ 
            marginBottom: '40px',
            padding: '32px',
            background: 'white',
            borderRadius: '12px',
            border: '1px solid #E2E8F0'
          }}>
            <h2 style={{ 
              fontSize: '28px', 
              fontWeight: '700', 
              color: '#1E293B',
              marginBottom: '24px',
              display: 'flex',
              alignItems: 'center',
              gap: '12px'
            }}>
              <span style={{
                width: '32px',
                height: '32px',
                borderRadius: '8px',
                background: 'linear-gradient(135deg, #2563EB, #1D4ED8)',
                color: 'white',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '16px',
                fontWeight: '700'
              }}>4</span>
              QuickBooks Integration
            </h2>
            
            <h3 style={{ 
              fontSize: '20px', 
              fontWeight: '600', 
              color: '#334155',
              marginBottom: '12px',
              marginTop: '20px'
            }}>
              4.1 Authorization
            </h3>
            <p style={{ marginBottom: '16px' }}>
              By connecting your QuickBooks account, you authorize us to access and manage your 
              QuickBooks data on your behalf, including customers, invoices, estimates, and 
              financial information.
            </p>

            <h3 style={{ 
              fontSize: '20px', 
              fontWeight: '600', 
              color: '#334155',
              marginBottom: '12px',
              marginTop: '20px'
            }}>
              4.2 Data Accuracy
            </h3>
            <p style={{ marginBottom: '16px' }}>
              While we strive for accuracy, you are responsible for verifying all financial 
              data and transactions created through the Service. We are not liable for errors 
              in QuickBooks data synchronization.
            </p>

            <h3 style={{ 
              fontSize: '20px', 
              fontWeight: '600', 
              color: '#334155',
              marginBottom: '12px',
              marginTop: '20px'
            }}>
              4.3 Disconnection
            </h3>
            <p style={{ marginBottom: '0' }}>
              You may disconnect your QuickBooks integration at any time. Disconnecting will 
              revoke our access to your QuickBooks data.
            </p>
          </section>

          {/* Section 5 */}
          <section style={{ 
            marginBottom: '40px',
            padding: '32px',
            background: '#F8FAFC',
            borderRadius: '12px',
            border: '1px solid #E2E8F0'
          }}>
            <h2 style={{ 
              fontSize: '28px', 
              fontWeight: '700', 
              color: '#1E293B',
              marginBottom: '16px',
              display: 'flex',
              alignItems: 'center',
              gap: '12px'
            }}>
              <span style={{
                width: '32px',
                height: '32px',
                borderRadius: '8px',
                background: 'linear-gradient(135deg, #2563EB, #1D4ED8)',
                color: 'white',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '16px',
                fontWeight: '700'
              }}>5</span>
              AI Services
            </h2>
            <p style={{ marginBottom: '0' }}>
              Our AI-powered features are provided for convenience and assistance. AI-generated 
              content should be reviewed and verified before use. We do not guarantee the accuracy, 
              completeness, or reliability of AI-generated information.
            </p>
          </section>

          {/* Section 6 */}
          <section style={{ 
            marginBottom: '40px',
            padding: '32px',
            background: 'white',
            borderRadius: '12px',
            border: '1px solid #E2E8F0'
          }}>
            <h2 style={{ 
              fontSize: '28px', 
              fontWeight: '700', 
              color: '#1E293B',
              marginBottom: '16px',
              display: 'flex',
              alignItems: 'center',
              gap: '12px'
            }}>
              <span style={{
                width: '32px',
                height: '32px',
                borderRadius: '8px',
                background: 'linear-gradient(135deg, #2563EB, #1D4ED8)',
                color: 'white',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '16px',
                fontWeight: '700'
              }}>6</span>
              User Responsibilities
            </h2>
            <p style={{ marginBottom: '12px' }}>You agree to:</p>
            <ul style={{
              paddingLeft: '24px',
              margin: '12px 0',
              listStyleType: 'none'
            }}>
              <li style={{ marginBottom: '8px', position: 'relative', paddingLeft: '20px' }}>
                <span style={{ 
                  position: 'absolute', 
                  left: '0', 
                  color: '#2563EB',
                  fontWeight: '700'
                }}>•</span>
                Use the Service in compliance with all applicable laws and regulations
              </li>
              <li style={{ marginBottom: '8px', position: 'relative', paddingLeft: '20px' }}>
                <span style={{ 
                  position: 'absolute', 
                  left: '0', 
                  color: '#2563EB',
                  fontWeight: '700'
                }}>•</span>
                Provide accurate and up-to-date information
              </li>
              <li style={{ marginBottom: '8px', position: 'relative', paddingLeft: '20px' }}>
                <span style={{ 
                  position: 'absolute', 
                  left: '0', 
                  color: '#2563EB',
                  fontWeight: '700'
                }}>•</span>
                Maintain the security of your account
              </li>
              <li style={{ marginBottom: '8px', position: 'relative', paddingLeft: '20px' }}>
                <span style={{ 
                  position: 'absolute', 
                  left: '0', 
                  color: '#2563EB',
                  fontWeight: '700'
                }}>•</span>
                Not attempt to gain unauthorized access to the Service
              </li>
              <li style={{ marginBottom: '8px', position: 'relative', paddingLeft: '20px' }}>
                <span style={{ 
                  position: 'absolute', 
                  left: '0', 
                  color: '#2563EB',
                  fontWeight: '700'
                }}>•</span>
                Not use the Service for illegal or fraudulent purposes
              </li>
              <li style={{ marginBottom: '8px', position: 'relative', paddingLeft: '20px' }}>
                <span style={{ 
                  position: 'absolute', 
                  left: '0', 
                  color: '#2563EB',
                  fontWeight: '700'
                }}>•</span>
                Not interfere with or disrupt the Service
              </li>
              <li style={{ marginBottom: '8px', position: 'relative', paddingLeft: '20px' }}>
                <span style={{ 
                  position: 'absolute', 
                  left: '0', 
                  color: '#2563EB',
                  fontWeight: '700'
                }}>•</span>
                Respect intellectual property rights
              </li>
            </ul>
          </section>

          {/* Section 7 */}
          <section style={{ 
            marginBottom: '40px',
            padding: '32px',
            background: '#F8FAFC',
            borderRadius: '12px',
            border: '1px solid #E2E8F0'
          }}>
            <h2 style={{ 
              fontSize: '28px', 
              fontWeight: '700', 
              color: '#1E293B',
              marginBottom: '16px',
              display: 'flex',
              alignItems: 'center',
              gap: '12px'
            }}>
              <span style={{
                width: '32px',
                height: '32px',
                borderRadius: '8px',
                background: 'linear-gradient(135deg, #2563EB, #1D4ED8)',
                color: 'white',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '16px',
                fontWeight: '700'
              }}>7</span>
              Intellectual Property
            </h2>
            <p style={{ marginBottom: '0' }}>
              The Service, including all content, features, and functionality, is owned by 
              House Renovators LLC and is protected by copyright, trademark, and other 
              intellectual property laws. You retain ownership of your data, but grant us 
              a license to use it to provide the Service.
            </p>
          </section>

          {/* Section 8 */}
          <section style={{ 
            marginBottom: '40px',
            padding: '32px',
            background: 'white',
            borderRadius: '12px',
            border: '1px solid #E2E8F0'
          }}>
            <h2 style={{ 
              fontSize: '28px', 
              fontWeight: '700', 
              color: '#1E293B',
              marginBottom: '24px',
              display: 'flex',
              alignItems: 'center',
              gap: '12px'
            }}>
              <span style={{
                width: '32px',
                height: '32px',
                borderRadius: '8px',
                background: 'linear-gradient(135deg, #2563EB, #1D4ED8)',
                color: 'white',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '16px',
                fontWeight: '700'
              }}>8</span>
              Payment and Fees
            </h2>
            
            <h3 style={{ 
              fontSize: '20px', 
              fontWeight: '600', 
              color: '#334155',
              marginBottom: '12px',
              marginTop: '20px'
            }}>
              8.1 Subscription
            </h3>
            <p style={{ marginBottom: '16px' }}>
              Access to certain features may require a paid subscription. Subscription fees 
              are billed in advance on a recurring basis.
            </p>

            <h3 style={{ 
              fontSize: '20px', 
              fontWeight: '600', 
              color: '#334155',
              marginBottom: '12px',
              marginTop: '20px'
            }}>
              8.2 Refunds
            </h3>
            <p style={{ marginBottom: '16px' }}>
              Subscription fees are non-refundable except as required by law or at our sole discretion.
            </p>

            <h3 style={{ 
              fontSize: '20px', 
              fontWeight: '600', 
              color: '#334155',
              marginBottom: '12px',
              marginTop: '20px'
            }}>
              8.3 Price Changes
            </h3>
            <p style={{ marginBottom: '0' }}>
              We reserve the right to modify subscription prices with 30 days' notice.
            </p>
          </section>

          {/* Section 9 */}
          <section style={{ 
            marginBottom: '40px',
            padding: '32px',
            background: '#F8FAFC',
            borderRadius: '12px',
            border: '1px solid #E2E8F0'
          }}>
            <h2 style={{ 
              fontSize: '28px', 
              fontWeight: '700', 
              color: '#1E293B',
              marginBottom: '16px',
              display: 'flex',
              alignItems: 'center',
              gap: '12px'
            }}>
              <span style={{
                width: '32px',
                height: '32px',
                borderRadius: '8px',
                background: 'linear-gradient(135deg, #2563EB, #1D4ED8)',
                color: 'white',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '16px',
                fontWeight: '700'
              }}>9</span>
              Data Backup and Loss
            </h2>
            <p style={{ marginBottom: '0' }}>
              While we implement backup procedures, you are responsible for maintaining your 
              own backups of critical data. We are not liable for data loss or corruption.
            </p>
          </section>

          {/* Section 10 */}
          <section style={{ 
            marginBottom: '40px',
            padding: '32px',
            background: 'white',
            borderRadius: '12px',
            border: '1px solid #E2E8F0'
          }}>
            <h2 style={{ 
              fontSize: '28px', 
              fontWeight: '700', 
              color: '#1E293B',
              marginBottom: '16px',
              display: 'flex',
              alignItems: 'center',
              gap: '12px'
            }}>
              <span style={{
                width: '32px',
                height: '32px',
                borderRadius: '8px',
                background: 'linear-gradient(135deg, #2563EB, #1D4ED8)',
                color: 'white',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '16px',
                fontWeight: '700'
              }}>10</span>
              Limitation of Liability
            </h2>
            <p style={{ marginBottom: '12px', fontWeight: '600' }}>
              TO THE MAXIMUM EXTENT PERMITTED BY LAW:
            </p>
            <ul style={{
              paddingLeft: '24px',
              margin: '12px 0',
              listStyleType: 'none'
            }}>
              <li style={{ marginBottom: '8px', position: 'relative', paddingLeft: '20px' }}>
                <span style={{ 
                  position: 'absolute', 
                  left: '0', 
                  color: '#2563EB',
                  fontWeight: '700'
                }}>•</span>
                THE SERVICE IS PROVIDED "AS IS" WITHOUT WARRANTIES OF ANY KIND
              </li>
              <li style={{ marginBottom: '8px', position: 'relative', paddingLeft: '20px' }}>
                <span style={{ 
                  position: 'absolute', 
                  left: '0', 
                  color: '#2563EB',
                  fontWeight: '700'
                }}>•</span>
                WE ARE NOT LIABLE FOR INDIRECT, INCIDENTAL, OR CONSEQUENTIAL DAMAGES
              </li>
              <li style={{ marginBottom: '8px', position: 'relative', paddingLeft: '20px' }}>
                <span style={{ 
                  position: 'absolute', 
                  left: '0', 
                  color: '#2563EB',
                  fontWeight: '700'
                }}>•</span>
                OUR TOTAL LIABILITY SHALL NOT EXCEED THE AMOUNT YOU PAID IN THE LAST 12 MONTHS
              </li>
              <li style={{ marginBottom: '8px', position: 'relative', paddingLeft: '20px' }}>
                <span style={{ 
                  position: 'absolute', 
                  left: '0', 
                  color: '#2563EB',
                  fontWeight: '700'
                }}>•</span>
                WE ARE NOT LIABLE FOR THIRD-PARTY SERVICES (QuickBooks, OpenAI, Google)
              </li>
            </ul>
          </section>

          {/* Section 11 */}
          <section style={{ 
            marginBottom: '40px',
            padding: '32px',
            background: '#F8FAFC',
            borderRadius: '12px',
            border: '1px solid #E2E8F0'
          }}>
            <h2 style={{ 
              fontSize: '28px', 
              fontWeight: '700', 
              color: '#1E293B',
              marginBottom: '16px',
              display: 'flex',
              alignItems: 'center',
              gap: '12px'
            }}>
              <span style={{
                width: '32px',
                height: '32px',
                borderRadius: '8px',
                background: 'linear-gradient(135deg, #2563EB, #1D4ED8)',
                color: 'white',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '16px',
                fontWeight: '700'
              }}>11</span>
              Indemnification
            </h2>
            <p style={{ marginBottom: '0' }}>
              You agree to indemnify and hold harmless House Renovators LLC from any claims, 
              damages, or expenses arising from your use of the Service or violation of these Terms.
            </p>
          </section>

          {/* Section 12 */}
          <section style={{ 
            marginBottom: '40px',
            padding: '32px',
            background: '#F8FAFC',
            borderRadius: '12px',
            border: '1px solid #E2E8F0'
          }}>
            <h2 style={{ 
              fontSize: '28px', 
              fontWeight: '700', 
              color: '#1E293B',
              marginBottom: '16px',
              display: 'flex',
              alignItems: 'center',
              gap: '12px'
            }}>
              <span style={{
                width: '32px',
                height: '32px',
                borderRadius: '8px',
                background: 'linear-gradient(135deg, #2563EB, #1D4ED8)',
                color: 'white',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '16px',
                fontWeight: '700'
              }}>12</span>
              Service Availability
            </h2>
            <p style={{ marginBottom: '0' }}>
              We strive for 99.9% uptime but do not guarantee uninterrupted access. We may 
              perform maintenance, updates, or modifications that temporarily affect Service availability.
            </p>
          </section>

          {/* Section 13 */}
          <section style={{ 
            marginBottom: '40px',
            padding: '32px',
            background: 'white',
            borderRadius: '12px',
            border: '1px solid #E2E8F0'
          }}>
            <h2 style={{ 
              fontSize: '28px', 
              fontWeight: '700', 
              color: '#1E293B',
              marginBottom: '16px',
              display: 'flex',
              alignItems: 'center',
              gap: '12px'
            }}>
              <span style={{
                width: '32px',
                height: '32px',
                borderRadius: '8px',
                background: 'linear-gradient(135deg, #2563EB, #1D4ED8)',
                color: 'white',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '16px',
                fontWeight: '700'
              }}>13</span>
              Third-Party Services
            </h2>
            <p style={{ marginBottom: '0' }}>
              The Service integrates with third-party platforms (QuickBooks, OpenAI, Google). 
              Your use of these services is subject to their respective terms and policies. 
              We are not responsible for third-party service interruptions or changes.
            </p>
          </section>

          {/* Section 14 */}
          <section style={{ 
            marginBottom: '40px',
            padding: '32px',
            background: '#F8FAFC',
            borderRadius: '12px',
            border: '1px solid #E2E8F0'
          }}>
            <h2 style={{ 
              fontSize: '28px', 
              fontWeight: '700', 
              color: '#1E293B',
              marginBottom: '16px',
              display: 'flex',
              alignItems: 'center',
              gap: '12px'
            }}>
              <span style={{
                width: '32px',
                height: '32px',
                borderRadius: '8px',
                background: 'linear-gradient(135deg, #2563EB, #1D4ED8)',
                color: 'white',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '16px',
                fontWeight: '700'
              }}>14</span>
              Modifications to Service
            </h2>
            <p style={{ marginBottom: '0' }}>
              We reserve the right to modify, suspend, or discontinue any part of the Service 
              at any time with or without notice.
            </p>
          </section>

          {/* Section 15 */}
          <section style={{ 
            marginBottom: '40px',
            padding: '32px',
            background: 'white',
            borderRadius: '12px',
            border: '1px solid #E2E8F0'
          }}>
            <h2 style={{ 
              fontSize: '28px', 
              fontWeight: '700', 
              color: '#1E293B',
              marginBottom: '16px',
              display: 'flex',
              alignItems: 'center',
              gap: '12px'
            }}>
              <span style={{
                width: '32px',
                height: '32px',
                borderRadius: '8px',
                background: 'linear-gradient(135deg, #2563EB, #1D4ED8)',
                color: 'white',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '16px',
                fontWeight: '700'
              }}>15</span>
              Governing Law
            </h2>
            <p style={{ marginBottom: '0' }}>
              These Terms shall be governed by and construed in accordance with the laws of the 
              State of California, United States, without regard to its conflict of law provisions.
            </p>
          </section>

          {/* Section 16 */}
          <section style={{ 
            marginBottom: '40px',
            padding: '32px',
            background: '#F8FAFC',
            borderRadius: '12px',
            border: '1px solid #E2E8F0'
          }}>
            <h2 style={{ 
              fontSize: '28px', 
              fontWeight: '700', 
              color: '#1E293B',
              marginBottom: '16px',
              display: 'flex',
              alignItems: 'center',
              gap: '12px'
            }}>
              <span style={{
                width: '32px',
                height: '32px',
                borderRadius: '8px',
                background: 'linear-gradient(135deg, #2563EB, #1D4ED8)',
                color: 'white',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '16px',
                fontWeight: '700'
              }}>16</span>
              Dispute Resolution
            </h2>
            <p style={{ marginBottom: '0' }}>
              Any disputes arising from these Terms or the Service shall be resolved through 
              binding arbitration in accordance with the American Arbitration Association rules.
            </p>
          </section>

          {/* Section 17 */}
          <section style={{ 
            marginBottom: '40px',
            padding: '32px',
            background: 'white',
            borderRadius: '12px',
            border: '1px solid #E2E8F0'
          }}>
            <h2 style={{ 
              fontSize: '28px', 
              fontWeight: '700', 
              color: '#1E293B',
              marginBottom: '16px',
              display: 'flex',
              alignItems: 'center',
              gap: '12px'
            }}>
              <span style={{
                width: '32px',
                height: '32px',
                borderRadius: '8px',
                background: 'linear-gradient(135deg, #2563EB, #1D4ED8)',
                color: 'white',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '16px',
                fontWeight: '700'
              }}>17</span>
              Changes to Terms
            </h2>
            <p style={{ marginBottom: '0' }}>
              We may update these Terms from time to time. We will notify you of material changes 
              by email or through the Service. Continued use of the Service after changes 
              constitutes acceptance of the new Terms.
            </p>
          </section>

          {/* Section 18 */}
          <section style={{ 
            marginBottom: '40px',
            padding: '32px',
            background: '#F8FAFC',
            borderRadius: '12px',
            border: '1px solid #E2E8F0'
          }}>
            <h2 style={{ 
              fontSize: '28px', 
              fontWeight: '700', 
              color: '#1E293B',
              marginBottom: '16px',
              display: 'flex',
              alignItems: 'center',
              gap: '12px'
            }}>
              <span style={{
                width: '32px',
                height: '32px',
                borderRadius: '8px',
                background: 'linear-gradient(135deg, #2563EB, #1D4ED8)',
                color: 'white',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '16px',
                fontWeight: '700'
              }}>18</span>
              Contact Information
            </h2>
            <p style={{ marginBottom: '16px' }}>
              For questions about these Terms, contact us:
            </p>
            <div style={{
              background: 'white',
              padding: '20px',
              borderRadius: '8px',
              border: '1px solid #E2E8F0'
            }}>
              <p style={{ fontWeight: '700', marginBottom: '8px', color: '#1E293B' }}>House Renovators LLC</p>
              <p style={{ marginBottom: '4px' }}>
                Email: <a href="mailto:legal@houserenovatorsllc.com" style={{ color: '#2563EB', textDecoration: 'none' }} onMouseOver={(e) => e.target.style.textDecoration = 'underline'} onMouseOut={(e) => e.target.style.textDecoration = 'none'}>legal@houserenovatorsllc.com</a>
              </p>
              <p style={{ marginBottom: '0' }}>
                Website: <a href="https://portal.houserenovatorsllc.com" style={{ color: '#2563EB', textDecoration: 'none' }} onMouseOver={(e) => e.target.style.textDecoration = 'underline'} onMouseOut={(e) => e.target.style.textDecoration = 'none'}>https://portal.houserenovatorsllc.com</a>
              </p>
            </div>
          </section>

          {/* Acceptance Section */}
          <section style={{ 
            marginBottom: '32px',
            padding: '32px',
            background: 'linear-gradient(135deg, #EFF6FF, #DBEAFE)',
            borderRadius: '12px',
            border: '2px solid #2563EB'
          }}>
            <h2 style={{ 
              fontSize: '24px', 
              fontWeight: '700', 
              color: '#1E3A8A',
              marginBottom: '16px',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}>
              <span style={{ fontSize: '20px' }}>✓</span>
              Acceptance
            </h2>
            <p style={{ marginBottom: '0', color: '#1E40AF' }}>
              By using the House Renovators AI Portal, you acknowledge that you have read, 
              understood, and agree to be bound by these Terms of Service and our Privacy Policy.
            </p>
          </section>
        </div>

        {/* Footer */}
        <div style={{
          marginTop: '48px',
          paddingTop: '24px',
          borderTop: '2px solid #E2E8F0',
          textAlign: 'center',
          display: 'flex',
          gap: '24px',
          justifyContent: 'center',
          flexWrap: 'wrap'
        }}>
          <a 
            href="/privacy" 
            style={{
              color: '#2563EB',
              textDecoration: 'none',
              fontWeight: '600',
              fontSize: '16px',
              display: 'inline-flex',
              alignItems: 'center',
              padding: '12px 24px',
              borderRadius: '8px',
              transition: 'all 0.2s'
            }}
            onMouseOver={(e) => {
              e.target.style.background = '#EFF6FF';
              e.target.style.color = '#1D4ED8';
            }}
            onMouseOut={(e) => {
              e.target.style.background = 'transparent';
              e.target.style.color = '#2563EB';
            }}
          >
            Privacy Policy
          </a>
          <a 
            href="/" 
            style={{
              color: '#2563EB',
              textDecoration: 'none',
              fontWeight: '600',
              fontSize: '16px',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '8px',
              padding: '12px 24px',
              borderRadius: '8px',
              transition: 'all 0.2s'
            }}
            onMouseOver={(e) => {
              e.target.style.background = '#EFF6FF';
              e.target.style.color = '#1D4ED8';
            }}
            onMouseOut={(e) => {
              e.target.style.background = 'transparent';
              e.target.style.color = '#2563EB';
            }}
          >
            <span>←</span> Back to Home
          </a>
        </div>
      </div>
    </div>
  );
}
