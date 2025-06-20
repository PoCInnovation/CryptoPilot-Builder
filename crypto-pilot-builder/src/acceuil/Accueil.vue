<template>
  <div class="app-container">
    <aside class="sidebar">
      <header class="sidebar-header">
        <h2 class="sidebar-title">CryptoPilot Builder</h2>
      </header>
      <nav class="chat-navigation">
        <section class="chat-controls-section">
          <button class="new-chat-button" @click="createNewChat">
            + Nouveau Chat
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
        <h1 class="welcome-title">Welcome</h1>

        <!-- Bouton de connexion/profil utilisateur -->
        <div class="user-section">
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
          <button v-else class="login-button" @click="showAuthModal = true">
            <span class="login-icon">👤</span>
            Se connecter
          </button>
        </div>
      </header>
      <section class="dashboard-section">
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
          <!-- Protection du bouton Talk to Agent -->
          <div v-if="isAuthenticated" class="authenticated-actions">
            <router-link to="/AI" class="agent-navigation-link">
              <button class="configure-agent-button">
                ⚙️ Configurer mon Agent
              </button>
            </router-link>

            <!-- Bouton pour accéder au chat si la configuration est valide -->
            <router-link
              v-if="hasValidConfig"
              to="/chat"
              class="agent-navigation-link"
            >
              <button class="chat-access-button">💬 Accéder au Chat</button>
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
    </main>

    <!-- Menu contextuel -->
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

    <!-- Composant d'authentification -->
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

export default {
  name: "Accueil",
  components: {
    AuthModal,
  },
  data() {
    return {
      activeChat: 1,
      nextChatId: 2,
      editingChatId: null,
      tempChatName: "",
      showContextMenu: false,
      contextMenuX: 0,
      contextMenuY: 0,
      contextMenuChatId: null,
      showAuthModal: false,
      redirectAfterAuth: null,
      chats: [{ id: 1, name: "Trading Analysis" }],
    };
  },
  computed: {
    ...mapState("auth", ["isAuthenticated", "user"]),
    ...mapGetters(["aiConfig"]),

    // Vérifier si la configuration est valide
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
    deleteChat(chatId) {
      if (this.chats.length <= 1) {
        alert("Vous devez garder au moins un chat");
        return;
      }
      const index = this.chats.findIndex((chat) => chat.id === chatId);
      if (index !== -1) {
        this.chats.splice(index, 1);
        if (this.activeChat === chatId) {
          this.activeChat = this.chats[0].id;
        }
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
      // Charger la configuration de l'agent après authentification
      this.loadAgentConfig();

      // Rediriger vers la page demandée si elle existe
      if (this.redirectAfterAuth) {
        this.$router.push(this.redirectAfterAuth);
        this.redirectAfterAuth = null;
      }
    },

    async handleLogout() {
      await this.logout();
      // Rediriger vers l'accueil après déconnexion
      this.$router.push("/");
    },
  },

  mounted() {
    // Vérifier l'authentification au montage
    this.$store.dispatch("auth/checkAuth");

    // Charger la config si déjà authentifié
    if (this.isAuthenticated) {
      this.loadAgentConfig();
    }

    // Gérer la redirection après authentification si nécessaire
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get("authRequired") === "true") {
      // Afficher automatiquement la modale de connexion
      this.showAuthModal = true;

      // Stocker l'URL de redirection
      this.redirectAfterAuth = urlParams.get("redirect") || "/AI";
    }
  },
};
</script>

<style scoped>
.app-container {
  display: flex;
  height: 100vh;
  font-family: "Arial", sans-serif;
  background-color: #fafafa;
}

.sidebar {
  width: 250px;
  background-color: #2c3e50;
  color: white;
  padding: 20px;
  box-shadow: 2px 0 5px rgba(0, 0, 0, 0.1);
}

.sidebar-header {
  margin-bottom: 30px;
}

.sidebar-title {
  font-size: 20px;
  font-weight: bold;
  text-align: center;
  color: #ecf0f1;
  margin: 0;
}

.chat-navigation {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.chat-controls-section {
  margin-bottom: 15px;
}

.new-chat-button {
  width: 100%;
  padding: 10px 15px;
  background-color: #27ae60;
  border: none;
  color: white;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: bold;
  transition: all 0.3s ease;
}

.new-chat-button:hover {
  background-color: #219a52;
  transform: translateY(-1px);
}

.chat-list-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.chat-item-container {
  display: flex;
  align-items: center;
  gap: 5px;
}

.chat-edit-form {
  flex: 1;
}

.chat-name-input {
  width: 100%;
  padding: 12px 15px;
  background-color: #ecf0f1;
  border: 2px solid #3498db;
  color: #2c3e50;
  border-radius: 6px;
  font-size: 14px;
  font-family: inherit;
  outline: none;
}

.chat-name-input:focus {
  border-color: #2980b9;
}

.chat-item-button {
  flex: 1;
  padding: 12px 15px;
  background-color: #34495e;
  border: none;
  color: #ecf0f1;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
  text-align: left;
}

.chat-item-button:hover {
  background-color: #3498db;
  transform: translateX(5px);
}

.chat-item-button--active {
  background-color: #3498db;
  font-weight: bold;
}

.chat-delete-button {
  width: 25px;
  height: 25px;
  background-color: #e74c3c;
  border: none;
  color: white;
  border-radius: 50%;
  cursor: pointer;
  font-size: 16px;
  font-weight: bold;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  line-height: 1;
}

.chat-delete-button:hover {
  background-color: #c0392b;
  transform: scale(1.1);
}

.context-menu {
  position: fixed;
  background-color: white;
  border: 1px solid #ddd;
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  min-width: 150px;
  overflow: hidden;
}

.context-menu-item {
  width: 100%;
  padding: 10px 15px;
  border: none;
  background: none;
  text-align: left;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: background-color 0.2s ease;
}

.context-menu-item:hover {
  background-color: #f5f5f5;
}

.context-menu-item--danger {
  color: #e74c3c;
}

.context-menu-item--danger:hover {
  background-color: #fdf2f2;
}

.context-menu-divider {
  margin: 0;
  border: none;
  border-top: 1px solid #eee;
}

.main-content {
  flex: 1;
  padding: 40px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.main-header {
  margin-bottom: 40px;
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
}

.welcome-title {
  font-size: 100px;
  font-weight: bold;
  color: #2c3e50;
  margin: 0;
}

/* Section utilisateur */
.user-section {
  position: absolute;
  right: 0;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.user-welcome {
  color: #2c3e50;
  font-weight: 500;
  font-size: 14px;
}

.login-button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  color: white;
  border-radius: 25px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.login-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.logout-button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: #e74c3c;
  border: none;
  color: white;
  border-radius: 20px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.logout-button:hover {
  background: #c0392b;
  transform: translateY(-1px);
}

.login-icon,
.logout-icon {
  font-size: 16px;
}

.dashboard-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 30px;
  max-width: 600px;
  width: 100%;
}

.widgets-container {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 200px;
  flex-wrap: wrap;
}

.crypto-widget,
.news-widget {
  width: 140px;
  height: 120px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease;
}

.crypto-widget:hover,
.news-widget:hover {
  transform: translateY(-5px);
}

.crypto-percentage {
  font-size: 24px;
  margin-bottom: 5px;
}

.crypto-symbol {
  font-size: 16px;
  opacity: 0.9;
}

.news-widget {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.news-title {
  font-size: 18px;
  text-align: center;
}

.action-section {
  width: 100%;
  display: flex;
  justify-content: center;
}

.authenticated-actions {
  display: flex;
  flex-direction: column;
  gap: 15px;
  align-items: center;
}

.agent-navigation-link {
  text-decoration: none;
}

.configure-agent-button {
  padding: 15px 30px;
  font-size: 18px;
  font-weight: bold;
  background: linear-gradient(135deg, #4caf50 0%, #45a049 100%);
  border: none;
  color: white;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
}

.configure-agent-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(76, 175, 80, 0.4);
}

.chat-access-button {
  padding: 15px 30px;
  font-size: 18px;
  font-weight: bold;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  color: white;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.chat-access-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

/* Section d'authentification requise */
.auth-required-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.talk-to-agent-button-disabled {
  padding: 15px 30px;
  font-size: 18px;
  font-weight: bold;
  background: linear-gradient(135deg, #95a5a6 0%, #7f8c8d 100%);
  border: none;
  color: white;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(149, 165, 166, 0.3);
  position: relative;
  overflow: hidden;
}

.talk-to-agent-button-disabled:hover {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.talk-to-agent-button-disabled:hover::after {
  content: "Cliquer pour se connecter";
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(102, 126, 234, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 500;
}

.auth-message {
  margin: 0;
  color: #7f8c8d;
  font-size: 14px;
  text-align: center;
  max-width: 300px;
  line-height: 1.4;
}

/* Styles pour la modale */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000;
  backdrop-filter: blur(5px);
}

.modal-container {
  background: white;
  border-radius: 16px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
  width: 90%;
  max-width: 400px;
  overflow: hidden;
  transform: scale(0.9);
  animation: modalAppear 0.3s ease forwards;
}

@keyframes modalAppear {
  to {
    transform: scale(1);
  }
}

.modal-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-title {
  font-size: 20px;
  font-weight: bold;
  margin: 0;
}

.modal-close {
  background: none;
  border: none;
  color: white;
  font-size: 24px;
  cursor: pointer;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background-color 0.2s ease;
}

.modal-close:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.login-form {
  padding: 30px;
}

.form-group {
  margin-bottom: 20px;
}

.form-label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: #2c3e50;
  font-size: 14px;
}

.form-input {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e1e8ed;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.3s ease;
  background-color: #f8f9fa;
  box-sizing: border-box;
}

.form-input:focus {
  outline: none;
  border-color: #667eea;
  background-color: white;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-input::placeholder {
  color: #95a5a6;
}

.form-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 30px;
}

.btn-secondary {
  padding: 10px 20px;
  border: 2px solid #e1e8ed;
  background: white;
  color: #2c3e50;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.btn-secondary:hover {
  background-color: #f8f9fa;
  border-color: #d1d9e0;
}

.btn-primary {
  padding: 10px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  color: white;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

@media (max-width: 768px) {
  .app-container {
    flex-direction: column;
  }
  .sidebar {
    width: 100%;
    height: auto;
  }
  .chat-navigation {
    flex-direction: row;
    overflow-x: auto;
  }
  .main-content {
    padding: 20px;
  }
  .main-header {
    flex-direction: column;
    gap: 20px;
    align-items: center;
  }
  .welcome-title {
    font-size: 36px;
  }
  .authenticated-actions {
    gap: 12px;
  }
  .configure-agent-button,
  .chat-access-button {
    padding: 12px 24px;
    font-size: 16px;
  }
  .modal-container {
    margin: 20px;
  }
  .login-form {
    padding: 20px;
  }
}
</style>
