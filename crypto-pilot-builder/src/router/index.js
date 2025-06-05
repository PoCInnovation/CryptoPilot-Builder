import { createRouter, createWebHashHistory } from 'vue-router'
import Accueil from '../acceuil/Accueil.vue'
import Model from '../agent_building/model_window.vue'
import ChatPage from '../acceuil/Chat_Page.vue'

const routes = [
  {
    path: '/',
    name: 'Accueil',
    component: Accueil
  },
  {
    path: '/Model',
    name: 'Model',
    component: Model
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