class CryptoService {
  constructor() {
    this.baseURL = "https://api.coingecko.com/api/v3";
  }

  async getTopCryptos(limit = 10) {
    try {
      const response = await fetch(
        `${this.baseURL}/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=${limit}&page=1&sparkline=true&price_change_percentage=24h,7d`
      );
      return await response.json();
    } catch (error) {
      console.error("Erreur lors de la récupération des cryptos:", error);
      return [];
    }
  }

  async getCryptoDetails(id) {
    try {
      const response = await fetch(`${this.baseURL}/coins/${id}`);
      return await response.json();
    } catch (error) {
      console.error(
        `Erreur lors de la récupération des détails pour ${id}:`,
        error
      );
      return null;
    }
  }

  async getGlobalStats() {
    try {
      const response = await fetch(`${this.baseURL}/global`);
      const data = await response.json();
      return data.data;
    } catch (error) {
      console.error(
        "Erreur lors de la récupération des stats globales:",
        error
      );
      return null;
    }
  }

  async getTrendingCoins() {
    try {
      const response = await fetch(`${this.baseURL}/search/trending`);
      const data = await response.json();

      if (data && data.coins && Array.isArray(data.coins)) {
        return data;
      }

      // Si la structure n'est pas comme attendue, retourner le fallback
      return this.getTrendingFallback();
    } catch (error) {
      console.error(
        "Erreur lors de la récupération des coins trending:",
        error
      );
      return this.getTrendingFallback();
    }
  }

  getTrendingFallback() {
    return {
      coins: [
        {
          item: {
            id: "bitcoin",
            name: "Bitcoin",
            symbol: "BTC",
            market_cap_rank: 1,
            thumb:
              "https://assets.coingecko.com/coins/images/1/thumb/bitcoin.png",
            small:
              "https://assets.coingecko.com/coins/images/1/small/bitcoin.png",
            large:
              "https://assets.coingecko.com/coins/images/1/large/bitcoin.png",
          },
        },
        {
          item: {
            id: "ethereum",
            name: "Ethereum",
            symbol: "ETH",
            market_cap_rank: 2,
            thumb:
              "https://assets.coingecko.com/coins/images/279/thumb/ethereum.png",
            small:
              "https://assets.coingecko.com/coins/images/279/small/ethereum.png",
            large:
              "https://assets.coingecko.com/coins/images/279/large/ethereum.png",
          },
        },
        {
          item: {
            id: "binancecoin",
            name: "BNB",
            symbol: "BNB",
            market_cap_rank: 3,
            thumb:
              "https://assets.coingecko.com/coins/images/825/thumb/bnb-icon2_2x.png",
            small:
              "https://assets.coingecko.com/coins/images/825/small/bnb-icon2_2x.png",
            large:
              "https://assets.coingecko.com/coins/images/825/large/bnb-icon2_2x.png",
          },
        },
        {
          item: {
            id: "solana",
            name: "Solana",
            symbol: "SOL",
            market_cap_rank: 4,
            thumb:
              "https://assets.coingecko.com/coins/images/4128/thumb/solana.png",
            small:
              "https://assets.coingecko.com/coins/images/4128/small/solana.png",
            large:
              "https://assets.coingecko.com/coins/images/4128/large/solana.png",
          },
        },
        {
          item: {
            id: "ripple",
            name: "XRP",
            symbol: "XRP",
            market_cap_rank: 5,
            thumb:
              "https://assets.coingecko.com/coins/images/44/thumb/xrp-symbol-white-128.png",
            small:
              "https://assets.coingecko.com/coins/images/44/small/xrp-symbol-white-128.png",
            large:
              "https://assets.coingecko.com/coins/images/44/large/xrp-symbol-white-128.png",
          },
        },
        {
          item: {
            id: "cardano",
            name: "Cardano",
            symbol: "ADA",
            market_cap_rank: 6,
            thumb:
              "https://assets.coingecko.com/coins/images/975/thumb/cardano.png",
            small:
              "https://assets.coingecko.com/coins/images/975/small/cardano.png",
            large:
              "https://assets.coingecko.com/coins/images/975/large/cardano.png",
          },
        },
        {
          item: {
            id: "dogecoin",
            name: "Dogecoin",
            symbol: "DOGE",
            market_cap_rank: 7,
            thumb:
              "https://assets.coingecko.com/coins/images/5/thumb/dogecoin.png",
            small:
              "https://assets.coingecko.com/coins/images/5/small/dogecoin.png",
            large:
              "https://assets.coingecko.com/coins/images/5/large/dogecoin.png",
          },
        },
        {
          item: {
            id: "avalanche-2",
            name: "Avalanche",
            symbol: "AVAX",
            market_cap_rank: 8,
            thumb:
              "https://assets.coingecko.com/coins/images/12559/thumb/Avalanche_Circle_RedWhite_Trans.png",
            small:
              "https://assets.coingecko.com/coins/images/12559/small/Avalanche_Circle_RedWhite_Trans.png",
            large:
              "https://assets.coingecko.com/coins/images/12559/large/Avalanche_Circle_RedWhite_Trans.png",
          },
        },
        {
          item: {
            id: "polkadot",
            name: "Polkadot",
            symbol: "DOT",
            market_cap_rank: 9,
            thumb:
              "https://assets.coingecko.com/coins/images/12171/thumb/polkadot.png",
            small:
              "https://assets.coingecko.com/coins/images/12171/small/polkadot.png",
            large:
              "https://assets.coingecko.com/coins/images/12171/large/polkadot.png",
          },
        },
        {
          item: {
            id: "chainlink",
            name: "Chainlink",
            symbol: "LINK",
            market_cap_rank: 10,
            thumb:
              "https://assets.coingecko.com/coins/images/877/thumb/chainlink-new-logo.png",
            small:
              "https://assets.coingecko.com/coins/images/877/small/chainlink-new-logo.png",
            large:
              "https://assets.coingecko.com/coins/images/877/large/chainlink-new-logo.png",
          },
        },
      ],
    };
  }

  async getCryptoNews() {
    try {
      // Utilisation de l'API CryptoCompare pour récupérer de vraies actualités crypto
      const response = await fetch(
        "https://min-api.cryptocompare.com/data/v2/news/?lang=EN&limit=20"
      );
      const data = await response.json();

      if (data.Data && Array.isArray(data.Data)) {
        return data.Data.map((article) => ({
          title: article.title,
          source: article.source_info
            ? article.source_info.name
            : "CryptoCompare",
          time: this.formatTimeAgo(article.published_on),
          url: article.url,
          categories: article.categories || "General",
          lang: article.lang || "EN",
          body: article.body || "",
        }));
      }

      return [];
    } catch (error) {
      console.error(
        "Erreur lors de la récupération des actualités crypto:",
        error
      );
      // Fallback en cas d'erreur API
      return [
        {
          title: "Bitcoin atteint de nouveaux sommets historiques",
          source: "CoinTelegraph",
          time: "2h",
          url: "https://cointelegraph.com/news/bitcoin-reaches-new-all-time-high",
          categories: "Bitcoin",
          body: "Bitcoin continue sa progression avec de nouveaux records...",
        },
        {
          title: "Ethereum 2.0 : La mise à jour révolutionnaire",
          source: "CoinDesk",
          time: "4h",
          url: "https://coindesk.com/news/ethereum-2-0-revolutionary-update",
          categories: "Ethereum",
          body: "Ethereum lance sa mise à jour majeure...",
        },
        {
          title: "Nouvelle réglementation DeFi en Europe",
          source: "DeFi Pulse",
          time: "6h",
          url: "https://defipulse.com/blog/new-defi-regulation-europe",
          categories: "DeFi",
          body: "L'Europe annonce de nouvelles règles pour la DeFi...",
        },
      ];
    }
  }

  async getPersonalizedNews(cryptoName) {
    try {
      console.log("🔍 Recherche de nouvelles personnalisées pour:", cryptoName);

      // Récupérer toutes les nouvelles
      const allNews = await this.getCryptoNews();

      if (!allNews || allNews.length === 0) {
        console.log("⚠️ Aucune nouvelle disponible, utilisation du fallback");
        return this.getPersonalizedNewsFallback(cryptoName);
      }

      // Créer des mots-clés de recherche pour la crypto
      const searchKeywords = this.generateSearchKeywords(cryptoName);
      console.log("🔑 Mots-clés de recherche:", searchKeywords);

      // Filtrer les nouvelles par mots-clés
      const personalizedNews = allNews.filter((article) => {
        const searchText =
          `${article.title} ${article.body} ${article.categories}`.toLowerCase();
        return searchKeywords.some((keyword) =>
          searchText.includes(keyword.toLowerCase())
        );
      });

      console.log(
        `📰 Trouvé ${personalizedNews.length} nouvelles personnalisées sur ${allNews.length} totales`
      );

      // Si pas assez de nouvelles personnalisées, ajouter des nouvelles générales
      if (personalizedNews.length < 4) {
        const remainingSlots = 4 - personalizedNews.length;
        const generalNews = allNews
          .filter((article) => !personalizedNews.includes(article))
          .slice(0, remainingSlots);

        personalizedNews.push(...generalNews);
        console.log(`➕ Ajouté ${generalNews.length} nouvelles générales`);
      }

      // Limiter à 4 nouvelles maximum
      return personalizedNews.slice(0, 4);
    } catch (error) {
      console.error(
        "❌ Erreur lors de la récupération des nouvelles personnalisées:",
        error
      );
      return this.getPersonalizedNewsFallback(cryptoName);
    }
  }

  generateSearchKeywords(cryptoName) {
    // Mapping des noms de crypto vers des mots-clés de recherche
    const keywordMapping = {
      bitcoin: [
        "bitcoin",
        "btc",
        "bitcoin price",
        "bitcoin news",
        "crypto king",
      ],
      ethereum: [
        "ethereum",
        "eth",
        "ethereum price",
        "ethereum news",
        "defi",
        "smart contracts",
      ],
      solana: [
        "solana",
        "sol",
        "solana price",
        "solana news",
        "fast blockchain",
      ],
      cardano: [
        "cardano",
        "ada",
        "cardano price",
        "cardano news",
        "proof of stake",
      ],
      polkadot: [
        "polkadot",
        "dot",
        "polkadot price",
        "polkadot news",
        "parachain",
      ],
      avalanche: [
        "avalanche",
        "avax",
        "avalanche price",
        "avalanche news",
        "subnet",
      ],
      chainlink: [
        "chainlink",
        "link",
        "chainlink price",
        "chainlink news",
        "oracle",
      ],
      ripple: ["ripple", "xrp", "ripple price", "ripple news", "xrp ledger"],
      binance: [
        "binance",
        "bnb",
        "binance coin",
        "binance price",
        "binance news",
      ],
      dogecoin: [
        "dogecoin",
        "doge",
        "dogecoin price",
        "dogecoin news",
        "meme coin",
      ],
    };

    const normalizedName = cryptoName.toLowerCase();

    // Chercher dans le mapping
    for (const [key, keywords] of Object.entries(keywordMapping)) {
      if (normalizedName.includes(key) || key.includes(normalizedName)) {
        return keywords;
      }
    }

    // Fallback : utiliser le nom de la crypto et des mots-clés génériques
    return [
      cryptoName.toLowerCase(),
      cryptoName,
      cryptoName.toUpperCase(),
      "crypto",
      "blockchain",
      "digital currency",
    ];
  }

  getPersonalizedNewsFallback(cryptoName) {
    // Fallback avec des nouvelles simulées si l'API échoue
    const cryptoDisplayName =
      cryptoName.charAt(0).toUpperCase() + cryptoName.slice(1);

    return [
      {
        title: `${cryptoDisplayName} : Nouvelles avancées technologiques et adoption croissante`,
        source: "CryptoDaily",
        time: "1h",
        url: "#",
        categories: cryptoDisplayName,
        body: `Les dernières nouvelles sur ${cryptoDisplayName} montrent une adoption croissante...`,
      },
      {
        title: `Développements majeurs pour ${cryptoDisplayName} : Mise à jour du protocole`,
        source: "CoinDesk",
        time: "3h",
        url: "#",
        categories: cryptoDisplayName,
        body: `${cryptoDisplayName} annonce de nouveaux développements majeurs...`,
      },
      {
        title: `Analyse technique : ${cryptoDisplayName} en 2024 - Perspectives et tendances`,
        source: "The Block",
        time: "5h",
        url: "#",
        categories: cryptoDisplayName,
        body: `Analyse approfondie des perspectives pour ${cryptoDisplayName}...`,
      },
      {
        title: `Écosystème ${cryptoDisplayName} : Nouveaux partenariats et intégrations`,
        source: "CryptoNews",
        time: "8h",
        url: "#",
        categories: cryptoDisplayName,
        body: `L'écosystème ${cryptoDisplayName} continue de s'étendre...`,
      },
    ];
  }

  formatTimeAgo(timestamp) {
    const now = Math.floor(Date.now() / 1000);
    const diff = now - timestamp;

    if (diff < 3600) {
      const minutes = Math.floor(diff / 60);
      return `${minutes}min`;
    } else if (diff < 86400) {
      const hours = Math.floor(diff / 3600);
      return `${hours}h`;
    } else {
      const days = Math.floor(diff / 86400);
      return `${days}j`;
    }
  }

  formatPrice(price) {
    if (price >= 1) {
      return new Intl.NumberFormat("fr-FR", {
        style: "currency",
        currency: "USD",
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      }).format(price);
    } else {
      return new Intl.NumberFormat("fr-FR", {
        style: "currency",
        currency: "USD",
        minimumFractionDigits: 4,
        maximumFractionDigits: 6,
      }).format(price);
    }
  }

  formatPercentage(percentage) {
    return `${percentage >= 0 ? "+" : ""}${percentage.toFixed(2)}%`;
  }

  formatMarketCap(marketCap) {
    if (marketCap >= 1e12) {
      return `${(marketCap / 1e12).toFixed(2)}T $`;
    } else if (marketCap >= 1e9) {
      return `${(marketCap / 1e9).toFixed(2)}B $`;
    } else if (marketCap >= 1e6) {
      return `${(marketCap / 1e6).toFixed(2)}M $`;
    } else {
      return `${marketCap.toFixed(0)} $`;
    }
  }
}

export default new CryptoService();
