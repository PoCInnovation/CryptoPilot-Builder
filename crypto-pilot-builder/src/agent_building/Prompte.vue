<template>
  <div class="container">
    <progress-bar :current-step="3" :total-steps="3" />
    <div class="page-content">
      <div class="header-section">
        <h2 class="page-title">Finalisation</h2>
        <p class="page-subtitle">
          Définissez le comportement de votre assistant IA
        </p>
      </div>
      <div class="prompt-section">
        <div class="prompt-header">
          <div class="prompt-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <path
                d="M14 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V8L14 2Z"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
              <polyline
                points="14,2 14,8 20,8"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
              <line
                x1="16"
                y1="13"
                x2="8"
                y2="13"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
              <line
                x1="16"
                y1="17"
                x2="8"
                y2="17"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
              <polyline
                points="10,9 9,9 8,9"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
            </svg>
          </div>
          <div class="prompt-title">
            <h3>Comportement de l'Assistant</h3>
            <p>Décrivez comment votre assistant doit interagir et répondre</p>
          </div>
        </div>
        <div class="textarea-wrapper">
          <textarea
            id="prompt-input"
            v-model="localPrompt"
            class="prompt-textarea"
            placeholder="Exemple : Tu es un assistant spécialisé en développement web. Tu réponds de manière concise et pratique, en fournissant des exemples de code quand c'est pertinent. Tu utilises un ton professionnel mais accessible..."
            @input="updatePrompt"
          ></textarea>
          <div class="textarea-decoration"></div>
        </div>
        <div class="prompt-footer">
          <div class="character-count">
            <span
              :class="{
                warning: characterCount > 1800,
                danger: characterCount > 2000,
              }"
            >
              {{ characterCount }}
            </span>
            <span class="count-separator">/</span>
            <span class="count-max">2000</span>
            <span class="count-label">caractères</span>
          </div>
          <div class="prompt-suggestions">
            <button
              @click="useSuggestion('assistant-general')"
              class="suggestion-btn"
            >
              💼 Assistant Général
            </button>
            <button
              @click="useSuggestion('assistant-technique')"
              class="suggestion-btn"
            >
              🔧 Assistant Technique
            </button>
            <button
              @click="useSuggestion('assistant-creatif')"
              class="suggestion-btn"
            >
              🎨 Assistant Créatif
            </button>
          </div>
        </div>
      </div>
      <div class="summary-section">
        <div class="summary-header">
          <h3>Résumé de Configuration</h3>
          <div class="summary-status" :class="{ complete: isReadyToFinish }">
            <svg
              v-if="isReadyToFinish"
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
            >
              <circle
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                stroke-width="2"
              />
              <path
                d="M9 12L11 14L15 10"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
            </svg>
            <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none">
              <circle
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                stroke-width="2"
              />
              <path
                d="M12 8V12"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
              <path
                d="M12 16H12.01"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
            </svg>
            {{
              isReadyToFinish
                ? "Configuration complète"
                : "Configuration incomplète"
            }}
          </div>
        </div>
        <div class="config-grid">
          <div class="config-card">
            <div class="config-icon">🤖</div>
            <div class="config-content">
              <h4>Modèle IA</h4>
              <p>{{ selectedModel || "Non défini" }}</p>
            </div>
            <div class="config-status" :class="{ valid: selectedModel }">
              <svg
                v-if="selectedModel"
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
              >
                <path
                  d="M20 6L9 17L4 12"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                />
              </svg>
              <svg
                v-else
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
              >
                <line
                  x1="18"
                  y1="6"
                  x2="6"
                  y2="18"
                  stroke="currentColor"
                  stroke-width="2"
                />
                <line
                  x1="6"
                  y1="6"
                  x2="18"
                  y2="18"
                  stroke="currentColor"
                  stroke-width="2"
                />
              </svg>
            </div>
          </div>
          <div class="config-card">
            <div class="config-icon">🔐</div>
            <div class="config-content">
              <h4>Clé API</h4>
              <p>
                {{ apiKey ? "●●●●●●●●" + apiKey.slice(-4) : "Non définie" }}
              </p>
            </div>
            <div class="config-status" :class="{ valid: apiKey }">
              <svg
                v-if="apiKey"
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
              >
                <path
                  d="M20 6L9 17L4 12"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                />
              </svg>
              <svg
                v-else
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
              >
                <line
                  x1="18"
                  y1="6"
                  x2="6"
                  y2="18"
                  stroke="currentColor"
                  stroke-width="2"
                />
                <line
                  x1="6"
                  y1="6"
                  x2="18"
                  y2="18"
                  stroke="currentColor"
                  stroke-width="2"
                />
              </svg>
            </div>
          </div>
          <div class="config-card">
            <div class="config-icon">💬</div>
            <div class="config-content">
              <h4>Comportement</h4>
              <p>
                {{
                  localPrompt
                    ? "Défini (" + localPrompt.length + " caractères)"
                    : "Non défini"
                }}
              </p>
            </div>
            <div class="config-status" :class="{ valid: localPrompt }">
              <svg
                v-if="localPrompt"
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
              >
                <path
                  d="M20 6L9 17L4 12"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                />
              </svg>
              <svg
                v-else
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
              >
                <line
                  x1="18"
                  y1="6"
                  x2="6"
                  y2="18"
                  stroke="currentColor"
                  stroke-width="2"
                />
                <line
                  x1="6"
                  y1="6"
                  x2="18"
                  y2="18"
                  stroke="currentColor"
                  stroke-width="2"
                />
              </svg>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="button-container">
      <router-link to="/Module" class="btn-link">
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
      <router-link to="/chat" class="btn-link">
        <button
          class="btn btn-primary"
          :disabled="!isFormValid"
          @click="saveConfig"
        >
          Go to chatbot
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
import { mapGetters, mapActions } from "vuex";
import ProgressBar from "./Progress_bar.vue";

export default {
  name: "Prompte",
  components: {
    ProgressBar,
  },
  data() {
    return {
      localPrompt: "",
      suggestions: {
        "assistant-general":
          "Tu es un assistant IA polyvalent et bienveillant. Tu réponds de manière claire, précise et utile à toutes les questions. Tu adoptes un ton professionnel mais chaleureux, et tu t'adaptes au niveau de connaissance de l'utilisateur. Tu fournis des exemples concrets quand c'est pertinent.",
        "assistant-technique":
          "Tu es un assistant technique spécialisé en développement et technologies. Tu réponds avec précision en fournissant du code, des solutions pratiques et des explications détaillées. Tu utilises un langage technique approprié et proposes toujours des alternatives quand c'est possible.",
        "assistant-creatif":
          "Tu es un assistant créatif spécialisé dans la génération de contenu artistique et innovant. Tu adoptes un ton inspirant et imaginatif, tu proposes des idées originales et tu encourages la créativité. Tu sais adapter ton style selon le type de création demandé.",
      },
    };
  },
  computed: {
    ...mapGetters(["aiConfig", "isAuthenticated"]),
    selectedModel() {
      return this.aiConfig.selectedModel;
    },
    apiKey() {
      return this.aiConfig.apiKey;
    },
    characterCount() {
      return this.localPrompt.length;
    },
    isFormValid() {
      return this.localPrompt.trim().length > 0;
    },
    isReadyToFinish() {
      return this.selectedModel && this.apiKey && this.localPrompt;
    },
  },
  mounted() {
    this.localPrompt = this.aiConfig.prompt || "";
  },
  methods: {
    ...mapActions(["setPrompt", "saveCompleteConfig"]),
    updatePrompt() {
      if (this.localPrompt.length > 2000) {
        this.localPrompt = this.localPrompt.substring(0, 2000);
      }
      this.setPrompt(this.localPrompt);
    },
    useSuggestion(type) {
      this.localPrompt = this.suggestions[type];
      this.setPrompt(this.localPrompt);
    },
    async saveConfig() {
      if (!this.isFormValid) {
        return;
      }

      try {
        // Préparer la configuration complète
        const completeConfig = {
          selectedModel: this.aiConfig.selectedModel,
          apiKey: this.aiConfig.apiKey,
          prompt: this.localPrompt,
          modules: this.aiConfig.modules || {},
          name: "Mon Assistant CryptoPilot",
          description: "Assistant IA configuré pour les cryptomonnaies",
        };

        // Sauvegarder la configuration complète
        await this.saveCompleteConfig(completeConfig);

        console.log("Configuration complète sauvegardée avec succès!");

        // Optionnel: Afficher un message de succès ou rediriger
        this.$emit("config-completed");
      } catch (error) {
        console.error("Erreur lors de la sauvegarde finale:", error);
        // Afficher un message d'erreur à l'utilisateur
        alert(
          "Erreur lors de la sauvegarde de la configuration. Veuillez réessayer."
        );
      }
    },
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
  overflow-x: hidden;
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
  background: linear-gradient(135deg, #f3e8ff 0%, #e9d5ff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
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

.prompt-section,
.summary-section {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  padding: 25px;
  border-radius: 20px;
  text-align: center;
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  color: #f3e8ff;
}

.prompt-section::before,
.summary-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(120deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.1) 50%, rgba(255,255,255,0) 80%);
  transition: left 0.5s ease;
}

.prompt-section:hover::before,
.summary-section:hover::before {
  left: 100%;
}

.prompt-icon,
.config-icon {
  display: inline-flex;
  padding: 15px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 15px;
  color: white;
  margin-bottom: 15px;
  transition: transform 0.3s ease;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.prompt-title h3 {
  font-size: 1.3rem;
  font-weight: 700;
  color: #f3e8ff;
  margin: 0 0 10px 0;
  text-shadow: 0 1px 2px rgba(0,0,0,0.2);
}

.prompt-textarea {
  width: 100%;
  min-height: 200px;
  padding: 20px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  font-family: 'Roboto', sans-serif;
  font-size: 15px;
  line-height: 1.6;
  resize: vertical;
  box-sizing: border-box;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  color: white;
  position: relative;
  z-index: 1;
}

.prompt-textarea::placeholder {
  color: #f3e8ff;
}

.prompt-textarea:focus {
  outline: none;
  border-color: rgba(255, 255, 255, 0.3);
  background: rgba(255, 255, 255, 0.2);
  box-shadow: 0 0 8px rgba(118, 75, 162, 0.3);
  transform: translateY(-2px);
}

.textarea-decoration {
  position: absolute;
  top: -1px;
  left: -1px;
  right: -1px;
  bottom: -1px;
  border-radius: 16px;
  background: linear-gradient(120deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.1) 50%, rgba(255,255,255,0) 80%);
  opacity: 0;
  transition: opacity 0.3s ease;
  pointer-events: none;
  z-index: 0;
}

.prompt-textarea:focus + .textarea-decoration {
  opacity: 1;
}

.character-count {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
  font-weight: 500;
}

.character-count .warning {
  color: #f59e0b;
}
.character-count .danger {
  color: #ef4444;
  font-weight: 700;
}

.suggestion-btn {
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  color: #f3e8ff;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  z-index: 1;
  backdrop-filter: blur(10px);
}

.suggestion-btn::before {
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

.suggestion-btn:hover::before {
  left: 100%;
}

.suggestion-btn:hover {
  transform: translateY(-2px);
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.3);
}

.summary-status {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  background: rgba(118, 75, 162, 0.2);
  color: #e9d5ff;
  border: 1px solid rgba(118, 75, 162, 0.3);
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.summary-status.complete {
  background: rgba(22, 163, 74, 0.2);
  color: #86efac;
  border-color: rgba(22, 163, 74, 0.3);
}

.config-card {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.config-card:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
}

.config-icon {
  font-size: 24px;
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  color: white;
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.config-content h4 {
  font-size: 1rem;
  font-weight: 600;
  color: #f3e8ff;
  margin: 0 0 4px 0;
  text-shadow: 0 1px 2px rgba(0,0,0,0.2);
}

.config-content p {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
  margin: 0;
  word-break: break-word;
}

.config-status {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
  flex-shrink: 0;
  transition: all 0.3s ease;
  box-shadow: 0 2px 6px rgba(0,0,0,0.2);
}

.config-status.valid {
  background: rgba(22, 163, 74, 0.2);
  color: #16a34a;
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

  .prompt-section,
  .summary-section {
    padding: 20px;
  }

  .button-container {
    flex-direction: column;
    gap: 15px;
    padding: 0 15px;
  }

  .module-selection {
    padding: 25px 20px;
  }
}

@media (max-width: 480px) {
  .page-title {
    font-size: 1.8rem;
  }

  .page-subtitle {
    font-size: 1rem;
  }

  .prompt-textarea {
    min-height: 150px;
  }
}
</style>