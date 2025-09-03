#!/usr/bin/env python3
"""
Configuration d'exemple pour l'autowallet
"""

import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration de base
AUTOWALLET_CONFIG = {
    'is_active': True,
    'analysis_interval': 15,  # minutes
    'max_investment_per_trade': 100.0,  # USD
    'risk_tolerance': 'medium',  # low, medium, high
    'investment_strategy': 'balanced',  # conservative, balanced, aggressive
    'crypto_whitelist': ['BTC', 'ETH', 'ADA', 'DOT', 'SOL'],
    'crypto_blacklist': [],
    'min_confidence_threshold': 0.7,
    'max_daily_trades': 10
}

# Configuration des alertes
ALERT_CONFIGS = {
    'email': {
        'channel_type': 'email',
        'config': {
            'email': 'votre@email.com'
        },
        'is_active': True
    },
    'telegram': {
        'channel_type': 'telegram',
        'config': {
            'bot_token': 'VOTRE_BOT_TOKEN',
            'chat_id': 'VOTRE_CHAT_ID'
        },
        'is_active': False
    },
    'discord': {
        'channel_type': 'discord',
        'config': {
            'webhook_url': 'VOTRE_WEBHOOK_URL',
            'channel_name': 'alertes-crypto'
        },
        'is_active': False
    }
}

# Configuration des variables d'environnement
ENV_VARS = {
    'NEWS_API_KEY': 'Votre clé API pour les news crypto',
    'SMTP_SERVER': 'smtp.gmail.com',
    'SMTP_PORT': '587',
    'SMTP_USERNAME': 'votre_email@gmail.com',
    'SMTP_PASSWORD': 'votre_mot_de_passe_app',
    'FROM_EMAIL': 'alerts@cryptopilot.com'
}

def print_config():
    """Affiche la configuration d'exemple"""
    print("🤖 Configuration d'exemple pour CryptoPilot AutoWallet")
    print("=" * 60)
    
    print("\n📋 Configuration de l'autowallet:")
    for key, value in AUTOWALLET_CONFIG.items():
        print(f"   {key}: {value}")
    
    print("\n🔔 Configuration des alertes:")
    for name, config in ALERT_CONFIGS.items():
        print(f"   {name}: {config['channel_type']} - {'Actif' if config['is_active'] else 'Inactif'}")
    
    print("\n⚙️ Variables d'environnement nécessaires:")
    for key, description in ENV_VARS.items():
        current_value = os.getenv(key, 'Non définie')
        print(f"   {key}: {current_value}")
        if current_value == 'Non définie':
            print(f"      → {description}")
    
    print("\n🚀 Pour démarrer:")
    print("   1. Configurez vos variables d'environnement")
    print("   2. Démarrez le serveur: python app.py")
    print("   3. Accédez à l'interface: http://localhost:5000")
    print("   4. Naviguez vers /autowallet")

if __name__ == "__main__":
    print_config()
