<template>
  <div class="container">
    <progress-bar :current-step="1" :total-steps="3" />
    <div class="page-content">
      <h2>Première étape - Configuration IA</h2>
      <div>Bloc 1</div>
      <div class="ligne"></div>
      <div>Bloc 2</div>
      <p>Remplissez les informations nécessaires pour continuer.</p>
    </div>
    <div class="button-container">
      <router-link to="/">
        <button class="btn-prev">Précédent</button>
      </router-link>
      <router-link to="/Module">
        <button class="btn-next">Suivant</button>
      </router-link>
    </div>
  </div>
</template>

<script>
import ProgressBar from './Progress_bar.vue'

export default {
  name: 'AI',
  components: {
    ProgressBar
  }
}
</script>

<style scoped>
.container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.page-content {
  min-height: 200px;
  padding: 20px;
  background-color: #f9f9f9;
  border-radius: 8px;
  margin: 20px 0;
  border-left: 4px solid #333;
}

.page-content h2 {
  margin-top: 0;
  color: #333;
}

.ligne {
  height: 1px;
  background-color: gray;
  width: 100%;
  margin: 10px 0;
}

.button-container {
  display: flex;
  justify-content: space-between;
  margin-top: 30px;
}

button {
  padding: 12px 24px;
  border: none;
  border-radius: 5px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.btn-prev {
  background-color: #6c757d;
  color: white;
}

.btn-prev:hover:not(:disabled) {
  background-color: #545b62;
}

.btn-next {
  background-color: #333;
  color: white;
}

.btn-next:hover {
  background-color: #555;
}

button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>