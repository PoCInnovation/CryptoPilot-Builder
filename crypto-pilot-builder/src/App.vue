<template>
  <div class="chat-container">
    <aside class="sidebar">
      <h2>Discussions</h2>
      <ul>
        <li v-for="(chat, index) in chats" :key="index" @click="selectChat(index)" :class="{ active: selectedChat === index }">
          {{ chat }}
        </li>
      </ul>
    </aside>

    <main class="chat-main">
      <div class="messages" ref="messagesContainer">
        <div v-for="(msg, index) in messages" :key="index" :class="['message', msg.isUser ? 'user' : 'bot']">
          <div v-html="formatMessage(msg.text)"></div>
        </div>
      </div>

      <form @submit.prevent="sendMessage" class="input-form">
        <div class="input-bubble-container">
          <input v-model="newMessage" placeholder="Écrire un message..." class="input-bubble" />
        </div>
        <button type="submit" class="send-button">➤</button>
      </form>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const messages = ref([
  { text: 'Bonjour ! Posez-moi une question.', isUser: false }
])

const chats = ref(['Chat 1'])
const selectedChat = ref(0)
const newMessage = ref('')

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
  if (!text)
    return '';
  let formattedText = text
    .replace(/\\n\\n/g, '<br><br>')
    .replace(/\\n/g, '<br>')
    .replace(/- /g, '• ');
  return formattedText;
}

const sendMessage = async () => {
  const text = newMessage.value.trim()
  if (!text) return

  messages.value.push({ text, isUser: true })
  newMessage.value = ''

  try {
    const response = await fetch('http://localhost:5000/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message: text }),
    })

    const data = await response.json()
    if (data && data.response) {
      let botResponse;
      if (typeof data.response === 'string') {
        botResponse = data.response.trim();
      } else if (data.response.content) {
        botResponse = data.response.content;
      }
      if (botResponse) {
        messages.value.push({ text: botResponse, isUser: false })
      } else {
        throw new Error('Réponse vide de l\'API.')
      }
    } else {
      throw new Error('Réponse invalide ou mal formatée de l\'API.')
    }
  } catch (err) {
    console.error('Erreur lors de l\'exécution de l\'API:', err)
    messages.value.push({
      text: "Erreur de communication avec l'IA locale.",
      isUser: false
    })
  }

  scrollToBottom()
}

const messagesContainer = ref(null)
const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}
</script>

<style scoped>
.chat-container {
  display: flex;
  height: 90vh;
  width: 80vw;
  margin-left: auto;
  border: 1px solid #ccc;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  background-color: #fff;
}

.sidebar {
  width: 250px;
  background-color: #f9f9f9;
  border-right: 1px solid #ddd;
  padding: 1rem;
  display: flex;
  color: black;
  flex-direction: column;
  gap: 1rem;
}

.sidebar h2 {
  font-size: 1.2rem;
  margin: 0 0 0.5rem 0;
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
  max-width: 70%;
}

.message.user {
  background-color: #dcf8c6;
  color: black;
  align-self: flex-end;
}

.message.bot {
  background-color: #ececec;
  color: black;
  align-self: flex-start;
}

.message ul {
  margin-top: 0.5rem;
  margin-bottom: 0.5rem;
  padding-left: 1.5rem;
}

.message li {
  margin-bottom: 0.25rem;
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
</style>