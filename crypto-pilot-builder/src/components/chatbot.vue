<template>
  <div class="chat-container">
    <ChatSidebar
      :chats="chats"
      :selected-chat="selectedChat"
      @select-chat="selectChat"
      @add-chat="addNewChat"
    />

    <main class="chat-main">
      <ChatMessages
        :messages="messages"
        :is-loading="isLoading"
      />

      <ChatInput @send-message="sendMessage" />
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import ChatSidebar from './chatbot/ChatSidebar.vue'
import ChatMessages from './chatbot/ChatMessages.vue'
import ChatInput from './chatbot/ChatInput.vue'

const messages = ref([
  { text: 'Bonjour ! Posez-moi une question.', isUser: false }
])

const chats = ref(['Chat 1'])
const selectedChat = ref(0)
const isLoading = ref(false)

function selectChat(index) {
  selectedChat.value = index
  messages.value = [
    { text: `Contenu du ${chats.value[index]}`, isUser: false }
  ]
}

function addNewChat() {
  const index = chats.value.length + 1
  chats.value.push(`Chat ${index}`)
  selectChat(chats.value.length - 1)
}

async function sendMessage(text) {
  if (!text.trim()) return

  messages.value.push({ text, isUser: true })
  isLoading.value = true

  try {
    const response = await fetch('http://localhost:5000/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text })
    })

    const data = await response.json()
    let botResponse = data?.response?.content || data?.response || ''

    if (botResponse.trim()) {
      messages.value.push({ text: botResponse.trim(), isUser: false })
    } else {
      throw new Error('Réponse vide de l\'API.')
    }
  } catch (err) {
    console.error('Erreur API :', err)
    messages.value.push({
      text: "Erreur de communication avec l'IA locale.",
      isUser: false
    })
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.chat-container {
  display: flex;
  height: 90vh;
  width: 80vw;
  border: 1px solid #ccc;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  background-color: black;
}

.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 1rem;
  background-color: #fff;
}
</style>
