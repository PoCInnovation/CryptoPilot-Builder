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
import { ref, inject } from 'vue'
import ChatSidebar from './chatbot/ChatSidebar.vue'
import ChatMessages from './chatbot/ChatMessages.vue'
import ChatInput from './chatbot/ChatInput.vue'

const messages = ref([
  { text: 'Bonjour ! Posez-moi une question ou demandez-moi d\'effectuer une transaction.', isUser: false }
])

const chats = ref(['Chat 1'])
const selectedChat = ref(0)
const isLoading = ref(false)
const pendingTransaction = ref(null)

const walletFunctions = inject('walletFunctions', null)

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
    
    if (data.transaction_request) {
      pendingTransaction.value = data.transaction_request
      
      if (data.response?.trim()) {
        messages.value.push({ text: data.response.trim(), isUser: false })
      }
    } else {
      let botResponse = data?.response?.content || data?.response || ''
      
      if (botResponse.trim()) {
        messages.value.push({ text: botResponse.trim(), isUser: false })
      } else {
        throw new Error('Réponse vide de l\'API.')
      }
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

async function confirmTransaction() {
  if (!pendingTransaction.value || !walletFunctions) {
    messages.value.push({
      text: "❌ Erreur : Wallet non connecté ou transaction invalide.",
      isUser: false
    })
    pendingTransaction.value = null
    return
  }

  try {
    await walletFunctions.sendTransaction(
      pendingTransaction.value.recipient,
      pendingTransaction.value.amount
    )

    messages.value.push({
      text: `✅ Transaction initiée : ${pendingTransaction.value.amount} ${pendingTransaction.value.currency} vers ${pendingTransaction.value.recipient}`,
      isUser: false
    })
    await fetch('http://localhost:5000/confirm-transaction', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ confirmed: true, transaction: pendingTransaction.value })
    })
  } catch (error) {
    console.error('Erreur transaction:', error)
    messages.value.push({
      text: `❌ Erreur lors de la transaction : ${error.message}`,
      isUser: false
    })
  }
  pendingTransaction.value = null
}

async function cancelTransaction() {
  messages.value.push({
    text: "❌ Transaction annulée par l'utilisateur.",
    isUser: false
  })
  try {
    await fetch('http://localhost:5000/confirm-transaction', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ confirmed: false, transaction: pendingTransaction.value })
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