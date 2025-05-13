<template>
  <aside class="sidebar">
    <div class="logo">CryptoPilot</div>
    <nav>
      <ul>
        <li v-for="chat in chats" :key="chat.id" :class="{active: chat.id === activeChatId}" @click="$emit('select-chat', chat.id)">
          <span class="avatar">💬</span>
          {{ chat.name }}
        </li>
      </ul>
      <button class="new-chat" @click="$emit('new-chat')">+ Nouveau Chat</button>
    </nav>
  </aside>
</template>

<script setup>
const props = defineProps({
  chats: Array,
  activeChatId: Number
});
</script>

<style scoped>
.sidebar {
  background: #232b4a;
  color: #fff;
  width: 260px;
  min-height: 100vh;
  box-shadow: 2px 0 12px #0002;
  display: flex;
  flex-direction: column;
  padding: 2rem 1rem;
}
.logo {
  font-size: 2rem;
  font-weight: bold;
  margin-bottom: 2rem;
  letter-spacing: 2px;
}
ul {
  list-style: none;
  padding: 0;
  margin: 0;
}
li {
  display: flex;
  align-items: center;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  margin-bottom: 0.5rem;
  cursor: pointer;
  transition: background 0.2s;
}
li.active, li:hover {
  background: #3a1c71;
}
.avatar {
  margin-right: 0.75rem;
  font-size: 1.2rem;
}
.new-chat {
  margin-top: 2rem;
  background: #3a1c71;
  color: #fff;
  border: none;
  border-radius: 8px;
  padding: 0.75rem 1.5rem;
  cursor: pointer;
  transition: background 0.2s;
  font-weight: bold;
  font-size: 1rem;
}
.new-chat:hover {
  background: #5e3be1;
}
</style> 