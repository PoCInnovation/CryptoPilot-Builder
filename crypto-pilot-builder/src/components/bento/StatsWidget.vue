<template>
  <article class="bento-item" :class="size">
    <div class="stats-widget">
      <div class="stats-header">
        <span class="stats-icon">{{ icon }}</span>
        <span class="stats-title">{{ title }}</span>
      </div>

      <!-- Slot pour contenu personnalisé ou affichage par défaut -->
      <slot name="content">
        <div class="stats-value">{{ formattedValue }}</div>
        <div v-if="change !== null" :class="changeClass">
          {{ formattedChange }}
        </div>
      </slot>
    </div>
  </article>
</template>

<script>
import cryptoService from "../../services/cryptoService";

export default {
  name: "StatsWidget",
  props: {
    title: {
      type: String,
      required: true,
    },
    value: {
      type: Number,
      required: true,
    },
    change: {
      type: Number,
      default: null,
    },
    icon: {
      type: String,
      required: true,
    },
    type: {
      type: String,
      default: "number", // 'number', 'currency', 'percentage', 'marketcap'
      validator: (value) =>
        ["number", "currency", "percentage", "marketcap"].includes(value),
    },
    size: {
      type: String,
      default: "bento-medium", // 'bento-medium', 'bento-square'
      validator: (value) => ["bento-medium", "bento-square"].includes(value),
    },
  },
  computed: {
    formattedValue() {
      switch (this.type) {
        case "currency":
          return cryptoService.formatPrice(this.value);
        case "percentage":
          return cryptoService.formatPercentage(this.value);
        case "marketcap":
          return cryptoService.formatMarketCap(this.value);
        default:
          return this.value.toLocaleString();
      }
    },
    formattedChange() {
      if (this.change === null) return "";
      return cryptoService.formatPercentage(this.change);
    },
    changeClass() {
      if (this.change === null) return "";
      return ["stats-change", this.change >= 0 ? "positive" : "negative"];
    },
  },
};
</script>

<style scoped>
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

.stats-value {
  font-size: 20px;
  font-weight: 700;
  color: #ffffff;
  line-height: 1.2;
  margin: 0;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.stats-change {
  font-size: 13px;
  font-weight: 600;
  text-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
  margin-top: 4px;
}

.stats-change.positive {
  color: #22c55e;
}

.stats-change.negative {
  color: #ef4444;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .stats-widget {
    padding: 12px;
  }

  .stats-value {
    font-size: 18px;
  }
}

@media (max-width: 480px) {
  .stats-widget {
    padding: 8px;
  }

  .stats-title {
    font-size: 11px;
  }

  .stats-value {
    font-size: 16px;
  }

  .stats-change {
    font-size: 11px;
  }
}
</style>
