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
        "https://min-api.cryptocompare.com/data/v2/news/?lang=EN&limit=8"
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
        },
        {
          title: "Ethereum 2.0 : La mise à jour révolutionnaire",
          source: "CryptoNews",
          time: "4h",
          url: "https://cryptonews.com/news/ethereum-2-0-revolutionary-update",
        },
        {
          title: "Nouvelle réglementation DeFi en Europe",
          source: "DeFi Pulse",
          time: "6h",
          url: "https://defipulse.com/blog/new-defi-regulation-europe",
        },
      ];
    }
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
