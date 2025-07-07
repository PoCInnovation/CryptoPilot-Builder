<template>
  <aside class="sidebar">
    <h2>Discussions</h2>
    <ul>
      <li
        v-for="(chat, index) in chats"
        :key="index"
        @click="$emit('select-chat', index)"
        :class="{ active: selectedChat === index }"
      >
        {{ chat }}
      </li>
      <li class="add-chat" @click="$emit('add-chat')">+ Nouveau chat</li>
    </ul>
  </aside>
</template>

<script setup>
defineProps({
  chats: {
    type: Array,
    required: true
  },
  selectedChat: {
    type: Number,
    required: true
  }
})

defineEmits(['select-chat', 'add-chat'])
</script>

<style scoped>
.sidebar {
  width: 250px;
  background-color: #f9f9f9;
  border-right: 1px solid #ddd;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  color: black;
}

.sidebar h2 {
  font-size: 1.2rem;
  margin-bottom: 0.5rem;
}

.sidebar ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.sidebar li {
  padding: 0.75rem;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.3s;
}

.sidebar li:hover,
.sidebar li.active {
  background-color: #e0e0e0;
}

.sidebar .add-chat {
  color: #4caf50;
  font-weight: bold;
}
</style>