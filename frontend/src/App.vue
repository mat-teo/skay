<template>
  <div>
    <nav class="navbar navbar-dark bg-dark mb-4">
      <div class="container">
        <a class="navbar-brand fw-bold" href="#">Skay Finance</a>
      </div>
    </nav>

    <main class="container">
      <div class="row">
        <div class="col-12 col-lg-5 mb-4">
          <AccountsList ref="accountsList" />
        </div>
        
        <div class="col-12 col-lg-7 mb-4">
          <TransactionsList @transaction-saved="refreshAccountsData" />
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import AccountsList from './components/AccountsList.vue';
import TransactionsList from './components/TransactionsList.vue';

export default {
  name: 'App',
  components: {
    AccountsList,
    TransactionsList
  },
  methods: {
    refreshAccountsData() {
      // Accessing the fetchAccounts method inside AccountsList component via Vue refs
      if (this.$refs.accountsList) {
        this.$refs.accountsList.fetchAccounts();
      }
    }
  }
};
</script>