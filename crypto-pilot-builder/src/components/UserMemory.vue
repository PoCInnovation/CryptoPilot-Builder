<template>
  <div class="user-memory-container">
    <div class="memory-header">
      <h2>🧠 Mémoire Utilisateur</h2>
      <p class="memory-description">
        Votre IA apprend automatiquement de vos conversations et retient les
        informations importantes vous concernant.
      </p>
    </div>

    <!-- Message de connexion requis -->
    <div v-if="!isAuthenticated" class="auth-required">
      <h3>🔐 Connexion requise</h3>
      <p>Vous devez être connecté pour voir votre mémoire utilisateur.</p>
      <p>Veuillez vous connecter ou créer un compte.</p>
    </div>

    <!-- Contenu principal (si connecté) -->
    <div v-else>
      <!-- Résumé du profil utilisateur -->
      <div class="profile-summary" v-if="memorySummary">
        <h3>📋 Résumé de votre profil</h3>
        <div class="summary-content">
          <pre>{{ memorySummary }}</pre>
        </div>
      </div>

      <!-- Statistiques par catégorie -->
      <div class="memory-stats" v-if="memories.length > 0">
        <div class="stat-card" v-for="(count, type) in memoryStats" :key="type">
          <div class="stat-icon">{{ getTypeIcon(type) }}</div>
          <div class="stat-content">
            <h4>{{ getTypeLabel(type) }}</h4>
            <span class="stat-count">{{ count }} éléments</span>
          </div>
        </div>
      </div>

      <!-- Liste des informations mémorisées -->
      <div class="memory-list" v-if="memories.length > 0">
        <div
          class="memory-section"
          v-for="(items, type) in groupedMemories"
          :key="type"
        >
          <h3>{{ getTypeIcon(type) }} {{ getTypeLabel(type) }}</h3>
          <div class="memory-items">
            <div class="memory-item" v-for="memory in items" :key="memory.id">
              <!-- Mode lecture -->
              <div v-if="editingId !== memory.id" class="memory-content">
                <strong>{{ memory.key_info }}</strong>
                <p>{{ memory.value_info }}</p>
                <div class="memory-meta">
                  <span class="confidence"
                    >Confiance:
                    {{ Math.round(memory.confidence_score * 100) }}%</span
                  >
                  <span class="date">{{ formatDate(memory.created_at) }}</span>
                </div>
              </div>

              <!-- Mode édition -->
              <div v-else class="memory-edit-form">
                <input
                  v-model="editForm.key_info"
                  placeholder="Titre"
                  class="edit-input"
                />
                <textarea
                  v-model="editForm.value_info"
                  placeholder="Détails"
                  class="edit-textarea"
                ></textarea>
                <div class="edit-actions">
                  <button @click="saveEdit(memory.id)" class="save-btn">
                    💾 Sauver
                  </button>
                  <button @click="cancelEdit()" class="cancel-btn">
                    ❌ Annuler
                  </button>
                </div>
              </div>

              <!-- Actions -->
              <div class="memory-actions">
                <button
                  v-if="editingId !== memory.id"
                  @click="startEdit(memory)"
                  class="edit-btn"
                  title="Modifier cette information"
                >
                  ✏️
                </button>
                <button
                  @click="deleteMemory(memory.id)"
                  class="delete-btn"
                  title="Supprimer cette information"
                >
                  🗑️
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Message si aucune mémoire -->
      <div v-if="memories.length === 0 && !statusMessage" class="no-memories">
        <h3>🤖 Aucune information mémorisée pour le moment</h3>
        <p>
          Commencez à discuter avec votre IA pour qu'elle apprenne à vous
          connaître !
        </p>
      </div>
    </div>

    <!-- Messages de statut -->
    <div v-if="statusMessage" class="status-message" :class="statusType">
      {{ statusMessage }}
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted, computed } from "vue";
import { useStore } from "vuex";

export default {
  name: "UserMemory",
  setup() {
    const store = useStore();
    const memories = ref([]);
    const memorySummary = ref("");
    const statusMessage = ref("");
    const statusType = ref("");
    const editingId = ref(null);

    const editForm = reactive({
      key_info: "",
      value_info: "",
    });

    // Récupérer les données d'auth depuis Vuex
    const token = computed(() => store.state.auth.token);
    const isAuthenticated = computed(() => store.state.auth.isAuthenticated);

    // Statistiques par type
    const memoryStats = computed(() => {
      const stats = {};
      memories.value.forEach((memory) => {
        stats[memory.memory_type] = (stats[memory.memory_type] || 0) + 1;
      });
      return stats;
    });

    // Mémoires groupées par type
    const groupedMemories = computed(() => {
      const grouped = {};
      memories.value.forEach((memory) => {
        if (!grouped[memory.memory_type]) {
          grouped[memory.memory_type] = [];
        }
        grouped[memory.memory_type].push(memory);
      });
      return grouped;
    });

    // Fonctions utilitaires
    const getTypeIcon = (type) => {
      // Icônes dynamiques basées sur des mots-clés dans le type
      const iconMap = {
        identite: "👤",
        personal: "👤",
        nom: "👤",
        preferences: "⚙️",
        crypto: "₿",
        blockchain: "🔗",
        expertise: "🎯",
        niveau: "📊",
        experience: "📈",
        objectifs: "🚀",
        goals: "🚀",
        budget: "💰",
        risque: "⚠️",
        trading: "📊",
        investissement: "💎",
        situation: "🏢",
        professionnel: "💼",
        localisation: "📍",
        communication: "💬",
        style: "🎨",
        projet: "🛠️",
        horizon: "⏰",
        tolerance: "🎚️",
        contacts: "👥",
        relations: "🤝",
        portefeuille: "💳",
        wallet: "💳",
      };

      // Chercher une correspondance dans le nom du type
      const lowerType = type.toLowerCase();
      for (const [keyword, icon] of Object.entries(iconMap)) {
        if (lowerType.includes(keyword)) {
          return icon;
        }
      }

      // Icône par défaut
      return "📋";
    };

    const getTypeLabel = (type) => {
      // Convertir snake_case en format lisible
      return type
        .split("_")
        .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
        .join(" ");
    };

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString("fr-FR", {
        year: "numeric",
        month: "short",
        day: "numeric",
      });
    };

    // Charger les mémoires
    const loadMemories = async () => {
      if (!isAuthenticated.value || !token.value) {
        console.log("Utilisateur non authentifié");
        return;
      }

      try {
        const response = await fetch("http://localhost:5000/user-memory", {
          headers: {
            Authorization: `Bearer ${token.value}`,
          },
        });

        if (response.ok) {
          const data = await response.json();
          memories.value = data.memories || [];
          memorySummary.value = data.summary || "";
          console.log("Mémoires chargées:", data);
        } else {
          console.error("Erreur API:", response.status, response.statusText);
          showStatus(`Erreur API: ${response.status}`, "error");
        }
      } catch (error) {
        console.error("Erreur lors du chargement des mémoires:", error);
        showStatus("Erreur de connexion au serveur", "error");
      }
    };

    // Commencer l'édition
    const startEdit = (memory) => {
      editingId.value = memory.id;
      editForm.key_info = memory.key_info;
      editForm.value_info = memory.value_info;
    };

    // Annuler l'édition
    const cancelEdit = () => {
      editingId.value = null;
      editForm.key_info = "";
      editForm.value_info = "";
    };

    // Sauvegarder l'édition
    const saveEdit = async (memoryId) => {
      try {
        const response = await fetch(
          `http://localhost:5000/user-memory/${memoryId}`,
          {
            method: "PUT",
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${token.value}`,
            },
            body: JSON.stringify({
              key_info: editForm.key_info,
              value_info: editForm.value_info,
            }),
          }
        );

        if (response.ok) {
          // Mettre à jour localement
          const memoryIndex = memories.value.findIndex(
            (m) => m.id === memoryId
          );
          if (memoryIndex !== -1) {
            memories.value[memoryIndex].key_info = editForm.key_info;
            memories.value[memoryIndex].value_info = editForm.value_info;
          }

          cancelEdit();
          showStatus("Information modifiée avec succès", "success");
        } else {
          showStatus("Erreur lors de la modification", "error");
        }
      } catch (error) {
        console.error("Erreur lors de la modification:", error);
        showStatus("Erreur lors de la modification", "error");
      }
    };

    // Supprimer une mémoire
    const deleteMemory = async (memoryId) => {
      if (!confirm("Êtes-vous sûr de vouloir supprimer cette information ?")) {
        return;
      }

      try {
        const response = await fetch(
          `http://localhost:5000/user-memory/${memoryId}`,
          {
            method: "DELETE",
            headers: {
              Authorization: `Bearer ${token.value}`,
            },
          }
        );

        if (response.ok) {
          memories.value = memories.value.filter((m) => m.id !== memoryId);
          showStatus("Information supprimée avec succès", "success");
        }
      } catch (error) {
        console.error("Erreur lors de la suppression:", error);
        showStatus("Erreur lors de la suppression", "error");
      }
    };

    // Afficher un message de statut
    const showStatus = (message, type) => {
      statusMessage.value = message;
      statusType.value = type;
      setTimeout(() => {
        statusMessage.value = "";
        statusType.value = "";
      }, 3000);
    };

    // Charger les données au montage
    onMounted(() => {
      // Vérifier l'auth au démarrage
      store.dispatch("auth/checkAuth");
      loadMemories();
    });

    return {
      memories,
      memorySummary,
      memoryStats,
      groupedMemories,
      editingId,
      editForm,
      statusMessage,
      statusType,
      isAuthenticated,
      getTypeIcon,
      getTypeLabel,
      formatDate,
      startEdit,
      cancelEdit,
      saveEdit,
      deleteMemory,
    };
  },
};
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');

/* Scroll behavior */
.user-memory-container {
  scroll-behavior: smooth;
}

/* Particle background - styles for elements if used */
.particles-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: -1;
}

.particle {
  position: absolute;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 50%;
  animation: float 15s infinite ease-in-out;
  box-shadow: 0 0 10px rgba(118, 75, 162, 0.8);
}

@keyframes float {
  0% {
    transform: translate(0, 0) rotate(0deg);
    opacity: 0;
  }
  10% {
    opacity: 1;
  }
  90% {
    opacity: 1;
  }
  100% {
    transform: translate(calc((var(--tx, 0) - 0.5) * 100vw), calc((var(--ty, 0) - 0.5) * 100vh)) rotate(360deg);
    opacity: 0;
  }
}

/* Animations */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

/* Main Container */
.user-memory-container {
  animation: fadeIn 0.5s ease;
  width: 98vw;
  height: 100vh;
  margin: 0;
  padding: 20px;
  min-height: 100vh;
  font-family: 'Roboto', sans-serif;
  background: linear-gradient(135deg, #111421 0%, #111421 100%);
  position: relative;
  z-index: 1;
  backdrop-filter: blur(10px);
  border: none;
  box-shadow: none;
  overflow-y: auto;
  margin: 0 auto;
}

/* Header */
.memory-header {
  text-align: center;
  margin-bottom: 30px;
  animation: fadeInUp 0.6s ease;
}

.memory-header h2 {
  color: white;
  margin-bottom: 10px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.memory-description {
  color: rgba(255, 255, 255, 0.8);
  font-size: 16px;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

/* Auth Required Message */
.auth-required {
  text-align: center;
  padding: 40px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  color: white;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.auth-required h3 {
  color: white;
  margin-bottom: 15px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

/* Profile Summary */
.profile-summary {
  /* background: #f8f9fa; Removed for glassmorphism */
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 30px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  color: white;
}

.profile-summary h3 {
  color: white;
  margin-bottom: 15px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.summary-content pre {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  padding: 15px;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  white-space: pre-wrap;
  font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
  line-height: 1.5;
  color: white;
}

/* Memory Stats */
.memory-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
  animation: fadeInUp 0.7s ease;
}

.stat-card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border-radius: 16px;
  padding: 20px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  gap: 15px;
  color: white;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.stat-card::before {
  content: '';
  position: absolute;
  top: -2px;
  left: -2px;
  right: -2px;
  bottom: -2px;
  background: linear-gradient(45deg, rgba(118, 75, 162, 0.2), rgba(200, 100, 200, 0.2), rgba(118, 75, 162, 0.2));
  z-index: -1;
  border-radius: 18px;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.stat-card:hover::before {
  opacity: 1;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 40px rgba(118, 75, 162, 0.4);
}

.stat-icon {
  font-size: 2rem;
}

.stat-content h4 {
  margin: 0 0 5px 0;
  color: white;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.stat-count {
  color: rgba(255, 255, 255, 0.9);
  font-weight: bold;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

/* Memory List */
.memory-list {
  margin-bottom: 30px;
  animation: fadeInUp 0.8s ease;
}

.memory-section {
  margin-bottom: 25px;
}

.memory-section h3 {
  color: white;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 2px solid rgba(255, 255, 255, 0.1);
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.memory-items {
  display: grid;
  gap: 15px;
}

.memory-item {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border-radius: 16px;
  padding: 15px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  color: white;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  animation: fadeInUp 0.5s ease forwards;
  opacity: 0;
  position: relative;
  overflow: hidden;
}

.memory-item::before {
  content: '';
  position: absolute;
  top: -2px;
  left: -2px;
  right: -2px;
  bottom: -2px;
  background: linear-gradient(45deg, rgba(118, 75, 162, 0.2), rgba(200, 100, 200, 0.2), rgba(118, 75, 162, 0.2));
  z-index: -1;
  border-radius: 18px;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.memory-item:hover::before {
  opacity: 1;
}

.memory-item:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 40px rgba(118, 75, 162, 0.4);
}

.memory-content {
  flex: 1;
}

.memory-content strong {
  color: white;
  display: block;
  margin-bottom: 8px;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.memory-content p {
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 10px;
  line-height: 1.5;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.memory-meta {
  display: flex;
  gap: 15px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.confidence {
  background: rgba(39, 174, 96, 0.2);
  color: rgba(255, 255, 255, 0.9);
  padding: 2px 6px;
  border-radius: 4px;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

/* Edit Form */
.memory-edit-form {
  flex: 1;
  margin-right: 10px;
}

.edit-input,
.edit-textarea {
  width: 100%;
  padding: 12px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  margin-bottom: 10px;
  color: white;
  font-family: 'Roboto', sans-serif;
  font-size: 14px;
  transition: all 0.3s ease;
  box-sizing: border-box; /* Ensure padding is included in width */
}

.edit-input:focus,
.edit-textarea:focus {
  outline: none;
  border-color: rgba(118, 75, 162, 0.5);
  box-shadow: 0 0 0 2px rgba(118, 75, 162, 0.3);
  background: rgba(255, 255, 255, 0.15);
}

.edit-input::placeholder,
.edit-textarea::placeholder {
  color: rgba(255, 255, 255, 0.6);
}

.edit-textarea {
  resize: vertical;
  min-height: 80px;
}

.edit-actions {
  display: flex;
  gap: 10px;
}

.save-btn,
.cancel-btn {
  padding: 8px 15px;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  font-size: 14px;
  font-weight: bold;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  color: white;
  z-index: 1;
  flex: 1; /* Make buttons share space equally */
}

.save-btn::before,
.cancel-btn::before {
  content: '';
  position: absolute;
  top: -2px;
  left: -2px;
  right: -2px;
  bottom: -2px;
  background: linear-gradient(45deg, rgba(255, 255, 255, 0.2), rgba(255, 255, 255, 0.4), rgba(255, 255, 255, 0.2));
  z-index: -1;
  border-radius: 12px;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.save-btn:hover::before,
.cancel-btn:hover::before {
  opacity: 1;
}

.save-btn {
  background: linear-gradient(120deg, rgba(40, 167, 69, 0.8), rgba(30, 120, 50, 0.8));
  box-shadow: 0 4px 12px rgba(40, 167, 69, 0.3);
}

.save-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(40, 167, 69, 0.4);
}

.cancel-btn {
  background: linear-gradient(120deg, rgba(220, 53, 69, 0.8), rgba(180, 40, 50, 0.8));
  box-shadow: 0 4px 12px rgba(220, 53, 69, 0.3);
}

.cancel-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(220, 53, 69, 0.4);
}

/* Memory Actions */
.memory-actions {
  display: flex;
  flex-direction: column;
  gap: 5px;
  margin-left: 10px; /* Add space between content and actions */
}

.edit-btn,
.delete-btn {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  cursor: pointer;
  font-size: 16px;
  padding: 8px;
  border-radius: 8px;
  transition: all 0.3s ease;
  color: white;
  backdrop-filter: blur(10px);
  position: relative;
  overflow: hidden;
  z-index: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 40px; /* Ensure consistent button size */
  height: 40px;
}

.edit-btn::before,
.delete-btn::before {
  content: '';
  position: absolute;
  top: -2px;
  left: -2px;
  right: -2px;
  bottom: -2px;
  background: linear-gradient(45deg, rgba(255, 255, 255, 0.2), rgba(255, 255, 255, 0.4), rgba(255, 255, 255, 0.2));
  z-index: -1;
  border-radius: 10px;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.edit-btn:hover::before,
.delete-btn:hover::before {
  opacity: 1;
}

.edit-btn:hover {
  background: rgba(52, 152, 219, 0.3);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(52, 152, 219, 0.3);
}

.delete-btn:hover {
  background: rgba(231, 76, 60, 0.3);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(231, 76, 60, 0.3);
}

/* No Memories Message */
.no-memories {
  text-align: center;
  padding: 40px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  color: rgba(255, 255, 255, 0.8);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

/* Status Message */
.status-message {
  padding: 15px;
  border-radius: 8px;
  margin-top: 20px;
  text-align: center;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.status-message.success {
  background: rgba(40, 167, 69, 0.2);
  border: 1px solid rgba(40, 167, 69, 0.3);
}

.status-message.error {
  background: rgba(220, 53, 69, 0.2);
  border: 1px solid rgba(220, 53, 69, 0.3);
}
</style>