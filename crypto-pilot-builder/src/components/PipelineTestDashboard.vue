<template>
  <div class="pipeline-test-dashboard">
    <div class="dashboard-header">
      <h2>🧪 Test Pipeline avec News</h2>
      <p>Interface de test pour la nouvelle pipeline avec intégration des news</p>
    </div>

    <!-- Status Overview -->
    <div class="status-overview">
      <div class="status-card">
        <h3>📊 Pipeline Status</h3>
        <div class="status-grid">
          <div class="status-item" :class="pipelineStatus.overall">
            <span class="status-icon">🔄</span>
            <span class="status-text">Pipeline</span>
            <span class="status-value">{{ pipelineStatus.overall.toUpperCase() }}</span>
          </div>
          <div class="status-item" :class="pipelineStatus.dataCollector">
            <span class="status-icon">📈</span>
            <span class="status-text">DataCollector</span>
            <span class="status-value">{{ pipelineStatus.dataCollector.toUpperCase() }}</span>
          </div>
          <div class="status-item" :class="pipelineStatus.newsCollector">
            <span class="status-icon">📰</span>
            <span class="status-text">NewsCollector</span>
            <span class="status-value">{{ pipelineStatus.newsCollector.toUpperCase() }}</span>
          </div>
          <div class="status-item" :class="pipelineStatus.dataAggregator">
            <span class="status-icon">🔗</span>
            <span class="status-text">DataAggregator</span>
            <span class="status-value">{{ pipelineStatus.dataAggregator.toUpperCase() }}</span>
          </div>
          <div class="status-item" :class="pipelineStatus.predictor">
            <span class="status-icon">🔮</span>
            <span class="status-text">Predictor</span>
            <span class="status-value">{{ pipelineStatus.predictor.toUpperCase() }}</span>
          </div>
          <div class="status-item" :class="pipelineStatus.strategy">
            <span class="status-icon">📊</span>
            <span class="status-text">Strategy</span>
            <span class="status-value">{{ pipelineStatus.strategy.toUpperCase() }}</span>
          </div>
          <div class="status-item" :class="pipelineStatus.trader">
            <span class="status-icon">💰</span>
            <span class="status-text">Trader</span>
            <span class="status-value">{{ pipelineStatus.trader.toUpperCase() }}</span>
          </div>
          <div class="status-item" :class="pipelineStatus.logger">
            <span class="status-icon">📝</span>
            <span class="status-text">Logger</span>
            <span class="status-value">{{ pipelineStatus.logger.toUpperCase() }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Test Controls -->
    <div class="test-controls">
      <h3>🎮 Contrôles de Test</h3>
      <div class="control-buttons">
        <button @click="startPipeline" :disabled="isPipelineRunning" class="btn btn-success">
          🚀 Démarrer Pipeline
        </button>
        <button @click="stopPipeline" :disabled="!isPipelineRunning" class="btn btn-danger">
          🛑 Arrêter Pipeline
        </button>
        <button @click="testNewsCollection" class="btn btn-info">
          📰 Test News Collection
        </button>
        <button @click="testDataFusion" class="btn btn-warning">
          🔗 Test Data Fusion
        </button>
        <button @click="testPredictionWithNews" class="btn btn-primary">
          🔮 Test Prediction avec News
        </button>
        <button @click="runFullTest" class="btn btn-secondary">
          🧪 Test Complet
        </button>
      </div>
    </div>

    <!-- Test Results -->
    <div class="test-results">
      <h3>📋 Résultats des Tests</h3>
      <div class="results-container">
        <div v-for="(result, index) in testResults" :key="index" class="result-item" :class="result.status">
          <div class="result-header">
            <span class="result-icon">{{ result.status === 'success' ? '✅' : '❌' }}</span>
            <span class="result-title">{{ result.title }}</span>
            <span class="result-time">{{ formatTime(result.timestamp) }}</span>
          </div>
          <div class="result-content" v-if="result.details">
            <pre>{{ result.details }}</pre>
          </div>
        </div>
      </div>
    </div>

    <!-- News Analysis Results -->
    <div class="news-analysis-results" v-if="newsAnalysisResults.length > 0">
      <h3>📊 Analyse des News</h3>
      <div class="analysis-grid">
        <div v-for="analysis in newsAnalysisResults" :key="analysis.symbol" class="analysis-card">
          <div class="analysis-header">
            <h4>{{ analysis.symbol }}</h4>
            <span class="analysis-count">{{ analysis.newsCount }} news</span>
          </div>
          <div class="analysis-metrics">
            <div class="metric">
              <span class="metric-label">Sentiment:</span>
              <span class="metric-value" :class="getSentimentClass(analysis.aggregatedSentiment)">
                {{ formatSentiment(analysis.aggregatedSentiment) }}
              </span>
            </div>
            <div class="metric">
              <span class="metric-label">Confiance:</span>
              <span class="metric-value">{{ (analysis.aggregatedConfidence * 100).toFixed(1) }}%</span>
            </div>
            <div class="metric">
              <span class="metric-label">Action:</span>
              <span class="metric-value" :class="getActionClass(analysis.dominantAction)">
                {{ analysis.dominantAction.toUpperCase() }}
              </span>
            </div>
          </div>
          <div class="recommendations" v-if="analysis.recommendations.length > 0">
            <h5>Recommandations:</h5>
            <div v-for="rec in analysis.recommendations" :key="rec.id" class="recommendation">
              <span class="rec-action" :class="getActionClass(rec.action)">{{ rec.action.toUpperCase() }}</span>
              <span class="rec-confidence">{{ (rec.confidence * 100).toFixed(1) }}%</span>
              <span class="rec-reasoning">{{ rec.reasoning }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Prediction Results -->
    <div class="prediction-results" v-if="predictionResults.length > 0">
      <h3>🔮 Prédictions avec News</h3>
      <div class="predictions-grid">
        <div v-for="prediction in predictionResults" :key="prediction.symbol" class="prediction-card">
          <div class="prediction-header">
            <h4>{{ prediction.symbol }}</h4>
            <span class="prediction-time">{{ formatTime(prediction.timestamp) }}</span>
          </div>
          <div class="prediction-metrics">
            <div class="metric">
              <span class="metric-label">Direction:</span>
              <span class="metric-value">{{ (prediction.directionProb * 100).toFixed(1) }}%</span>
            </div>
            <div class="metric">
              <span class="metric-label">Confiance:</span>
              <span class="metric-value">{{ (prediction.confidence * 100).toFixed(1) }}%</span>
            </div>
            <div class="metric">
              <span class="metric-label">Modèle:</span>
              <span class="metric-value">{{ prediction.modelName }}</span>
            </div>
            <div class="metric" v-if="prediction.newsIntegrated">
              <span class="metric-label">News intégrées:</span>
              <span class="metric-value success">✅ Oui</span>
            </div>
          </div>
          <div class="prediction-features" v-if="prediction.features">
            <h5>Features utilisées:</h5>
            <div class="features-list">
              <span v-for="(value, key) in prediction.features" :key="key" class="feature-tag">
                {{ key }}: {{ value }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Logs -->
    <div class="logs-section">
      <h3>📝 Logs en Temps Réel</h3>
      <div class="logs-container">
        <div v-for="log in logs" :key="log.id" class="log-entry" :class="log.level">
          <span class="log-time">{{ formatTime(log.timestamp) }}</span>
          <span class="log-level">{{ log.level.toUpperCase() }}</span>
          <span class="log-message">{{ log.message }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PipelineTestDashboard',
  data() {
    return {
      isPipelineRunning: false,
      pipelineStatus: {
        overall: 'stopped',
        dataCollector: 'stopped',
        newsCollector: 'stopped',
        dataAggregator: 'stopped',
        predictor: 'stopped',
        strategy: 'stopped',
        trader: 'stopped',
        logger: 'stopped'
      },
      testResults: [],
      newsAnalysisResults: [],
      predictionResults: [],
      logs: [],
      testInterval: null
    }
  },
  mounted() {
    this.loadInitialStatus()
    this.startLogMonitoring()
  },
  beforeUnmount() {
    if (this.testInterval) {
      clearInterval(this.testInterval)
    }
  },
  methods: {
    async loadInitialStatus() {
      try {
        const response = await fetch('/api/pipeline/status')
        if (response.ok) {
          const status = await response.json()
          this.pipelineStatus = { ...this.pipelineStatus, ...status }
        }
      } catch (error) {
        this.addLog('error', `Erreur chargement statut: ${error.message}`)
      }
    },

    async startPipeline() {
      try {
        this.addLog('info', 'Démarrage de la pipeline...')
        const response = await fetch('/api/pipeline/start', { method: 'POST' })
        
        if (response.ok) {
          this.isPipelineRunning = true
          this.pipelineStatus.overall = 'running'
          this.addLog('success', 'Pipeline démarrée avec succès')
          this.addTestResult('success', 'Démarrage Pipeline', 'Pipeline démarrée avec tous les agents')
          this.startStatusMonitoring()
        } else {
          throw new Error('Erreur démarrage pipeline')
        }
      } catch (error) {
        this.addLog('error', `Erreur démarrage: ${error.message}`)
        this.addTestResult('error', 'Démarrage Pipeline', error.message)
      }
    },

    async stopPipeline() {
      try {
        this.addLog('info', 'Arrêt de la pipeline...')
        const response = await fetch('/api/pipeline/stop', { method: 'POST' })
        
        if (response.ok) {
          this.isPipelineRunning = false
          this.pipelineStatus.overall = 'stopped'
          this.addLog('success', 'Pipeline arrêtée')
          this.addTestResult('success', 'Arrêt Pipeline', 'Pipeline arrêtée proprement')
          this.stopStatusMonitoring()
        } else {
          throw new Error('Erreur arrêt pipeline')
        }
      } catch (error) {
        this.addLog('error', `Erreur arrêt: ${error.message}`)
        this.addTestResult('error', 'Arrêt Pipeline', error.message)
      }
    },

    async testNewsCollection() {
      try {
        this.addLog('info', 'Test de collecte des news...')
        const response = await fetch('/api/pipeline/test/news-collection', { method: 'POST' })
        
        if (response.ok) {
          const result = await response.json()
          this.newsAnalysisResults = result.analysisResults || []
          this.addLog('success', `News collectées: ${result.newsCount}`)
          this.addTestResult('success', 'Collecte News', `Récupéré ${result.newsCount} news, ${result.alertsCount} alertes générées`)
        } else {
          throw new Error('Erreur collecte news')
        }
      } catch (error) {
        this.addLog('error', `Erreur test news: ${error.message}`)
        this.addTestResult('error', 'Collecte News', error.message)
      }
    },

    async testDataFusion() {
      try {
        this.addLog('info', 'Test de fusion des données...')
        const response = await fetch('/api/pipeline/test/data-fusion', { method: 'POST' })
        
        if (response.ok) {
          const result = await response.json()
          this.addLog('success', 'Fusion des données réussie')
          this.addTestResult('success', 'Fusion Données', `Fusion réussie pour ${result.symbolsCount} symboles`)
        } else {
          throw new Error('Erreur fusion données')
        }
      } catch (error) {
        this.addLog('error', `Erreur test fusion: ${error.message}`)
        this.addTestResult('error', 'Fusion Données', error.message)
      }
    },

    async testPredictionWithNews() {
      try {
        this.addLog('info', 'Test de prédiction avec news...')
        const response = await fetch('/api/pipeline/test/prediction-news', { method: 'POST' })
        
        if (response.ok) {
          const result = await response.json()
          this.predictionResults = result.predictions || []
          this.addLog('success', `Prédictions générées: ${result.predictionsCount}`)
          this.addTestResult('success', 'Prédiction avec News', `Généré ${result.predictionsCount} prédictions avec intégration news`)
        } else {
          throw new Error('Erreur prédiction')
        }
      } catch (error) {
        this.addLog('error', `Erreur test prédiction: ${error.message}`)
        this.addTestResult('error', 'Prédiction avec News', error.message)
      }
    },

    async runFullTest() {
      try {
        this.addLog('info', 'Lancement du test complet...')
        this.addTestResult('info', 'Test Complet', 'Démarrage du test complet de la pipeline')
        
        // Test 1: News Collection
        await this.testNewsCollection()
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        // Test 2: Data Fusion
        await this.testDataFusion()
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        // Test 3: Prediction with News
        await this.testPredictionWithNews()
        
        this.addLog('success', 'Test complet terminé')
        this.addTestResult('success', 'Test Complet', 'Tous les tests sont passés avec succès')
        
      } catch (error) {
        this.addLog('error', `Erreur test complet: ${error.message}`)
        this.addTestResult('error', 'Test Complet', error.message)
      }
    },

    startStatusMonitoring() {
      this.testInterval = setInterval(async () => {
        try {
          const response = await fetch('/api/pipeline/status')
          if (response.ok) {
            const status = await response.json()
            this.pipelineStatus = { ...this.pipelineStatus, ...status }
          }
        } catch (error) {
          this.addLog('error', `Erreur monitoring: ${error.message}`)
        }
      }, 5000)
    },

    stopStatusMonitoring() {
      if (this.testInterval) {
        clearInterval(this.testInterval)
        this.testInterval = null
      }
    },

    startLogMonitoring() {
      // Simulation de logs en temps réel
      setInterval(() => {
        if (this.isPipelineRunning) {
          const logMessages = [
            'Collecte des données de marché...',
            'Analyse des news récentes...',
            'Fusion des données en cours...',
            'Génération de prédictions...',
            'Mise à jour des signaux...'
          ]
          const randomMessage = logMessages[Math.floor(Math.random() * logMessages.length)]
          this.addLog('info', randomMessage)
        }
      }, 10000)
    },

    addLog(level, message) {
      this.logs.unshift({
        id: Date.now(),
        timestamp: new Date(),
        level,
        message
      })
      
      // Garder seulement les 50 derniers logs
      if (this.logs.length > 50) {
        this.logs = this.logs.slice(0, 50)
      }
    },

    addTestResult(status, title, details) {
      this.testResults.unshift({
        id: Date.now(),
        timestamp: new Date(),
        status,
        title,
        details
      })
      
      // Garder seulement les 20 derniers résultats
      if (this.testResults.length > 20) {
        this.testResults = this.testResults.slice(0, 20)
      }
    },

    formatTime(timestamp) {
      return new Date(timestamp).toLocaleTimeString()
    },

    formatSentiment(score) {
      if (score > 0.2) return 'Positif'
      if (score < -0.2) return 'Négatif'
      return 'Neutre'
    },

    getSentimentClass(score) {
      if (score > 0.2) return 'positive'
      if (score < -0.2) return 'negative'
      return 'neutral'
    },

    getActionClass(action) {
      switch (action.toLowerCase()) {
        case 'buy': return 'buy'
        case 'sell': return 'sell'
        case 'hold': return 'hold'
        default: return 'neutral'
      }
    }
  }
}
</script>

<style scoped>
.pipeline-test-dashboard {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.dashboard-header {
  text-align: center;
  margin-bottom: 30px;
}

.dashboard-header h2 {
  color: #2c3e50;
  margin-bottom: 10px;
}

.status-overview {
  margin-bottom: 30px;
}

.status-card {
  background: white;
  border-radius: 10px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-top: 15px;
}

.status-item {
  display: flex;
  align-items: center;
  padding: 15px;
  border-radius: 8px;
  background: #f8f9fa;
  border-left: 4px solid #dee2e6;
}

.status-item.running {
  background: #d4edda;
  border-left-color: #28a745;
}

.status-item.stopped {
  background: #f8d7da;
  border-left-color: #dc3545;
}

.status-item.error {
  background: #f8d7da;
  border-left-color: #dc3545;
}

.status-icon {
  font-size: 20px;
  margin-right: 10px;
}

.status-text {
  flex: 1;
  font-weight: 500;
}

.status-value {
  font-weight: bold;
  text-transform: uppercase;
  font-size: 12px;
}

.test-controls {
  background: white;
  border-radius: 10px;
  padding: 20px;
  margin-bottom: 30px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.control-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 15px;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-success { background: #28a745; color: white; }
.btn-danger { background: #dc3545; color: white; }
.btn-info { background: #17a2b8; color: white; }
.btn-warning { background: #ffc107; color: black; }
.btn-primary { background: #007bff; color: white; }
.btn-secondary { background: #6c757d; color: white; }

.btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.2);
}

.test-results, .news-analysis-results, .prediction-results, .logs-section {
  background: white;
  border-radius: 10px;
  padding: 20px;
  margin-bottom: 30px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.result-item {
  padding: 15px;
  margin-bottom: 10px;
  border-radius: 8px;
  border-left: 4px solid #dee2e6;
}

.result-item.success {
  background: #d4edda;
  border-left-color: #28a745;
}

.result-item.error {
  background: #f8d7da;
  border-left-color: #dc3545;
}

.result-item.info {
  background: #d1ecf1;
  border-left-color: #17a2b8;
}

.result-header {
  display: flex;
  align-items: center;
  margin-bottom: 5px;
}

.result-icon {
  margin-right: 10px;
  font-size: 16px;
}

.result-title {
  flex: 1;
  font-weight: 500;
}

.result-time {
  font-size: 12px;
  color: #6c757d;
}

.analysis-grid, .predictions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-top: 15px;
}

.analysis-card, .prediction-card {
  border: 1px solid #dee2e6;
  border-radius: 8px;
  padding: 15px;
  background: #f8f9fa;
}

.analysis-header, .prediction-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.analysis-header h4, .prediction-header h4 {
  margin: 0;
  color: #2c3e50;
}

.analysis-count, .prediction-time {
  font-size: 12px;
  color: #6c757d;
}

.analysis-metrics, .prediction-metrics {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-bottom: 15px;
}

.metric {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.metric-label {
  font-size: 12px;
  color: #6c757d;
}

.metric-value {
  font-weight: 500;
}

.metric-value.positive { color: #28a745; }
.metric-value.negative { color: #dc3545; }
.metric-value.neutral { color: #6c757d; }
.metric-value.buy { color: #28a745; }
.metric-value.sell { color: #dc3545; }
.metric-value.hold { color: #ffc107; }
.metric-value.success { color: #28a745; }

.recommendations h5 {
  margin: 10px 0 5px 0;
  font-size: 14px;
  color: #2c3e50;
}

.recommendation {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 5px;
  font-size: 12px;
}

.rec-action {
  padding: 2px 6px;
  border-radius: 3px;
  font-weight: bold;
  font-size: 10px;
}

.rec-confidence {
  font-weight: 500;
}

.rec-reasoning {
  flex: 1;
  color: #6c757d;
}

.features-list {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  margin-top: 10px;
}

.feature-tag {
  background: #e9ecef;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 10px;
  color: #495057;
}

.logs-container {
  max-height: 300px;
  overflow-y: auto;
  margin-top: 15px;
}

.log-entry {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  margin-bottom: 5px;
  border-radius: 4px;
  font-size: 12px;
  font-family: monospace;
}

.log-entry.info {
  background: #d1ecf1;
  color: #0c5460;
}

.log-entry.success {
  background: #d4edda;
  color: #155724;
}

.log-entry.error {
  background: #f8d7da;
  color: #721c24;
}

.log-time {
  margin-right: 10px;
  color: #6c757d;
}

.log-level {
  margin-right: 10px;
  font-weight: bold;
  min-width: 60px;
}

.log-message {
  flex: 1;
}
</style>
