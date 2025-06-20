<template>
  <div class="config-manager">
    <div class="header">
      <h2>🤖 Mes Configurations d'Agent</h2>
      <p>Gérez vos configurations d'assistants IA</p>
    </div>

    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>Chargement des configurations...</p>
    </div>

    <div v-if="error" class="error-message">
      <div class="error-icon">⚠️</div>
      <p>{{ error }}</p>
      <button @click="loadConfigs" class="retry-btn">Réessayer</button>
    </div>

    <div v-if="!loading && !error" class="configs-grid">
      <div
        v-for="config in configs"
        :key="config.id"
        class="config-card"
        :class="{ active: config.isActive }"
      >
        <div class="config-header">
          <div class="config-icon">🤖</div>
          <div class="config-info">
            <h3>{{ config.name }}</h3>
            <p>{{ config.description || "Aucune description" }}</p>
          </div>
          <div v-if="config.isActive" class="active-badge">Actif</div>
        </div>

        <div class="config-details">
          <div class="detail-row">
            <span class="label">Modèle:</span>
            <span class="value">{{ config.selectedModel }}</span>
          </div>
          <div class="detail-row">
            <span class="label">Créé le:</span>
            <span class="value">{{ formatDate(config.createdAt) }}</span>
          </div>
          <div class="detail-row">
            <span class="label">Modifié le:</span>
            <span class="value">{{ formatDate(config.updatedAt) }}</span>
          </div>
        </div>

        <div class="config-actions">
          <button
            v-if="!config.isActive"
            @click="activateConfig(config)"
            class="btn btn-primary"
          >
            Activer
          </button>
          <button @click="editConfig(config)" class="btn btn-secondary">
            Modifier
          </button>
          <button @click="duplicateConfig(config)" class="btn btn-secondary">
            Dupliquer
          </button>
          <button
            @click="deleteConfig(config)"
            class="btn btn-danger"
            :disabled="config.isActive"
          >
            Supprimer
          </button>
        </div>
      </div>

      <div class="add-config-card" @click="createNewConfig">
        <div class="add-icon">➕</div>
        <h3>Nouvelle Configuration</h3>
        <p>Créer un nouvel assistant IA</p>
      </div>
    </div>

    <div v-if="!loading && !error && configs.length === 0" class="empty-state">
      <div class="empty-icon">🤖</div>
      <h3>Aucune configuration trouvée</h3>
      <p>Créez votre première configuration d'agent</p>
      <button @click="createNewConfig" class="btn btn-primary">
        Créer ma première configuration
      </button>
    </div>
  </div>
</template>

<script>
import { mapGetters, mapActions } from "vuex";
import apiService from "../services/apiService";

export default {
  name: "AgentConfigManager",
  data() {
    return {
      configs: [],
      loading: false,
      error: null,
    };
  },
  computed: {
    ...mapGetters(["isAuthenticated"]),
  },
  methods: {
    ...mapActions(["loadAgentConfig"]),

    async loadConfigs() {
      if (!this.isAuthenticated) {
        this.error = "Vous devez être connecté pour voir vos configurations";
        return;
      }

      try {
        this.loading = true;
        this.error = null;

        const response = await apiService.listAgentConfigs();
        this.configs = response.configs || [];
      } catch (error) {
        console.error("Erreur lors du chargement des configurations:", error);
        this.error = error.message;
      } finally {
        this.loading = false;
      }
    },

    async activateConfig(config) {
      try {
        // Marquer cette configuration comme active
        await apiService.updatePartialConfig({ isActive: true });

        // Recharger la configuration dans le store
        await this.loadAgentConfig();

        // Recharger la liste
        await this.loadConfigs();

        this.$emit("config-activated", config);
      } catch (error) {
        console.error("Erreur lors de l'activation:", error);
        this.error = error.message;
      }
    },

    editConfig(config) {
      this.$emit("edit-config", config);
      // Ou rediriger vers la page d'édition
      this.$router.push({ name: "AI", params: { configId: config.id } });
    },

    async duplicateConfig(config) {
      try {
        const newConfig = {
          selectedModel: config.selectedModel,
          modules: config.modules,
          prompt: config.prompt,
          name: `${config.name} (Copie)`,
          description: config.description,
        };

        await apiService.saveAgentConfig(newConfig);
        await this.loadConfigs();
      } catch (error) {
        console.error("Erreur lors de la duplication:", error);
        this.error = error.message;
      }
    },

    async deleteConfig(config) {
      if (config.isActive) {
        alert("Impossible de supprimer la configuration active");
        return;
      }

      if (!confirm(`Êtes-vous sûr de vouloir supprimer "${config.name}" ?`)) {
        return;
      }

      try {
        // Note: Il faudrait ajouter une route de suppression dans l'API
        // await apiService.deleteAgentConfig(config.id)
        await this.loadConfigs();
      } catch (error) {
        console.error("Erreur lors de la suppression:", error);
        this.error = error.message;
      }
    },

    createNewConfig() {
      this.$router.push({ name: "AI" });
    },

    formatDate(dateString) {
      return new Date(dateString).toLocaleDateString("fr-FR", {
        year: "numeric",
        month: "long",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });
    },
  },

  async mounted() {
    await this.loadConfigs();
  },
};
</script>

<style scoped>
.config-manager {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI",
    sans-serif;
}

.header {
  text-align: center;
  margin-bottom: 40px;
}

.header h2 {
  font-size: 2.5rem;
  font-weight: 800;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin: 0 0 10px 0;
}

.header p {
  color: #64748b;
  font-size: 1.1rem;
  margin: 0;
}

.loading,
.empty-state {
  text-align: center;
  padding: 60px 20px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e2e8f0;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.error-message {
  background: #fee2e2;
  border: 1px solid #fecaca;
  border-radius: 12px;
  padding: 20px;
  text-align: center;
  margin-bottom: 20px;
}

.error-icon {
  font-size: 2rem;
  margin-bottom: 10px;
}

.retry-btn {
  background: #ef4444;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 8px;
  cursor: pointer;
  margin-top: 10px;
}

.configs-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 24px;
}

.config-card,
.add-config-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  border: 1px solid #e2e8f0;
  transition: all 0.3s ease;
}

.config-card:hover,
.add-config-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.config-card.active {
  border-color: #667eea;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
}

.config-header {
  display: flex;
  align-items: flex-start;
  margin-bottom: 20px;
}

.config-icon {
  font-size: 2rem;
  margin-right: 16px;
}

.config-info {
  flex: 1;
}

.config-info h3 {
  margin: 0 0 8px 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: #1e293b;
}

.config-info p {
  margin: 0;
  color: #64748b;
  font-size: 0.9rem;
}

.active-badge {
  background: #10b981;
  color: white;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
}

.config-details {
  margin-bottom: 20px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.label {
  color: #64748b;
  font-weight: 500;
}

.value {
  color: #1e293b;
  font-weight: 600;
}

.config-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.btn {
  padding: 8px 16px;
  border-radius: 8px;
  border: none;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 0.9rem;
}

.btn-primary {
  background: #667eea;
  color: white;
}

.btn-primary:hover {
  background: #5a67d8;
}

.btn-secondary {
  background: #e2e8f0;
  color: #475569;
}

.btn-secondary:hover {
  background: #cbd5e1;
}

.btn-danger {
  background: #ef4444;
  color: white;
}

.btn-danger:hover {
  background: #dc2626;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.add-config-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  cursor: pointer;
  border: 2px dashed #cbd5e1;
  background: #f8fafc;
}

.add-config-card:hover {
  border-color: #667eea;
  background: #f1f5f9;
}

.add-icon {
  font-size: 3rem;
  color: #667eea;
  margin-bottom: 16px;
}

.add-config-card h3 {
  margin: 0 0 8px 0;
  color: #1e293b;
}

.add-config-card p {
  margin: 0;
  color: #64748b;
}

.empty-state {
  background: #f8fafc;
  border-radius: 16px;
  border: 2px dashed #cbd5e1;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 20px;
}

.empty-state h3 {
  color: #1e293b;
  margin: 0 0 10px 0;
}

.empty-state p {
  color: #64748b;
  margin: 0 0 20px 0;
}
</style>
