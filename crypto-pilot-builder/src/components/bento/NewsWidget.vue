<template>
  <article class="bento-item bento-medium" v-if="article">
    <div
      class="news-single-widget"
      @click="openNewsLink(article.url)"
      :style="{ backgroundImage: `url(${backgroundImage})` }"
    >
      <div class="news-single-overlay"></div>
      <div class="news-single-content">
        <div class="news-single-header">
          <span class="news-single-icon">📰</span>
          <span class="news-single-source">{{ article.source }}</span>
          <span v-if="isPersonalized" class="personalization-badge">✨</span>
        </div>
        <h4 class="news-single-title">{{ article.title }}</h4>
        <div class="news-single-time">{{ article.time }}</div>
      </div>
    </div>
  </article>
</template>

<script>
export default {
  name: "NewsWidget",
  props: {
    article: {
      type: Object,
      required: true,
    },
    isPersonalized: {
      type: Boolean,
      default: false,
    },
    backgroundImageIndex: {
      type: Number,
      default: 0,
    },
  },
  computed: {
    backgroundImage() {
      const images = [
        "https://images.unsplash.com/photo-1621761191319-c6fb62004040?w=400&h=300&fit=crop&crop=center",
        "https://images.unsplash.com/photo-1639762681485-074b7f938ba0?w=400&h=300&fit=crop&crop=center",
        "https://images.unsplash.com/photo-1518546305927-5a555bb7020d?w=400&h=300&fit=crop&crop=center",
        "https://images.unsplash.com/photo-1559526324-4b87b5e36e44?w=400&h=300&fit=crop&crop=center",
      ];
      return images[this.backgroundImageIndex % images.length];
    },
  },
  methods: {
    openNewsLink(url) {
      if (url && url !== "#") {
        window.open(url, "_blank");
      }
    },
  },
};
</script>

<style scoped>
/* News widgets */
.news-single-widget {
  height: 100%;
  border-radius: 16px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
}

.news-single-widget:hover {
  transform: scale(1.02);
}

.news-single-content {
  position: relative;
  z-index: 2;
  padding: 16px;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  color: white;
}

.news-single-header {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 8px;
}

.news-single-icon {
  font-size: 14px;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3));
}

.news-single-source {
  font-size: 10px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
  text-transform: uppercase;
  background: rgba(255, 255, 255, 0.15);
  padding: 2px 6px;
  border-radius: 6px;
  letter-spacing: 0.5px;
  text-shadow: 0 2px 6px rgba(0, 0, 0, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.news-single-title {
  font-size: 13px;
  font-weight: 600;
  color: #ffffff;
  line-height: 1.3;
  margin: 0 0 auto 0;
  text-shadow: 0 1px 4px rgba(0, 0, 0, 0.8);
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
}

.news-single-time {
  color: rgba(255, 255, 255, 0.8);
  font-weight: 500;
  font-size: 10px;
  background: rgba(0, 0, 0, 0.3);
  padding: 3px 8px;
  border-radius: 8px;
  width: fit-content;
  text-shadow: 0 1px 4px rgba(0, 0, 0, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.news-single-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    135deg,
    rgba(0, 0, 0, 0.7) 0%,
    rgba(0, 0, 0, 0.4) 50%,
    rgba(0, 0, 0, 0.8) 100%
  );
  backdrop-filter: blur(1px);
  border-radius: inherit;
}

/* Badge de personnalisation */
.personalization-badge {
  font-size: 10px;
  color: #fbbf24;
  animation: sparkle 2s ease-in-out infinite;
  margin-left: 4px;
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
