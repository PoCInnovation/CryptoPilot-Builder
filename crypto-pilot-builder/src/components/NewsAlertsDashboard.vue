<template>
  <div class="news-alerts-dashboard">

    <div class="content-grid">
    <!-- Investment Alerts Section (first) -->
    <div class="alerts-section section-card">
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

    <!-- Recent News Section (second) -->
    <div class="news-section section-card">
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
            <span class="type-badge buy">📈 BUY</span>
            <span>Recommandation d'achat</span>
          </div>
          <div class="alert-type">
            <span class="type-badge sell">📉 SELL</span>
            <span>Recommandation de vente</span>
          </div>
          <div class="alert-type">
            <span class="type-badge hold">⏸️ HOLD</span>
            <span>Attendre et observer</span>
          </div>
        </div>
      </div>

      <div class="recent-alerts" v-if="recentAlerts && recentAlerts.length > 0">
        <h4>Alertes récentes</h4>
        <div class="alert-list">
          <div v-for="alert in recentAlerts" :key="alert.id" class="alert-item" :class="alert.alert_type.toLowerCase()">
            <div class="alert-header">
              <div class="alert-left">
                <span class="alert-type" :class="alert.alert_type.toLowerCase()">{{ alert.alert_type.toUpperCase() }}</span>
                <span class="crypto-symbol">{{ alert.crypto_symbol }}</span>
              </div>
              <div class="alert-right">
                <span class="confidence-badge">{{ Math.round(alert.confidence_score * 100) }}%</span>
              </div>
            </div>
            <div class="alert-reasoning" v-if="alert.reasoning">
              <p>{{ alert.reasoning }}</p>
            </div>
            <div class="alert-meta">
              <span class="time">{{ formatTime(alert.created_at) }}</span>
              <span class="alert-id">ID: {{ alert.id.slice(0, 8) }}...</span>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="no-alerts">
        <p>Aucune alerte générée pour le moment</p>
        <p class="hint">Les alertes apparaîtront automatiquement lors de l'analyse des news</p>
      </div>
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
  --text-primary: #f3e8ff;
  --text-secondary: rgba(255, 255, 255, 0.8);
}

.news-alerts-dashboard { padding: 20px; max-width: 1200px; margin: 0 auto; color: var(--text-primary); }
.content-grid { display: grid; grid-template-columns: 1.25fr .85fr; gap: 32px; align-items: start; }
.section-card { background: var(--glass-bg); border: 1px solid var(--glass-border); border-radius: 16px; box-shadow: var(--card-shadow); padding: 20px; display: flex; flex-direction: column; gap: 16px; }

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 2px solid var(--glass-border);
}

.dashboard-header h2 {
  margin: 0;
  color: var(--text-primary);
  font-size: 1.8rem;
  text-shadow: 0 2px 4px rgba(0,0,0,.3);
}

.header-actions { display: flex; align-items: center; gap: 20px; }

.refresh-btn {
  display: flex; align-items: center; gap: 8px;
  padding: 10px 20px; border: none; border-radius: 10px;
  background: var(--primary-gradient); color: white; cursor: pointer;
  transition: all 0.3s ease;
}
.refresh-btn:hover:not(:disabled) { transform: translateY(-2px); box-shadow: var(--card-shadow-hover); }
.refresh-btn:disabled { opacity: .6; cursor: not-allowed; }

.last-updated { color: var(--text-secondary); font-size: .9rem; }

.alerts-explanation { background: var(--primary-gradient); color: white; margin-bottom: 30px; }
.alerts-explanation h3 { margin-top: 0; color: white; }

.alerts-section, .news-section { margin-bottom: 0; }
.alerts-section h3, .news-section h3 { color: var(--text-primary); margin-bottom: 20px; font-size: 1.4rem; }

.news-section-header { display: flex; align-items: center; justify-content: space-between; cursor: pointer; padding: 14px 16px; background: rgba(255,255,255,.06); border-radius: 12px; border: 1px solid var(--glass-border); transition: all .3s ease; margin-bottom: 0; }
.news-section-header:hover { background: rgba(255,255,255,.12); border-color: rgba(255,255,255,.2); transform: translateY(-1px); }
.news-section-header h3 { margin: 0; color: var(--text-primary); font-size: 1.4rem; }

.news-count { background: #3498db; color: white; padding: 4px 8px; border-radius: 12px; font-size: .8rem; font-weight: bold; margin-left: 10px; }

.accordion-toggle { display: flex; align-items: center; justify-content: center; width: 30px; height: 30px; border-radius: 50%; background: #3498db; color: white; transition: all .3s ease; }
.accordion-toggle:hover { background: #2980b9; transform: scale(1.1); }
.toggle-icon { font-size: 12px; transition: transform .3s ease; }
.toggle-icon.expanded { transform: rotate(180deg); }

.news-accordion-content { margin-top: 14px; animation: slideDown .3s ease-out; position: relative; border: 1px solid var(--glass-border); border-radius: 14px; overflow: hidden; background: var(--glass-bg); padding-bottom: 12px; }

.resize-handle { position: absolute; bottom: 0; left: 0; right: 0; height: 14px; background: rgba(255,255,255,.06); border-top: 1px solid var(--glass-border); cursor: ns-resize; display: flex; align-items: center; justify-content: center; transition: background-color .2s ease; z-index: 10; }
.resize-handle:hover { background: rgba(255,255,255,.12); }
.resize-grip { display: flex; flex-direction: column; gap: 2px; opacity: .8; transition: opacity .2s ease; }
.resize-handle:hover .resize-grip { opacity: 1; }
.grip-line { width: 30px; height: 2px; background: #cbd5e1; border-radius: 1px; }

@keyframes slideDown { from { opacity: 0; max-height: 0; transform: translateY(-10px); } to { opacity: 1; max-height: 1000px; transform: translateY(0); } }

.alerts-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 20px; margin-bottom: 20px; }

.alert-card { background: var(--glass-bg); border-radius: 14px; padding: 18px; border: 1px solid var(--glass-border); box-shadow: var(--card-shadow); transition: transform .3s ease; }
.alert-card:hover { transform: translateY(-2px); box-shadow: var(--card-shadow-hover); }
.alert-card.alert-buy { border-left: 4px solid #27ae60; }
.alert-card.alert-sell { border-left: 4px solid #e74c3c; }
.alert-card.alert-hold { border-left: 4px solid #f39c12; }

.alert-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.alert-left { display: flex; align-items: center; gap: 10px; }
.alert-right { display: flex; align-items: center; }
.alert-type { font-weight: 800; font-size: .9rem; padding: 4px 10px; border-radius: 999px; color: white; letter-spacing: .3px; }
.alert-buy .alert-type { background: #27ae60; }
.alert-sell .alert-type { background: #e74c3c; }
.alert-hold .alert-type { background: #f39c12; }
.alert-crypto { font-weight: bold; color: var(--text-primary); font-size: 1.05rem; }
.confidence-badge { background: rgba(255,255,255,.15); padding: 4px 10px; border-radius: 999px; font-weight: 800; color: #e2e8f0; font-size: .85rem; }
.alert-reasoning { margin-bottom: 15px; line-height: 1.6; color: #cbd5e1; }
.alert-meta { display: flex; justify-content: space-between; align-items: center; color: #94a3b8; font-size: .9rem; }
.alert-priority { padding: 4px 8px; border-radius: 12px; font-size: .8rem; font-weight: bold; }
.priority-urgent { background: #e74c3c; color: white; }
.priority-high { background: #f39c12; color: white; }
.priority-medium { background: #3498db; color: white; }
.priority-low { background: #6b7280; color: white; }
.alert-time { color: #94a3b8; font-size: .9rem; }

.no-alerts, .no-news { text-align: center; padding: 40px; color: #94a3b8; }
.no-alerts-hint, .no-news-hint { font-size: .9rem; margin-top: 10px; }

.news-filters { display: flex; gap: 10px; margin-bottom: 20px; }
.filter-btn { padding: 8px 16px; border: 2px solid #94a3b8; background: transparent; border-radius: 20px; cursor: pointer; transition: all .3s ease; color: #cbd5e1; }
.filter-btn.active { background: var(--primary-gradient); border-color: transparent; color: white; }
.filter-btn:hover { border-color: #667eea; color: #ffffff; }

.news-list { display: flex; flex-direction: column; gap: 16px; overflow-y: auto; padding: 16px 16px 36px; height: 100%; scrollbar-width: thin; scrollbar-color: #667eea transparent; }
.news-list::-webkit-scrollbar { width: 8px; }
.news-list::-webkit-scrollbar-track { background: rgba(255,255,255,.06); border-radius: 4px; }
.news-list::-webkit-scrollbar-thumb { background: linear-gradient(135deg, #667eea, #764ba2); border-radius: 4px; }
.news-list::-webkit-scrollbar-thumb:hover { background: linear-gradient(135deg, #5a67d8, #6b46c1); }

.news-item { background: var(--glass-bg); border-radius: 16px; padding: 18px; box-shadow: var(--card-shadow); border-left: 4px solid #bdc3c7; transition: all .3s ease; }
.news-item + .news-item { margin-top: 2px; }
.news-item:hover { transform: translateY(-2px); box-shadow: var(--card-shadow-hover); }
.news-item.news-impact-critical { border-left-color: #e74c3c; }
.news-item.news-impact-high { border-left-color: #f39c12; }
.news-item.news-impact-medium { border-left-color: #3498db; }
.news-item.news-impact-low { border-left-color: #95a5a6; }

.news-header { margin-bottom: 15px; }
.news-title { margin: 0 0 8px 0; color: var(--text-primary); font-size: 1.1rem; line-height: 1.45; }
.news-meta { display: flex; gap: 15px; color: #94a3b8; font-size: .9rem; }
.news-content { margin: 10px 0 16px; line-height: 1.65; color: #cbd5e1; }

.news-analysis { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 14px; margin-top: 10px; margin-bottom: 6px; padding: 12px; background: rgba(255,255,255,.08); border-radius: 12px; }
.analysis-item { display: flex; flex-direction: column; gap: 5px; }
.analysis-item .label { font-weight: bold; color: var(--text-primary); font-size: .9rem; }
.sentiment.positive { color: #27ae60; font-weight: bold; }
.sentiment.negative { color: #e74c3c; font-weight: bold; }
.sentiment.neutral { color: #fbbf24; font-weight: bold; }
.impact-critical { color: #e74c3c; font-weight: bold; }
.impact-high { color: #f39c12; font-weight: bold; }
.impact-medium { color: #3498db; font-weight: bold; }
.impact-low { color: #95a5a6; font-weight: bold; }

.crypto-mentions { display: flex; flex-wrap: wrap; gap: 5px; }
.crypto-tag { background: #3498db; color: white; padding: 2px 8px; border-radius: 12px; font-size: .8rem; font-weight: bold; }

.news-actions { display: flex; gap: 10px; justify-content: flex-end; margin-top: 8px; }

.btn { padding: 8px 16px; border: none; border-radius: 10px; cursor: pointer; text-decoration: none; display: inline-block; transition: all .3s ease; font-size: .9rem; color: white; position: relative; overflow: hidden; }
.btn::before { content: ""; position: absolute; top: 0; left: -100%; width: 100%; height: 100%; background: linear-gradient(120deg, rgba(255,255,255,.2) 0%, rgba(255,255,255,.2) 50%, rgba(255,255,255,0) 80%); transition: left .5s; }
.btn:hover::before { left: 100%; }

.btn-primary { background: var(--primary-gradient); }
.btn-outline { background: transparent; color: #cbd5e1; border: 2px solid #667eea; }
.btn-outline:hover { background: #667eea; color: white; }
.btn-sm { padding: 6px 12px; font-size: .8rem; }
.btn-secondary { background: linear-gradient(135deg, #6b7280 0%, #4b5563 100%); color: white; }
.btn-secondary:hover { filter: brightness(1.05); }

.loading-overlay { position: fixed; inset: 0; background: rgba(0,0,0,.6); display: flex; flex-direction: column; justify-content: center; align-items: center; z-index: 1000; color: var(--text-primary); }
.loading-spinner { font-size: 2rem; animation: spin 1s linear infinite; margin-bottom: 20px; }
@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }

.card { background: var(--glass-bg); border-radius: 12px; padding: 20px; box-shadow: var(--card-shadow); border: 1px solid var(--glass-border); margin-bottom: 20px; }

/* alert list items */
.alert-item { padding: 16px; background: rgba(255,255,255,.06); border-radius: 16px; border-left: 6px solid #3498db; box-shadow: var(--card-shadow); position: relative; overflow: hidden; }
.alert-item.buy { border-left-color: #22c55e; }
.alert-item.sell { border-left-color: #ef4444; }
.alert-item.hold { border-left-color: #f59e0b; }
.alert-item + .alert-item { margin-top: 12px; }
.crypto-symbol { font-weight: 800; color: var(--text-primary); font-size: 1.05rem; letter-spacing: .2px; }
.confidence { background: rgba(255,255,255,.15); padding: 4px 10px; border-radius: 999px; font-size: .85rem; font-weight: 800; color: #e2e8f0; }
.alert-reasoning { font-size: .9rem; color: #cbd5e1; font-style: italic; margin-top: 8px; }

@media (max-width: 1024px) {
  .content-grid { grid-template-columns: 1fr; }
}
@media (max-width: 768px) {
  .dashboard-header { flex-direction: column; gap: 15px; align-items: flex-start; }
  .header-actions { width: 100%; justify-content: space-between; }
  .alerts-grid { grid-template-columns: 1fr; }
  .news-analysis { grid-template-columns: 1fr; }
  .alert-types { flex-direction: column; gap: 10px; }
  .alert-header { flex-direction: column; align-items: flex-start; gap: 8px; }
  .alert-meta { flex-direction: column; align-items: flex-start; gap: 4px; }
  .resize-handle { height: 16px; }
  .grip-line { width: 40px; }
}
</style>
