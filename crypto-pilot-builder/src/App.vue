<template>
  <div class="main-layout">
    <Sidebar :chats="chats" :activeChatId="activeChatId" @select-chat="selectChat" @new-chat="addNewChat" />
    <div class="main-content">
      <ChatView :chatId="activeChatId" />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import Sidebar from './components/Sidebar.vue';
import ChatView from './views/ChatView.vue';

const chats = ref([
  { id: 1, name: 'Chat 1' },
]);
const activeChatId = ref(1);

function selectChat(id) {
  activeChatId.value = id;
}
function addNewChat() {
  const newId = chats.value.length ? Math.max(...chats.value.map(c => c.id)) + 1 : 1;
  chats.value.push({ id: newId, name: `Chat ${newId}` });
  activeChatId.value = newId;
}
</script>

<style scoped>
html, body, #app {
  height: 100%;
  margin: 0;
  padding: 0;
}
.main-layout {
  display: flex;
  height: 100vh;
  width: 100vw;
  background: #f5f6fa;
}
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #fff;
  box-shadow: none;
  margin: 0;
  max-width: none;
}
</style>