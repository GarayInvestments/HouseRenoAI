import React from 'react';

export default function PrivacyPolicy() {
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
            Privacy Policy
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
              Introduction
            </h2>
            <p style={{ marginBottom: '0' }}>
              House Renovators LLC ("we," "our," or "us") operates the House Renovators AI Portal 
              (the "Service"). This Privacy Policy explains how we collect, use, disclose, and 
              safeguard your information when you use our Service.
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
              }}>2</span>
              Information We Collect
            </h2>
            
            <h3 style={{ 
              fontSize: '20px', 
              fontWeight: '600', 
              color: '#334155',
              marginBottom: '12px',
              marginTop: '20px'
            }}>
              2.1 Information You Provide
            </h3>
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
                Account information (name, email, company details)
              </li>
              <li style={{ marginBottom: '8px', position: 'relative', paddingLeft: '20px' }}>
                <span style={{ 
                  position: 'absolute', 
                  left: '0', 
                  color: '#2563EB',
                  fontWeight: '700'
                }}>•</span>
                Project and permit information
              </li>
              <li style={{ marginBottom: '8px', position: 'relative', paddingLeft: '20px' }}>
                <span style={{ 
                  position: 'absolute', 
                  left: '0', 
                  color: '#2563EB',
                  fontWeight: '700'
                }}>•</span>
                Client and customer data
              </li>
              <li style={{ marginBottom: '8px', position: 'relative', paddingLeft: '20px' }}>
                <span style={{ 
                  position: 'absolute', 
                  left: '0', 
                  color: '#2563EB',
                  fontWeight: '700'
                }}>•</span>
                Financial data from QuickBooks integration
              </li>
              <li style={{ marginBottom: '8px', position: 'relative', paddingLeft: '20px' }}>
                <span style={{ 
                  position: 'absolute', 
                  left: '0', 
                  color: '#2563EB',
                  fontWeight: '700'
                }}>•</span>
                Communications with our AI assistant
              </li>
              <li style={{ marginBottom: '8px', position: 'relative', paddingLeft: '20px' }}>
                <span style={{ 
                  position: 'absolute', 
                  left: '0', 
                  color: '#2563EB',
                  fontWeight: '700'
                }}>•</span>
                Documents and files you upload
              </li>
            </ul>

            <h3 style={{ 
              fontSize: '20px', 
              fontWeight: '600', 
              color: '#334155',
              marginBottom: '12px',
              marginTop: '20px'
            }}>
              2.2 Automatically Collected Information
            </h3>
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
                Device information (browser type, operating system)
              </li>
              <li style={{ marginBottom: '8px', position: 'relative', paddingLeft: '20px' }}>
                <span style={{ 
                  position: 'absolute', 
                  left: '0', 
                  color: '#2563EB',
                  fontWeight: '700'
                }}>•</span>
                Usage data (pages visited, features used)
              </li>
              <li style={{ marginBottom: '8px', position: 'relative', paddingLeft: '20px' }}>
                <span style={{ 
                  position: 'absolute', 
                  left: '0', 
                  color: '#2563EB',
                  fontWeight: '700'
                }}>•</span>
                IP address and location data
              </li>
              <li style={{ marginBottom: '8px', position: 'relative', paddingLeft: '20px' }}>
                <span style={{ 
                  position: 'absolute', 
                  left: '0', 
                  color: '#2563EB',
                  fontWeight: '700'
                }}>•</span>
                Cookies and similar tracking technologies
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
              }}>3</span>
              How We Use Your Information
            </h2>
            <p style={{ marginBottom: '12px' }}>We use the collected information for:</p>
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
                Providing and maintaining the Service
              </li>
              <li style={{ marginBottom: '8px', position: 'relative', paddingLeft: '20px' }}>
                <span style={{ 
                  position: 'absolute', 
                  left: '0', 
                  color: '#2563EB',
                  fontWeight: '700'
                }}>•</span>
                Processing transactions and managing projects
              </li>
              <li style={{ marginBottom: '8px', position: 'relative', paddingLeft: '20px' }}>
                <span style={{ 
                  position: 'absolute', 
                  left: '0', 
                  color: '#2563EB',
                  fontWeight: '700'
                }}>•</span>
                Syncing data with QuickBooks Online
              </li>
              <li style={{ marginBottom: '8px', position: 'relative', paddingLeft: '20px' }}>
                <span style={{ 
                  position: 'absolute', 
                  left: '0', 
                  color: '#2563EB',
                  fontWeight: '700'
                }}>•</span>
                Generating AI-powered insights and recommendations
              </li>
              <li style={{ marginBottom: '8px', position: 'relative', paddingLeft: '20px' }}>
                <span style={{ 
                  position: 'absolute', 
                  left: '0', 
                  color: '#2563EB',
                  fontWeight: '700'
                }}>•</span>
                Improving our Service and developing new features
              </li>
              <li style={{ marginBottom: '8px', position: 'relative', paddingLeft: '20px' }}>
                <span style={{ 
                  position: 'absolute', 
                  left: '0', 
                  color: '#2563EB',
                  fontWeight: '700'
                }}>•</span>
                Communicating with you about updates and support
              </li>
              <li style={{ marginBottom: '8px', position: 'relative', paddingLeft: '20px' }}>
                <span style={{ 
                  position: 'absolute', 
                  left: '0', 
                  color: '#2563EB',
                  fontWeight: '700'
                }}>•</span>
                Ensuring security and preventing fraud
              </li>
              <li style={{ marginBottom: '8px', position: 'relative', paddingLeft: '20px' }}>
                <span style={{ 
                  position: 'absolute', 
                  left: '0', 
                  color: '#2563EB',
                  fontWeight: '700'
                }}>•</span>
                Complying with legal obligations
              </li>
            </ul>
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
              }}>4</span>
              Third-Party Services
            </h2>
            <p style={{ marginBottom: '12px' }}>We integrate with the following third-party services:</p>
            <ul style={{
              paddingLeft: '24px',
              margin: '12px 0',
              listStyleType: 'none'
            }}>
              <li style={{ marginBottom: '12px', position: 'relative', paddingLeft: '20px' }}>
                <span style={{ 
                  position: 'absolute', 
                  left: '0', 
                  color: '#2563EB',
                  fontWeight: '700'
                }}>•</span>
                <strong>QuickBooks Online (Intuit Inc.):</strong> Financial data management and invoicing
              </li>
              <li style={{ marginBottom: '12px', position: 'relative', paddingLeft: '20px' }}>
                <span style={{ 
                  position: 'absolute', 
                  left: '0', 
                  color: '#2563EB',
                  fontWeight: '700'
                }}>•</span>
                <strong>OpenAI:</strong> AI-powered chat and document analysis
              </li>
              <li style={{ marginBottom: '12px', position: 'relative', paddingLeft: '20px' }}>
                <span style={{ 
                  position: 'absolute', 
                  left: '0', 
                  color: '#2563EB',
                  fontWeight: '700'
                }}>•</span>
                <strong>Google Sheets API:</strong> Data storage and synchronization
              </li>
              <li style={{ marginBottom: '12px', position: 'relative', paddingLeft: '20px' }}>
                <span style={{ 
                  position: 'absolute', 
                  left: '0', 
                  color: '#2563EB',
                  fontWeight: '700'
                }}>•</span>
                <strong>Cloudflare:</strong> Content delivery and security
              </li>
              <li style={{ marginBottom: '12px', position: 'relative', paddingLeft: '20px' }}>
                <span style={{ 
                  position: 'absolute', 
                  left: '0', 
                  color: '#2563EB',
                  fontWeight: '700'
                }}>•</span>
                <strong>Render:</strong> Application hosting
              </li>
            </ul>
            <p style={{ marginTop: '12px', fontStyle: 'italic', color: '#64748B' }}>
              Each third-party service has its own privacy policy governing the use of your data.
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
              Data Security
            </h2>
            <p style={{ marginBottom: '12px' }}>
              We implement industry-standard security measures to protect your information:
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
                End-to-end encryption for data transmission (HTTPS/TLS)
              </li>
              <li style={{ marginBottom: '8px', position: 'relative', paddingLeft: '20px' }}>
                <span style={{ 
                  position: 'absolute', 
                  left: '0', 
                  color: '#2563EB',
                  fontWeight: '700'
                }}>•</span>
                Secure OAuth 2.0 authentication
              </li>
              <li style={{ marginBottom: '8px', position: 'relative', paddingLeft: '20px' }}>
                <span style={{ 
                  position: 'absolute', 
                  left: '0', 
                  color: '#2563EB',
                  fontWeight: '700'
                }}>•</span>
                Regular security audits and updates
              </li>
              <li style={{ marginBottom: '8px', position: 'relative', paddingLeft: '20px' }}>
                <span style={{ 
                  position: 'absolute', 
                  left: '0', 
                  color: '#2563EB',
                  fontWeight: '700'
                }}>•</span>
                Access controls and user authentication
              </li>
              <li style={{ marginBottom: '8px', position: 'relative', paddingLeft: '20px' }}>
                <span style={{ 
                  position: 'absolute', 
                  left: '0', 
                  color: '#2563EB',
                  fontWeight: '700'
                }}>•</span>
                Encrypted storage of sensitive credentials
              </li>
            </ul>
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
              Data Retention
            </h2>
            <p style={{ marginBottom: '0' }}>
              We retain your information for as long as necessary to provide the Service and 
              comply with legal obligations. You may request deletion of your data at any time 
              by contacting us.
            </p>
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
              Your Rights
            </h2>
            <p style={{ marginBottom: '12px' }}>You have the right to:</p>
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
                Access your personal information
              </li>
              <li style={{ marginBottom: '8px', position: 'relative', paddingLeft: '20px' }}>
                <span style={{ 
                  position: 'absolute', 
                  left: '0', 
                  color: '#2563EB',
                  fontWeight: '700'
                }}>•</span>
                Correct inaccurate data
              </li>
              <li style={{ marginBottom: '8px', position: 'relative', paddingLeft: '20px' }}>
                <span style={{ 
                  position: 'absolute', 
                  left: '0', 
                  color: '#2563EB',
                  fontWeight: '700'
                }}>•</span>
                Request deletion of your data
              </li>
              <li style={{ marginBottom: '8px', position: 'relative', paddingLeft: '20px' }}>
                <span style={{ 
                  position: 'absolute', 
                  left: '0', 
                  color: '#2563EB',
                  fontWeight: '700'
                }}>•</span>
                Export your data
              </li>
              <li style={{ marginBottom: '8px', position: 'relative', paddingLeft: '20px' }}>
                <span style={{ 
                  position: 'absolute', 
                  left: '0', 
                  color: '#2563EB',
                  fontWeight: '700'
                }}>•</span>
                Opt-out of marketing communications
              </li>
              <li style={{ marginBottom: '8px', position: 'relative', paddingLeft: '20px' }}>
                <span style={{ 
                  position: 'absolute', 
                  left: '0', 
                  color: '#2563EB',
                  fontWeight: '700'
                }}>•</span>
                Disconnect third-party integrations (e.g., QuickBooks)
              </li>
            </ul>
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
              }}>8</span>
              Children's Privacy
            </h2>
            <p style={{ marginBottom: '0' }}>
              Our Service is not intended for users under 18 years of age. We do not knowingly 
              collect personal information from children.
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
              International Data Transfers
            </h2>
            <p style={{ marginBottom: '0' }}>
              Your information may be transferred to and processed in countries other than your 
              country of residence. We ensure appropriate safeguards are in place for such transfers.
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
              Changes to This Policy
            </h2>
            <p style={{ marginBottom: '0' }}>
              We may update this Privacy Policy from time to time. We will notify you of any 
              changes by posting the new Privacy Policy on this page and updating the "Last Updated" date.
            </p>
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
              Contact Us
            </h2>
            <p style={{ marginBottom: '16px' }}>
              If you have questions about this Privacy Policy, please contact us:
            </p>
            <div style={{
              background: 'white',
              padding: '20px',
              borderRadius: '8px',
              border: '1px solid #E2E8F0'
            }}>
              <p style={{ fontWeight: '700', marginBottom: '8px', color: '#1E293B' }}>House Renovators LLC</p>
              <p style={{ marginBottom: '4px' }}>
                Email: <a href="mailto:privacy@houserenovatorsllc.com" style={{ color: '#2563EB', textDecoration: 'none' }} onMouseOver={(e) => e.target.style.textDecoration = 'underline'} onMouseOut={(e) => e.target.style.textDecoration = 'none'}>privacy@houserenovatorsllc.com</a>
              </p>
              <p style={{ marginBottom: '0' }}>
                Website: <a href="https://portal.houserenovatorsllc.com" style={{ color: '#2563EB', textDecoration: 'none' }} onMouseOver={(e) => e.target.style.textDecoration = 'underline'} onMouseOut={(e) => e.target.style.textDecoration = 'none'}>https://portal.houserenovatorsllc.com</a>
              </p>
            </div>
          </section>

          {/* QuickBooks Integration Notice */}
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
              <span style={{ fontSize: '20px' }}>🔒</span>
              QuickBooks Integration Privacy Notice
            </h2>
            <p style={{ marginBottom: '12px', color: '#1E40AF' }}>
              When you connect your QuickBooks account, we access and store:
            </p>
            <ul style={{
              paddingLeft: '24px',
              margin: '12px 0',
              listStyleType: 'none',
              color: '#1E40AF'
            }}>
              <li style={{ marginBottom: '8px', position: 'relative', paddingLeft: '20px' }}>
                <span style={{ 
                  position: 'absolute', 
                  left: '0', 
                  color: '#2563EB',
                  fontWeight: '700'
                }}>•</span>
                Company information
              </li>
              <li style={{ marginBottom: '8px', position: 'relative', paddingLeft: '20px' }}>
                <span style={{ 
                  position: 'absolute', 
                  left: '0', 
                  color: '#2563EB',
                  fontWeight: '700'
                }}>•</span>
                Customer and vendor data
              </li>
              <li style={{ marginBottom: '8px', position: 'relative', paddingLeft: '20px' }}>
                <span style={{ 
                  position: 'absolute', 
                  left: '0', 
                  color: '#2563EB',
                  fontWeight: '700'
                }}>•</span>
                Invoices and estimates
              </li>
              <li style={{ marginBottom: '8px', position: 'relative', paddingLeft: '20px' }}>
                <span style={{ 
                  position: 'absolute', 
                  left: '0', 
                  color: '#2563EB',
                  fontWeight: '700'
                }}>•</span>
                Items and services
              </li>
              <li style={{ marginBottom: '8px', position: 'relative', paddingLeft: '20px' }}>
                <span style={{ 
                  position: 'absolute', 
                  left: '0', 
                  color: '#2563EB',
                  fontWeight: '700'
                }}>•</span>
                Financial transaction data
              </li>
            </ul>
            <p style={{ marginTop: '12px', marginBottom: '0', color: '#1E40AF' }}>
              This data is used solely to provide integration features and is not shared with 
              third parties except as necessary to operate the Service. You can disconnect 
              QuickBooks integration at any time from the Settings page.
            </p>
          </section>
        </div>

        {/* Footer */}
        <div style={{
          marginTop: '48px',
          paddingTop: '24px',
          borderTop: '2px solid #E2E8F0',
          textAlign: 'center'
        }}>
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
