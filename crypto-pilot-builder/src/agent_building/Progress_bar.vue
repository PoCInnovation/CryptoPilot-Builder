<template>
  <div class="progress-container">
    <div class="progress-line"></div>
    <div class="progress-line-fill" :style="{ width: progressWidth + '%' }"></div>
    <div
      v-for="step in totalSteps"
      :key="step"
      :class="getStepClass(step)"
      class="step">
      <span>{{ step }}</span>
      <div class="step-label">Step {{ step }}</div>
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
      default: 3
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
        return '';
      }
    }
  }
}
</script>

<style scoped>
.progress-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 40px 0;
  position: relative;
}

.progress-line {
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  height: 4px;
  background-color: #e0e0e0;
  transform: translateY(-50%);
  z-index: 1;
}

.progress-line-fill {
  position: absolute;
  top: 50%;
  left: 0;
  height: 4px;
  background-color: #333;
  transform: translateY(-50%);
  z-index: 2;
  transition: width 0.5s ease;
}

.step {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: white;
  border: 4px solid #e0e0e0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  color: #999;
  position: relative;
  z-index: 3;
  transition: all 0.3s ease;
}

.step.active {
  border-color: green;
  background-color: green;
  color: white;
}

.step.completed {
  border-color: green;
  background-color: green;
  color: white;
}

.step-label {
  position: absolute;
  top: 50px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 14px;
  color: #666;
  white-space: nowrap;
}

.step.active .step-label,
.step.completed .step-label {
  color: #333;
  font-weight: bold;
}

@media (max-width: 768px) {
  .progress-container {
    margin: 20px 0;
  }
  .step {
    width: 30px;
    height: 30px;
    font-size: 14px;
  }
  .step-label {
    font-size: 12px;
    top: 40px;
  }
}
</style>