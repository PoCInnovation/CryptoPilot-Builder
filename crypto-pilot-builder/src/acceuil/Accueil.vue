<template>
  <div class="accueil">
    <h1>Bienvenue</h1>
    <p>Ceci est l'écran d'accueil</p>
    <router-link to="/chat">
      <button>Accéder au chatbot</button>
    </router-link>
  </div>
</template>

<script>
export default {
  name: 'Accueil'
}
</script>

<style scoped>
.accueil {
  text-align: center;
  padding-top: 100px;
}

button {
  padding: 10px 20px;
  font-size: 16px;
  background-color: #007bff;
  color: black;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

button:hover {
  background-color: #0056b3;
}
</style>