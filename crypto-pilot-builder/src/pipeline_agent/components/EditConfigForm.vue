<template>
  <form @submit.prevent="saveConfig" class="edit-config-form">
    <div class="form-group">
      <label>Activer l'autowallet</label>
      <input type="checkbox" v-model="editedConfig.is_active" />
    </div>
    
    <div class="form-group">
      <label>Intervalle d'analyse (minutes)</label>
      <select v-model="editedConfig.analysis_interval">
        <option value="5">5 minutes</option>
        <option value="15">15 minutes</option>
        <option value="30">30 minutes</option>
        <option value="60">1 heure</option>
      </select>
    </div>
    
    <div class="form-group">
      <label>Montant maximum par trade (USD)</label>
      <input type="number" v-model="editedConfig.max_investment_per_trade" min="10" step="10" />
    </div>
    
    <div class="form-group">
      <label>Tolérance au risque</label>
      <select v-model="editedConfig.risk_tolerance">
        <option value="low">Faible</option>
        <option value="medium">Moyenne</option>
        <option value="high">Élevée</option>
      </select>
    </div>
    
    <div class="form-group">
      <label>Stratégie d'investissement</label>
      <select v-model="editedConfig.investment_strategy">
        <option value="conservative">Conservatrice</option>
        <option value="balanced">Équilibrée</option>
        <option value="aggressive">Agressive</option>
      </select>
    </div>
    
    <div class="form-group">
      <label>Seuil de confiance minimum (%)</label>
      <input type="number" v-model="editedConfig.min_confidence_threshold" min="50" max="95" step="5" />
    </div>
    
    <div class="form-group">
      <label>Cryptomonnaies autorisées</label>
      <div class="crypto-list">
        <label v-for="crypto in availableCryptos" :key="crypto" class="crypto-checkbox">
          <input type="checkbox" :value="crypto" v-model="editedConfig.crypto_whitelist" />
          {{ crypto }}
        </label>
      </div>
    </div>
    
    <div class="form-actions">
      <button type="button" @click="$emit('cancel')" class="btn btn-secondary">
        Annuler
      </button>
      <button type="submit" class="btn btn-primary" :disabled="isLoading">
        {{ isLoading ? 'Sauvegarde...' : 'Sauvegarder' }}
      </button>
    </div>
  </form>
</template>

<script>
import { ref, onMounted } from 'vue'

export default {
  name: 'EditConfigForm',
  props: {
    config: {
      type: Object,
      required: true
    }
  },
  emits: ['save', 'cancel'],
  setup(props, { emit }) {
    const editedConfig = ref({})
    const isLoading = ref(false)
    
    const availableCryptos = [
      'BTC', 'ETH', 'ADA', 'DOT', 'SOL', 'MATIC', 'AVAX', 'UNI', 'LINK',
      'BNB', 'XRP', 'DOGE', 'SHIB', 'LTC', 'BCH', 'XLM', 'VET', 'TRX'
    ]
    
    onMounted(() => {
      // Copier la configuration actuelle
      editedConfig.value = {
        is_active: props.config.is_active,
        analysis_interval: props.config.analysis_interval,
        max_investment_per_trade: props.config.max_investment_per_trade,
        risk_tolerance: props.config.risk_tolerance,
        investment_strategy: props.config.investment_strategy,
        min_confidence_threshold: props.config.min_confidence_threshold,
        crypto_whitelist: [...props.config.crypto_whitelist]
      }
    })
    
    const saveConfig = async () => {
      isLoading.value = true
      try {
        // Convertir le seuil de confiance en décimal
        const configToSave = {
          ...editedConfig.value,
          min_confidence_threshold: editedConfig.value.min_confidence_threshold / 100
        }
        
        emit('save', configToSave)
      } catch (error) {
        console.error('Erreur lors de la sauvegarde:', error)
      } finally {
        isLoading.value = false
      }
    }
    
    return {
      editedConfig,
      isLoading,
      availableCryptos,
      saveConfig
    }
  }
}
</script>

<style scoped>
.edit-config-form {
  display: grid;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-weight: 600;
  color: #34495e;
}

.form-group input,
.form-group select {
  padding: 12px;
  border: 2px solid #e1e8ed;
  border-radius: 8px;
  font-size: 16px;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #3498db;
}

.crypto-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 12px;
}

.crypto-checkbox {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.form-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 20px;
}

.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: #3498db;
  color: white;
}

.btn-primary:hover {
  background: #2980b9;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  background: #95a5a6;
  color: white;
}

.btn-secondary:hover {
  background: #7f8c8d;
}
</style>
