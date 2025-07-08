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
.user-memory-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.memory-header {
  text-align: center;
  margin-bottom: 30px;
}

.memory-header h2 {
  color: #2c3e50;
  margin-bottom: 10px;
}

.memory-description {
  color: #7f8c8d;
  font-size: 16px;
}

.auth-required {
  text-align: center;
  padding: 40px;
  background: #fff3cd;
  border: 1px solid #ffeaa7;
  border-radius: 8px;
  color: #856404;
}

.auth-required h3 {
  color: #856404;
  margin-bottom: 15px;
}

.profile-summary {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 30px;
}

.profile-summary h3 {
  color: #2c3e50;
  margin-bottom: 15px;
}

.summary-content pre {
  background: white;
  padding: 15px;
  border-radius: 4px;
  white-space: pre-wrap;
  font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
  line-height: 1.5;
}

.memory-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 15px;
}

.stat-icon {
  font-size: 2rem;
}

.stat-content h4 {
  margin: 0 0 5px 0;
  color: #2c3e50;
}

.stat-count {
  color: #3498db;
  font-weight: bold;
}

.memory-list {
  margin-bottom: 30px;
}

.memory-section {
  margin-bottom: 25px;
}

.memory-section h3 {
  color: #2c3e50;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 2px solid #ecf0f1;
}

.memory-items {
  display: grid;
  gap: 15px;
}

.memory-item {
  background: white;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.memory-content {
  flex: 1;
}

.memory-content strong {
  color: #2c3e50;
  display: block;
  margin-bottom: 8px;
}

.memory-content p {
  color: #34495e;
  margin-bottom: 10px;
  line-height: 1.5;
}

.memory-meta {
  display: flex;
  gap: 15px;
  font-size: 12px;
  color: #7f8c8d;
}

.confidence {
  background: #e8f5e8;
  color: #27ae60;
  padding: 2px 6px;
  border-radius: 4px;
}

.memory-edit-form {
  flex: 1;
  margin-right: 10px;
}

.edit-input,
.edit-textarea {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  margin-bottom: 10px;
}

.edit-textarea {
  resize: vertical;
  min-height: 60px;
}

.edit-actions {
  display: flex;
  gap: 10px;
}

.save-btn,
.cancel-btn {
  padding: 5px 10px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

.save-btn {
  background: #28a745;
  color: white;
}

.cancel-btn {
  background: #dc3545;
  color: white;
}

.memory-actions {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.edit-btn,
.delete-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 16px;
  padding: 5px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.edit-btn:hover {
  background: #e3f2fd;
}

.delete-btn:hover {
  background: #fee;
}

.no-memories {
  text-align: center;
  padding: 40px;
  color: #7f8c8d;
}

.status-message {
  padding: 10px;
  border-radius: 4px;
  margin-top: 20px;
  text-align: center;
}

.status-message.success {
  background: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.status-message.error {
  background: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}
</style>
