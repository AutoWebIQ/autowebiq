import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles, ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import '../styles/Terms.css';

const PrivacyPolicy = () => {
  const navigate = useNavigate();

  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  return (
    <div className="terms-page">
      {/* Navigation */}
      <nav className="terms-nav">
        <div className="nav-content">
          <div className="brand" onClick={() => navigate('/')}>
            <div className="brand-icon">
              <Sparkles size={28} />
            </div>
            <span className="brand-name">AutoWebIQ</span>
          </div>
          <Button className="back-btn" onClick={() => navigate('/')}>
            <ArrowLeft size={18} />
            Back to Home
          </Button>
        </div>
      </nav>

      {/* Content */}
      <div className="terms-container">
        <div className="terms-content">
          <h1 className="terms-title">AutoWebIQ Inc. — Privacy Policy</h1>
          <p style={{ textAlign: 'center', marginBottom: '2rem', color: '#6B7280' }}>
            <strong>Effective Date:</strong> October 28, 2025
          </p>
          
          <p style={{ marginBottom: '2rem' }}>
            AutoWebIQ Inc. ("AutoWebIQ", "we", "us", or "our") values your privacy. This Privacy Policy explains how we collect, use, disclose, and protect information when you use our website autowebiq.com, desktop application, and related services (collectively, the "Services"). This Privacy Policy is incorporated into and subject to our Terms of Service. By using our Services, you agree to the practices described in this Privacy Policy.
          </p>

          <section className="terms-section">
            <h2>1. Information We Collect</h2>
            
            <h3>1.1 Information You Provide Directly</h3>
            <p>When you create an account or use our Services, you may provide:</p>
            
            <h4>Account & Identity Information</h4>
            <ul>
              <li>Full name</li>
              <li>Email address</li>
              <li>Password (securely stored)</li>
              <li>OAuth or third-party credentials you choose to link (e.g., GitHub)</li>
              <li>Payment information and billing details (for paid plans)</li>
              <li>Company or professional information (optional)</li>
            </ul>
            
            <h4>User Content & Project Data</h4>
            <ul>
              <li>Code, projects, repository metadata, files you upload or generate</li>
              <li>Commands, prompts, build/deploy configurations, database connection metadata (not raw secrets unless you provide them)</li>
              <li>Application builds, test data, test configurations, environment settings</li>
            </ul>
            
            <h4>Communications</h4>
            <ul>
              <li>Support requests, feedback, surveys, bug reports, and feature requests</li>
            </ul>

            <h3>1.2 Information Collected Automatically</h3>
            
            <h4>Device & Technical Information</h4>
            <ul>
              <li>Device type and identifiers</li>
              <li>Operating system and environment data</li>
              <li>IP address and approximate geolocation (country/region level)</li>
              <li>App installation and version data</li>
              <li>Hardware specs relevant to performance</li>
            </ul>
            
            <h4>Usage & Telemetry</h4>
            <ul>
              <li>Features and tools used, session duration, frequency</li>
              <li>Commands executed and AI agent interactions (prompts and outputs)</li>
              <li>Performance metrics, error logs, resource utilization</li>
              <li>Build and compilation events, code execution patterns</li>
            </ul>
            
            <h4>Clipboard Content</h4>
            <ul>
              <li>May be collected only when you explicitly use paste-related features.</li>
            </ul>

            <h3>1.3 Analytics</h3>
            <p>We use analytics tools (for example, PostHog and other product analytics providers) to measure and improve product usage, feature adoption, performance, and AI effectiveness. These analytics are collected in aggregated and/or pseudonymized form where possible. You can manage analytics participation through application settings.</p>
          </section>

          <section className="terms-section">
            <h2>2. How We Use Your Information</h2>
            <p>We use collected information for the following purposes:</p>
            
            <h3>To Provide & Improve Services</h3>
            <ul>
              <li>Authenticate users and maintain accounts</li>
              <li>Process payments, manage subscriptions, and deliver access</li>
              <li>Connect and integrate with third-party developer services (e.g., GitHub, database providers) with your consent</li>
              <li>Execute builds, tests, deployments, and run commands on your behalf</li>
              <li>Diagnose and fix issues, improve performance, and develop new features</li>
              <li>Enhance our AI assistance capabilities and agent accuracy</li>
            </ul>
            
            <h3>Communications</h3>
            <ul>
              <li>Respond to support requests and inquiries</li>
              <li>Send service notices, security alerts, and updates</li>
              <li>Send marketing communications where you consent and provide unsubscribe options</li>
            </ul>
            
            <h3>Security & Compliance</h3>
            <ul>
              <li>Detect, investigate, and prevent fraud, abuse, or security incidents</li>
              <li>Scan for vulnerabilities in code when enabled and permitted</li>
              <li>Enforce our Terms of Service and legal obligations</li>
            </ul>
            
            <h3>Research & Analytics</h3>
            <ul>
              <li>Produce aggregated insights on usage patterns (without identifying individuals)</li>
              <li>Improve AI models, workflows, and product design (subject to the AI training controls described below)</li>
            </ul>
          </section>

          <section className="terms-section">
            <h2>3. AI Features, Training, and Controls</h2>
            
            <h3>AI Processing</h3>
            <ul>
              <li>AI-powered features analyze inputs (e.g., code, prompts) to produce suggestions, generate code, and automate tasks. Processing generally occurs within our secure environment.</li>
            </ul>
            
            <h3>Training Use</h3>
            <ul>
              <li><strong>Default policy:</strong> We do not use your proprietary code or private data to train our general-purpose AI models without explicit consent.</li>
              <li><strong>Enterprise customers:</strong> May opt into custom arrangements or explicitly prohibit training use; Enterprise agreements can include stricter controls, data residency, or a formal Data Processing Agreement.</li>
            </ul>
            
            <h3>Bias & Responsibility</h3>
            <ul>
              <li>AI outputs may reflect biases present in training data. Review and test all generated code or outputs before relying on them in production.</li>
            </ul>
            
            <h3>Controls</h3>
            <ul>
              <li>You may control AI assistance levels and opt-out of analytics or training usage through application settings or account controls. Contact privacy@autowebiq.com for enterprise-level controls and custom agreements.</li>
            </ul>
          </section>

          <section className="terms-section">
            <h2>4. How We Share Information</h2>
            <p>We do not sell your personal information. We may share information in these situations:</p>
            
            <h3>Service Providers</h3>
            <ul>
              <li>Payment processors, cloud hosting, analytics, customer support platforms, AI infrastructure providers, monitoring and security services. These parties act on our behalf under contracts that require confidentiality and security.</li>
            </ul>
            
            <h3>Connected Third-Party Services</h3>
            <ul>
              <li>When you link third-party services (e.g., GitHub, MongoDB), we exchange the information necessary to enable the integration (authentication tokens with your permission, repository metadata, commit/pull request metadata, and sync data). Review third-party privacy policies before connecting.</li>
            </ul>
            
            <h3>Legal Requirements</h3>
            <ul>
              <li>To comply with lawful requests (e.g., court orders, subpoenas), to protect rights and safety, or to respond to legal processes.</li>
            </ul>
            
            <h3>Business Transfers</h3>
            <ul>
              <li>In the event of a merger, acquisition, bankruptcy, or sale of assets, user information may be transferred. We will provide notice of such change in ownership and updated privacy practices.</li>
            </ul>
            
            <h3>With Your Consent</h3>
            <ul>
              <li>Where you explicitly consent to sharing with other parties.</li>
            </ul>
            
            <h3>Enterprise Protections</h3>
            <ul>
              <li>For Enterprise accounts, we provide additional privacy protections: restrictions on training usage, contractual data handling terms, and limited third-party sharing as negotiated.</li>
            </ul>
          </section>

          <section className="terms-section">
            <h2>5. Data Retention</h2>
            <p>We retain personal information as necessary to provide Services and for legitimate business purposes, including:</p>
            <ul>
              <li>Account information while your account is active</li>
              <li>Usage and analytics data generally for up to 24 months (or as otherwise required)</li>
              <li>Backups and logs according to our backup and rotation policies</li>
              <li>Payment records as required by finance and tax regulations</li>
            </ul>
            <p>When data is no longer necessary, we delete or anonymize it in a secure manner. Specific retention periods may vary by data type and legal obligations.</p>
          </section>

          <section className="terms-section">
            <h2>6. Your Rights & Choices</h2>
            
            <h3>Account Controls</h3>
            <ul>
              <li>Review and update account information via application settings. You may request account deletion; certain records may be retained to comply with legal obligations.</li>
            </ul>
            
            <h3>Privacy Settings</h3>
            <ul>
              <li>Manage repository visibility, code-sharing preferences, third-party integrations, analytics participation, local vs. cloud execution, and AI assistance settings through the app.</li>
            </ul>
            
            <h3>Data Access & Portability</h3>
            <ul>
              <li>You may request a copy of personal data in a machine-readable format by contacting privacy@autowebiq.com.</li>
            </ul>
            
            <h3>Deletion & Restriction</h3>
            <ul>
              <li>Depending on law, you may request deletion, restriction, or correction of your personal data. We will respond in accordance with applicable data protection laws.</li>
            </ul>
            
            <h3>State-Specific Rights</h3>
            <ul>
              <li>California residents have rights under the CCPA/CPRA (right to know, delete, and opt-out of sale — we do not sell personal information). Residents of Colorado, Connecticut, Utah, and Virginia may have similar rights. Please contact privacy@autowebiq.com to exercise rights.</li>
            </ul>
            
            <h3>To Exercise Rights</h3>
            <ul>
              <li><strong>Email:</strong> privacy@autowebiq.com. We typically respond to privacy inquiries within 7 business days. For urgent matters, mark the subject line "PRIVACY URGENT".</li>
            </ul>
          </section>

          <section className="terms-section">
            <h2>7. Security</h2>
            <p>We implement administrative, technical, and physical safeguards designed to protect personal information, including:</p>
            <ul>
              <li>Encryption in transit and at rest where applicable</li>
              <li>Secure development lifecycle and code-signing practices</li>
              <li>Access controls and multi-factor authentication for employees</li>
              <li>Regular security assessments, penetration testing, and vulnerability management</li>
              <li>Employee security and privacy training</li>
            </ul>
            <p>No system is completely secure; we cannot guarantee absolute security. We will notify affected users in the event of certain security incidents in accordance with applicable laws.</p>
          </section>

          <section className="terms-section">
            <h2>8. Desktop Application Specifics</h2>
            <p>When you use our desktop application (installer or DMG):</p>
            <ul>
              <li><strong>Local Storage:</strong> Some project files, caches, and settings may be stored locally. You control what is stored locally versus in the cloud.</li>
              <li><strong>Installation Data:</strong> We may collect installation and update metrics to troubleshoot installs and deliver updates.</li>
              <li><strong>Automatic Updates:</strong> The app may check for and download updates to provide security and feature updates (you may be able to opt-out in settings).</li>
              <li><strong>System Integration:</strong> The app may integrate with local development tools (editors, terminals) as permitted by you.</li>
              <li><strong>Resource Monitoring:</strong> We may collect app performance metrics (CPU, memory) to optimize the app.</li>
            </ul>
            <p>You can change many of these behaviors from application preferences.</p>
          </section>

          <section className="terms-section">
            <h2>9. Third-Party Links & Services</h2>
            <p>Our Services may contain links to third-party websites and services. We are not responsible for their privacy practices. Review third-party privacy policies before providing personal data.</p>
          </section>

          <section className="terms-section">
            <h2>10. Children's Privacy</h2>
            <p>Our Services are not directed to children under the age of 13. We do not knowingly collect personal information from children under 13. If you believe we collected such information in error, contact privacy@autowebiq.com and we will promptly delete it.</p>
          </section>

          <section className="terms-section">
            <h2>11. International Transfers</h2>
            <p>AutoWebIQ is based in the United States and may operate services and vendors in India and other countries. If you are located outside these regions, your information may be transferred internationally. We take steps (e.g., contractual safeguards, standard contractual clauses) to protect data in transfers. By using the Services, you consent to such transfers.</p>
          </section>

          <section className="terms-section">
            <h2>12. Legal Bases for Processing (EEA/GDPR)</h2>
            <p>If you are in the European Economic Area (EEA), we process personal data based on legal grounds such as:</p>
            <ul>
              <li>Performance of a contract (providing Services)</li>
              <li>Legitimate interests (product improvement, security)</li>
              <li>Consent where requested (marketing, certain analytics)</li>
              <li>Compliance with legal obligations</li>
            </ul>
            <p>Contact privacy@autowebiq.com to exercise GDPR rights or to request a Data Processing Agreement (DPA).</p>
          </section>

          <section className="terms-section">
            <h2>13. Changes to This Policy</h2>
            <p>We may update this Privacy Policy to reflect changes in legal, operational, or product requirements. We will post the updated policy at autowebiq.com/privacy with a revised "Effective Date." For material changes, we will provide at least 30 days' notice via email or in-app notification where feasible. Continued use after changes constitutes acceptance.</p>
          </section>

          <section className="terms-section">
            <h2>14. Contact & Data Requests</h2>
            <p><strong>Privacy & Data Requests:</strong> privacy@autowebiq.com</p>
            <p><strong>Support & General Inquiries:</strong> support@autowebiq.com</p>
            <p><strong>Mailing address:</strong><br />
            AutoWebIQ Inc.<br />
            Saidulajab, New Delhi - 110017</p>
            <p>For urgent matters, include "PRIVACY URGENT" in your subject line. We aim to respond to privacy requests within 7 business days.</p>
          </section>

          <section className="terms-section">
            <h2>15. Miscellaneous</h2>
            <p>This Privacy Policy is part of and governed by our Terms of Service. If any provision conflicts with the Terms of Service, the Terms will prevail unless stated otherwise.</p>
          </section>

          <div className="last-updated">
            <p><strong>Last Updated:</strong> October 28, 2025</p>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="terms-footer">
        <div className="footer-container-terms">
          <div className="footer-brand">
            <div className="brand-icon">
              <Sparkles size={24} />
            </div>
            <span>AutoWebIQ</span>
          </div>
          <p className="footer-text">© 2025 AutoWebIQ. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
};

export default PrivacyPolicy;
