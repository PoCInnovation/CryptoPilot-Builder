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
import { marked } from 'marked'

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

// Configuration de marked pour un rendu sécurisé
marked.setOptions({
  breaks: true,
  gfm: true,
  sanitize: false, // Nous faisons confiance au contenu de l'IA
  smartLists: true,
  smartypants: true
})

function formatMessage(text) {
  if (!text) return ''

  // Détecter si le texte contient du markdown
  const hasMarkdown = /^#+\s|^\*\*|^\- |^\* |^\d+\.|^>|^\|/.test(text.trim()) ||
                     /\*\*.*\*\*|__.*__|\*.*\*|_.*_|`.*`|\[.*\]\(.*\)/.test(text) ||
                     text.includes('```') || text.includes('##') || text.includes('**')

  console.log('FormatMessage - Text:', text.substring(0, 100) + '...')
  console.log('FormatMessage - HasMarkdown:', hasMarkdown)

  if (hasMarkdown) {
    try {
      const rendered = marked.parse(text)
      console.log('FormatMessage - Rendered:', rendered.substring(0, 100) + '...')
      return rendered
    } catch (error) {
      console.warn('Erreur lors du rendu markdown:', error)
      // Fallback vers le formatage basique
      return text
        .replace(/\\n\\n/g, '<br><br>')
        .replace(/\\n/g, '<br>')
        .replace(/- /g, '• ')
    }
  }

  // Pour les messages de l'IA, essayer toujours le rendu markdown
  // car l'IA peut générer du markdown même si notre détection échoue
  try {
    const rendered = marked.parse(text)
    console.log('FormatMessage - Force markdown rendered:', rendered.substring(0, 100) + '...')
    return rendered
  } catch (error) {
    console.warn('Erreur lors du rendu markdown forcé:', error)
    // Fallback vers le formatage basique
    return text
      .replace(/\\n\\n/g, '<br><br>')
      .replace(/\\n/g, '<br>')
      .replace(/- /g, '• ')
  }
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

/* Styles pour le rendu markdown */
.message :deep(h1),
.message :deep(h2),
.message :deep(h3),
.message :deep(h4),
.message :deep(h5),
.message :deep(h6) {
  color: #ffffff;
  margin: 0.5rem 0;
  font-weight: bold;
}

.message :deep(h1) { font-size: 1.5rem; }
.message :deep(h2) { font-size: 1.3rem; }
.message :deep(h3) { font-size: 1.1rem; }

.message :deep(p) {
  margin: 0.5rem 0;
  line-height: 1.6;
}

.message :deep(ul),
.message :deep(ol) {
  margin: 0.5rem 0;
  padding-left: 1.5rem;
}

.message :deep(li) {
  margin: 0.25rem 0;
}

.message :deep(strong),
.message :deep(b) {
  font-weight: bold;
  color: #ffffff;
}

.message :deep(em),
.message :deep(i) {
  font-style: italic;
}

.message :deep(code) {
  background-color: #2d3748;
  color: #68d391;
  padding: 0.2rem 0.4rem;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
}

.message :deep(pre) {
  background-color: #2d3748;
  color: #ffffff;
  padding: 1rem;
  border-radius: 8px;
  overflow-x: auto;
  margin: 0.5rem 0;
  border: 1px solid #4a5568;
}

.message :deep(pre code) {
  background-color: transparent;
  color: inherit;
  padding: 0;
  border-radius: 0;
}

.message :deep(blockquote) {
  border-left: 4px solid #4a5568;
  padding-left: 1rem;
  margin: 0.5rem 0;
  color: #a0aec0;
  font-style: italic;
}

.message :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 0.5rem 0;
}

.message :deep(th),
.message :deep(td) {
  border: 1px solid #4a5568;
  padding: 0.5rem;
  text-align: left;
}

.message :deep(th) {
  background-color: #2d3748;
  font-weight: bold;
}

.message :deep(a) {
  color: #63b3ed;
  text-decoration: underline;
}

.message :deep(a:hover) {
  color: #90cdf4;
}
</style>
