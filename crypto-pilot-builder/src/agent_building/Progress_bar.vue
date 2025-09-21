<template>
  <div class="progress-container">
    <div class="progress-track">
      <div class="progress-fill" :style="{ width: progressWidth + '%' }"></div>
    </div>
    <div
      v-for="step in totalSteps"
      :key="step"
      :class="getStepClass(step)"
      class="step-wrapper"
      :style="{ left: getStepPosition(step) + '%' }">
      <div class="step-circle">
        <div v-if="step < currentStep" class="step-check">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
            <path d="M20 6L9 17L4 12" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <span v-else class="step-number">{{ step }}</span>
      </div>
      <div class="step-label">
        <span class="step-title">{{ getStepTitle(step) }}</span>
        <span class="step-subtitle">{{ getStepSubtitle(step) }}</span>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ProgressBar',
  props: {
    currentStep: {
      type: Number,
      required: true
    },
    totalSteps: {
      type: Number,
      default: 2
    }
  },
  computed: {
    progressWidth() {
      return ((this.currentStep - 1) / (this.totalSteps - 1)) * 100;
    }
  },
  methods: {
    getStepClass(step) {
      if (step < this.currentStep) {
        return 'completed';
      } else if (step === this.currentStep) {
        return 'active';
      } else {
        return 'upcoming';
      }
    },
    getStepPosition(step) {
      return ((step - 1) / (this.totalSteps - 1)) * 100;
    },
    getStepTitle(step) {
      const titles = {
        1: 'Configuration IA',
        2: 'Finalisation'
      };
      return titles[step] || `Étape ${step}`;
    },
    getStepSubtitle(step) {
      const subtitles = {
        1: 'Modèle & API',
        2: 'Prompt & Chat'
      };
      return subtitles[step] || '';
    }
  }
}
</script>

<style scoped>
.progress-container {
  position: relative;
  margin: 0;
  padding: 40px 20px 60px 20px;
  height: 120px;
  width: 100%;
  max-width: 900px;
  margin: 0 auto;
  box-sizing: border-box;
}

.progress-track {
  position: absolute;
  top: 50%;
  left: 10%;
  right: 10%;
  height: 6px;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 10px;
  transform: translateY(-50%);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #10b981, #059669);
  border-radius: 10px;
  transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.progress-fill::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  animation: shimmer 2s infinite;
}

@keyframes shimmer {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

.step-wrapper {
  position: absolute;
  top: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  z-index: 10;
}

.step-circle {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 18px;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  backdrop-filter: blur(20px);
  border: 3px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.step-wrapper.upcoming .step-circle {
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.6);
  border-color: rgba(255, 255, 255, 0.2);
}

.step-wrapper.active .step-circle {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-color: rgba(255, 255, 255, 0.4);
  transform: scale(1.1);
  box-shadow: 0 12px 40px rgba(102, 126, 234, 0.4);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% {
    box-shadow: 0 12px 40px rgba(102, 126, 234, 0.4);
  }
  50% {
    box-shadow: 0 12px 40px rgba(102, 126, 234, 0.6);
  }
}

.step-wrapper.completed .step-circle {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  border-color: rgba(255, 255, 255, 0.4);
  box-shadow: 0 8px 32px rgba(16, 185, 129, 0.3);
}

.step-check {
  display: flex;
  align-items: center;
  justify-content: center;
}

.step-number {
  font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif;
  letter-spacing: -0.02em;
}

.step-label {
  margin-top: 16px;
  text-align: center;
  transition: all 0.3s ease;
}

.step-title {
  display: block;
  font-weight: 600;
  font-size: 14px;
  color: white;
  margin-bottom: 4px;
  letter-spacing: -0.01em;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.step-subtitle {
  display: block;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.8);
  font-weight: 400;
  text-shadow: 0 1px 4px rgba(0, 0, 0, 0.2);
}

.step-wrapper.upcoming .step-title {
  color: rgba(255, 255, 255, 0.6);
}

.step-wrapper.upcoming .step-subtitle {
  color: rgba(255, 255, 255, 0.4);
}

.step-wrapper.active .step-title {
  color: white;
  font-weight: 700;
  transform: scale(1.05);
}

.step-wrapper.active .step-subtitle {
  color: rgba(255, 255, 255, 0.9);
}

.step-wrapper.completed .step-title,
.step-wrapper.completed .step-subtitle {
  color: rgba(255, 255, 255, 0.9);
}

@media (max-width: 768px) {
  .progress-container {
    padding: 30px 15px 50px 15px;
    height: 100px;
  }

  .progress-track {
    left: 15%;
    right: 15%;
  }

  .step-circle {
    width: 44px;
    height: 44px;
    font-size: 16px;
  }

  .step-wrapper.active .step-circle {
    transform: scale(1.05);
  }

  .step-title {
    font-size: 12px;
  }

  .step-subtitle {
    font-size: 10px;
  }

  .step-label {
    margin-top: 12px;
  }
}

@media (max-width: 480px) {
  .progress-container {
    padding: 25px 10px 45px 10px;
    height: 80px;
  }

  .progress-track {
    left: 20%;
    right: 20%;
  }

  .step-title {
    font-size: 11px;
  }

  .step-subtitle {
    display: none;
  }

  .step-circle {
    width: 36px;
    height: 36px;
    font-size: 14px;
  }
}
</style>