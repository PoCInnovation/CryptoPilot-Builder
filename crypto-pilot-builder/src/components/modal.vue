<template>
  <div v-if="show" class="popup-overlay" @click.self="close">
    <div class="popup-content">
      <slot />
      <button @click="close">Fermer</button>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue'

const props = defineProps({
  show: Boolean,
})

const emit = defineEmits(['close'])

function close() {
  emit('close')
}
</script>

<style scoped>
.popup-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
}

.popup-content {
  background: black;
  padding: 20px;
  border-radius: 8px;
}
</style>
