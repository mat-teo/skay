<template>
  <footer class="global-footer">
    <div class="container">
      <div class="footer-content">
        <div class="footer-section">
          <h5>Skay Finance</h5>
          <p class="text-muted small">Personal finance management made simple.</p>
        </div>
        
        <div class="footer-section">
          <h6>Quick Links</h6>
          <ul class="footer-links">
            <li><router-link to="/dashboard">Dashboard</router-link></li>
            <li><router-link to="/transactions">Transactions</router-link></li>
            <li><router-link to="/stats">Statistics</router-link></li>
            <li><router-link to="/categories">Categories</router-link></li>
            <li><router-link to="/profile">Profile</router-link></li>
          </ul>
        </div>
        
        <div class="footer-section">
          <h6>Legal</h6>
          <ul class="footer-links">
            <li><a href="#" @click.prevent="openModal('privacy')">Privacy Policy</a></li>
            <li><a href="#" @click.prevent="openModal('terms')">Terms of Service</a></li>
            <li><a href="#" @click.prevent="openModal('cookies')">Cookie Policy</a></li>
          </ul>
        </div>
        
        <div class="footer-section">
          <h6>Connect</h6>
          <div class="social-links">
            <a href="https://github.com/mat-teo/skay" target="_blank" rel="noopener noreferrer" class="social-icon">
              <i class="bi bi-github"></i>
            </a>
            <a href="mailto:mat27art@hotmail.com" class="social-icon">
              <i class="bi bi-envelope"></i>
            </a>
          </div>
          <p class="small text-muted mt-2">
            <i class="bi bi-code-slash"></i> Built with FastAPI & Vue.js
          </p>
        </div>
      </div>
      
      <div class="footer-bottom">
        <p class="small text-muted mb-0">
          &copy; {{ currentYear }} Skay Finance. All rights reserved.
        </p>
        <p class="small text-muted mb-0">
          Version 0.9.0
        </p>
      </div>
    </div>

    <!-- Legal Modals -->
    <LegalModal 
      modal-id="privacyModal"
      title="Privacy Policy"
      :content="privacyContent"
    />
    <LegalModal 
      modal-id="termsModal"
      title="Terms of Service"
      :content="termsContent"
    />
    <LegalModal 
      modal-id="cookiesModal"
      title="Cookie Policy"
      :content="cookiesContent"
    />
  </footer>
</template>

<script>
import LegalModal from './LegalModal.vue'
import { Modal } from 'bootstrap'

export default {
  name: 'GlobalFooter',
  components: { LegalModal },
  computed: {
    currentYear() {
      return new Date().getFullYear();
    },
    privacyContent() {
      return `
        <h6>Privacy Policy for Skay Finance</h6>
        <p><strong>Effective Date:</strong> June 15, 2026</p>
        
        <h6>1. Data Collection</h6>
        <p>Skay Finance collects the following personal information:</p>
        <ul>
          <li>Email address (for account identification and password recovery)</li>
          <li>Financial transaction data (amounts, categories, dates, notes)</li>
          <li>Account balances and financial preferences</li>
        </ul>
        
        <h6>2. Data Storage</h6>
        <p>Your data is stored securely in a PostgreSQL database. If you self-host, all data remains on your own infrastructure.</p>
        
        <h6>3. Data Usage</h6>
        <p>We use your data solely to provide the core functionality of the application: tracking income, expenses, accounts, categories, and generating financial reports.</p>
        
        <h6>4. Data Sharing</h6>
        <p>We do NOT sell, rent, or share your personal or financial data with third parties. All data is used exclusively within Skay Finance.</p>
        
        <h6>5. Data Security</h6>
        <p>Passwords are hashed using bcrypt. JWT tokens are used for authentication. All API communication should be over HTTPS in production.</p>
        
        <h6>6. User Rights</h6>
        <p>You have the right to access, modify, or delete your personal data at any time through the application interface.</p>
        
        <h6>7. Data Retention</h6>
        <p>Your data is retained as long as your account is active. Upon account deletion, all associated data is permanently removed.</p>
        
        <h6>8. Contact</h6>
        <p>For privacy concerns, contact: <a href="mailto:mat27art@hotmail.com">mat27art@hotmail.com</a></p>
      `;
    },
    termsContent() {
      return `
        <h6>Terms of Service for Skay Finance</h6>
        <p><strong>Effective Date:</strong> June 15, 2026</p>
        
        <h6>1. Acceptance of Terms</h6>
        <p>By using Skay Finance, you agree to these Terms of Service.</p>
        
        <h6>2. Description of Service</h6>
        <p>Skay Finance provides personal financial management tools including transaction tracking, account management, budgeting, and financial reporting.</p>
        
        <h6>3. User Responsibilities</h6>
        <p>You are responsible for:</p>
        <ul>
          <li>Maintaining the confidentiality of your account credentials</li>
          <li>All activities that occur under your account</li>
          <li>Ensuring the accuracy of the financial data you enter</li>
        </ul>
        
        <h6>4. Prohibited Activities</h6>
        <p>You may not:</p>
        <ul>
          <li>Use the service for any illegal purpose</li>
          <li>Attempt to gain unauthorized access to other users' data</li>
          <li>Reverse engineer or modify the application</li>
        </ul>
        
        <h6>5. Data Accuracy</h6>
        <p>Skay Finance is a tool for tracking your finances. We are not responsible for any financial decisions made based on the data you enter.</p>
        
        <h6>6. Service Availability</h6>
        <p>We strive to maintain high availability but do not guarantee uninterrupted service.</p>
        
        <h6>7. Limitation of Liability</h6>
        <p>Skay Finance is provided "as is" without warranties. We are not liable for any financial losses or damages resulting from use of this application.</p>
        
        <h6>8. Modifications</h6>
        <p>We reserve the right to modify these terms at any time. Continued use constitutes acceptance of modified terms.</p>
        
        <h6>9. Termination</h6>
        <p>We reserve the right to suspend or terminate accounts that violate these terms.</p>
        
        <h6>10. Contact</h6>
        <p>Questions? Contact: <a href="mailto:mat27art@hotmail.com">mat27art@hotmail.com</a></p>
      `;
    },
    cookiesContent() {
      return `
        <h6>Cookie Policy for Skay Finance</h6>
        <p><strong>Effective Date:</strong> June 15, 2026</p>
        
        <h6>1. What Are Cookies</h6>
        <p>Cookies are small text files stored on your device that help websites function properly.</p>
        
        <h6>2. Cookies We Use</h6>
        <p>Skay Finance uses the following cookies:</p>
        <ul>
          <li><strong>Authentication Token (JWT):</strong> Stored in localStorage to keep you logged in</li>
          <li><strong>Dark Mode Preference:</strong> Saved in localStorage to remember your theme preference</li>
        </ul>
        <p><strong>Note:</strong> Skay Finance does NOT use tracking cookies, analytics cookies, or third-party advertising cookies.</p>
        
        <h6>3. Managing Cookies</h6>
        <p>You can clear localStorage data through your browser settings. Note that doing so will log you out and reset your theme preference.</p>
        
        <h6>4. Third-Party Cookies</h6>
        <p>We do not use any third-party cookies. All data storage is local to your browser and our database.</p>
        
        <h6>5. Contact</h6>
        <p>For cookie-related questions: <a href="mailto:mat27art@hotmail.com">mat27art@hotmail.com</a></p>
      `;
    }
  },
  methods: {
    openModal(type) {
      let modalId;
      switch(type) {
        case 'privacy':
          modalId = 'privacyModal';
          break;
        case 'terms':
          modalId = 'termsModal';
          break;
        case 'cookies':
          modalId = 'cookiesModal';
          break;
        default:
          return;
      }
      const modalElement = document.getElementById(modalId);
      if (modalElement) {
        const modal = new Modal(modalElement);
        modal.show();
      }
    }
  }
};
</script>

<style scoped>
.global-footer {
  background-color: #f8f9fa;
  border-top: 1px solid rgba(0, 0, 0, 0.05);
  margin-top: 60px;
  padding: 48px 0 24px 0;
}

.dark-theme .global-footer {
  background-color: #1c1c1e;
  border-top-color: rgba(255, 255, 255, 0.05);
}

.footer-content {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1.5fr;
  gap: 40px;
  margin-bottom: 40px;
}

.footer-section h5 {
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 12px;
  color: #1d1d1f;
}

.footer-section h6 {
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 16px;
  color: #86868b;
}

.footer-links {
  list-style: none;
  padding: 0;
  margin: 0;
}

.footer-links li {
  margin-bottom: 8px;
}

.footer-links a {
  color: #515154;
  text-decoration: none;
  font-size: 0.875rem;
  transition: color 0.2s ease;
}

.footer-links a:hover {
  color: #4f46e5;
}

.dark-theme .footer-links a {
  color: #8e8e93;
}

.dark-theme .footer-links a:hover {
  color: #6366f1;
}

.social-links {
  display: flex;
  gap: 16px;
}

.social-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background-color: rgba(0, 0, 0, 0.04);
  color: #515154;
  transition: all 0.2s ease;
}

.social-icon:hover {
  background-color: #4f46e5;
  color: white;
  transform: translateY(-2px);
}

.dark-theme .social-icon {
  background-color: rgba(255, 255, 255, 0.08);
  color: #8e8e93;
}

.dark-theme .social-icon:hover {
  background-color: #4f46e5;
  color: white;
}

.footer-bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 24px;
  border-top: 1px solid rgba(0, 0, 0, 0.05);
}

.dark-theme .footer-bottom {
  border-top-color: rgba(255, 255, 255, 0.05);
}

@media (max-width: 768px) {
  .global-footer {
    padding: 32px 0 20px 0;
    margin-top: 40px;
  }
  
  .footer-content {
    grid-template-columns: 1fr;
    gap: 24px;
    text-align: center;
  }
  
  .social-links {
    justify-content: center;
  }
  
  .footer-bottom {
    flex-direction: column;
    gap: 8px;
    text-align: center;
  }
}
</style>