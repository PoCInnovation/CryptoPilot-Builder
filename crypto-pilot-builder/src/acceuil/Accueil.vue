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
              <button class="chat-access-button">💬 Accéder au Chat</button>
            </router-link>
            <router-link
              v-if="hasValidConfig"
              to="/memory"
              class="agent-navigation-link"
            >
              <button class="memory-button">🧠 Mémoire de l'IA</button>
            </router-link>
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
.sidebar {
  position: fixed;
  top: 40px;
  left: 40px;
  width: 200px;
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
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
.sidebar-title {
  font-size: 80px;
  font-weight: 600px;
  color: #f3e8ff;
  margin: 0;
  letter-spacing: 1px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}
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
.new-chat-button {
  width: 20%;
  padding-top: 12px;
  padding-right: 18px;
  padding-bottom: 12px;
  padding-left: 10px;
  background: linear-gradient(120deg, rgba(28, 32, 51, 0), rgba(16, 21, 33, 0));
  border: none;
  color: white;
  border-radius: 10px;
  cursor: pointer;
  font-size: 15px;
  font-weight: bold;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  text-align: center;
}
.new-chat-button:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(125, 82, 204, 0.4);
}
.new-chat-button::after {
  content: "";
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(120deg, rgba(28, 32, 51, 0), rgba(16, 21, 33, 0));
  border: none;
  transition: left 0.5s ease;
}
.new-chat-button:hover::after {
  left: 100%;
}
.login-button {
  width: 100%;
  padding: 14px 24px;
  background: rgba(28, 32, 51, 0.1);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: white;
  border-radius: 30px;
  cursor: pointer;
  font-size: 15px;
  font-weight: 700;
  transition: all 0.3s ease;
  box-shadow: 0 6px 18px rgba(118, 75, 162, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
}
.login-button:hover {
  background: rgba(28, 32, 51, 0.2);
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(118, 75, 162, 0.4);
}
.login-icon {
  font-size: 18px;
  margin-right: 8px;
}
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
.chat-list-section::-webkit-scrollbar-track {
  background: rgba(46, 27, 77, 0.3);
  border-radius: 10px;
  margin: 5px 0;
  box-shadow: inset 0 0 3px rgba(0, 0, 0, 0.1);
}
.chat-list-section::-webkit-scrollbar-thumb {
  background: linear-gradient(120deg, rgba(28, 32, 51, 0), rgba(16, 21, 33, 0));
  border: none;
  transition: left 0.5s ease;
  border-radius: 10px;
  box-shadow: 0 2px 6px rgba(118, 75, 162, 0.3);
  transition: all 0.3s ease;
}
.chat-list-section::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(120deg, rgba(28, 32, 51, 0), rgba(16, 21, 33, 0));
  border: none;
  transition: left 0.5s ease;
  box-shadow: 0 3px 8px rgba(157, 78, 221, 0.4);
  transform: scaleX(1.2);
}
.chat-list-section::-webkit-scrollbar-thumb:active {
  background: linear-gradient(120deg, rgba(28, 32, 51, 0), rgba(16, 21, 33, 0));
  border: none;
  transition: left 0.5s ease;
}
.chat-list-section::-webkit-scrollbar-thumb {
  opacity: 0.7;
}
.chat-list-section:hover::-webkit-scrollbar-thumb {
  opacity: 1;
}
@supports (scrollbar-width: thin) {
  .chat-list-section {
    scrollbar-width: thin;
    scrollbar-color: #764ba2 rgba(46, 27, 77, 0.3);
  }
}
.chat-list-section:hover {
  box-shadow: inset 2px 0 0 rgba(118, 75, 162, 0.2);
  transition: box-shadow 0.3s ease;
}
.chat-list-section::-webkit-scrollbar-thumb {
  position: relative;
}
.chat-list-section::-webkit-scrollbar-thumb::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(45deg,
    rgba(255,255,255,0.1) 0%,
    transparent 50%,
    rgba(255,255,255,0.1) 100%);
  border-radius: 10px;
  opacity: 0;
  transition: opacity 0.3s ease;
}
.chat-list-section::-webkit-scrollbar-thumb:hover::before {
  opacity: 1;
}
.chat-item-container {
  display: flex;
  align-items: center;
  gap: 8px;
  position: relative;
  transition: transform 0.2s ease;
}
.chat-item-container:hover {
  transform: translateX(5px);
}
.chat-edit-form {
  flex: 1;
}
.chat-name-input {
  width: 100%;
  padding: 14px 18px;
  background-color: #f3e8ff;
  border: 2px solid #a552cc;
  color: #2c1b4d;
  border-radius: 10px;
  font-size: 15px;
  font-family: inherit;
  outline: none;
  transition: all 0.3s ease;
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.05);
}
.chat-name-input:focus {
  border-color: #764ba2;
  box-shadow: 0 0 8px rgba(118, 75, 162, 0.3);
}
.chat-item-button {
  flex: 1;
  padding: 14px 18px;
  background: linear-gradient(120deg, rgba(28, 32, 51, 0), rgba(16, 21, 33, 0));
  border: none;
  transition: left 0.5s ease;
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #f3e8ff;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 30px;
  font-weight: 500;
  text-align: left;
  position: relative;
  overflow: hidden;
}
.chat-item-button:hover {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.3);
  transform: translateX(8px);
}
.chat-item-button::after {
  content: "";
  position: absolute;
  top: 0;
  left: -50%;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    120deg,
    rgba(255, 255, 255, 0.1) 0%,
    rgba(255, 255, 255, 0.1) 50%,
    rgba(255, 255, 255, 0) 80%
  );
  transition: left 0.5s ease;
}
.chat-item-button:hover::after {
  left: 100%;
}
.chat-item-button--active {
  background: linear-gradient(120deg, rgba(28, 32, 51, 0), rgba(16, 21, 33, 0));
  border: none;
  transition: left 0.5s ease;
  font-weight: bold;
  box-shadow: 0 4px 12px rgba(118, 75, 162, 0.3);
  transform: translateX(5px);
}
.chat-delete-button {
  width: 30px;
  height: 30px;
  background-color: #e74c3c;
  border: none;
  color: white;
  border-radius: 50%;
  cursor: pointer;
  font-size: 18px;
  font-weight: bold;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
  position: relative;
}
.chat-delete-button:hover {
  background-color: #c0392b;
  transform: scale(1.1) rotate(90deg);
}
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
@keyframes slideDown {
  from {
    transform: translateY(-10px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
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
  transition: background-color 0.2s ease;
  color: #f3e8ff;
}
.context-menu-item:hover {
  background-color: #5a3494;
}
.context-menu-item--danger {
  color: #ff7675;
}
.context-menu-divider {
  margin: 0;
  border: none;
  border-top: 1px solid #5a3494;
}
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
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
.user-section {
  position: absolute;
  right: 0;
  display: flex;
  align-items: center;
  gap: 15px;
  animation: fadeInRight 0.5s ease;
}
@keyframes fadeInRight {
  from {
    opacity: 0;
    transform: translateX(20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}
.user-info {
  display: flex;
  align-items: center;
  gap: 18px;
}
.user-welcome {
  color: white;
  font-weight: bold;
  font-size: 16px;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}
.logout-button {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 20px;
  background: rgba(28, 32, 51, 0.1);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: white;
  border-radius: 25px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}
.logout-button:hover {
  background: rgba(28, 32, 51, 0.2);
  box-shadow: 0 8px 20px rgba(192, 57, 43, 0.4);
  transform: translateY(-1px);
}
.logout-icon {
  font-size: 18px;
}
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
.crypto-widget,
.news-widget {
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
.crypto-widget::before,
.news-widget::before {
  content: "";
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(
    circle at center,
    rgba(255, 255, 255, 0.2) 0%,
    transparent 70%
  );
  transform: rotate(45deg);
  pointer-events: none;
}
.crypto-widget:hover,
.news-widget:hover {
  transform: perspective(1000px) rotateY(5deg) translateY(-5px);
  box-shadow: 0 10px 30px rgba(118, 75, 162, 0.4);
}
.crypto-percentage {
  font-size: 28px;
  margin-bottom: 8px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}
.crypto-symbol {
  font-size: 18px;
  opacity: 0.9;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}
.news-widget {
  background: linear-gradient(120deg, rgba(28, 32, 51, 0), rgba(16, 21, 33, 0));
  border: none;
}
.news-title {
  font-size: 20px;
  text-align: center;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}
.action-section {
  width: 100%;
  display: flex;
  justify-content: center;
}
.authenticated-actions {
  display: flex;
  flex-direction: column;
  gap: 20px;
  align-items: center;
}
.agent-navigation-link {
  text-decoration: none;
}
.configure-agent-button {
  padding: 18px 35px;
  font-size: 20px;
  font-weight: bold;
  background: linear-gradient(120deg, rgba(28, 32, 51, 0), rgba(16, 21, 33, 0));
  border: none;
  color: white;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 6px 18px rgba(118, 75, 162, 0.3);
  position: relative;
  overflow: hidden;
  z-index: 1;
}
.configure-agent-button::before {
  content: "";
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    120deg,
    rgba(255, 255, 255, 0.2) 0%,
    rgba(255, 255, 255, 0.2) 50%,
    rgba(255, 255, 255, 0) 80%
  );
  transition: left 0.5s ease;
  z-index: -1;
}
.configure-agent-button:hover::before {
  left: 100%;
}
.configure-agent-button:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(118, 75, 162, 0.4);
}
.chat-access-button {
  padding: 18px 35px;
  font-size: 20px;
  font-weight: bold;
  background: linear-gradient(120deg, rgba(28, 32, 51, 0), rgba(16, 21, 33, 0));
  border: none;
  color: white;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 6px 18px rgba(165, 82, 204, 0.3);
  position: relative;
  overflow: hidden;
  z-index: 1;
}
.chat-access-button::before {
  content: "";
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    120deg,
    rgba(255, 255, 255, 0.2) 0%,
    rgba(255, 255, 255, 0.2) 50%,
    rgba(255, 255, 255, 0) 80%
  );
  transition: left 0.5s ease;
  z-index: -1;
}
.chat-access-button:hover::before {
  left: 100%;
}
.chat-access-button:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(165, 82, 204, 0.4);
}

.memory-button {
  padding: 18px 35px;
  font-size: 20px;
  font-weight: bold;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  color: white;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 6px 18px rgba(102, 126, 234, 0.3);
  position: relative;
  overflow: hidden;
  z-index: 1;
}

.memory-button::before {
  content: "";
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    120deg,
    rgba(255, 255, 255, 0.2) 0%,
    rgba(255, 255, 255, 0.2) 50%,
    rgba(255, 255, 255, 0) 80%
  );
  transition: left 0.5s ease;
  z-index: -1;
}

.memory-button:hover::before {
  left: 100%;
}

.memory-button:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4);
}

.auth-required-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
}
.talk-to-agent-button-disabled {
  padding: 18px 35px;
  font-size: 20px;
  font-weight: bold;
  background: rgba(28, 32, 51, 0.1);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: white;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.1);
  position: relative;
  overflow: hidden;
  text-align: center;
}
.talk-to-agent-button-disabled:hover {
  background: rgba(28, 32, 51, 0.2);
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(118, 75, 162, 0.4);
}
.talk-to-agent-button-disabled:hover::after {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(28, 32, 51, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 500;
  color: #fff;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
  animation: fadeInUp 0.3s ease;
}
.auth-message {
  margin: 0;
  color: white;
  font-size: 15px;
  text-align: center;
  max-width: 320px;
  line-height: 1.5;
  font-style: italic;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}
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
  to {
    transform: scale(1);
  }
}
.modal-header {
  background: linear-gradient(120deg, rgba(28, 32, 51, 0), rgba(16, 21, 33, 0));
  border: none;
  color: white;
  padding: 25px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}
.modal-title {
  font-size: 22px;
  font-weight: bold;
  margin: 0;
  letter-spacing: 0.5px;
}
.modal-close {
  background: none;
  border: none;
  color: white;
  font-size: 26px;
  cursor: pointer;
  width: 35px;
  height: 35px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background-color 0.2s ease;
}
.modal-close:hover {
  background-color: rgba(255, 255, 255, 0.2);
}
.login-form {
  padding: 35px;
}
.form-group {
  margin-bottom: 25px;
}
.form-label {
  display: block;
  margin-bottom: 10px;
  font-weight: 700;
  color: #4b2e83;
  font-size: 15px;
}
.form-input {
  width: 100%;
  padding: 14px 18px;
  border: 2px solid #dcdcdc;
  border-radius: 12px;
  font-size: 15px;
  transition: all 0.3s ease;
  background-color: #f8f6ff;
  box-sizing: border-box;
  font-family: inherit;
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.05);
}
.form-input:focus {
  outline: none;
  border-color: #764ba2;
  background-color: white;
  box-shadow: 0 0 0 4px rgba(118, 75, 162, 0.15);
}
.form-input::placeholder {
  color: #aaa;
}
.form-actions {
  display: flex;
  gap: 15px;
  justify-content: flex-end;
  margin-top: 35px;
}
.btn-secondary {
  padding: 12px 24px;
  border: 2px solid #e1e8ed;
  background: white;
  color: #4b2e83;
  border-radius: 10px;
  cursor: pointer;
  font-size: 15px;
  font-weight: 600;
  transition: all 0.3s ease;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
}
.btn-secondary:hover {
  background-color: #f3e8ff;
  border-color: #c5b3f4;
}
.btn-primary {
  padding: 12px 24px;
  background: linear-gradient(120deg, rgba(28, 32, 51, 0), rgba(16, 21, 33, 0));
  border: none;
  color: white;
  border-radius: 10px;
  cursor: pointer;
  font-size: 15px;
  font-weight: 600;
  transition: all 0.3s ease;
  box-shadow: 0 6px 18px rgba(118, 75, 162, 0.3);
}
.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(118, 75, 162, 0.4);
}
.chat-fullscreen {
  width: 100vw;
  height: 100vh;
  position: fixed;
  left: 0; top: 0;
  z-index: 2000;
  background: #fff;
}
.back-dashboard-btn {
  position: absolute;
  top: 20px; left: 20px;
  z-index: 10;
  background: #764ba2;
  color: #fff;
  border: none;
  border-radius: 8px;
  padding: 10px 18px;
  font-size: 16px;
  cursor: pointer;
}
@media (max-width: 768px) {
  .app-container {
    flex-direction: column;
  }
  .sidebar {
    width: 100%;
    height: auto;
    padding: 20px;
  }
  .chat-navigation {
    flex-direction: row;
    overflow-x: auto;
    padding-bottom: 10px;
  }
  .main-content {
    padding: 25px;
  }
  .main-header {
    flex-direction: column;
    gap: 25px;
    align-items: center;
  }
  .welcome-title {
    font-size: 42px;
    text-align: center;
  }
  .authenticated-actions {
    gap: 15px;
  }
  .configure-agent-button,
  .chat-access-button {
    padding: 14px 28px;
    font-size: 18px;
  }
  .modal-container {
    margin: 25px;
  }
  .login-form {
    padding: 25px;
  }
  .chat-list-section::-webkit-scrollbar {
    width: 6px;
  }
  .chat-list-section {
    padding-right: 6px;
  }
}
</style>
