<template>
  <article class="bento-item bento-medium">
    <div class="crypto-widget">
      <div class="crypto-mini-header">
        <img
          v-if="cryptoData"
          :src="cryptoData.image"
          :alt="cryptoData.name"
          class="crypto-mini-icon"
        />
        <span class="crypto-mini-symbol">{{
          cryptoData?.symbol?.toUpperCase() || "?"
        }}</span>
      </div>
      <div class="crypto-mini-price">
        {{ formatPrice(cryptoData?.current_price || 0) }}
      </div>
      <div
        :class="[
          'crypto-mini-change',
          cryptoData?.price_change_percentage_24h >= 0
            ? 'positive'
            : 'negative',
        ]"
      >
        {{ formatPercentage(cryptoData?.price_change_percentage_24h || 0) }}
      </div>
    </div>
  </article>
</template>

<script>
import cryptoService from "../../services/cryptoService";

export default {
  name: "CryptoWidget",
  props: {
    cryptoData: {
      type: Object,
      required: true,
    },
  },
  methods: {
    formatPrice(price) {
      return cryptoService.formatPrice(price);
    },
    formatPercentage(percentage) {
      return cryptoService.formatPercentage(percentage);
    },
  },
};
</script>

<style scoped>
.crypto-widget {
  padding: 16px;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  color: white;
}

.crypto-mini-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.crypto-mini-icon {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  box-shadow: 0 3px 8px rgba(0, 0, 0, 0.2);
}

.crypto-mini-symbol {
  font-size: 13px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.8);
  text-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
  letter-spacing: 0.3px;
}

.crypto-mini-price {
  font-size: 18px;
  font-weight: 700;
  color: #ffffff;
  margin-bottom: 8px;
  line-height: 1.2;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.crypto-mini-change {
  font-size: 13px;
  font-weight: 600;
  text-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
}

.crypto-mini-change.positive {
  color: #22c55e;
}

.crypto-mini-change.negative {
  color: #ef4444;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .crypto-widget {
    padding: 12px;
  }

  .crypto-mini-price {
    font-size: 16px;
  }
}

@media (max-width: 480px) {
  .crypto-widget {
    padding: 8px;
  }

  .crypto-mini-symbol {
    font-size: 11px;
  }

  .crypto-mini-price {
    font-size: 14px;
  }

  .crypto-mini-change {
    font-size: 11px;
  }
}
</style>
