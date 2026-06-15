<template>
  <div class="card">
    <div class="card-header">
      <h5>Two-Factor Authentication (2FA)</h5>
    </div>
    <div class="card-body">
      <div class="d-flex justify-content-between align-items-center">
        <div>
          <p class="mb-0">Protect your account with 2FA</p>
          <small class="text-muted">{{ is2FAEnabled ? 'Enabled' : 'Disabled' }}</small>
        </div>
        <button v-if="!is2FAEnabled" class="btn btn-primary" @click="openSetup">Enable 2FA</button>
        <button v-else class="btn btn-danger" @click="disable2FA">Disable 2FA</button>
      </div>
    </div>

    <!-- Setup Modal -->
    <div class="modal fade" id="setup2FAModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5>Enable 2FA</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div v-if="!qrCode">
              <button class="btn btn-primary" @click="startSetup">Generate QR Code</button>
            </div>
            <div v-else>
              <img :src="qrCode" class="img-fluid mb-3">
              <p>Secret: <code>{{ secret }}</code></p>
              <input type="text" class="form-control" v-model="otpCode" placeholder="6-digit code">
              <button class="btn btn-success mt-2" @click="verify2FA">Verify & Enable</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { Modal } from 'bootstrap';
import { API_URL } from '../config';

export default {
  name: 'TwoFactorSetup',
  data() {
    return {
      is2FAEnabled: false,
      qrCode: null,
      secret: null,
      otpCode: '',
      modal: null
    }
  },
  mounted() {
    this.checkStatus();
    this.modal = new Modal(document.getElementById('setup2FAModal'));
  },
  methods: {
    async checkStatus() {
      try {
        const res = await axios.get(`${API_URL}/auth/2fa/status`);
        this.is2FAEnabled = res.data.is_enabled;
      } catch (err) {}
    },
    openSetup() {
      this.qrCode = null;
      this.secret = null;
      this.otpCode = '';
      this.modal.show();
    },
    async startSetup() {
      const res = await axios.post(`${API_URL}/auth/2fa/setup`);
      this.qrCode = res.data.qr_code;
      this.secret = res.data.secret;
    },
    async verify2FA() {
      await axios.post(`${API_URL}/auth/2fa/verify`, {
        secret: this.secret,
        token: this.otpCode
      });
      this.is2FAEnabled = true;
      this.modal.hide();
      alert('2FA enabled!');
    },
    async disable2FA() {
      await axios.post(`${API_URL}/auth/2fa/disable`);
      this.is2FAEnabled = false;
      alert('2FA disabled');
    }
  }
}
</script>