<template>
  <div class="container">
    <progress-bar :current-step="1" :total-steps="3" />
    <div class="page-content">
      <h2>First - AI Configuration</h2>
      <div class="form-group">
        <label for="model-select">AI Model :</label>
        <select id="model-select" v-model="selectedModel" class="form-select">
          <option value="">Choose a Model</option>
          <option value="gpt-4o-mini">GPT-4o Mini</option>
        </select>
      </div>
      <div class="ligne"></div>
      <div class="form-group">
        <label for="api-key">API key :</label>
        <input
          id="api-key"
          type="password"
          v-model="apiKey"
          placeholder="Entrez votre clé API"
          class="form-input"
        />
      </div>
      <div v-if="isConfigured" class="success-message">
        ✅ Configuration sauvegardée avec succès !
      </div>
    </div>
    <div class="button-container">
      <router-link to="/">
        <button class="btn-prev">Previous</button>
      </router-link>
      <router-link to="/Module">
        <button class="btn-next" :disabled="!isFormValid" @click="saveConfig">Next</button>
      </router-link>
    </div>
  </div>
</template>

<script>
import ProgressBar from './Progress_bar.vue'
import { mapGetters, mapActions } from 'vuex'

export default {
  name: 'AI',
  components: {
    ProgressBar
  },
  data() {
    return {
      selectedModel: '',
      apiKey: ''
    }
  },
  computed: {
    ...mapGetters(['getApiKey', 'getSelectedModel', 'isConfigured']),
    isFormValid() {
      return this.selectedModel && this.apiKey.trim()
    }
  },
  methods: {
    ...mapActions(['updateAIConfig', 'setApiKey', 'setModel']),
    saveConfig() {
      this.updateAIConfig({
        selectedModel: this.selectedModel,
        apiKey: this.apiKey
      })
    }
  },
  watch: {
    selectedModel(newVal) {
      if (newVal) {
        this.setModel(newVal)
      }
    },
    apiKey(newVal) {
      if (newVal) {
        this.setApiKey(newVal)
      }
    }
  },
  mounted() {
    this.selectedModel = this.getSelectedModel
    this.apiKey = this.getApiKey
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

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
  color: #333;
}

.form-select,
.form-input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
  background-color: white;
}

.form-select:focus,
.form-input:focus {
  outline: none;
  border-color: #333;
  box-shadow: 0 0 5px rgba(51, 51, 51, 0.3);
}

.ligne {
  height: 1px;
  background-color: gray;
  width: 100%;
  margin: 20px 0;
}

.success-message {
  background-color: #d4edda;
  color: #155724;
  padding: 10px;
  border-radius: 4px;
  margin-top: 15px;
  border: 1px solid #c3e6cb;
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
  background-color: #28a745;
  color: white;
}

.btn-prev:hover:not(:disabled) {
  background-color: #218838;
}

.btn-next {
  background-color: #28a745;
  color: white;
}

.btn-next:hover:not(:disabled) {
  background-color: #218838;
}

button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>