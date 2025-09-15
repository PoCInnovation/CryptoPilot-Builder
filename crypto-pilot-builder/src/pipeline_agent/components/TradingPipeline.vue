<template>
  <div class="trading-pipeline-container">
    <div class="header">
      <h2>🚀 Pipeline de Trading Unifiée</h2>
      <p class="subtitle">Pipeline d'agents intégrée avec l'autowallet existant</p>
    </div>

    <!-- Statut de la pipeline -->
    <div class="status-card card">
      <h3>📊 Statut de la Pipeline</h3>
      <div class="status-grid">
        <div class="status-item">
          <span class="label">Statut:</span>
          <span :class="['status', pipelineStatus.is_running ? 'active' : 'inactive']">
            {{ pipelineStatus.is_running ? 'Active' : 'Inactive' }}
          </span>
        </div>
        <div class="status-item">
          <span class="label">Données de marché:</span>
          <span class="value">{{ pipelineStatus.market_data_count || 0 }}</span>
        </div>
        <div class="status-item">
          <span class="label">Prédictions:</span>
          <span class="value">{{ pipelineStatus.predictions_count || 0 }}</span>
        </div>
        <div class="status-item">
          <span class="label">Signaux:</span>
          <span class="value">{{ pipelineStatus.signals_count || 0 }}</span>
        </div>
        <div class="status-item">
          <span class="label">Trades actifs:</span>
          <span class="value">{{ pipelineStatus.trades_count || 0 }}</span>
        </div>
        <div class="status-item">
          <span class="label">Dernière mise à jour:</span>
          <span class="value">{{ formatTime(pipelineStatus.last_update) }}</span>
        </div>
      </div>
      
      <div class="actions">
        <button 
          @click="startPipeline" 
          class="btn btn-success" 
          :disabled="pipelineStatus.is_running || isLoading"
        >
          🚀 Démarrer la Pipeline
        </button>
        <button 
          @click="stopPipeline" 
          class="btn btn-warning" 
          :disabled="!pipelineStatus.is_running || isLoading"
        >
          ⏹️ Arrêter la Pipeline
        </button>
      </div>
    </div>

    <!-- Configuration de la pipeline -->
    <div class="config-card card">
      <h3>⚙️ Configuration de la Pipeline</h3>
      <div class="config-grid">
        <div class="config-item">
          <span class="label">Intervalle collecte:</span>
          <span class="value">{{ pipelineConfig.data_collection_interval }}s</span>
        </div>
        <div class="config-item">
          <span class="label">Intervalle prédictions:</span>
          <span class="value">{{ pipelineConfig.prediction_interval }}s</span>
        </div>
        <div class="config-item">
          <span class="label">Intervalle signaux:</span>
          <span class="value">{{ pipelineConfig.signal_generation_interval }}s</span>
        </div>
        <div class="config-item">
          <span class="label">Intervalle trades:</span>
          <span class="value">{{ pipelineConfig.trade_execution_interval }}s</span>
        </div>
        <div class="config-item">
          <span class="label">Trades max concurrents:</span>
          <span class="value">{{ pipelineConfig.max_concurrent_trades }}</span>
        </div>
        <div class="config-item">
          <span class="label">Seuil confiance min:</span>
          <span class="value">{{ Math.round(pipelineConfig.min_confidence_threshold * 100) }}%</span>
        </div>
      </div>
      
      <div class="risk-management">
        <h4>🎯 Gestion des Risques</h4>
        <div class="risk-grid">
          <div class="risk-item">
            <span class="label">Taille position max:</span>
            <span class="value">{{ Math.round(pipelineConfig.risk_management.max_position_size * 100) }}%</span>
          </div>
          <div class="risk-item">
            <span class="label">Perte quotidienne max:</span>
            <span class="value">{{ Math.round(pipelineConfig.risk_management.max_daily_loss * 100) }}%</span>
          </div>
          <div class="risk-item">
            <span class="label">Stop loss:</span>
            <span class="value">{{ Math.round(pipelineConfig.risk_management.stop_loss_percentage * 100) }}%</span>
          </div>
          <div class="risk-item">
            <span class="label">Take profit:</span>
            <span class="value">{{ Math.round(pipelineConfig.risk_management.take_profit_percentage * 100) }}%</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Actions manuelles -->
    <div class="actions-card card">
      <h3>🔧 Actions Manuelles</h3>
      <p class="info-text">
        Ces actions permettent de forcer l'exécution des étapes de la pipeline pour des tests ou des ajustements.
      </p>
      
      <div class="actions-grid">
        <button @click="forceDataCollection" class="btn btn-secondary" :disabled="isLoading">
          📊 Collecter les Données
        </button>
        <button @click="forcePredictionGeneration" class="btn btn-secondary" :disabled="isLoading">
          🔮 Générer Prédictions
        </button>
        <button @click="forceSignalGeneration" class="btn btn-secondary" :disabled="isLoading">
          📈 Générer Signaux
        </button>
        <button @click="forceTradeExecution" class="btn btn-secondary" :disabled="isLoading">
          💼 Exécuter Trades
        </button>
        <button @click="clearPipelineCache" class="btn btn-warning" :disabled="isLoading">
          🗑️ Vider le Cache
        </button>
      </div>
    </div>

    <!-- Données en temps réel -->
    <div class="data-section">
      <!-- Données de marché -->
      <div class="data-card card">
        <h3>📊 Données de Marché</h3>
        <div class="data-list" v-if="marketData && Object.keys(marketData).length > 0">
          <div v-for="(data, symbol) in marketData" :key="symbol" class="data-item">
            <div class="data-header">
              <span class="symbol">{{ symbol }}</span>
              <span class="price">${{ data.price?.toFixed(2) || 'N/A' }}</span>
            </div>
            <div class="data-details">
              <span class="sentiment" :class="getSentimentClass(data.news_sentiment)">
                Sentiment: {{ formatSentiment(data.news_sentiment) }}
              </span>
              <span class="volume">Volume: {{ formatVolume(data.volume) }}</span>
              <span class="time">{{ formatTime(data.timestamp) }}</span>
            </div>
          </div>
        </div>
        <div v-else class="no-data">
          <p>Aucune donnée de marché disponible</p>
        </div>
      </div>

      <!-- Prédictions -->
      <div class="data-card card">
        <h3>🔮 Prédictions de Trading</h3>
        <div class="data-list" v-if="predictions && Object.keys(predictions).length > 0">
          <div v-for="(pred, symbol) in predictions" :key="symbol" class="data-item">
            <div class="data-header">
              <span class="symbol">{{ symbol }}</span>
              <span class="direction" :class="getDirectionClass(pred.direction_prob)">
                {{ getDirectionLabel(pred.direction_prob) }}
              </span>
            </div>
            <div class="data-details">
              <span class="confidence">{{ Math.round(pred.confidence * 100) }}% confiance</span>
              <span class="volatility">Volatilité: {{ Math.round(pred.volatility * 100) }}%</span>
              <span class="reasoning">{{ pred.reasoning }}</span>
            </div>
          </div>
        </div>
        <div v-else class="no-data">
          <p>Aucune prédiction disponible</p>
        </div>
      </div>

      <!-- Signaux de trading -->
      <div class="data-card card">
        <h3>📈 Signaux de Trading</h3>
        <div class="data-list" v-if="signals && Object.keys(signals).length > 0">
          <div v-for="(signal, symbol) in signals" :key="symbol" class="data-item">
            <div class="data-header">
              <span class="symbol">{{ symbol }}</span>
              <span :class="['signal-type', signal.signal_type.toLowerCase()]">
                {{ signal.signal_type }}
              </span>
            </div>
            <div class="data-details">
              <span class="confidence">{{ Math.round(signal.confidence * 100) }}% confiance</span>
              <span class="price">Prix: ${{ signal.price?.toFixed(2) }}</span>
              <span class="position">Position: {{ Math.round(signal.position_size * 100) }}%</span>
            </div>
            <div class="signal-reasoning">
              <p>{{ signal.reasoning }}</p>
            </div>
          </div>
        </div>
        <div v-else class="no-data">
          <p>Aucun signal de trading disponible</p>
        </div>
      </div>

      <!-- Trades exécutés -->
      <div class="data-card card">
        <h3>💼 Trades Exécutés</h3>
        <div class="data-list" v-if="trades && Object.keys(trades).length > 0">
          <div v-for="(trade, symbol) in trades" :key="symbol" class="data-item">
            <div class="data-header">
              <span class="symbol">{{ symbol }}</span>
              <span :class="['trade-type', trade.signal_type.toLowerCase()]">
                {{ trade.signal_type }}
              </span>
            </div>
            <div class="data-details">
              <span class="quantity">Quantité: {{ trade.quantity }}</span>
              <span class="price">Prix: ${{ trade.price?.toFixed(2) }}</span>
              <span class="status" :class="trade.status">{{ trade.status }}</span>
            </div>
            <div class="trade-pnl" v-if="trade.pnl">
              <span class="pnl" :class="trade.pnl > 0 ? 'positive' : 'negative'">
                P&L: ${{ trade.pnl.toFixed(2) }}
              </span>
            </div>
          </div>
        </div>
        <div v-else class="no-data">
          <p>Aucun trade exécuté</p>
        </div>
      </div>
    </div>

    <!-- Statistiques -->
    <div class="stats-card card">
      <h3>📈 Statistiques de la Pipeline</h3>
      <div class="stats-grid">
        <div class="stat-item">
          <span class="label">Total signaux:</span>
          <span class="value">{{ pipelineStats.total_signals || 0 }}</span>
        </div>
        <div class="stat-item">
          <span class="label">Total trades:</span>
          <span class="value">{{ pipelineStats.total_trades || 0 }}</span>
        </div>
        <div class="stat-item">
          <span class="label">Trades réussis:</span>
          <span class="value">{{ pipelineStats.successful_trades || 0 }}</span>
        </div>
        <div class="stat-item">
          <span class="label">P&L total:</span>
          <span class="value" :class="getPnlClass(pipelineStats.total_pnl)">
            ${{ pipelineStats.total_pnl?.toFixed(2) || '0.00' }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import apiService from '../services/apiService'

export default {
  name: 'TradingPipeline',
  setup() {
    const pipelineStatus = ref({})
    const pipelineConfig = ref({})
    const pipelineStats = ref({})
    const marketData = ref({})
    const predictions = ref({})
    const signals = ref({})
    const trades = ref({})
    const isLoading = ref(false)

    // Charger le statut de la pipeline
    const loadPipelineStatus = async () => {
      try {
        const response = await apiService.request('/api/trading-pipeline/status')
        if (response.success) {
          pipelineStatus.value = response.status
          pipelineConfig.value = response.status.config || {}
          pipelineStats.value = response.status.stats || {}
        }
      } catch (error) {
        console.error('Erreur lors du chargement du statut:', error)
      }
    }

    // Charger les données de marché
    const loadMarketData = async () => {
      try {
        const response = await apiService.request('/api/trading-pipeline/market-data')
        if (response.success) {
          marketData.value = response.market_data || {}
        }
      } catch (error) {
        console.error('Erreur lors du chargement des données de marché:', error)
      }
    }

    // Charger les prédictions
    const loadPredictions = async () => {
      try {
        const response = await apiService.request('/api/trading-pipeline/predictions')
        if (response.success) {
          predictions.value = response.predictions || {}
        }
      } catch (error) {
        console.error('Erreur lors du chargement des prédictions:', error)
      }
    }

    // Charger les signaux
    const loadSignals = async () => {
      try {
        const response = await apiService.request('/api/trading-pipeline/signals')
        if (response.success) {
          signals.value = response.signals || {}
        }
      } catch (error) {
        console.error('Erreur lors du chargement des signaux:', error)
      }
    }

    // Charger les trades
    const loadTrades = async () => {
      try {
        const response = await apiService.request('/api/trading-pipeline/trades')
        if (response.success) {
          trades.value = response.trades || {}
        }
      } catch (error) {
        console.error('Erreur lors du chargement des trades:', error)
      }
    }

    // Démarrer la pipeline
    const startPipeline = async () => {
      isLoading.value = true
      try {
        const response = await apiService.request('/api/trading-pipeline/start', {
          method: 'POST'
        })
        
        if (response.success) {
          await loadPipelineStatus()
        }
      } catch (error) {
        console.error('Erreur lors du démarrage de la pipeline:', error)
      } finally {
        isLoading.value = false
      }
    }

    // Arrêter la pipeline
    const stopPipeline = async () => {
      isLoading.value = true
      try {
        const response = await apiService.request('/api/trading-pipeline/stop', {
          method: 'POST'
        })
        
        if (response.success) {
          await loadPipelineStatus()
        }
      } catch (error) {
        console.error('Erreur lors de l\'arrêt de la pipeline:', error)
      } finally {
        isLoading.value = false
      }
    }

    // Actions manuelles
    const forceDataCollection = async () => {
      isLoading.value = true
      try {
        await apiService.request('/api/trading-pipeline/force-collect', { method: 'POST' })
        await loadMarketData()
      } catch (error) {
        console.error('Erreur lors de la collecte forcée:', error)
      } finally {
        isLoading.value = false
      }
    }

    const forcePredictionGeneration = async () => {
      isLoading.value = true
      try {
        await apiService.request('/api/trading-pipeline/force-predict', { method: 'POST' })
        await loadPredictions()
      } catch (error) {
        console.error('Erreur lors de la génération forcée:', error)
      } finally {
        isLoading.value = false
      }
    }

    const forceSignalGeneration = async () => {
      isLoading.value = true
      try {
        await apiService.request('/api/trading-pipeline/force-signals', { method: 'POST' })
        await loadSignals()
      } catch (error) {
        console.error('Erreur lors de la génération forcée:', error)
      } finally {
        isLoading.value = false
      }
    }

    const forceTradeExecution = async () => {
      isLoading.value = true
      try {
        await apiService.request('/api/trading-pipeline/force-execute', { method: 'POST' })
        await loadTrades()
      } catch (error) {
        console.error('Erreur lors de l\'exécution forcée:', error)
      } finally {
        isLoading.value = false
      }
    }

    const clearPipelineCache = async () => {
      isLoading.value = true
      try {
        await apiService.request('/api/trading-pipeline/clear-cache', { method: 'POST' })
        await loadPipelineStatus()
        await loadMarketData()
        await loadPredictions()
        await loadSignals()
        await loadTrades()
      } catch (error) {
        console.error('Erreur lors du vidage du cache:', error)
      } finally {
        isLoading.value = false
      }
    }

    // Charger toutes les données
    const loadAllData = async () => {
      await Promise.all([
        loadPipelineStatus(),
        loadMarketData(),
        loadPredictions(),
        loadSignals(),
        loadTrades()
      ])
    }

    // Utilitaires
    const formatTime = (timeStr) => {
      if (!timeStr) return 'N/A'
      return new Date(timeStr).toLocaleString('fr-FR')
    }

    const formatSentiment = (score) => {
      if (score > 0.3) return 'Positif'
      if (score < -0.3) return 'Négatif'
      return 'Neutre'
    }

    const getSentimentClass = (score) => {
      if (score > 0.3) return 'positive'
      if (score < -0.3) return 'negative'
      return 'neutral'
    }

    const formatVolume = (volume) => {
      if (!volume) return 'N/A'
      if (volume >= 1000000) return `${(volume / 1000000).toFixed(1)}M`
      if (volume >= 1000) return `${(volume / 1000).toFixed(1)}K`
      return volume.toFixed(0)
    }

    const getDirectionClass = (prob) => {
      if (prob > 0.6) return 'bullish'
      if (prob < 0.4) return 'bearish'
      return 'neutral'
    }

    const getDirectionLabel = (prob) => {
      if (prob > 0.6) return 'Hausse'
      if (prob < 0.4) return 'Baisse'
      return 'Stable'
    }

    const getPnlClass = (pnl) => {
      if (!pnl) return ''
      return pnl > 0 ? 'positive' : 'negative'
    }

    // Charger les données au montage
    onMounted(async () => {
      await loadAllData()
      
      // Actualiser les données toutes les 30 secondes
      setInterval(loadAllData, 30000)
    })

    return {
      pipelineStatus,
      pipelineConfig,
      pipelineStats,
      marketData,
      predictions,
      signals,
      trades,
      isLoading,
      startPipeline,
      stopPipeline,
      forceDataCollection,
      forcePredictionGeneration,
      forceSignalGeneration,
      forceTradeExecution,
      clearPipelineCache,
      formatTime,
      formatSentiment,
      getSentimentClass,
      formatVolume,
      getDirectionClass,
      getDirectionLabel,
      getPnlClass
    }
  }
}
</script>

<style scoped>
.trading-pipeline-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.header {
  text-align: center;
  margin-bottom: 30px;
}

.header h2 {
  color: #2c3e50;
  margin-bottom: 10px;
}

.subtitle {
  color: #7f8c8d;
  font-size: 1.1em;
}

.card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  border: 1px solid #e1e8ed;
}

.card h3, .card h4 {
  color: #2c3e50;
  margin-bottom: 16px;
}

.status-grid,
.config-grid,
.risk-grid,
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}

.status-item,
.config-item,
.risk-item,
.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
}

.label {
  font-weight: 600;
  color: #34495e;
}

.value {
  color: #2c3e50;
}

.status {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
}

.status.active {
  background: #d4edda;
  color: #155724;
}

.status.inactive {
  background: #f8d7da;
  color: #721c24;
}

.actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
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

.btn-secondary {
  background: #95a5a6;
  color: white;
}

.btn-secondary:hover {
  background: #7f8c8d;
}

.btn-success {
  background: #27ae60;
  color: white;
}

.btn-success:hover {
  background: #229954;
}

.btn-warning {
  background: #f39c12;
  color: white;
}

.btn-warning:hover {
  background: #e67e22;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.risk-management {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #e1e8ed;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
}

.info-text {
  color: #7f8c8d;
  margin-bottom: 20px;
  line-height: 1.6;
}

.data-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 24px;
  margin-bottom: 24px;
}

.data-card {
  min-height: 300px;
}

.data-list {
  max-height: 400px;
  overflow-y: auto;
}

.data-item {
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
  margin-bottom: 12px;
  border-left: 4px solid #3498db;
}

.data-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.symbol {
  font-weight: 600;
  color: #2c3e50;
}

.price {
  font-weight: 600;
  color: #27ae60;
}

.direction,
.signal-type,
.trade-type {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
  color: white;
}

.direction.bullish,
.signal-type.buy,
.trade-type.buy {
  background: #27ae60;
}

.direction.bearish,
.signal-type.sell,
.trade-type.sell {
  background: #e74c3c;
}

.direction.neutral,
.signal-type.hold,
.trade-type.hold {
  background: #f39c12;
}

.data-details {
  display: flex;
  gap: 16px;
  margin-bottom: 8px;
  flex-wrap: wrap;
  font-size: 14px;
}

.sentiment,
.confidence,
.volatility,
.volume,
.time,
.position,
.quantity,
.status {
  padding: 2px 8px;
  border-radius: 12px;
  background: #e1e8ed;
  color: #34495e;
}

.sentiment.positive {
  background: #d4edda;
  color: #155724;
}

.sentiment.negative {
  background: #f8d7da;
  color: #721c24;
}

.sentiment.neutral {
  background: #fff3cd;
  color: #856404;
}

.status.executed {
  background: #d4edda;
  color: #155724;
}

.status.pending {
  background: #fff3cd;
  color: #856404;
}

.status.failed {
  background: #f8d7da;
  color: #721c24;
}

.signal-reasoning,
.trade-reasoning {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid #e1e8ed;
}

.signal-reasoning p,
.trade-reasoning p {
  margin: 0;
  font-size: 14px;
  color: #34495e;
  line-height: 1.4;
}

.trade-pnl {
  margin-top: 8px;
}

.pnl {
  font-weight: 600;
  padding: 4px 8px;
  border-radius: 12px;
}

.pnl.positive {
  background: #d4edda;
  color: #155724;
}

.pnl.negative {
  background: #f8d7da;
  color: #721c24;
}

.no-data {
  text-align: center;
  padding: 40px;
  color: #7f8c8d;
}

@media (max-width: 768px) {
  .trading-pipeline-container {
    padding: 16px;
  }
  
  .card {
    padding: 16px;
  }
  
  .status-grid,
  .config-grid,
  .risk-grid,
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .data-section {
    grid-template-columns: 1fr;
  }
  
  .actions-grid {
    grid-template-columns: 1fr;
  }
  
  .data-details {
    flex-direction: column;
    gap: 8px;
  }
}
</style>
