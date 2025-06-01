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
      <div v-if="pendingTransaction" class="transaction-modal-overlay" @click.self="cancelTransaction">
      <div class="transaction-modal">
        <h3>🔐 Confirmation de transaction</h3>
        <div class="transaction-details">
          <p><strong>Destinataire :</strong> {{ pendingTransaction.recipient }}</p>
          <p><strong>Montant :</strong> {{ pendingTransaction.amount }} {{ pendingTransaction.currency?.toUpperCase() }}</p>
        </div>
        <div class="transaction-actions">
          <button
            @click="handleConfirmClick"
            class="confirm-btn"
            :disabled="isProcessingTransaction"
          >
            {{ isProcessingTransaction ? '⏳ En cours...' : '✅ Confirmer' }}
          </button>
          <button
            @click="handleCancelClick"
            class="cancel-btn"
            :disabled="isProcessingTransaction"
          >
            ❌ Annuler
          </button>
        </div>
      </div>
      </div>

      <ChatInput @send-message="sendMessage" />
    </main>
  </div>
</template>

<script setup>
import { ref, inject, onMounted, watch } from 'vue'
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
const isProcessingTransaction = ref(false)
const chatSessions = ref({})
const walletFunctions = inject('walletFunctions', null)

onMounted(() => {
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
    const chatName = `Chat ${chats.value.length + 1}`
    chats.value.push(chatName)
    chatSessions.value[chatName] = {
      sessionId: sessionId,
      messages: [
        { text: 'Bonjour ! Posez-moi une question ou demandez-moi d\'effectuer une transaction.', isUser: false }
      ]
    }
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
  const currentChatName = chats.value[selectedChat.value]
  if (chatSessions.value[currentChatName]) {
    chatSessions.value[currentChatName].messages.push(newMessage)
  }
  isLoading.value = true

  try {
    console.log('🚀 Envoi du message:', text)
    const response = await fetch('http://localhost:5000/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        message: text,
        session_id: currentSessionId.value 
      })
    })
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }
    const data = await response.json()
    console.log('📥 Réponse complète du serveur:')
    console.log('📦 Type de data:', typeof data)
    console.log('📋 Clés de data:', Object.keys(data))
    console.log('🎯 data.transaction_request:', data.transaction_request)
    console.log('💬 data.response:', data.response)
    console.log('🆔 data.session_id:', data.session_id)
    if (data.session_id) {
      currentSessionId.value = data.session_id
      if (chatSessions.value[currentChatName]) {
        chatSessions.value[currentChatName].sessionId = data.session_id
      }
    }
    if (data.transaction_request && typeof data.transaction_request === 'object') {
      console.log('✅ Transaction détectée et valide:', data.transaction_request)
      const requiredFields = ['recipient', 'amount', 'currency']
      const hasAllFields = requiredFields.every(field => data.transaction_request[field])
      if (hasAllFields) {
        console.log('🔔 Tous les champs requis présents, affichage de la modal')
        pendingTransaction.value = { ...data.transaction_request }
        if (data.response && data.response.trim()) {
          const botMessage = { text: data.response.trim(), isUser: false }
          messages.value.push(botMessage)
          if (chatSessions.value[currentChatName]) {
            chatSessions.value[currentChatName].messages.push(botMessage)
          }
        }
      } else {
        console.log('❌ Champs manquants dans transaction_request:', data.transaction_request)
        console.log('📋 Champs requis:', requiredFields)
        console.log('📋 Champs présents:', Object.keys(data.transaction_request))
      }
    } else {
      console.log('❌ Pas de transaction_request valide dans la réponse')
      console.log('🔍 Type de transaction_request:', typeof data.transaction_request)
      let botResponse = data?.response || ''
      console.log('💬 Réponse bot brute:', botResponse)
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
    console.error('❌ Erreur API complète:', err)
    const errorMessage = {
      text: `Erreur de communication: ${err.message}`,
      isUser: false
    }
    messages.value.push(errorMessage)
    if (chatSessions.value[currentChatName]) {
      chatSessions.value[currentChatName].messages.push(errorMessage)
    }
  } finally {
    isLoading.value = false
  }
}

async function confirmTransaction() {
  console.log('🔥 confirmTransaction() appelée')
  console.log('📋 pendingTransaction.value:', pendingTransaction.value)
  if (!pendingTransaction.value) {
    console.error('❌ Pas de transaction en attente')
    return
  }
  isProcessingTransaction.value = true
  console.log('🔍 Vérification du wallet...')
  console.log('💼 walletFunctions disponible:', !!walletFunctions)
  if (!walletFunctions) {
    console.error('❌ walletFunctions non disponible')
    const errorMessage = {
      text: "❌ Erreur : Wallet non disponible. Veuillez connecter votre wallet.",
      isUser: false
    }
    messages.value.push(errorMessage)
    const currentChatName = chats.value[selectedChat.value]
    if (chatSessions.value[currentChatName]) {
      chatSessions.value[currentChatName].messages.push(errorMessage)
    }
    pendingTransaction.value = null
    isProcessingTransaction.value = false
    return
  }
  console.log('🔗 Vérification connexion wallet...')
  const isConnected = walletFunctions.isConnected()
  console.log('🔗 Wallet connecté:', isConnected)
  if (!isConnected) {
    console.error('❌ Wallet non connecté')
    const errorMessage = {
      text: "❌ Erreur : Wallet non connecté. Veuillez d'abord connecter votre wallet MetaMask.",
      isUser: false
    }
    messages.value.push(errorMessage)
    const currentChatName = chats.value[selectedChat.value]
    if (chatSessions.value[currentChatName]) {
      chatSessions.value[currentChatName].messages.push(errorMessage)
    }
    pendingTransaction.value = null
    isProcessingTransaction.value = false
    return
  }

  try {
    console.log('🚀 Début de la transaction...')
    const processingMessage = {
      text: `🔄 Traitement de la transaction : ${pendingTransaction.value.amount} ${pendingTransaction.value.currency?.toUpperCase()} vers ${pendingTransaction.value.recipient.slice(0, 6)}...${pendingTransaction.value.recipient.slice(-4)}`,
      isUser: false
    }
    messages.value.push(processingMessage)
    const currentChatName = chats.value[selectedChat.value]
    if (chatSessions.value[currentChatName]) {
      chatSessions.value[currentChatName].messages.push(processingMessage)
    }
    console.log('💸 Paramètres de transaction:')
    console.log('  - Destinataire:', pendingTransaction.value.recipient)
    console.log('  - Montant:', pendingTransaction.value.amount)
    console.log('  - Devise:', pendingTransaction.value.currency)
    console.log('⚡ Appel de sendTransaction...')
    const result = await walletFunctions.sendTransaction(
      pendingTransaction.value.recipient,
      pendingTransaction.value.amount
    )
    console.log('✅ Résultat de la transaction:', result)
    const successMessage = {
      text: `✅ Transaction réussie ! Hash: ${result.hash?.slice(0, 10)}...`,
      isUser: false
    }
    messages.value.push(successMessage)
    if (chatSessions.value[currentChatName]) {
      chatSessions.value[currentChatName].messages.push(successMessage)
    }
    console.log('📡 Notification au serveur...')
    const confirmResponse = await fetch('http://localhost:5000/confirm-transaction', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        confirmed: true,
        transaction: pendingTransaction.value,
        session_id: currentSessionId.value,
        transaction_hash: result.hash
      })
    })
    if (confirmResponse.ok) {
      const confirmData = await confirmResponse.json()
      console.log('📡 Réponse serveur confirmation:', confirmData)
    }
  } catch (error) {
    console.error('❌ Erreur transaction complète:', error)
    console.error('❌ Type d\'erreur:', typeof error)
    console.error('❌ Message d\'erreur:', error.message)
    let errorText = `❌ Erreur lors de la transaction : ${error.message}`
    if (error.message.includes('User rejected')) {
      errorText = '❌ Transaction rejetée par l\'utilisateur dans MetaMask'
    } else if (error.message.includes('insufficient funds')) {
      errorText = '💸 Fonds insuffisants pour effectuer la transaction'
    } else if (error.message.includes('Wallet non connecté')) {
      errorText = '🔗 Wallet non connecté. Veuillez connecter MetaMask d\'abord.'
    }
    const errorMessage = {
      text: errorText,
      isUser: false
    }
    messages.value.push(errorMessage)
    const currentChatName = chats.value[selectedChat.value]
    if (chatSessions.value[currentChatName]) {
      chatSessions.value[currentChatName].messages.push(errorMessage)
    }
  } finally {
    console.log('🏁 Fin de confirmTransaction, suppression de pendingTransaction')
    pendingTransaction.value = null
    isProcessingTransaction.value = false
  }
}

async function handleConfirmClick() {
  console.log('🔘 Bouton Confirmer cliqué')
  await confirmTransaction()
}

async function handleCancelClick() {
  console.log('🔘 Bouton Annuler cliqué')
  await cancelTransaction()
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
watch(pendingTransaction, (newVal, oldVal) => {
  console.log('🔄 pendingTransaction changed:', { old: oldVal, new: newVal })
  if (newVal) {
    console.log('✅ Modal devrait s\'afficher maintenant!')
    console.log('🎯 Détails de la transaction:', newVal)
  } else {
    console.log('❌ Modal fermée')
  }
}, { deep: true })

function testWalletConnection() {
  console.log('🧪 Test de connexion wallet')
  console.log('💼 walletFunctions:', walletFunctions)
  if (!walletFunctions) {
    console.log('❌ walletFunctions non disponible')
    return
  }
  try {
    const isConnected = walletFunctions.isConnected()
    console.log('🔗 isConnected():', isConnected)
    if (isConnected) {
      const address = walletFunctions.getAddress()
      console.log('📍 Adresse:', address)
    }
    console.log('🔧 Fonctions disponibles dans walletFunctions:')
    console.log(Object.keys(walletFunctions))
  } catch (error) {
    console.error('❌ Erreur test wallet:', error)
  }
}
if (typeof window !== 'undefined') {
  window.testWalletConnection = testWalletConnection
}

function checkWalletStatus() {
  if (!walletFunctions) {
    return { connected: false, error: 'Wallet non disponible' }
  }
  return {
    connected: walletFunctions.isConnected(),
    address: walletFunctions.getAddress()
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
  color: black;
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