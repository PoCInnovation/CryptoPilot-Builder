<template>
  <div class="agent-creator">
    <div class="stepper">
      <div :class="['step', {active: step === 1}]">AI</div>
      <div class="arrow">→</div>
      <div :class="['step', {active: step === 2}]">Module</div>
      <div class="arrow">→</div>
      <div :class="['step', {active: step === 3}]">Prompt</div>
    </div>
    <div class="step-content">
      <div v-if="step === 1">
        <label>AI model</label>
        <select v-model="model">
          <option value="claude-3.5">Claude 3.5</option>
          <option value="gpt-4o">GPT-4o</option>
          <option value="local">Local Model</option>
        </select>
        <label>API Key</label>
        <input type="password" v-model="apiKey" placeholder="Entrer votre clé API" />
        <div class="actions">
          <button @click="cancel">Cancel</button>
          <button class="next" @click="nextStep">Next</button>
        </div>
        <div class="hint"> <span class="warn">*</span> Choisir le modèle et définir la connexion avec la clé API.</div>
      </div>
      <div v-else-if="step === 2">
        <label>Modules accessibles :</label>
        <div class="modules">
          <div v-for="mod in modules" :key="mod.name" class="module-toggle">
            <span>{{ mod.label }}</span>
            <input type="checkbox" v-model="mod.enabled" />
          </div>
        </div>
        <div class="actions">
          <button @click="prevStep">Cancel</button>
          <button class="next" @click="nextStep">Next</button>
        </div>
        <div class="hint"> <span class="warn">*</span> Définir les modules accessibles à l'IA.</div>
      </div>
      <div v-else-if="step === 3">
        <label>Agent personality :</label>
        <textarea v-model="prompt" rows="5" placeholder="Décris la personnalité de ton agent..."></textarea>
        <div class="actions">
          <button @click="prevStep">Cancel</button>
          <button class="next" @click="finish">Créer l'agent</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
const step = ref(1);
const model = ref('claude-3.5');
const apiKey = ref('');
const modules = ref([
  { name: 'wallet', label: 'Wallet', enabled: true },
  { name: 'prices', label: 'Prices', enabled: false },
  { name: 'truc', label: 'Truc', enabled: false },
]);
const prompt = ref('');

function nextStep() {
  if (step.value < 3) step.value++;
}
function prevStep() {
  if (step.value > 1) step.value--;
}
function cancel() {
  step.value = 1;
}
function finish() {
  // Logique de création d'agent ici
  alert('Agent créé !');
}
</script>

<style scoped>
.agent-creator {
  padding: 2rem 3rem;
  color: #fff;
  max-width: 600px;
  margin: 0 auto;
}
.stepper {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 2rem;
}
.step {
  background: #232b4a;
  color: #b3b3b3;
  padding: 0.7rem 2rem;
  border-radius: 12px;
  font-weight: bold;
  font-size: 1.1rem;
  transition: background 0.2s, color 0.2s;
}
.step.active {
  background: #00e6a0;
  color: #232b4a;
}
.arrow {
  margin: 0 1rem;
  font-size: 1.5rem;
  color: #b3b3b3;
}
.step-content {
  background: #232b4a;
  border-radius: 18px;
  box-shadow: 0 2px 12px #0002;
  padding: 2rem;
}
label {
  font-weight: 600;
  margin-top: 1rem;
  display: block;
}
select, input[type="password"], textarea {
  width: 100%;
  margin: 0.5rem 0 1.2rem 0;
  padding: 0.7rem 1rem;
  border-radius: 8px;
  border: none;
  background: #1a223f;
  color: #fff;
  font-size: 1rem;
}
.modules {
  display: flex;
  gap: 2rem;
  margin: 1rem 0 2rem 0;
}
.module-toggle {
  display: flex;
  align-items: center;
  gap: 0.7rem;
}
.actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1rem;
}
button {
  background: #3a1c71;
  color: #fff;
  border: none;
  border-radius: 8px;
  padding: 0.7rem 1.5rem;
  font-weight: bold;
  font-size: 1rem;
  cursor: pointer;
  transition: background 0.2s;
}
button.next {
  background: #00e6a0;
  color: #232b4a;
}
button.next:hover {
  background: #00b37a;
}
.hint {
  margin-top: 1rem;
  color: #ffb347;
  font-size: 0.95rem;
}
.warn {
  color: #ff4d4f;
  font-weight: bold;
}
</style> 