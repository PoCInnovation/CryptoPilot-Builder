<template>
  <div class="chat-container">
    <aside class="sidebar">
      <h2>Discussions</h2>
      <ul>
        <li
          v-for="(chat, index) in chats"
          :key="index"
          @click="selectChat(index)"
          :class="{ active: selectedChat === index }"
        >
          {{ chat }}
        </li>
        <li class="add-chat" @click="addNewChat">+ Nouveau chat</li>
      </ul>
    </aside>

    <main class="chat-main">
      <div class="messages" ref="messagesContainer">
        <div
          v-for="(msg, index) in messages"
          :key="index"
          :class="['message', msg.isUser ? 'user' : 'bot']"
        >
          <div v-html="formatMessage(msg.text)"></div>
        </div>
        <div v-if="isLoading" class="message bot loading">
          <div class="loading-dots">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      </div>

      <form @submit.prevent="sendMessage" class="input-form">
        <div class="input-bubble-container">
          <input
            v-model="newMessage"
            placeholder="Écrire un message..."
            class="input-bubble"
          />
        </div>
        <button type="submit" class="send-button">➤</button>
      </form>
    </main>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted, watch } from 'vue'

const messages = ref([
  { text: 'Bonjour ! Posez-moi une question.', isUser: false }
])
const isLoading = ref(false)
const shouldAutoScroll = ref(true)
const chats = ref(['Chat 1'])
const selectedChat = ref(0)
const newMessage = ref('')
const messagesContainer = ref(null)

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

function formatMessage(text) {
  if (!text) return ''
  return text
    .replace(/\\n\\n/g, '<br><br>')
    .replace(/\\n/g, '<br>')
    .replace(/- /g, '• ')
}

function scrollToBottom() {
  nextTick(() => {
    if (messagesContainer.value && shouldAutoScroll.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

function handleScroll() {
  if (!messagesContainer.value) return
  
  const { scrollTop, scrollHeight, clientHeight } = messagesContainer.value
  const isAtBottom = scrollHeight - scrollTop - clientHeight < 10
  shouldAutoScroll.value = isAtBottom
}

onMounted(() => {
  if (messagesContainer.value) {
    messagesContainer.value.addEventListener('scroll', handleScroll)
  }
})

watch(messages, () => {
  scrollToBottom()
}, { deep: true })

async function sendMessage() {
  const text = newMessage.value.trim()
  if (!text) return

  messages.value.push({ text, isUser: true })
  newMessage.value = ''
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

  scrollToBottom()
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

.sidebar {
  width: 250px;
  background-color: #f9f9f9;
  border-right: 1px solid #ddd;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  color: black;
}

.sidebar h2 {
  font-size: 1.2rem;
  margin-bottom: 0.5rem;
}

.sidebar ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.sidebar li {
  padding: 0.75rem;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.3s;
}

.sidebar li:hover,
.sidebar li.active {
  background-color: #e0e0e0;
}

.sidebar .add-chat {
  color: #4caf50;
  font-weight: bold;
}

.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 1rem;
  background-color: #fff;
}

.messages {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  color: black;
  gap: 0.5rem;
  padding: 0.5rem;
  background-color: #f0f0f0;
  border-radius: 8px;
  max-height: 80%;
}

.message {
  padding: 0.75rem 1rem;
  border-radius: 10px;
  word-wrap: break-word;
  line-height: 1.4;
  color: black;
  max-width: 70%;
}

.message.user {
  background-color: #dcf8c6;
  align-self: flex-end;
}

.message.bot {
  background-color: #ececec;
  align-self: flex-start;
}

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

.loading-dots {
  display: flex;
  gap: 4px;
  padding: 8px 12px;
}

.loading-dots span {
  width: 8px;
  height: 8px;
  background-color: #666;
  border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out;
}

.loading-dots span:nth-child(1) {
  animation-delay: -0.32s;
}

.loading-dots span:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes bounce {
  0%, 80%, 100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}

.message.loading {
  background-color: #ececec;
  align-self: flex-start;
  min-height: 40px;
  display: flex;
  align-items: center;
}
</style>
