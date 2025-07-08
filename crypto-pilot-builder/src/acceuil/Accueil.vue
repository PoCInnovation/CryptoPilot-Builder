<template>
  <div class="app-container">
    <aside class="sidebar">
      <header class="sidebar-header">
        <h2 class="sidebar-title">CryptoPilot Builder</h2>
      </header>
      <nav class="chat-navigation">
        <section class="chat-controls-section">
          <!-- Bouton Nouveau Chat uniquement pour les utilisateurs authentifiés -->
          <button v-if="isAuthenticated" class="new-chat-button" @click="createNewChat">
            + Nouveau Chat
          </button>
          <!-- Bouton Se connecter pour les utilisateurs non authentifiés -->
          <button v-else class="login-button" @click="showAuthModal = true">
            <span class="login-icon">👤</span>
            Se connecter
          </button>
        </section>
        <section class="chat-list-section">
          <article
            v-for="chat in chats"
            :key="chat.id"
            class="chat-item-container"
          >
            <form
              v-if="editingChatId === chat.id"
              class="chat-edit-form"
              @submit.prevent="saveEditingChat"
            >
              <input
                v-model="tempChatName"
                @keydown="handleEditKeydown"
                @blur="saveEditingChat"
                ref="chatEditInput"
                class="chat-name-input"
                maxlength="50"
                type="text"
              />
            </form>
            <button
              v-else
              :class="[
                'chat-item-button',
                { 'chat-item-button--active': chat.id === activeChat },
              ]"
              @click="selectChat(chat.id)"
              @dblclick="startEditingChat(chat.id)"
              @contextmenu="showChatContextMenu($event, chat.id)"
              :title="'Double-cliquez pour renommer | Clic droit pour plus d\'options'"
            >
              {{ chat.name }}
            </button>
            <button
              class="chat-delete-button"
              @click="deleteChat(chat.id)"
              title="Supprimer ce chat"
              :aria-label="`Supprimer le chat ${chat.name}`"
            >
              ×
            </button>
          </article>
        </section>
      </nav>
    </aside>
    <main class="main-content">
      <header class="main-header">
        <div class="user-section">
          <!-- Affichage uniquement pour les utilisateurs authentifiés -->
          <div v-if="isAuthenticated" class="user-info">
            <span class="user-welcome"
              >Bonjour, {{ user?.username || user?.email }}</span
            >
            <button
              class="logout-button"
              @click="handleLogout"
              title="Se déconnecter"
            >
              <span class="logout-icon">🚪</span>
              Déconnexion
            </button>
          </div>
        </div>
      </header>
      
      <!-- Section Dashboard (widgets + actions) -->
      <section v-if="!showChat" class="dashboard-section">
        <div class="widgets-container">
          <article class="crypto-widget">
            <span class="crypto-percentage">+27%</span>
            <span class="crypto-symbol">BTC</span>
          </article>
          <article class="news-widget">
            <span class="news-title">Actu by lulu</span>
          </article>
        </div>
        <section class="action-section">
          <div v-if="isAuthenticated" class="authenticated-actions">
            <router-link to="/AI" class="agent-navigation-link">
              <button class="configure-agent-button">
                ⚙️ Configurer mon Agent
              </button>
            </router-link>
            <button
              v-if="hasValidConfig"
              class="chat-access-button"
              @click="showChat = true"
            >
              💬 Accéder au Chat
            </button>
          </div>
          <div v-else class="auth-required-section">
            <button
              class="talk-to-agent-button-disabled"
              @click="showAuthModal = true"
            >
              🔒 Configurer mon Agent
            </button>
            <p class="auth-message">
              Veuillez vous connecter pour configurer votre agent IA
              personnalisé
            </p>
          </div>
        </section>
      </section>
      
      <!-- Section Chat intégrée -->
      <section v-else class="chat-section">
        <div class="chat-header">
          <button class="back-dashboard-btn" @click="showChat = false">
            ← Retour au Dashboard
          </button>
          <h3 class="chat-title">Chat avec votre Agent IA</h3>
        </div>
        <div class="chat-container">
          <Chatbot />
        </div>
      </section>
    </main>
    
    <aside
      v-if="showContextMenu"
      class="context-menu"
      :style="{ left: contextMenuX + 'px', top: contextMenuY + 'px' }"
      role="menu"
    >
      <button
        @click="renameFromContextMenu"
        class="context-menu-item"
        role="menuitem"
      >
        ✏️ Renommer
      </button>
      <button @click="duplicateChat" class="context-menu-item" role="menuitem">
        📋 Dupliquer
      </button>
      <hr class="context-menu-divider" role="separator" />
      <button
        @click="deleteChatFromContextMenu"
        class="context-menu-item context-menu-item--danger"
        role="menuitem"
      >
        🗑️ Supprimer
      </button>
    </aside>
    
    <AuthModal
      :show="showAuthModal"
      @close="showAuthModal = false"
      @authenticated="handleAuthenticated"
    />
  </div>
</template>

<script>
import { mapState, mapActions, mapGetters } from "vuex";
import AuthModal from "../components/AuthModal.vue";
import apiService from "../services/apiService";
import Chatbot from '../components/chatbot.vue';

export default {
  name: "Accueil",
  components: {
    AuthModal,
    Chatbot,
  },
  data() {
    return {
      activeChat: null,
      nextChatId: 1,
      editingChatId: null,
      tempChatName: "",
      showContextMenu: false,
      contextMenuX: 0,
      contextMenuY: 0,
      contextMenuChatId: null,
      showAuthModal: false,
      redirectAfterAuth: null,
      chats: [],
      showChat: false,
    };
  },
  computed: {
    ...mapState("auth", ["isAuthenticated", "user"]),
    ...mapGetters(["aiConfig"]),
    hasValidConfig() {
      return (
        this.aiConfig &&
        this.aiConfig.selectedModel &&
        this.aiConfig.apiKey &&
        this.aiConfig.prompt
      );
    },
  },
  methods: {
    ...mapActions("auth", ["logout"]),
    ...mapActions(["loadAgentConfig"]),
    selectChat(chatId) {
      this.activeChat = chatId;
      console.log(`Chat sélectionné: ${chatId}`);
    },
    createNewChat() {
      const chatName = prompt(
        "Nom du nouveau chat:",
        `Chat ${this.nextChatId}`
      );
      if (chatName && chatName.trim()) {
        const newChat = {
          id: this.nextChatId,
          name: chatName.trim(),
        };
        this.chats.push(newChat);
        this.activeChat = this.nextChatId;
        this.nextChatId++;
        console.log(`Nouveau chat créé: ${newChat.name}`);
      }
    },
    startEditingChat(chatId) {
      const chat = this.chats.find((c) => c.id === chatId);
      if (chat) {
        this.editingChatId = chatId;
        this.tempChatName = chat.name;
      }
    },
    saveEditingChat() {
      if (this.tempChatName.trim()) {
        const chat = this.chats.find((c) => c.id === this.editingChatId);
        if (chat) {
          chat.name = this.tempChatName.trim();
        }
      }
      this.cancelEditingChat();
    },
    cancelEditingChat() {
      this.editingChatId = null;
      this.tempChatName = "";
    },
    showChatContextMenu(event, chatId) {
      event.preventDefault();
      this.contextMenuChatId = chatId;
      this.contextMenuX = event.clientX;
      this.contextMenuY = event.clientY;
      this.showContextMenu = true;
      document.addEventListener("click", this.hideContextMenu);
    },
    hideContextMenu() {
      this.showContextMenu = false;
      this.contextMenuChatId = null;
      document.removeEventListener("click", this.hideContextMenu);
    },
    renameFromContextMenu() {
      if (this.contextMenuChatId) {
        this.startEditingChat(this.contextMenuChatId);
        this.hideContextMenu();
      }
    },
    duplicateChat() {
      if (this.contextMenuChatId) {
        const originalChat = this.chats.find(
          (c) => c.id === this.contextMenuChatId
        );
        if (originalChat) {
          const newChat = {
            id: this.nextChatId,
            name: `${originalChat.name} (copie)`,
          };
          this.chats.push(newChat);
          this.nextChatId++;
          this.hideContextMenu();
        }
      }
    },
    deleteChatFromContextMenu() {
      if (this.contextMenuChatId) {
        this.deleteChat(this.contextMenuChatId);
        this.hideContextMenu();
      }
    },
    async loadChatsFromApi() {
      try {
        const response = await apiService.listSessions();
        const sessions = response.sessions || [];
        this.chats = sessions.map((session, idx) => ({
          id: session.session_id,
          name: session.session_name || `Chat ${idx + 1}`,
        }));
        if (this.chats.length > 0) {
          this.activeChat = this.chats[0].id;
          this.nextChatId = this.chats.length + 1;
        }
      } catch (error) {
        console.error("Erreur lors du chargement des chats:", error);
        this.chats = [{ id: 1, name: "Trading Analysis" }];
        this.activeChat = 1;
        this.nextChatId = 2;
      }
    },
    async deleteChat(chatId) {
      if (this.chats.length <= 1) {
        alert("Vous devez garder au moins un chat");
        return;
      }
      try {
        await apiService.deleteSession(chatId);
        const index = this.chats.findIndex((chat) => chat.id === chatId);
        if (index !== -1) {
          this.chats.splice(index, 1);
          if (this.activeChat === chatId && this.chats.length > 0) {
            this.activeChat = this.chats[0].id;
          }
        }
      } catch (error) {
        console.error("Erreur lors de la suppression du chat:", error);
        alert("Erreur lors de la suppression du chat.");
      }
    },
    handleEditKeydown(event) {
      if (event.key === "Enter") {
        this.saveEditingChat();
      } else if (event.key === "Escape") {
        this.cancelEditingChat();
      }
    },
    handleAuthenticated() {
      this.loadAgentConfig();
      if (this.redirectAfterAuth) {
        this.$router.push(this.redirectAfterAuth);
        this.redirectAfterAuth = null;
      }
    },
    async handleLogout() {
      await this.logout();
      this.$router.push("/");
    },
  },
  async mounted() {
    this.$store.dispatch("auth/checkAuth");
    if (this.isAuthenticated) {
      await this.loadAgentConfig();
      await this.loadChatsFromApi();
    }
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get("authRequired") === "true") {
      this.showAuthModal = true;
      this.redirectAfterAuth = urlParams.get("redirect") || "/AI";
    }
  },
};
</script>

<style scoped>
.app-container {
  display: flex;
  height: 100vh;
  font-family: 'Roboto', sans-serif;
  background: linear-gradient(120deg, rgba(28, 32, 51, 0), rgba(16, 21, 33, 0));
  border: none;
  transition: left 0.5s ease;
  overflow: hidden;
}

/* SIDEBAR */
.sidebar {
  position: fixed;
  top: 40px;
  left: 40px;
  width: 400px;
  height: 80vh;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-radius: 24px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  padding: 20px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
  color: #fff;
}

.sidebar-header {
  margin-bottom: 35px;
  text-align: center;
  animation: fadeIn 0.5s ease;
}

.sidebar-title {
  font-size: 80px;
  font-weight: 600;
  color: #f3e8ff;
  margin: 0;
  letter-spacing: 1px;
  text-shadow: 0 2px 4px rgba(0,0,0,0.3);
}

/* ANIMATIONS */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes fadeInRight {
  from { opacity: 0; transform: translateX(20px); }
  to { opacity: 1; transform: translateX(0); }
}

@keyframes slideDown {
  from { transform: translateY(-10px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

/* NAVIGATION CHAT */
.chat-navigation {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.chat-controls-section {
  margin-bottom: 20px;
  display: flex;
  gap: 80px;
}

/* BOUTONS */
.new-chat-button, .login-button, .configure-agent-button, .chat-access-button {
  padding: 14px 24px;
  border-radius: 12px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  z-index: 1;
}

.new-chat-button {
  width: 20%;
  background: linear-gradient(120deg, rgba(28, 32, 51, 0), rgba(16, 21, 33, 0));
  color: white;
  font-size: 15px;
}

.login-button {
  background: rgba(28, 32, 51, 0.1);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 6px 18px rgba(118, 75, 162, 0.3);
}

.configure-agent-button, .chat-access-button {
  padding: 18px 35px;
  font-size: 20px;
  background: linear-gradient(120deg, rgba(28, 32, 51, 0), rgba(16, 21, 33, 0));
  color: white;
  box-shadow: 0 6px 18px rgba(118, 75, 162, 0.3);
}

/* HOVER EFFECTS */
.new-chat-button:hover,
.login-button:hover,
.configure-agent-button:hover,
.chat-access-button:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(118, 75, 162, 0.4);
}

.new-chat-button::after,
.configure-agent-button::before,
.chat-access-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(120deg, rgba(255,255,255,0.2) 0%, rgba(255,255,255,0.2) 50%, rgba(255,255,255,0) 80%);
  transition: left 0.5s ease;
  z-index: -1;
}

.new-chat-button:hover::after,
.configure-agent-button:hover::before,
.chat-access-button:hover::before {
  left: 100%;
}

/* LISTE DES CHATS */
.chat-list-section {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: 70vh;
  overflow-y: auto;
  padding-right: 8px;
  scrollbar-width: thin;
  scrollbar-color: rgba(118, 75, 162, 0.6) rgba(46, 27, 77, 0.3);
}

.chat-list-section::-webkit-scrollbar {
  width: 8px;
  background-color: transparent;
}

.chat-list-section::-webkit-scrollbar-thumb {
  background: linear-gradient(120deg, rgba(28, 32, 51, 0), rgba(16, 21, 33, 0));
  border-radius: 10px;
  box-shadow: 0 2px 6px rgba(118, 75, 162, 0.3);
}

.chat-item-container:hover {
  transform: translateX(5px);
}

.chat-name-input {
  width: 100%;
  padding: 14px 18px;
  background-color: #f3e8ff;
  border: 2px solid #a552cc;
  color: #2c1b4d;
  border-radius: 10px;
  font-size: 15px;
  outline: none;
  transition: all 0.3s ease;
}

.chat-name-input:focus {
  border-color: #764ba2;
  box-shadow: 0 0 8px rgba(118, 75, 162, 0.3);
}

.chat-item-button {
  flex: 1;
  padding: 14px 18px;
  background: linear-gradient(120deg, rgba(28, 32, 51, 0), rgba(16, 21, 33, 0));
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #f3e8ff;
  border-radius: 10px;
  font-size: 30px;
  text-align: left;
  position: relative;
  overflow: hidden;
}

.chat-item-button:hover {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.3);
  transform: translateX(8px);
}

.chat-delete-button {
  width: 30px;
  height: 30px;
  background-color: #e74c3c;
  border: none;
  color: white;
  border-radius: 50%;
  font-size: 18px;
  transition: all 0.3s ease;
}

.chat-delete-button:hover {
  background-color: #c0392b;
  transform: scale(1.1) rotate(90deg);
}

/* CONTEXT MENU */
.context-menu {
  position: fixed;
  background-color: #2e1b4d;
  border: 1px solid #5a3494;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(75, 25, 140, 0.3);
  z-index: 1000;
  min-width: 180px;
  overflow: hidden;
  animation: slideDown 0.3s ease;
}

.context-menu-item {
  width: 100%;
  padding: 12px 20px;
  border: none;
  background: none;
  text-align: left;
  cursor: pointer;
  font-size: 15px;
  display: flex;
  align-items: center;
  gap: 10px;
  color: #f3e8ff;
}

.context-menu-item:hover {
  background-color: #5a3494;
}

.context-menu-divider {
  margin: 0;
  border-top: 1px solid #5a3494;
}

/* MAIN CONTENT */
.main-content {
  flex: 1;
  padding: 50px;
  display: flex;
  flex-direction: column;
  align-items: center;
  background: linear-gradient(135deg, #111421 0%, #111421 100%);
  overflow-y: auto;
}

.main-header {
  margin-bottom: 50px;
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
  animation: fadeInUp 0.6s ease;
}

.user-section {
  position: absolute;
  right: 0;
  display: flex;
  align-items: center;
  gap: 15px;
  animation: fadeInRight 0.5s ease;
}

.user-welcome {
  color: white;
  font-weight: bold;
  font-size: 16px;
  text-shadow: 0 1px 2px rgba(0,0,0,0.05);
}

.logout-button {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 20px;
  background: rgba(28, 32, 51, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: white;
  border-radius: 25px;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.logout-button:hover {
  background: rgba(28, 32, 51, 0.2);
  box-shadow: 0 8px 20px rgba(192, 57, 43, 0.4);
  transform: translateY(-1px);
}

/* DASHBOARD */
.dashboard-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 40px;
  max-width: 700px;
  width: 100%;
  animation: fadeInUp 0.6s ease;
}

.widgets-container {
  display: flex;
  justify-content: center;
  gap: 30px;
  margin-top: 150px;
  flex-wrap: wrap;
}

.crypto-widget, .news-widget {
  width: 160px;
  height: 140px;
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
  transition: all 0.4s ease;
  position: relative;
  overflow: hidden;
  transform: perspective(1000px) rotateY(0deg);
}

.crypto-widget:hover, .news-widget:hover {
  transform: perspective(1000px) rotateY(5deg) translateY(-5px);
  box-shadow: 0 10px 30px rgba(118, 75, 162, 0.4);
}

/* MODAL */
.modal-container {
  background: white;
  border-radius: 20px;
  box-shadow: 0 25px 50px rgba(75, 25, 140, 0.3);
  width: 90%;
  max-width: 450px;
  overflow: hidden;
  transform: scale(0.95);
  animation: modalAppear 0.4s ease forwards;
}

@keyframes modalAppear {
  to { transform: scale(1); }
}

/* FULLSCREEN CHAT */
.chat-fullscreen {
  width: 100vw;
  height: 100vh;
  position: fixed;
  left: 0;
  top: 0;
  z-index: 2000;
  background: #fff;
  display: flex;
  flex-direction: column;
  padding: 20px;
  box-sizing: border-box;
  animation: fadeIn 0.5s ease;
}

.back-dashboard-btn {
  position: absolute;
  top: 20px;
  left: 20px;
  z-index: 10;
  background: linear-gradient(120deg, rgba(28, 32, 51, 0), rgba(16, 21, 33, 0));
  color: #fff;
  border: none;
  border-radius: 12px;
  padding: 12px 24px;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 6px 18px rgba(118, 75, 162, 0.3);
}

.back-dashboard-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(118, 75, 162, 0.4);
}

/* RESPONSIVE DESIGN */
@media (max-width: 768px) {
  .app-container {
    flex-direction: column;
  }
  
  .sidebar {
    width: 100%;
    height: auto;
    padding: 15px;
  }
  
  .chat-navigation {
    flex-direction: row;
    overflow-x: auto;
    padding-bottom: 10px;
  }
  
  .main-content {
    padding: 20px;
  }
  
  .configure-agent-button,
  .chat-access-button {
    padding: 14px 28px;
    font-size: 18px;
  }
}
</style>