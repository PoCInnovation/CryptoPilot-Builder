<template>
  <div class="autowallet-container">
    <div class="header">
      <h1>🤖 CryptoPilot AutoWallet</h1>
      <p class="subtitle">IA d'investissement automatique basée sur l'analyse des news crypto</p>
      <div class="header-actions">
        <router-link to="/pipeline-test" class="btn btn-outline">
          🧪 Tester la Pipeline
        </router-link>
      </div>
    </div>

    <!-- Configuration de l'autowallet -->
    <div class="config-section" v-if="!autowalletConfig">
      <div class="card">
        <h2>🚀 Configuration initiale</h2>
        <p>Configurez votre autowallet pour commencer l'investissement automatique</p>
        
        <!-- Bouton de configuration rapide -->
        <div class="quick-setup">
          <button @click="createDefaultConfig" class="btn btn-success" :disabled="isLoading">
            ⚡ Configuration rapide (recommandée)
          </button>
          <p class="quick-hint">Utilise les paramètres par défaut optimisés pour commencer rapidement</p>
        </div>
        
        <div class="separator">
          <span>ou</span>
        </div>
        
        <form @submit.prevent="createAutowallet" class="config-form">
          <div class="form-group">
            <label>Activer l'autowallet</label>
            <input type="checkbox" v-model="newConfig.is_active" />
          </div>
          
          <div class="form-group">
            <label>Intervalle d'analyse (minutes)</label>
            <select v-model="newConfig.analysis_interval">
              <option value="5">5 minutes</option>
              <option value="15">15 minutes</option>
              <option value="30">30 minutes</option>
              <option value="60">1 heure</option>
            </select>
          </div>
          
          <div class="form-group">
            <label>Montant maximum par trade (USD)</label>
            <input type="number" v-model="newConfig.max_investment_per_trade" min="10" step="10" />
          </div>
          
          <div class="form-group">
            <label>Tolérance au risque</label>
            <select v-model="newConfig.risk_tolerance">
              <option value="low">Faible</option>
              <option value="medium">Moyenne</option>
              <option value="high">Élevée</option>
            </select>
          </div>
          
          <div class="form-group">
            <label>Stratégie d'investissement</label>
            <select v-model="newConfig.investment_strategy">
              <option value="conservative">Conservatrice</option>
              <option value="balanced">Équilibrée</option>
              <option value="aggressive">Agressive</option>
            </select>
          </div>
          
          <div class="form-group">
            <label>Seuil de confiance minimum (%)</label>
            <input type="number" v-model="newConfig.min_confidence_threshold" min="50" max="95" step="5" />
          </div>
          
          <div class="form-group">
            <label>Cryptomonnaies autorisées</label>
            <div class="crypto-list">
              <label v-for="crypto in availableCryptos" :key="crypto" class="crypto-checkbox">
                <input type="checkbox" :value="crypto" v-model="newConfig.crypto_whitelist" />
                {{ crypto }}
              </label>
            </div>
          </div>
          
          <button type="submit" class="btn btn-primary" :disabled="isLoading">
            {{ isLoading ? 'Création...' : 'Créer l\'autowallet' }}
          </button>
        </form>
      </div>
    </div>

    <!-- Dashboard de l'autowallet -->
    <div class="dashboard" v-if="autowalletConfig">
      <div class="status-card card">
        <h3>📊 Statut de l'autowallet</h3>
        <div class="status-grid">
          <div class="status-item">
            <span class="label">Statut:</span>
            <span :class="['status', autowalletConfig.is_active ? 'active' : 'inactive']">
              {{ autowalletConfig.is_active ? 'Actif' : 'Inactif' }}
            </span>
          </div>
          <div class="status-item">
            <span class="label">Monitoring:</span>
            <span :class="['status', autowalletConfig.is_monitoring ? 'active' : 'inactive']">
              {{ autowalletConfig.is_monitoring ? 'En cours' : 'Arrêté' }}
            </span>
          </div>
          <div class="status-item">
            <span class="label">Trades aujourd'hui:</span>
            <span class="value">{{ autowalletConfig.today_trades }}/{{ autowalletConfig.max_daily_trades }}</span>
          </div>
          <div class="status-item">
            <span class="label">Total trades:</span>
            <span class="value">{{ autowalletConfig.total_trades }}</span>
          </div>
        </div>
        
        <div class="actions">
          <button 
            @click="startMonitoring" 
            class="btn btn-success" 
            :disabled="autowalletConfig.is_monitoring || !autowalletConfig.is_active"
          >
            Démarrer le monitoring
          </button>
          <button 
            @click="stopMonitoring" 
            class="btn btn-warning" 
            :disabled="!autowalletConfig.is_monitoring"
          >
            Arrêter le monitoring
          </button>
        </div>
      </div>

      <!-- Navigation principale -->
      <div class="main-navigation card">
        <h3>🎛️ Navigation du Dashboard</h3>
        <p class="nav-description">Sélectionnez la section que vous souhaitez consulter</p>
        
        <div class="nav-buttons">
          <button 
            @click="currentPage = 'overview'"
            class="nav-btn"
            :class="{ active: currentPage === 'overview' }"
          >
            <span class="nav-icon">📊</span>
            <span class="nav-label">Vue d'ensemble</span>
          </button>
          
          <button 
            @click="currentPage = 'news-alerts'"
            class="nav-btn"
            :class="{ active: currentPage === 'news-alerts' }"
          >
            <span class="nav-icon">📰🚨</span>
            <span class="nav-label">News + Alertes</span>
          </button>
          
          <button 
            @click="currentPage = 'pipeline'"
            class="nav-btn"
            :class="{ active: currentPage === 'pipeline' }"
          >
            <span class="nav-icon">🔧</span>
            <span class="nav-label">Pipeline d'exécution</span>
          </button>
        </div>
      </div>

      <!-- Contenu des sous-pages -->
      <div class="page-content">
        
        <!-- Vue d'ensemble -->
        <div v-if="currentPage === 'overview'" class="overview-page">
      <!-- Configuration actuelle -->
      <div class="config-card card">
        <h3>⚙️ Configuration actuelle</h3>
        <div class="config-grid">
          <div class="config-item">
            <span class="label">Intervalle d'analyse:</span>
            <span class="value">{{ autowalletConfig.analysis_interval }} minutes</span>
          </div>
          <div class="config-item">
            <span class="label">Montant max par trade:</span>
            <span class="value">${{ autowalletConfig.max_investment_per_trade }}</span>
          </div>
          <div class="config-item">
            <span class="label">Tolérance au risque:</span>
            <span class="value">{{ getRiskLabel(autowalletConfig.risk_tolerance) }}</span>
          </div>
          <div class="config-item">
            <span class="label">Stratégie:</span>
            <span class="value">{{ getStrategyLabel(autowalletConfig.investment_strategy) }}</span>
          </div>
          <div class="config-item">
            <span class="label">Seuil de confiance:</span>
            <span class="value">{{ autowalletConfig.min_confidence_threshold }}%</span>
          </div>
        </div>
        
        <button @click="showEditConfig = true" class="btn btn-secondary">
          Modifier la configuration
        </button>
          </div>
        </div>
        
        <!-- Sous-page 1: News + Alertes -->
        <div v-if="currentPage === 'news-alerts'" class="news-alerts-page">
          <NewsAlertsDashboard />
        </div>
        
        <!-- Sous-page 2: Pipeline d'exécution -->
        <div v-if="currentPage === 'pipeline'" class="pipeline-page">
          <FullPipelineDashboard />
        </div>
        
      </div>


    </div>

    <!-- Modals -->
    <Modal v-if="showEditConfig" @close="showEditConfig = false">
      <template #header>Modifier la configuration</template>
      <template #body>
        <EditConfigForm 
          :config="autowalletConfig" 
          @save="updateConfig" 
          @cancel="showEditConfig = false" 
        />
      </template>
    </Modal>

    <Modal v-if="showAddChannel" @close="showAddChannel = false">
      <template #header>Ajouter un canal d'alerte</template>
      <template #body>
        <AddChannelForm @save="addChannel" @cancel="showAddChannel = false" />
      </template>
    </Modal>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import apiService from '../services/apiService'
import Modal from './Modal.vue'
import EditConfigForm from './EditConfigForm.vue'
import AddChannelForm from './AddChannelForm.vue'
import NewsAlertsDashboard from './NewsAlertsDashboard.vue'
import FullPipelineDashboard from './FullPipelineDashboard.vue'

export default {
  name: 'AutoWallet',
  components: {
    Modal,
    EditConfigForm,
    AddChannelForm,
    NewsAlertsDashboard,
    FullPipelineDashboard
  },
  setup() {
    const autowalletConfig = ref(null)
    const alertChannels = ref([])
    const recentNews = ref([])
    const tradeHistory = ref([])
    const recentAlerts = ref([])
    const isLoading = ref(false)
    const showEditConfig = ref(false)
    const showAddChannel = ref(false)
    
    // Variables pour la pipeline de trading
    const pipelineStatus = ref({})
    const pipelineMarketData = ref({})
    const pipelinePredictions = ref({})
    const pipelineSignals = ref({})

    const newConfig = ref({
      is_active: true,
      analysis_interval: 15,
      max_investment_per_trade: 100,
      risk_tolerance: 'medium',
      investment_strategy: 'balanced',
      min_confidence_threshold: 30,  // 30% au lieu de 70%
      crypto_whitelist: ['BTC', 'ETH', 'ADA', 'DOT', 'SOL']
    })

    const availableCryptos = [
      'BTC', 'ETH', 'ADA', 'DOT', 'SOL', 'MATIC', 'AVAX', 'UNI', 'LINK',
      'BNB', 'XRP', 'DOGE', 'SHIB', 'LTC', 'BCH', 'XLM', 'VET', 'TRX'
    ]

    // Variables pour la navigation des sous-pages
    const currentPage = ref('overview')

    // Charger la configuration existante
    const loadAutowalletConfig = async () => {
      try {
        const response = await apiService.request('/api/autowallet/config')
        if (response.success !== false) {
          autowalletConfig.value = response
          await loadAlertChannels()
          await loadRecentNews()
          await loadTradeHistory()
          await loadRecentAlerts()
          await loadPipelineStatus()
        }
      } catch (error) {
        console.error('Erreur lors du chargement de la config:', error)
        // Si la configuration n'existe pas, créer une configuration par défaut
        if (error.message && error.message.includes('Autowallet non trouvé')) {
          console.log('Création automatique d\'une configuration par défaut...')
          await createDefaultConfig()
        }
      }
      
      // Toujours charger les alertes, même si la config n'existe pas
      await loadRecentAlerts()
      await loadPipelineStatus()
    }

    // Créer une configuration par défaut
    const createDefaultConfig = async () => {
      try {
        const defaultConfig = {
          is_active: true,
          analysis_interval: 15,
          max_investment_per_trade: 100,
          risk_tolerance: 'medium',
          investment_strategy: 'balanced',
          min_confidence_threshold: 0.3,  // Utiliser le nom attendu par le backend
          max_daily_trades: 10,
          stop_loss_percentage: 5.0,
          take_profit_percentage: 15.0
        }
        
        const response = await apiService.request('/api/autowallet/config', {
          method: 'POST',
          body: defaultConfig
        })
        
        if (response.success) {
          console.log('Configuration par défaut créée avec succès')
          autowalletConfig.value = defaultConfig
          await loadAlertChannels()
          await loadRecentNews()
          await loadTradeHistory()
          await loadRecentAlerts()
          
          // Démarrer l'analyse automatique
          await startAutoAnalysis()
        }
      } catch (createError) {
        console.error('Erreur lors de la création de la config par défaut:', createError)
      }
    }

    // Charger les canaux d'alerte
    const loadAlertChannels = async () => {
      try {
        const response = await apiService.request('/api/autowallet/alerts/channels')
        if (response.success) {
          alertChannels.value = response.channels
        }
      } catch (error) {
        console.error('Erreur lors du chargement des canaux:', error)
      }
    }

    // Charger les news récentes
    const loadRecentNews = async () => {
      try {
        const response = await apiService.request('/api/autowallet/news?hours=24')
        if (response.success) {
          recentNews.value = response.news
        }
      } catch (error) {
        console.error('Erreur lors du chargement des news:', error)
      }
    }

    // Charger l'historique des trades
    const loadTradeHistory = async () => {
      try {
        const response = await apiService.request('/api/autowallet/trades?limit=20')
        if (response.success) {
          tradeHistory.value = response.trades
        }
      } catch (error) {
        console.error('Erreur lors du chargement des trades:', error)
      }
    }

    // Charger les alertes récentes
    const loadRecentAlerts = async () => {
      console.log('🔄 Chargement des alertes récentes...')
      try {
        // Récupérer les alertes depuis l'API
        const response = await apiService.request('/api/autowallet/alerts?limit=10')
        if (response.success) {
          recentAlerts.value = response.alerts || []
          console.log('✅ Alertes récupérées:', recentAlerts.value)
          console.log('📊 Nombre d\'alertes:', recentAlerts.value.length)
          console.log('🔍 Première alerte:', recentAlerts.value[0])
          console.log('📱 recentAlerts.value:', recentAlerts.value)
        } else {
          console.log('⚠️ Aucune alerte trouvée ou erreur API')
          recentAlerts.value = []
        }
      } catch (error) {
        console.error('Erreur lors du chargement des alertes:', error)
        recentAlerts.value = []
      }
    }

    // Créer l'autowallet
    const createAutowallet = async () => {
      isLoading.value = true
      try {
        const response = await apiService.request('/api/autowallet/config', {
          method: 'POST',
          body: newConfig.value
        })
        
        if (response.success) {
          await loadAutowalletConfig()
        }
      } catch (error) {
        console.error('Erreur lors de la création:', error)
      } finally {
        isLoading.value = false
      }
    }

    // Démarrer le monitoring
    const startMonitoring = async () => {
      try {
        const response = await apiService.request('/api/autowallet/start', {
          method: 'POST'
        })
        
        if (response.success) {
          await loadAutowalletConfig()
        }
      } catch (error) {
        console.error('Erreur lors du démarrage:', error)
      }
    }

    // Arrêter le monitoring
    const stopMonitoring = async () => {
      try {
        const response = await apiService.request('/api/autowallet/stop', {
          method: 'POST'
        })
        
        if (response.success) {
          await loadAutowalletConfig()
        }
      } catch (error) {
        console.error('Erreur lors de l\'arrêt:', error)
      }
    }

    // Démarrer l'analyse automatique
    const startAutoAnalysis = async () => {
      try {
        const response = await apiService.request('/api/autowallet/start', {
          method: 'POST'
        })
        
        if (response.success) {
          console.log('✅ Analyse automatique démarrée')
          await loadAutowalletConfig()
        }
      } catch (error) {
        console.error('Erreur lors du démarrage de l\'analyse automatique:', error)
      }
    }

    // Analyser des news
    const analyzeNews = async (newsIds) => {
      try {
        console.log('🔍 Analyse des news:', newsIds)
        
        const response = await apiService.request('/api/autowallet/analyze', {
          method: 'POST',
          body: { news_ids: newsIds }
        })
        
        if (response.success) {
          console.log('✅ Alertes générées:', response.alerts)
          console.log(`📊 ${response.count} alertes créées`)
          
          // Recharger les alertes récentes
          await loadRecentAlerts()
          
          // Afficher un message de succès à l'utilisateur
          if (response.count > 0) {
            alert(`✅ ${response.count} alerte(s) générée(s) avec succès !`)
          } else {
            alert('ℹ️ Aucune alerte générée pour ces news')
          }
        }
      } catch (error) {
        console.error('❌ Erreur lors de l\'analyse:', error)
        
        // Afficher un message d'erreur à l'utilisateur
        let errorMessage = 'Erreur lors de l\'analyse des news'
        
        if (error.message.includes('401')) {
          errorMessage = 'Erreur d\'authentification. Veuillez vous reconnecter.'
        } else if (error.message.includes('404')) {
          errorMessage = 'Configuration AutoWallet non trouvée. Création en cours...'
          // Essayer de créer une configuration par défaut
          await createDefaultConfig()
        } else if (error.message.includes('500')) {
          errorMessage = 'Erreur serveur. Veuillez réessayer plus tard.'
        }
        
        alert(`❌ ${errorMessage}`)
      }
    }

    // Actualiser les news
    const refreshNews = async () => {
      await loadRecentNews()
    }

    // ===== MÉTHODES DE LA PIPELINE DE TRADING =====
    
    // Charger le statut de la pipeline
    const loadPipelineStatus = async () => {
      try {
        const response = await apiService.request('/api/trading-pipeline/status')
        if (response.success) {
          pipelineStatus.value = response.status
        }
      } catch (error) {
        console.error('Erreur lors du chargement du statut de la pipeline:', error)
      }
    }

    // Charger les données de marché de la pipeline
    const loadPipelineMarketData = async () => {
      try {
        const response = await apiService.request('/api/trading-pipeline/market-data')
        if (response.success) {
          pipelineMarketData.value = response.market_data || {}
        }
      } catch (error) {
        console.error('Erreur lors du chargement des données de marché:', error)
      }
    }

    // Charger les prédictions de la pipeline
    const loadPipelinePredictions = async () => {
      try {
        // Les prédictions sont disponibles dans les données de marché
        const response = await apiService.request('/api/trading-pipeline/test/market-data')
        if (response.success && response.market_data) {
          // Extraire les prédictions des données de marché
          const predictions = {}
          response.market_data.forEach(data => {
            if (data.prediction) {
              predictions[data.symbol] = data.prediction
            }
          })
          pipelinePredictions.value = predictions
        }
      } catch (error) {
        console.error('Erreur lors du chargement des prédictions:', error)
      }
    }

    // Charger les signaux de la pipeline
    const loadPipelineSignals = async () => {
      try {
        // Les signaux sont disponibles dans les données de marché
        const response = await apiService.request('/api/trading-pipeline/test/market-data')
        if (response.success && response.market_data) {
          // Extraire les signaux des données de marché
          const signals = {}
          response.market_data.forEach(data => {
            if (data.strategy_signal) {
              signals[data.symbol] = data.strategy_signal
            }
          })
          pipelineSignals.value = signals
        }
      } catch (error) {
        console.error('Erreur lors du chargement des signaux:', error)
      }
    }

    // Démarrer la pipeline
    const startTradingPipeline = async () => {
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
    const stopTradingPipeline = async () => {
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

    // Actions manuelles de la pipeline
    const forcePipelineDataCollection = async () => {
      isLoading.value = true
      try {
        await apiService.request('/api/trading-pipeline/force-collect', { method: 'POST' })
        await loadPipelineMarketData()
      } catch (error) {
        console.error('Erreur lors de la collecte forcée:', error)
      } finally {
        isLoading.value = false
      }
    }

    const forcePipelinePrediction = async () => {
      isLoading.value = true
      try {
        // Démarrer la pipeline pour générer de nouvelles prédictions
        await apiService.request('/api/trading-pipeline/test/start', { method: 'POST' })
        await loadPipelinePredictions()
      } catch (error) {
        console.error('Erreur lors de la génération forcée:', error)
      } finally {
        isLoading.value = false
      }
    }

    const forcePipelineSignals = async () => {
      isLoading.value = true
      try {
        // Démarrer la pipeline pour générer de nouveaux signaux
        await apiService.request('/api/trading-pipeline/test/start', { method: 'POST' })
        await loadPipelineSignals()
      } catch (error) {
        console.error('Erreur lors de la génération forcée:', error)
      } finally {
        isLoading.value = false
      }
    }

    const forcePipelineExecution = async () => {
      isLoading.value = true
      try {
        // Démarrer la pipeline pour une exécution forcée
        await apiService.request('/api/trading-pipeline/test/start', { method: 'POST' })
        // Recharger toutes les données de la pipeline
        await Promise.all([
          loadPipelineStatus(),
          loadPipelineMarketData(),
          loadPipelinePredictions(),
          loadPipelineSignals()
        ])
      } catch (error) {
        console.error('Erreur lors de l\'exécution forcée:', error)
      } finally {
        isLoading.value = false
      }
    }

    // Ajouter un canal d'alerte
    const addChannel = async (channelData) => {
      try {
        const response = await apiService.request('/api/autowallet/alerts/channels', {
          method: 'POST',
          body: channelData
        })
        
        if (response.success) {
          await loadAlertChannels()
          showAddChannel.value = false
        }
      } catch (error) {
        console.error('Erreur lors de l\'ajout du canal:', error)
      }
    }

    // Supprimer un canal
    const removeChannel = async (channelId) => {
      try {
        const response = await apiService.request(`/api/autowallet/alerts/channels/${channelId}`, {
          method: 'DELETE'
        })
        
        if (response.success) {
          await loadAlertChannels()
        }
      } catch (error) {
        console.error('Erreur lors de la suppression:', error)
      }
    }

    // Toggle canal
    const toggleChannel = async (channelId) => {
      try {
        const channel = alertChannels.value.find(c => c.id === channelId)
        const response = await apiService.request(`/api/autowallet/alerts/channels/${channelId}`, {
          method: 'PUT',
          body: { is_active: !channel.is_active }
        })
        
        if (response.success) {
          await loadAlertChannels()
        }
      } catch (error) {
        console.error('Erreur lors du toggle:', error)
      }
    }

    // Mettre à jour la configuration
    const updateConfig = async (updatedConfig) => {
      try {
        const response = await apiService.request('/api/autowallet/config', {
          method: 'PUT',
          body: updatedConfig
        })
        
        if (response.success) {
          await loadAutowalletConfig()
          showEditConfig.value = false
        }
      } catch (error) {
        console.error('Erreur lors de la mise à jour:', error)
      }
    }

    // Utilitaires
    const getRiskLabel = (risk) => {
      const labels = { low: 'Faible', medium: 'Moyenne', high: 'Élevée' }
      return labels[risk] || risk
    }

    const getStrategyLabel = (strategy) => {
      const labels = { conservative: 'Conservatrice', balanced: 'Équilibrée', aggressive: 'Agressive' }
      return labels[strategy] || strategy
    }

    const getChannelTypeLabel = (type) => {
      const labels = { email: 'Email', webhook: 'Webhook', telegram: 'Telegram', discord: 'Discord' }
      return labels[type] || type
    }

    const getSentimentClass = (score) => {
      if (score > 0.3) return 'positive'
      if (score < -0.3) return 'negative'
      return 'neutral'
    }

    const formatSentiment = (score) => {
      if (score > 0.3) return 'Positif'
      if (score < -0.3) return 'Négatif'
      return 'Neutre'
    }

    const getImpactClass = (level) => {
      return level
    }

    const getImpactLabel = (level) => {
      const labels = { low: 'Faible', medium: 'Moyen', high: 'Élevé', critical: 'Critique' }
      return labels[level] || level
    }

    const formatTime = (timeStr) => {
      return new Date(timeStr).toLocaleString('fr-FR')
    }

    onMounted(async () => {
      await loadAutowalletConfig()
      // Charger aussi les alertes directement
      await loadRecentAlerts()
      // Charger les données de la pipeline
      await Promise.all([
        loadPipelineMarketData(),
        loadPipelinePredictions(),
        loadPipelineSignals()
      ])
    })

    return {
      autowalletConfig,
      alertChannels,
      recentNews,
      tradeHistory,
      recentAlerts,
      isLoading,
      showEditConfig,
      showAddChannel,
      newConfig,
      availableCryptos,
      currentPage,
      createAutowallet,
      startMonitoring,
      stopMonitoring,
      startAutoAnalysis,
      createDefaultConfig,
      loadRecentAlerts,
      analyzeNews,
      refreshNews,
      addChannel,
      removeChannel,
      toggleChannel,
      updateConfig,
      getRiskLabel,
      getStrategyLabel,
      getChannelTypeLabel,
      getSentimentClass,
      formatSentiment,
      getImpactClass,
      getImpactLabel,
      formatTime,
      // Pipeline de trading
      pipelineStatus,
      pipelineMarketData,
      pipelinePredictions,
      pipelineSignals,
      startTradingPipeline,
      stopTradingPipeline,
      forcePipelineDataCollection,
      forcePipelinePrediction,
      forcePipelineSignals,
      forcePipelineExecution
    }
  }
}
</script>

<style scoped>
.autowallet-container {
  margin: 0 auto;
  padding: 20px;
}

.header {
  text-align: center;
  margin-bottom: 30px;
}

.header h1 {
  color: var(--text-primary);
  margin-bottom: 10px;
  font-weight: 600;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  letter-spacing: 1px;
}

.subtitle {
  color: var(--text-secondary);
  font-size: 1.1em;
}

.card {
  background: var(--glass-bg);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--glass-border);
  border-radius: 20px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: var(--card-shadow);
  transition: all 0.2s ease;
  position: relative;
  overflow: hidden;
  animation: fadeInUp 0.6s ease;
}

.card::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(
    135deg,
    rgba(255, 255, 255, 0.15) 0%,
    transparent 60%
  );
  pointer-events: none;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.card:hover {
  transform: scale(1.02);
  background: rgba(255, 255, 255, 0.12);
  border-color: rgba(255, 255, 255, 0.2);
  box-shadow: var(--card-shadow-hover);
}

.card:hover::before {
  opacity: 1;
}

.card h2, .card h3 {
  color: var(--text-primary);
  margin-bottom: 16px;
  font-weight: 600;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  letter-spacing: 1px;
}

.config-form {
  display: grid;
  gap: 20px;
}

.quick-setup {
  text-align: center;
  margin-bottom: 30px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 2px dashed #dee2e6;
}

.quick-setup .btn {
  font-size: 18px;
  padding: 16px 32px;
  margin-bottom: 10px;
}

.quick-hint {
  color: #6c757d;
  font-size: 0.9em;
  margin: 0;
}

.separator {
  text-align: center;
  margin: 30px 0;
  position: relative;
}

.separator::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  height: 1px;
  background: #dee2e6;
}

.separator span {
  background: white;
  padding: 0 20px;
  color: #6c757d;
  font-size: 0.9em;
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

.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 10px;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  color: white;
}

.btn::before {
  content: "";
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    120deg,
    rgba(255, 255, 255, 0.2) 0%,
    rgba(255, 255, 255, 0.2) 50%,
    rgba(255, 255, 255, 0) 80%
  );
  transition: left 0.5s ease;
  z-index: -1;
}

.btn:hover::before {
  left: 100%;
}

.btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(125, 82, 204, 0.4);
}

.btn-primary {
  background: var(--primary-gradient);
  color: white;
}

.btn-primary:hover {
  background: var(--primary-gradient);
}

.btn-secondary {
  background: linear-gradient(135deg, #6b7280 0%, #4b5563 100%);
  color: white;
}

.btn-secondary:hover {
  background: linear-gradient(135deg, #6b7280 0%, #4b5563 100%);
}

.btn-success {
  background: var(--success-gradient);
  color: white;
}

.btn-success:hover {
  background: var(--success-gradient);
}

.btn-warning {
  background: var(--warning-gradient);
  color: white;
}

.btn-warning:hover {
  background: var(--warning-gradient);
}

.btn-danger {
  background: var(--error-gradient);
  color: white;
}

.btn-danger:hover {
  background: var(--error-gradient);
}

.btn-sm {
  padding: 8px 16px;
  font-size: 14px;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.status-grid,
.config-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}

.status-item,
.config-item {
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

.channels-list {
  margin-bottom: 20px;
}

.channel-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
  margin-bottom: 12px;
}

.channel-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.channel-type {
  font-weight: 600;
  color: #34495e;
}

.channel-actions {
  display: flex;
  gap: 8px;
}

.news-list {
  margin-bottom: 20px;
}

.news-item {
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
  margin-bottom: 16px;
  border-left: 4px solid #3498db;
}

.news-header h4 {
  margin: 0 0 8px 0;
  color: #2c3e50;
}

.news-meta {
  display: flex;
  gap: 16px;
  margin-bottom: 12px;
  font-size: 14px;
  color: #7f8c8d;
}

.news-content {
  margin-bottom: 16px;
  line-height: 1.6;
  color: #34495e;
}

.news-analysis {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.sentiment,
.relevance,
.impact {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
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

.impact.low {
  background: #d1ecf1;
  color: #0c5460;
}

.impact.medium {
  background: #fff3cd;
  color: #856404;
}

.impact.high {
  background: #f8d7da;
  color: #721c24;
}

.impact.critical {
  background: #f8d7da;
  color: #721c24;
  font-weight: bold;
}

.news-actions {
  display: flex;
  gap: 12px;
}

.trades-list {
  margin-bottom: 20px;
}

.trade-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
  margin-bottom: 12px;
}

.trade-header {
  display: flex;
  align-items: center;
  gap: 16px;
}

.action {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
}

.action.buy {
  background: #d4edda;
  color: #155724;
}

.action.sell {
  background: #f8d7da;
  color: #721c24;
}

.crypto {
  font-weight: 600;
  color: #34495e;
}

.amount {
  font-weight: 600;
  color: #27ae60;
}

.trade-details {
  display: flex;
  gap: 16px;
  align-items: center;
}

.confidence {
  font-weight: 600;
  color: #3498db;
}

.status {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
}

.status.pending {
  background: #fff3cd;
  color: #856404;
}

.status.executed {
  background: #d4edda;
  color: #155724;
}

.status.cancelled {
  background: #f8d7da;
  color: #721c24;
}

.status.failed {
  background: #f8d7da;
  color: #721c24;
}

.time {
  font-size: 14px;
  color: #7f8c8d;
}

.no-channels,
.no-trades,
.loading {
  text-align: center;
  padding: 40px;
  color: #7f8c8d;
}

.auto-analysis-status {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 20px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e1e8ed;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background-color: #27ae60; /* Default to green */
}

.status-dot.active {
  background-color: #27ae60; /* Green for active */
}

.status-text {
  font-size: 16px;
  font-weight: 600;
  color: #34495e;
}

.status-details {
  font-size: 14px;
  color: #7f8c8d;
}

.alert-types {
  display: flex;
  justify-content: space-around;
  margin-top: 15px;
  padding: 10px 0;
  border-top: 1px solid #e1e8ed;
  border-bottom: 1px solid #e1e8ed;
}

.alert-type {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #34495e;
}

.type-badge {
  padding: 4px 10px;
  border-radius: 15px;
  font-weight: 600;
  color: white;
}

.type-badge.buy {
  background-color: #27ae60;
}

.type-badge.sell {
  background-color: #e74c3c;
}

.type-badge.hold {
  background-color: #f39c12;
}

.recent-alerts h4 {
  margin-bottom: 15px;
  color: #2c3e50;
}

.alert-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.alert-item {
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #3498db; /* Default color */
}

.alert-item.buy {
  border-left-color: #27ae60; /* Green for BUY */
}

.alert-item.sell {
  border-left-color: #e74c3c; /* Red for SELL */
}

.alert-item.hold {
  border-left-color: #f39c12; /* Orange for HOLD */
}

.alert-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.alert-type {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
  color: white;
}

.alert-type.buy {
  background-color: #27ae60;
}

.alert-type.sell {
  background-color: #e74c3c;
}

.alert-type.hold {
  background-color: #f39c12;
}

.crypto-symbol {
  font-weight: 600;
  color: #34495e;
}

.confidence {
  font-weight: 600;
  color: #3498db;
}

.alert-reasoning {
  font-size: 14px;
  color: #34495e;
  line-height: 1.5;
  margin-bottom: 12px;
}

.alert-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
  color: #7f8c8d;
}

.priority {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
}

.priority.high {
  background-color: #f8d7da;
  color: #721c24;
}

.priority.medium {
  background-color: #fff3cd;
  color: #856404;
}

.priority.low {
  background-color: #d4edda;
  color: #155724;
}

.no-alerts {
  text-align: center;
  padding: 40px;
  color: #7f8c8d;
}

.no-alerts .hint {
  margin-top: 10px;
  font-size: 0.9em;
  color: #95a5a6;
}

.trades-info {
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #e1e8ed;
}

.trades-info .info-text {
  font-size: 14px;
  color: #7f8c8d;
  margin-bottom: 10px;
}

.trade-reasoning {
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px dashed #e1e8ed;
}

.trade-reasoning p {
  font-size: 14px;
  color: #34495e;
  line-height: 1.5;
}

.alerts-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

  .alerts-header h3 {
    margin: 0;
  }

  /* Styles pour la pipeline de trading */
  .trading-pipeline-section {
    margin-bottom: 30px;
  }

  .section-header {
    margin-bottom: 20px;
    text-align: center;
  }

  .section-header h3 {
    color: #2c3e50;
    margin-bottom: 8px;
  }

  .section-description {
    color: #7f8c8d;
    font-size: 0.95em;
  }

  .pipeline-status-card {
    margin-bottom: 20px;
  }

  .pipeline-status-card h4 {
    color: #2c3e50;
    margin-bottom: 16px;
  }

  .pipeline-status-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 12px;
    margin-bottom: 16px;
  }

  .pipeline-actions {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
    justify-content: center;
  }

  .pipeline-data-section {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 20px;
    margin-bottom: 20px;
  }

  .pipeline-data-card {
    min-height: 200px;
  }

  .pipeline-data-card h4 {
    color: #2c3e50;
    margin-bottom: 16px;
  }

  .data-list {
    max-height: 300px;
    overflow-y: auto;
  }

  .data-item {
    padding: 12px;
    background: #f8f9fa;
    border-radius: 8px;
    margin-bottom: 8px;
    border-left: 3px solid #3498db;
  }

  .data-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 6px;
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
  .signal-type {
    padding: 3px 10px;
    border-radius: 16px;
    font-size: 12px;
    font-weight: 600;
    color: white;
  }

  .direction.bullish,
  .signal-type.buy {
    background: #27ae60;
  }

  .direction.bearish,
  .signal-type.sell {
    background: #e74c3c;
  }

  .direction.neutral,
  .signal-type.hold {
    background: #f39c12;
  }

  .data-details {
    display: flex;
    gap: 12px;
    font-size: 13px;
  }

  .sentiment,
  .confidence,
  .volatility,
  .volume,
  .position {
    padding: 2px 6px;
    border-radius: 10px;
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

  .pipeline-actions-card {
    text-align: center;
  }

  .pipeline-actions-card h4 {
    color: #2c3e50;
    margin-bottom: 12px;
  }

  .pipeline-actions-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 12px;
    max-width: 800px;
    margin: 0 auto;
  }

  .no-data {
    text-align: center;
    padding: 30px;
    color: #7f8c8d;
  }

@media (max-width: 768px) {
  .autowallet-container {
    padding: 16px;
  }
  
  .card {
    padding: 16px;
  }
  
  .status-grid,
  .config-grid {
    grid-template-columns: 1fr;
  }
  
  .news-analysis {
    flex-direction: column;
    gap: 8px;
  }

  .pipeline-data-section {
    grid-template-columns: 1fr;
  }

  .pipeline-actions-grid {
    grid-template-columns: 1fr;
  }

  .pipeline-status-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .trade-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .trade-details {
    flex-direction: column;
    gap: 8px;
  }
}

/* Styles pour la navigation principale */
.main-navigation {
  margin-bottom: 30px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.main-navigation h3 {
  margin-top: 0;
  color: white;
  margin-bottom: 10px;
}

.nav-description {
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 25px;
  font-size: 1rem;
}

.nav-buttons {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.nav-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 20px 25px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  background: rgba(255, 255, 255, 0.1);
  border-radius: 15px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 500;
  color: white;
  min-width: 150px;
  backdrop-filter: blur(10px);
}

.nav-btn:hover {
  border-color: rgba(255, 255, 255, 0.6);
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
}

.nav-btn.active {
  background: rgba(255, 255, 255, 0.9);
  border-color: white;
  color: #2c3e50;
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
}

.nav-icon {
  font-size: 2rem;
}

.nav-label {
  font-size: 0.9rem;
  font-weight: 600;
  text-align: center;
}

/* ===== VARIABLES CSS COHÉRENTES AVEC FULLPIPELINEDASHBOARD ===== */
:root {
  --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  --secondary-gradient: linear-gradient(135deg, #8b5cf6 0%, #a855f7 100%);
  --success-gradient: linear-gradient(135deg, #10b981 0%, #059669 100%);
  --warning-gradient: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  --error-gradient: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  --glass-bg: rgba(255, 255, 255, 0.08);
  --glass-border: rgba(255, 255, 255, 0.12);
  --card-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
  --card-shadow-hover: 0 10px 30px rgba(118, 75, 162, 0.4);
  --main-bg: linear-gradient(135deg, #111421 0%, #111421 100%);
  --text-primary: #f3e8ff;
  --text-secondary: rgba(255, 255, 255, 0.8);
}

/* ===== ANIMATIONS COHÉRENTES ===== */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

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

/* Background principal */
.autowallet-container {
  background: linear-gradient(135deg, #111421 0%, #111421 100%);
  min-height: 100vh;
  width: 100vw;
  max-width: 100vw;
  box-sizing: border-box;
  font-family: "Roboto", sans-serif;
  color: #f3e8ff;
  animation: fadeIn 0.6s ease;
  overflow-x: hidden;
  position: relative;
}

/* Styles pour le contenu des pages */
.page-content {
  margin-bottom: 30px;
  animation: fadeInUp 0.6s ease-out;
}

.overview-page,
.news-alerts-page,
.pipeline-page {
  animation: fadeIn 0.3s ease-in-out;
}

/* Animations améliorées */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Amélioration des cartes */
.card {
  background: white;
  box-shadow: var(--card-shadow);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border-radius: 1rem;
  overflow: hidden;
}

.card:hover {
  box-shadow: var(--card-shadow-hover);
  transform: translateY(-2px);
}

/* Amélioration des boutons */
.btn {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
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
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
  transition: left 0.5s;
}

.btn:hover::before {
  left: 100%;
}

.btn:hover {
  transform: translateY(-1px);
  box-shadow: var(--card-shadow-hover);
}

/* Amélioration des sections */
.section-header {
  position: relative;
  padding-bottom: 1rem;
  margin-bottom: 2rem;
}

.section-header::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 60px;
  height: 3px;
  background: var(--primary-gradient);
  border-radius: 2px;
}

/* Effets de glassmorphism pour certaines sections */
.glass-effect {
  background: rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.18);
}

/* Amélioration des indicateurs de statut */
.status-indicator {
  position: relative;
  box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.2);
}

.status-indicator.running {
  animation: pulse-green 2s infinite;
}

.status-indicator.processing {
  animation: pulse-yellow 1s infinite;
}

.status-indicator.error {
  animation: pulse-red 1s infinite;
}

@keyframes pulse-green {
  0%, 100% { 
    box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
  }
  50% { 
    box-shadow: 0 0 0 10px rgba(16, 185, 129, 0);
  }
}

@keyframes pulse-yellow {
  0%, 100% { 
    box-shadow: 0 0 0 0 rgba(245, 158, 11, 0.7);
  }
  50% { 
    box-shadow: 0 0 0 10px rgba(245, 158, 11, 0);
  }
}

@keyframes pulse-red {
  0%, 100% { 
    box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7);
  }
  50% { 
    box-shadow: 0 0 0 10px rgba(239, 68, 68, 0);
  }
}

/* Scrollbars personnalisées */
.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

@media (max-width: 768px) {
  .nav-buttons {
    flex-direction: column;
    gap: 15px;
  }
  
  .nav-btn {
    min-width: auto;
    width: 100%;
    flex-direction: row;
    justify-content: center;
    padding: 15px 20px;
  }
  
  .nav-icon {
    font-size: 1.5rem;
  }
  
  .nav-label {
    font-size: 1rem;
  }
}
</style>
