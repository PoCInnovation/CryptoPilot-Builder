<template>
  <div class="bento-grid">
    <!-- Widget crypto principal (Bitcoin ou crypto préférée) -->
    <MainCryptoWidget
      :crypto-data="mainCryptoData"
      :is-personalized="isPersonalized"
    />

    <!-- Widget Ethereum -->
    <CryptoWidget :crypto-data="ethereumData" />

    <!-- Widget Market Cap -->
    <StatsWidget
      title="Market Cap"
      :value="globalStats?.total_market_cap?.usd || 0"
      :change="globalStats?.market_cap_change_percentage_24h_usd || null"
      icon="🌍"
      type="marketcap"
      size="bento-medium"
    />

    <!-- Widget Top Gainer -->
    <article class="bento-item bento-medium" v-if="topGainer">
      <div class="stats-widget">
        <div class="stats-header">
          <span class="stats-icon">📈</span>
          <span class="stats-title">Top Gainer</span>
        </div>
        <div class="gainer-content">
          <div class="gainer-name">{{ topGainer.symbol?.toUpperCase() }}</div>
          <div class="gainer-change positive">
            {{ formatPercentage(topGainer.price_change_percentage_24h) }}
          </div>
        </div>
      </div>
    </article>

    <!-- Widgets de nouvelles -->
    <NewsWidget
      v-for="(article, index) in displayNews.slice(0, 4)"
      :key="`news-${index}`"
      :article="article"
      :is-personalized="isPersonalized && personalizedNews.length > 0"
      :background-image-index="index"
    />

    <!-- Widget Trending -->
    <TrendingWidget :trending-coins="trendingCoins" />

    <!-- Widget Fear & Greed Index -->
    <article class="bento-item bento-square">
      <div class="fear-greed-widget">
        <div class="fear-greed-header">
          <span class="fear-greed-title">Fear & Greed</span>
        </div>
        <div class="fear-greed-content">
          <div class="fear-greed-value">{{ fearGreedIndex }}</div>
          <div class="fear-greed-label">{{ fearGreedLabel }}</div>
        </div>
      </div>
    </article>

    <!-- Widget Volume -->
    <StatsWidget
      title="24h Volume"
      :value="globalStats?.total_volume?.usd || 0"
      icon="💰"
      type="marketcap"
      size="bento-square"
    />
  </div>
</template>

<script>
import MainCryptoWidget from "./MainCryptoWidget.vue";
import NewsWidget from "./NewsWidget.vue";
import StatsWidget from "./StatsWidget.vue";
import CryptoWidget from "./CryptoWidget.vue";
import TrendingWidget from "./TrendingWidget.vue";
import cryptoService from "../../services/cryptoService";

export default {
  name: "BentoGrid",
  components: {
    MainCryptoWidget,
    NewsWidget,
    StatsWidget,
    CryptoWidget,
    TrendingWidget,
  },
  props: {
    // Données crypto
    mainCryptoData: {
      type: Object,
      default: null,
    },
    ethereumData: {
      type: Object,
      default: null,
    },
    globalStats: {
      type: Object,
      default: null,
    },
    topCryptos: {
      type: Array,
      default: () => [],
    },
    trendingCoins: {
      type: Array,
      default: () => [],
    },
    // Nouvelles
    displayNews: {
      type: Array,
      default: () => [],
    },
    personalizedNews: {
      type: Array,
      default: () => [],
    },
    // Personnalisation
    isPersonalized: {
      type: Boolean,
      default: false,
    },
    // Fear & Greed
    fearGreedIndex: {
      type: Number,
      default: 50,
    },
  },
  computed: {
    topGainer() {
      if (!this.topCryptos.length) return null;
      return this.topCryptos.reduce((prev, current) =>
        prev.price_change_percentage_24h > current.price_change_percentage_24h
          ? prev
          : current
      );
    },
    fearGreedLabel() {
      if (this.fearGreedIndex >= 75) return "Extreme Greed";
      if (this.fearGreedIndex >= 55) return "Greed";
      if (this.fearGreedIndex >= 45) return "Neutral";
      if (this.fearGreedIndex >= 25) return "Fear";
      return "Extreme Fear";
    },
  },
  methods: {
    formatPercentage(percentage) {
      return cryptoService.formatPercentage(percentage);
    },
  },
};
</script>

<style scoped>
/* Bento Grid Layout - Style Apple */
.bento-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  grid-template-rows: repeat(4, 140px);
  gap: 12px;
  width: 100%;
  max-width: 1000px;
  margin: 40px auto;
  padding: 0 20px;
}

/* Styles globaux pour les items du bento */
:deep(.bento-item) {
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.12);
  overflow: hidden;
  transition: all 0.2s ease;
  position: relative;
  box-shadow: 0 1px 10px rgba(0, 0, 0, 0.15);
}

:deep(.bento-item:hover) {
  transform: scale(1.02);
  background: rgba(255, 255, 255, 0.12);
  border-color: rgba(255, 255, 255, 0.2);
}

/* Bitcoin au centre - Style Apple */
:deep(.bento-large) {
  grid-column: 3 / 5;
  grid-row: 2 / 4;
  border-radius: 28px;
}

/* Disposition autour du Bitcoin */
/* Ligne du haut */
:deep(.bento-item:nth-child(2)) {
  /* Ethereum */
  grid-column: 1 / 3;
  grid-row: 1 / 2;
}

:deep(.bento-item:nth-child(3)) {
  /* Market Cap */
  grid-column: 3 / 5;
  grid-row: 1 / 2;
}

:deep(.bento-item:nth-child(4)) {
  /* Top Gainer */
  grid-column: 5 / 7;
  grid-row: 1 / 2;
}

/* Côtés du Bitcoin - Cases hautes qui se collent (2 cases chacune) */
:deep(.bento-item:nth-child(5)) {
  /* News 1 */
  grid-column: 1 / 3;
  grid-row: 2 / 3;
}

:deep(.bento-item:nth-child(6)) {
  /* News 2 */
  grid-column: 5 / 7;
  grid-row: 2 / 3;
}

:deep(.bento-item:nth-child(7)) {
  /* Trending */
  grid-column: 1 / 3;
  grid-row: 3 / 4;
}

:deep(.bento-item:nth-child(8)) {
  /* Fear & Greed */
  grid-column: 5 / 7;
  grid-row: 3 / 4;
}

/* Ligne du bas */
:deep(.bento-item:nth-child(9)) {
  /* News 3 */
  grid-column: 1 / 2;
  grid-row: 4 / 5;
}

:deep(.bento-item:nth-child(10)) {
  /* Volume */
  grid-column: 2 / 6;
  grid-row: 4 / 5;
}

:deep(.bento-item:nth-child(11)) {
  /* News 4 */
  grid-column: 6 / 7;
  grid-row: 4 / 5;
}

/* Styles spéciaux pour le Top Gainer */
.stats-widget {
  padding: 16px;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  color: white;
}

.stats-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-bottom: 8px;
}

.stats-icon {
  font-size: 16px;
}

.stats-title {
  font-size: 13px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.8);
  text-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
  letter-spacing: 0.3px;
}

.gainer-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.gainer-name {
  font-size: 16px;
  font-weight: 700;
  color: #ffffff;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.gainer-change {
  font-size: 14px;
  font-weight: 600;
  text-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
}

.gainer-change.positive {
  color: #22c55e;
}

/* Styles spéciaux pour Fear & Greed */
.fear-greed-widget {
  padding: 16px;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  color: white;
}

.fear-greed-header {
  margin-bottom: 12px;
}

.fear-greed-title {
  font-size: 13px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.8);
  text-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
  letter-spacing: 0.3px;
}

.fear-greed-content {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 6px;
  height: 100%;
}

.fear-greed-value {
  font-size: 32px;
  font-weight: 800;
  color: #ffffff;
  line-height: 1;
  text-shadow: 0 3px 12px rgba(0, 0, 0, 0.4);
}

.fear-greed-label {
  font-size: 11px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.7);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  text-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
}

/* Responsive Design Apple Style */
@media (max-width: 1024px) {
  .bento-grid {
    grid-template-columns: repeat(4, 1fr);
    grid-template-rows: repeat(4, 130px);
    gap: 10px;
    max-width: 800px;
  }

  /* Bitcoin toujours centré */
  :deep(.bento-large) {
    grid-column: 2 / 4;
    grid-row: 2 / 4;
  }

  /* Réorganisation autour */
  :deep(.bento-item:nth-child(2)) {
    grid-column: 1 / 3;
    grid-row: 1 / 2;
  }
  :deep(.bento-item:nth-child(3)) {
    grid-column: 3 / 5;
    grid-row: 1 / 2;
  }
  :deep(.bento-item:nth-child(4)) {
    grid-column: 1 / 2;
    grid-row: 2 / 3;
  }
  :deep(.bento-item:nth-child(5)) {
    grid-column: 4 / 5;
    grid-row: 2 / 3;
  }
  :deep(.bento-item:nth-child(6)) {
    grid-column: 1 / 2;
    grid-row: 3 / 4;
  }
  :deep(.bento-item:nth-child(7)) {
    grid-column: 4 / 5;
    grid-row: 3 / 4;
  }
  :deep(.bento-item:nth-child(8)) {
    grid-column: 1 / 2;
    grid-row: 4 / 5;
  }
  :deep(.bento-item:nth-child(9)) {
    grid-column: 2 / 4;
    grid-row: 4 / 5;
  }
  :deep(.bento-item:nth-child(10)) {
    grid-column: 4 / 5;
    grid-row: 4 / 5;
  }
  :deep(.bento-item:nth-child(11)) {
    display: none;
  } /* Masqué sur tablette */
}

@media (max-width: 768px) {
  .bento-grid {
    grid-template-columns: repeat(3, 1fr);
    grid-template-rows: repeat(4, 120px);
    gap: 8px;
    max-width: 100%;
    margin: 20px auto;
    padding: 0;
  }

  /* Bitcoin centré sur mobile */
  :deep(.bento-large) {
    grid-column: 2 / 3;
    grid-row: 2 / 4;
    border-radius: 24px;
  }

  /* Disposition mobile */
  :deep(.bento-item:nth-child(2)) {
    grid-column: 1 / 4;
    grid-row: 1 / 2;
  }
  :deep(.bento-item:nth-child(3)) {
    grid-column: 1 / 2;
    grid-row: 2 / 3;
  }
  :deep(.bento-item:nth-child(4)) {
    grid-column: 3 / 4;
    grid-row: 2 / 3;
  }
  :deep(.bento-item:nth-child(5)) {
    grid-column: 1 / 2;
    grid-row: 3 / 4;
  }
  :deep(.bento-item:nth-child(6)) {
    grid-column: 3 / 4;
    grid-row: 3 / 4;
  }
  :deep(.bento-item:nth-child(7)) {
    grid-column: 1 / 4;
    grid-row: 4 / 5;
  }
  :deep(.bento-item:nth-child(8)),
  :deep(.bento-item:nth-child(9)),
  :deep(.bento-item:nth-child(10)),
  :deep(.bento-item:nth-child(11)) {
    display: none;
  }
}

@media (max-width: 480px) {
  .bento-grid {
    grid-template-columns: 1fr;
    grid-template-rows: repeat(5, 120px);
    gap: 8px;
    margin: 16px auto;
  }

  /* Mobile simple - stack vertical */
  :deep(.bento-large),
  :deep(.bento-item:nth-child(2)),
  :deep(.bento-item:nth-child(3)),
  :deep(.bento-item:nth-child(4)),
  :deep(.bento-item:nth-child(5)),
  :deep(.bento-item:nth-child(6)),
  :deep(.bento-item:nth-child(7)) {
    grid-column: 1 / 2;
  }

  :deep(.bento-large) {
    grid-row: 1 / 2;
  }
  :deep(.bento-item:nth-child(2)) {
    grid-row: 2 / 3;
  }
  :deep(.bento-item:nth-child(3)) {
    grid-row: 3 / 4;
  }
  :deep(.bento-item:nth-child(4)) {
    grid-row: 4 / 5;
  }
  :deep(.bento-item:nth-child(7)) {
    grid-row: 5 / 6;
  }
}
</style>
