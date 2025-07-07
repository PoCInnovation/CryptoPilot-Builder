<template>
  <div class="chat-container">
    <!-- Effet de fond animé -->
    <div class="background-animation">
      <div class="floating-orb orb-1"></div>
      <div class="floating-orb orb-2"></div>
      <div class="floating-orb orb-3"></div>
    </div>

    <ChatSidebar
      :chats="chats"
      :selected-chat="selectedChat"
      @select-chat="selectChat"
      @add-chat="addNewChat"
    />

    <main class="chat-main">
      <!-- Header amélioré avec glassmorphism -->
      <div class="chat-header">
        <div class="session-info">
          <div class="session-indicator"></div>
          <h3>
            <span class="session-label">Session Active</span>
            <span class="session-id">
              {{
                currentSessionId
                  ? currentSessionId.substring(0, 8) + "..."
                  : "Nouvelle session"
              }}
            </span>
          </h3>
        </div>
        <!-- Menu déroulant de sélection de modèle -->
        <div class="model-select-wrapper">
          <select v-model="selectedModel" class="model-select">
            <option value="gpt-4o-mini">GPT-4o Mini</option>
            <option value="gpt-4">GPT-4</option>
            <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
            <!-- Ajoute d'autres modèles si besoin -->
          </select>
          <span class="model-select-label">Modèle IA</span>
        </div>
        <div class="header-glow"></div>
      </div>

      <ChatMessages :messages="messages" :is-loading="isLoading" />

      <!-- Message d'erreur d'authentification amélioré -->
      <div v-if="authError" class="auth-error">
        <div class="auth-error-content">
          <div class="error-icon-container">
            <div class="error-icon">🔒</div>
            <div class="icon-pulse"></div>
          </div>
          <h3>Authentification requise</h3>
          <p>{{ authError }}</p>
          <div class="auth-actions">
            <button @click="redirectToLogin" class="btn btn-primary">
              <span>Se connecter</span>
              <div class="btn-shine"></div>
            </button>
          </div>
        </div>
      </div>

      <!-- Modal de transaction -->
      <div
        v-if="pendingTransaction"
        class="modal-overlay"
        @click="rejectTransaction"
      >
        <div class="transaction-modal" @click.stop>
          <div class="modal-header">
            <div class="notification-icon">🔔</div>
            <h3>Confirmation de Transaction</h3>
          </div>
          <div class="transaction-details">
            <div class="detail-row">
              <span class="detail-label">Destinataire</span>
              <span class="detail-value address-value">
                {{ pendingTransaction.recipient?.slice(0, 6) }}...{{
                  pendingTransaction.recipient?.slice(-4)
                }}
              </span>
            </div>
            <div class="detail-row">
              <span class="detail-label">Montant</span>
              <span class="detail-value amount-value">
                {{ pendingTransaction.amount }}
                <span class="currency">{{ pendingTransaction.currency?.toUpperCase() }}</span>
              </span>
            </div>
          </div>
          <div class="modal-actions">
            <button
              @click="rejectTransaction"
              class="btn btn-cancel"
              :disabled="isProcessingTransaction"
            >
              <span>Annuler</span>
            </button>
            <button
              @click="confirmTransaction"
              class="btn btn-confirm"
              :disabled="isProcessingTransaction"
            >
              <span>{{ isProcessingTransaction ? "En cours..." : "Confirmer" }}</span>
              <div class="btn-shine"></div>
            </button>
          </div>
        </div>
      </div>

      <ChatInput @send-message="handleSendMessage" />
    </main>
  </div>
</template>

<script setup>
import { ref, inject, onMounted, watch, computed } from "vue";
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
const selectedModel = ref("gpt-4o-mini");

// Récupère la config IA du store (comme dans Ai.vue)
const aiConfig = computed(() => store.getters.aiConfig);

// Restaure le modèle au montage
onMounted(() => {
  selectedModel.value = aiConfig.value.selectedModel || "gpt-4o-mini";
});

// Met à jour le store à chaque changement
watch(selectedModel, (newVal) => {
  if (newVal) {
    store.dispatch("setModel", newVal);
  }
});

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
  router.push("/");
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

// Gère l'envoi d'un message utilisateur et la détection d'une transaction
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
    console.log("📤 Envoi du message:", text);
    const data = await apiService.sendChatMessage(text, currentSessionId.value);
    
    console.log("📥 Données reçues du backend (type):", typeof data);
    console.log("📥 Données reçues du backend (contenu):", data);
    
    // Le backend renvoie soit une string directe, soit un objet avec une propriété response
    const responseText = typeof data === "string" ? data : (data.response || "");
    console.log("🔍 Réponse brute du backend:", responseText);
    console.log("🔍 Longueur de la réponse:", responseText.length);
    console.log("🔍 Contient TRANSACTION_REQUEST:", responseText.includes("TRANSACTION_REQUEST:"));
    
    // Debug: afficher les 200 premiers et derniers caractères pour voir si le marqueur est caché
    if (responseText.length > 100) {
      console.log("🔍 Début de la réponse:", responseText.substring(0, 200));
      console.log("🔍 Fin de la réponse:", responseText.substring(responseText.length - 200));
    }

    let botResponse = "";
    let transactionRequest = null;

    // Vérifier s'il y a un marqueur TRANSACTION_REQUEST dans la réponse
    if (responseText.includes("TRANSACTION_REQUEST:")) {
      console.log("🔍 Marqueur TRANSACTION_REQUEST détecté");
      
      // Séparer le message du JSON
      const parts = responseText.split("TRANSACTION_REQUEST:");
      botResponse = parts[0].trim(); // Message avant le marqueur
      
      if (parts[1]) {
        try {
          // Parser le JSON après le marqueur
          const jsonPart = parts[1].trim();
          console.log("🔍 Partie JSON à parser:", jsonPart);
          
          transactionRequest = JSON.parse(jsonPart);
          console.log("✅ Transaction parsée avec succès:", transactionRequest);
          
          // Vérifier que tous les champs requis sont présents
          const requiredFields = ["recipient", "amount", "currency"];
          const hasAllFields = requiredFields.every(field => transactionRequest[field]);
          
          if (!hasAllFields) {
            console.warn("⚠️ Champs manquants dans la transaction:", transactionRequest);
            transactionRequest = null;
            // Garder le message complet si la transaction est invalide
            botResponse = responseText;
          }
        } catch (parseError) {
          console.error("❌ Erreur parsing JSON transaction:", parseError);
          console.error("❌ JSON à parser était:", parts[1]);
          // En cas d'erreur de parsing, garder le message complet
          botResponse = responseText;
          transactionRequest = null;
        }
      }
    } else {
      // Pas de transaction, message normal
      botResponse = responseText;
    }

    console.log("📝 Message final à afficher:", botResponse);
    console.log("💰 Transaction détectée:", !!transactionRequest);

    // Afficher le message du bot s'il y en a un
    if (botResponse.trim()) {
      const botMessage = { text: botResponse.trim(), isUser: false };
      messages.value.push(botMessage);
      if (chatSessions.value[currentChatName]) {
        chatSessions.value[currentChatName].messages.push(botMessage);
      }
    }

    // Si une transaction est détectée, afficher la modal
    if (transactionRequest) {
      console.log("🚀 Affichage de la modal de transaction");
      pendingTransaction.value = { ...transactionRequest };
    }

  } catch (err) {
    console.error("❌ Erreur API complète:", err);
    if (err.message.includes("401") || err.message.includes("UNAUTHORIZED")) {
      authError.value = "Votre session a expiré. Veuillez vous reconnecter.";
      return;
    }
    const errorMessage = { text: `Erreur de communication: ${err.message}`, isUser: false };
    messages.value.push(errorMessage);
    if (chatSessions.value[currentChatName]) {
      chatSessions.value[currentChatName].messages.push(errorMessage);
    }
  } finally {
    isLoading.value = false;
  }
}

// 2. Fonction de test pour forcer une transaction (pour debug)
function forceTestTransaction() {
  console.log("🧪 Test forcé de transaction");
  pendingTransaction.value = {
    type: "transaction_request",
    recipient: "0xFa6D1Ff93Fa73f3105f24FF47911b8C544CDA195",
    amount: "0.01",
    currency: "sepolia",
    status: "pending_confirmation"
  };
  console.log("✅ Modal de transaction forcée:", pendingTransaction.value);
}

// Ajouter la fonction de test au window pour debug
if (typeof window !== "undefined") {
  window.forceTestTransaction = forceTestTransaction;
}

async function confirmTransaction() {
  console.log("🔥 confirmTransaction() appelée");
  console.log("📋 pendingTransaction.value:", pendingTransaction.value);
  console.log("💼 walletFunctions disponible:", !!walletFunctions);
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
    } else if (error.message.includes("Failed to fetch")) {
      errorText = "✅ Transaction réussie mais le serveur n'a pas répondu.";
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
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 24px;
  box-shadow: 
    0 25px 50px -12px rgba(0, 0, 0, 0.25),
    0 0 0 1px rgba(255, 255, 255, 0.05);
  overflow: hidden;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
}

/* Animation de fond */
.background-animation {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  overflow: hidden;
}

.floating-orb {
  position: absolute;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
  animation: float 6s ease-in-out infinite;
}

.orb-1 {
  width: 200px;
  height: 200px;
  top: 10%;
  left: 10%;
  animation-delay: 0s;
}

.orb-2 {
  width: 150px;
  height: 150px;
  top: 60%;
  right: 20%;
  animation-delay: 2s;
}

.orb-3 {
  width: 100px;
  height: 100px;
  bottom: 20%;
  left: 60%;
  animation-delay: 4s;
}

@keyframes float {
  0%, 100% { transform: translateY(0px) scale(1); opacity: 0.3; }
  50% { transform: translateY(-20px) scale(1.1); opacity: 0.6; }
}

.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 0;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  position: relative;
  border-radius: 0 24px 24px 0;
}

/* Header moderne avec glassmorphism */
.chat-header {
  position: relative;
  padding: 1.5rem 2rem;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  margin-bottom: 0;
}

.session-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.session-indicator {
  width: 12px;
  height: 12px;
  background: linear-gradient(45deg, #10b981, #059669);
  border-radius: 50%;
  animation: pulse 2s infinite;
  box-shadow: 0 0 20px rgba(16, 185, 129, 0.5);
}

@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.7; transform: scale(1.1); }
}

.chat-header h3 {
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.session-label {
  font-size: 0.75rem;
  color: #64748b;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.session-id {
  font-size: 1rem;
  color: #1e293b;
  font-weight: 600;
  background: linear-gradient(135deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.header-glow {
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 100px;
  height: 2px;
  background: linear-gradient(90deg, transparent, #667eea, transparent);
  opacity: 0.8;
}

/* Auth error amélioré */
.auth-error {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  z-index: 100;
}

.auth-error-content {
  text-align: center;
  padding: 3rem;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(30px);
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.2);
  max-width: 500px;
}

.error-icon-container {
  position: relative;
  display: inline-block;
  margin-bottom: 2rem;
}

.error-icon {
  font-size: 4rem;
  filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.1));
}

.icon-pulse {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 80px;
  height: 80px;
  border: 2px solid #667eea;
  border-radius: 50%;
  animation: ripple 2s infinite;
  opacity: 0.3;
}

@keyframes ripple {
  0% { transform: translate(-50%, -50%) scale(0.8); opacity: 0.8; }
  100% { transform: translate(-50%, -50%) scale(1.5); opacity: 0; }
}

.auth-error h3 {
  color: #1e293b;
  margin: 0 0 1rem 0;
  font-size: 1.8rem;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.auth-error p {
  color: #64748b;
  margin: 0 0 2rem 0;
  font-size: 1.1rem;
  line-height: 1.6;
}

.auth-actions {
  margin-top: 2rem;
}

/* Boutons modernes */
.btn {
  position: relative;
  padding: 16px 32px;
  border: none;
  border-radius: 16px;
  font-weight: 600;
  cursor: pointer;
  font-size: 16px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none !important;
}

.btn span {
  position: relative;
  z-index: 2;
}

.btn-shine {
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
  transition: left 0.5s;
}

.btn:hover .btn-shine {
  left: 100%;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
}

.btn-primary:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 40px rgba(102, 126, 234, 0.4);
}

.btn-secondary {
  background: rgba(226, 232, 240, 0.8);
  backdrop-filter: blur(10px);
  color: #475569;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.btn-secondary:hover {
  background: rgba(203, 213, 225, 0.9);
  transform: translateY(-2px);
}

/* Modal overlay avec glassmorphisme sombre */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(118, 75, 162, 0.9) 0%, rgba(90, 52, 148, 0.9) 100%);
  backdrop-filter: blur(12px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* Modal transaction avec glassmorphisme */
.transaction-modal {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 24px;
  padding: 0;
  max-width: 500px;
  width: 90%;
  box-shadow: 
    0 25px 50px -12px rgba(0, 0, 0, 0.4),
    0 0 0 1px rgba(255, 255, 255, 0.1);
  animation: modalSlideIn 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  position: relative;
}

/* Effet de brillance sur la modal */
.transaction-modal::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
  animation: shimmer 3s infinite;
  pointer-events: none;
}

@keyframes shimmer {
  0% { left: -100%; }
  100% { left: 100%; }
}

@keyframes modalSlideIn {
  from { 
    opacity: 0; 
    transform: scale(0.9) translateY(30px); 
  }
  to { 
    opacity: 1; 
    transform: scale(1) translateY(0); 
  }
}

/* Header avec dégradé sombre */
.modal-header {
  padding: 2rem 2rem 1rem 2rem;
  text-align: center;
  background: linear-gradient(135deg, rgba(118, 75, 162, 0.3), rgba(90, 52, 148, 0.3));
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  position: relative;
}

.modal-header::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 100px;
  height: 2px;
  background: linear-gradient(90deg, transparent, #764ba2, transparent);
  opacity: 0.8;
}

.notification-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
  animation: bounce 2s infinite;
  filter: drop-shadow(0 4px 8px rgba(118, 75, 162, 0.3));
  color: rgba(255, 255, 255, 0.9);
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

.modal-header h3 {
  margin: 0;
  color: rgba(255, 255, 255, 0.95);
  font-size: 1.5rem;
  font-weight: 700;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  letter-spacing: 0.5px;
}

/* Détails de transaction avec glassmorphisme */
.transaction-details {
  margin: 0;
  padding: 2rem;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
}

.detail-row:hover {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding-left: 1rem;
  padding-right: 1rem;
  margin: 0 -1rem;
}

.detail-row:last-child {
  border-bottom: none;
}

.detail-label {
  font-weight: 600;
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.detail-value {
  font-weight: 700;
  color: rgba(255, 255, 255, 0.95);
  font-size: 1rem;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.address-value {
  font-family: 'Monaco', 'Menlo', monospace;
  background: rgba(118, 75, 162, 0.2);
  color: rgba(255, 255, 255, 0.9);
  padding: 0.5rem 1rem;
  border-radius: 8px;
  border: 1px solid rgba(118, 75, 162, 0.3);
  backdrop-filter: blur(10px);
  font-size: 0.85rem;
}

.amount-value {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.currency {
  background: linear-gradient(135deg, #764ba2, #5a3494);
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  box-shadow: 0 4px 15px rgba(118, 75, 162, 0.3);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

/* Actions avec boutons glassmorphisme */
.modal-actions {
  display: flex;
  gap: 1rem;
  padding: 2rem;
  justify-content: center;
  background: rgba(255, 255, 255, 0.03);
}

.btn-cancel {
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
}

.btn-cancel:hover {
  background: rgba(255, 255, 255, 0.15);
  color: rgba(255, 255, 255, 0.95);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
}

.btn-confirm {
  background: linear-gradient(135deg, #764ba2 0%, #5a3494 100%);
  color: white;
  box-shadow: 0 8px 25px rgba(118, 75, 162, 0.4);
  border: 1px solid rgba(118, 75, 162, 0.3);
}

.btn-confirm:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 35px rgba(118, 75, 162, 0.5);
  background: linear-gradient(135deg, #8b5fbf 0%, #6a4a9e 100%);
}

.btn:focus {
  outline: 2px solid rgba(118, 75, 162, 0.5);
  outline-offset: 2px;
}

/* Animation pour les états de validation */
.form-input.error {
  border-color: #ff6b6b;
  background: rgba(255, 107, 107, 0.1);
  animation: shake 0.5s ease-in-out;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-5px); }
  75% { transform: translateX(5px); }
}

/* États de chargement avec animations fluides */
.loading-state {
  animation: fadeInOut 1.5s ease-in-out infinite;
}

@keyframes fadeInOut {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 1; }
}

/* Transition douce pour les changements d'état */
.state-transition {
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Effets de survol pour l'interactivité */
.interactive-element {
  cursor: pointer;
  transition: all 0.3s ease;
}

.interactive-element:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

/* Scrollbar personnalisée */
.chat-main ::-webkit-scrollbar {
  width: 8px;
}

.chat-main ::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
}

.chat-main ::-webkit-scrollbar-thumb {
  background: linear-gradient(135deg, #667eea, #764ba2);
  border-radius: 10px;
  box-shadow: inset 0 0 2px rgba(255, 255, 255, 0.2);
}

.chat-main ::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(135deg, #5a67d8, #6b46c1);
}

/* Responsive design */
@media (max-width: 768px) {
  .chat-container {
    width: 95vw;
    height: 95vh;
    border-radius: 16px;
    margin: 10px;
  }
  
  .chat-main {
    border-radius: 0 16px 16px 0;
  }
  
  .chat-header {
    padding: 1rem 1.5rem;
  }
  
  .session-label {
    font-size: 0.65rem;
  }
  
  .session-id {
    font-size: 0.9rem;
  }
  
  .auth-error-content {
    padding: 2rem;
    margin: 20px;
    border-radius: 16px;
  }
  
  .error-icon {
    font-size: 3rem;
  }
  
  .auth-error h3 {
    font-size: 1.5rem;
  }
  
  .auth-error p {
    font-size: 1rem;
  }
  
  .transaction-modal {
    width: 95%;
    margin: 20px;
    border-radius: 16px;
  }
  
  .modal-header {
    padding: 1.5rem 1.5rem 1rem 1.5rem;
  }
  
  .notification-icon {
    font-size: 2.5rem;
  }
  
  .modal-header h3 {
    font-size: 1.3rem;
  }
  
  .transaction-details {
    padding: 1.5rem;
  }
  
  .modal-actions {
    flex-direction: column;
    padding: 1.5rem;
    gap: 0.75rem;
  }
  
  .btn {
    width: 100%;
    padding: 14px 24px;
    font-size: 14px;
  }
  
  .detail-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
    padding: 0.75rem 0;
  }
  
  .detail-row:hover {
    margin: 0;
    padding: 0.75rem 0;
  }
  
  .detail-label {
    font-size: 0.8rem;
  }
  
  .detail-value {
    font-size: 0.9rem;
  }
  
  .address-value {
    font-size: 0.75rem;
    padding: 0.4rem 0.8rem;
    word-break: break-all;
  }
  
  .currency {
    font-size: 0.7rem;
    padding: 0.2rem 0.6rem;
  }
  
  .floating-orb {
    display: none;
  }
}

@media (max-width: 480px) {
  .chat-container {
    width: 100vw;
    height: 100vh;
    border-radius: 0;
    margin: 0;
    border: none;
  }
  
  .chat-main {
    border-radius: 0;
  }
  
  .chat-header {
    padding: 1rem;
  }
  
  .auth-error-content {
    margin: 10px;
    padding: 1.5rem;
  }
  
  .transaction-modal {
    width: 100%;
    margin: 10px;
    max-height: 90vh;
    overflow-y: auto;
  }
  
  .modal-header {
    padding: 1rem;
  }
  
  .transaction-details {
    padding: 1rem;
  }
  
  .modal-actions {
    padding: 1rem;
  }
}

.model-select-wrapper {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-left: auto;
}

.model-select {
  padding: 8px 24px 8px 12px;
  border-radius: 12px;
  border: 1px solid rgba(118, 75, 162, 0.25);
  background: rgba(255,255,255,0.15);
  color: #764ba2;
  font-weight: 600;
  font-size: 1rem;
  outline: none;
  transition: border 0.2s, background 0.2s;
  box-shadow: 0 2px 8px rgba(118, 75, 162, 0.08);
  font-family: 'Roboto', 'Inter', 'Poppins', Arial, sans-serif;
}

.model-select:focus {
  border-color: #764ba2;
  background: rgba(255,255,255,0.25);
}

.model-select-label {
  font-size: 0.95rem;
  color: #764ba2;
  font-weight: 700;
  margin-left: 4px;
}
</style>