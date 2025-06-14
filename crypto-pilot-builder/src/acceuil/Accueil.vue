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
            class="chat-item-container">
            <form
              v-if="editingChatId === chat.id"
              class="chat-edit-form"
              @submit.prevent="saveEditingChat">
              <input
                v-model="tempChatName"
                @keydown="handleEditKeydown"
                @blur="saveEditingChat"
                ref="chatEditInput"
                class="chat-name-input"
                maxlength="50"
                type="text"/>
            </form>
            <button
              v-else
              :class="['chat-item-button', { 'chat-item-button--active': chat.id === activeChat }]"
              @click="selectChat(chat.id)"
              @dblclick="startEditingChat(chat.id)"
              @contextmenu="showChatContextMenu($event, chat.id)"
              :title="'Double-cliquez pour renommer | Clic droit pour plus d\'options'">
              {{ chat.name }}
            </button>
            <button
              class="chat-delete-button"
              @click="deleteChat(chat.id)"
              title="Supprimer ce chat"
              :aria-label="`Supprimer le chat ${chat.name}`">
              ×
            </button>
          </article>
        </section>
      </nav>
    </aside>
    <main class="main-content">
      <header class="main-header">
        <h1 class="welcome-title">Welcome</h1>
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
          <router-link to="/Model" class="agent-navigation-link">
            <button class="talk-to-agent-button">Talk to Agent</button>
          </router-link>
        </section>
      </section>
    </main>
    <aside
      v-if="showContextMenu"
      class="context-menu"
      :style="{ left: contextMenuX + 'px', top: contextMenuY + 'px' }"
      role="menu">
      <button
        @click="renameFromContextMenu"
        class="context-menu-item"
        role="menuitem">
        ✏️ Renommer
      </button>
      <button
        @click="duplicateChat"
        class="context-menu-item"
        role="menuitem">
        📋 Dupliquer
      </button>
      <hr class="context-menu-divider" role="separator">
      <button
        @click="deleteChatFromContextMenu"
        class="context-menu-item context-menu-item--danger"
        role="menuitem">
        🗑️ Supprimer
      </button>
    </aside>
  </div>
</template>

<script>
export default {
  name: 'Accueil',
  data() {
    return {
      activeChat: 1,
      nextChatId: 2,
      editingChatId: null,
      tempChatName: '',
      showContextMenu: false,
      contextMenuX: 0,
      contextMenuY: 0,
      contextMenuChatId: null,
      chats: [
        { id: 1, name: 'Trading Analysis' }
      ]
    }
  },
  methods: {
    selectChat(chatId) {
      this.activeChat = chatId;
      console.log(`Chat sélectionné: ${chatId}`);
    },
    createNewChat() {
      const chatName = prompt('Nom du nouveau chat:', `Chat ${this.nextChatId}`);
      if (chatName && chatName.trim()) {
        const newChat = {
          id: this.nextChatId,
          name: chatName.trim()
        };
        this.chats.push(newChat);
        this.activeChat = this.nextChatId;
        this.nextChatId++;
        console.log(`Nouveau chat créé: ${newChat.name}`);
      }
    },
    startEditingChat(chatId) {
      const chat = this.chats.find(c => c.id === chatId);
      if (chat) {
        this.editingChatId = chatId;
        this.tempChatName = chat.name;
      }
    },
    saveEditingChat() {
      if (this.tempChatName.trim()) {
        const chat = this.chats.find(c => c.id === this.editingChatId);
        if (chat) {
          chat.name = this.tempChatName.trim();
        }
      }
      this.cancelEditingChat();
    },
    cancelEditingChat() {
      this.editingChatId = null;
      this.tempChatName = '';
    },

    showChatContextMenu(event, chatId) {
      event.preventDefault();
      this.contextMenuChatId = chatId;
      this.contextMenuX = event.clientX;
      this.contextMenuY = event.clientY;
      this.showContextMenu = true;
      document.addEventListener('click', this.hideContextMenu);
    },
    hideContextMenu() {
      this.showContextMenu = false;
      this.contextMenuChatId = null;
      document.removeEventListener('click', this.hideContextMenu);
    },
    renameFromContextMenu() {
      if (this.contextMenuChatId) {
        this.startEditingChat(this.contextMenuChatId);
        this.hideContextMenu();
      }
    },
    duplicateChat() {
      if (this.contextMenuChatId) {
        const originalChat = this.chats.find(c => c.id === this.contextMenuChatId);
        if (originalChat) {
          const newChat = {
            id: this.nextChatId,
            name: `${originalChat.name} (copie)`
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
        alert('Vous devez garder au moins un chat');
        return;
      }
      const index = this.chats.findIndex(chat => chat.id === chatId);
      if (index !== -1) {
        this.chats.splice(index, 1);
        if (this.activeChat === chatId) {
          this.activeChat = this.chats[0].id;
        }
      }
    },
    handleEditKeydown(event) {
      if (event.key === 'Enter') {
        this.saveEditingChat();
      } else if (event.key === 'Escape') {
        this.cancelEditingChat();
      }
    }
  }
}
</script>

<style scoped>
.app-container {
  display: flex;
  height: 100vh;
  font-family: 'Arial', sans-serif;
  background-color: #fafafa;
}

.sidebar {
  width: 250px;
  background-color: #2c3e50;
  color: white;
  padding: 20px;
  box-shadow: 2px 0 5px rgba(0,0,0,0.1);
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
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
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
}

.welcome-title {
  font-size: 48px;
  font-weight: bold;
  color: #2c3e50;
  margin: 0;
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
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
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

.agent-navigation-link {
  text-decoration: none;
}

.talk-to-agent-button {
  padding: 15px 30px;
  font-size: 18px;
  font-weight: bold;
  background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
  border: none;
  color: white;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
}

.talk-to-agent-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(76, 175, 80, 0.4);
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
  .welcome-title {
    font-size: 36px;
  }
}</style>