<template>
  <div class="flex-container">
    <div>Bloc 1</div>
    <div class="ligne"></div>
    <div>Bloc 2</div>
    <router-link to="/chat">
      <button>Accéder au Chatbot</button>
    </router-link>
  </div>
</template>

<script>
export default {
  name: 'Model'
}
</script>

<style>
.flex-container {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

button {
  margin-top: 20px;
  padding: 10px 20px;
  font-size: 16px;
  background-color: #28a745;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.ligne {
  height: 1px;
  background-color: gray;
  width: 100%;
}
</style>
