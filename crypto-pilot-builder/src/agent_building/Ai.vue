<template>
  <div class="container">
    <progress-bar :current-step="1" :total-steps="3" />
    <div class="page-content">
      <div class="header-section">
        <h2 class="page-title">Configuration IA</h2>
        <p class="page-subtitle">
          Configurez votre assistant intelligent en quelques étapes
        </p>
      </div>
      <div class="form-section">
        <div class="form-group">
          <label for="model-select" class="form-label">
            <i class="icon">🤖</i>
            Modèle d'IA
          </label>
          <div class="select-wrapper">
            <select
              id="model-select"
              v-model="selectedModel"
              class="form-select"
            >
              <option value="">Choisir un modèle</option>
              <option value="gpt-4o-mini">GPT-4o Mini</option>
            </select>
            <div class="select-arrow">
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path
                  d="M5 7.5L10 12.5L15 7.5"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                />
              </svg>
            </div>
          </div>
        </div>
        <div class="form-group">
          <label for="api-key" class="form-label">
            <i class="icon">🔐</i>
            Clé API
          </label>
          <div class="input-wrapper">
            <input
              id="api-key"
              type="password"
              v-model="apiKey"
              placeholder="Entrez votre clé API"
              class="form-input"
            />
            <div class="input-icon">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
                <path
                  d="M6 10V8C6 5.79086 7.79086 4 10 4H14C16.2091 4 18 5.79086 18 8V10"
                  stroke="currentColor"
                  stroke-width="2"
                />
                <rect
                  x="4"
                  y="10"
                  width="16"
                  height="10"
                  rx="2"
                  stroke="currentColor"
                  stroke-width="2"
                />
              </svg>
            </div>
          </div>
        </div>
        <div v-if="isConfigured" class="success-message">
          <div class="success-icon">✨</div>
          <div class="success-text">
            <strong>Configuration sauvegardée !</strong>
            <p>Votre assistant IA est prêt à être configuré</p>
          </div>
        </div>
      </div>
    </div>
    <div class="button-container">
      <router-link to="/" class="btn-link">
        <button class="btn btn-secondary">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
            <path
              d="M19 12H5M12 19L5 12L12 5"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
          </svg>
          Précédent
        </button>
      </router-link>
      <router-link to="/Module" class="btn-link">
        <button
          class="btn btn-primary"
          :disabled="!isFormValid"
          @click="saveConfig"
        >
          Suivant
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
            <path
              d="M5 12H19M12 5L19 12L12 19"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
          </svg>
        </button>
      </router-link>
    </div>
  </div>
</template>

<script>
import ProgressBar from "./Progress_bar.vue";
import { mapGetters, mapActions } from "vuex";

export default {
  name: "AI",
  components: {
    ProgressBar,
  },
  data() {
    return {
      selectedModel: "",
      apiKey: "",
    };
  },
  computed: {
    ...mapGetters(["aiConfig", "isAuthenticated"]),
    isFormValid() {
      return this.selectedModel && this.apiKey.trim();
    },
    isConfigured() {
      return this.selectedModel && this.apiKey;
    },
  },
  methods: {
    ...mapActions(["updateAIConfig", "setApiKey", "setModel"]),
    saveConfig() {
      this.updateAIConfig({
        selectedModel: this.selectedModel,
        apiKey: this.apiKey,
      });
    },
  },
  watch: {
    selectedModel(newVal) {
      if (newVal) {
        this.setModel(newVal);
      }
    },
    apiKey(newVal) {
      if (newVal) {
        this.setApiKey(newVal);
      }
    },
  },
  mounted() {
    this.selectedModel = this.aiConfig.selectedModel || "";
    this.apiKey = this.aiConfig.apiKey || "";
  },
};
</script>

<style scoped>
.container {
  width: 100vw;
  height: 100vh;
  margin: 0;
  padding: 20px;
  box-sizing: border-box;
  background: linear-gradient(135deg, #111421 0%, #111421 100%);
  display: flex;
  flex-direction: column;
  position: fixed;
  top: 0;
  left: 0;
  overflow-y: auto;
  font-family: 'Roboto', sans-serif;
}

.page-content {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-radius: 24px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  padding: 40px;
  margin: 30px auto;
  max-width: 900px;
  width: 100%;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
  animation: slideUp 0.6s ease-out;
  box-sizing: border-box;
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.page-content::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle at center, rgba(255,255,255,0.1) 0%, transparent 70%);
  transform: rotate(45deg);
  pointer-events: none;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.header-section {
  text-align: center;
  margin-bottom: 40px;
  animation: fadeIn 0.5s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

.page-title {
  font-size: 2.5rem;
  font-weight: 800;
  color: #f3e8ff;
  margin: 0 0 10px 0;
  letter-spacing: -0.02em;
  text-shadow: 0 2px 4px rgba(0,0,0,0.3);
}

.page-subtitle {
  color: rgba(255, 255, 255, 0.8);
  font-size: 1.1rem;
  margin: 0;
  font-weight: 500;
  text-shadow: 0 1px 2px rgba(0,0,0,0.2);
}

.form-section {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.form-group {
  display: flex;
  flex-direction: column;
  animation: fadeInUp 0.6s ease;
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.form-label {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 600;
  font-size: 1rem;
  color: #f3e8ff;
  margin-bottom: 12px;
  letter-spacing: -0.01em;
  text-shadow: 0 1px 2px rgba(0,0,0,0.2);
}

.icon {
  font-size: 1.2rem;
}

.select-wrapper {
  position: relative;
}

.form-select {
  width: 100%;
  padding: 16px 50px 16px 20px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  font-size: 16px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  color: #f3e8ff;
  appearance: none;
  transition: all 0.3s ease;
  font-weight: 500;
  box-sizing: border-box;
  position: relative;
  overflow: hidden;
}

.form-select::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(120deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.1) 50%, rgba(255,255,255,0) 80%);
  transition: left 0.5s ease;
}

.form-select:hover::before {
  left: 100%;
}

.form-select:focus {
  outline: none;
  border-color: rgba(255, 255, 255, 0.3);
  background: rgba(255, 255, 255, 0.2);
  box-shadow: 0 0 8px rgba(118, 75, 162, 0.3);
  transform: translateY(-2px);
}

.form-select option {
  background: #2e1b4d;
  color: #f3e8ff;
}

.select-arrow {
  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
  color: rgba(255, 255, 255, 0.7);
  pointer-events: none;
  transition: transform 0.3s ease;
}

.form-select:focus + .select-arrow {
  transform: translateY(-50%) rotate(180deg);
}

.input-wrapper {
  position: relative;
}

.form-input {
  width: 100%;
  padding: 16px 50px 16px 20px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  font-size: 16px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  color: #f3e8ff;
  transition: all 0.3s ease;
  font-weight: 500;
  box-sizing: border-box;
  position: relative;
  overflow: hidden;
}

.form-input::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(120deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.1) 50%, rgba(255,255,255,0) 80%);
  transition: left 0.5s ease;
}

.form-input:hover::before {
  left: 100%;
}

.form-input:focus {
  outline: none;
  border-color: rgba(255, 255, 255, 0.3);
  background: rgba(255, 255, 255, 0.2);
  box-shadow: 0 0 8px rgba(118, 75, 162, 0.3);
  transform: translateY(-2px);
}

.form-input::placeholder {
  color: rgba(255, 255, 255, 0.5);
  font-weight: 400;
}

.input-icon {
  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
  color: rgba(255, 255, 255, 0.7);
  pointer-events: none;
}

.success-message {
  display: flex;
  align-items: center;
  gap: 16px;
  background: rgba(16, 185, 129, 0.2);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(16, 185, 129, 0.3);
  color: #10b981;
  padding: 20px;
  border-radius: 16px;
  animation: bounceIn 0.6s ease-out;
  position: relative;
  overflow: hidden;
}

.success-message::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle at center, rgba(16,185,129,0.1) 0%, transparent 70%);
  transform: rotate(45deg);
  pointer-events: none;
}

@keyframes bounceIn {
  0% {
    opacity: 0;
    transform: scale(0.8);
  }
  60% {
    opacity: 1;
    transform: scale(1.05);
  }
  100% {
    transform: scale(1);
  }
}

.success-icon {
  font-size: 2rem;
  position: relative;
  z-index: 1;
}

.success-text {
  position: relative;
  z-index: 1;
}

.success-text strong {
  display: block;
  font-size: 1.1rem;
  margin-bottom: 4px;
  color: #f3e8ff;
}

.success-text p {
  margin: 0;
  opacity: 0.9;
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.8);
}

.button-container {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  margin-top: 40px;
  max-width: 900px;
  width: 100%;
  margin-left: auto;
  margin-right: auto;
  padding: 0 20px;
  box-sizing: border-box;
}

.btn-link {
  text-decoration: none;
  flex: 1;
}

.btn {
  width: 100%;
  padding: 16px 32px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  letter-spacing: -0.01em;
  box-sizing: border-box;
  position: relative;
  overflow: hidden;
}

.btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(120deg, rgba(255,255,255,0.2) 0%, rgba(255,255,255,0.2) 50%, rgba(255,255,255,0) 80%);
  transition: left 0.5s ease;
  z-index: -1;
}

.btn:hover::before {
  left: 100%;
}

.btn-primary {
  background: rgba(118, 75, 162, 0.3);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  color: white;
  box-shadow: 0 6px 18px rgba(118, 75, 162, 0.3);
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(118, 75, 162, 0.4);
  background: rgba(118, 75, 162, 0.4);
}

.btn-primary:disabled {
  background: rgba(148, 163, 184, 0.2);
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
  color: rgba(255, 255, 255, 0.5);
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  color: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.btn-secondary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.3);
}

@media (max-width: 768px) {
  .container {
    padding: 15px;
  }

  .page-content {
    padding: 30px 20px;
    margin: 20px auto;
  }

  .page-title {
    font-size: 2rem;
  }

  .button-container {
    flex-direction: column;
    gap: 15px;
    padding: 0 15px;
  }

  .btn-link {
    flex: none;
  }
}
</style>