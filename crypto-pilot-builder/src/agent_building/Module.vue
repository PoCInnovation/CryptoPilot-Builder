<template>
  <div class="container">
    <progress-bar :current-step="2" :total-steps="3" />
    <div class="page-content">
      <div class="header-section">
        <h2 class="page-title">Configuration des Modules</h2>
        <p class="page-subtitle">
          Personnalisez les fonctionnalités de votre assistant
        </p>
      </div>
      <div class="content-section">
        <div class="feature-cards">
          <div class="feature-card">
            <div class="feature-icon">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none">
                <path
                  d="M9 12L11 14L15 10M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                />
              </svg>
            </div>
            <h3>Configuration</h3>
            <p>
              Définissez les paramètres avancés de votre assistant IA selon vos
              besoins spécifiques.
            </p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none">
                <path
                  d="M10.325 4.317C10.751 2.561 13.249 2.561 13.675 4.317C13.7389 4.5808 13.8642 4.82578 14.0407 5.032C14.2172 5.23822 14.4399 5.39985 14.6907 5.50375C14.9414 5.60764 15.2132 5.65085 15.4838 5.62987C15.7544 5.60889 16.0162 5.5243 16.248 5.383C17.791 4.443 19.558 6.209 18.618 7.753C18.4769 7.98466 18.3924 8.24634 18.3715 8.51677C18.3506 8.78721 18.3938 9.05877 18.4975 9.30938C18.6013 9.55999 18.7627 9.78258 18.9687 9.95905C19.1747 10.1355 19.4194 10.2609 19.683 10.325C21.439 10.751 21.439 13.249 19.683 13.675C19.4192 13.7389 19.1742 13.8642 18.968 14.0407C18.7618 14.2172 18.6001 14.4399 18.4963 14.6907C18.3924 14.9414 18.3491 15.2132 18.3701 15.4838C18.3911 15.7544 18.4757 16.0162 18.617 16.248C19.557 17.791 17.791 19.558 16.247 18.618C16.0153 18.4769 15.7537 18.3924 15.4832 18.3715C15.2128 18.3506 14.9412 18.3938 14.6906 18.4975C14.44 18.6013 14.2174 18.7627 14.0409 18.9687C13.8645 19.1747 13.7391 19.4194 13.675 19.683C13.249 21.439 10.751 21.439 10.325 19.683C10.2611 19.4192 10.1358 19.1742 9.95929 18.968C9.7828 18.7618 9.56011 18.6001 9.30935 18.4963C9.05859 18.3924 8.78683 18.3491 8.51621 18.3701C8.24559 18.3911 7.98375 18.4757 7.752 18.617C6.209 19.557 4.442 17.791 5.382 16.247C5.5231 16.0153 5.60755 15.7537 5.62848 15.4832C5.64942 15.2128 5.60624 14.9412 5.50247 14.6906C5.3987 14.44 5.23726 14.2174 5.03127 14.0409C4.82529 13.8645 4.58056 13.7391 4.317 13.675C2.561 13.249 2.561 10.751 4.317 10.325C4.5808 10.2611 4.82578 10.1358 5.032 9.95929C5.23822 9.7828 5.39985 9.56011 5.50375 9.30935C5.60764 9.05859 5.65085 8.78683 5.62987 8.51621C5.60889 8.24559 5.5243 7.98375 5.383 7.752C4.443 6.209 6.209 4.442 7.753 5.382C7.98466 5.5231 8.24634 5.60755 8.51677 5.62848C8.78721 5.64942 9.05877 5.60624 9.30938 5.50247C9.55999 5.3987 9.78258 5.23726 9.95905 5.03127C10.1355 4.82529 10.2609 4.58056 10.325 4.317Z"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                />
                <circle
                  cx="12"
                  cy="12"
                  r="3"
                  stroke="currentColor"
                  stroke-width="2"
                />
              </svg>
            </div>
            <h3>Paramètres</h3>
            <p>
              Ajustez les réglages pour optimiser les performances et
              l'expérience utilisateur.
            </p>
          </div>
        </div>
        <div class="module-selection">
          <h3>Choisissez vos modules</h3>
          <div class="modules-grid">
            <div class="module-card">
              <div class="module-header">
                <div class="module-icon">💬</div>
                <h4>Chat Avancé</h4>
              </div>
              <p>Conversations naturelles avec mémoire contextuelle</p>
              <label class="toggle-switch">
                <input type="checkbox" v-model="modules.chatAdvanced" />
                <span class="slider"></span>
              </label>
            </div>
            <div class="module-card">
              <div class="module-header">
                <div class="module-icon">📊</div>
                <h4>Analyse de Données</h4>
              </div>
              <p>Traitement et visualisation de données complexes</p>
              <label class="toggle-switch">
                <input type="checkbox" v-model="modules.dataAnalysis" />
                <span class="slider"></span>
              </label>
            </div>
            <div class="module-card">
              <div class="module-header">
                <div class="module-icon">🔍</div>
                <h4>Recherche Web</h4>
              </div>
              <p>Accès aux informations en temps réel</p>
              <label class="toggle-switch">
                <input type="checkbox" v-model="modules.webSearch" />
                <span class="slider"></span>
              </label>
            </div>
            <div class="module-card">
              <div class="module-header">
                <div class="module-icon">🎨</div>
                <h4>Génération Creative</h4>
              </div>
              <p>Création de contenu artistique et créatif</p>
              <label class="toggle-switch">
                <input type="checkbox" v-model="modules.creativeGeneration" />
                <span class="slider"></span>
              </label>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="button-container">
      <router-link to="/AI" class="btn-link">
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
      <router-link to="/Prompte" class="btn-link">
        <button class="btn btn-primary" @click="saveConfig">
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
  name: "Module",
  components: {
    ProgressBar,
  },
  data() {
    return {
      modules: {
        chatAdvanced: true,
        dataAnalysis: false,
        webSearch: false,
        creativeGeneration: false,
      },
    };
  },
  computed: {
    ...mapGetters(["aiConfig", "isLoading"]),
    isFormValid() {
      return Object.values(this.modules).some((module) => module);
    },
  },
  methods: {
    ...mapActions(["setModules"]),
    async saveConfig() {
      try {
        await this.setModules(this.modules);
        console.log("Configuration des modules sauvegardée:", this.modules);

        // Montrer un feedback visuel de succès
        this.$emit("config-saved", "modules");
      } catch (error) {
        console.error("Erreur lors de la sauvegarde des modules:", error);
        // Afficher un message d'erreur à l'utilisateur
      }
    },
  },
  mounted() {
    // Charger la configuration existante des modules
    const existingModules = this.aiConfig.modules || {};
    if (Object.keys(existingModules).length > 0) {
      this.modules = { ...this.modules, ...existingModules };
    }
  },
  watch: {
    // Sauvegarder automatiquement quand les modules changent
    modules: {
      handler(newModules) {
        this.setModules(newModules);
      },
      deep: true,
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
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  flex-direction: column;
  position: fixed;
  top: 0;
  left: 0;
  overflow-y: auto;
  font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI",
    sans-serif;
}

.page-content {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  padding: 40px;
  margin: 30px auto;
  max-width: 900px;
  width: 100%;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  animation: slideUp 0.6s ease-out;
  box-sizing: border-box;
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
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
  margin-bottom: 30px;
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

.content-section {
  display: flex;
  flex-direction: column;
  gap: 30px;
  flex: 1;
}

.feature-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.feature-card {
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  padding: 25px;
  border-radius: 20px;
  text-align: center;
  border: 1px solid rgba(255, 255, 255, 0.8);
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  position: relative;
  overflow: hidden;
}

.feature-card::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  transform: translateX(-100%);
  transition: transform 0.4s ease;
}

.feature-card:hover::before {
  transform: translateX(0);
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.15);
}

.feature-icon {
  display: inline-flex;
  padding: 15px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 15px;
  color: white;
  margin-bottom: 15px;
  transition: transform 0.3s ease;
}

.feature-card:hover .feature-icon {
  transform: scale(1.1);
}

.feature-card h3 {
  font-size: 1.3rem;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 10px 0;
}

.feature-card p {
  color: #64748b;
  font-size: 0.95rem;
  line-height: 1.5;
  margin: 0;
}

.module-selection {
  background: white;
  padding: 30px;
  border-radius: 20px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.08);
  border: 1px solid #f1f5f9;
}

.module-selection h3 {
  font-size: 1.6rem;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 25px 0;
  text-align: center;
  position: relative;
}

.module-selection h3::after {
  content: "";
  position: absolute;
  bottom: -8px;
  left: 50%;
  transform: translateX(-50%);
  width: 50px;
  height: 3px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 2px;
}

.modules-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.module-card {
  background: #fafbfc;
  padding: 25px;
  border-radius: 16px;
  border: 2px solid #e2e8f0;
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  position: relative;
  overflow: hidden;
}

.module-card::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(
    135deg,
    rgba(102, 126, 234, 0.05) 0%,
    rgba(118, 75, 162, 0.05) 100%
  );
  opacity: 0;
  transition: opacity 0.3s ease;
}

.module-card:hover::before {
  opacity: 1;
}

.module-card:hover {
  border-color: #667eea;
  transform: translateY(-3px);
  box-shadow: 0 10px 25px rgba(102, 126, 234, 0.2);
  background: white;
}

.module-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 15px;
}

.module-icon {
  font-size: 1.8rem;
  width: 45px;
  height: 45px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  box-shadow: 0 6px 12px rgba(102, 126, 234, 0.3);
  transition: transform 0.3s ease;
}

.module-card:hover .module-icon {
  transform: scale(1.1);
}

.module-card h4 {
  font-size: 1.1rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.module-card p {
  color: #64748b;
  font-size: 0.9rem;
  line-height: 1.5;
  margin: 0 0 20px 0;
}

.toggle-switch {
  position: absolute;
  top: 20px;
  right: 20px;
  width: 48px;
  height: 26px;
}

.toggle-switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #cbd5e1;
  transition: 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  border-radius: 26px;
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1);
}

.slider:before {
  position: absolute;
  content: "";
  height: 20px;
  width: 20px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  border-radius: 50%;
  box-shadow: 0 3px 6px rgba(0, 0, 0, 0.15);
}

input:checked + .slider {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.2);
}

input:checked + .slider:before {
  transform: translateX(22px);
}

.slider:hover {
  box-shadow: 0 0 0 6px rgba(102, 126, 234, 0.1);
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
  border: none;
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
  content: "";
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(255, 255, 255, 0.2),
    transparent
  );
  transition: left 0.5s;
}

.btn:hover::before {
  left: 100%;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
}

.btn-primary:hover {
  transform: translateY(-3px);
  box-shadow: 0 15px 30px rgba(102, 126, 234, 0.4);
}

.btn-secondary {
  background: white;
  color: #64748b;
  border: 2px solid #e2e8f0;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.btn-secondary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
  border-color: #cbd5e1;
  color: #475569;
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

  .feature-cards {
    grid-template-columns: 1fr;
  }

  .modules-grid {
    grid-template-columns: 1fr;
  }

  .button-container {
    flex-direction: column;
    gap: 15px;
    padding: 0 15px;
  }

  .btn-link {
    flex: none;
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

  .feature-card {
    padding: 20px;
  }
}
</style>
