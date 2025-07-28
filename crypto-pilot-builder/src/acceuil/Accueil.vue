<template>
  <div class="app-container">
    <!-- Sidebar -->
    <aside class="sidebar">
      <header class="sidebar-header">
        <h2 class="sidebar-title">CryptoPilot Builder</h2>
      </header>

      <!-- Contrôles utilisateur -->
      <nav class="chat-navigation">
        <section class="chat-controls-section">
          <button
            v-if="isAuthenticated"
            class="new-chat-button"
            @click="createNewChat"
          >
            + Nouveau Chat
          </button>
          <button v-else class="login-button" @click="showAuthModal = true">
            <span class="login-icon">👤</span> Se connecter
          </button>
        </section>

        <!-- Liste des chats -->
        <section class="chat-list-section">
          <article
            v-for="chat in chats"
            :key="chat.id"
            class="chat-item-container"
          >
            <form
              v-if="editingChatId === chat.id"
              class="chat-edit-form"
              @submit.prevent="saveEditingChat"
            >
              <input
                v-model="tempChatName"
                @keydown="handleEditKeydown"
                @blur="saveEditingChat"
                ref="chatEditInput"
                class="chat-name-input"
                maxlength="50"
                type="text"
              />
            </form>

            <button
              v-else
              :class="[
                'chat-item-button',
                { 'chat-item-button--active': chat.id === activeChat },
              ]"
              @click="selectChat(chat.id)"
              @dblclick="startEditingChat(chat.id)"
              @contextmenu="showChatContextMenu($event, chat.id)"
              :title="'Double-cliquez pour renommer | Clic droit pour plus d\'options'"
            >
              {{ chat.name }}
            </button>

            <button
              class="chat-delete-button"
              @click="deleteChat(chat.id)"
              :aria-label="`Supprimer le chat ${chat.name}`"
            >
              ×
            </button>
          </article>
        </section>
      </nav>
    </aside>

    <!-- Contenu principal -->
    <main class="main-content">
      <!-- En-tête utilisateur -->
      <header class="main-header">
        <div class="user-section">
          <div v-if="isAuthenticated" class="user-info">
            <span class="user-welcome"
              >Bonjour, {{ user?.username || user?.email }}</span
            >
            <button class="logout-button" @click="handleLogout">
              <span class="logout-icon">🚪</span> Déconnexion
            </button>
          </div>
        </div>
      </header>

      <!-- Dashboard -->
      <section v-if="!showChat" class="dashboard-section">
        <div class="bento-grid">
          <!-- Bitcoin Widget (Large) -->
          <article class="bento-item bento-large">
            <div class="crypto-main-widget">
              <div class="crypto-compact-header">
                <div class="crypto-title-section">
                  <img
                    v-if="bitcoinData"
                    :src="bitcoinData.image"
                    alt="Bitcoin"
                    class="crypto-compact-icon"
                  />
                  <div class="crypto-compact-info">
                    <h3 class="crypto-compact-name">
                      {{ bitcoinData?.name || "Bitcoin" }}
                    </h3>
                    <span class="crypto-compact-symbol">{{
                      bitcoinData?.symbol?.toUpperCase() || "BTC"
                    }}</span>
                  </div>
                </div>
                <div class="crypto-metrics">
                  <div class="crypto-compact-price">
                    {{ formatPrice(bitcoinData?.current_price || 0) }}
                  </div>
                  <div
                    :class="[
                      'crypto-compact-change',
                      bitcoinData?.price_change_percentage_24h >= 0
                        ? 'positive'
                        : 'negative',
                    ]"
                  >
                    {{
                      formatPercentage(
                        bitcoinData?.price_change_percentage_24h || 0
                      )
                    }}
                  </div>
                </div>
              </div>
              <div class="chart-section" v-if="bitcoinData?.sparkline_in_7d">
                <div class="chart-period-label">7 jours</div>
                <canvas
                  ref="bitcoinChart"
                  class="full-sparkline-chart"
                ></canvas>
              </div>
            </div>
          </article>

          <!-- Ethereum Widget -->
          <article class="bento-item bento-medium">
            <div class="crypto-widget">
              <div class="crypto-mini-header">
                <img
                  v-if="ethereumData"
                  :src="ethereumData.image"
                  alt="Ethereum"
                  class="crypto-mini-icon"
                />
                <span class="crypto-mini-symbol">{{
                  ethereumData?.symbol?.toUpperCase() || "ETH"
                }}</span>
              </div>
              <div class="crypto-mini-price">
                {{ formatPrice(ethereumData?.current_price || 0) }}
              </div>
              <div
                :class="[
                  'crypto-mini-change',
                  ethereumData?.price_change_percentage_24h >= 0
                    ? 'positive'
                    : 'negative',
                ]"
              >
                {{
                  formatPercentage(
                    ethereumData?.price_change_percentage_24h || 0
                  )
                }}
              </div>
            </div>
          </article>

          <!-- Market Cap Widget -->
          <article class="bento-item bento-medium">
            <div class="stats-widget">
              <div class="stats-header">
                <span class="stats-icon">🌍</span>
                <span class="stats-title">Market Cap</span>
              </div>
              <div class="stats-value">
                {{ formatMarketCap(globalStats?.total_market_cap?.usd || 0) }}
              </div>
              <div class="stats-change">
                {{
                  formatPercentage(
                    globalStats?.market_cap_change_percentage_24h_usd || 0
                  )
                }}
              </div>
            </div>
          </article>

          <!-- Top Gainer Widget -->
          <article class="bento-item bento-medium">
            <div class="gainer-widget">
              <div class="gainer-header">
                <span class="gainer-icon">📈</span>
                <span class="gainer-title">Top Gainer</span>
              </div>
              <div v-if="topGainer" class="gainer-content">
                <div class="gainer-name">
                  {{ topGainer.symbol?.toUpperCase() }}
                </div>
                <div class="gainer-change positive">
                  {{ formatPercentage(topGainer.price_change_percentage_24h) }}
                </div>
              </div>
            </div>
          </article>

          <!-- News Widget 1 -->
          <article class="bento-item bento-medium" v-if="cryptoNews[0]">
            <div
              class="news-single-widget"
              @click="openNewsLink(cryptoNews[0].url)"
              :style="{ backgroundImage: `url(${getNewsBackgroundImage(0)})` }"
            >
              <div class="news-single-overlay"></div>
              <div class="news-single-content">
                <div class="news-single-header">
                  <span class="news-single-icon">📰</span>
                  <span class="news-single-source">{{
                    cryptoNews[0].source
                  }}</span>
                </div>
                <h4 class="news-single-title">{{ cryptoNews[0].title }}</h4>
                <div class="news-single-time">{{ cryptoNews[0].time }}</div>
              </div>
            </div>
          </article>

          <!-- News Widget 2 -->
          <article class="bento-item bento-medium" v-if="cryptoNews[1]">
            <div
              class="news-single-widget"
              @click="openNewsLink(cryptoNews[1].url)"
              :style="{ backgroundImage: `url(${getNewsBackgroundImage(1)})` }"
            >
              <div class="news-single-overlay"></div>
              <div class="news-single-content">
                <div class="news-single-header">
                  <span class="news-single-icon">📰</span>
                  <span class="news-single-source">{{
                    cryptoNews[1].source
                  }}</span>
                </div>
                <h4 class="news-single-title">{{ cryptoNews[1].title }}</h4>
                <div class="news-single-time">{{ cryptoNews[1].time }}</div>
              </div>
            </div>
          </article>

          <!-- Trending Widget -->
          <article class="bento-item bento-medium">
            <div class="trending-widget">
              <div class="trending-header">
                <span class="trending-icon">🔥</span>
                <span class="trending-title">Trending</span>
              </div>
              <div class="trending-container">
                <div
                  class="trending-list"
                  :style="{
                    transform: `translateY(${trendingScrollOffset}px)`,
                  }"
                >
                  <div
                    v-for="(coin, index) in extendedTrendingCoins"
                    :key="coin.id + '_' + index"
                    class="trending-item"
                  >
                    <img
                      :src="coin.thumb"
                      :alt="coin.name"
                      class="trending-coin-icon"
                    />
                    <span class="trending-coin-name">{{
                      coin.name || coin.symbol
                    }}</span>
                    <span class="trending-rank"
                      >#{{ coin.market_cap_rank || "?" }}</span
                    >
                  </div>
                </div>
              </div>
            </div>
          </article>

          <!-- Fear & Greed Index Widget -->
          <article class="bento-item bento-square">
            <div class="fear-greed-widget">
              <div class="fear-greed-header">
                <span class="fear-greed-title">Fear & Greed</span>
              </div>
              <div class="fear-greed-content">
                <div class="fear-greed-value">{{ fearGreedIndex }}</div>
                <div class="fear-greed-label">{{ fearGreedLabel }}</div>
              </div>
            </div>
          </article>

          <!-- News Widget 3 -->
          <article class="bento-item bento-medium" v-if="cryptoNews[2]">
            <div
              class="news-single-widget"
              @click="openNewsLink(cryptoNews[2].url)"
              :style="{ backgroundImage: `url(${getNewsBackgroundImage(2)})` }"
            >
              <div class="news-single-overlay"></div>
              <div class="news-single-content">
                <div class="news-single-header">
                  <span class="news-single-icon">📰</span>
                  <span class="news-single-source">{{
                    cryptoNews[2].source
                  }}</span>
                </div>
                <h4 class="news-single-title">{{ cryptoNews[2].title }}</h4>
                <div class="news-single-time">{{ cryptoNews[2].time }}</div>
              </div>
            </div>
          </article>

          <!-- Volume Widget -->
          <article class="bento-item bento-square">
            <div class="volume-widget">
              <div class="volume-header">
                <span class="volume-icon">💰</span>
                <span class="volume-title">24h Volume</span>
              </div>
              <div class="volume-value">
                {{ formatMarketCap(globalStats?.total_volume?.usd || 0) }}
              </div>
            </div>
          </article>

          <!-- News Widget 4 -->
          <article class="bento-item bento-medium" v-if="cryptoNews[3]">
            <div
              class="news-single-widget"
              @click="openNewsLink(cryptoNews[3].url)"
              :style="{ backgroundImage: `url(${getNewsBackgroundImage(3)})` }"
            >
              <div class="news-single-overlay"></div>
              <div class="news-single-content">
                <div class="news-single-header">
                  <span class="news-single-icon">📰</span>
                  <span class="news-single-source">{{
                    cryptoNews[3].source
                  }}</span>
                </div>
                <h4 class="news-single-title">{{ cryptoNews[3].title }}</h4>
                <div class="news-single-time">{{ cryptoNews[3].time }}</div>
              </div>
            </div>
          </article>
        </div>

        <!-- Actions -->
        <section class="action-section">
          <div v-if="isAuthenticated" class="authenticated-actions">
            <router-link to="/AI" class="agent-navigation-link">
              <button class="configure-agent-button">
                ⚙️ Configurer mon Agent
              </button>
            </router-link>
            <button
              v-if="hasValidConfig"
              class="chat-access-button"
              @click="showChat = true"
            >
              💬 Accéder au Chat
            </button>
          </div>

          <div v-else class="auth-required-section">
            <button
              class="talk-to-agent-button-disabled"
              @click="showAuthModal = true"
            >
              🔒 Configurer mon Agent
            </button>
            <p class="auth-message">
              Veuillez vous connecter pour configurer votre agent IA
              personnalisé
            </p>
          </div>
        </section>
      </section>

      <!-- Chat -->
      <section v-else class="chat-section">
        <div class="chat-header">
          <button
            class="configure-agent-button back-dashboard-btn"
            @click="showChat = false"
          >
            ← Retour au Dashboard
          </button>
          <h3 class="chat-title">Chat avec votre Agent IA</h3>
        </div>
        <div class="chat-container">
          <Chatbot />
        </div>
      </section>
    </main>

    <!-- Menu contextuel -->
    <aside
      v-if="showContextMenu"
      class="context-menu"
      :style="{ left: contextMenuX + 'px', top: contextMenuY + 'px' }"
    >
      <button @click="renameFromContextMenu" class="context-menu-item">
        ✏️ Renommer
      </button>
      <button @click="duplicateChat" class="context-menu-item">
        📋 Dupliquer
      </button>
      <hr class="context-menu-divider" />
      <button
        @click="deleteChatFromContextMenu"
        class="context-menu-item context-menu-item--danger"
      >
        🗑️ Supprimer
      </button>
    </aside>

    <!-- Modale d'authentification -->
    <AuthModal
      :show="showAuthModal"
      @close="showAuthModal = false"
      @authenticated="handleAuthenticated"
    />
  </div>
</template>

<script>
import { mapState, mapActions, mapGetters } from "vuex";
import AuthModal from "../components/AuthModal.vue";
import apiService from "../services/apiService";
import Chatbot from "../components/chatbot.vue";
import cryptoService from "../services/cryptoService";

export default {
  name: "Accueil",
  components: {
    AuthModal,
    Chatbot,
  },
  data() {
    return {
      activeChat: null,
      nextChatId: 1,
      editingChatId: null,
      tempChatName: "",
      showContextMenu: false,
      contextMenuX: 0,
      contextMenuY: 0,
      contextMenuChatId: null,
      showAuthModal: false,
      redirectAfterAuth: null,
      chats: [],
      showChat: false,
      // Données crypto
      bitcoinData: null,
      ethereumData: null,
      globalStats: null,
      topCryptos: [],
      trendingCoins: [],
      cryptoNews: [],
      fearGreedIndex: 75,
      updateInterval: null,
      chartPoints: null,
      chartBounds: null,
      // Défilement trending
      trendingCurrentIndex: 0,
      trendingScrollInterval: null,
      trendingScrollOffset: 0,
    };
  },
  computed: {
    ...mapState("auth", ["isAuthenticated", "user"]),
    ...mapGetters(["aiConfig"]),
    hasValidConfig() {
      return (
        this.aiConfig &&
        this.aiConfig.selectedModel &&
        this.aiConfig.apiKey &&
        this.aiConfig.prompt
      );
    },
    topGainer() {
      if (!this.topCryptos.length) return null;
      return this.topCryptos.reduce((prev, current) =>
        prev.price_change_percentage_24h > current.price_change_percentage_24h
          ? prev
          : current
      );
    },
    fearGreedLabel() {
      if (this.fearGreedIndex >= 75) return "Extreme Greed";
      if (this.fearGreedIndex >= 55) return "Greed";
      if (this.fearGreedIndex >= 45) return "Neutral";
      if (this.fearGreedIndex >= 25) return "Fear";
      return "Extreme Fear";
    },
    extendedTrendingCoins() {
      return [...this.trendingCoins, ...this.trendingCoins];
    },
  },
  methods: {
    ...mapActions("auth", ["logout"]),
    ...mapActions(["loadAgentConfig"]),

    // Méthodes crypto
    async loadCryptoData() {
      try {
        console.log("🔄 Chargement des données crypto...");

        // Charger les données principales avec gestion d'erreur individuelle
        const promises = [
          cryptoService.getTopCryptos(10).catch((e) => {
            console.error("❌ Erreur getTopCryptos:", e);
            return [];
          }),
          cryptoService.getGlobalStats().catch((e) => {
            console.error("❌ Erreur getGlobalStats:", e);
            return null;
          }),
          cryptoService.getTrendingCoins().catch((e) => {
            console.error("❌ Erreur getTrendingCoins:", e);
            return { coins: [] };
          }),
          cryptoService.getCryptoNews().catch((e) => {
            console.error("❌ Erreur getCryptoNews:", e);
            return [];
          }),
        ];

        const [cryptos, globalData, trending, news] = await Promise.all(
          promises
        );

        console.log("📊 Données reçues:", {
          cryptos: cryptos?.length || 0,
          globalData: !!globalData,
          trending: trending?.coins?.length || 0,
          news: news?.length || 0,
        });

        console.log("🔥 Données trending brutes:", trending);

        // Assigner les données avec fallbacks
        this.topCryptos = Array.isArray(cryptos) ? cryptos : [];
        this.bitcoinData =
          this.topCryptos.find((c) => c.id === "bitcoin") || null;
        this.ethereumData =
          this.topCryptos.find((c) => c.id === "ethereum") || null;
        this.globalStats = globalData || null;
        this.trendingCoins =
          trending?.coins
            ?.map((coin) => ({
              id: coin.item?.id || coin.id,
              name: coin.item?.name || coin.name,
              symbol: coin.item?.symbol || coin.symbol,
              thumb: coin.item?.thumb || coin.thumb,
              market_cap_rank:
                coin.item?.market_cap_rank || coin.market_cap_rank,
            }))
            .slice(0, 10) || [];
        this.cryptoNews = Array.isArray(news) ? news : [];

        console.log("🔥 Trending coins traités:", this.trendingCoins);

        // Générer un index Fear & Greed aléatoire (en attendant une vraie API)
        this.fearGreedIndex = Math.floor(Math.random() * 100);

        console.log("✅ Données crypto assignées:", {
          bitcoinPrice: this.bitcoinData?.current_price,
          ethereumPrice: this.ethereumData?.current_price,
          marketCap: this.globalStats?.total_market_cap?.usd,
          newsCount: this.cryptoNews.length,
        });

        // Dessiner le sparkline pour Bitcoin
        this.$nextTick(() => {
          if (this.bitcoinData?.sparkline_in_7d?.price) {
            this.drawSparkline();
          } else {
            console.warn("⚠️ Pas de données sparkline pour Bitcoin");
          }
        });
      } catch (error) {
        console.error(
          "❌ Erreur générale lors du chargement des données crypto:",
          error
        );

        // Fallback avec données fictives en cas d'échec total
        this.setFallbackData();
      }
    },

    setFallbackData() {
      console.log("🔄 Chargement des données de fallback...");

      this.bitcoinData = {
        id: "bitcoin",
        name: "Bitcoin",
        symbol: "btc",
        current_price: 43250.0,
        price_change_percentage_24h: 2.45,
        image: "https://assets.coingecko.com/coins/images/1/large/bitcoin.png",
        sparkline_in_7d: {
          price: Array.from(
            { length: 168 },
            (_, i) => 42000 + Math.sin(i / 10) * 2000 + Math.random() * 1000
          ),
        },
      };

      this.ethereumData = {
        id: "ethereum",
        name: "Ethereum",
        symbol: "eth",
        current_price: 2650.0,
        price_change_percentage_24h: 1.85,
        image:
          "https://assets.coingecko.com/coins/images/279/large/ethereum.png",
      };

      this.globalStats = {
        total_market_cap: { usd: 1680000000000 },
        total_volume: { usd: 45000000000 },
        market_cap_change_percentage_24h_usd: 2.1,
      };

      this.topCryptos = [this.bitcoinData, this.ethereumData];

      this.trendingCoins = [
        {
          id: "bitcoin",
          symbol: "BTC",
          name: "Bitcoin",
          thumb:
            "https://assets.coingecko.com/coins/images/1/thumb/bitcoin.png",
          market_cap_rank: 1,
        },
        {
          id: "ethereum",
          symbol: "ETH",
          name: "Ethereum",
          thumb:
            "https://assets.coingecko.com/coins/images/279/thumb/ethereum.png",
          market_cap_rank: 2,
        },
        {
          id: "binancecoin",
          symbol: "BNB",
          name: "BNB",
          thumb:
            "https://assets.coingecko.com/coins/images/825/thumb/bnb-icon2_2x.png",
          market_cap_rank: 3,
        },
        {
          id: "solana",
          symbol: "SOL",
          name: "Solana",
          thumb:
            "https://assets.coingecko.com/coins/images/4128/thumb/solana.png",
          market_cap_rank: 4,
        },
        {
          id: "ripple",
          symbol: "XRP",
          name: "XRP",
          thumb:
            "https://assets.coingecko.com/coins/images/44/thumb/xrp-symbol-white-128.png",
          market_cap_rank: 5,
        },
        {
          id: "cardano",
          symbol: "ADA",
          name: "Cardano",
          thumb:
            "https://assets.coingecko.com/coins/images/975/thumb/cardano.png",
          market_cap_rank: 6,
        },
        {
          id: "dogecoin",
          symbol: "DOGE",
          name: "Dogecoin",
          thumb:
            "https://assets.coingecko.com/coins/images/5/thumb/dogecoin.png",
          market_cap_rank: 7,
        },
        {
          id: "avalanche-2",
          symbol: "AVAX",
          name: "Avalanche",
          thumb:
            "https://assets.coingecko.com/coins/images/12559/thumb/Avalanche_Circle_RedWhite_Trans.png",
          market_cap_rank: 8,
        },
        {
          id: "polkadot",
          symbol: "DOT",
          name: "Polkadot",
          thumb:
            "https://assets.coingecko.com/coins/images/12171/thumb/polkadot.png",
          market_cap_rank: 9,
        },
        {
          id: "chainlink",
          symbol: "LINK",
          name: "Chainlink",
          thumb:
            "https://assets.coingecko.com/coins/images/877/thumb/chainlink-new-logo.png",
          market_cap_rank: 10,
        },
      ];

      this.cryptoNews = [
        {
          title: "Bitcoin franchit un nouveau seuil historique de $43,000",
          source: "CryptoDaily",
          time: "1h",
          url: "#",
        },
        {
          title: "Ethereum lance sa mise à jour majeure Cancun-Deneb",
          source: "CoinDesk",
          time: "3h",
          url: "#",
        },
        {
          title: "Les institutions adoptent massivement les cryptomonnaies",
          source: "The Block",
          time: "5h",
          url: "#",
        },
        {
          title: "Nouvelle réglementation crypto favorable en Europe",
          source: "CryptoNews",
          time: "8h",
          url: "#",
        },
      ];

      this.fearGreedIndex = 67;

      console.log("✅ Données de fallback chargées");

      // Dessiner le sparkline avec les données de fallback
      this.$nextTick(() => {
        this.drawSparkline();
      });
    },

    drawSparkline() {
      if (!this.bitcoinData?.sparkline_in_7d?.price || !this.$refs.bitcoinChart)
        return;

      const canvas = this.$refs.bitcoinChart;
      const ctx = canvas.getContext("2d");
      const prices = this.bitcoinData.sparkline_in_7d.price;

      // Définir les dimensions du canvas pour qu'il prenne toute la largeur disponible
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
      const isPositive = this.bitcoinData.price_change_percentage_24h >= 0;
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

      // Ajouter les événements de souris pour l'interactivité
      this.addChartInteractivity();
    },

    addChartInteractivity() {
      const canvas = this.$refs.bitcoinChart;
      if (!canvas || !this.chartPoints) return;

      // Supprimer les anciens événements
      canvas.removeEventListener("mousemove", this.handleChartMouseMove);
      canvas.removeEventListener("mouseleave", this.handleChartMouseLeave);
      canvas.removeEventListener("click", this.handleChartClick);

      // Ajouter les nouveaux événements
      canvas.addEventListener("mousemove", this.handleChartMouseMove);
      canvas.addEventListener("mouseleave", this.handleChartMouseLeave);
      canvas.addEventListener("click", this.handleChartClick);
    },

    handleChartMouseMove(event) {
      if (!this.chartPoints || !this.chartBounds) return;

      const canvas = this.$refs.bitcoinChart;
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
          // Zone de détection de 30px
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
      const canvas = this.$refs.bitcoinChart;
      if (canvas) canvas.style.cursor = "default";
    },

    handleChartClick(event) {
      if (!this.chartPoints || !this.chartBounds) return;

      const canvas = this.$refs.bitcoinChart;
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
      const canvas = this.$refs.bitcoinChart;
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
      const canvas = this.$refs.bitcoinChart;
      const ctx = canvas.getContext("2d");

      // Redessiner le graphique
      this.redrawChart();

      // Dessiner le point en surbrillance
      const isPositive = this.bitcoinData.price_change_percentage_24h >= 0;
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
      const canvas = this.$refs.bitcoinChart;
      const ctx = canvas.getContext("2d");

      let animationFrame = 0;
      const animate = () => {
        if (animationFrame < 20) {
          this.redrawChart();

          const isPositive = this.bitcoinData.price_change_percentage_24h >= 0;
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

    formatPrice(price) {
      return cryptoService.formatPrice(price);
    },

    formatPercentage(percentage) {
      return cryptoService.formatPercentage(percentage);
    },

    formatMarketCap(marketCap) {
      return cryptoService.formatMarketCap(marketCap);
    },

    getNewsBackgroundImage(index) {
      const images = [
        "https://images.unsplash.com/photo-1621761191319-c6fb62004040?w=400&h=300&fit=crop&crop=center",
        "https://images.unsplash.com/photo-1639762681485-074b7f938ba0?w=400&h=300&fit=crop&crop=center",
        "https://images.unsplash.com/photo-1518546305927-5a555bb7020d?w=400&h=300&fit=crop&crop=center",
        "https://images.unsplash.com/photo-1559526324-4b87b5e36e44?w=400&h=300&fit=crop&crop=center",
      ];
      return images[index % images.length];
    },

    openNewsLink(url) {
      if (url) {
        window.open(url, "_blank");
      }
    },

    // Méthodes existantes
    selectChat(chatId) {
      this.activeChat = chatId;
      console.log(`Chat sélectionné: ${chatId}`);
    },
    createNewChat() {
      const chatName = prompt(
        "Nom du nouveau chat:",
        `Chat ${this.nextChatId}`
      );
      if (chatName && chatName.trim()) {
        const newChat = {
          id: this.nextChatId,
          name: chatName.trim(),
        };
        this.chats.push(newChat);
        this.activeChat = this.nextChatId;
        this.nextChatId++;
        console.log(`Nouveau chat créé: ${newChat.name}`);
      }
    },
    startEditingChat(chatId) {
      const chat = this.chats.find((c) => c.id === chatId);
      if (chat) {
        this.editingChatId = chatId;
        this.tempChatName = chat.name;
      }
    },
    saveEditingChat() {
      if (this.tempChatName.trim()) {
        const chat = this.chats.find((c) => c.id === this.editingChatId);
        if (chat) {
          chat.name = this.tempChatName.trim();
        }
      }
      this.cancelEditingChat();
    },
    cancelEditingChat() {
      this.editingChatId = null;
      this.tempChatName = "";
    },
    showChatContextMenu(event, chatId) {
      event.preventDefault();
      this.contextMenuChatId = chatId;
      this.contextMenuX = event.clientX;
      this.contextMenuY = event.clientY;
      this.showContextMenu = true;
      document.addEventListener("click", this.hideContextMenu);
    },
    hideContextMenu() {
      this.showContextMenu = false;
      this.contextMenuChatId = null;
      document.removeEventListener("click", this.hideContextMenu);
    },
    renameFromContextMenu() {
      if (this.contextMenuChatId) {
        this.startEditingChat(this.contextMenuChatId);
        this.hideContextMenu();
      }
    },
    duplicateChat() {
      if (this.contextMenuChatId) {
        const originalChat = this.chats.find(
          (c) => c.id === this.contextMenuChatId
        );
        if (originalChat) {
          const newChat = {
            id: this.nextChatId,
            name: `${originalChat.name} (copie)`,
          };
          this.chats.push(newChat);
          this.nextChatId++;
          this.hideContextMenu();
        }
      }
    },
    deleteChatFromContextMenu() {
      if (this.contextMenuChatId) {
        this.deleteChat(this.contextMenuChatId);
        this.hideContextMenu();
      }
    },
    async loadChatsFromApi() {
      try {
        const response = await apiService.listSessions();
        const sessions = response.sessions || [];
        this.chats = sessions.map((session, idx) => ({
          id: session.session_id,
          name: session.session_name || `Chat ${idx + 1}`,
        }));
        if (this.chats.length > 0) {
          this.activeChat = this.chats[0].id;
          this.nextChatId = this.chats.length + 1;
        }
      } catch (error) {
        console.error("Erreur lors du chargement des chats:", error);
        this.chats = [{ id: 1, name: "Trading Analysis" }];
        this.activeChat = 1;
        this.nextChatId = 2;
      }
    },
    async deleteChat(chatId) {
      if (this.chats.length <= 1) {
        alert("Vous devez garder au moins un chat");
        return;
      }
      try {
        await apiService.deleteSession(chatId);
        const index = this.chats.findIndex((chat) => chat.id === chatId);
        if (index !== -1) {
          this.chats.splice(index, 1);
          if (this.activeChat === chatId && this.chats.length > 0) {
            this.activeChat = this.chats[0].id;
          }
        }
      } catch (error) {
        console.error("Erreur lors de la suppression du chat:", error);
        alert("Erreur lors de la suppression du chat.");
      }
    },
    handleEditKeydown(event) {
      if (event.key === "Enter") {
        this.saveEditingChat();
      } else if (event.key === "Escape") {
        this.cancelEditingChat();
      }
    },
    handleAuthenticated() {
      this.loadAgentConfig();
      if (this.redirectAfterAuth) {
        this.$router.push(this.redirectAfterAuth);
        this.redirectAfterAuth = null;
      }
    },
    async handleLogout() {
      await this.logout();
      this.$router.push("/");
    },
    startTrendingScroll() {
      // Démarrer le défilement automatique progressif
      this.trendingScrollInterval = setInterval(() => {
        this.smoothTrendingScroll();
      }, 50); // Défilement fluide toutes les 50ms
    },
    smoothTrendingScroll() {
      if (this.trendingCoins.length <= 3) return;

      const itemHeight = 56; // Hauteur réelle : min-height 44px + padding 10px + gap 12px / 2
      const scrollStep = 0.5; // Défilement plus lent et plus fluide

      this.trendingScrollOffset -= scrollStep;

      // Calculer quand remettre à zéro pour un défilement infini
      const totalItemsHeight = this.trendingCoins.length * itemHeight;

      if (Math.abs(this.trendingScrollOffset) >= totalItemsHeight) {
        this.trendingScrollOffset = 0;
      }
    },
    nextTrendingBatch() {
      // Méthode conservée pour compatibilité mais non utilisée
      if (this.trendingCoins.length <= 3) return;

      this.trendingCurrentIndex += 3;
      if (this.trendingCurrentIndex >= this.trendingCoins.length) {
        this.trendingCurrentIndex = 0;
      }
    },
    stopTrendingScroll() {
      if (this.trendingScrollInterval) {
        clearInterval(this.trendingScrollInterval);
        this.trendingScrollInterval = null;
      }
    },
  },
  async mounted() {
    this.$store.dispatch("auth/checkAuth");
    if (this.isAuthenticated) {
      await this.loadAgentConfig();
      await this.loadChatsFromApi();
    }

    // Charger les données crypto
    await this.loadCryptoData();

    // Mettre à jour les données crypto toutes les 30 secondes
    this.updateInterval = setInterval(() => {
      this.loadCryptoData();
    }, 30000);

    // Démarrer le défilement des trending coins
    this.startTrendingScroll();

    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get("authRequired") === "true") {
      this.showAuthModal = true;
      this.redirectAfterAuth = urlParams.get("redirect") || "/AI";
    }
  },
  beforeUnmount() {
    if (this.updateInterval) {
      clearInterval(this.updateInterval);
    }

    // Arrêter le défilement des trending coins
    this.stopTrendingScroll();

    // Nettoyer les événements du graphique
    const canvas = this.$refs.bitcoinChart;
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
.app-container {
  display: flex;
  height: 100vh;
  font-family: "Roboto", sans-serif;
  background: linear-gradient(120deg, rgba(28, 32, 51, 0), rgba(16, 21, 33, 0));
  border: none;
  transition: left 0.5s ease;
  overflow: hidden;
}
.sidebar {
  position: fixed;
  top: 10vh;
  left: 5vh;
  width: 40vh;
  height: 80vh;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-radius: 24px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  padding: 20px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
  color: #fff;
}
.sidebar-header {
  margin-bottom: 35px;
  text-align: center;
  animation: fadeIn 0.5s ease;
}
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
.sidebar-title {
  font-size: 80px;
  font-weight: 600px;
  color: #f3e8ff;
  margin: 0;
  letter-spacing: 1px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}
.chat-navigation {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.chat-controls-section {
  margin-bottom: 20px;
  display: flex;
  gap: 80px;
}
.new-chat-button {
  width: 20%;
  padding-top: 12px;
  padding-right: 18px;
  padding-bottom: 12px;
  padding-left: 10px;
  background: linear-gradient(120deg, rgba(28, 32, 51, 0), rgba(16, 21, 33, 0));
  border: none;
  color: white;
  border-radius: 10px;
  cursor: pointer;
  font-size: 15px;
  font-weight: bold;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  text-align: center;
}
.new-chat-button:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(125, 82, 204, 0.4);
}
.new-chat-button::after {
  content: "";
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    120deg,
    rgba(255, 255, 255, 0.2) 0%,
    rgba(255, 255, 255, 0.2) 50%,
    rgba(255, 255, 255, 0) 80%
  );
  transition: left 0.5s ease;
}
.new-chat-button:hover::after {
  left: 100%;
}
.login-button {
  width: 100%;
  padding: 14px 24px;
  background: rgba(28, 32, 51, 0.1);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: white;
  border-radius: 30px;
  cursor: pointer;
  font-size: 15px;
  font-weight: 700;
  transition: all 0.3s ease;
  box-shadow: 0 6px 18px rgba(118, 75, 162, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
}
.login-button:hover {
  background: rgba(28, 32, 51, 0.2);
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(118, 75, 162, 0.4);
}
.login-icon {
  font-size: 18px;
  margin-right: 8px;
}
.chat-list-section {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: 70vh;
  overflow-y: auto;
  padding-right: 8px; /* Légèrement augmenté pour laisser place à la scrollbar */

  /* Scrollbar WebKit (Chrome, Safari, Edge) */
  scrollbar-width: thin;
  scrollbar-color: rgba(118, 75, 162, 0.6) rgba(46, 27, 77, 0.3);
}
.chat-list-section::-webkit-scrollbar {
  width: 8px;
  background-color: transparent;
}
.chat-list-section::-webkit-scrollbar-track {
  background: rgba(46, 27, 77, 0.3);
  border-radius: 10px;
  margin: 5px 0;
  box-shadow: inset 0 0 3px rgba(0, 0, 0, 0.1);
}
.chat-list-section::-webkit-scrollbar-thumb {
  background: linear-gradient(120deg, rgba(28, 32, 51, 0), rgba(16, 21, 33, 0));
  border: none;
  transition: left 0.5s ease;
  border-radius: 10px;
  box-shadow: 0 2px 6px rgba(118, 75, 162, 0.3);
  transition: all 0.3s ease;
}
.chat-list-section::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(120deg, rgba(28, 32, 51, 0), rgba(16, 21, 33, 0));
  border: none;
  transition: left 0.5s ease;
  box-shadow: 0 3px 8px rgba(157, 78, 221, 0.4);
  transform: scaleX(1.2);
}
.chat-list-section::-webkit-scrollbar-thumb:active {
  background: linear-gradient(120deg, rgba(28, 32, 51, 0), rgba(16, 21, 33, 0));
  border: none;
  transition: left 0.5s ease;
}
.chat-list-section::-webkit-scrollbar-thumb {
  opacity: 0.7;
}
.chat-list-section:hover::-webkit-scrollbar-thumb {
  opacity: 1;
}
@supports (scrollbar-width: thin) {
  .chat-list-section {
    scrollbar-width: thin;
    scrollbar-color: #764ba2 rgba(46, 27, 77, 0.3);
  }
}
.chat-list-section:hover {
  box-shadow: inset 2px 0 0 rgba(118, 75, 162, 0.2);
  transition: box-shadow 0.3s ease;
}
.chat-list-section::-webkit-scrollbar-thumb {
  position: relative;
}
.chat-list-section::-webkit-scrollbar-thumb::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(
    45deg,
    rgba(255, 255, 255, 0.1) 0%,
    transparent 50%,
    rgba(255, 255, 255, 0.1) 100%
  );
  border-radius: 10px;
  opacity: 0;
  transition: opacity 0.3s ease;
}
.chat-list-section::-webkit-scrollbar-thumb:hover::before {
  opacity: 1;
}
.chat-item-container {
  display: flex;
  align-items: center;
  gap: 8px;
  position: relative;
  transition: transform 0.2s ease;
}
.chat-item-container:hover {
  transform: translateX(5px);
}
.chat-edit-form {
  flex: 1;
}
.chat-name-input {
  width: 100%;
  padding: 14px 18px;
  background-color: #f3e8ff;
  border: 2px solid #a552cc;
  color: #2c1b4d;
  border-radius: 10px;
  font-size: 15px;
  font-family: inherit;
  outline: none;
  transition: all 0.3s ease;
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.05);
}
.chat-name-input:focus {
  border-color: #764ba2;
  box-shadow: 0 0 8px rgba(118, 75, 162, 0.3);
}
.chat-item-button {
  flex: 1;
  padding: 14px 18px;
  background: linear-gradient(120deg, rgba(28, 32, 51, 0), rgba(16, 21, 33, 0));
  border: none;
  transition: left 0.5s ease;
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #f3e8ff;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 30px;
  font-weight: 500;
  text-align: left;
  position: relative;
  overflow: hidden;
}
.chat-item-button:hover {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.3);
  transform: translateX(8px);
}
.chat-item-button::after {
  content: "";
  position: absolute;
  top: 0;
  left: -50%;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    120deg,
    rgba(255, 255, 255, 0.1) 0%,
    rgba(255, 255, 255, 0.1) 50%,
    rgba(255, 255, 255, 0) 80%
  );
  transition: left 0.5s ease;
}
.chat-item-button:hover::after {
  left: 100%;
}
.chat-item-button--active {
  background: linear-gradient(120deg, rgba(28, 32, 51, 0), rgba(16, 21, 33, 0));
  border: none;
  transition: left 0.5s ease;
  font-weight: bold;
  box-shadow: 0 4px 12px rgba(118, 75, 162, 0.3);
  transform: translateX(5px);
}
.chat-delete-button {
  width: 30px;
  height: 30px;
  background-color: #e74c3c;
  border: none;
  color: white;
  border-radius: 50%;
  cursor: pointer;
  font-size: 18px;
  font-weight: bold;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
  position: relative;
}
.chat-delete-button:hover {
  background-color: #c0392b;
  transform: scale(1.1) rotate(90deg);
}
.context-menu {
  position: fixed;
  background-color: #2e1b4d;
  border: 1px solid #5a3494;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(75, 25, 140, 0.3);
  z-index: 1000;
  min-width: 180px;
  overflow: hidden;
  animation: slideDown 0.3s ease;
}
@keyframes slideDown {
  from {
    transform: translateY(-10px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}
.context-menu-item {
  width: 100%;
  padding: 12px 20px;
  border: none;
  background: none;
  text-align: left;
  cursor: pointer;
  font-size: 15px;
  display: flex;
  align-items: center;
  gap: 10px;
  transition: background-color 0.2s ease;
  color: #f3e8ff;
}
.context-menu-item:hover {
  background-color: #5a3494;
}
.context-menu-item--danger {
  color: #ff7675;
}
.context-menu-divider {
  margin: 0;
  border: none;
  border-top: 1px solid #5a3494;
}
.main-content {
  flex: 1;
  padding: 50px;
  display: flex;
  flex-direction: column;
  align-items: center;
  background: linear-gradient(135deg, #111421 0%, #111421 100%);
  overflow-y: auto;
}
.main-header {
  margin-bottom: 50px;
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
  animation: fadeInUp 0.6s ease;
}
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
.user-section {
  position: absolute;
  right: 0;
  display: flex;
  align-items: center;
  gap: 15px;
  animation: fadeInRight 0.5s ease;
}
@keyframes fadeInRight {
  from {
    opacity: 0;
    transform: translateX(20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}
.user-info {
  display: flex;
  align-items: center;
  gap: 18px;
}
.user-welcome {
  color: white;
  font-weight: bold;
  font-size: 16px;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}
.logout-button {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 20px;
  background: rgba(28, 32, 51, 0.1);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: white;
  border-radius: 25px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}
.logout-button:hover {
  background: rgba(28, 32, 51, 0.2);
  box-shadow: 0 8px 20px rgba(192, 57, 43, 0.4);
  transform: translateY(-1px);
}
.logout-icon {
  font-size: 18px;
}

.back-dashboard-btn {
  /* Hérite des styles de .configure-agent-button */
  padding: 18px 35px;
  font-size: 20px;
  font-weight: bold;
  background: linear-gradient(120deg, rgba(28, 32, 51, 0), rgba(16, 21, 33, 0));
  border: none;
  color: white;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 6px 18px rgba(118, 75, 162, 0.3);
  position: relative;
  overflow: hidden;
  z-index: 1;
  margin-bottom: 20px; /* Espace sous le bouton */
}

/* Effet hover (identique aux autres boutons) */
.back-dashboard-btn::before {
  content: "";
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    120deg,
    rgba(255, 255, 255, 0.2) 0%,
    rgba(255, 255, 255, 0.2) 50%,
    rgba(255, 255, 255, 0) 80%
  );
  transition: left 0.5s ease;
  z-index: -1;
}

.back-dashboard-btn:hover::before {
  left: 100%;
}

.back-dashboard-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(118, 75, 162, 0.4);
}

.dashboard-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 40px;
  max-width: 1200px;
  width: 100%;
  animation: fadeInUp 0.6s ease;
}

/* Bento Grid Layout - Style Apple */
.bento-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  grid-template-rows: repeat(4, 140px);
  gap: 12px;
  width: 100%;
  max-width: 1000px;
  margin: 40px auto;
  padding: 0 20px;
}

.bento-item {
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.12);
  overflow: hidden;
  transition: all 0.2s ease;
  position: relative;
  box-shadow: 0 1px 10px rgba(0, 0, 0, 0.15);
}

.bento-item:hover {
  transform: scale(1.02);
  background: rgba(255, 255, 255, 0.12);
  border-color: rgba(255, 255, 255, 0.2);
}

/* Bitcoin au centre - Style Apple */
.bento-large {
  grid-column: 3 / 5;
  grid-row: 2 / 4;
  border-radius: 28px;
}

/* Disposition autour du Bitcoin */
/* Ligne du haut */
.bento-item:nth-child(2) {
  /* Ethereum */
  grid-column: 1 / 3;
  grid-row: 1 / 2;
}

.bento-item:nth-child(3) {
  /* Market Cap */
  grid-column: 3 / 5;
  grid-row: 1 / 2;
}

.bento-item:nth-child(4) {
  /* Top Gainer */
  grid-column: 5 / 7;
  grid-row: 1 / 2;
}

/* Côtés du Bitcoin - Cases hautes qui se collent (2 cases chacune) */
.bento-item:nth-child(5) {
  /* News 1 */
  grid-column: 1 / 3;
  grid-row: 2 / 3;
}

.bento-item:nth-child(6) {
  /* News 2 */
  grid-column: 5 / 7;
  grid-row: 2 / 3;
}

.bento-item:nth-child(7) {
  /* Trending */
  grid-column: 1 / 3;
  grid-row: 3 / 4;
}

.bento-item:nth-child(8) {
  /* Fear & Greed */
  grid-column: 5 / 7;
  grid-row: 3 / 4;
}

/* Ligne du bas */
.bento-item:nth-child(9) {
  /* News 3 */
  grid-column: 1 / 2;
  grid-row: 4 / 5;
}

.bento-item:nth-child(10) {
  /* Volume */
  grid-column: 2 / 6;
  grid-row: 4 / 5;
}

.bento-item:nth-child(11) {
  /* News 4 */
  grid-column: 6 / 7;
  grid-row: 4 / 5;
}

/* Other Widgets */
.crypto-widget,
.stats-widget,
.gainer-widget,
.trending-widget,
.fear-greed-widget,
.volume-widget {
  padding: 24px;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  color: white;
}

.crypto-mini-header,
.stats-header,
.gainer-header,
.trending-header,
.volume-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.crypto-mini-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  box-shadow: 0 3px 8px rgba(0, 0, 0, 0.2);
}

.crypto-mini-symbol,
.stats-title,
.gainer-title,
.trending-title,
.volume-title,
.fear-greed-title {
  font-size: 16px;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.9);
  text-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
  letter-spacing: 0.3px;
}

.crypto-mini-price,
.stats-value,
.gainer-name,
.volume-value {
  font-size: 24px;
  font-weight: 800;
  color: #ffffff;
  margin-bottom: 10px;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  line-height: 1.2;
}

.crypto-mini-change,
.stats-change,
.gainer-change {
  font-size: 16px;
  font-weight: 700;
  text-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
}

/* Fear & Greed Widget */
.fear-greed-widget {
  justify-content: center;
  align-items: center;
  text-align: center;
}

.fear-greed-content {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 8px;
}

.fear-greed-value {
  font-size: 44px;
  font-weight: 900;
  color: #ffffff;
  text-shadow: 0 3px 12px rgba(0, 0, 0, 0.4);
  line-height: 1;
}

.fear-greed-label {
  font-size: 14px;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.8);
  text-transform: uppercase;
  letter-spacing: 1px;
  text-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
}

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

.news-single-content {
  position: relative;
  z-index: 2;
  padding: 24px;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  color: white;
}

.news-single-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.news-single-icon {
  font-size: 18px;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3));
}

.news-single-source {
  font-size: 12px;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.9);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  text-shadow: 0 2px 6px rgba(0, 0, 0, 0.8);
  background: rgba(255, 255, 255, 0.2);
  padding: 4px 8px;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.news-single-title {
  font-size: 16px;
  font-weight: 700;
  color: #ffffff;
  line-height: 1.3;
  margin: 0 0 auto 0;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.8);
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
}

.news-single-time {
  color: rgba(255, 255, 255, 0.8);
  font-weight: 600;
  font-size: 13px;
  text-shadow: 0 1px 4px rgba(0, 0, 0, 0.8);
  background: rgba(0, 0, 0, 0.3);
  padding: 4px 10px;
  border-radius: 12px;
  width: fit-content;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

/* Trending widget */
.trending-container {
  flex: 1;
  overflow: hidden;
  position: relative;
  height: 150px;
}

.trending-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  transition: transform 0.05s linear;
  will-change: transform;
}

.trending-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
  min-height: 44px;
  flex-shrink: 0;
}

.trending-item:last-child {
  border-bottom: none;
}

.trending-item:hover {
  transform: translateX(4px);
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  padding-left: 8px;
}

.trending-coin-icon {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
  transition: transform 0.3s ease;
}

.trending-item:hover .trending-coin-icon {
  transform: scale(1.1);
}

.trending-coin-name {
  font-size: 16px;
  font-weight: 700;
  color: #ffffff;
  flex: 1;
  text-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
  letter-spacing: 0.3px;
}

.trending-rank {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.7);
  font-weight: 600;
  text-shadow: 0 1px 4px rgba(0, 0, 0, 0.3);
  background: rgba(255, 255, 255, 0.1);
  padding: 4px 8px;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
}

.trending-item:hover .trending-rank {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.3);
  color: rgba(255, 255, 255, 0.9);
}

/* Styles manquants */
.crypto-compact-change.positive,
.crypto-mini-change.positive,
.stats-change.positive,
.gainer-change.positive {
  color: #22c55e !important;
}

.crypto-compact-change.negative,
.crypto-mini-change.negative,
.stats-change.negative,
.gainer-change.negative {
  color: #ef4444 !important;
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

/* Responsive Design pour disposition circulaire */
@media (max-width: 768px) {
  .bento-grid {
    width: 400px;
    height: 400px;
    max-width: 400px;
    grid-template-columns: repeat(6, 1fr);
    grid-template-rows: repeat(6, 60px);
    gap: 8px;
  }

  /* Repositionnement pour mobile */
  .bento-large {
    grid-column: 3 / 5;
    grid-row: 3 / 5;
  }

  .bento-item:nth-child(2) {
    grid-column: 4 / 6;
    grid-row: 2 / 3;
  }
  .bento-item:nth-child(3) {
    grid-column: 5 / 7;
    grid-row: 3 / 4;
  }
  .bento-item:nth-child(4) {
    grid-column: 4 / 6;
    grid-row: 5 / 6;
  }
  .bento-item:nth-child(5) {
    grid-column: 3 / 5;
    grid-row: 6 / 7;
  }
  .bento-item:nth-child(6) {
    grid-column: 2 / 4;
    grid-row: 6 / 7;
  }
  .bento-item:nth-child(7) {
    grid-column: 1 / 3;
    grid-row: 5 / 6;
  }
  .bento-item:nth-child(8) {
    grid-column: 1 / 2;
    grid-row: 3 / 4;
  }
  .bento-item:nth-child(9) {
    grid-column: 1 / 3;
    grid-row: 2 / 3;
  }
  .bento-item:nth-child(10) {
    grid-column: 2 / 3;
    grid-row: 1 / 2;
  }
  .bento-item:nth-child(11) {
    grid-column: 4 / 5;
    grid-row: 1 / 2;
  }

  .crypto-main-widget,
  .crypto-widget,
  .stats-widget,
  .gainer-widget,
  .trending-widget,
  .fear-greed-widget,
  .volume-widget {
    padding: 8px;
  }

  .crypto-compact-price,
  .stats-value,
  .gainer-name,
  .volume-value {
    font-size: 12px;
  }

  .fear-greed-value {
    font-size: 18px;
  }

  .news-single-title {
    font-size: 9px;
    -webkit-line-clamp: 2;
  }
}

@media (max-width: 480px) {
  .bento-grid {
    width: 300px;
    height: 300px;
    max-width: 300px;
    grid-template-columns: repeat(5, 1fr);
    grid-template-rows: repeat(5, 50px);
    gap: 6px;
  }

  /* Repositionnement ultra-compact */
  .bento-large {
    grid-column: 3 / 4;
    grid-row: 3 / 4;
  }

  .bento-item:nth-child(2) {
    grid-column: 4 / 5;
    grid-row: 2 / 3;
  }
  .bento-item:nth-child(3) {
    grid-column: 4 / 5;
    grid-row: 3 / 4;
  }
  .bento-item:nth-child(4) {
    grid-column: 4 / 5;
    grid-row: 4 / 5;
  }
  .bento-item:nth-child(5) {
    grid-column: 3 / 4;
    grid-row: 5 / 6;
  }
  .bento-item:nth-child(6) {
    grid-column: 2 / 3;
    grid-row: 5 / 6;
  }
  .bento-item:nth-child(7) {
    grid-column: 1 / 2;
    grid-row: 4 / 5;
  }
  .bento-item:nth-child(8) {
    grid-column: 1 / 2;
    grid-row: 3 / 4;
  }
  .bento-item:nth-child(9) {
    grid-column: 1 / 2;
    grid-row: 2 / 3;
  }
  .bento-item:nth-child(10) {
    grid-column: 2 / 3;
    grid-row: 1 / 2;
  }
  .bento-item:nth-child(11) {
    grid-column: 3 / 4;
    grid-row: 1 / 2;
  }

  .crypto-main-widget,
  .crypto-widget,
  .stats-widget,
  .gainer-widget,
  .trending-widget,
  .fear-greed-widget,
  .volume-widget {
    padding: 4px;
  }

  .crypto-compact-name,
  .crypto-mini-symbol,
  .stats-title,
  .gainer-title,
  .trending-title,
  .volume-title,
  .fear-greed-title {
    font-size: 8px;
  }

  .crypto-compact-price,
  .crypto-mini-price,
  .stats-value,
  .gainer-name,
  .volume-value {
    font-size: 10px;
  }

  .fear-greed-value {
    font-size: 14px;
  }

  .fear-greed-label {
    font-size: 6px;
  }

  .news-single-title {
    font-size: 7px;
    -webkit-line-clamp: 2;
  }

  .trending-coin-name {
    font-size: 7px;
  }

  .trending-rank {
    font-size: 6px;
  }
}

/* Colors */
.crypto-compact-change.positive,
.crypto-mini-change.positive,
.stats-change.positive,
.gainer-change.positive {
  color: #22c55e;
}

.crypto-compact-change.negative,
.crypto-mini-change.negative,
.stats-change.negative,
.gainer-change.negative {
  color: #ef4444;
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
}

/* Responsive Design Simple */
@media (max-width: 1024px) {
  .bento-grid {
    grid-template-columns: repeat(3, 1fr);
    grid-template-rows: repeat(4, 180px);
    gap: 16px;
    max-width: 900px;
  }

  .bento-large {
    grid-column: span 2;
    grid-row: span 2;
  }

  .crypto-main-widget,
  .crypto-widget,
  .stats-widget,
  .gainer-widget,
  .trending-widget,
  .fear-greed-widget,
  .volume-widget {
    padding: 20px;
  }

  .news-single-content {
    padding: 20px;
  }
}

@media (max-width: 768px) {
  .sidebar {
    display: none;
  }

  .main-content {
    padding: 20px 16px;
    margin-left: 0;
  }

  .bento-grid {
    grid-template-columns: repeat(2, 1fr);
    grid-template-rows: repeat(6, 160px);
    gap: 12px;
    max-width: 100%;
    margin: 20px auto;
    padding: 0;
  }

  .bento-large {
    grid-column: span 2;
    grid-row: span 2;
  }

  .bento-medium,
  .bento-square,
  .bento-wide {
    grid-column: span 1;
    grid-row: span 1;
  }

  .crypto-main-widget,
  .crypto-widget,
  .stats-widget,
  .gainer-widget,
  .trending-widget,
  .fear-greed-widget,
  .volume-widget {
    padding: 16px;
  }

  .news-single-content {
    padding: 16px;
  }

  .crypto-compact-price {
    font-size: 24px;
  }

  .crypto-mini-price,
  .stats-value,
  .gainer-name,
  .volume-value {
    font-size: 20px;
  }

  .fear-greed-value {
    font-size: 36px;
  }

  .chart-section {
    min-height: 80px;
  }

  .trending-container {
    height: 120px;
  }
}

@media (max-width: 480px) {
  .main-content {
    padding: 16px 12px;
  }

  .bento-grid {
    grid-template-columns: 1fr;
    grid-template-rows: repeat(11, 140px);
    gap: 10px;
    margin: 16px auto;
  }

  .bento-large,
  .bento-medium,
  .bento-square,
  .bento-wide {
    grid-column: span 1;
    grid-row: span 1;
  }

  .crypto-main-widget,
  .crypto-widget,
  .stats-widget,
  .gainer-widget,
  .trending-widget,
  .fear-greed-widget,
  .volume-widget {
    padding: 12px;
  }

  .news-single-content {
    padding: 12px;
  }

  .crypto-compact-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
    margin-bottom: 12px;
  }

  .crypto-metrics {
    align-items: flex-start;
  }

  .crypto-compact-price {
    font-size: 20px;
  }

  .crypto-mini-price,
  .stats-value,
  .gainer-name,
  .volume-value {
    font-size: 18px;
  }

  .fear-greed-value {
    font-size: 28px;
  }

  .chart-section {
    min-height: 60px;
  }

  .trending-container {
    height: 100px;
  }

  .trending-coin-name {
    font-size: 14px;
  }

  .news-single-title {
    font-size: 14px;
    -webkit-line-clamp: 2;
  }
}

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

/* Widgets compacts - Style Apple */
.crypto-widget,
.stats-widget,
.gainer-widget,
.trending-widget,
.fear-greed-widget {
  padding: 16px;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  color: white;
}

.crypto-mini-header,
.stats-header,
.gainer-header,
.trending-header,
.volume-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.crypto-mini-icon {
  width: 24px;
  height: 24px;
  border-radius: 50%;
}

.stats-icon,
.gainer-icon,
.trending-icon,
.volume-icon {
  font-size: 16px;
}

.crypto-mini-symbol,
.stats-title,
.gainer-title,
.trending-title,
.volume-title,
.fear-greed-title {
  font-size: 13px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.8);
}

.crypto-mini-price,
.stats-value,
.gainer-name,
.volume-value {
  font-size: 18px;
  font-weight: 700;
  color: #ffffff;
  margin-bottom: 8px;
  line-height: 1.2;
}

.crypto-mini-change,
.stats-change,
.gainer-change {
  font-size: 13px;
  font-weight: 600;
}

/* Fear & Greed Widget compact */
.fear-greed-widget {
  justify-content: center;
  align-items: center;
  text-align: center;
  padding: 12px;
}

.fear-greed-content {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 6px;
}

.fear-greed-value {
  font-size: 32px;
  font-weight: 800;
  color: #ffffff;
  line-height: 1;
}

.fear-greed-label {
  font-size: 11px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.7);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* News widgets compacts */
.news-single-widget {
  height: 100%;
  border-radius: 20px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
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
}

.news-single-source {
  font-size: 10px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
  text-transform: uppercase;
  background: rgba(255, 255, 255, 0.15);
  padding: 2px 6px;
  border-radius: 6px;
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
}

/* Trending widget compact */
.trending-container {
  flex: 1;
  overflow: hidden;
  position: relative;
  height: 100px;
}

.trending-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  transition: transform 0.05s linear;
}

.trending-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  min-height: 28px;
  flex-shrink: 0;
}

.trending-item:last-child {
  border-bottom: none;
}

.trending-coin-icon {
  width: 18px;
  height: 18px;
  border-radius: 50%;
}

.trending-coin-name {
  font-size: 12px;
  font-weight: 600;
  color: #ffffff;
  flex: 1;
}

.trending-rank {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.6);
  font-weight: 500;
  background: rgba(255, 255, 255, 0.1);
  padding: 2px 6px;
  border-radius: 6px;
}

/* Actions section */
.action-section {
  width: 100%;
  display: flex;
  justify-content: center;
  margin-top: 40px;
}

.authenticated-actions {
  display: flex;
  flex-direction: column;
  gap: 16px;
  align-items: center;
}

.agent-navigation-link {
  text-decoration: none;
}

.configure-agent-button,
.chat-access-button {
  padding: 16px 32px;
  font-size: 16px;
  font-weight: 600;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.2s ease;
  backdrop-filter: blur(20px);
}

.configure-agent-button:hover,
.chat-access-button:hover {
  background: rgba(255, 255, 255, 0.15);
  transform: scale(1.02);
}

.talk-to-agent-button-disabled {
  padding: 16px 32px;
  font-size: 16px;
  font-weight: 600;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.6);
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.2s ease;
  backdrop-filter: blur(20px);
}

/* Responsive Design Apple Style */
@media (max-width: 1024px) {
  .bento-grid {
    grid-template-columns: repeat(4, 1fr);
    grid-template-rows: repeat(4, 130px);
    gap: 10px;
    max-width: 800px;
  }

  /* Bitcoin toujours centré */
  .bento-large {
    grid-column: 2 / 4;
    grid-row: 2 / 4;
  }

  /* Réorganisation autour */
  .bento-item:nth-child(2) {
    grid-column: 1 / 3;
    grid-row: 1 / 2;
  }
  .bento-item:nth-child(3) {
    grid-column: 3 / 5;
    grid-row: 1 / 2;
  }
  .bento-item:nth-child(4) {
    grid-column: 1 / 2;
    grid-row: 2 / 3;
  }
  .bento-item:nth-child(5) {
    grid-column: 4 / 5;
    grid-row: 2 / 3;
  }
  .bento-item:nth-child(6) {
    grid-column: 1 / 2;
    grid-row: 3 / 4;
  }
  .bento-item:nth-child(7) {
    grid-column: 4 / 5;
    grid-row: 3 / 4;
  }
  .bento-item:nth-child(8) {
    grid-column: 1 / 2;
    grid-row: 4 / 5;
  }
  .bento-item:nth-child(9) {
    grid-column: 2 / 4;
    grid-row: 4 / 5;
  }
  .bento-item:nth-child(10) {
    grid-column: 4 / 5;
    grid-row: 4 / 5;
  }
  .bento-item:nth-child(11) {
    display: none;
  } /* Masqué sur tablette */
}

@media (max-width: 768px) {
  .sidebar {
    display: none;
  }

  .main-content {
    padding: 20px 16px;
    margin-left: 0;
  }

  .bento-grid {
    grid-template-columns: repeat(3, 1fr);
    grid-template-rows: repeat(4, 120px);
    gap: 8px;
    max-width: 100%;
    margin: 20px auto;
    padding: 0;
  }

  /* Bitcoin centré sur mobile */
  .bento-large {
    grid-column: 2 / 3;
    grid-row: 2 / 4;
    border-radius: 24px;
  }

  /* Disposition mobile */
  .bento-item:nth-child(2) {
    grid-column: 1 / 4;
    grid-row: 1 / 2;
  }
  .bento-item:nth-child(3) {
    grid-column: 1 / 2;
    grid-row: 2 / 3;
  }
  .bento-item:nth-child(4) {
    grid-column: 3 / 4;
    grid-row: 2 / 3;
  }
  .bento-item:nth-child(5) {
    grid-column: 1 / 2;
    grid-row: 3 / 4;
  }
  .bento-item:nth-child(6) {
    grid-column: 3 / 4;
    grid-row: 3 / 4;
  }
  .bento-item:nth-child(7) {
    grid-column: 1 / 4;
    grid-row: 4 / 5;
  }
  .bento-item:nth-child(8) {
    display: none;
  }
  .bento-item:nth-child(9) {
    display: none;
  }
  .bento-item:nth-child(10) {
    display: none;
  }
  .bento-item:nth-child(11) {
    display: none;
  }

  .crypto-main-widget,
  .crypto-widget,
  .stats-widget,
  .gainer-widget,
  .trending-widget,
  .fear-greed-widget,
  .volume-widget {
    padding: 12px;
  }

  .news-single-content {
    padding: 12px;
  }
}

@media (max-width: 480px) {
  .main-content {
    padding: 16px 12px;
  }

  .bento-grid {
    grid-template-columns: 1fr;
    grid-template-rows: repeat(5, 120px);
    gap: 8px;
    margin: 16px auto;
  }

  /* Mobile simple - stack vertical */
  .bento-large,
  .bento-item:nth-child(2),
  .bento-item:nth-child(3),
  .bento-item:nth-child(4),
  .bento-item:nth-child(5),
  .bento-item:nth-child(6),
  .bento-item:nth-child(7) {
    grid-column: 1 / 2;
  }

  .bento-large {
    grid-row: 1 / 2;
  }
  .bento-item:nth-child(2) {
    grid-row: 2 / 3;
  }
  .bento-item:nth-child(3) {
    grid-row: 3 / 4;
  }
  .bento-item:nth-child(4) {
    grid-row: 4 / 5;
  }
  .bento-item:nth-child(7) {
    grid-row: 5 / 6;
  }

  .crypto-compact-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
    margin-bottom: 8px;
  }

  .crypto-metrics {
    align-items: flex-start;
  }

  .chart-section {
    min-height: 60px;
  }

  .trending-container {
    height: 80px;
  }
}

/* Volume Widget - Style spécial pour centrage */
.volume-widget {
  padding: 16px !important;
  height: 100%;
  display: flex !important;
  flex-direction: column !important;
  justify-content: center !important;
  align-items: center !important;
  text-align: center;
  color: white;
}

.volume-header {
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  gap: 8px !important;
  margin-bottom: 8px !important;
}

.volume-icon {
  font-size: 16px;
}

.volume-title {
  font-size: 13px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.8);
}

.volume-value {
  font-size: 20px !important;
  font-weight: 700;
  color: #ffffff;
  line-height: 1.2;
  margin: 0 !important;
}
</style>
