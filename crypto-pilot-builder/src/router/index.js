import { createRouter, createWebHashHistory } from "vue-router";
import Accueil from "../acceuil/Accueil.vue";
import AI from "../agent_building/Ai.vue";
import Module from "../agent_building/Module.vue";
import Prompte from "../agent_building/Prompte.vue";
import ChatPage from "../acceuil/Chat_Page.vue";
import UserMemory from "../components/UserMemory.vue";
import AutoWallet from "../components/AutoWallet.vue";
import PipelineTestDashboard from "../components/PipelineTestDashboard.vue";
import store from "../store";

const routes = [
  {
    path: "/",
    name: "Accueil",
    component: Accueil,
  },
  {
    path: "/Model",
    redirect: "/AI",
  },
  {
    path: "/AI",
    name: "AI",
    component: AI,
    meta: { requiresAuth: true },
  },
  {
    path: "/Module",
    name: "Module",
    component: Module,
    meta: { requiresAuth: true },
  },
  {
    path: "/Prompte",
    name: "Prompte",
    component: Prompte,
    meta: { requiresAuth: true },
  },
  {
    path: "/chat",
    name: "Chat",
    component: ChatPage,
    meta: { requiresAuth: true },
  },
  {
    path: "/memory",
    name: "UserMemory",
    component: UserMemory,
    meta: { requiresAuth: true },
  },
  {
    path: "/autowallet",
    name: "AutoWallet",
    component: AutoWallet,
    meta: { requiresAuth: true },
  },
  {
    path: "/pipeline-test",
    name: "PipelineTest",
    component: PipelineTestDashboard,
    meta: { requiresAuth: true },
  },
];

const router = createRouter({
  history: createWebHashHistory(),
  routes,
});

// Navigation guard pour l'authentification
router.beforeEach((to, from, next) => {
  // Vérifier si la route nécessite une authentification
  if (to.meta.requiresAuth) {
    // Vérifier si l'utilisateur est authentifié
    if (store.getters.isAuthenticated) {
      next(); // L'utilisateur est authentifié, continuer
    } else {
      // L'utilisateur n'est pas authentifié, rediriger vers l'accueil
      next({
        path: "/",
        query: {
          redirect: to.fullPath,
          authRequired: "true",
        },
      });
    }
  } else {
    next(); // La route ne nécessite pas d'authentification
  }
});

export default router;
