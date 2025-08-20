<template>
  <article class="bento-item bento-medium">
    <div class="trending-widget">
      <div class="trending-header">
        <span class="trending-icon">🔥</span>
        <span class="trending-title">Trending</span>
      </div>
      <div class="trending-container">
        <div
          class="trending-list"
          :style="{
            transform: `translateY(${scrollOffset}px)`,
          }"
        >
          <div
            v-for="(coin, index) in extendedCoins"
            :key="coin.id + '_' + index"
            class="trending-item"
          >
            <img
              :src="coin.thumb"
              :alt="coin.name"
              class="trending-coin-icon"
            />
            <span class="trending-coin-name">{{
              coin.name || coin.symbol
            }}</span>
            <span class="trending-rank"
              >#{{ coin.market_cap_rank || "?" }}</span
            >
          </div>
        </div>
      </div>
    </div>
  </article>
</template>

<script>
export default {
  name: "TrendingWidget",
  props: {
    trendingCoins: {
      type: Array,
      default: () => [],
    },
  },
  data() {
    return {
      scrollOffset: 0,
      scrollInterval: null,
    };
  },
  computed: {
    extendedCoins() {
      // Dupliquer les coins pour un défilement infini
      return [...this.trendingCoins, ...this.trendingCoins];
    },
  },
  methods: {
    startScrolling() {
      if (this.trendingCoins.length <= 3) return;

      this.scrollInterval = setInterval(() => {
        this.smoothScroll();
      }, 50); // Défilement fluide toutes les 50ms
    },
    smoothScroll() {
      if (this.trendingCoins.length <= 3) return;

      const itemHeight = 56; // Hauteur réelle : min-height 44px + padding 10px + gap 12px / 2
      const scrollStep = 0.5; // Défilement plus lent et plus fluide

      this.scrollOffset -= scrollStep;

      // Calculer quand remettre à zéro pour un défilement infini
      const totalItemsHeight = this.trendingCoins.length * itemHeight;

      if (Math.abs(this.scrollOffset) >= totalItemsHeight) {
        this.scrollOffset = 0;
      }
    },
    stopScrolling() {
      if (this.scrollInterval) {
        clearInterval(this.scrollInterval);
        this.scrollInterval = null;
      }
    },
  },
  mounted() {
    this.startScrolling();
  },
  beforeUnmount() {
    this.stopScrolling();
  },
  watch: {
    trendingCoins: {
      handler() {
        // Redémarrer le défilement si les données changent
        this.stopScrolling();
        this.$nextTick(() => {
          this.startScrolling();
        });
      },
    },
  },
};
</script>

<style scoped>
.trending-widget {
  padding: 16px;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  color: white;
}

.trending-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.trending-icon {
  font-size: 16px;
}

.trending-title {
  font-size: 13px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.8);
  text-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
  letter-spacing: 0.3px;
}

.trending-container {
  flex: 1;
  overflow: hidden;
  position: relative;
  height: 100px;
}

.trending-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  transition: transform 0.05s linear;
  will-change: transform;
}

.trending-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  min-height: 28px;
  flex-shrink: 0;
  transition: all 0.3s ease;
}

.trending-item:last-child {
  border-bottom: none;
}

.trending-item:hover {
  transform: translateX(4px);
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  padding-left: 8px;
}

.trending-coin-icon {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
  transition: transform 0.3s ease;
}

.trending-item:hover .trending-coin-icon {
  transform: scale(1.1);
}

.trending-coin-name {
  font-size: 12px;
  font-weight: 600;
  color: #ffffff;
  flex: 1;
  text-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
  letter-spacing: 0.3px;
}

.trending-rank {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.6);
  font-weight: 500;
  background: rgba(255, 255, 255, 0.1);
  padding: 2px 6px;
  border-radius: 6px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
}

.trending-item:hover .trending-rank {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.3);
  color: rgba(255, 255, 255, 0.9);
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .trending-widget {
    padding: 12px;
  }

  .trending-container {
    height: 80px;
  }
}

@media (max-width: 480px) {
  .trending-widget {
    padding: 8px;
  }

  .trending-title {
    font-size: 11px;
  }

  .trending-coin-name {
    font-size: 10px;
  }

  .trending-rank {
    font-size: 8px;
    padding: 1px 4px;
  }

  .trending-container {
    height: 60px;
  }
}
</style>
