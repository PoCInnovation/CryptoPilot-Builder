import { createRouter, createWebHashHistory } from 'vue-router'
import Accueil from '../acceuil/Accueil.vue'
import AI from '../agent_building/Ai.vue'
import Module from '../agent_building/Module.vue'
import Prompte from '../agent_building/Prompte.vue'
import ChatPage from '../acceuil/Chat_Page.vue'

const routes = [
  {
    path: '/',
    name: 'Accueil',
    component: Accueil
  },
  {
    path: '/Model',
    redirect: '/AI'
  },
  {
    path: '/AI',
    name: 'AI',
    component: AI
  },
  {
    path: '/Module',
    name: 'Module',
    component: Module
  },
  {
    path: '/Prompte',
    name: 'Prompte',
    component: Prompte
  },
  {
    path: '/chat',
    name: 'Chat',
    component: ChatPage
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

export default router