import { createRouter, createWebHistory } from 'vue-router';
import HomeView from '../views/HomeView.vue';
import CreateAgentView from '../views/CreateAgentView.vue';
import ChatView from '../views/ChatView.vue';

const routes = [
  { path: '/', name: 'Home', component: HomeView },
  { path: '/create-agent', name: 'CreateAgent', component: CreateAgentView },
  { path: '/chat', name: 'Chat', component: ChatView },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router; 