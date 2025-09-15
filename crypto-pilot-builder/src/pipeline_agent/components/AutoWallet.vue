<template>
  <div class="autowallet-container">
    <div class="header">
      <h1>🤖 CryptoPilot AutoWallet</h1>
      <p class="subtitle">IA d'investissement automatique basée sur l'analyse des news crypto</p>
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

      <!-- News récentes -->
      <div class="news-card card">
        <h3>📰 News récentes</h3>
        
        <!-- Statut de l'analyse automatique -->
        <div class="auto-analysis-status" v-if="autowalletConfig">
          <div class="status-indicator">
            <span class="status-dot" :class="{ active: autowalletConfig.is_monitoring }"></span>
            <span class="status-text">
              {{ autowalletConfig.is_monitoring ? '🔄 Analyse automatique active' : '⏸️ Analyse automatique arrêtée' }}
            </span>
          </div>
          <div class="status-details">
            <span>Intervalle: {{ autowalletConfig.analysis_interval }} minutes</span>
            <span>News analysées: {{ autowalletConfig.total_trades || 0 }}</span>
          </div>
        </div>
        
        <div class="news-list" v-if="recentNews.length > 0">
          <div v-for="news in recentNews" :key="news.id" class="news-item">
            <div class="news-header">
              <h4>{{ news.title }}</h4>
              <div class="news-meta">
                <span class="source">{{ news.source }}</span>
                <span class="time">{{ formatTime(news.published_at) }}</span>
              </div>
            </div>
            <p class="news-content">{{ news.content }}</p>
            <div class="news-analysis">
              <span class="sentiment" :class="getSentimentClass(news.sentiment_score)">
                Sentiment: {{ formatSentiment(news.sentiment_score) }}
              </span>
              <span class="relevance">
                Pertinence: {{ Math.round(news.relevance_score * 100) }}%
              </span>
              <span class="impact" :class="getImpactClass(news.impact_level)">
                Impact: {{ getImpactLabel(news.impact_level) }}
              </span>
            </div>
            <div class="news-actions">
              <a :href="news.url" target="_blank" class="btn btn-sm btn-secondary">
                Lire l'article
              </a>
              <button @click="analyzeNews([news.id])" class="btn btn-sm btn-primary">
                🔍 Analyser manuellement
              </button>
            </div>
          </div>
        </div>
        
        <div v-else class="loading">
          <p>Chargement des news...</p>
        </div>
        
        <button @click="refreshNews" class="btn btn-secondary">
          Actualiser les news
        </button>
      </div>

          <!-- Onglets de navigation -->
    <div class="tabs-navigation">
      <button 
        @click="activeTab = 'autowallet'" 
        :class="['tab-button', { active: activeTab === 'autowallet' }]"
      >
        🤖 AutoWallet
      </button>
      <button 
        @click="activeTab = 'pipeline'" 
        :class="['tab-button', { active: activeTab === 'pipeline' }]"
      >
        🚀 Pipeline de Trading
      </button>
    </div>

    <!-- Contenu de l'onglet AutoWallet -->
    <div v-if="activeTab === 'autowallet'" class="tab-content">
      <!-- Section des alertes et trades -->
      <div class="alerts-trades-section">
        <!-- Alertes récentes -->
        <div class="alerts-card card">
          <div class="alerts-header">
            <h3>🚨 Alertes d'investissement</h3>
            <button @click="loadRecentAlerts" class="btn btn-sm btn-secondary">
              🔄 Actualiser
            </button>
          </div>
          <div class="alerts-info">
            <p class="info-text">
              <strong>Que sont les alertes ?</strong> Ce sont des recommandations d'investissement générées par l'IA 
              basées sur l'analyse des news crypto. Elles vous indiquent quand acheter, vendre ou attendre.
            </p>
            <div class="alert-types">
              <div class="alert-type">
                <span class="type-badge buy">BUY</span>
                <span>Recommandation d'achat</span>
              </div>
              <div class="alert-type">
                <span class="type-badge sell">SELL</span>
                <span>Recommandation de vente</span>
              </div>
              <div class="alert-type">
                <span class="type-badge hold">HOLD</span>
                <span>Attendre et observer</span>
              </div>
            </div>
          </div>
          
          <div class="recent-alerts" v-if="recentAlerts && recentAlerts.length > 0">
            <!-- Debug info -->
            <div style="background: #f0f0f0; padding: 10px; margin-bottom: 15px; border-radius: 5px; font-size: 12px;">
              <strong>Debug:</strong> recentAlerts.length = {{ recentAlerts ? recentAlerts.length : 'undefined' }}
            </div>
            <h4>Alertes récentes</h4>
            <div class="alert-list">
              <div v-for="alert in recentAlerts" :key="alert.id" class="alert-item" :class="alert.alert_type.toLowerCase()">
                <div class="alert-header">
                  <span class="alert-type" :class="alert.alert_type.toLowerCase()">
                    {{ alert.alert_type.toUpperCase() }}
                  </span>
                  <span class="crypto-symbol">{{ alert.crypto_symbol }}</span>
                  <span class="confidence">{{ Math.round(alert.confidence_score * 100) }}%</span>
                </div>
                <div class="alert-meta">
                  <span class="time">{{ formatTime(alert.created_at) }}</span>
                  <span class="alert-id">ID: {{ alert.id.slice(0, 8) }}...</span>
                </div>
              </div>
            </div>
          </div>
          
          <div v-else class="no-alerts">
            <!-- Debug info -->
            <div style="background: #f0f0f0; padding: 10px; margin-bottom: 15px; border-radius: 5px; font-size: 12px;">
              <strong>Debug:</strong> recentAlerts = {{ recentAlerts }}, length = {{ recentAlerts ? recentAlerts.length : 'undefined' }}
            </div>
            <p>Aucune alerte générée pour le moment</p>
            <p class="hint">Les alertes apparaîtront automatiquement lors de l'analyse des news</p>
          </div>
        </div>

        <!-- Historique des trades -->
        <div class="trades-card card">
          <h3>💼 Historique des trades</h3>
          <div class="trades-info">
            <p class="info-text">
              <strong>Que sont les trades ?</strong> Ce sont les actions d'investissement exécutées automatiquement 
              par l'IA basées sur les alertes générées. Chaque trade représente un achat ou une vente de cryptomonnaie.
            </p>
          </div>
          
          <div class="trades-list" v-if="tradeHistory && tradeHistory.length > 0">
            <div v-for="trade in tradeHistory" :key="trade.id" class="trade-item">
              <div class="trade-header">
                <span :class="['action', trade.action.toLowerCase()]">{{ trade.action.toUpperCase() }}</span>
                <span class="crypto">{{ trade.crypto_symbol }}</span>
                <span class="amount">${{ trade.amount }}</span>
              </div>
              <div class="trade-details">
                <span class="confidence">{{ Math.round(trade.confidence_score * 100) }}%</span>
                <span class="status" :class="trade.status">{{ trade.status }}</span>
                <span class="time">{{ formatTime(trade.executed_at) }}</span>
              </div>
              <div class="trade-reasoning" v-if="trade.reasoning">
                <p>{{ trade.reasoning }}</p>
              </div>
            </div>
          </div>
          
          <div v-else class="no-trades">
            <p>Aucun trade effectué pour le moment</p>
            <p class="hint">Les trades seront exécutés automatiquement lors de la génération d'alertes BUY/SELL</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Contenu de l'onglet Pipeline -->
    <div v-if="activeTab === 'pipeline'" class="tab-content">
      <TradingPipeline />
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
import TradingPipeline from './TradingPipeline.vue'

export default {
  name: 'AutoWallet',
  components: {
    Modal,
    EditConfigForm,
    AddChannelForm,
    TradingPipeline
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
    const activeTab = ref('autowallet')

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
      activeTab,
      newConfig,
      availableCryptos,
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
      formatTime
    }
  }
}
</script>

<style scoped>
.autowallet-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.header {
  text-align: center;
  margin-bottom: 30px;
}

.header h1 {
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

.card h2, .card h3 {
  color: #2c3e50;
  margin-bottom: 16px;
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

.btn-danger {
  background: #e74c3c;
  color: white;
}

.btn-danger:hover {
  background: #c0392b;
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

  .tabs-navigation {
    display: flex;
    gap: 8px;
    margin-bottom: 24px;
    border-bottom: 2px solid #e1e8ed;
  }

  .tab-button {
    padding: 12px 24px;
    border: none;
    background: none;
    font-size: 16px;
    font-weight: 600;
    color: #7f8c8d;
    cursor: pointer;
    border-bottom: 3px solid transparent;
    transition: all 0.2s;
  }

  .tab-button:hover {
    color: #3498db;
  }

  .tab-button.active {
    color: #3498db;
    border-bottom-color: #3498db;
  }

  .tab-content {
    min-height: 400px;
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
</style>
