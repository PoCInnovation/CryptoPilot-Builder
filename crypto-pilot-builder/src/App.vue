<template>
  <div class="app-container">
    <Wallet ref="walletComponent" />
    <ChatBot />
  </div>
</template>

<script setup>
import { ref, provide } from 'vue'
import Wallet from './components/wallet.vue'
import ChatBot from './components/chatbot.vue'

const walletComponent = ref(null)

provide('walletFunctions', {
  sendTransaction: (recipient, amount) => {
    if (walletComponent.value) {
      return walletComponent.value.sendTransactionFromChat(recipient, amount)
    }
    throw new Error('Wallet non disponible')
  },
  getAddress: () => {
    return walletComponent.value?.address || null
  },
  isConnected: () => {
    return !!(walletComponent.value?.address)
  }
})
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