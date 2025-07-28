<template>
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
</template>

<script setup>
import { ref, nextTick, onMounted, watch } from 'vue'

const props = defineProps({
  messages: {
    type: Array,
    required: true
  },
  isLoading: {
    type: Boolean,
    default: false
  }
})

const messagesContainer = ref(null)
const shouldAutoScroll = ref(true)

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

watch(() => props.messages, () => {
  scrollToBottom()
}, { deep: true })
</script>

<style scoped>
.messages {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  color: black;
  gap: 0.5rem;
  padding: 0.5rem;
  background-color: #111421;
  border-radius: 8px;
  max-height: 80%;
}

.message {
  padding: 0.75rem 1rem;
  border-radius: 10px;
  word-wrap: break-word;
  line-height: 1.4;
  color: white;
  max-width: 70%;
}

.message.user {
  background-color: #000000;
  color: white;
  align-self: flex-end;
  color: black;
}

.message.bot {
  background-color: #111421;
  align-self: flex-start;
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