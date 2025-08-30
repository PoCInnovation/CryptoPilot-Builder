<template>
  <article class="bento-item bento-large">
    <div class="crypto-main-widget">
      <div class="crypto-compact-header">
        <div class="crypto-title-section">
          <img
            v-if="cryptoData"
            :src="cryptoIcon"
            :alt="cryptoName"
            class="crypto-compact-icon"
          />
          <div class="crypto-compact-info">
            <h3 class="crypto-compact-name">
              {{ cryptoName }}
              <span v-if="isPersonalized" class="personalization-badge"
                >✨</span
              >
            </h3>
            <span class="crypto-compact-symbol">{{ cryptoSymbol }}</span>
          </div>
        </div>
        <div class="crypto-metrics">
          <div class="crypto-compact-price">
            {{ formatPrice(cryptoData?.current_price || 0) }}
          </div>
          <div
            :class="[
              'crypto-compact-change',
              cryptoData?.price_change_percentage_24h >= 0
                ? 'positive'
                : 'negative',
            ]"
          >
            {{ formatPercentage(cryptoData?.price_change_percentage_24h || 0) }}
          </div>
        </div>
      </div>
      <div class="chart-section" v-if="cryptoData?.sparkline_in_7d">
        <div class="chart-period-label">7 jours</div>
        <canvas
          ref="cryptoChart"
          class="full-sparkline-chart"
          @mousemove="handleChartMouseMove"
          @mouseleave="handleChartMouseLeave"
          @click="handleChartClick"
        ></canvas>
      </div>
    </div>
  </article>
</template>

<script>
import cryptoService from "../../services/cryptoService";

export default {
  name: "MainCryptoWidget",
  props: {
    cryptoData: {
      type: Object,
      default: null,
    },
    isPersonalized: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      chartPoints: null,
      chartBounds: null,
    };
  },
  computed: {
    cryptoName() {
      return this.cryptoData?.name || "Bitcoin";
    },
    cryptoSymbol() {
      return this.cryptoData?.symbol?.toUpperCase() || "BTC";
    },
    cryptoIcon() {
      return (
        this.cryptoData?.image ||
        "https://assets.coingecko.com/coins/images/1/large/bitcoin.png"
      );
    },
  },
  methods: {
    formatPrice(price) {
      return cryptoService.formatPrice(price);
    },
    formatPercentage(percentage) {
      return cryptoService.formatPercentage(percentage);
    },
    drawSparkline() {
      if (!this.cryptoData?.sparkline_in_7d?.price || !this.$refs.cryptoChart)
        return;

      const canvas = this.$refs.cryptoChart;
      const ctx = canvas.getContext("2d");
      const prices = this.cryptoData.sparkline_in_7d.price;

      // Définir les dimensions du canvas
      const dpr = window.devicePixelRatio || 1;
      const containerWidth = canvas.parentElement.clientWidth || 400;
      const containerHeight = canvas.parentElement.clientHeight || 140;

      const width = (canvas.width = containerWidth * dpr);
      const height = (canvas.height = containerHeight * dpr);

      // Mise à l'échelle pour la densité de pixels
      ctx.scale(dpr, dpr);
      canvas.style.width = containerWidth + "px";
      canvas.style.height = containerHeight + "px";

      // Effacer le canvas
      ctx.clearRect(0, 0, containerWidth, containerHeight);

      // Trouver min et max pour normaliser
      const min = Math.min(...prices);
      const max = Math.max(...prices);
      const range = max - min;

      // Marges pour le graphique
      const margin = 15;
      const chartWidth = containerWidth - margin * 2;
      const chartHeight = containerHeight - margin * 2;

      // Couleur selon la tendance
      const isPositive = this.cryptoData.price_change_percentage_24h >= 0;
      const lineColor = isPositive ? "#22C55E" : "#EF4444";
      const gradientColorStart = isPositive
        ? "rgba(34, 197, 94, 0.4)"
        : "rgba(239, 68, 68, 0.4)";
      const gradientColorEnd = isPositive
        ? "rgba(34, 197, 94, 0.05)"
        : "rgba(239, 68, 68, 0.05)";

      // Créer un gradient pour le remplissage
      const gradient = ctx.createLinearGradient(
        0,
        margin,
        0,
        margin + chartHeight
      );
      gradient.addColorStop(0, gradientColorStart);
      gradient.addColorStop(1, gradientColorEnd);

      // Calculer les points avec une courbe lissée
      const points = prices.map((price, index) => ({
        x: margin + (index / (prices.length - 1)) * chartWidth,
        y: margin + chartHeight - ((price - min) / range) * chartHeight,
        price: price,
        index: index,
      }));

      // Stocker les points pour l'interactivité
      this.chartPoints = points;
      this.chartBounds = {
        left: margin,
        right: margin + chartWidth,
        top: margin,
        bottom: margin + chartHeight,
        containerWidth,
        containerHeight,
      };

      // Dessiner le remplissage sous la courbe
      ctx.beginPath();
      ctx.moveTo(points[0].x, margin + chartHeight);

      // Créer une courbe lissée avec des points de contrôle
      for (let i = 0; i < points.length; i++) {
        if (i === 0) {
          ctx.lineTo(points[i].x, points[i].y);
        } else if (i === points.length - 1) {
          ctx.lineTo(points[i].x, points[i].y);
        } else {
          const xc = (points[i].x + points[i + 1].x) / 2;
          const yc = (points[i].y + points[i + 1].y) / 2;
          ctx.quadraticCurveTo(points[i].x, points[i].y, xc, yc);
        }
      }

      ctx.lineTo(points[points.length - 1].x, margin + chartHeight);
      ctx.closePath();
      ctx.fillStyle = gradient;
      ctx.fill();

      // Dessiner la ligne principale avec effet glow
      ctx.strokeStyle = lineColor;
      ctx.lineWidth = 3;
      ctx.lineCap = "round";
      ctx.lineJoin = "round";
      ctx.shadowColor = lineColor;
      ctx.shadowBlur = 8;

      ctx.beginPath();
      for (let i = 0; i < points.length; i++) {
        if (i === 0) {
          ctx.moveTo(points[i].x, points[i].y);
        } else if (i === points.length - 1) {
          ctx.lineTo(points[i].x, points[i].y);
        } else {
          const xc = (points[i].x + points[i + 1].x) / 2;
          const yc = (points[i].y + points[i + 1].y) / 2;
          ctx.quadraticCurveTo(points[i].x, points[i].y, xc, yc);
        }
      }
      ctx.stroke();

      // Dessiner des points de données clés
      ctx.shadowBlur = 0;
      ctx.fillStyle = lineColor;

      // Point de début
      ctx.beginPath();
      ctx.arc(points[0].x, points[0].y, 5, 0, 2 * Math.PI);
      ctx.fill();

      // Point de fin avec un effet spécial
      ctx.beginPath();
      ctx.arc(
        points[points.length - 1].x,
        points[points.length - 1].y,
        6,
        0,
        2 * Math.PI
      );
      ctx.fill();

      // Ajouter un ring autour du point final
      ctx.strokeStyle = lineColor;
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.arc(
        points[points.length - 1].x,
        points[points.length - 1].y,
        10,
        0,
        2 * Math.PI
      );
      ctx.stroke();
    },

    handleChartMouseMove(event) {
      if (!this.chartPoints || !this.chartBounds) return;

      const canvas = this.$refs.cryptoChart;
      const rect = canvas.getBoundingClientRect();
      const x = event.clientX - rect.left;
      const y = event.clientY - rect.top;

      // Trouver le point le plus proche
      let closestPoint = null;
      let minDistance = Infinity;

      for (const point of this.chartPoints) {
        const distance = Math.sqrt(
          Math.pow(x - point.x, 2) + Math.pow(y - point.y, 2)
        );
        if (distance < minDistance && distance < 30) {
          minDistance = distance;
          closestPoint = point;
        }
      }

      if (closestPoint) {
        this.showTooltip(closestPoint, x, y);
        this.highlightPoint(closestPoint);
        canvas.style.cursor = "pointer";
      } else {
        this.hideTooltip();
        this.redrawChart();
        canvas.style.cursor = "default";
      }
    },

    handleChartMouseLeave() {
      this.hideTooltip();
      this.redrawChart();
      const canvas = this.$refs.cryptoChart;
      if (canvas) canvas.style.cursor = "default";
    },

    handleChartClick(event) {
      if (!this.chartPoints || !this.chartBounds) return;

      const canvas = this.$refs.cryptoChart;
      const rect = canvas.getBoundingClientRect();
      const x = event.clientX - rect.left;
      const y = event.clientY - rect.top;

      // Trouver le point cliqué
      for (const point of this.chartPoints) {
        const distance = Math.sqrt(
          Math.pow(x - point.x, 2) + Math.pow(y - point.y, 2)
        );
        if (distance < 30) {
          this.animatePointClick(point);
          break;
        }
      }
    },

    showTooltip(point, mouseX, mouseY) {
      // Créer ou mettre à jour le tooltip
      let tooltip = document.getElementById("chart-tooltip");
      if (!tooltip) {
        tooltip = document.createElement("div");
        tooltip.id = "chart-tooltip";
        tooltip.style.position = "absolute";
        tooltip.style.background = "rgba(0, 0, 0, 0.9)";
        tooltip.style.color = "white";
        tooltip.style.padding = "8px 12px";
        tooltip.style.borderRadius = "8px";
        tooltip.style.fontSize = "12px";
        tooltip.style.fontWeight = "600";
        tooltip.style.pointerEvents = "none";
        tooltip.style.zIndex = "1000";
        tooltip.style.border = "1px solid rgba(255, 255, 255, 0.2)";
        tooltip.style.boxShadow = "0 4px 12px rgba(0, 0, 0, 0.3)";
        tooltip.style.transition = "all 0.2s ease";
        document.body.appendChild(tooltip);
      }

      // Calculer la date approximative (7 jours en arrière)
      const daysAgo = Math.round(
        ((this.chartPoints.length - point.index - 1) * 7) /
          this.chartPoints.length
      );
      const dateText =
        daysAgo === 0
          ? "Maintenant"
          : `Il y a ${daysAgo} jour${daysAgo > 1 ? "s" : ""}`;

      tooltip.innerHTML = `
        <div style="text-align: center;">
          <div style="color: #22C55E; font-size: 14px; font-weight: 700;">
            ${this.formatPrice(point.price)}
          </div>
          <div style="color: rgba(255, 255, 255, 0.7); font-size: 10px; margin-top: 2px;">
            ${dateText}
          </div>
        </div>
      `;

      // Positionner le tooltip
      const canvas = this.$refs.cryptoChart;
      const canvasRect = canvas.getBoundingClientRect();
      tooltip.style.left = canvasRect.left + mouseX + 10 + "px";
      tooltip.style.top = canvasRect.top + mouseY - 40 + "px";
      tooltip.style.opacity = "1";
    },

    hideTooltip() {
      const tooltip = document.getElementById("chart-tooltip");
      if (tooltip) {
        tooltip.style.opacity = "0";
        setTimeout(() => {
          if (tooltip.parentNode) {
            tooltip.parentNode.removeChild(tooltip);
          }
        }, 200);
      }
    },

    highlightPoint(point) {
      const canvas = this.$refs.cryptoChart;
      const ctx = canvas.getContext("2d");

      // Redessiner le graphique
      this.redrawChart();

      // Dessiner le point en surbrillance
      const isPositive = this.cryptoData.price_change_percentage_24h >= 0;
      const lineColor = isPositive ? "#22C55E" : "#EF4444";

      ctx.shadowColor = lineColor;
      ctx.shadowBlur = 15;
      ctx.fillStyle = lineColor;
      ctx.beginPath();
      ctx.arc(point.x, point.y, 8, 0, 2 * Math.PI);
      ctx.fill();

      // Ajouter un ring animé
      ctx.shadowBlur = 0;
      ctx.strokeStyle = lineColor;
      ctx.lineWidth = 3;
      ctx.beginPath();
      ctx.arc(point.x, point.y, 15, 0, 2 * Math.PI);
      ctx.stroke();

      // Dessiner une ligne verticale pointillée
      ctx.strokeStyle = "rgba(255, 255, 255, 0.3)";
      ctx.lineWidth = 1;
      ctx.setLineDash([3, 3]);
      ctx.beginPath();
      ctx.moveTo(point.x, this.chartBounds.top);
      ctx.lineTo(point.x, this.chartBounds.bottom);
      ctx.stroke();
      ctx.setLineDash([]);
    },

    animatePointClick(point) {
      const canvas = this.$refs.cryptoChart;
      const ctx = canvas.getContext("2d");

      let animationFrame = 0;
      const animate = () => {
        if (animationFrame < 20) {
          this.redrawChart();

          const isPositive = this.cryptoData.price_change_percentage_24h >= 0;
          const lineColor = isPositive ? "#22C55E" : "#EF4444";

          // Effet de pulsation
          const pulseRadius = 8 + Math.sin(animationFrame * 0.5) * 5;

          ctx.shadowColor = lineColor;
          ctx.shadowBlur = 20;
          ctx.fillStyle = lineColor;
          ctx.beginPath();
          ctx.arc(point.x, point.y, pulseRadius, 0, 2 * Math.PI);
          ctx.fill();

          animationFrame++;
          requestAnimationFrame(animate);
        } else {
          this.redrawChart();
        }
      };

      animate();
    },

    redrawChart() {
      // Redessiner le graphique complet
      this.drawSparkline();
    },
  },
  watch: {
    cryptoData: {
      handler(newData) {
        if (newData?.sparkline_in_7d?.price) {
          this.$nextTick(() => {
            this.drawSparkline();
          });
        }
      },
      immediate: true,
    },
  },
  beforeUnmount() {
    // Nettoyer les événements du graphique
    const canvas = this.$refs.cryptoChart;
    if (canvas) {
      canvas.removeEventListener("mousemove", this.handleChartMouseMove);
      canvas.removeEventListener("mouseleave", this.handleChartMouseLeave);
      canvas.removeEventListener("click", this.handleChartClick);
    }

    // Supprimer le tooltip s'il existe
    const tooltip = document.getElementById("chart-tooltip");
    if (tooltip && tooltip.parentNode) {
      tooltip.parentNode.removeChild(tooltip);
    }
  },
};
</script>

<style scoped>
/* Bitcoin Main Widget - Centré style Apple */
.crypto-main-widget {
  padding: 20px;
  height: 100%;
  display: flex;
  flex-direction: column;
  color: white;
  position: relative;
}

.crypto-compact-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
  z-index: 2;
  position: relative;
}

.crypto-title-section {
  display: flex;
  align-items: center;
  gap: 10px;
}

.crypto-compact-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.crypto-compact-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.crypto-compact-name {
  font-size: 16px;
  font-weight: 700;
  margin: 0;
  color: #ffffff;
  line-height: 1.2;
}

.crypto-compact-symbol {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
  font-weight: 600;
}

.crypto-metrics {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
}

.crypto-compact-price {
  font-size: 20px;
  font-weight: 800;
  color: #ffffff;
  line-height: 1;
}

.crypto-compact-change {
  font-size: 13px;
  font-weight: 600;
}

.crypto-compact-change.positive {
  color: #22c55e;
}

.crypto-compact-change.negative {
  color: #ef4444;
}

.chart-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  position: relative;
  min-height: 160px;
}

.chart-period-label {
  position: absolute;
  top: 8px;
  left: 8px;
  font-size: 10px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.5);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  z-index: 2;
}

.full-sparkline-chart {
  width: 100%;
  height: 100%;
  border-radius: 16px;
  background: transparent;
}

/* Badge de personnalisation */
.personalization-badge {
  font-size: 14px;
  color: #fbbf24;
  animation: sparkle 2s ease-in-out infinite;
  margin-left: 6px;
}

@keyframes sparkle {
  0%,
  100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.7;
    transform: scale(1.1);
  }
}
</style>
