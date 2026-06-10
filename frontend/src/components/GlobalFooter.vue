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
          </ul>
        </div>
        
        <div class="footer-section">
          <h6>Info</h6>
          <ul class="footer-links">
            <li><a href="#" @click.prevent="showAbout">About</a></li>
            <li><a href="#" @click.prevent="showPrivacy">Privacy</a></li>
            <li><a href="#" @click.prevent="showTerms">Terms</a></li>
          </ul>
        </div>
        
        <div class="footer-section">
          <h6>Connect</h6>
          <div class="social-links">
            <a href="#" class="social-icon"><i class="bi bi-github"></i></a>
            <a href="#" class="social-icon"><i class="bi bi-twitter-x"></i></a>
            <a href="#" class="social-icon"><i class="bi bi-envelope"></i></a>
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
          Version 1.0.0
        </p>
      </div>
    </div>
  </footer>
</template>

<script>
export default {
  name: 'GlobalFooter',
  computed: {
    currentYear() {
      return new Date().getFullYear();
    }
  },
  methods: {
    showAbout() {
      alert('Skay Finance - Personal Finance Management App\n\nTrack your expenses, manage accounts, and achieve your financial goals.');
    },
    showPrivacy() {
      alert('Privacy Policy\n\nYour data is stored locally or on your own server. We do not share your financial data with third parties.');
    },
    showTerms() {
      alert('Terms of Service\n\nThis application is provided for personal use. Use at your own risk.');
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

/* Dark mode support */
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

/* Responsive */
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