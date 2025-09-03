#!/bin/bash

# Script de démarrage de la pipeline de trading unifiée
# CryptoPilot Builder - Pipeline de Trading

echo "🚀 Démarrage de la pipeline de trading unifiée CryptoPilot"
echo "=================================================="

# Vérifier que Python est installé
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 n'est pas installé. Veuillez l'installer d'abord."
    exit 1
fi

# Vérifier que les dépendances sont installées
echo "🔧 Vérification des dépendances..."
if ! python3 -c "import flask" &> /dev/null; then
    echo "⚠️ Flask n'est pas installé."
    echo "   Pour installer Flask, utilisez l'une de ces méthodes :"
    echo "   1. Créer un environnement virtuel : python3 -m venv venv && source venv/bin/activate"
    echo "   2. Installer via pipx : pipx install flask"
    echo "   3. Installer via apt : sudo apt install python3-flask"
    echo ""
    echo "   Pour l'instant, nous continuons sans Flask..."
    FLASK_AVAILABLE=false
else
    echo "✅ Flask est disponible"
    FLASK_AVAILABLE=true
fi

# Vérifier la configuration
echo "⚙️ Vérification de la configuration..."
if ! python3 -c "from config.trading_pipeline_config import PIPELINE_CONFIG; print('✅ Configuration OK')" &> /dev/null; then
    echo "❌ Erreur de configuration. Vérifiez le fichier config/trading_pipeline_config.py"
    exit 1
fi

# Vérifier le service
echo "🔍 Vérification du service..."
if ! python3 -c "from services.trading_pipeline_service import trading_pipeline_service; print('✅ Service OK')" &> /dev/null; then
    echo "❌ Erreur du service. Vérifiez le fichier services/trading_pipeline_service.py"
    exit 1
fi

# Vérifier les routes API
echo "🌐 Vérification des routes API..."
if [ "$FLASK_AVAILABLE" = true ]; then
    if ! python3 -c "from mcp_client.trading_pipeline_routes import create_trading_pipeline_routes; print('✅ Routes API OK')" &> /dev/null; then
        echo "❌ Erreur des routes API. Vérifiez le fichier mcp_client/trading_pipeline_routes.py"
        exit 1
    fi
else
    echo "⚠️ Routes API non vérifiées (Flask non disponible)"
fi

echo ""
echo "✅ Toutes les vérifications sont passées !"
echo ""
echo "📋 Configuration actuelle de la pipeline :"
python3 -c "
from config.trading_pipeline_config import PIPELINE_CONFIG
config = PIPELINE_CONFIG
print(f'   • Collecte de données: {config[\"data_collection_interval\"]}s')
print(f'   • Génération de prédictions: {config[\"prediction_interval\"]}s')
print(f'   • Génération de signaux: {config[\"signal_generation_interval\"]}s')
print(f'   • Exécution des trades: {config[\"trade_execution_interval\"]}s')
print(f'   • Trades max simultanés: {config[\"max_concurrent_trades\"]}')
print(f'   • Seuil de confiance: {config[\"min_confidence_threshold\"]*100:.0f}%')
print(f'   • Mode simulation: {\"Activé\" if config[\"trade_execution\"][\"paper_trading\"] else \"Désactivé\"}')
"

echo ""
echo "🚀 La pipeline est prête à être utilisée !"
echo ""
echo "📚 Prochaines étapes :"
echo "   1. Démarrer le serveur Flask principal (app.py)"
echo "   2. Accéder à l'interface AutoWallet dans votre navigateur"
echo "   3. Utiliser la section 'Pipeline de Trading Unifiée'"
echo "   4. Démarrer la pipeline et surveiller les performances"
echo ""
echo "🔧 Pour tester la pipeline en mode standalone :"
echo "   python3 demo_pipeline.py"
echo ""
echo "📖 Pour plus d'informations, consultez README_TRADING_PIPELINE.md"
echo ""
echo "🎉 Pipeline de trading unifiée CryptoPilot prête !"
