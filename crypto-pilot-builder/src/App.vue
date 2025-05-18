<template>
  <div class="app-container">
    <Wallet />
    <ChatBot />
  </div>
</template>

<script setup>
import Wallet from './components/wallet.vue'
import ChatBot from './components/chatbot.vue'
</script>

<style scoped>
.app-container {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  min-height: 100vh;
  background-color: #eef1f5;
  padding-top: 0rem;
}
</style>
