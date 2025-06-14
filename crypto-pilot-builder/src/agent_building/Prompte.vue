<template>
  <div class="container">
    <progress-bar :current-step="3" :total-steps="3" />
    <div class="page-content">
      <div class="header-section">
        <h2 class="page-title">Finalisation</h2>
        <p class="page-subtitle">Définissez le comportement de votre assistant IA</p>
      </div>
      <div class="prompt-section">
        <div class="prompt-header">
          <div class="prompt-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <path d="M14 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V8L14 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <polyline points="14,2 14,8 20,8" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <line x1="16" y1="13" x2="8" y2="13" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <line x1="16" y1="17" x2="8" y2="17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <polyline points="10,9 9,9 8,9" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
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
            <span :class="{ 'warning': characterCount > 1800, 'danger': characterCount > 2000 }">
              {{ characterCount }}
            </span>
            <span class="count-separator">/</span>
            <span class="count-max">2000</span>
            <span class="count-label">caractères</span>
          </div>
          <div class="prompt-suggestions">
            <button @click="useSuggestion('assistant-general')" class="suggestion-btn">
              💼 Assistant Général
            </button>
            <button @click="useSuggestion('assistant-technique')" class="suggestion-btn">
              🔧 Assistant Technique
            </button>
            <button @click="useSuggestion('assistant-creatif')" class="suggestion-btn">
              🎨 Assistant Créatif
            </button>
          </div>
        </div>
      </div>
      <div class="summary-section">
        <div class="summary-header">
          <h3>Résumé de Configuration</h3>
          <div class="summary-status" :class="{ 'complete': isReadyToFinish }">
            <svg v-if="isReadyToFinish" width="20" height="20" viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
              <path d="M9 12L11 14L15 10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
              <path d="M12 8V12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M12 16H12.01" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            {{ isReadyToFinish ? 'Configuration complète' : 'Configuration incomplète' }}
          </div>
        </div>
        <div class="config-grid">
          <div class="config-card">
            <div class="config-icon">🤖</div>
            <div class="config-content">
              <h4>Modèle IA</h4>
              <p>{{ selectedModel || 'Non défini' }}</p>
            </div>
            <div class="config-status" :class="{ 'valid': selectedModel }">
              <svg v-if="selectedModel" width="16" height="16" viewBox="0 0 24 24" fill="none">
                <path d="M20 6L9 17L4 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none">
                <line x1="18" y1="6" x2="6" y2="18" stroke="currentColor" stroke-width="2"/>
                <line x1="6" y1="6" x2="18" y2="18" stroke="currentColor" stroke-width="2"/>
              </svg>
            </div>
          </div>
          <div class="config-card">
            <div class="config-icon">🔐</div>
            <div class="config-content">
              <h4>Clé API</h4>
              <p>{{ apiKey ? '●●●●●●●●' + apiKey.slice(-4) : 'Non définie' }}</p>
            </div>
            <div class="config-status" :class="{ 'valid': apiKey }">
              <svg v-if="apiKey" width="16" height="16" viewBox="0 0 24 24" fill="none">
                <path d="M20 6L9 17L4 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none">
                <line x1="18" y1="6" x2="6" y2="18" stroke="currentColor" stroke-width="2"/>
                <line x1="6" y1="6" x2="18" y2="18" stroke="currentColor" stroke-width="2"/>
              </svg>
            </div>
          </div>
          <div class="config-card">
            <div class="config-icon">💬</div>
            <div class="config-content">
              <h4>Comportement</h4>
              <p>{{ localPrompt ? 'Défini (' + localPrompt.length + ' caractères)' : 'Non défini' }}</p>
            </div>
            <div class="config-status" :class="{ 'valid': localPrompt }">
              <svg v-if="localPrompt" width="16" height="16" viewBox="0 0 24 24" fill="none">
                <path d="M20 6L9 17L4 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none">
                <line x1="18" y1="6" x2="6" y2="18" stroke="currentColor" stroke-width="2"/>
                <line x1="6" y1="6" x2="18" y2="18" stroke="currentColor" stroke-width="2"/>
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
            <path d="M19 12H5M12 19L5 12L12 5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          Précédent
        </button>
      </router-link>
      <router-link to="/chat" class="btn-link">
        <button class="btn btn-primary" :disabled="!isFormValid" @click="saveConfig">
          Go to chatbot
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
            <path d="M5 12H19M12 5L19 12L12 19" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
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
      localPrompt: '',
      suggestions: {
        'assistant-general': 'Tu es un assistant IA polyvalent et bienveillant. Tu réponds de manière claire, précise et utile à toutes les questions. Tu adoptes un ton professionnel mais chaleureux, et tu t\'adaptes au niveau de connaissance de l\'utilisateur. Tu fournis des exemples concrets quand c\'est pertinent.',
        'assistant-technique': 'Tu es un assistant technique spécialisé en développement et technologies. Tu réponds avec précision en fournissant du code, des solutions pratiques et des explications détaillées. Tu utilises un langage technique approprié et proposes toujours des alternatives quand c\'est possible.',
        'assistant-creatif': 'Tu es un assistant créatif spécialisé dans la génération de contenu artistique et innovant. Tu adoptes un ton inspirant et imaginatif, tu proposes des idées originales et tu encourages la créativité. Tu sais adapter ton style selon le type de création demandé.'
      }
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
    isFormValid() {
    return this.localPrompt.trim().length > 0
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
    },
    useSuggestion(type) {
      this.localPrompt = this.suggestions[type]
      this.setPrompt(this.localPrompt)
    }
  }
}
</script>

<style scoped>
.container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.page-content {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  padding: 40px;
  margin: 30px 0;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  animation: slideUp 0.6s ease-out;
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
  margin-bottom: 50px;
}

.page-title {
  font-size: 2.5rem;
  font-weight: 800;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0 0 10px 0;
  letter-spacing: -0.02em;
}

.page-subtitle {
  color: #64748b;
  font-size: 1.1rem;
  margin: 0;
  font-weight: 500;
}

.prompt-section {
  background: white;
  border-radius: 20px;
  padding: 30px;
  margin-bottom: 40px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.05);
  border: 1px solid #f1f5f9;
}

.prompt-header {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 25px;
}

.prompt-icon {
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.prompt-title h3 {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 5px 0;
}

.prompt-title p {
  color: #64748b;
  margin: 0;
  font-size: 0.95rem;
}

.textarea-wrapper {
  position: relative;
  margin-bottom: 20px;
}

.prompt-textarea {
  width: 100%;
  min-height: 200px;
  padding: 20px;
  border: 2px solid #e2e8f0;
  border-radius: 16px;
  font-family: 'SF Pro Text', -apple-system, BlinkMacSystemFont, sans-serif;
  font-size: 15px;
  line-height: 1.6;
  resize: vertical;
  box-sizing: border-box;
  transition: all 0.3s ease;
  background: #fafbfc;
  color: #334155;
}

.prompt-textarea:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
  background: white;
  transform: translateY(-2px);
}

.prompt-textarea::placeholder {
  color: #94a3b8;
  font-style: italic;
}

.textarea-decoration {
  position: absolute;
  top: -1px;
  left: -1px;
  right: -1px;
  bottom: -1px;
  border-radius: 16px;
  background: linear-gradient(135deg, #667eea, #764ba2, #10b981);
  opacity: 0;
  transition: opacity 0.3s ease;
  pointer-events: none;
  z-index: -1;
}

.prompt-textarea:focus + .textarea-decoration {
  opacity: 0.1;
}

.prompt-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 20px;
}

.character-count {
  font-size: 14px;
  color: #64748b;
  font-weight: 500;
}

.character-count .warning {
  color: #f59e0b;
}

.character-count .danger {
  color: #ef4444;
  font-weight: 700;
}

.count-separator {
  margin: 0 4px;
  opacity: 0.5;
}

.count-max {
  color: #94a3b8;
}

.count-label {
  margin-left: 8px;
  font-size: 13px;
  opacity: 0.7;
}

.prompt-suggestions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.suggestion-btn {
  padding: 8px 16px;
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  color: #475569;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.suggestion-btn:hover {
  background: #e2e8f0;
  border-color: #cbd5e1;
  transform: translateY(-1px);
}

.summary-section {
  background: white;
  border-radius: 20px;
  padding: 30px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.05);
  border: 1px solid #f1f5f9;
}

.summary-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  flex-wrap: wrap;
  gap: 15px;
}

.summary-header h3 {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1e293b;
  margin: 0;
}

.summary-status {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  background: #fef3c7;
  color: #92400e;
  border: 1px solid #fcd34d;
  transition: all 0.3s ease;
}

.summary-status.complete {
  background: #dcfce7;
  color: #166534;
  border-color: #86efac;
}

.summary-status svg {
  flex-shrink: 0;
}

.config-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
}

.config-card {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 20px;
  background: #fafbfc;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  transition: all 0.3s ease;
}

.config-card:hover {
  background: #f8fafc;
  border-color: #cbd5e1;
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
}

.config-icon {
  font-size: 24px;
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  flex-shrink: 0;
}

.config-content {
  flex: 1;
  min-width: 0;
}

.config-content h4 {
  font-size: 1rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 4px 0;
}

.config-content p {
  font-size: 14px;
  color: #64748b;
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
  background: #fef2f2;
  color: #dc2626;
  flex-shrink: 0;
  transition: all 0.3s ease;
}

.config-status.valid {
  background: #f0fdf4;
  color: #16a34a;
}

.config-status svg {
  flex-shrink: 0;
}

.button-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
  margin-top: 30px;
  flex-wrap: wrap;
}

.btn-link {
  text-decoration: none;
  flex: 1;
  max-width: 300px;
}

.btn {
  width: 100%;
  padding: 16px 24px;
  border-radius: 16px;
  font-size: 16px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  transition: all 0.3s ease;
  cursor: pointer;
  border: none;
  min-height: 56px;
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.9);
  color: #475569;
  border: 1px solid rgba(255, 255, 255, 0.3);
  backdrop-filter: blur(10px);
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 1);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.2);
  position: relative;
  overflow: hidden;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 12px 35px rgba(102, 126, 234, 0.4);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.btn-primary::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s;
}

.btn-primary:hover:not(:disabled)::before {
  left: 100%;
}

.btn svg {
  flex-shrink: 0;
}

/* Styles spécifiques pour les boutons */
.btn-finish {
  position: relative;
  overflow: hidden;
}

.btn-finish:not(:disabled) {
  background: linear-gradient(135deg, #10b981 0%, #059669 50%, #047857 100%);
  box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
}

.btn-finish:hover:not(:disabled) {
  box-shadow: 0 8px 25px rgba(16, 185, 129, 0.4);
  transform: translateY(-3px);
}

.btn-finish:disabled {
  background: #9ca3af;
  color: #6b7280;
  box-shadow: none;
}

.btn-primary.btn-finish:not(:disabled)::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, transparent 0%, rgba(255, 255, 255, 0.1) 50%, transparent 100%);
  transform: translateX(-100%);
  transition: transform 0.6s ease;
}

.btn-primary.btn-finish:hover:not(:disabled)::after {
  transform: translateX(100%);
}

/* Animation pour les icônes des boutons */
.btn svg {
  transition: transform 0.3s ease;
}

.btn:hover svg {
  transform: scale(1.1);
}

.btn-secondary:hover svg {
  transform: translateX(-2px) scale(1.1);
}

.btn-primary:hover:not(:disabled) svg {
  transform: translateX(2px) scale(1.1);
}

/* Styles pour les liens de boutons */
.btn-link {
  display: block;
  transition: all 0.3s ease;
}

.btn-link:first-child {
  flex: 0 0 auto;
}

.btn-link:last-child {
  flex: 1;
}

/* États de focus pour l'accessibilité */
.btn:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.3);
}

.btn-secondary:focus {
  box-shadow: 0 0 0 3px rgba(71, 85, 105, 0.3);
}

/* Animation de chargement pour le bouton primaire */
.btn-primary.loading {
  position: relative;
  color: transparent;
}

.btn-primary.loading::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 20px;
  height: 20px;
  margin: -10px 0 0 -10px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Styles pour les boutons de suggestion */
.suggestion-btn {
  position: relative;
  overflow: hidden;
}

.suggestion-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.1), transparent);
  transition: left 0.4s ease;
}

.suggestion-btn:hover::before {
  left: 100%;
}

.suggestion-btn:active {
  transform: scale(0.98);
}

@media (max-width: 768px) {
  .container {
    padding: 15px;
  }
  
  .page-content {
    padding: 25px;
    margin: 20px 0;
  }
  
  .page-title {
    font-size: 2rem;
  }
  
  .prompt-section,
  .summary-section {
    padding: 20px;
  }
  
  .prompt-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .prompt-footer {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .config-grid {
    grid-template-columns: 1fr;
  }
  
  .button-container {
    flex-direction: column;
  }
  
  .btn-link {
    max-width: none;
  }
  
  .summary-header {
    flex-direction: column;
    align-items: flex-start;
  }
}

@media (max-width: 480px) {
  .page-title {
    font-size: 1.8rem;
  }
  
  .prompt-textarea {
    min-height: 150px;
  }
  
  .config-card {
    padding: 15px;
  }
  
  .config-icon {
    width: 40px;
    height: 40px;
    font-size: 20px;
  }
}
</style>