<template>
  <div class="container">
    <progress-bar :current-step="3" :total-steps="3" />
    <div class="page-content">
      <h2>Étape finale - Prompt</h2>
      <div>Configuration of the prompt system</div>
      <div class="ligne"></div>
      <div class="prompt-section">
        <label for="prompt-input" class="prompt-label">
          Define the behavior of your AI assistant :
        </label>
        <textarea
          id="prompt-input"
          v-model="localPrompt"
          class="prompt-textarea"
          placeholder="Exemple : Tu es un assistant spécialisé en crypto. Tu réponds de manière concise et pratique, en fournissant des exemples quand c'est pertinent..."
          @input="updatePrompt"
        ></textarea>
        <div class="prompt-info">
          <small>{{ characterCount }}/2000 caractères</small>
        </div>
      </div>
      <div class="validation-section">
        <h3>Summary of your configuration :</h3>
        <div class="config-summary">
          <div class="config-item">
            <strong>Choosen Model :</strong> {{ selectedModel || 'Non défini' }}
          </div>
          <div class="config-item">
            <strong>API key :</strong> {{ apiKey ? '●●●●●●●●' + apiKey.slice(-4) : 'Non définie' }}
          </div>
          <div class="config-item">
            <strong>Assistant behavior :</strong> {{ localPrompt ? 'Défini (' + localPrompt.length + ' caractères)' : 'Non défini' }}
          </div>
        </div>
      </div>
    </div>
    <div class="button-container">
      <router-link to="/Module">
        <button class="btn-prev">Previous</button>
      </router-link>
      <router-link to="/chat">
        <button class="btn-finish" :disabled="!isReadyToFinish">Go to Chatbot</button>
      </router-link>
    </div>
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'
import ProgressBar from './Progress_bar.vue'

export default {
  name: 'Prompte',
  components: {
    ProgressBar
  },
  data() {
    return {
      localPrompt: ''
    }
  },
  computed: {
    ...mapGetters(['getPrompt', 'getSelectedModel', 'getApiKey', 'isConfigured']),
    selectedModel() {
      return this.getSelectedModel
    },
    apiKey() {
      return this.getApiKey
    },
    characterCount() {
      return this.localPrompt.length
    },
    isReadyToFinish() {
      return this.isConfigured
    }
  },
  mounted() {
    this.localPrompt = this.getPrompt || ''
  },
  methods: {
    ...mapActions(['setPrompt']),
    updatePrompt() {
      if (this.localPrompt.length > 2000) {
        this.localPrompt = this.localPrompt.substring(0, 2000)
      }
      this.setPrompt(this.localPrompt)
    }
  }
}
</script>

<style scoped>
.container {
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
}

.page-content {
  min-height: 400px;
  padding: 30px;
  background-color: #f9f9f9;
  border-radius: 8px;
  margin: 20px 0;
  border-left: 4px solid #333;
}

.page-content h2 {
  margin-top: 0;
  color: #333;
  font-size: 24px;
}

.ligne {
  height: 1px;
  background-color: gray;
  width: 100%;
  margin: 15px 0;
}

.prompt-section {
  margin: 25px 0;
}

.prompt-label {
  display: block;
  font-weight: 600;
  font-size: 16px;
  color: #333;
  margin-bottom: 10px;
}

.prompt-textarea {
  width: 100%;
  min-height: 200px;
  padding: 15px;
  border: 2px solid #ddd;
  border-radius: 8px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  font-size: 14px;
  line-height: 1.5;
  resize: vertical;
  box-sizing: border-box;
  transition: border-color 0.3s ease;
  background-color: white;
}

.prompt-textarea:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
}

.prompt-textarea::placeholder {
  color: #888;
  font-style: italic;
}

.prompt-info {
  text-align: right;
  margin-top: 8px;
  color: #666;
}

.validation-section {
  margin-top: 30px;
  padding: 20px;
  background-color: #fff;
  border-radius: 6px;
  border: 1px solid #e0e0e0;
}

.validation-section h3 {
  margin-top: 0;
  color: #333;
  font-size: 18px;
}

.config-summary {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.config-item {
  padding: 10px;
  background-color: #f8f9fa;
  border-radius: 4px;
  border-left: 3px solid #007bff;
}

.config-item strong {
  color: #495057;
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
  transition: all 0.3s ease;
  font-weight: 600;
}

.btn-prev {
  background-color: #28a745;
  color: white;
}

.btn-prev:hover {
  background-color: #218838;
  transform: translateY(-1px);
}

.btn-finish {
  background-color: #28a745;
  color: white;
}

.btn-finish:hover:not(:disabled) {
  background-color: #218838;
  transform: translateY(-1px);
}

.btn-finish:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
  transform: none;
}

@media (max-width: 768px) {
  .container {
    padding: 15px;
  }
  .page-content {
    padding: 20px;
  }
  .prompt-textarea {
    min-height: 150px;
  }
  .button-container {
    flex-direction: column;
    gap: 15px;
  }
  button {
    width: 100%;
  }
}
</style>