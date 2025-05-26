<template>
  <form @submit.prevent="handleSubmit" class="input-form">
    <div class="input-bubble-container">
      <input
        v-model="newMessage"
        placeholder="Écrire un message..."
        class="input-bubble"
      />
    </div>
    <button type="submit" class="send-button">➤</button>
  </form>
</template>

<script setup>
import { ref } from 'vue'

const newMessage = ref('')

const emit = defineEmits(['send-message'])

function handleSubmit() {
  emit('send-message', newMessage.value)
  newMessage.value = ''
}
</script>

<style scoped>
.input-form {
  display: flex;
  gap: 0.5rem;
  margin-top: 1rem;
  align-items: center;
}

.input-bubble-container {
  flex: 1;
  background-color: #f0f0f0;
  border-radius: 20px;
  padding: 0.2rem 0.5rem;
  display: flex;
  align-items: center;
}

.input-bubble {
  flex: 1;
  border: none;
  outline: none;
  background-color: transparent;
  padding: 0.5rem 0.75rem;
  font-size: 1rem;
  border-radius: 16px;
}

.input-bubble::placeholder {
  color: #aaa;
}

.input-bubble:focus {
  background-color: #e9e9e9;
}

.send-button {
  background-color: #4caf50;
  color: white;
  border: none;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  font-size: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.send-button:hover {
  background-color: #45a049;
}
</style>
