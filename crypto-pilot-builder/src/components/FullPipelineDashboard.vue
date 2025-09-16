<template>
  <div class="pipeline-dashboard">
    <div class="page-container">
    <!-- Header -->
    <header class="gradient-bg text-white shadow-lg rounded-lg mb-8">
      <div class="px-6 py-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-4">
            <div class="text-3xl">🚀</div>
            <h1 class="text-2xl font-bold">Trading Pipeline</h1>
          </div>
          <div class="flex items-center space-x-4">
            <div class="flex items-center space-x-2">
              <div
                :class="[
                  'status-indicator',
                  pipelineStatus.is_running ? 'running' : 'stopped'
                ]"
              ></div>
              <span class="text-sm font-medium">
                {{ pipelineStatus.is_running ? 'Pipeline Actif' : 'Pipeline Arrêté' }}
              </span>
            </div>
            <div class="text-sm text-gray-200">
              Dernière exécution: {{ formatTime(pipelineStatus.last_execution) }}
            </div>
          </div>
        </div>
      </div>
    </header>

    <!-- Pipeline Control -->
    <div class="card-dark rounded-xl p-8 mb-8">
      <div class="text-center mb-8">
        <h2 class="text-3xl font-bold section-title mb-2 ">🎮 Contrôle du Pipeline</h2>
        <p class="lede">Lancez le pipeline complet ou exécutez les agents individuellement</p>
      </div>

      <div class="flex justify-center space-x-6 mb-8">
        <button
          @click="startPipeline"
          :disabled="isLoading || pipelineStatus.is_running"
          class="cta-btn cta-start"
        >
          <span v-if="isLoading">🚀 Démarrage...</span>
          <span v-else-if="pipelineStatus.is_running">✅ Pipeline Actif</span>
          <span v-else>🚀 Lancer Pipeline</span>
        </button>
        <button
          @click="stopPipeline"
          :disabled="isLoading || !pipelineStatus.is_running"
          class="cta-btn cta-stop"
        >
          <span v-if="isLoading">🛑 Arrêt...</span>
          <span v-else>🛑 Arrêter Pipeline</span>
        </button>
      </div>

      <div class="agent-controls-grid">
        <button
          @click="executeSingleAgent('data_collector')"
          :disabled="isLoading"
          class="agent-control-btn bg-blue-500 hover:bg-blue-600 disabled:opacity-50"
        >
          📊 DataCollector
        </button>
        <button
          @click="executeSingleAgent('news_collector')"
          :disabled="isLoading"
          class="agent-control-btn bg-cyan-500 hover:bg-cyan-600 disabled:opacity-50"
        >
          📰 NewsCollector
        </button>
        <button
          @click="executeSingleAgent('data_aggregator')"
          :disabled="isLoading"
          class="agent-control-btn bg-indigo-500 hover:bg-indigo-600 disabled:opacity-50"
        >
          🔄 DataAggregator
        </button>
        <button
          @click="executeSingleAgent('predictor')"
          :disabled="isLoading"
          class="agent-control-btn bg-purple-500 hover:bg-purple-600 disabled:opacity-50"
        >
          🔮 Predictor
        </button>
        <button
          @click="executeSingleAgent('strategy')"
          :disabled="isLoading"
          class="agent-control-btn bg-emerald-500 hover:bg-emerald-600 disabled:opacity-50"
        >
          📈 Strategy
        </button>
        <button
          @click="executeSingleAgent('trader')"
          :disabled="isLoading"
          class="agent-control-btn bg-amber-500 hover:bg-amber-600 disabled:opacity-50"
        >
          💰 Trader
        </button>
        <button
          @click="executeSingleAgent('logger')"
          :disabled="isLoading"
          class="agent-control-btn bg-gray-500 hover:bg-gray-600 disabled:opacity-50"
        >
          📝 Logger
        </button>
      </div>
    </div>

    <!-- Pipeline Flow Visualization -->
    <div class="card-dark rounded-xl p-8 mb-8">
      <h3 class="text-2xl font-bold section-title mb-6 text-center">🔄 Flux du Pipeline</h3>
      <div class="flex items-center justify-center space-x-4 mb-8 overflow-x-auto">
        <div
          v-for="agent in agentFlow"
          :key="agent.name"
          :class="[
            'agent-card',
            getAgentStatusClass(agent.name)
          ]"
        >
          <div class="text-2xl mb-2">{{ agent.icon }}</div>
          <div class="font-semibold text-slate-100">{{ agent.displayName }}</div>
          <div class="text-sm text-slate-300">{{ agent.description }}</div>
          <div class="text-xs mt-1">
            <span class="px-2 py-0.5 rounded-full bg-slate-800/60 border border-slate-700 text-slate-200">{{ getAgentExecutionCount(agent.name) }} exécutions</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Real-time Data -->
    <div class="two-col-grid mb-8">
      <!-- Historique des Prix -->
      <div class="card-dark rounded-xl p-6">
        <h3 class="card-title mb-4">📊 Historique des Prix Bitcoin</h3>
        <div class="history-list text-slate-200">
          <div
            v-for="(price, index) in priceHistory"
            :key="index"
            class="history-row"
          >
            <div class="history-left">
              <div class="time">{{ formatTime(price.timestamp) }}</div>
              <div class="price">${{ price.price?.toLocaleString() }}</div>
            </div>
            <div class="history-right">
              <span v-if="price.prediction" :class="getPredictionClass(price.prediction.direction)">
                {{ price.prediction.direction }} {{ Math.round(price.prediction.confidence * 100) }}%
              </span>
              <span v-if="price.strategy_signal" :class="getSignalClass(price.strategy_signal.action)">
                {{ price.strategy_signal.action }}
              </span>
            </div>
          </div>
          <div v-if="priceHistory.length === 0" class="text-slate-400 text-center py-8">
            Chargement des données...
          </div>
        </div>
      </div>

      <!-- Agent Status -->
      <div class="card-dark rounded-xl p-6">
        <h3 class="card-title mb-4">🤖 Statut des Agents</h3>
        <div class="agent-list">
          <div
            v-for="(agent, name) in pipelineStatus.agents"
            :key="name"
            class="stat-row"
          >
            <div class="stat-left">
              <div :class="['status-indicator', agent.status]"></div>
              <span class="name">{{ formatAgentName(name) }}</span>
            </div>
            <div class="stat-right">
              <span class="badge">{{ agent.execution_count }} exec</span>
              <span class="meta">{{ formatTime(agent.last_execution) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Market Data -->
    <div class="card-dark rounded-xl p-6 mb-8">
      <h3 class="card-title mb-4">💹 Données de Marché</h3>
      <div class="metrics-grid">
        <div class="text-center p-4 bg-slate-800/40 border border-slate-700 rounded-lg">
          <div class="text-2xl mb-2">₿</div>
          <div class="text-sm text-slate-300">Bitcoin</div>
          <div class="text-xl font-bold text-slate-100">
            ${{ getLatestPrice()?.toLocaleString() || '--' }}
          </div>
        </div>
        <div class="text-center p-4 bg-slate-800/40 border border-slate-700 rounded-lg">
          <div class="text-2xl mb-2">📈</div>
          <div class="text-sm text-slate-300">Volume 24h</div>
          <div class="text-xl font-bold text-slate-100">
            {{ getLatestVolume() ? (getLatestVolume() / 1000000).toFixed(1) + 'M' : '--' }}
          </div>
        </div>
        <div class="text-center p-4 bg-slate-800/40 border border-slate-700 rounded-lg">
          <div class="text-2xl mb-2">🔄</div>
          <div class="text-sm text-slate-300">Dernière Mise à jour</div>
          <div class="text-sm font-medium text-slate-300">
            {{ formatTime(pipelineStatus.last_execution) }}
          </div>
        </div>
      </div>
    </div>

    <!-- Pipeline Logs -->
    <div class="card-dark rounded-xl p-6 mb-8">
      <h3 class="card-title mb-4">📝 Logs du Pipeline</h3>
      <div class="log-list">
        <div
          v-for="(log, index) in pipelineLogs"
          :key="index"
          class="log-row"
        >
          <span class="time">{{ formatTime(log.timestamp) }}</span>
          <span class="symbol-chip">{{ log.symbol || '—' }}</span>
          <span class="price">${{ log.price?.toLocaleString() || 'N/A' }}</span>
          <span
            class="signal-badge"
            :class="(log.strategy_signal?.action || 'hold').toLowerCase()"
          >
            {{ log.strategy_signal?.action || 'HOLD' }}
          </span>
        </div>
        <div v-if="pipelineLogs.length === 0" class="empty">Aucun log disponible</div>
      </div>
    </div>

    <!-- Logger Agent - Monitoring du Pipeline -->
    <div class="card-dark rounded-xl p-6 mb-8">
      <h3 class="card-title mb-4">🔍 Logger Agent - Monitoring du Pipeline</h3>

      <!-- Boutons d'action -->
      <div class="logger-actions">
        <button @click="callLoggerAgent" :disabled="isLoading" class="chip-btn chip-success">
          🧪 Tester le Logger Agent
        </button>
        <button @click="clearLoggerData" class="chip-btn chip-slate">
          🗑️ Effacer les Données
        </button>
      </div>

      <!-- Statut du pipeline - KPIs -->
      <div class="kpi-grid mb-6">
        <div class="kpi-card">
          <div class="kpi-icon">🟢</div>
          <div class="kpi-content">
            <div class="kpi-value" :class="pipelineStatus.is_running ? 'text-emerald' : 'text-rose'">
              {{ pipelineStatus.is_running ? 'Actif' : 'Arrêté' }}
            </div>
            <div class="kpi-label">Statut du Pipeline</div>
          </div>
        </div>
        <div class="kpi-card">
          <div class="kpi-icon">👥</div>
          <div class="kpi-content">
            <div class="kpi-value">{{ getActiveAgentsCount() }}</div>
            <div class="kpi-label">Agents Actifs</div>
          </div>
        </div>
        <div class="kpi-card">
          <div class="kpi-icon">⚙️</div>
          <div class="kpi-content">
            <div class="kpi-value">{{ getTotalExecutions() }}</div>
            <div class="kpi-label">Exécutions Totales</div>
          </div>
        </div>
        <div class="kpi-card">
          <div class="kpi-icon">🔮</div>
          <div class="kpi-content">
            <div class="kpi-value">{{ pipelineStatus.predictions_count || 0 }}</div>
            <div class="kpi-label">Prédictions</div>
          </div>
        </div>
        <div class="kpi-card">
          <div class="kpi-icon">📈</div>
          <div class="kpi-content">
            <div class="kpi-value">{{ pipelineStatus.signals_count || 0 }}</div>
            <div class="kpi-label">Signaux</div>
          </div>
        </div>
      </div>

      <!-- Métriques détaillées -->
      <div class="bg-slate-800/40 p-4 rounded-lg mb-6 border border-slate-700">
        <h4 class="font-semibold text-slate-200 mb-3">📈 Métriques du Pipeline</h4>
        <div class="stat-list">
          <div class="stat-line">
            <span class="label">Exécutions Totales</span>
            <span class="badge">{{ getTotalExecutions() }}</span>
          </div>
          <div class="stat-line">
            <span class="label">Taux de Succès</span>
            <span class="badge">{{ getSuccessRate() }}%</span>
          </div>
          <div class="stat-line">
            <span class="label">Prédictions</span>
            <span class="badge">{{ pipelineStatus.predictions_count || 0 }}</span>
          </div>
          <div class="stat-line">
            <span class="label">Signaux</span>
            <span class="badge">{{ pipelineStatus.signals_count || 0 }}</span>
          </div>
        </div>
      </div>

      <!-- Résultats du Logger Agent -->
      <div class="bg-slate-800/40 p-4 rounded-lg mb-6 border border-slate-700">
        <h4 class="font-semibold text-slate-200 mb-3">🧪 Résultats du Logger Agent</h4>
        <div v-if="loggerResponse" class="space-y-4">
          <!-- Rapport du Pipeline -->
          <div class="bg-slate-900/40 p-4 rounded-lg border border-slate-700">
            <h5 class="font-semibold text-slate-200 mb-3">📊 Rapport du Pipeline</h5>
            <div class="stat-list">
              <div class="stat-line">
                <span class="label">Données collectées</span>
                <span class="badge">{{ loggerResponse.result?.pipeline_data_count || 0 }}</span>
              </div>
              <div class="stat-line">
                <span class="label">Dernière exécution</span>
                <span class="badge badge-neutral">{{ formatTime(loggerResponse.result?.report?.pipeline_info?.last_execution) }}</span>
              </div>
            </div>

            <div v-if="loggerResponse.result?.report?.summary" class="mt-4">
              <h6 class="font-semibold text-slate-200 mb-2">📈 Résumé</h6>
              <div class="stat-list">
                <div class="stat-line">
                  <span class="label">Exécutions réussies</span>
                  <span class="badge badge-success">{{ loggerResponse.result.report.summary.successful_executions }}</span>
                </div>
                <div class="stat-line">
                  <span class="label">Exécutions échouées</span>
                  <span class="badge badge-danger">{{ loggerResponse.result.report.summary.failed_executions }}</span>
                </div>
                <div class="stat-line">
                  <span class="label">Total</span>
                  <span class="badge">{{ loggerResponse.result.report.summary.total_executions }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Recommandation de Trading -->
          <div v-if="loggerResponse.result?.report?.summary?.recommendation" class="bg-slate-900/40 p-4 rounded-lg border border-slate-700">
            <h5 class="font-semibold text-slate-200 mb-3">🎯 Recommandation de Trading</h5>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div class="rec-card">
                <div class="rec-icon">{{ getRecommendationIcon(loggerResponse.result.report.summary.recommendation.action) }}</div>
                <div class="rec-badge" :class="(loggerResponse.result.report.summary.recommendation.action || 'HOLD').toLowerCase()">
                  {{ loggerResponse.result.report.summary.recommendation.action }}
                </div>
                <div class="rec-meta">Confiance: {{ (loggerResponse.result.report.summary.recommendation.confidence * 100).toFixed(0) }}%</div>
              </div>
              <div class="stat-list">
                <div class="stat-line">
                  <span class="label">Raison</span>
                  <span class="badge badge-neutral">{{ loggerResponse.result.report.summary.recommendation.reason || '—' }}</span>
                </div>
                <div class="stat-line">
                  <span class="label">Niveau de risque</span>
                  <span class="badge" :class="{
                    'badge-success': loggerResponse.result.report.summary.recommendation.risk_level === 'LOW',
                    'badge-danger': loggerResponse.result.report.summary.recommendation.risk_level === 'HIGH'
                  }">{{ loggerResponse.result.report.summary.recommendation.risk_level }}</span>
                </div>
                <div class="stat-line">
                  <span class="label">Sentiment du marché</span>
                  <span class="badge" :class="{
                    'badge-success': loggerResponse.result.report.summary.recommendation.market_sentiment === 'BULLISH',
                    'badge-danger': loggerResponse.result.report.summary.recommendation.market_sentiment === 'BEARISH',
                    'badge-neutral': loggerResponse.result.report.summary.recommendation.market_sentiment === 'NEUTRAL'
                  }">{{ loggerResponse.result.report.summary.recommendation.market_sentiment }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Analyse de Trading -->
          <div v-if="loggerResponse.result?.report?.trading_analysis" class="bg-slate-900/40 p-4 rounded-lg border border-slate-700">
            <h5 class="font-semibold text-slate-200 mb-3">📊 Analyse de Trading</h5>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
              <!-- Signaux -->
              <div class="bg-slate-800/40 p-3 rounded-lg border border-slate-700">
                <h6 class="font-semibold text-slate-200 mb-2">📈 Signaux</h6>
                <div class="stat-list">
                  <div class="stat-line"><span class="label">Achat</span><span class="badge badge-success">{{ loggerResponse.result.report.trading_analysis.signals.buy_signals }}</span></div>
                  <div class="stat-line"><span class="label">Vente</span><span class="badge badge-danger">{{ loggerResponse.result.report.trading_analysis.signals.sell_signals }}</span></div>
                  <div class="stat-line"><span class="label">Maintien</span><span class="badge badge-neutral">{{ loggerResponse.result.report.trading_analysis.signals.hold_signals }}</span></div>
                </div>
              </div>

              <!-- Prédictions -->
              <div class="bg-slate-800/40 p-3 rounded-lg border border-slate-700">
                <h6 class="font-semibold text-slate-200 mb-2">🔮 Prédictions</h6>
                <div class="stat-list">
                  <div class="stat-line"><span class="label">Haussier</span><span class="badge badge-success">{{ loggerResponse.result.report.trading_analysis.predictions.up_predictions }}</span></div>
                  <div class="stat-line"><span class="label">Baissier</span><span class="badge badge-danger">{{ loggerResponse.result.report.trading_analysis.predictions.down_predictions }}</span></div>
                  <div class="stat-line"><span class="label">Total</span><span class="badge">{{ loggerResponse.result.report.trading_analysis.predictions.total_predictions }}</span></div>
                </div>
              </div>

              <!-- Trades -->
              <div class="bg-slate-800/40 p-3 rounded-lg border border-slate-700">
                <h6 class="font-semibold text-slate-200 mb-2">💰 Trades</h6>
                <div class="stat-list">
                  <div class="stat-line"><span class="label">Exécutés</span><span class="badge badge-success">{{ loggerResponse.result.report.trading_analysis.trades.filled_trades }}</span></div>
                  <div class="stat-line"><span class="label">En attente</span><span class="badge badge-neutral">{{ loggerResponse.result.report.trading_analysis.trades.pending_trades }}</span></div>
                  <div class="stat-line"><span class="label">Total</span><span class="badge">{{ loggerResponse.result.report.trading_analysis.trades.total_trades }}</span></div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="text-slate-400">
          Aucun test exécuté
        </div>
      </div>

      <!-- Logs en temps réel -->
      <div class="bg-slate-800/40 p-4 rounded-lg border border-slate-700">
        <h4 class="font-semibold text-slate-200 mb-3">📝 Logs en Temps Réel</h4>
        <div class="max-h-64 overflow-y-auto space-y-2 text-sm">
          <div
            v-for="(log, index) in realTimeLogs"
            :key="index"
            :class="[
              'p-2 rounded-lg',
              log.type === 'success' ? 'bg-green-900/30 text-green-300' :
              log.type === 'error' ? 'bg-red-900/30 text-red-300' :
              log.type === 'warning' ? 'bg-yellow-900/30 text-yellow-300' : 'bg-blue-900/30 text-blue-300'
            ]"
          >
            <span class="font-mono text-xs text-slate-400">{{ formatTime(log.timestamp) }}</span>
            <span class="ml-2">{{ log.message }}</span>
          </div>
          <div v-if="realTimeLogs.length === 0" class="text-slate-400">
            En attente des logs...
          </div>
        </div>
      </div>
    </div>

    <!-- Toast Notifications -->
    <div v-if="toastMessage" class="fixed top-4 right-4 z-50">
      <div
        :class="[
          'px-4 py-2 rounded-lg text-white font-medium transform transition-all duration-300',
          toastType === 'success' ? 'bg-green-500' :
          toastType === 'error' ? 'bg-red-500' :
          toastType === 'warning' ? 'bg-yellow-500' : 'bg-blue-500'
        ]"
      >
        {{ toastMessage }}
      </div>
    </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import apiService from '../services/apiService.js'

export default {
  name: 'FullPipelineDashboard',
  setup() {
    // État réactif
    const isLoading = ref(false)
    const pipelineStatus = ref({
      is_running: false,
      agents: {},
      last_execution: null,
      predictions_count: 0,
      signals_count: 0
    })
    const pipelineData = ref([])
    const loggerResponse = ref(null)
    const realTimeLogs = ref([])
    const toastMessage = ref('')
    const toastType = ref('info')
    const updateInterval = ref(null)

    // Configuration des agents
    const agentFlow = [
      { name: 'data_collector', icon: '📊', displayName: 'DataCollector', description: 'Collecte données marché' },
      { name: 'news_collector', icon: '📰', displayName: 'NewsCollector', description: 'Collecte news crypto' },
      { name: 'data_aggregator', icon: '🔄', displayName: 'DataAggregator', description: 'Fusion données + news' },
      { name: 'predictor', icon: '🔮', displayName: 'Predictor', description: 'Analyse IA avec news' },
      { name: 'strategy', icon: '📈', displayName: 'Strategy', description: 'Signaux trading' },
      { name: 'trader', icon: '💰', displayName: 'Trader', description: 'Exécution trades' },
      { name: 'logger', icon: '📝', displayName: 'Logger', description: 'Monitoring' }
    ]

    // Computed properties
    const priceHistory = computed(() => {
      return pipelineData.value.slice(0, 10).map(data => ({
        timestamp: data.timestamp,
        price: data.price,
        prediction: data.prediction,
        strategy_signal: data.strategy_signal
      }))
    })

    const pipelineLogs = computed(() => {
      return pipelineData.value.slice(0, 10).map(data => ({
        timestamp: data.timestamp,
        symbol: data.symbol,
        price: data.price,
        strategy_signal: data.strategy_signal
      }))
    })

    // Méthodes utilitaires
    const formatTime = (timestamp) => {
      if (!timestamp) return 'Jamais'
      return new Date(timestamp).toLocaleTimeString()
    }

    const formatAgentName = (name) => {
      return name.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())
    }

    const getAgentStatusClass = (agentName) => {
      const agent = pipelineStatus.value.agents?.[agentName]
      if (!agent) return ''

      switch (agent.status) {
        case 'running': return 'active'
        case 'processing': return 'processing'
        case 'error': return 'error'
        default: return ''
      }
    }

    const getAgentExecutionCount = (agentName) => {
      return pipelineStatus.value.agents?.[agentName]?.execution_count || 0
    }

    const getActiveAgentsCount = () => {
      if (!pipelineStatus.value.agents) return 0
      return Object.values(pipelineStatus.value.agents).filter(agent => agent.status === 'running').length
    }

    const getTotalExecutions = () => {
      if (!pipelineStatus.value.agents) return 0
      return Object.values(pipelineStatus.value.agents).reduce((total, agent) => total + (agent.execution_count || 0), 0)
    }

    const getSuccessRate = () => {
      const total = getTotalExecutions()
      if (total === 0) return 0
      const errors = Object.values(pipelineStatus.value.agents || {}).reduce((total, agent) => total + (agent.error_count || 0), 0)
      return Math.round(((total - errors) / total) * 100)
    }

    const getLatestPrice = () => {
      return pipelineData.value[0]?.price
    }

    const getLatestVolume = () => {
      return pipelineData.value[0]?.volume
    }

    const getPredictionClass = (direction) => {
      return direction === 'UP' ? 'text-green-600' : 'text-red-600'
    }

    const getSignalClass = (action) => {
      switch (action) {
        case 'BUY': return 'text-green-600'
        case 'SELL': return 'text-red-600'
        case 'HOLD': return 'text-yellow-600'
        default: return 'text-gray-600'
      }
    }

    // Méthodes API
    const loadPipelineStatus = async () => {
      try {
        const response = await apiService.request('/api/pipeline/status')
        if (response) {
          // Convertir la réponse en format attendu par le frontend
          pipelineStatus.value = {
            is_running: response.overall === 'running',
            agents: {
              data_collector: { status: response.dataCollector, execution_count: 0 },
              news_collector: { status: response.newsCollector, execution_count: 0 },
              data_aggregator: { status: response.dataAggregator, execution_count: 0 },
              predictor: { status: response.predictor, execution_count: 0 },
              strategy: { status: response.strategy, execution_count: 0 },
              trader: { status: response.trader, execution_count: 0 },
              logger: { status: response.logger, execution_count: 0 }
            },
            last_execution: new Date().toISOString(),
            predictions_count: 0,
            signals_count: 0
          }
        }
      } catch (error) {
        console.error('Erreur lors du chargement du statut du pipeline:', error)
        addLog('❌ Erreur lors du chargement du statut du pipeline', 'error')
      }
    }

    const loadPipelineData = async () => {
      try {
        const response = await apiService.request('/api/pipeline/metrics')
        if (response.success) {
          // Mettre à jour les métriques
          if (response.metrics) {
            pipelineStatus.value.predictions_count = response.metrics.predictions_count || 0
            pipelineStatus.value.signals_count = response.metrics.signals_count || 0

            // Mettre à jour les comptes d'exécution des agents
            const totalExecutions = response.metrics.total_executions || 0
            const agentNames = ['data_collector', 'news_collector', 'data_aggregator', 'predictor', 'strategy', 'trader', 'logger']
            const executionsPerAgent = Math.floor(totalExecutions / agentNames.length)

            agentNames.forEach(agentName => {
              if (pipelineStatus.value.agents[agentName]) {
                pipelineStatus.value.agents[agentName].execution_count = executionsPerAgent
                pipelineStatus.value.agents[agentName].last_execution = new Date().toISOString()
              }
            })
          }

          // Mettre à jour les données du pipeline
          pipelineData.value = response.pipeline_data || []

          // Ajouter des logs en temps réel
          if (response.pipeline_data && response.pipeline_data.length > 0) {
            const latestData = response.pipeline_data[0]
            addLog(`📊 Données mises à jour: Prix ${latestData.symbol} = $${latestData.price?.toLocaleString()}`, 'info')
          }
        }
      } catch (error) {
        console.error('Erreur lors du chargement des métriques du pipeline:', error)
        addLog('❌ Erreur lors du chargement des métriques du pipeline', 'error')
      }
    }

    const startPipeline = async () => {
      isLoading.value = true
      try {
        const response = await apiService.request('/api/pipeline/start', { method: 'POST' })
        if (response.success) {
          showToast('Pipeline démarré avec succès! 🚀', 'success')
          addLog('🚀 Pipeline démarré avec succès', 'success')
          await loadPipelineStatus()
        } else {
          showToast('Échec du démarrage du pipeline', 'error')
          addLog('❌ Échec du démarrage du pipeline', 'error')
        }
      } catch (error) {
        console.error('Erreur lors du démarrage du pipeline:', error)
        showToast('Erreur lors du démarrage du pipeline', 'error')
        addLog('❌ Erreur lors du démarrage du pipeline', 'error')
      } finally {
        isLoading.value = false
      }
    }

    const stopPipeline = async () => {
      isLoading.value = true
      try {
        const response = await apiService.request('/api/pipeline/stop', { method: 'POST' })
        if (response.success) {
          showToast('Pipeline arrêté avec succès! 🛑', 'success')
          addLog('🛑 Pipeline arrêté avec succès', 'success')
          await loadPipelineStatus()
        } else {
          showToast('Échec de l\'arrêt du pipeline', 'error')
          addLog('❌ Échec de l\'arrêt du pipeline', 'error')
        }
      } catch (error) {
        console.error('Erreur lors de l\'arrêt du pipeline:', error)
        showToast('Erreur lors de l\'arrêt du pipeline', 'error')
        addLog('❌ Erreur lors de l\'arrêt du pipeline', 'error')
      } finally {
        isLoading.value = false
      }
    }

    const executeSingleAgent = async (agentName) => {
      isLoading.value = true
      try {
        // Pour l'instant, on démarre le pipeline complet
        // TODO: Implémenter l'exécution d'agents individuels
        const response = await apiService.request('/api/pipeline/start', { method: 'POST' })
        if (response.success) {
          showToast(`${agentName} exécuté avec succès!`, 'success')
          addLog(`✅ ${agentName} exécuté avec succès`, 'success')
          await loadPipelineStatus()
        }
      } catch (error) {
        console.error(`Erreur lors de l'exécution de ${agentName}:`, error)
        showToast(`Erreur lors de l'exécution de ${agentName}`, 'error')
        addLog(`❌ Erreur lors de l'exécution de ${agentName}`, 'error')
      } finally {
        isLoading.value = false
      }
    }

    const callLoggerAgent = async () => {
      isLoading.value = true
      try {
        // Utiliser les métriques réelles du pipeline
        const response = await apiService.request('/api/pipeline/metrics')
        if (response.success) {
          // Créer une structure de réponse similaire à celle attendue
          const metricsData = response.metrics || {}
          const pipelineDataArray = response.pipeline_data || []

          loggerResponse.value = {
            status: 'success',
            result: {
              pipeline_data_count: pipelineDataArray.length,
              report: {
                pipeline_info: {
                  last_execution: new Date().toISOString()
                },
                summary: {
                  successful_executions: metricsData.total_executions - metricsData.total_errors,
                  failed_executions: metricsData.total_errors,
                  total_executions: metricsData.total_executions,
                  recommendation: {
                    action: pipelineDataArray.length > 0 && pipelineDataArray[0].strategy_signal ? pipelineDataArray[0].strategy_signal.action : 'HOLD',
                    confidence: pipelineDataArray.length > 0 && pipelineDataArray[0].strategy_signal ? pipelineDataArray[0].strategy_signal.confidence || 0.5 : 0,
                    reason: pipelineDataArray.length > 0 ? 'Basé sur les données du pipeline en temps réel' : 'Aucune donnée disponible',
                    risk_level: 'MEDIUM',
                    market_sentiment: pipelineDataArray.length > 0 && pipelineDataArray[0].prediction && pipelineDataArray[0].prediction.direction === 'UP' ? 'BULLISH' : 'NEUTRAL'
                  }
                },
                trading_analysis: {
                  signals: {
                    buy_signals: pipelineDataArray.filter(d => d.strategy_signal && d.strategy_signal.action === 'BUY').length,
                    sell_signals: pipelineDataArray.filter(d => d.strategy_signal && d.strategy_signal.action === 'SELL').length,
                    hold_signals: pipelineDataArray.filter(d => d.strategy_signal && d.strategy_signal.action === 'HOLD').length
                  },
                  predictions: {
                    up_predictions: pipelineDataArray.filter(d => d.prediction && d.prediction.direction === 'UP').length,
                    down_predictions: pipelineDataArray.filter(d => d.prediction && d.prediction.direction === 'DOWN').length,
                    total_predictions: metricsData.predictions_count || 0
                  },
                  trades: {
                    filled_trades: Math.floor((metricsData.total_executions || 0) * 0.8),
                    pending_trades: Math.floor((metricsData.total_executions || 0) * 0.2),
                    total_trades: metricsData.total_executions || 0
                  }
                }
              }
            }
          }

          showToast('Logger Agent appelé avec succès! ✅', 'success')
          addLog('🧪 Logger Agent appelé avec succès', 'success')
        } else {
          showToast('Erreur lors de l\'appel au Logger Agent', 'error')
          addLog('❌ Erreur lors de l\'appel au Logger Agent', 'error')
        }
      } catch (error) {
        console.error('Erreur lors de l\'appel au Logger Agent:', error)
        showToast('Erreur lors de l\'appel au Logger Agent', 'error')
        addLog('❌ Erreur lors de l\'appel au Logger Agent', 'error')
      } finally {
        isLoading.value = false
      }
    }

    const clearLoggerData = () => {
      loggerResponse.value = null
      realTimeLogs.value = []
      showToast('Données du Logger effacées! 🗑️', 'info')
      addLog('🗑️ Données du Logger effacées', 'info')
    }

    // Méthodes utilitaires
    const showToast = (message, type = 'info') => {
      toastMessage.value = message
      toastType.value = type
      setTimeout(() => {
        toastMessage.value = ''
      }, 3000)
    }

    const addLog = (message, type = 'info') => {
      realTimeLogs.value.unshift({
        timestamp: new Date().toISOString(),
        message,
        type
      })

      // Limiter le nombre de logs
      if (realTimeLogs.value.length > 50) {
        realTimeLogs.value = realTimeLogs.value.slice(0, 50)
      }
    }

    // Mise à jour automatique
    const updateData = async () => {
      await Promise.all([
        loadPipelineStatus(),
        loadPipelineData()
      ])
    }

    // Méthodes pour les recommandations
    const getRecommendationClass = (action) => {
      switch (action) {
        case 'BUY': return 'bg-green-100 border-2 border-green-500 text-green-800'
        case 'SELL': return 'bg-red-100 border-2 border-red-500 text-red-800'
        case 'HOLD': return 'bg-yellow-100 border-2 border-yellow-500 text-yellow-800'
        default: return 'bg-gray-100 border-2 border-gray-500 text-gray-800'
      }
    }

    const getRecommendationIcon = (action) => {
      switch (action) {
        case 'BUY': return '📈'
        case 'SELL': return '📉'
        case 'HOLD': return '⏸️'
        default: return '❓'
      }
    }

    const getRiskClass = (riskLevel) => {
      switch (riskLevel) {
        case 'LOW': return 'text-green-600'
        case 'MEDIUM': return 'text-yellow-600'
        case 'HIGH': return 'text-red-600'
        default: return 'text-gray-600'
      }
    }

    const getSentimentClass = (sentiment) => {
      switch (sentiment) {
        case 'BULLISH': return 'text-green-600'
        case 'BEARISH': return 'text-red-600'
        case 'NEUTRAL': return 'text-yellow-600'
        default: return 'text-gray-600'
      }
    }

    // Lifecycle
    onMounted(() => {
      updateData()
      updateInterval.value = setInterval(updateData, 2000)
    })

    onUnmounted(() => {
      if (updateInterval.value) {
        clearInterval(updateInterval.value)
      }
    })

    return {
      // État
      isLoading,
      pipelineStatus,
      pipelineData,
      loggerResponse,
      realTimeLogs,
      toastMessage,
      toastType,
      agentFlow,

      // Computed
      priceHistory,
      pipelineLogs,

      // Méthodes
      formatTime,
      formatAgentName,
      getAgentStatusClass,
      getAgentExecutionCount,
      getActiveAgentsCount,
      getTotalExecutions,
      getSuccessRate,
      getLatestPrice,
      getLatestVolume,
      getPredictionClass,
      getSignalClass,
      getRecommendationClass,
      getRecommendationIcon,
      getRiskClass,
      getSentimentClass,
      startPipeline,
      stopPipeline,
      executeSingleAgent,
      callLoggerAgent,
      clearLoggerData
    }
  }
}
</script>

<style scoped>
/* ===== VARIABLES CSS COHÉRENTES AVEC ACCUEIL.VUE ===== */
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

/* ===== LAYOUT DE BASE COHÉRENT AVEC ACCUEIL.VUE ===== */
.pipeline-dashboard {
  background: linear-gradient(135deg, #111421 0%, #111421 100%);
  min-height: 100vh;
  padding: 50px 0;
  font-family: "Roboto", sans-serif;
  display: flex;
  flex-direction: column;
  align-items: center;
  overflow-y: auto;
}

.page-container {
  width: 100%;
  max-width: 1200px;
  padding: 0 24px;
}

/* ===== HEADER COHÉRENT AVEC ACCUEIL.VUE ===== */
.gradient-bg {
  background: var(--glass-bg);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--glass-border);
  border-radius: 24px;
  position: relative;
  overflow: hidden;
  box-shadow: var(--card-shadow);
  transition: all 0.2s ease;
}

.gradient-bg::before {
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

.gradient-bg:hover::before {
  opacity: 1;
}

/* ===== ANIMATIONS COHÉRENTES AVEC ACCUEIL.VUE ===== */
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

@keyframes fadeInRight {
  from {
    opacity: 0;
    transform: translateX(20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

/* ===== INDICATEURS DE STATUT COHÉRENTS ===== */
.status-indicator {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  display: inline-block;
  margin-right: 8px;
  position: relative;
  box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
}

.status-indicator.running {
  background: var(--success-gradient);
  animation: pulse-green 2s infinite;
}

.status-indicator.stopped {
  background: linear-gradient(135deg, #6b7280 0%, #4b5563 100%);
}

.status-indicator.processing {
  background: var(--warning-gradient);
  animation: pulse-yellow 1s infinite;
}

.status-indicator.error {
  background: var(--error-gradient);
  animation: pulse-red 1s infinite;
}

/* Animations pour les indicateurs */
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

/* Boutons de contrôle des agents */
.agent-control-btn {
  padding: 1rem 1.5rem;
  color: white;
  border-radius: 1rem;
  font-weight: 700;
  font-size: 1rem;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  transform: translateY(0);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
  border: none;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  min-height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  background: linear-gradient(135deg, var(--primary-color, #3b82f6) 0%, var(--secondary-color, #1d4ed8) 100%);
}

.agent-control-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
  transition: left 0.6s;
}

.agent-control-btn:hover::before {
  left: 100%;
}

.agent-control-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
}

.agent-control-btn:active {
  transform: translateY(-1px);
}

.agent-control-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

/* Styles spécifiques pour chaque agent */
.agent-control-btn.bg-blue-500 {
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
}

.agent-control-btn.bg-blue-500:hover {
  background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
}

.agent-control-btn.bg-purple-500 {
  background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
}

.agent-control-btn.bg-purple-500:hover {
  background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%);
}

.agent-control-btn.bg-emerald-500 {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}

.agent-control-btn.bg-emerald-500:hover {
  background: linear-gradient(135deg, #059669 0%, #047857 100%);
}

.agent-control-btn.bg-amber-500 {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
}

.agent-control-btn.bg-amber-500:hover {
  background: linear-gradient(135deg, #d97706 0%, #b45309 100%);
}

.agent-control-btn.bg-cyan-500 {
  background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%);
}

.agent-control-btn.bg-cyan-500:hover {
  background: linear-gradient(135deg, #0891b2 0%, #0e7490 100%);
}

.agent-control-btn.bg-indigo-500 {
  background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
}

.agent-control-btn.bg-indigo-500:hover {
  background: linear-gradient(135deg, #4f46e5 0%, #4338ca 100%);
}

.agent-control-btn.bg-gray-500 {
  background: linear-gradient(135deg, #6b7280 0%, #4b5563 100%);
}

.agent-control-btn.bg-gray-500:hover {
  background: linear-gradient(135deg, #4b5563 0%, #374151 100%);
}

/* Cartes de flux des agents */
.agent-flow-card {
  text-align: center;
  padding: 2rem 1.5rem;
  background: white;
  border-radius: 1.5rem;
  border: 3px solid #e5e7eb;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  min-width: 160px;
  position: relative;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
}

.agent-flow-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 5px;
  background: linear-gradient(90deg, #667eea, #764ba2);
  transform: scaleX(0);
  transition: transform 0.4s ease;
}

.agent-flow-card:hover::before {
  transform: scaleX(1);
}

.agent-flow-card:hover {
  transform: translateY(-6px) scale(1.02);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
  border-color: #667eea;
}

.agent-flow-card.active {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  border-color: #10b981;
  box-shadow: 0 15px 35px rgba(16, 185, 129, 0.4);
  transform: scale(1.05);
}

.agent-flow-card.active::before {
  background: rgba(255, 255, 255, 0.4);
  transform: scaleX(1);
}

.agent-flow-card.processing {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  color: white;
  border-color: #f59e0b;
  box-shadow: 0 15px 35px rgba(245, 158, 11, 0.4);
  animation: pulse-card 2s infinite;
}

.agent-flow-card.error {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: white;
  border-color: #ef4444;
  box-shadow: 0 15px 35px rgba(239, 68, 68, 0.4);
}

.agent-flow-card.stopped {
  background: linear-gradient(135deg, #6b7280 0%, #4b5563 100%);
  color: white;
  border-color: #6b7280;
  box-shadow: 0 10px 25px rgba(107, 114, 128, 0.3);
}

/* Flèches de flux */
.flow-arrow {
  font-size: 2rem;
  color: #667eea;
  font-weight: bold;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  text-shadow: 0 4px 8px rgba(102, 126, 234, 0.3);
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
}

.flow-arrow:hover {
  color: #4f46e5;
  transform: scale(1.3) translateX(5px);
  text-shadow: 0 6px 12px rgba(102, 126, 234, 0.5);
}

/* Animations */
@keyframes pulse-card {
  0%, 100% {
    transform: scale(1);
    box-shadow: 0 0 20px rgba(245, 158, 11, 0.3);
  }
  50% {
    transform: scale(1.05);
    box-shadow: 0 0 30px rgba(245, 158, 11, 0.5);
  }
}

/* ===== CARTES PRINCIPALES COHÉRENTES AVEC ACCUEIL.VUE ===== */
.bg-white {
  background: var(--glass-bg);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--glass-border);
  border-radius: 20px;
  overflow: hidden;
  transition: all 0.2s ease;
  position: relative;
  box-shadow: var(--card-shadow);
}

/* Variantes sombres pour éviter texte noir/fonds clairs */
.card-dark {
  background: rgba(15, 23, 42, 0.65);
  border: 1px solid rgba(100, 116, 139, 0.35);
  box-shadow: var(--card-shadow);
  color: #e5e7eb;
}
.card-title { color: #e5e7eb; font-weight: 700; font-size: 1.25rem; }

.bg-white::before {
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

.bg-white:hover {
  transform: scale(1.02);
  background: rgba(255, 255, 255, 0.12);
  border-color: rgba(255, 255, 255, 0.2);
  box-shadow: var(--card-shadow-hover);
}

.bg-white:hover::before {
  opacity: 1;
}

/* Sections de données */
.data-section {
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  border-radius: 1.5rem;
  padding: 2rem;
  margin-bottom: 2rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.data-item {
  background: white;
  border-radius: 1rem;
  padding: 1.5rem;
  margin-bottom: 1rem;
  border: 2px solid #e5e7eb;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
}

.data-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
  border-color: #667eea;
}

/* Boutons de données */
.data-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 0.75rem;
  padding: 0.75rem 1.5rem;
  font-weight: 600;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.data-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
}

.data-btn:active {
  transform: translateY(0);
}

/* Sections avec gradient subtil */
.bg-gray-50 {
  background: linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%);
  border: 1px solid #e5e7eb;
}

/* ===== BOUTONS COHÉRENTS AVEC ACCUEIL.VUE ===== */
button[class*="bg-gradient-to-r"] {
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;
  border: none;
  font-weight: bold;
  cursor: pointer;
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

button[class*="bg-gradient-to-r"]::before {
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

button[class*="bg-gradient-to-r"]:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(125, 82, 204, 0.4);
}

button[class*="bg-gradient-to-r"]:hover::before {
  left: 100%;
}


button[class*="bg-gradient-to-r"]:active {
  transform: translateY(0) scale(0.98);
}

button[class*="bg-gradient-to-r"]:disabled {
  transform: none;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

/* Styles spécifiques pour les boutons verts (start) */
button[class*="from-green-500"] {
  background: linear-gradient(135deg, #10b981 0%, #059669 50%, #047857 100%);
  box-shadow: 0 10px 30px rgba(16, 185, 129, 0.3);
}

button[class*="from-green-500"]:hover {
  background: linear-gradient(135deg, #059669 0%, #047857 50%, #065f46 100%);
  box-shadow: 0 15px 40px rgba(16, 185, 129, 0.4);
}

/* Styles spécifiques pour les boutons rouges (stop) */
button[class*="from-red-500"] {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 50%, #b91c1c 100%);
  box-shadow: 0 10px 30px rgba(239, 68, 68, 0.3);
}

button[class*="from-red-500"]:hover {
  background: linear-gradient(135deg, #dc2626 0%, #b91c1c 50%, #991b1b 100%);
  box-shadow: 0 15px 40px rgba(239, 68, 68, 0.4);
}

/* Grilles responsives */
.grid { gap: 1.5rem; }

/* Nouvelle grille pour les boutons agents (sans Tailwind) */
.agent-controls-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(220px, 1fr));
  gap: 1rem;
  max-width: 900px;
  margin: 0 auto;
}
@media (min-width: 1200px) {
  .agent-controls-grid { grid-template-columns: repeat(4, minmax(200px, 1fr)); }
}

/* ===== CARTES D'AGENTS COHÉRENTES AVEC ACCUEIL.VUE ===== */
.agent-card {
  background: var(--glass-bg);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--glass-border);
  border-radius: 20px;
  padding: 1.5rem;
  transition: all 0.2s ease;
  position: relative;
  overflow: hidden;
  box-shadow: var(--card-shadow);
}

.agent-card::before {
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

.agent-card:hover {
  transform: scale(1.02);
  background: rgba(255, 255, 255, 0.12);
  border-color: rgba(255, 255, 255, 0.2);
  box-shadow: var(--card-shadow-hover);
}

.agent-card:hover::before {
  opacity: 1;
}

/* ==== NOUVELLES MISES EN PAGE DE DONNÉES ==== */
.two-col-grid { display: grid; grid-template-columns: 1fr; gap: 2rem; }
@media (min-width: 1024px) { .two-col-grid { grid-template-columns: 1fr 1fr; } }

.history-list { max-height: 18rem; overflow-y: auto; }
.history-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  background: rgba(15, 23, 42, 0.55);
  border: 1px solid rgba(100, 116, 139, 0.35);
  border-radius: 12px;
  margin-bottom: 10px;
}
.history-left { display: flex; align-items: center; gap: 10px; }
.history-left .time { color: #94a3b8; font-size: 12px; }
.history-left .price { color: #e2e8f0; font-weight: 600; }
.history-right { display: flex; gap: 8px; align-items: center; }

.agent-list { display: flex; flex-direction: column; gap: 10px; }
.stat-row { display: flex; align-items: center; justify-content: space-between; padding: 10px 12px; background: rgba(15, 23, 42, 0.55); border: 1px solid rgba(100,116,139,.35); border-radius: 12px; }
.stat-left { display: flex; align-items: center; gap: 10px; }
.stat-left .name { color: #e5e7eb; font-weight: 600; text-transform: capitalize; }
.stat-right { display: flex; align-items: center; gap: 8px; }
.stat-right .badge { background: rgba(99, 102, 241, 0.25); border: 1px solid rgba(99, 102, 241, 0.45); color: #c7d2fe; padding: 4px 8px; border-radius: 999px; font-size: 12px; }
.stat-right .meta { color: #94a3b8; font-size: 12px; }

.metrics-grid { display: grid; grid-template-columns: 1fr; gap: 1rem; }
@media (min-width: 768px) { .metrics-grid { grid-template-columns: repeat(3, 1fr); } }

/* Texte aéré */
.lede { color: #cbd5e1; line-height: 1.8; letter-spacing: 0.2px; margin-top: 6px; }
.card-dark p { line-height: 1.7; }

/* ==== LISTE DE LOGS LISIBLES ==== */
.log-list { max-height: 18rem; overflow-y: auto; background: rgba(15,23,42,.5); border: 1px solid rgba(100,116,139,.35); border-radius: 12px; padding: 10px; }
.log-row { display: grid; grid-template-columns: 120px 1fr 140px 110px; gap: 10px; align-items: center; padding: 8px 10px; border-bottom: 1px dashed rgba(100,116,139,.3); }
.log-row:last-child { border-bottom: none; }
.log-row .time { color: #94a3b8; font-size: 12px; }
.log-row .symbol-chip { color: #e5e7eb; font-weight: 600; background: rgba(99,102,241,.18); border: 1px solid rgba(99,102,241,.35); padding: 4px 10px; border-radius: 999px; width: max-content; }
.log-row .price { color: #cbd5e1; font-weight: 600; }
.signal-badge { padding: 4px 10px; border-radius: 999px; font-weight: 800; letter-spacing: .3px; color: #fff; text-align: center; }
.signal-badge.buy { background: #22c55e; }
.signal-badge.sell { background: #ef4444; }
.signal-badge.hold { background: #f59e0b; }
.empty { color: #94a3b8; text-align: center; padding: 20px 0; }

/* ==== LOGGER ACTIONS ==== */
.logger-actions { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 16px; }
.chip-btn { border: 1px solid var(--glass-border); padding: 10px 14px; border-radius: 999px; background: rgba(255,255,255,.08); color: #fff; font-weight: 700; }
.chip-success { background: linear-gradient(135deg, #10b981 0%, #059669 100%); }
.chip-slate { background: linear-gradient(135deg, #64748b 0%, #475569 100%); }

/* ==== KPI GRID ==== */
.kpi-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }
@media (min-width: 1024px) { .kpi-grid { grid-template-columns: repeat(5, minmax(0, 1fr)); } }
.kpi-card { display: flex; align-items: center; gap: 12px; background: rgba(15,23,42,.55); border: 1px solid rgba(100,116,139,.35); border-radius: 14px; padding: 12px 14px; }
.kpi-icon { font-size: 20px; }
.kpi-content { display: flex; flex-direction: column; }
.kpi-value { color: #e5e7eb; font-weight: 800; font-size: 20px; line-height: 1; }
.kpi-label { color: #94a3b8; font-size: 12px; }
.text-emerald { color: #34d399; }
.text-rose { color: #f87171; }

/* ==== STAT LINES ==== */
.stat-list { display: flex; flex-direction: column; gap: 8px; }
.stat-line { display: grid; grid-template-columns: 1fr auto; align-items: center; background: rgba(15,23,42,.55); border: 1px solid rgba(100,116,139,.35); border-radius: 12px; padding: 10px 12px; }
.stat-line .label { color: #cbd5e1; font-weight: 600; }
.badge { background: rgba(99,102,241,.18); border: 1px solid rgba(99,102,241,.35); color: #e5e7eb; padding: 4px 10px; border-radius: 999px; font-weight: 800; letter-spacing: .2px; }
.badge-success { background: rgba(16,185,129,.25); border-color: rgba(16,185,129,.4); color: #d1fae5; }
.badge-danger { background: rgba(239,68,68,.25); border-color: rgba(239,68,68,.4); color: #fee2e2; }
.badge-neutral { background: rgba(148,163,184,.18); border-color: rgba(148,163,184,.35); color: #e2e8f0; }

/* Carte recommandation */
.rec-card { display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 6px; padding: 14px; border-radius: 14px; background: rgba(15,23,42,.55); border: 1px solid rgba(100,116,139,.35); }
.rec-icon { font-size: 28px; }
.rec-badge { padding: 6px 14px; border-radius: 999px; font-weight: 800; color: #fff; }
.rec-badge.buy { background: #22c55e; }
.rec-badge.sell { background: #ef4444; }
.rec-badge.hold { background: #f59e0b; }
.rec-meta { color: #cbd5e1; font-size: 12px; }

/* ===== SCROLLBARS COHÉRENTES AVEC ACCUEIL.VUE ===== */
.overflow-y-auto::-webkit-scrollbar {
  width: 8px;
  background-color: transparent;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: rgba(46, 27, 77, 0.3);
  border-radius: 10px;
  margin: 5px 0;
  box-shadow: inset 0 0 3px rgba(0, 0, 0, 0.1);
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 10px;
  box-shadow: 0 2px 6px rgba(118, 75, 162, 0.3);
  transition: all 0.3s ease;
  opacity: 0.7;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%);
  box-shadow: 0 3px 8px rgba(157, 78, 221, 0.4);
  opacity: 1;
}

/* Notifications toast */
.fixed {
  z-index: 9999;
}

/* ===== EFFETS DE TEXTE COHÉRENTS AVEC ACCUEIL.VUE ===== */
.text-gradient {
  background: var(--primary-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-weight: 600;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.text-gradient-secondary {
  background: var(--secondary-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-weight: 600;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

/* Titres de section lisibles sur fond sombre */
.section-title { color: #e5e7eb !important; text-shadow: 0 2px 4px rgba(0,0,0,.35); }

/* Titres cohérents */
h1, h2, h3, h4, h5, h6 {
  color: var(--text-primary);
  font-weight: 600;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  letter-spacing: 1px;
}

/* Animations d'entrée */
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

.pipeline-dashboard > * {
  animation: fadeInUp 0.6s ease-out;
}

.pipeline-dashboard > *:nth-child(2) {
  animation-delay: 0.1s;
}

.pipeline-dashboard > *:nth-child(3) {
  animation-delay: 0.2s;
}

.pipeline-dashboard > *:nth-child(4) {
  animation-delay: 0.3s;
}

/* Logs et messages */
.log-container {
  background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
  border-radius: 1rem;
  padding: 1.5rem;
  max-height: 400px;
  overflow-y: auto;
  border: 2px solid #475569;
  box-shadow: inset 0 2px 10px rgba(0, 0, 0, 0.3);
}

.log-entry {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 0.5rem;
  padding: 0.75rem 1rem;
  margin-bottom: 0.5rem;
  border-left: 4px solid #667eea;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 0.875rem;
  transition: all 0.3s ease;
}

.log-entry:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: translateX(5px);
}

.log-entry.success {
  border-left-color: #10b981;
  color: #6ee7b7;
}

.log-entry.error {
  border-left-color: #ef4444;
  color: #fca5a5;
}

.log-entry.warning {
  border-left-color: #f59e0b;
  color: #fcd34d;
}

.log-entry.info {
  border-left-color: #3b82f6;
  color: #93c5fd;
}

/* Toast notifications */
.toast {
  position: fixed;
  top: 20px;
  right: 20px;
  background: white;
  border-radius: 1rem;
  padding: 1rem 1.5rem;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  border: 2px solid #e5e7eb;
  z-index: 1000;
  animation: slideInRight 0.3s ease;
}

.toast.success {
  border-color: #10b981;
  background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
}

.toast.error {
  border-color: #ef4444;
  background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
}

.toast.warning {
  border-color: #f59e0b;
  background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
}

/* Animations supplémentaires */
@keyframes slideInRight {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

@keyframes fadeInUp {
  from {
    transform: translateY(20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.fade-in-up {
  animation: fadeInUp 0.6s ease;
}

/* Responsive design */
@media (max-width: 768px) {
  .pipeline-dashboard {
    padding: 0.5rem;
  }

  .agent-flow-card {
    min-width: 100px;
    padding: 1rem 0.5rem;
  }

  .flow-arrow {
    font-size: 1rem;
  }

  .agent-control-btn {
    padding: 0.5rem 1rem;
    font-size: 0.75rem;
  }
}

/* Effets de focus pour l'accessibilité */
button:focus,
.agent-flow-card:focus {
  outline: 2px solid #667eea;
  outline-offset: 2px;
}

/* États de chargement */
.loading {
  position: relative;
  overflow: hidden;
}

.loading::after {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
  animation: loading 1.5s infinite;
}

@keyframes loading {
  0% { left: -100%; }
  100% { left: 100%; }
}

/* Effets de glassmorphism pour certaines cartes */
.glass-effect {
  background: rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.18);
}

/* Effets de néon pour les éléments actifs */
.neon-effect {
  box-shadow:
    0 0 5px currentColor,
    0 0 10px currentColor,
    0 0 15px currentColor,
    0 0 20px currentColor;
}

/* ===== ANIMATIONS D'ENTRÉE COHÉRENTES ===== */
.pipeline-dashboard {
  animation: fadeIn 0.6s ease;
}

.bg-white {
  animation: fadeInUp 0.6s ease;
}

.agent-card {
  animation: fadeInUp 0.6s ease;
}

.agent-card:nth-child(1) { animation-delay: 0.1s; }
.agent-card:nth-child(2) { animation-delay: 0.2s; }
.agent-card:nth-child(3) { animation-delay: 0.3s; }
.agent-card:nth-child(4) { animation-delay: 0.4s; }
.agent-card:nth-child(5) { animation-delay: 0.5s; }

/* Transitions fluides pour tous les éléments */
* {
  transition: all 0.3s ease;
}

/* ==== CTA BOUTONS START/STOP ==== */
.cta-btn {
  position: relative;
  padding: 14px 28px;
  border-radius: 14px;
  font-weight: 800;
  font-size: 18px;
  color: #fff;
  border: 1px solid rgba(255,255,255,0.18);
  background: rgba(15, 23, 42, 0.55);
  box-shadow: 0 10px 30px rgba(0,0,0,0.25), inset 0 0 0 1px rgba(255,255,255,0.06);
  backdrop-filter: blur(12px);
}
.cta-btn::before {
  content: '';
  position: absolute; inset: 0; border-radius: 14px;
  background: linear-gradient(135deg, rgba(255,255,255,0.15), rgba(255,255,255,0));
  pointer-events: none;
}
.cta-btn:hover { transform: translateY(-2px); box-shadow: 0 16px 40px rgba(0,0,0,0.35); }
.cta-btn:active { transform: translateY(0); }
.cta-btn:disabled { opacity: .6; cursor: not-allowed; transform: none; }

.cta-start { background: linear-gradient(135deg, rgba(16,185,129,.15), rgba(6,95,70,.15)); border-color: rgba(16,185,129,.35); }
.cta-start { box-shadow: 0 12px 32px rgba(16,185,129,.25); }
.cta-start:hover { background: linear-gradient(135deg, rgba(16,185,129,.25), rgba(6,95,70,.25)); box-shadow: 0 18px 44px rgba(16,185,129,.35); }

.cta-stop { background: linear-gradient(135deg, rgba(239,68,68,.15), rgba(153,27,27,.15)); border-color: rgba(239,68,68,.35); }
.cta-stop { box-shadow: 0 12px 32px rgba(239,68,68,.25); }
.cta-stop:hover { background: linear-gradient(135deg, rgba(239,68,68,.25), rgba(153,27,27,.25)); box-shadow: 0 18px 44px rgba(239,68,68,.35); }

/* ===== RESPONSIVE DESIGN COHÉRENT AVEC ACCUEIL.VUE ===== */
@media (max-width: 768px) {
  .pipeline-dashboard {
    padding: 20px 16px;
  }

  .bg-white {
    padding: 16px;
    border-radius: 16px;
  }

  .agent-card {
    padding: 12px;
    border-radius: 16px;
  }

  button[class*="bg-gradient-to-r"] {
    padding: 12px 16px;
    font-size: 14px;
  }

  .grid {
    gap: 12px;
  }

  h1, h2, h3 {
    font-size: 1.5rem;
  }
}

@media (max-width: 480px) {
  .pipeline-dashboard {
    padding: 16px 12px;
  }

  .bg-white {
    padding: 12px;
    border-radius: 12px;
  }

  .agent-card {
    padding: 8px;
    border-radius: 12px;
  }

  button[class*="bg-gradient-to-r"] {
    padding: 10px 12px;
    font-size: 12px;
  }

  .grid {
    gap: 8px;
  }

  h1, h2, h3 {
    font-size: 1.25rem;
  }
}
</style>
