<template>
  <div class="app-container">
    <!-- Sidebar -->
    <aside class="sidebar">
      <header class="sidebar-header">
        <h2 class="sidebar-title">CryptoPilot Builder</h2>
      </header>
      <nav class="chat-navigation">
        <section class="chat-controls">
          <button v-if="isAuthenticated" class="btn-icon" @click="createNewChat" title="Nouveau chat">+</button>
          <router-link v-if="isAuthenticated" to="/memory" class="btn-icon" title="Mémoire IA">🧠</router-link>
          <button v-if="isAuthenticated" class="btn-icon" @click="showChat = false" title="Retour">🏠️</button>
          <button v-else class="btn-full" @click="showAuthModal = true">👤 Se connecter</button>
        </section>
        <section class="chat-list-section">
          <article v-for="chat in chatsForTemplate" :key="chat.id" class="chat-item">
            <form v-if="editingChatId === chat.id" @submit.prevent="saveEditingChat" class="chat-edit-form">
              <input 
                v-model="tempChatName"
                @blur="saveEditingChat"
                @keydown="handleEditKeydown"
                maxlength="50" 
                class="chat-name-input" 
                ref="chatNameInput"
              />
            </form>
            <button 
              v-else 
              :class="['chat-name', { active: chat.id === activeChat }]"
              @click="selectChat(chat.id)"
              @dblclick="startEditingChat(chat.id)"
              @contextmenu.prevent="showChatContextMenu($event, chat.id)"
              :title="'Double-cliquez pour renommer ou clic droit pour options'"
            >
              {{ chat.name }}
            </button>
            <button class="chat-delete" @click="deleteChat(chat.id)" aria-label="Supprimer">×</button>
          </article>
        </section>
      </nav>
    </aside>

    <!-- Contenu principal -->
    <main class="main-content">
      <!-- En-tête utilisateur -->
      <header class="main-header">
        <div class="user-section">
          <div v-if="isAuthenticated" class="user-info">
            <span class="user-welcome">Bonjour, {{ user?.username || user?.email }}</span>
            <button class="logout-button" @click="handleLogout">
              <span class="logout-icon">🚪</span> Déconnexion
            </button>
          </div>
        </div>
      </header>

      <!-- Dashboard -->
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

        <!-- Actions -->
        <section class="action-section">
          <div v-if="isAuthenticated" class="authenticated-actions">
            <router-link to="/AI" class="agent-navigation-link">
              <button class="configure-agent-button">⚙️ Configurer mon Agent</button>
            </router-link>
            <button v-if="hasValidConfig" class="chat-access-button" @click="showChat = true">
              💬 Accéder au Chat
            </button>
          </div>
          <div v-else class="auth-required-section">
            <button class="talk-to-agent-button-disabled" @click="showAuthModal = true">
              🔒 Configurer mon Agent
            </button>
            <p class="auth-message">Veuillez vous connecter pour configurer votre agent IA personnalisé</p>
          </div>
        </section>
      </section>

      <!-- Chat -->
      <section v-else class="chat-section">
        <div class="chat-container">
          <Chatbot 
            :key="activeChat"
            :active-session-id="activeChat" 
            @session-changed="handleSessionChanged"
            @new-session-created="handleNewSessionCreated"
          />
        </div>
      </section>
    </main>

    <!-- Menu contextuel -->
    <aside v-if="showContextMenu" class="context-menu" :style="{ left: contextMenuX + 'px', top: contextMenuY + 'px' }">
      <button @click="renameFromContextMenu" class="context-menu-item">✏️ Renommer</button>
      <button @click="duplicateChat" class="context-menu-item">📋 Dupliquer</button>
      <hr class="context-menu-divider" />
      <button @click="deleteChatFromContextMenu" class="context-menu-item context-menu-item--danger">🗑️ Supprimer</button>
    </aside>

    <!-- Modale d'authentification -->
    <AuthModal :show="showAuthModal" @close="showAuthModal = false" @authenticated="handleAuthenticated" />
  </div>
</template>

<script>
import { mapState, mapActions, mapGetters } from "vuex";
import AuthModal from "../components/AuthModal.vue";
import Chatbot from '../components/chatbot.vue';
import apiService from "../services/apiService";

export default {
  name: "Accueil",
  components: {
    AuthModal,
    Chatbot,
  },
  data() {
    return {
      // Structure simplifiée - directement compatible avec le template
      chats: [], // Format: [{id: sessionId, name: chatName}, ...]
      chatSessions: {}, // Mapping sessionId -> {messages, originalName, etc.}
      
      // Variables d'interface
      activeChat: null, // ID de session active
      currentSessionId: null, // Pour compatibilité avec Chatbot
      nextChatId: 1,
      editingChatId: null,
      tempChatName: "",
      showContextMenu: false,
      contextMenuX: 0,
      contextMenuY: 0,
      contextMenuChatId: null,
      showAuthModal: false,
      redirectAfterAuth: null,
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
    // Computed pour le template (maintenant c'est juste un alias)
    chatsForTemplate() {
      return this.chats;
    }
  },
  methods: {
    ...mapActions("auth", ["logout"]),
    ...mapActions(["loadAgentConfig"]),

    // CRÉATION D'UN NOUVEAU CHAT - Version simplifiée
    async createNewChat() {
      const chatName = prompt("Nom du nouveau chat:", `Chat ${this.nextChatId}`);
      if (chatName && chatName.trim()) {
        try {
          console.log("🆕 Création d'un nouveau chat:", chatName.trim());
          
          // Créer une nouvelle session via l'API
          const sessionData = await apiService.createNewSession(chatName.trim());
          const sessionId = sessionData.session_id;
          
          if (!sessionId) {
            throw new Error("Aucun session_id reçu de l'API");
          }

          // Créer le chat avec l'ID de session
          const newChat = {
            id: sessionId,
            name: chatName.trim()
          };

          // Ajouter à la liste des chats
          this.chats.push(newChat);

          // Créer les données de session
          this.chatSessions[sessionId] = {
            sessionId: sessionId,
            messages: [
              {
                text: "Bonjour ! Posez-moi une question ou demandez-moi d'effectuer une transaction.",
                isUser: false,
              },
            ],
            originalName: chatName.trim(),
          };

          // Activer le nouveau chat
          this.activeChat = sessionId;
          this.currentSessionId = sessionId;
          this.showChat = true;
          this.nextChatId++;

          console.log(`✅ Nouveau chat créé: ${newChat.name} (Session: ${sessionId})`);
          console.log("📋 Chats actuels:", this.chats);
          
        } catch (error) {
          console.error("❌ Erreur lors de la création du chat:", error);
          alert("Impossible de créer le chat. Vérifiez votre connexion ou réessayez.");
        }
      }
    },

    // CHARGEMENT DES CHATS DEPUIS L'API - Version simplifiée
    async loadChatsFromApi() {
      try {
        console.log("📂 Chargement des chats depuis l'API...");
        const response = await apiService.listSessions();
        const sessions = response.sessions || [];
        
        console.log(`📡 ${sessions.length} session(s) reçue(s):`, sessions);

        // Réinitialiser
        this.chats = [];
        this.chatSessions = {};

        if (sessions.length > 0) {
          // Traiter chaque session
          for (let i = 0; i < sessions.length; i++) {
            const session = sessions[i];
            const sessionId = session.session_id;
            const chatName = session.session_name || `Chat ${i + 1}`;

            // Ajouter le chat
            this.chats.push({
              id: sessionId,
              name: chatName
            });

            try {
              // Charger les messages de la session
              const sessionDetail = await apiService.getSession(sessionId);
              const messages = sessionDetail.messages || [];

              // Convertir au format frontend
              const frontendMessages = messages.map((msg) => ({
                text: msg.content,
                isUser: msg.role === "user",
                created_at: msg.created_at,
              }));

              // Message de bienvenue si vide
              if (frontendMessages.length === 0) {
                frontendMessages.push({
                  text: "Bonjour ! Posez-moi une question ou demandez-moi d'effectuer une transaction.",
                  isUser: false,
                });
              }

              // Stocker les données de session
              this.chatSessions[sessionId] = {
                sessionId: sessionId,
                messages: frontendMessages,
                originalName: session.session_name,
              };

              console.log(`✅ Session chargée: ${chatName} (${sessionId})`);

            } catch (sessionError) {
              console.error(`❌ Erreur session ${sessionId}:`, sessionError);
              // Session basique en cas d'erreur
              this.chatSessions[sessionId] = {
                sessionId: sessionId,
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

          // Sélectionner le premier chat
          if (this.chats.length > 0) {
            this.activeChat = this.chats[0].id;
            this.currentSessionId = this.chats[0].id;
          }

          this.nextChatId = this.chats.length + 1;
          console.log("✅ Tous les chats chargés:", this.chats);

        } else {
          // Créer une session par défaut
          console.log("📝 Aucune session, création d'une session par défaut");
          await this.createDefaultSession();
        }

      } catch (error) {
        console.error("❌ Erreur lors du chargement:", error);
        await this.createDefaultSession();
      }
    },

    // Créer une session par défaut
    async createDefaultSession() {
      try {
        const now = new Date();
        const sessionName = `Chat ${now.toLocaleDateString("fr-FR")} ${now.toLocaleTimeString("fr-FR", {
          hour: "2-digit",
          minute: "2-digit",
        })}`;

        const sessionData = await apiService.createNewSession(sessionName);
        const sessionId = sessionData.session_id;

        this.chats = [{
          id: sessionId,
          name: sessionName
        }];

        this.chatSessions[sessionId] = {
          sessionId: sessionId,
          messages: [
            {
              text: "Bonjour ! Posez-moi une question ou demandez-moi d'effectuer une transaction.",
              isUser: false,
            },
          ],
          originalName: sessionName,
        };

        this.activeChat = sessionId;
        this.currentSessionId = sessionId;
        this.nextChatId = 2;

        console.log(`✅ Session par défaut créée: ${sessionName} (${sessionId})`);

      } catch (error) {
        console.error("❌ Erreur création session par défaut:", error);
      }
    },

    // SÉLECTION DE CHAT - Version simplifiée
    selectChat(chatId) {
      console.log("🔄 Sélection du chat:", chatId);
      
      // Vérifier que le chat existe
      const chat = this.chats.find(c => c.id === chatId);
      if (!chat) {
        console.error("❌ Chat non trouvé:", chatId);
        return;
      }

      // Vérifier que la session existe
      if (!this.chatSessions[chatId]) {
        console.error("❌ Session non trouvée:", chatId);
        return;
      }

      // Activer le chat
      this.activeChat = chatId;
      this.currentSessionId = chatId;
      this.showChat = true;

      console.log(`✅ Chat sélectionné: ${chat.name} (Session: ${chatId})`);
    },

    // ÉDITION DE CHAT
    startEditingChat(chatId) {
      const chat = this.chats.find(c => c.id === chatId);
      if (chat) {
        this.editingChatId = chatId;
        this.tempChatName = chat.name;
        this.$nextTick(() => {
          const inputElement = document.querySelector('.chat-name-input');
          if (inputElement) {
            inputElement.focus();
            inputElement.select();
          }
        });
      }
    },

    async saveEditingChat() {
      if (this.tempChatName.trim() && this.editingChatId !== null) {
        const chat = this.chats.find(c => c.id === this.editingChatId);
        if (chat) {
          const oldName = chat.name;
          
          try {
            const response = await apiService.renameSession(
              this.editingChatId, 
              this.tempChatName.trim()
            );
            
            if (response && response.status === 'renamed') {
              // Mettre à jour le nom du chat
              chat.name = this.tempChatName.trim();
              
              // Mettre à jour les données de session si elles existent
              if (this.chatSessions[this.editingChatId]) {
                this.chatSessions[this.editingChatId].originalName = this.tempChatName.trim();
              }
              
              console.log(`✅ Chat renommé: ${chat.name}`);
              this.$forceUpdate();
            } else {
              chat.name = oldName;
              alert("Erreur lors du renommage du chat.");
            }
          } catch (error) {
            console.error("❌ Erreur lors du renommage:", error);
            chat.name = oldName;
            alert("Impossible de renommer le chat. Vérifiez votre connexion ou réessayez.");
          }
        }
      }
      this.cancelEditingChat();
    },

    cancelEditingChat() {
      this.editingChatId = null;
      this.tempChatName = "";
    },

    // DUPLICATION DE CHAT
    async duplicateChat() {
      if (this.contextMenuChatId) {
        const originalChat = this.chats.find(c => c.id === this.contextMenuChatId);
        if (originalChat) {
          try {
            console.log("📋 Duplication du chat:", originalChat.name);
            
            const sessionData = await apiService.createNewSession(`${originalChat.name} (copie)`);
            const newSessionId = sessionData.session_id;

            const newChat = {
              id: newSessionId,
              name: `${originalChat.name} (copie)`
            };

            this.chats.push(newChat);
            
            this.chatSessions[newSessionId] = {
              sessionId: newSessionId,
              messages: [
                {
                  text: "Bonjour ! Posez-moi une question ou demandez-moi d'effectuer une transaction.",
                  isUser: false,
                },
              ],
              originalName: `${originalChat.name} (copie)`,
            };

            this.hideContextMenu();
            console.log(`✅ Chat dupliqué: ${newChat.name} (${newSessionId})`);
            
          } catch (error) {
            console.error("❌ Erreur lors de la duplication:", error);
            alert("Impossible de dupliquer le chat.");
          }
        }
      }
    },

    // SUPPRESSION DE CHAT
    async deleteChat(chatId) {
      if (this.chats.length <= 1) {
        alert("Vous devez garder au moins un chat");
        return;
      }
      
      try {
        console.log("🗑️ Suppression du chat:", chatId);
        await apiService.deleteSession(chatId);
        
        // Supprimer de la liste des chats
        const chatIndex = this.chats.findIndex(c => c.id === chatId);
        if (chatIndex !== -1) {
          this.chats.splice(chatIndex, 1);
        }
        
        // Supprimer les données de session
        delete this.chatSessions[chatId];
        
        // Sélectionner un autre chat si nécessaire
        if (this.activeChat === chatId && this.chats.length > 0) {
          this.activeChat = this.chats[0].id;
          this.currentSessionId = this.chats[0].id;
          console.log("✅ Nouveau chat actif:", this.activeChat);
        }
        
      } catch (error) {
        console.error("❌ Erreur lors de la suppression:", error);
        alert("Erreur lors de la suppression du chat.");
      }
    },

    // MENU CONTEXTUEL
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

    deleteChatFromContextMenu() {
      if (this.contextMenuChatId) {
        this.deleteChat(this.contextMenuChatId);
        this.hideContextMenu();
      }
    },

    // AUTRES MÉTHODES
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

    handleSessionChanged(sessionData) {
      console.log("📡 Session changée depuis Chatbot:", sessionData);
    },

    handleNewSessionCreated(sessionData) {
      console.log("📡 Nouvelle session créée depuis le Chatbot:", sessionData);
      this.loadChatsFromApi();
    },
  },

  // WATCHERS POUR DEBUG
  watch: {
    activeChat(newVal, oldVal) {
      console.log("👀 WATCHER activeChat:", { old: oldVal, new: newVal });
    },
    
    chats: {
      handler(newChats) {
        console.log("👀 WATCHER chats:", newChats.map(c => ({ id: c.id, name: c.name })));
      },
      deep: true
    }
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
/* ===== LAYOUT DE BASE ===== */
.app-container {
  display: flex;
  height: 100vh;
  font-family: 'Roboto', sans-serif;
  background: linear-gradient(120deg, rgba(28, 32, 51, 0), rgba(16, 21, 33, 0));
  overflow: hidden;
}

/* ===== SIDEBAR ===== */
.sidebar {
  position: fixed;
  top: 10vh;
  left: 5vh;
  width: 28vh;
  height: 80vh;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  padding: 15px;
  color: #fff;
  display: flex;
  flex-direction: column;
  gap: 20px;
  overflow: hidden;
}

.sidebar-title {
  font-size: 1.6rem;
  font-weight: 600;
  text-align: center;
  color: #f3e8ff;
}

.chat-navigation {
  display: flex;
  flex-direction: column;
  gap: 12px;
  flex: 1;
  overflow: hidden;
}

/* Contrôles de la sidebar */
.chat-controls {
  display: flex;
  gap: 84px;
  flex-shrink: 0;
}

/* Boutons génériques */
.btn-icon,
.btn-full,
.configure-agent-button,
.chat-access-button,
.talk-to-agent-button-disabled {
  padding: 12px 10px;
  background: linear-gradient(120deg, rgba(28, 32, 51, 0), rgba(16, 21, 33, 0));
  border: none;
  color: white;
  border-radius: 10px;
  font-size: 13px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: center;
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-icon:hover,
.btn-full:hover,
.configure-agent-button:hover,
.chat-access-button:hover,
.talk-to-agent-button-disabled:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(125, 82, 204, 0.4);
}

/* Effet de brillance sur les boutons */
.btn-icon::after,
.btn-full::after,
.configure-agent-button::before,
.chat-access-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(120deg, 
    rgba(255, 255, 255, 0.2) 0%, 
    rgba(255, 255, 255, 0.2) 50%, 
    rgba(255, 255, 255, 0) 80%);
  transition: left 0.5s ease;
  z-index: -1;
}

.btn-icon:hover::after,
.btn-full:hover::after,
.configure-agent-button:hover::before,
.chat-access-button:hover::before {
  left: 100%;
}

/* Liste des chats */
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

/* Styles de scrollbar personnalisés */
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
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 10px;
  box-shadow: 0 2px 6px rgba(118, 75, 162, 0.3);
  transition: all 0.3s ease;
  opacity: 0.7;
}

.chat-list-section::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%);
  box-shadow: 0 3px 8px rgba(157, 78, 221, 0.4);
  opacity: 1;
}

.chat-list-section:hover {
  box-shadow: inset 2px 0 0 rgba(118, 75, 162, 0.2);
  transition: box-shadow 0.3s ease;
}

/* Items de chat */
.chat-item {
  position: relative;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.chat-name {
  flex: 1;
  text-align: left;
  padding: 10px 12px;
  border: none;
  background: transparent;
  color: #f3e8ff;
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.chat-name:hover,
.chat-name.active {
  background: rgba(118, 75, 162, 0.1);
}

.chat-name.active {
  background: rgba(118, 75, 162, 0.2);
  font-weight: 600;
}

/* Formulaire d'édition */
.chat-edit-form {
  width: 100%;
  margin: 0;
}

.chat-name-input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #a552cc;
  border-radius: 6px;
  background: #f3e8ff;
  color: #2c1b4d;
  font-size: 0.9rem;
  outline: none;
  transition: all 0.3s ease;
  font-family: inherit;
}

.chat-name-input:focus {
  border-color: #764ba2;
  box-shadow: 0 0 8px rgba(118, 75, 162, 0.3);
  background: #ffffff;
}

/* Bouton de suppression */
.chat-delete {
  opacity: 0;
  transition: opacity 0.3s ease;
  background: #ff4757;
  color: white;
  border: none;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chat-item:hover .chat-delete {
  opacity: 1;
}

.chat-delete:hover {
  background: #ff3742;
  transform: scale(1.1);
}

/* ===== MENU CONTEXTUEL ===== */
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
  from { transform: translateY(-10px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.context-menu-item {
  width: 100%;
  padding: 12px 20px;
  border: none;
  background: none;
  text-align: left;
  cursor: pointer;
  font-size: 13px;
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

/* ===== CONTENU PRINCIPAL ===== */
.main-content {
  flex: 1;
  padding: 50px;
  display: flex;
  flex-direction: column;
  align-items: center;
  background: linear-gradient(135deg, #111421 0%, #111421 100%);
  overflow-y: auto;
}

/* En-tête */
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
  from { opacity: 0; transform: translateX(20px); }
  to { opacity: 1; transform: translateX(0); }
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
  text-shadow: 0 1px 2px rgba(0,0,0,0.05);
}

.logout-button {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 20px;
  background: rgba(28, 32, 51, 0.1);
  backdrop-filter: blur(10px);
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

/* ===== DASHBOARD ===== */
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

/* Widgets */
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
  background: linear-gradient(120deg, rgba(28, 32, 51, 0), rgba(16, 21, 33, 0));
  border: none;
}

.crypto-widget::before,
.news-widget::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle at center, rgba(255,255,255,0.2) 0%, transparent 70%);
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
  text-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

.crypto-symbol,
.news-title {
  font-size: 18px;
  opacity: 0.9;
  text-shadow: 0 1px 2px rgba(0,0,0,0.2);
}

.news-title {
  font-size: 20px;
  text-align: center;
}

/* Section d'actions */
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

/* Boutons d'action */
.configure-agent-button,
.chat-access-button {
  padding: 18px 35px;
  font-size: 20px;
  z-index: 1;
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
  background: rgba(28, 32, 51, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  text-align: center;
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

/* ===== RESPONSIVE ===== */
@media (max-width: 768px) {
  .app-container {
    flex-direction: column;
  }
  
  .sidebar {
    position: relative;
    top: 0;
    left: 0;
    width: 100%;
    height: auto;
    max-height: 50vh;
    margin-bottom: 20px;
    border-radius: 0 0 24px 24px;
  }
  
  .chat-list-section {
    max-height: 30vh;
    padding-right: 6px;
  }
  
  .chat-list-section::-webkit-scrollbar {
    width: 6px;
  }
  
  .chat-controls {
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
  
  .configure-agent-button,
  .chat-access-button {
    padding: 14px 28px;
    font-size: 18px;
  }
}

@media (max-width: 480px) {
  .sidebar {
    max-height: 40vh;
  }
  
  .chat-list-section {
    max-height: 25vh;
    padding-right: 4px;
  }
  
  .chat-list-section::-webkit-scrollbar {
    width: 4px;
  }
  
  .widgets-container {
    flex-direction: column;
    gap: 20px;
    margin-top: 50px;
  }
  
  .configure-agent-button,
  .chat-access-button {
    padding: 12px 24px;
    font-size: 16px;
    width: 100%;
  }
}
</style>