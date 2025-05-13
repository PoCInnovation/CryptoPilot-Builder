<template>
  <div class="chat-main">
    <div class="messages" ref="messagesContainer">
      <div v-for="(msg, index) in messages" :key="index" :class="['msg', msg.isUser ? 'user' : 'bot']">
        <div class="bubble">
          {{ msg.text }}
        </div>
      </div>
    </div>
    <form class="chat-input" @submit.prevent="send">
      <input v-model="input" placeholder="Écris ton message..." autocomplete="off" />
      <button type="submit">Envoyer</button>
    </form>
  </div>
</template>

<script setup>
import { ref, watch, nextTick, onMounted } from 'vue';
const props = defineProps({ chatId: Number });

const chatsMessages = ref({});
const input = ref('');
const messages = ref([]);
const messagesContainer = ref(null);

watch(() => props.chatId, (newId) => {
  messages.value = chatsMessages.value[newId] || [
    { text: 'Bonjour ! Posez-moi une question.', isUser: false }
  ];
  scrollToBottom();
}, { immediate: true });

function scrollToBottom() {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
    }
  });
}

onMounted(scrollToBottom);

async function send() {
  const text = input.value.trim();
  if (!text) return;
  messages.value.push({ text, isUser: true });
  input.value = '';
  scrollToBottom();
  try {
    const response = await fetch('http://localhost:5000/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text }),
    });
    const data = await response.json();
    let botResponse = data?.response?.content || data?.response || 'Réponse vide.';
    messages.value.push({ text: botResponse, isUser: false });
    chatsMessages.value[props.chatId] = [...messages.value];
    scrollToBottom();
  } catch (err) {
    messages.value.push({ text: "Erreur de communication avec l'IA.", isUser: false });
    scrollToBottom();
  }
}
</script>

<style scoped>
.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #fff;
}
.messages {
  flex: 1;
  overflow-y: auto;
  padding: 2rem 0 1rem 0;
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
  min-height: 0;
}
.msg {
  display: flex;
  align-items: flex-end;
  padding: 0 2rem;
}
.msg.user {
  justify-content: flex-end;
}
.bubble {
  background: #f0f0f0;
  color: #232b4a;
  border-radius: 16px;
  padding: 1rem 1.5rem;
  max-width: 60vw;
  box-shadow: 0 2px 8px #0001;
  font-size: 1.1rem;
  word-break: break-word;
}
.msg.user .bubble {
  background: #e6f7ff;
  color: #232b4a;
}
.chat-input {
  display: flex;
  gap: 1rem;
  background: #fafbfc;
  border-top: 1px solid #eee;
  padding: 1.2rem 2rem;
  position: sticky;
  bottom: 0;
  z-index: 2;
}
.chat-input input {
  flex: 1;
  border: 1px solid #ddd;
  background: #fff;
  color: #232b4a;
  font-size: 1.1rem;
  border-radius: 8px;
  padding: 0.7rem 1rem;
  outline: none;
}
.chat-input button {
  background: #232b4a;
  color: #fff;
  border: none;
  border-radius: 8px;
  padding: 0.7rem 1.5rem;
  font-weight: bold;
  font-size: 1rem;
  cursor: pointer;
  transition: background 0.2s;
}
.chat-input button:hover {
  background: #3a1c71;
}
</style> 