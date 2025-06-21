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
        <h3>
          Session:
          {{
            currentSessionId
              ? currentSessionId.substring(0, 8) + "..."
              : "Nouvelle session"
          }}
        </h3>
        <router-link to="/">
          <button class="back-btn">⬅️ Retour à l'accueil</button>
        </router-link>
      </div>

      <ChatMessages :messages="messages" :is-loading="isLoading" />

      <!-- Message d'erreur d'authentification -->
      <div v-if="authError" class="auth-error">
        <div class="error-icon">🔒</div>
        <h3>Authentification requise</h3>
        <p>{{ authError }}</p>
        <div class="auth-actions">
          <button @click="redirectToLogin" class="btn btn-primary">
            Se connecter
          </button>
        </div>
      </div>

      <!-- Modal de transaction -->
      <div
        v-if="pendingTransaction"
        class="modal-overlay"
        @click="rejectTransaction"
      >
        <div class="transaction-modal" @click.stop>
          <h3>🔔 Confirmation de Transaction</h3>
          <div class="transaction-details">
            <p>
              <strong>Destinataire:</strong>
              {{ pendingTransaction.recipient?.slice(0, 6) }}...{{
                pendingTransaction.recipient?.slice(-4)
              }}
            </p>
            <p>
              <strong>Montant:</strong> {{ pendingTransaction.amount }}
              {{ pendingTransaction.currency?.toUpperCase() }}
            </p>
          </div>
          <div class="modal-actions">
            <button
              @click="rejectTransaction"
              class="btn btn-cancel"
              :disabled="isProcessingTransaction"
            >
              Annuler
            </button>
            <button
              @click="confirmTransaction"
              class="btn btn-confirm"
              :disabled="isProcessingTransaction"
            >
              {{ isProcessingTransaction ? "En cours..." : "Confirmer" }}
            </button>
          </div>
        </div>
      </div>

      <ChatInput @send-message="handleSendMessage" />
    </main>
  </div>
</template>

<script setup>
import { ref, inject, onMounted, watch, computed, nextTick } from "vue";
import { useStore } from "vuex";
import { useRouter } from "vue-router";
import ChatSidebar from "./chatbot/ChatSidebar.vue";
import ChatMessages from "./chatbot/ChatMessages.vue";
import ChatInput from "./chatbot/ChatInput.vue";
import apiService from "../services/apiService";

const store = useStore();
const router = useRouter();

const isAuthenticated = computed(() => store.getters.isAuthenticated);
const authError = ref(null);

const messages = ref([
  {
    text: "Bonjour ! Posez-moi une question ou demandez-moi d'effectuer une transaction.",
    isUser: false,
  },
]);

const chats = ref([]);
const selectedChat = ref(0);
const isLoading = ref(false);
const pendingTransaction = ref(null);
const currentSessionId = ref(null);
const isProcessingTransaction = ref(false);
const chatSessions = ref({});
const walletFunctions = inject("walletFunctions", null);

async function checkAuthentication() {
  if (!isAuthenticated.value) {
    authError.value =
      "Vous devez être connecté pour utiliser le chat avec votre configuration personnalisée.";
    return false;
  }

  try {
    await store.dispatch("loadAgentConfig");
    authError.value = null;
    return true;
  } catch (error) {
    if (
      error.message.includes("404") ||
      error.message.includes("Aucune configuration")
    ) {
      authError.value =
        "Aucune configuration d'agent trouvée. Veuillez d'abord configurer votre assistant IA.";
    } else {
      authError.value =
        "Erreur de chargement de la configuration. Veuillez vous reconnecter.";
    }
    return false;
  }
}

async function redirectToLogin() {
  router.push("/AI");
}

onMounted(async () => {
  const authOk = await checkAuthentication();
  if (authOk) {
    await loadExistingSessions();
  }
});

async function loadExistingSessions() {
  try {
    console.log("Chargement des sessions existantes...");
    const response = await apiService.listSessions();
    const existingSessions = response.sessions || [];

    console.log(`${existingSessions.length} session(s) trouvée(s)`);

    if (existingSessions.length > 0) {
      // Charger les sessions existantes
      chats.value = [];
      chatSessions.value = {};

      for (let i = 0; i < existingSessions.length; i++) {
        const session = existingSessions[i];
        // Utiliser le vrai nom de session ou générer un nom unique
        const chatName = session.session_name || `Chat ${i + 1}`;

        // Éviter les doublons de noms
        let uniqueChatName = chatName;
        let counter = 1;
        while (chats.value.includes(uniqueChatName)) {
          uniqueChatName = `${chatName} (${counter})`;
          counter++;
        }

        chats.value.push(uniqueChatName);

        try {
          // Charger les messages de la session
          const sessionDetail = await apiService.getSession(session.session_id);
          const messages = sessionDetail.messages || [];

          // Convertir les messages au format frontend
          const frontendMessages = messages.map((msg) => ({
            text: msg.content,
            isUser: msg.role === "user",
            created_at: msg.created_at,
          }));

          // Ajouter le message de bienvenue si pas de messages
          if (frontendMessages.length === 0) {
            frontendMessages.push({
              text: "Bonjour ! Posez-moi une question ou demandez-moi d'effectuer une transaction.",
              isUser: false,
            });
          }

          chatSessions.value[uniqueChatName] = {
            sessionId: session.session_id,
            messages: frontendMessages,
            originalName: session.session_name,
          };
        } catch (sessionError) {
          console.error(
            `Erreur lors du chargement de la session ${session.session_id}:`,
            sessionError
          );
          // En cas d'erreur, créer une entrée basique
          chatSessions.value[uniqueChatName] = {
            sessionId: session.session_id,
            messages: [
              {
                text: "Bonjour ! Posez-moi une question ou demandez-moi d'effectuer une transaction.",
                isUser: false,
              },
            ],
            originalName: session.session_name,
          };
        }
      }

      // Sélectionner la première session
      if (chats.value.length > 0) {
        selectedChat.value = 0;
        const firstChatName = chats.value[0];
        currentSessionId.value = chatSessions.value[firstChatName].sessionId;
        messages.value = [...chatSessions.value[firstChatName].messages];
      }

      console.log("Sessions existantes chargées avec succès");
    } else {
      // Aucune session existante, créer une nouvelle
      console.log("Aucune session existante, création d'une nouvelle session");
      await createNewSession();
    }
  } catch (error) {
    console.error("Erreur lors du chargement des sessions:", error);
    // En cas d'erreur, créer une nouvelle session
    await createNewSession();
  }
}

async function createNewSession() {
  try {
    if (!isAuthenticated.value) {
      authError.value = "Vous devez être connecté pour utiliser le chat.";
      return;
    }

    // Générer un nom de session intelligent
    const now = new Date();
    const sessionName = `Chat ${now.toLocaleDateString(
      "fr-FR"
    )} ${now.toLocaleTimeString("fr-FR", {
      hour: "2-digit",
      minute: "2-digit",
    })}`;

    const sessionData = await apiService.createNewSession(sessionName);
    const sessionId = sessionData.session_id;

    // Éviter les doublons de noms
    let uniqueChatName = sessionName;
    let counter = 1;
    while (chats.value.includes(uniqueChatName)) {
      uniqueChatName = `${sessionName} (${counter})`;
      counter++;
    }

    chats.value.push(uniqueChatName);
    chatSessions.value[uniqueChatName] = {
      sessionId: sessionId,
      messages: [
        {
          text: "Bonjour ! Posez-moi une question ou demandez-moi d'effectuer une transaction.",
          isUser: false,
        },
      ],
      originalName: sessionName,
    };
    selectedChat.value = chats.value.length - 1;
    currentSessionId.value = sessionId;
    messages.value = [...chatSessions.value[uniqueChatName].messages];

    console.log(`Nouvelle session créée: ${uniqueChatName}`);
  } catch (error) {
    console.error("Erreur lors de la création de session:", error);
    authError.value =
      "Erreur lors de la création de session. Veuillez réessayer.";
  }
}

function selectChat(index) {
  selectedChat.value = index;
  const chatName = chats.value[index];
  if (chatSessions.value[chatName]) {
    currentSessionId.value = chatSessions.value[chatName].sessionId;
    messages.value = [...chatSessions.value[chatName].messages];
  } else {
    createNewSession();
  }
}

async function addNewChat() {
  await createNewSession();
}

async function handleSendMessage(text) {
  if (!text.trim()) return;

  if (!isAuthenticated.value) {
    authError.value = "Vous devez être connecté pour envoyer des messages.";
    return;
  }

  const newMessage = { text, isUser: true };
  messages.value.push(newMessage);
  const currentChatName = chats.value[selectedChat.value];
  if (chatSessions.value[currentChatName]) {
    chatSessions.value[currentChatName].messages.push(newMessage);
  }
  isLoading.value = true;

  try {
    console.log("🚀 Envoi du message:", text);

    const data = await apiService.sendChatMessage(text, currentSessionId.value);

    console.log("📥 Réponse complète du serveur:", data);

    if (data.session_id) {
      currentSessionId.value = data.session_id;
      if (chatSessions.value[currentChatName]) {
        chatSessions.value[currentChatName].sessionId = data.session_id;
      }
    }

    if (
      data.transaction_request &&
      typeof data.transaction_request === "object"
    ) {
      console.log(
        "✅ Transaction détectée et valide:",
        data.transaction_request
      );
      const requiredFields = ["recipient", "amount", "currency"];
      const hasAllFields = requiredFields.every(
        (field) => data.transaction_request[field]
      );
      if (hasAllFields) {
        console.log(
          "🔔 Tous les champs requis présents, affichage de la modal"
        );
        pendingTransaction.value = { ...data.transaction_request };
        if (data.response && data.response.trim()) {
          const botMessage = { text: data.response.trim(), isUser: false };
          messages.value.push(botMessage);
          if (chatSessions.value[currentChatName]) {
            chatSessions.value[currentChatName].messages.push(botMessage);
          }
        }
      } else {
        console.log(
          "❌ Champs manquants dans transaction_request:",
          data.transaction_request
        );
      }
    } else {
      let botResponse = data?.response || "";
      console.log("💬 Réponse bot brute:", botResponse);
      if (botResponse.trim()) {
        const botMessage = { text: botResponse.trim(), isUser: false };
        messages.value.push(botMessage);
        if (chatSessions.value[currentChatName]) {
          chatSessions.value[currentChatName].messages.push(botMessage);
        }
      } else {
        throw new Error("Réponse vide de l'API.");
      }
    }
  } catch (err) {
    console.error("❌ Erreur API complète:", err);

    if (err.message.includes("401") || err.message.includes("UNAUTHORIZED")) {
      authError.value = "Votre session a expiré. Veuillez vous reconnecter.";
      return;
    }

    const errorMessage = {
      text: `Erreur de communication: ${err.message}`,
      isUser: false,
    };
    messages.value.push(errorMessage);
    if (chatSessions.value[currentChatName]) {
      chatSessions.value[currentChatName].messages.push(errorMessage);
    }
  } finally {
    isLoading.value = false;
  }
}

async function confirmTransaction() {
  console.log("🔥 confirmTransaction() appelée");
  console.log("📋 pendingTransaction.value:", pendingTransaction.value);
  if (!pendingTransaction.value) {
    console.error("❌ Pas de transaction en attente");
    return;
  }
  isProcessingTransaction.value = true;
  console.log("🔍 Vérification du wallet...");
  console.log("💼 walletFunctions disponible:", !!walletFunctions);
  if (!walletFunctions) {
    console.error("❌ walletFunctions non disponible");
    const errorMessage = {
      text: "❌ Erreur : Wallet non disponible. Veuillez connecter votre wallet.",
      isUser: false,
    };
    messages.value.push(errorMessage);
    const currentChatName = chats.value[selectedChat.value];
    if (chatSessions.value[currentChatName]) {
      chatSessions.value[currentChatName].messages.push(errorMessage);
    }
    pendingTransaction.value = null;
    isProcessingTransaction.value = false;
    return;
  }
  console.log("🔗 Vérification connexion wallet...");
  const isConnected = walletFunctions.isConnected();
  console.log("🔗 Wallet connecté:", isConnected);
  if (!isConnected) {
    console.error("❌ Wallet non connecté");
    const errorMessage = {
      text: "❌ Erreur : Wallet non connecté. Veuillez d'abord connecter votre wallet MetaMask.",
      isUser: false,
    };
    messages.value.push(errorMessage);
    const currentChatName = chats.value[selectedChat.value];
    if (chatSessions.value[currentChatName]) {
      chatSessions.value[currentChatName].messages.push(errorMessage);
    }
    pendingTransaction.value = null;
    isProcessingTransaction.value = false;
    return;
  }

  try {
    console.log("🚀 Début de la transaction...");
    const processingMessage = {
      text: `🔄 Traitement de la transaction : ${
        pendingTransaction.value.amount
      } ${pendingTransaction.value.currency?.toUpperCase()} vers ${pendingTransaction.value.recipient.slice(
        0,
        6
      )}...${pendingTransaction.value.recipient.slice(-4)}`,
      isUser: false,
    };
    messages.value.push(processingMessage);
    const currentChatName = chats.value[selectedChat.value];
    if (chatSessions.value[currentChatName]) {
      chatSessions.value[currentChatName].messages.push(processingMessage);
    }
    console.log("💸 Paramètres de transaction:");
    console.log("  - Destinataire:", pendingTransaction.value.recipient);
    console.log("  - Montant:", pendingTransaction.value.amount);
    console.log("  - Devise:", pendingTransaction.value.currency);
    console.log("⚡ Appel de sendTransaction...");
    const result = await walletFunctions.sendTransaction(
      pendingTransaction.value.recipient,
      pendingTransaction.value.amount
    );
    console.log("✅ Résultat de la transaction:", result);
    const successMessage = {
      text: `✅ Transaction réussie ! Hash: ${result.hash?.slice(0, 10)}...`,
      isUser: false,
    };
    messages.value.push(successMessage);
    if (chatSessions.value[currentChatName]) {
      chatSessions.value[currentChatName].messages.push(successMessage);
    }
    console.log("📡 Notification au serveur...");
    const confirmResponse = await fetch(
      "http://localhost:5000/confirm-transaction",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          confirmed: true,
          transaction: pendingTransaction.value,
          session_id: currentSessionId.value,
          transaction_hash: result.hash,
        }),
      }
    );
    if (confirmResponse.ok) {
      const confirmData = await confirmResponse.json();
      console.log("📡 Réponse serveur confirmation:", confirmData);
    }
  } catch (error) {
    console.error("❌ Erreur transaction complète:", error);
    let errorText = `❌ Erreur lors de la transaction : ${error.message}`;
    if (error.message.includes("User rejected")) {
      errorText = "❌ Transaction rejetée par l'utilisateur dans MetaMask";
    } else if (error.message.includes("insufficient funds")) {
      errorText = "💸 Fonds insuffisants pour effectuer la transaction";
    } else if (error.message.includes("Wallet non connecté")) {
      errorText =
        "🔗 Wallet non connecté. Veuillez connecter MetaMask d'abord.";
    }
    const errorMessage = { text: errorText, isUser: false };
    messages.value.push(errorMessage);
    const currentChatName = chats.value[selectedChat.value];
    if (chatSessions.value[currentChatName]) {
      chatSessions.value[currentChatName].messages.push(errorMessage);
    }
  } finally {
    pendingTransaction.value = null;
    isProcessingTransaction.value = false;
  }
}

function rejectTransaction() {
  console.log("❌ Transaction rejetée par l'utilisateur");
  const rejectionMessage = {
    text: "❌ Transaction annulée par l'utilisateur.",
    isUser: false,
  };
  messages.value.push(rejectionMessage);
  const currentChatName = chats.value[selectedChat.value];
  if (chatSessions.value[currentChatName]) {
    chatSessions.value[currentChatName].messages.push(rejectionMessage);
  }
  pendingTransaction.value = null;
}

watch(
  pendingTransaction,
  (newVal, oldVal) => {
    console.log("🔄 pendingTransaction changed:", { old: oldVal, new: newVal });
    if (newVal) {
      console.log("✅ Modal devrait s'afficher maintenant!");
      console.log("🎯 Détails de la transaction:", newVal);
    } else {
      console.log("❌ Modal fermée");
    }
  },
  { deep: true }
);

function testWalletConnection() {
  console.log("🧪 Test de connexion wallet");
  console.log("💼 walletFunctions:", walletFunctions);
  if (!walletFunctions) {
    console.log("❌ walletFunctions non disponible");
    return;
  }
  try {
    const isConnected = walletFunctions.isConnected();
    console.log("🔗 isConnected():", isConnected);
    if (isConnected) {
      const address = walletFunctions.getAddress();
      console.log("📍 Adresse:", address);
    }
    console.log("🔧 Fonctions disponibles dans walletFunctions:");
    console.log(Object.keys(walletFunctions));
  } catch (error) {
    console.error("❌ Erreur test wallet:", error);
  }
}
if (typeof window !== "undefined") {
  window.testWalletConnection = testWalletConnection;
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
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 1rem;
  border-bottom: 1px solid #eee;
  margin-bottom: 1rem;
}

.header-actions {
  display: flex;
  align-items: center;
}

.back-btn {
  padding: 0.5rem 1rem;
  background-color: #4caf50;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background-color 0.2s ease;
}

.back-btn:hover {
  background-color: #218838;
}

.chat-header h3 {
  margin: 0;
  color: #666;
  font-size: 0.9rem;
  font-weight: normal;
}

.auth-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
  text-align: center;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  margin: 20px;
  border-radius: 24px;
  padding: 40px;
}

.error-icon {
  font-size: 4rem;
  margin-bottom: 20px;
}

.auth-error h3 {
  color: #1e293b;
  margin: 0 0 15px 0;
  font-size: 1.5rem;
}

.auth-error p {
  color: #64748b;
  margin: 0 0 30px 0;
  font-size: 1.1rem;
  max-width: 500px;
}

.auth-actions {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
  justify-content: center;
}

.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 16px;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
}

.btn-secondary {
  background: #e2e8f0;
  color: #475569;
}

.btn-secondary:hover {
  background: #cbd5e1;
}

.modal-overlay {
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
  border-radius: 20px;
  padding: 30px;
  max-width: 500px;
  width: 90%;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
}

.transaction-modal h3 {
  margin: 0 0 20px 0;
  color: #1e293b;
  text-align: center;
}

.transaction-details {
  margin: 20px 0;
  padding: 20px;
  background: #f8fafc;
  border-radius: 12px;
}

.transaction-details p {
  margin: 10px 0;
  color: #475569;
}

.modal-actions {
  display: flex;
  gap: 15px;
  justify-content: center;
  margin-top: 25px;
}

.btn-cancel {
  background: #e2e8f0;
  color: #475569;
}

.btn-confirm {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
}
</style>
