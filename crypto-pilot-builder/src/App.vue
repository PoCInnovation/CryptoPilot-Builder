<template>
  <div class="app-container">
    <ChatBot />
  </div>
</template>

<script setup>
import ChatBot from './components/chatbot.vue'
</script>

<style scoped>
.app-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #eef1f5;
}
</style>
