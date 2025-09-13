# 📋 Guide Technique - Frontend Pipeline CryptoPilot

## 🎯 Vue d'ensemble

Ce document détaille comment implémenter un frontend pour la pipeline de trading CryptoPilot. Le système utilise des agents uAgent avec des APIs REST pour l'orchestration et le monitoring en temps réel.

## 🏗️ Architecture du Système

### Pipeline d'Agents
```
DataCollector → NewsCollector → DataAggregator → Predictor → Strategy → Trader → Logger
     ↓              ↓              ↓            ↓         ↓        ↓        ↓
  CoinGecko    CryptoCompare    Fusion     ASI:One IA   Signaux  Trades   Logs
```

### Stack Technique Backend
- **Framework**: Flask (Python 3.11)
- **Agents**: uAgent framework (Fetch.ai)
- **IA**: ASI:One (asi1-mini model)
- **APIs Externes**: CoinGecko, CryptoCompare
- **Base de données**: PostgreSQL
- **Containerisation**: Docker + Docker Compose

## 🔌 APIs Disponibles

### 1. Contrôle du Pipeline

#### Démarrer le Pipeline
```http
POST /api/pipeline/start
Content-Type: application/json

Response:
{
  "success": true,
  "message": "Pipeline démarrée avec succès"
}
```

#### Arrêter le Pipeline
```http
POST /api/pipeline/stop
Content-Type: application/json

Response:
{
  "success": true,
  "message": "Pipeline arrêtée avec succès"
}
```

#### Statut du Pipeline
```http
GET /api/pipeline/status

Response:
{
  "overall": "running|stopped",
  "dataCollector": "running|stopped|processing|error",
  "newsCollector": "running|stopped|processing|error",
  "dataAggregator": "running|stopped|processing|error",
  "predictor": "running|stopped|processing|error",
  "strategy": "running|stopped|processing|error",
  "trader": "running|stopped|processing|error",
  "logger": "running|stopped|processing|error"
}
```

### 2. Métriques et Données

#### Métriques du Pipeline
```http
GET /api/pipeline/metrics

Response:
{
  "success": true,
  "metrics": {
    "total_executions": 156,
    "total_errors": 0,
    "success_rate": 100,
    "predictions_count": 156,
    "signals_count": 156
  },
  "pipeline_data": [
    {
      "timestamp": "2025-09-13T21:35:18.241743",
      "symbol": "BTC/USD",
      "price": 115991.0,
      "volume": 31724390239.54926,
      "prediction": {
        "direction": "UP",
        "confidence": 0.7,
        "price_target": 118310.82,
        "direction_probability": 0.85,
        "model_name": "ASI:One-asi1-mini",
        "technical_indicators": {
          "rsi": 100.0,
          "ma_5": 115759.018,
          "ma_10": 115469.040,
          "ma_20": 114889.085,
          "macd": 0.0,
          "bb_upper": 116226.759,
          "bb_lower": 113551.412,
          "stoch_k": 100.0,
          "volatility": 5.588e-06
        }
      },
      "strategy_signal": {
        "action": "BUY|SELL|HOLD",
        "confidence": 0.7,
        "position_size": 0.1,
        "stop_loss": 113671.18,
        "take_profit": 121790.55
      },
      "trade_execution": {
        "trade_id": "trade_1757799318.241888",
        "action": "BUY",
        "quantity": 0.1,
        "price": 115991.0,
        "status": "FILLED"
      }
    }
  ]
}
```

### 3. Tests et Debugging

#### Test de Collecte de News
```http
POST /api/pipeline/test/news-collection

Response:
{
  "status": "success",
  "news_collected": 15,
  "analysis_results": [
    {
      "symbol": "BTC",
      "sentiment": "positive|negative|neutral",
      "confidence": 0.85,
      "recommendation": "BUY|SELL|HOLD"
    }
  ]
}
```

#### Debug du Pipeline
```http
GET /api/pipeline/debug

Response:
{
  "pipeline_manager_type": "PipelineManager",
  "pipeline_data_count": 11,
  "pipeline_data_sample": {
    "type": "PipelineData",
    "price": 115970.0,
    "volume": 32219665858.803352
  }
}
```

## 🎨 Structure Frontend Recommandée

### 1. Architecture Vue.js/React

```
src/
├── components/
│   ├── Dashboard/
│   │   ├── PipelineStatus.vue
│   │   ├── AgentCards.vue
│   │   ├── MetricsPanel.vue
│   │   └── RealTimeChart.vue
│   ├── Controls/
│   │   ├── PipelineControls.vue
│   │   └── AgentControls.vue
│   └── Data/
│       ├── PriceHistory.vue
│       ├── TradingSignals.vue
│       └── NewsAnalysis.vue
├── services/
│   ├── apiService.js
│   ├── websocketService.js
│   └── pipelineService.js
├── stores/
│   ├── pipelineStore.js
│   └── metricsStore.js
└── utils/
    ├── formatters.js
    └── constants.js
```

### 2. Service API (JavaScript)

```javascript
// services/pipelineService.js
class PipelineService {
  constructor(baseURL = 'http://localhost:5000') {
    this.baseURL = baseURL;
  }

  async startPipeline() {
    const response = await fetch(`${this.baseURL}/api/pipeline/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    });
    return response.json();
  }

  async stopPipeline() {
    const response = await fetch(`${this.baseURL}/api/pipeline/stop`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    });
    return response.json();
  }

  async getStatus() {
    const response = await fetch(`${this.baseURL}/api/pipeline/status`);
    return response.json();
  }

  async getMetrics() {
    const response = await fetch(`${this.baseURL}/api/pipeline/metrics`);
    return response.json();
  }

  // Polling pour les mises à jour temps réel
  startPolling(callback, interval = 2000) {
    return setInterval(async () => {
      try {
        const [status, metrics] = await Promise.all([
          this.getStatus(),
          this.getMetrics()
        ]);
        callback({ status, metrics });
      } catch (error) {
        console.error('Polling error:', error);
      }
    }, interval);
  }
}
```

### 3. Store Vuex/Pinia

```javascript
// stores/pipelineStore.js
import { defineStore } from 'pinia'

export const usePipelineStore = defineStore('pipeline', {
  state: () => ({
    status: {
      overall: 'stopped',
      agents: {}
    },
    metrics: {
      total_executions: 0,
      success_rate: 0,
      predictions_count: 0,
      signals_count: 0
    },
    pipelineData: [],
    isLoading: false,
    error: null
  }),

  actions: {
    async startPipeline() {
      this.isLoading = true;
      try {
        const result = await pipelineService.startPipeline();
        if (result.success) {
          await this.fetchStatus();
        }
      } catch (error) {
        this.error = error.message;
      } finally {
        this.isLoading = false;
      }
    },

    async fetchMetrics() {
      try {
        const result = await pipelineService.getMetrics();
        if (result.success) {
          this.metrics = result.metrics;
          this.pipelineData = result.pipeline_data;
        }
      } catch (error) {
        this.error = error.message;
      }
    }
  }
})
```

## 📊 Composants UI Essentiels

### 1. Indicateurs de Statut

```vue
<!-- components/AgentStatusIndicator.vue -->
<template>
  <div class="agent-status" :class="statusClass">
    <div class="status-dot"></div>
    <span>{{ agentName }}</span>
    <div class="execution-count">{{ executionCount }} exécutions</div>
  </div>
</template>

<script>
export default {
  props: ['agentName', 'status', 'executionCount'],
  computed: {
    statusClass() {
      return {
        'running': this.status === 'running',
        'stopped': this.status === 'stopped',
        'processing': this.status === 'processing',
        'error': this.status === 'error'
      }
    }
  }
}
</script>
```

### 2. Graphique des Prix en Temps Réel

```vue
<!-- components/PriceChart.vue -->
<template>
  <div class="price-chart">
    <canvas ref="chartCanvas"></canvas>
  </div>
</template>

<script>
import Chart from 'chart.js/auto'

export default {
  props: ['priceData'],
  data() {
    return {
      chart: null
    }
  },
  mounted() {
    this.initChart();
  },
  watch: {
    priceData: {
      handler(newData) {
        this.updateChart(newData);
      },
      deep: true
    }
  },
  methods: {
    initChart() {
      const ctx = this.$refs.chartCanvas.getContext('2d');
      this.chart = new Chart(ctx, {
        type: 'line',
        data: {
          labels: [],
          datasets: [{
            label: 'Prix Bitcoin (USD)',
            data: [],
            borderColor: 'rgb(75, 192, 192)',
            tension: 0.1
          }]
        },
        options: {
          responsive: true,
          scales: {
            y: {
              beginAtZero: false
            }
          }
        }
      });
    },
    updateChart(data) {
      if (this.chart && data.length > 0) {
        this.chart.data.labels = data.map(d => 
          new Date(d.timestamp).toLocaleTimeString()
        );
        this.chart.data.datasets[0].data = data.map(d => d.price);
        this.chart.update();
      }
    }
  }
}
</script>
```

### 3. Panneau de Métriques

```vue
<!-- components/MetricsPanel.vue -->
<template>
  <div class="metrics-panel">
    <div class="metric-card">
      <h3>Exécutions Totales</h3>
      <div class="metric-value">{{ metrics.total_executions }}</div>
    </div>
    <div class="metric-card">
      <h3>Taux de Succès</h3>
      <div class="metric-value">{{ metrics.success_rate }}%</div>
    </div>
    <div class="metric-card">
      <h3>Prédictions</h3>
      <div class="metric-value">{{ metrics.predictions_count }}</div>
    </div>
    <div class="metric-card">
      <h3>Signaux</h3>
      <div class="metric-value">{{ metrics.signals_count }}</div>
    </div>
  </div>
</template>
```

## 🔄 Gestion des Mises à Jour Temps Réel

### Option 1: Polling HTTP
```javascript
// Mise à jour toutes les 2 secondes
const pollingInterval = setInterval(async () => {
  await store.fetchMetrics();
  await store.fetchStatus();
}, 2000);
```

### Option 2: WebSocket (recommandé pour production)
```javascript
// services/websocketService.js
class WebSocketService {
  constructor(url = 'ws://localhost:5000/ws') {
    this.url = url;
    this.ws = null;
    this.callbacks = new Map();
  }

  connect() {
    this.ws = new WebSocket(this.url);
    
    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      const callback = this.callbacks.get(data.type);
      if (callback) callback(data.payload);
    };
  }

  subscribe(eventType, callback) {
    this.callbacks.set(eventType, callback);
  }
}
```

## 🎨 Styles et Thème

### Variables CSS
```css
:root {
  --primary-color: #667eea;
  --success-color: #10b981;
  --warning-color: #f59e0b;
  --error-color: #ef4444;
  --bg-primary: #111421;
  --bg-card: rgba(255, 255, 255, 0.08);
  --text-primary: #f3e8ff;
  --border-color: rgba(255, 255, 255, 0.12);
}
```

### Composants Stylés
```css
.agent-status {
  display: flex;
  align-items: center;
  padding: 1rem;
  background: var(--bg-card);
  border-radius: 0.5rem;
  backdrop-filter: blur(10px);
}

.status-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  margin-right: 0.5rem;
}

.running .status-dot {
  background: var(--success-color);
  animation: pulse 2s infinite;
}

.stopped .status-dot {
  background: #6b7280;
}

.processing .status-dot {
  background: var(--warning-color);
  animation: pulse 1s infinite;
}

.error .status-dot {
  background: var(--error-color);
  animation: pulse 1s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
```

## 🚀 Configuration et Déploiement

### Variables d'Environnement
```env
# .env
VITE_API_URL=http://localhost:5000
VITE_WS_URL=ws://localhost:5000/ws
VITE_POLLING_INTERVAL=2000
VITE_CHART_UPDATE_INTERVAL=1000
```

### Docker Frontend
```dockerfile
# Dockerfile.frontend
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 3000
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
```

### Docker Compose
```yaml
# docker-compose.yml
services:
  frontend:
    build: .
    ports:
      - "3000:3000"
    environment:
      - VITE_API_URL=http://backend:5000
    depends_on:
      - backend
```

## 📱 Fonctionnalités Avancées

### 1. Notifications Push
```javascript
// Notifications pour les événements importants
if (newTrade.status === 'FILLED') {
  new Notification(`Trade exécuté: ${newTrade.action} ${newTrade.quantity} BTC`);
}
```

### 2. Export de Données
```javascript
// Export CSV des trades
function exportTrades(trades) {
  const csv = trades.map(trade => 
    `${trade.timestamp},${trade.action},${trade.price},${trade.quantity}`
  ).join('\n');
  
  const blob = new Blob([csv], { type: 'text/csv' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'trades.csv';
  a.click();
}
```

### 3. Alertes Configurables
```javascript
// Système d'alertes basé sur les métriques
const alerts = [
  {
    condition: (metrics) => metrics.success_rate < 80,
    message: 'Taux de succès faible détecté',
    severity: 'warning'
  },
  {
    condition: (data) => data.some(d => d.price < 100000),
    message: 'Prix Bitcoin sous 100k USD',
    severity: 'info'
  }
];
```

## 🔧 Debugging et Monitoring

### Logs Frontend
```javascript
// utils/logger.js
class Logger {
  static log(level, message, data = null) {
    const timestamp = new Date().toISOString();
    console[level](`[${timestamp}] ${message}`, data);
    
    // Envoyer au backend pour monitoring
    if (level === 'error') {
      fetch('/api/frontend-logs', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ level, message, data, timestamp })
      });
    }
  }
}
```

### Performance Monitoring
```javascript
// Mesurer les temps de réponse API
const apiTimer = {
  start: Date.now(),
  end() {
    const duration = Date.now() - this.start;
    Logger.log('info', `API call duration: ${duration}ms`);
    return duration;
  }
};
```

## 📋 Checklist d'Implémentation

### Phase 1: Base
- [ ] Configuration du projet (Vue.js/React)
- [ ] Service API avec toutes les endpoints
- [ ] Store pour la gestion d'état
- [ ] Composant de statut du pipeline
- [ ] Contrôles start/stop

### Phase 2: Données
- [ ] Affichage des métriques temps réel
- [ ] Graphique des prix Bitcoin
- [ ] Liste des trades récents
- [ ] Indicateurs techniques

### Phase 3: UX
- [ ] Design responsive
- [ ] Animations et transitions
- [ ] Notifications utilisateur
- [ ] Gestion des erreurs

### Phase 4: Avancé
- [ ] WebSocket pour temps réel
- [ ] Export de données
- [ ] Système d'alertes
- [ ] Monitoring des performances

## 🔗 Ressources Utiles

- [Documentation uAgent](https://docs.fetch.ai/uAgents/)
- [API CoinGecko](https://www.coingecko.com/en/api)
- [API CryptoCompare](https://min-api.cryptocompare.com/)
- [ASI:One Documentation](https://docs.fetch.ai/concepts/ai-agents/ai-engine)
- [Chart.js](https://www.chartjs.org/)
- [Vue.js](https://vuejs.org/) ou [React](https://reactjs.org/)

---

**Note**: Ce guide couvre l'implémentation complète d'un frontend pour la pipeline CryptoPilot. Adaptez les technologies selon vos préférences (React vs Vue, etc.) tout en conservant la même structure d'APIs et de données.
