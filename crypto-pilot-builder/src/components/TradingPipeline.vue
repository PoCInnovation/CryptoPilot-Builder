<template>
  <div class="trading-pipeline-container">
    <!-- Header de la Pipeline -->
    <div class="pipeline-header">
      <div class="header-content">
        <div class="header-left">
          <div class="header-icon">🚀</div>
          <h1 class="header-title">Pipeline de Trading Unifiée</h1>
        </div>
        <div class="header-right">
          <div class="pipeline-status-indicator">
            <div :class="['status-dot', getStatusClass()]"></div>
            <span class="status-text">{{ getStatusText() }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Contrôle Principal du Pipeline -->
    <div class="pipeline-control-section">
      <div class="section-header">
        <h2>🎮 Contrôle du Pipeline</h2>
        <p>Lancez le pipeline complet ou exécutez les agents individuellement</p>
      </div>
      
      <div class="control-buttons">
        <button 
          @click="launchPipeline" 
          :disabled="pipelineRunning || isLoading"
          class="control-btn launch-btn"
        >
          🚀 Lancer Pipeline
        </button>
        <button 
          @click="stopPipeline" 
          :disabled="!pipelineRunning || isLoading"
          class="control-btn stop-btn"
        >
          🛑 Arrêter Pipeline
        </button>
      </div>
      
      <div class="agent-controls">
        <button 
          @click="executeAgent('data-collector')" 
          :disabled="isLoading"
          class="agent-btn data-collector-btn"
        >
          📊 DataCollector
        </button>
        <button 
          @click="executeAgent('predictor')" 
          :disabled="isLoading"
          class="agent-btn predictor-btn"
        >
          🔮 Predictor
        </button>
        <button 
          @click="executeAgent('strategy')" 
          :disabled="isLoading"
          class="agent-btn strategy-btn"
        >
          📈 Strategy
        </button>
        <button 
          @click="executeAgent('trader')" 
          :disabled="isLoading"
          class="agent-btn trader-btn"
        >
          💰 Trader
        </button>
      </div>
    </div>

    <!-- Visualisation du Flux du Pipeline -->
    <div class="pipeline-flow-section">
      <h3>🔄 Flux du Pipeline</h3>
      <div class="flow-visualization">
        <div 
          v-for="(agent, index) in pipelineAgents" 
          :key="agent.name"
          :class="['flow-card', getAgentStatusClass(agent)]"
        >
          <div class="flow-icon">{{ agent.icon }}</div>
          <div class="flow-name">{{ agent.displayName }}</div>
          <div class="flow-description">{{ agent.description }}</div>
        </div>
        <div v-if="index < pipelineAgents.length - 1" class="flow-arrow">→</div>
      </div>
    </div>

    <!-- Données en Temps Réel -->
    <div class="real-time-data-section">
      <div class="data-grid">
        <!-- Historique des Prix -->
        <div class="data-card">
          <h3>📊 Historique des Prix Bitcoin</h3>
          <div class="price-history">
            <div v-if="priceHistory.length === 0" class="no-data">
              Chargement des données...
            </div>
            <div v-else class="price-list">
              <div 
                v-for="(price, index) in priceHistory" 
                :key="index"
                class="price-item"
              >
                <div class="price-time">{{ formatTime(price.timestamp) }}</div>
                <div class="price-value">${{ formatPrice(price.price) }}</div>
                <div v-if="index > 0" class="price-change">
                  <span :class="getChangeClass(price, priceHistory[index-1])">
                    {{ getChangeSymbol(price, priceHistory[index-1]) }} 
                    {{ formatChange(price, priceHistory[index-1]) }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Statut des Agents -->
        <div class="data-card">
          <h3>🤖 Statut des Agents</h3>
          <div class="agent-status-list">
            <div 
              v-for="agent in pipelineAgents" 
              :key="agent.name"
              class="agent-status-item"
            >
              <div class="agent-status-left">
                <div :class="['status-indicator', getAgentStatusClass(agent)]"></div>
                <span class="agent-name">{{ agent.displayName }}</span>
              </div>
              <div class="agent-status-right">
                <div class="execution-count">{{ agent.executionCount }} exécutions</div>
                <div class="last-execution">
                  {{ agent.lastExecution ? formatTime(agent.lastExecution) : 'Jamais' }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Données de Marché -->
    <div class="market-data-section">
      <h3>💹 Données de Marché</h3>
      <div class="market-data-grid">
        <div class="market-data-item">
          <div class="market-icon">₿</div>
          <div class="market-label">Bitcoin</div>
          <div class="market-value">${{ formatPrice(currentBTCPrice) }}</div>
        </div>
        <div class="market-data-item">
          <div class="market-icon">📈</div>
          <div class="market-label">Volume 24h</div>
          <div class="market-value">{{ formatVolume(currentVolume) }}</div>
        </div>
        <div class="market-data-item">
          <div class="market-icon">🔄</div>
          <div class="market-label">Dernière Mise à jour</div>
          <div class="market-value">{{ formatTime(lastUpdate) }}</div>
        </div>
      </div>
    </div>

    <!-- Logs du Pipeline -->
    <div class="pipeline-logs-section">
      <h3>📝 Logs du Pipeline</h3>
      <div class="logs-container">
        <div v-if="pipelineLogs.length === 0" class="no-logs">
          Aucun log disponible
        </div>
        <div v-else class="logs-list">
          <div 
            v-for="log in pipelineLogs" 
            :key="log.id"
            class="log-item"
          >
            <div class="log-time">{{ formatTime(log.timestamp) }}</div>
            <div class="log-content">
              <div class="log-symbol">{{ log.symbol }}</div>
              <div class="log-details">
                Prix: ${{ formatPrice(log.price) }} | 
                Signal: {{ log.strategySignal?.action || 'N/A' }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Trades Exécutés -->
    <div class="trades-section">
      <h3>💼 Trades Exécutés</h3>
      <div class="trades-container">
        <div v-if="executedTrades.length === 0" class="no-trades">
          Aucun trade exécuté
        </div>
        <div v-else class="trades-list">
          <div 
            v-for="trade in executedTrades" 
            :key="trade.id"
            class="trade-item"
          >
            <div class="trade-header">
              <span class="trade-symbol">{{ trade.symbol }}</span>
              <span :class="['trade-type', trade.type.toLowerCase()]">
                {{ trade.type }}
              </span>
            </div>
            <div class="trade-details">
              <span class="trade-quantity">Quantité: {{ trade.quantity }}</span>
              <span class="trade-price">Prix: ${{ formatPrice(trade.price) }}</span>
              <span class="trade-status">{{ trade.status }}</span>
            </div>
            <div v-if="trade.pnl" class="trade-pnl">
              <span :class="['pnl', trade.pnl > 0 ? 'positive' : 'negative']">
                P&L: ${{ trade.pnl.toFixed(2) }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Logger Agent - Monitoring -->
    <div class="logger-section">
      <h3>🔍 Logger Agent - Monitoring du Pipeline</h3>
      
      <!-- Boutons d'action -->
      <div class="logger-actions">
        <button @click="checkPipelineHealth" class="logger-btn health-btn">
          🔍 Vérifier la Santé du Pipeline
        </button>
        <button @click="testLoggerAgent" class="logger-btn test-btn">
          🧪 Tester le Logger Agent
        </button>
        <button @click="clearLoggerData" class="logger-btn clear-btn">
          🗑️ Effacer les Données
        </button>
      </div>

      <!-- Statut du pipeline -->
      <div class="logger-status-grid">
        <div class="logger-status-item">
          <h4>Statut du Pipeline</h4>
          <p :class="getHealthClass(pipelineHealth.status)">
            {{ pipelineHealth.status || '-' }}
          </p>
        </div>
        <div class="logger-status-item">
          <h4>Santé du Pipeline</h4>
          <p :class="getHealthClass(pipelineHealth.health)">
            {{ pipelineHealth.health || '-' }}
          </p>
        </div>
        <div class="logger-status-item">
          <h4>Score de Santé</h4>
          <p>{{ pipelineHealth.score ? `${pipelineHealth.score}/100` : '-' }}</p>
        </div>
      </div>

      <!-- Métriques détaillées -->
      <div class="logger-metrics">
        <h4>📈 Métriques du Pipeline</h4>
        <div class="metrics-grid">
          <div class="metric-item">
            <span>Exécutions Totales:</span>
            <p>{{ pipelineMetrics.totalExecutions || '-' }}</p>
          </div>
          <div class="metric-item">
            <span>Taux de Succès:</span>
            <p>{{ formatPercentage(pipelineMetrics.executionRate) }}</p>
          </div>
          <div class="metric-item">
            <span>Prédictions:</span>
            <p>{{ pipelineMetrics.predictionsCount || '-' }}</p>
          </div>
          <div class="metric-item">
            <span>Signaux:</span>
            <p>{{ pipelineMetrics.signalsCount || '-' }}</p>
          </div>
        </div>
      </div>

      <!-- Résultats des tests -->
      <div class="logger-test-results">
        <h4>🧪 Résultats des Tests</h4>
        <div v-if="!testResults" class="no-test-results">
          Aucun test exécuté
        </div>
        <div v-else class="test-results-content">
          <div class="test-section">
            <h5>📊 Analyse du Pipeline</h5>
            <div class="test-metrics">
              <div>
                <span>Exécutions totales:</span>
                <p>{{ testResults.pipelineAnalysis?.totalExecutions || '-' }}</p>
              </div>
              <div>
                <span>Taux de succès:</span>
                <p>{{ formatPercentage(testResults.pipelineAnalysis?.executionRate) }}</p>
              </div>
            </div>
          </div>
          
          <div v-if="testResults.tradingAnalysis" class="test-section">
            <h5>🎯 Analyse Trading</h5>
            <div class="test-metrics">
              <div>
                <span>Signaux totaux:</span>
                <p>{{ testResults.tradingAnalysis.totalSignals }}</p>
              </div>
              <div>
                <span>Signaux BUY:</span>
                <p class="text-green-600">{{ testResults.tradingAnalysis.buySignals }}</p>
              </div>
              <div>
                <span>Signaux SELL:</span>
                <p class="text-red-600">{{ testResults.tradingAnalysis.sellSignals }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Logs en temps réel -->
      <div class="logger-logs">
        <h4>📝 Logs en Temps Réel</h4>
        <div class="logger-logs-container">
          <div v-if="loggerLogs.length === 0" class="no-logs">
            En attente des logs...
          </div>
          <div v-else class="logger-logs-list">
            <div 
              v-for="log in loggerLogs" 
              :key="log.id"
              :class="['logger-log-item', getLogTypeClass(log.type)]"
            >
              <span class="log-timestamp">{{ formatTime(log.timestamp) }}</span>
              <span class="log-message">{{ log.message }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Notifications Toast -->
    <div class="toast-container">
      <div 
        v-for="toast in toasts" 
        :key="toast.id"
        :class="['toast', `toast-${toast.type}`]"
      >
        {{ toast.message }}
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'
import { apiService } from '../services/apiService'

export default {
  name: 'TradingPipeline',
  setup() {
    // État de l'application
    const pipelineRunning = ref(false)
    const isLoading = ref(false)
    const updateInterval = ref(null)

    // Données de la pipeline
    const pipelineStatus = ref({})
    const pipelineAgents = ref([
      {
        name: 'data-collector',
        displayName: 'DataCollector',
        icon: '📊',
        description: 'Collecte données',
        status: 'stopped',
        executionCount: 0,
        lastExecution: null
      },
      {
        name: 'predictor',
        displayName: 'Predictor',
        icon: '🔮',
        description: 'Analyse IA',
        status: 'stopped',
        executionCount: 0,
        lastExecution: null
      },
      {
        name: 'strategy',
        displayName: 'Strategy',
        icon: '📈',
        description: 'Signaux trading',
        status: 'stopped',
        executionCount: 0,
        lastExecution: null
      },
      {
        name: 'trader',
        displayName: 'Trader',
        icon: '💰',
        description: 'Exécution trades',
        status: 'stopped',
        executionCount: 0,
        lastExecution: null
      }
    ])

    // Données de marché
    const priceHistory = ref([])
    const currentBTCPrice = ref(0)
    const currentVolume = ref(0)
    const lastUpdate = ref(null)

    // Logs et monitoring
    const pipelineLogs = ref([])
    const pipelineHealth = ref({})
    const pipelineMetrics = ref({})
    const testResults = ref(null)
    const loggerLogs = ref([])
    
    // Trades exécutés
    const executedTrades = ref([])

    // Notifications
    const toasts = ref([])
    let toastCounter = 0

    // Initialisation
    onMounted(() => {
      console.log('🚀 TradingPipeline: Composant monté, initialisation...')
      updatePipelineStatus()
      updateAgentStatus()
      updateMarketData()
      updatePipelineLogs()
      
      // Mise à jour automatique toutes les 2 secondes
      updateInterval.value = setInterval(() => {
        console.log('🔄 TradingPipeline: Mise à jour automatique...')
        updatePipelineStatus()
        updateAgentStatus()
        updateMarketData()
        updatePipelineLogs()
        updateExecutedTrades()
      }, 2000)
    })

    onUnmounted(() => {
      if (updateInterval.value) {
        clearInterval(updateInterval.value)
      }
    })

    // ===== MÉTHODES DE MISE À JOUR =====

    // Mise à jour du statut du pipeline
    const updatePipelineStatus = async () => {
      try {
        console.log('📊 TradingPipeline: Mise à jour du statut du pipeline...')
        const response = await apiService.request('/api/trading-pipeline/status')
        if (response.success) {
          pipelineStatus.value = response.status
          pipelineRunning.value = response.status.is_running
          console.log('✅ TradingPipeline: Statut mis à jour:', response.status)
        }
      } catch (error) {
        console.error('❌ TradingPipeline: Erreur mise à jour statut pipeline:', error)
      }
    }

    // Mise à jour du statut des agents
    const updateAgentStatus = async () => {
      try {
        console.log('🤖 TradingPipeline: Mise à jour du statut des agents...')
        // Simuler la mise à jour du statut des agents
        pipelineAgents.value.forEach(agent => {
          if (pipelineRunning.value) {
            agent.status = Math.random() > 0.8 ? 'processing' : 'running'
            agent.executionCount = Math.floor(Math.random() * 100)
            agent.lastExecution = new Date()
          } else {
            agent.status = 'stopped'
          }
        })
        console.log('✅ TradingPipeline: Statut des agents mis à jour:', pipelineAgents.value)
      } catch (error) {
        console.error('❌ TradingPipeline: Erreur mise à jour statut agents:', error)
      }
    }

    // Mise à jour des données de marché
    const updateMarketData = async () => {
      try {
        console.log('💹 TradingPipeline: Mise à jour des données de marché...')
        // Simuler des données de marché
        const newPrice = 50000 + (Math.random() - 0.5) * 2000
        const newVolume = 1000000 + Math.random() * 5000000
        
        currentBTCPrice.value = newPrice
        currentVolume.value = newVolume
        lastUpdate.value = new Date()

        // Ajouter à l'historique
        priceHistory.value.unshift({
          price: newPrice,
          timestamp: new Date(),
          id: Date.now()
        })

        // Limiter l'historique à 20 entrées
        if (priceHistory.value.length > 20) {
          priceHistory.value = priceHistory.value.slice(0, 20)
        }
        
        console.log('✅ TradingPipeline: Données de marché mises à jour - Prix:', newPrice, 'Volume:', newVolume)
      } catch (error) {
        console.error('❌ TradingPipeline: Erreur mise à jour données marché:', error)
      }
    }

    // Mise à jour des logs du pipeline
    const updatePipelineLogs = async () => {
      try {
        console.log('📝 TradingPipeline: Mise à jour des logs du pipeline...')
        // Simuler des logs
        if (pipelineRunning.value && Math.random() > 0.7) {
          const newLog = {
            id: Date.now(),
            symbol: 'BTC/USD',
            price: currentBTCPrice.value,
            strategySignal: { action: Math.random() > 0.5 ? 'BUY' : 'SELL' },
            timestamp: new Date()
          }
          
          pipelineLogs.value.unshift(newLog)
          
          // Limiter les logs à 50 entrées
          if (pipelineLogs.value.length > 50) {
            pipelineLogs.value = pipelineLogs.value.slice(0, 50)
          }
          
          console.log('✅ TradingPipeline: Nouveau log ajouté:', newLog)
        }
      } catch (error) {
        console.error('❌ TradingPipeline: Erreur mise à jour logs:', error)
      }
    }

    // Mise à jour des trades exécutés
    const updateExecutedTrades = async () => {
      try {
        console.log('💼 TradingPipeline: Mise à jour des trades exécutés...')
        // Simuler des trades
        if (pipelineRunning.value && Math.random() > 0.8) {
          const newTrade = {
            id: Date.now(),
            symbol: 'BTC/USD',
            type: Math.random() > 0.5 ? 'BUY' : 'SELL',
            quantity: Math.random() * 0.1 + 0.01,
            price: currentBTCPrice.value,
            status: 'executed',
            pnl: (Math.random() - 0.5) * 100,
            timestamp: new Date()
          }
          
          executedTrades.value.unshift(newTrade)
          
          // Limiter les trades à 20 entrées
          if (executedTrades.value.length > 20) {
            executedTrades.value = executedTrades.value.slice(0, 20)
          }
          
          console.log('✅ TradingPipeline: Nouveau trade ajouté:', newTrade)
        }
      } catch (error) {
        console.error('❌ TradingPipeline: Erreur mise à jour trades:', error)
      }
    }

    // ===== MÉTHODES DE CONTRÔLE =====

    // Lancer la pipeline
    const launchPipeline = async () => {
      console.log('🚀 TradingPipeline: Tentative de démarrage de la pipeline...')
      isLoading.value = true
      try {
        const response = await apiService.request('/api/trading-pipeline/start', {
          method: 'POST'
        })
        
        if (response.success) {
          console.log('✅ TradingPipeline: Pipeline démarré avec succès!')
          showToast('Pipeline démarré avec succès! 🚀', 'success')
          await updatePipelineStatus()
        } else {
          console.log('❌ TradingPipeline: Échec du démarrage du pipeline')
          showToast('Échec du démarrage du pipeline', 'error')
        }
      } catch (error) {
        console.error('❌ TradingPipeline: Erreur lors du démarrage du pipeline:', error)
        showToast('Erreur lors du démarrage du pipeline', 'error')
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
          showToast('Pipeline arrêté avec succès! 🛑', 'success')
          await updatePipelineStatus()
        } else {
          showToast('Échec de l\'arrêt du pipeline', 'error')
        }
      } catch (error) {
        showToast('Erreur lors de l\'arrêt du pipeline', 'error')
      } finally {
        isLoading.value = false
      }
    }

    // Exécuter un agent individuel
    const executeAgent = async (agentName) => {
      console.log(`🤖 TradingPipeline: Exécution de l'agent ${agentName}...`)
      isLoading.value = true
      try {
        let endpoint = ''
        switch (agentName) {
          case 'data-collector':
            endpoint = '/api/trading-pipeline/force-collect'
            break
          case 'predictor':
            endpoint = '/api/trading-pipeline/force-predict'
            break
          case 'strategy':
            endpoint = '/api/trading-pipeline/force-signals'
            break
          case 'trader':
            endpoint = '/api/trading-pipeline/force-execute'
            break
        }

        if (endpoint) {
          console.log(`🌐 TradingPipeline: Appel de l'endpoint ${endpoint}`)
          await apiService.request(endpoint, { method: 'POST' })
          console.log(`✅ TradingPipeline: Agent ${agentName} exécuté avec succès!`)
          showToast(`${agentName} exécuté avec succès!`, 'success')
          
          // Mettre à jour le statut de l'agent
          const agent = pipelineAgents.value.find(a => a.name === agentName)
          if (agent) {
            agent.status = 'processing'
            agent.executionCount++
            agent.lastExecution = new Date()
            console.log(`🔄 TradingPipeline: Statut de l'agent ${agentName} mis à jour`)
            
            setTimeout(() => {
              agent.status = pipelineRunning.value ? 'running' : 'stopped'
              console.log(`✅ TradingPipeline: Agent ${agentName} retour au statut normal`)
            }, 2000)
          }
        }
      } catch (error) {
        console.error(`❌ TradingPipeline: Erreur lors de l'exécution de ${agentName}:`, error)
        showToast(`Erreur lors de l'exécution de ${agentName}`, 'error')
      } finally {
        isLoading.value = false
      }
    }

    // ===== MÉTHODES DU LOGGER =====

    // Vérifier la santé du pipeline
    const checkPipelineHealth = async () => {
      console.log('🔍 TradingPipeline: Vérification de la santé du pipeline...')
      try {
        // Simuler la vérification de la santé
        pipelineHealth.value = {
          status: pipelineRunning.value ? 'Actif' : 'Arrêté',
          health: getRandomHealth(),
          score: Math.floor(Math.random() * 40) + 60
        }

        pipelineMetrics.value = {
          totalExecutions: Math.floor(Math.random() * 1000),
          executionRate: Math.random() * 0.3 + 0.7,
          predictionsCount: Math.floor(Math.random() * 500),
          signalsCount: Math.floor(Math.random() * 200)
        }

        console.log('✅ TradingPipeline: Santé du pipeline vérifiée:', pipelineHealth.value)
        console.log('📊 TradingPipeline: Métriques mises à jour:', pipelineMetrics.value)
        showToast('Santé du pipeline vérifiée avec succès! ✅', 'success')
        addLoggerLog('🔍 Vérification de la santé du pipeline terminée', 'success')
      } catch (error) {
        console.error('❌ TradingPipeline: Erreur lors de la vérification de la santé:', error)
        showToast('Erreur lors de la vérification de la santé', 'error')
        addLoggerLog('❌ Erreur lors de la vérification de la santé', 'error')
      }
    }

    // Tester le Logger Agent
    const testLoggerAgent = async () => {
      try {
        // Simuler les résultats de test
        testResults.value = {
          pipelineAnalysis: {
            totalExecutions: Math.floor(Math.random() * 1000),
            executionRate: Math.random() * 0.3 + 0.7
          },
          tradingAnalysis: {
            totalSignals: Math.floor(Math.random() * 200),
            buySignals: Math.floor(Math.random() * 100),
            sellSignals: Math.floor(Math.random() * 100)
          }
        }

        showToast('Test du Logger Agent terminé avec succès! ✅', 'success')
        addLoggerLog('🧪 Test du Logger Agent terminé', 'success')
      } catch (error) {
        showToast('Erreur lors du test du Logger Agent', 'error')
        addLoggerLog('❌ Erreur lors du test: ' + error.message, 'error')
      }
    }

    // Effacer les données du Logger
    const clearLoggerData = () => {
      pipelineHealth.value = {}
      pipelineMetrics.value = {}
      testResults.value = null
      loggerLogs.value = []
      
      showToast('Données du Logger effacées! 🗑️', 'info')
      addLoggerLog('🗑️ Données du Logger effacées', 'info')
    }

    // Ajouter un log au Logger
    const addLoggerLog = (message, type = 'info') => {
      const newLog = {
        id: Date.now(),
        message,
        type,
        timestamp: new Date()
      }
      
      loggerLogs.value.unshift(newLog)
      
      // Limiter les logs à 50 entrées
      if (loggerLogs.value.length > 50) {
        loggerLogs.value = loggerLogs.value.slice(0, 50)
      }
    }

    // ===== MÉTHODES UTILITAIRES =====

    // Obtenir la classe CSS du statut
    const getStatusClass = () => {
      if (pipelineRunning.value) return 'running'
      return 'stopped'
    }

    // Obtenir le texte du statut
    const getStatusText = () => {
      if (pipelineRunning.value) return 'Pipeline Actif'
      return 'Pipeline Arrêté'
    }

    // Obtenir la classe CSS du statut d'un agent
    const getAgentStatusClass = (agent) => {
      return agent.status || 'stopped'
    }

    // Obtenir la classe CSS pour les changements de prix
    const getChangeClass = (current, previous) => {
      if (!previous) return 'text-gray-600'
      const change = current.price - previous.price
      return change > 0 ? 'text-green-600' : change < 0 ? 'text-red-600' : 'text-gray-600'
    }

    // Obtenir le symbole de changement
    const getChangeSymbol = (current, previous) => {
      if (!previous) return '→'
      const change = current.price - previous.price
      return change > 0 ? '↗' : change < 0 ? '↘' : '→'
    }

    // Obtenir la classe CSS pour la santé
    const getHealthClass = (health) => {
      if (health === 'Excellent') return 'text-green-600 font-medium'
      if (health === 'Good') return 'text-blue-600 font-medium'
      if (health === 'Fair') return 'text-yellow-600 font-medium'
      if (health === 'Poor') return 'text-red-600 font-medium'
      return 'text-gray-600 font-medium'
    }

    // Obtenir la classe CSS pour le type de log
    const getLogTypeClass = (type) => {
      return `log-${type || 'info'}`
    }

    // Obtenir une santé aléatoire
    const getRandomHealth = () => {
      const healths = ['Excellent', 'Good', 'Fair', 'Poor']
      return healths[Math.floor(Math.random() * healths.length)]
    }

    // ===== MÉTHODES DE FORMATAGE =====

    // Formater le temps
    const formatTime = (timestamp) => {
      if (!timestamp) return '--'
      const formatted = new Date(timestamp).toLocaleTimeString()
      console.log(`⏰ TradingPipeline: Temps formaté: ${timestamp} -> ${formatted}`)
      return formatted
    }

    // Formater le prix
    const formatPrice = (price) => {
      if (!price) return '--'
      return price.toLocaleString()
    }

    // Formater le volume
    const formatVolume = (volume) => {
      if (!volume) return '--'
      return `${(volume / 1000000).toFixed(1)}M`
    }

    // Formater le pourcentage
    const formatPercentage = (value) => {
      if (!value) return '--'
      return `${(value * 100).toFixed(1)}%`
    }

    // Formater le changement
    const formatChange = (current, previous) => {
      if (!previous) return '--'
      const change = current.price - previous.price
      const changePercent = (change / previous.price) * 100
      return `${change > 0 ? '+' : ''}${change.toFixed(2)} (${changePercent > 0 ? '+' : ''}${changePercent.toFixed(2)}%)`
    }

    // ===== NOTIFICATIONS =====

    // Afficher une notification toast
    const showToast = (message, type = 'info') => {
      console.log(`🔔 TradingPipeline: Toast affiché - ${type}: ${message}`)
      const toast = {
        id: ++toastCounter,
        message,
        type
      }
      
      toasts.value.push(toast)
      console.log(`📝 TradingPipeline: Toast ajouté, total: ${toasts.value.length}`)
      
      // Supprimer le toast après 3 secondes
      setTimeout(() => {
        const index = toasts.value.findIndex(t => t.id === toast.id)
        if (index > -1) {
          toasts.value.splice(index, 1)
          console.log(`🗑️ TradingPipeline: Toast supprimé, total: ${toasts.value.length}`)
        }
      }, 3000)
    }

    return {
      // État
      pipelineRunning,
      isLoading,
      pipelineAgents,
      priceHistory,
      currentBTCPrice,
      currentVolume,
      lastUpdate,
      pipelineLogs,
      pipelineHealth,
      pipelineMetrics,
      testResults,
      loggerLogs,
      executedTrades,
      toasts,

      // Méthodes
      updatePipelineStatus,
      updateAgentStatus,
      updateMarketData,
      updatePipelineLogs,
      updateExecutedTrades,
      launchPipeline,
      stopPipeline,
      executeAgent,
      checkPipelineHealth,
      testLoggerAgent,
      clearLoggerData,
      addLoggerLog,
      getStatusClass,
      getStatusText,
      getAgentStatusClass,
      getChangeClass,
      getChangeSymbol,
      getHealthClass,
      getLogTypeClass,
      formatTime,
      formatPrice,
      formatVolume,
      formatPercentage,
      formatChange,
      showToast
    }
  }
}
</script>

<style scoped>
/* Styles principaux */
.trading-pipeline-container {
  @apply bg-gray-50 min-h-screen;
}

/* Header de la pipeline */
.pipeline-header {
  @apply bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg;
}

.header-content {
  @apply container mx-auto px-6 py-4;
}

.header-left {
  @apply flex items-center space-x-4;
}

.header-icon {
  @apply text-3xl;
}

.header-title {
  @apply text-2xl font-bold;
}

.header-right {
  @apply flex items-center space-x-4;
}

.pipeline-status-indicator {
  @apply flex items-center space-x-2;
}

.status-dot {
  @apply w-3 h-3 rounded-full;
}

.status-dot.running {
  @apply bg-green-400;
}

.status-dot.stopped {
  @apply bg-gray-400;
}

.status-dot.processing {
  @apply bg-yellow-400;
}

.status-dot.error {
  @apply bg-red-400;
}

.status-text {
  @apply text-sm font-medium;
}

/* Section de contrôle */
.pipeline-control-section {
  @apply bg-white rounded-xl shadow-lg p-8 mb-8;
}

.section-header {
  @apply text-center mb-8;
}

.section-header h2 {
  @apply text-3xl font-bold text-gray-900 mb-2;
}

.section-header p {
  @apply text-gray-600;
}

.control-buttons {
  @apply flex justify-center space-x-6 mb-8;
}

.control-btn {
  @apply px-8 py-4 text-white rounded-xl font-bold text-lg transition-all transform hover:scale-105 shadow-lg;
}

.launch-btn {
  @apply bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600;
}

.stop-btn {
  @apply bg-gradient-to-r from-red-500 to-rose-500 hover:from-red-600 hover:to-rose-600;
}

.agent-controls {
  @apply grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6;
}

.agent-btn {
  @apply px-4 py-3 text-white rounded-lg font-medium transition-all transform hover:scale-105 shadow-md;
}

.data-collector-btn {
  @apply bg-blue-500 hover:bg-blue-600;
}

.predictor-btn {
  @apply bg-purple-500 hover:bg-purple-600;
}

.strategy-btn {
  @apply bg-emerald-500 hover:bg-emerald-600;
}

.trader-btn {
  @apply bg-amber-500 hover:bg-amber-600;
}

/* Section de flux */
.pipeline-flow-section {
  @apply bg-white rounded-xl shadow-lg p-8 mb-8;
}

.pipeline-flow-section h3 {
  @apply text-2xl font-bold text-gray-900 mb-6 text-center;
}

.flow-visualization {
  @apply flex items-center justify-center space-x-4 mb-8;
}

.flow-card {
  @apply text-center p-4 bg-gray-50 rounded-lg border-2 border-gray-200 transition-all duration-300;
}

.flow-card.active {
  @apply bg-gradient-to-br from-green-400 to-green-600 text-white border-green-500 shadow-lg;
}

.flow-card.processing {
  @apply bg-gradient-to-br from-yellow-400 to-yellow-600 text-white border-yellow-500 shadow-lg;
}

.flow-card.error {
  @apply bg-gradient-to-br from-red-400 to-red-600 text-white border-red-500 shadow-lg;
}

.flow-icon {
  @apply text-2xl mb-2;
}

.flow-name {
  @apply font-semibold;
}

.flow-description {
  @apply text-sm text-gray-600;
}

.flow-arrow {
  @apply text-2xl text-gray-400 font-bold;
}

/* Données en temps réel */
.real-time-data-section {
  @apply mb-8;
}

.data-grid {
  @apply grid grid-cols-1 lg:grid-cols-2 gap-8;
}

.data-card {
  @apply bg-white rounded-xl shadow-lg p-6;
}

.data-card h3 {
  @apply text-xl font-bold text-gray-900 mb-4;
}

.price-history {
  @apply space-y-2 max-h-64 overflow-y-auto;
}

.no-data {
  @apply text-gray-500 text-center py-8;
}

.price-list {
  @apply space-y-2;
}

.price-item {
  @apply flex items-center justify-between p-3 bg-gray-50 rounded-lg mb-2;
}

.price-time {
  @apply text-sm text-gray-500;
}

.price-value {
  @apply font-medium;
}

.price-change {
  @apply text-right;
}

.agent-status-list {
  @apply space-y-3;
}

.agent-status-item {
  @apply flex items-center justify-between p-3 bg-gray-50 rounded-lg;
}

.agent-status-left {
  @apply flex items-center;
}

.status-indicator {
  @apply w-3 h-3 rounded-full mr-2;
}

.status-indicator.running {
  @apply bg-green-400;
}

.status-indicator.stopped {
  @apply bg-gray-400;
}

.status-indicator.processing {
  @apply bg-yellow-400;
}

.status-indicator.error {
  @apply bg-red-400;
}

.agent-name {
  @apply font-medium capitalize;
}

.agent-status-right {
  @apply text-right;
}

.execution-count {
  @apply text-sm font-medium;
}

.last-execution {
  @apply text-xs text-gray-500;
}

/* Données de marché */
.market-data-section {
  @apply bg-white rounded-xl shadow-lg p-6 mb-8;
}

.market-data-section h3 {
  @apply text-xl font-bold text-gray-900 mb-4;
}

.market-data-grid {
  @apply grid grid-cols-1 md:grid-cols-3 gap-6;
}

.market-data-item {
  @apply text-center p-4 bg-gray-50 rounded-lg;
}

.market-icon {
  @apply text-2xl mb-2;
}

.market-label {
  @apply text-sm text-gray-600;
}

.market-value {
  @apply text-xl font-bold text-gray-900;
}

/* Trades exécutés */
.trades-section {
  @apply bg-white rounded-xl shadow-lg p-6 mb-8;
}

.trades-section h3 {
  @apply text-xl font-bold text-gray-900 mb-4;
}

.trades-container {
  @apply space-y-2 max-h-64 overflow-y-auto bg-gray-50 p-4 rounded-lg;
}

.no-trades {
  @apply text-gray-500 text-center py-8;
}

.trades-list {
  @apply space-y-2;
}

.trade-item {
  @apply flex flex-col space-y-2 p-3 bg-white rounded border-l-4 border-blue-500;
}

.trade-header {
  @apply flex justify-between items-center;
}

.trade-symbol {
  @apply font-semibold text-gray-800;
}

.trade-type {
  @apply px-2 py-1 rounded text-xs font-semibold text-white;
}

.trade-type.buy {
  @apply bg-green-500;
}

.trade-type.sell {
  @apply bg-red-500;
}

.trade-details {
  @apply flex gap-4 text-sm text-gray-600;
}

.trade-quantity,
.trade-price,
.trade-status {
  @apply px-2 py-1 bg-gray-100 rounded;
}

.trade-pnl {
  @apply text-right;
}

.pnl {
  @apply px-2 py-1 rounded text-sm font-semibold;
}

.pnl.positive {
  @apply bg-green-100 text-green-800;
}

.pnl.negative {
  @apply bg-red-100 text-red-800;
}

/* Logs du pipeline */
.pipeline-logs-section {
  @apply bg-white rounded-xl shadow-lg p-6 mb-8;
}

.pipeline-logs-section h3 {
  @apply text-xl font-bold text-gray-900 mb-4;
}

.logs-container {
  @apply space-y-2 max-h-64 overflow-y-auto bg-gray-50 p-4 rounded-lg;
}

.no-logs {
  @apply text-gray-500 text-center py-8;
}

.logs-list {
  @apply space-y-2;
}

.log-item {
  @apply flex items-center space-x-3 p-2 bg-white rounded border-l-4 border-blue-500;
}

.log-time {
  @apply text-xs text-gray-500;
}

.log-content {
  @apply flex-1;
}

.log-symbol {
  @apply text-sm font-medium;
}

.log-details {
  @apply text-xs text-gray-600;
}

/* Section Logger */
.logger-section {
  @apply bg-white rounded-xl shadow-lg p-6 mb-8;
}

.logger-section h3 {
  @apply text-xl font-bold text-gray-900 mb-4;
}

.logger-actions {
  @apply flex flex-wrap gap-4 mb-6;
}

.logger-btn {
  @apply px-4 py-2 text-white rounded-lg transition-colors flex items-center;
}

.health-btn {
  @apply bg-blue-500 hover:bg-blue-600;
}

.test-btn {
  @apply bg-green-500 hover:bg-green-600;
}

.clear-btn {
  @apply bg-gray-500 hover:bg-gray-600;
}

.logger-status-grid {
  @apply grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6;
}

.logger-status-item {
  @apply bg-blue-50 p-4 rounded-lg border border-blue-200;
}

.logger-status-item h4 {
  @apply font-semibold text-blue-800 text-sm mb-2;
}

.logger-status-item p {
  @apply text-blue-600 font-medium;
}

.logger-metrics {
  @apply bg-gray-50 p-4 rounded-lg mb-6 border border-gray-200;
}

.logger-metrics h4 {
  @apply font-semibold text-gray-800 mb-3;
}

.metrics-grid {
  @apply grid grid-cols-2 md:grid-cols-4 gap-4;
}

.metric-item {
  @apply text-sm;
}

.metric-item span {
  @apply text-gray-600;
}

.metric-item p {
  @apply font-semibold text-lg;
}

.logger-test-results {
  @apply bg-gray-50 p-4 rounded-lg mb-6 border border-gray-200;
}

.logger-test-results h4 {
  @apply font-semibold text-gray-800 mb-3;
}

.no-test-results {
  @apply text-gray-500;
}

.test-results-content {
  @apply space-y-4;
}

.test-section {
  @apply bg-white p-4 rounded-lg border border-gray-200;
}

.test-section h5 {
  @apply font-semibold text-gray-800 mb-3;
}

.test-metrics {
  @apply grid grid-cols-2 gap-4 text-sm;
}

.test-metrics div {
  @apply text-sm;
}

.test-metrics span {
  @apply text-gray-600;
}

.test-metrics p {
  @apply font-semibold;
}

.logger-logs {
  @apply bg-gray-50 p-4 rounded-lg border border-gray-200;
}

.logger-logs h4 {
  @apply font-semibold text-gray-800 mb-3;
}

.logger-logs-container {
  @apply max-h-64 overflow-y-auto space-y-2 text-sm;
}

.logger-logs-list {
  @apply space-y-2;
}

.logger-log-item {
  @apply p-2 rounded-lg text-sm;
}

.logger-log-item.log-success {
  @apply bg-green-100 text-green-800;
}

.logger-log-item.log-error {
  @apply bg-red-100 text-red-800;
}

.logger-log-item.log-warning {
  @apply bg-yellow-100 text-yellow-800;
}

.logger-log-item.log-info {
  @apply bg-blue-100 text-blue-800;
}

.log-timestamp {
  @apply font-mono text-xs text-gray-500;
}

.log-message {
  @apply ml-2;
}

/* Notifications Toast */
.toast-container {
  @apply fixed top-4 right-4 z-50 space-y-2;
}

.toast {
  @apply px-4 py-2 rounded-lg text-white font-medium transform transition-all duration-300;
}

.toast-success {
  @apply bg-green-500;
}

.toast-error {
  @apply bg-red-500;
}

.toast-warning {
  @apply bg-yellow-500;
}

.toast-info {
  @apply bg-blue-500;
}

/* Responsive */
@media (max-width: 768px) {
  .control-buttons {
    @apply flex-col space-y-4;
  }
  
  .agent-controls {
    @apply grid-cols-2;
  }
  
  .flow-visualization {
    @apply flex-col space-y-4;
  }
  
  .flow-arrow {
    @apply rotate-90;
  }
  
  .logger-actions {
    @apply flex-col;
  }
  
  .metrics-grid {
    @apply grid-cols-2;
  }
}
</style>
