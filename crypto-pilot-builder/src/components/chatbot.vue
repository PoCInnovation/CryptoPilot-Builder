<template>
  <div class="chat-container">
    <ChatSidebar
      :chats="chats"
      :selected-chat="selectedChat"
      @select-chat="selectChat"
      @add-chat="addNewChat"
    />

    <main class="chat-main">
      <div class="chat-header">
        <h3>Session: {{ currentSessionId ? currentSessionId.substring(0, 8) + '...' : 'Nouvelle session' }}</h3>
      </div>

      <ChatMessages
        :messages="messages"
        :is-loading="isLoading"
      />

      <!-- Modal de confirmation de transaction -->
      <div v-if="pendingTransaction" class="transaction-modal-overlay">
        <div class="transaction-modal">
          <h3>🔐 Confirmation de transaction</h3>
          <div class="transaction-details">
            <p><strong>Destinataire :</strong> {{ pendingTransaction.recipient }}</p>
            <p><strong>Montant :</strong> {{ pendingTransaction.amount }} {{ pendingTransaction.currency?.toUpperCase() }}</p>
          </div>
          <div class="transaction-actions">
            <button @click="confirmTransaction" class="confirm-btn">✅ Confirmer</button>
            <button @click="cancelTransaction" class="cancel-btn">❌ Annuler</button>
          </div>
        </div>
      </div>

      <ChatInput @send-message="sendMessage" />
    </main>
  </div>
</template>

<script setup>
import { ref, inject, onMounted } from 'vue'
import ChatSidebar from './chatbot/ChatSidebar.vue'
import ChatMessages from './chatbot/ChatMessages.vue'
import ChatInput from './chatbot/ChatInput.vue'

const messages = ref([
  { text: 'Bonjour ! Posez-moi une question ou demandez-moi d\'effectuer une transaction.', isUser: false }
])

const chats = ref([])
const selectedChat = ref(0)
const isLoading = ref(false)
const pendingTransaction = ref(null)
const currentSessionId = ref(null)

// Stockage des sessions avec leurs messages
const chatSessions = ref({})

const walletFunctions = inject('walletFunctions', null)

onMounted(() => {
  // Créer une session initiale
  createNewSession()
})

async function createNewSession() {
  try {
    const response = await fetch('http://localhost:5000/new-session', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    })
    
    const data = await response.json()
    const sessionId = data.session_id
    
    // Créer un nouveau chat
    const chatName = `Chat ${chats.value.length + 1}`
    chats.value.push(chatName)
    
    // Stocker la session
    chatSessions.value[chatName] = {
      sessionId: sessionId,
      messages: [
        { text: 'Bonjour ! Posez-moi une question ou demandez-moi d\'effectuer une transaction.', isUser: false }
      ]
    }
    
    // Sélectionner le nouveau chat
    selectedChat.value = chats.value.length - 1
    currentSessionId.value = sessionId
    messages.value = [...chatSessions.value[chatName].messages]
    
  } catch (error) {
    console.error('Erreur lors de la création de session:', error)
  }
}

function selectChat(index) {
  selectedChat.value = index
  const chatName = chats.value[index]
  
  if (chatSessions.value[chatName]) {
    currentSessionId.value = chatSessions.value[chatName].sessionId
    messages.value = [...chatSessions.value[chatName].messages]
  } else {
    // Session non trouvée, créer une nouvelle
    createNewSession()
  }
}

async function addNewChat() {
  await createNewSession()
}

async function sendMessage(text) {
  if (!text.trim()) return

  const newMessage = { text, isUser: true }
  messages.value.push(newMessage)
  
  // Sauvegarder dans la session actuelle
  const currentChatName = chats.value[selectedChat.value]
  if (chatSessions.value[currentChatName]) {
    chatSessions.value[currentChatName].messages.push(newMessage)
  }
  
  isLoading.value = true

  try {
    const response = await fetch('http://localhost:5000/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        message: text,
        session_id: currentSessionId.value 
      })
    })

    const data = await response.json()
    
    // Mettre à jour l'ID de session si nécessaire
    if (data.session_id) {
      currentSessionId.value = data.session_id
      if (chatSessions.value[currentChatName]) {
        chatSessions.value[currentChatName].sessionId = data.session_id
      }
    }
    
    if (data.transaction_request) {
      pendingTransaction.value = data.transaction_request
      
      if (data.response?.trim()) {
        const botMessage = { text: data.response.trim(), isUser: false }
        messages.value.push(botMessage)
        if (chatSessions.value[currentChatName]) {
          chatSessions.value[currentChatName].messages.push(botMessage)
        }
      }
    } else {
      let botResponse = data?.response?.content || data?.response || ''
      
      if (botResponse.trim()) {
        const botMessage = { text: botResponse.trim(), isUser: false }
        messages.value.push(botMessage)
        if (chatSessions.value[currentChatName]) {
          chatSessions.value[currentChatName].messages.push(botMessage)
        }
      } else {
        throw new Error('Réponse vide de l\'API.')
      }
    }
  } catch (err) {
    console.error('Erreur API :', err)
    const errorMessage = {
      text: "Erreur de communication avec l'IA locale.",
      isUser: false
    }
    messages.value.push(errorMessage)
    
    const currentChatName = chats.value[selectedChat.value]
    if (chatSessions.value[currentChatName]) {
      chatSessions.value[currentChatName].messages.push(errorMessage)
    }
  } finally {
    isLoading.value = false
  }
}

async function confirmTransaction() {
  if (!pendingTransaction.value || !walletFunctions) {
    const errorMessage = {
      text: "❌ Erreur : Wallet non connecté ou transaction invalide.",
      isUser: false
    }
    messages.value.push(errorMessage)
    
    const currentChatName = chats.value[selectedChat.value]
    if (chatSessions.value[currentChatName]) {
      chatSessions.value[currentChatName].messages.push(errorMessage)
    }
    
    pendingTransaction.value = null
    return
  }

  try {
    await walletFunctions.sendTransaction(
      pendingTransaction.value.recipient,
      pendingTransaction.value.amount
    )

    const successMessage = {
      text: `✅ Transaction initiée : ${pendingTransaction.value.amount} ${pendingTransaction.value.currency} vers ${pendingTransaction.value.recipient}`,
      isUser: false
    }
    messages.value.push(successMessage)
    
    const currentChatName = chats.value[selectedChat.value]
    if (chatSessions.value[currentChatName]) {
      chatSessions.value[currentChatName].messages.push(successMessage)
    }
    
    await fetch('http://localhost:5000/confirm-transaction', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        confirmed: true, 
        transaction: pendingTransaction.value,
        session_id: currentSessionId.value
      })
    })
  } catch (error) {
    console.error('Erreur transaction:', error)
    const errorMessage = {
      text: `❌ Erreur lors de la transaction : ${error.message}`,
      isUser: false
    }
    messages.value.push(errorMessage)
    
    const currentChatName = chats.value[selectedChat.value]
    if (chatSessions.value[currentChatName]) {
      chatSessions.value[currentChatName].messages.push(errorMessage)
    }
  }
  pendingTransaction.value = null
}

async function cancelTransaction() {
  const cancelMessage = {
    text: "❌ Transaction annulée par l'utilisateur.",
    isUser: false
  }
  messages.value.push(cancelMessage)
  
  const currentChatName = chats.value[selectedChat.value]
  if (chatSessions.value[currentChatName]) {
    chatSessions.value[currentChatName].messages.push(cancelMessage)
  }
  
  try {
    await fetch('http://localhost:5000/confirm-transaction', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        confirmed: false, 
        transaction: pendingTransaction.value,
        session_id: currentSessionId.value
      })
    })
  } catch (error) {
    console.error('Erreur lors de l\'annulation:', error)
  }
  pendingTransaction.value = null
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
  position: relative;
}

.chat-header {
  padding: 0.5rem 0;
  border-bottom: 1px solid #eee;
  margin-bottom: 1rem;
}

.chat-header h3 {
  margin: 0;
  color: #666;
  font-size: 0.9rem;
  font-weight: normal;
}

.transaction-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.transaction-modal {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  max-width: 400px;
  width: 90%;
}

.transaction-modal h3 {
  margin: 0 0 1rem 0;
  color: #333;
  text-align: center;
}

.transaction-details {
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
}

.transaction-details p {
  margin: 0.5rem 0;
  font-family: monospace;
  word-break: break-all;
}

.transaction-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

.confirm-btn, .cancel-btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.2s;
}

.confirm-btn {
  background: #4caf50;
  color: white;
}

.confirm-btn:hover {
  background: #43a047;
}

.cancel-btn {
  background: #f44336;
  color: white;
}

.cancel-btn:hover {
  background: #d32f2f;
}
</style>