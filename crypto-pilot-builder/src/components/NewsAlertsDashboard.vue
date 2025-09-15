<template>
  <div class="news-alerts-dashboard"> 

    <!-- Recent News Section -->
    <div class="news-section">
      <div class="news-section-header" @click="toggleNewsAccordion">
        <h3>📰 News Récentes</h3>
        <div class="news-count" v-if="filteredNews.length > 0">
          ({{ filteredNews.length }})
        </div>
        <div class="accordion-toggle">
          <span class="toggle-icon" :class="{ 'expanded': isNewsAccordionOpen }">▼</span>
        </div>
      </div>
      
      <div class="news-filters" v-if="isNewsAccordionOpen">
        <button 
          v-for="filter in newsFilters" 
          :key="filter.value"
          @click="selectedNewsFilter = filter.value"
          class="filter-btn"
          :class="{ active: selectedNewsFilter === filter.value }"
        >
          {{ filter.label }}
        </button>
      </div>
      
      <div class="news-accordion-content" v-if="isNewsAccordionOpen" :style="{ height: accordionHeight + 'px' }">
        <div class="news-list" v-if="filteredNews.length > 0">
          <div 
            v-for="news in filteredNews" 
            :key="news.id" 
            class="news-item"
            :class="getNewsImpactClass(news.impact_level)"
          >
            <div class="news-header">
              <h4 class="news-title">{{ news.title }}</h4>
              <div class="news-meta">
                <span class="news-source">{{ news.source }}</span>
                <span class="news-time">{{ formatTime(news.published_at) }}</span>
              </div>
            </div>
            
            <p class="news-content">{{ news.content }}</p>
            
            <div class="news-analysis">
              <div class="analysis-item">
                <span class="label">Sentiment:</span>
                <span class="sentiment" :class="getSentimentClass(news.sentiment_score)">
                  {{ formatSentiment(news.sentiment_score) }}
                </span>
              </div>
              <div class="analysis-item">
                <span class="label">Pertinence:</span>
                <span class="relevance">{{ Math.round(news.relevance_score * 100) }}%</span>
              </div>
              <div class="analysis-item">
                <span class="label">Impact:</span>
                <span class="impact" :class="getImpactClass(news.impact_level)">
                  {{ getImpactLabel(news.impact_level) }}
                </span>
              </div>
              <div class="analysis-item" v-if="news.crypto_mentions && news.crypto_mentions.length > 0">
                <span class="label">Cryptos:</span>
                <span class="crypto-mentions">
                  <span 
                    v-for="crypto in news.crypto_mentions" 
                    :key="crypto" 
                    class="crypto-tag"
                  >
                    {{ crypto }}
                  </span>
                </span>
              </div>
            </div>
            
            <div class="news-actions">
              <a :href="news.url" target="_blank" class="btn btn-sm btn-outline">
                Lire l'article
              </a>
              <button 
                @click="analyzeNews(news.id)" 
                class="btn btn-sm btn-primary"
                :disabled="isAnalyzing"
              >
                Analyser
              </button>
            </div>
          </div>
        </div>
        
        <div v-else class="no-news">
          <p>📰 Aucune news récente</p>
          <p class="no-news-hint">Les news crypto apparaîtront ici une fois récupérées</p>
        </div>
        
        <!-- Poignée de redimensionnement -->
        <div 
          class="resize-handle"
          @mousedown="startResize"
          @touchstart="startResize"
        >
          <div class="resize-grip">
            <span class="grip-line"></span>
            <span class="grip-line"></span>
            <span class="grip-line"></span>
          </div>
        </div>
      </div>
    </div>

    <!-- Investment Alerts Section -->
    <div class="alerts-section">
      <div class="alerts-header">
        <h3>🚨 Alertes d'investissement</h3>
        <button @click="refreshData" class="btn btn-sm btn-secondary">
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
            <div class="alert-reasoning" v-if="alert.reasoning">
              <p>{{ alert.reasoning }}</p>
            </div>
          </div>
        </div>
      </div>
      
      <div v-else class="no-alerts">
        <p>Aucune alerte générée pour le moment</p>
        <p class="hint">Les alertes apparaîtront automatiquement lors de l'analyse des news</p>
      </div>
    </div>

    <!-- Loading States -->
    <div v-if="isLoading" class="loading-overlay">
      <div class="loading-spinner">🔄</div>
      <p>Chargement des données...</p>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import apiService from '../services/apiService.js'

export default {
  name: 'NewsAlertsDashboard',
  setup() {
    const recentNews = ref([])
    const recentAlerts = ref([])
    const isLoading = ref(false)
    const isRefreshing = ref(false)
    const isAnalyzing = ref(false)
    const lastUpdated = ref(new Date())
    const selectedNewsFilter = ref('all')
    const isNewsAccordionOpen = ref(false)
    const accordionHeight = ref(400)
    const isResizing = ref(false)
    const startY = ref(0)
    const startHeight = ref(0)

    const newsFilters = [
      { value: 'all', label: 'Toutes' },
      { value: 'high', label: 'Impact élevé' },
      { value: 'medium', label: 'Impact moyen' },
      { value: 'low', label: 'Impact faible' }
    ]

    // Computed properties
    const filteredNews = computed(() => {
      if (selectedNewsFilter.value === 'all') {
        return recentNews.value
      }
      return recentNews.value.filter(news => news.impact_level === selectedNewsFilter.value)
    })

    // Methods
    const loadData = async () => {
      try {
        isLoading.value = true
        
        // Load news and alerts in parallel
        const [newsResponse, alertsResponse] = await Promise.all([
          apiService.getAutowalletNews(),
          apiService.getAutowalletAlerts()
        ])
        
        if (newsResponse && newsResponse.news) {
          recentNews.value = newsResponse.news
        }
        
        if (alertsResponse && alertsResponse.alerts) {
          recentAlerts.value = alertsResponse.alerts
        }
        
        lastUpdated.value = new Date()
        
      } catch (error) {
        console.error('Erreur lors du chargement des données:', error)
      } finally {
        isLoading.value = false
      }
    }

    const refreshData = async () => {
      try {
        isRefreshing.value = true
        await loadData()
      } catch (error) {
        console.error('Erreur lors de l\'actualisation:', error)
      } finally {
        isRefreshing.value = false
      }
    }

    const toggleNewsAccordion = () => {
      isNewsAccordionOpen.value = !isNewsAccordionOpen.value
    }

    const startResize = (e) => {
      e.preventDefault()
      isResizing.value = true
      startY.value = e.clientY || e.touches[0].clientY
      startHeight.value = accordionHeight.value
      
      document.addEventListener('mousemove', handleResize)
      document.addEventListener('mouseup', stopResize)
      document.addEventListener('touchmove', handleResize)
      document.addEventListener('touchend', stopResize)
    }

    const handleResize = (e) => {
      if (!isResizing.value) return
      
      e.preventDefault()
      const currentY = e.clientY || e.touches[0].clientY
      const deltaY = currentY - startY.value
      const newHeight = startHeight.value + deltaY
      
      // Limiter la hauteur entre 200px et 800px
      accordionHeight.value = Math.max(200, Math.min(800, newHeight))
    }

    const stopResize = () => {
      isResizing.value = false
      document.removeEventListener('mousemove', handleResize)
      document.removeEventListener('mouseup', stopResize)
      document.removeEventListener('touchmove', handleResize)
      document.removeEventListener('touchend', stopResize)
    }

    const analyzeNews = async (newsId) => {
      try {
        isAnalyzing.value = true
        
        const response = await apiService.analyzeNews([newsId], 'individual')
        
        if (response && response.alerts) {
          // Add new alerts to the list
          recentAlerts.value = [...response.alerts, ...recentAlerts.value]
        }
        
      } catch (error) {
        console.error('Erreur lors de l\'analyse:', error)
      } finally {
        isAnalyzing.value = false
      }
    }

    // Utility methods
    const formatTime = (dateString) => {
      const date = new Date(dateString)
      return date.toLocaleString('fr-FR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
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

    const getImpactClass = (level) => {
      return `impact-${level}`
    }

    const getImpactLabel = (level) => {
      const labels = {
        'critical': 'Critique',
        'high': 'Élevé',
        'medium': 'Moyen',
        'low': 'Faible'
      }
      return labels[level] || 'Inconnu'
    }

    const getNewsImpactClass = (level) => {
      return `news-impact-${level}`
    }

    const getAlertClass = (type) => {
      return `alert-${type}`
    }

    const getAlertTypeLabel = (type) => {
      const labels = {
        'buy': 'ACHAT',
        'sell': 'VENTE',
        'hold': 'CONSERVER'
      }
      return labels[type] || type.toUpperCase()
    }

    const getPriorityClass = (priority) => {
      return `priority-${priority}`
    }

    const getPriorityLabel = (priority) => {
      const labels = {
        'urgent': 'Urgent',
        'high': 'Élevée',
        'medium': 'Moyenne',
        'low': 'Faible'
      }
      return labels[priority] || priority
    }

    // Lifecycle
    onMounted(() => {
      loadData()
    })

    return {
      recentNews,
      recentAlerts,
      isLoading,
      isRefreshing,
      isAnalyzing,
      lastUpdated,
      selectedNewsFilter,
      newsFilters,
      filteredNews,
      isNewsAccordionOpen,
      accordionHeight,
      isResizing,
      loadData,
      refreshData,
      toggleNewsAccordion,
      startResize,
      analyzeNews,
      formatTime,
      formatSentiment,
      getSentimentClass,
      getImpactClass,
      getImpactLabel,
      getNewsImpactClass,
      getAlertClass,
      getAlertTypeLabel,
      getPriorityClass,
      getPriorityLabel
    }
  }
}
</script>

<style scoped>
.news-alerts-dashboard {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 2px solid #e0e0e0;
}

.dashboard-header h2 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.8rem;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 20px;
}

.refresh-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  background: #3498db;
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
}

.refresh-btn:hover:not(:disabled) {
  background: #2980b9;
  transform: translateY(-2px);
}

.refresh-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.last-updated {
  color: #7f8c8d;
  font-size: 0.9rem;
}

.alerts-explanation {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  margin-bottom: 30px;
}

.alerts-explanation h3 {
  margin-top: 0;
  color: white;
}

.alerts-section, .news-section {
  margin-bottom: 40px;
}

.alerts-section h3, .news-section h3 {
  color: #2c3e50;
  margin-bottom: 20px;
  font-size: 1.4rem;
}

.news-section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
  padding: 15px 20px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
  transition: all 0.3s ease;
  margin-bottom: 0;
}

.news-section-header:hover {
  background: #e9ecef;
  border-color: #dee2e6;
}

.news-section-header h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.4rem;
}

.news-count {
  background: #3498db;
  color: white;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: bold;
  margin-left: 10px;
}

.accordion-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: #3498db;
  color: white;
  transition: all 0.3s ease;
}

.accordion-toggle:hover {
  background: #2980b9;
  transform: scale(1.1);
}

.toggle-icon {
  font-size: 12px;
  transition: transform 0.3s ease;
}

.toggle-icon.expanded {
  transform: rotate(180deg);
}

.news-accordion-content {
  margin-top: 15px;
  animation: slideDown 0.3s ease-out;
  position: relative;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  overflow: hidden;
}

.resize-handle {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 12px;
  background: #f8f9fa;
  border-top: 1px solid #dee2e6;
  cursor: ns-resize;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s ease;
  z-index: 10;
}

.resize-handle:hover {
  background: #e9ecef;
}

.resize-grip {
  display: flex;
  flex-direction: column;
  gap: 2px;
  opacity: 0.6;
  transition: opacity 0.2s ease;
}

.resize-handle:hover .resize-grip {
  opacity: 1;
}

.grip-line {
  width: 30px;
  height: 2px;
  background: #6c757d;
  border-radius: 1px;
}

@keyframes slideDown {
  from {
    opacity: 0;
    max-height: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    max-height: 1000px;
    transform: translateY(0);
  }
}

.alerts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.alert-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  border-left: 4px solid #3498db;
  transition: transform 0.3s ease;
}

.alert-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
}

.alert-card.alert-buy {
  border-left-color: #27ae60;
}

.alert-card.alert-sell {
  border-left-color: #e74c3c;
}

.alert-card.alert-hold {
  border-left-color: #f39c12;
}

.alert-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.alert-type {
  font-weight: bold;
  font-size: 1.1rem;
  padding: 4px 12px;
  border-radius: 20px;
  color: white;
}

.alert-buy .alert-type {
  background: #27ae60;
}

.alert-sell .alert-type {
  background: #e74c3c;
}

.alert-hold .alert-type {
  background: #f39c12;
}

.alert-crypto {
  font-weight: bold;
  color: #2c3e50;
  font-size: 1.1rem;
}

.alert-confidence {
  background: #ecf0f1;
  padding: 4px 8px;
  border-radius: 12px;
  font-weight: bold;
  color: #2c3e50;
}

.alert-reasoning {
  margin-bottom: 15px;
  line-height: 1.6;
  color: #34495e;
}

.alert-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.alert-priority {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: bold;
}

.priority-urgent {
  background: #e74c3c;
  color: white;
}

.priority-high {
  background: #f39c12;
  color: white;
}

.priority-medium {
  background: #3498db;
  color: white;
}

.priority-low {
  background: #95a5a6;
  color: white;
}

.alert-time {
  color: #7f8c8d;
  font-size: 0.9rem;
}

.no-alerts, .no-news {
  text-align: center;
  padding: 40px;
  color: #7f8c8d;
}

.no-alerts-hint, .no-news-hint {
  font-size: 0.9rem;
  margin-top: 10px;
}

.news-filters {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.filter-btn {
  padding: 8px 16px;
  border: 2px solid #bdc3c7;
  background: white;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  color: #7f8c8d;
}

.filter-btn.active {
  background: #3498db;
  border-color: #3498db;
  color: white;
}

.filter-btn:hover {
  border-color: #3498db;
  color: #3498db;
}

.news-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
  overflow-y: auto;
  padding: 20px;
  padding-bottom: 32px; /* Espace pour la poignée de redimensionnement */
  height: 100%;
  scrollbar-width: thin;
  scrollbar-color: #3498db #f1f1f1;
}

.news-list::-webkit-scrollbar {
  width: 8px;
}

.news-list::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.news-list::-webkit-scrollbar-thumb {
  background: #3498db;
  border-radius: 4px;
}

.news-list::-webkit-scrollbar-thumb:hover {
  background: #2980b9;
}

.news-item {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  border-left: 4px solid #bdc3c7;
  transition: all 0.3s ease;
}

.news-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.news-item.news-impact-critical {
  border-left-color: #e74c3c;
}

.news-item.news-impact-high {
  border-left-color: #f39c12;
}

.news-item.news-impact-medium {
  border-left-color: #3498db;
}

.news-item.news-impact-low {
  border-left-color: #95a5a6;
}

.news-header {
  margin-bottom: 15px;
}

.news-title {
  margin: 0 0 10px 0;
  color: #2c3e50;
  font-size: 1.2rem;
  line-height: 1.4;
}

.news-meta {
  display: flex;
  gap: 15px;
  color: #7f8c8d;
  font-size: 0.9rem;
}

.news-content {
  margin-bottom: 20px;
  line-height: 1.6;
  color: #34495e;
}

.news-analysis {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
}

.analysis-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.analysis-item .label {
  font-weight: bold;
  color: #2c3e50;
  font-size: 0.9rem;
}

.sentiment.positive {
  color: #27ae60;
  font-weight: bold;
}

.sentiment.negative {
  color: #e74c3c;
  font-weight: bold;
}

.sentiment.neutral {
  color: #7f8c8d;
  font-weight: bold;
}

.impact-critical {
  color: #e74c3c;
  font-weight: bold;
}

.impact-high {
  color: #f39c12;
  font-weight: bold;
}

.impact-medium {
  color: #3498db;
  font-weight: bold;
}

.impact-low {
  color: #95a5a6;
  font-weight: bold;
}

.crypto-mentions {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.crypto-tag {
  background: #3498db;
  color: white;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: bold;
}

.news-actions {
  display: flex;
  gap: 10px;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  text-decoration: none;
  display: inline-block;
  transition: all 0.3s ease;
  font-size: 0.9rem;
}

.btn-primary {
  background: #3498db;
  color: white;
}

.btn-primary:hover {
  background: #2980b9;
}

.btn-outline {
  background: transparent;
  color: #3498db;
  border: 2px solid #3498db;
}

.btn-outline:hover {
  background: #3498db;
  color: white;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 0.8rem;
}

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.loading-spinner {
  font-size: 2rem;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
}

/* Styles pour la section des alertes d'investissement */
.alerts-section {
  margin-top: 30px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 12px;
  border: 1px solid #e9ecef;
}

.alerts-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.alerts-header h3 {
  margin: 0;
  color: #2c3e50;
}

.alerts-info {
  margin-bottom: 25px;
}

.info-text {
  margin-bottom: 15px;
  color: #5a6c7d;
  line-height: 1.5;
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
  font-size: 1.2rem;
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
  color: #2c3e50;
}

.confidence {
  background: #e9ecef;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: bold;
}

.alert-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.8rem;
  color: #6c757d;
  margin-bottom: 8px;
}

.alert-reasoning {
  font-size: 0.9rem;
  color: #495057;
  font-style: italic;
  margin-top: 8px;
}

.no-alerts {
  text-align: center;
  padding: 30px 20px;
  color: #6c757d;
}

.no-alerts .hint {
  font-size: 0.9rem;
  margin-top: 10px;
  color: #adb5bd;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background: #5a6268;
}

@media (max-width: 768px) {
  .dashboard-header {
    flex-direction: column;
    gap: 15px;
    align-items: flex-start;
  }
  
  .header-actions {
    width: 100%;
    justify-content: space-between;
  }
  
  .alerts-grid {
    grid-template-columns: 1fr;
  }
  
  .news-analysis {
    grid-template-columns: 1fr;
  }
  
  .alert-types {
    flex-direction: column;
    gap: 10px;
  }
  
  .alert-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .alert-meta {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }
  
  .resize-handle {
    height: 16px; /* Plus facile à utiliser sur mobile */
  }
  
  .grip-line {
    width: 40px; /* Plus visible sur mobile */
  }
}
</style>
