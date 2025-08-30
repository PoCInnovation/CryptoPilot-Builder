#!/usr/bin/env python3
"""
Service d'alertes pour l'autowallet
Gère les notifications d'investissement et les envoie aux utilisateurs
"""

import logging
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Union
from dataclasses import dataclass, asdict
import uuid
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests

from .news_service import InvestmentAlert
from .ai_analyzer import ai_analyzer

logger = logging.getLogger(__name__)

@dataclass
class AlertChannel:
    """Configuration d'un canal d'alerte"""
    id: str
    user_id: str
    channel_type: str  # email, webhook, telegram, discord
    config: Dict
    is_active: bool = True
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class AlertTemplate:
    """Template pour les alertes"""
    id: str
    name: str
    subject: str
    body_template: str
    variables: List[str]
    is_default: bool = False

class AlertService:
    """Service de gestion des alertes d'investissement"""
    
    def __init__(self):
        self.alert_channels = {}  # user_id -> List[AlertChannel]
        self.alert_templates = {}
        self.smtp_config = self._load_smtp_config()
        self._init_default_templates()
        
    def _load_smtp_config(self) -> Dict:
        """Charge la configuration SMTP depuis les variables d'environnement"""
        return {
            'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
            'smtp_port': int(os.getenv('SMTP_PORT', '587')),
            'smtp_username': os.getenv('SMTP_USERNAME', ''),
            'smtp_password': os.getenv('SMTP_PASSWORD', ''),
            'from_email': os.getenv('FROM_EMAIL', 'alerts@cryptopilot.com')
        }
    
    def _init_default_templates(self):
        """Initialise les templates d'alerte par défaut"""
        default_templates = [
            AlertTemplate(
                id="buy_alert",
                name="Alerte d'achat",
                subject="🚀 Opportunité d'achat détectée pour {crypto_symbol}",
                body_template="""
🚀 ALERTE D'INVESTISSEMENT - ACHAT

Cryptomonnaie: {crypto_symbol}
Confiance: {confidence}%
Priorité: {priority}
Raisonnement: {reasoning}

📰 News source: {news_title}
⏰ Heure de l'analyse: {timestamp}

⚠️  Ceci n'est pas un conseil financier. Faites vos propres recherches.
                """,
                variables=["crypto_symbol", "confidence", "priority", "reasoning", "news_title", "timestamp"],
                is_default=True
            ),
            AlertTemplate(
                id="sell_alert",
                name="Alerte de vente",
                subject="📉 Alerte de vente pour {crypto_symbol}",
                body_template="""
📉 ALERTE D'INVESTISSEMENT - VENTE

Cryptomonnaie: {crypto_symbol}
Confiance: {confidence}%
Priorité: {priority}
Raisonnement: {reasoning}

📰 News source: {news_title}
⏰ Heure de l'analyse: {timestamp}

⚠️  Ceci n'est pas un conseil financier. Faites vos propres recherches.
                """,
                variables=["crypto_symbol", "confidence", "priority", "reasoning", "news_title", "timestamp"],
                is_default=True
            ),
            AlertTemplate(
                id="market_update",
                name="Mise à jour du marché",
                subject="📊 Mise à jour du marché crypto",
                body_template="""
📊 MISE À JOUR DU MARCHÉ

Sentiment du marché: {market_sentiment}
Indice de peur/avidité: {fear_greed_index}
Volatilité: {volatility}

Nouvelles alertes: {alert_count}
Alertes critiques: {critical_count}

⏰ Dernière mise à jour: {timestamp}
                """,
                variables=["market_sentiment", "fear_greed_index", "volatility", "alert_count", "critical_count", "timestamp"],
                is_default=True
            )
        ]
        
        for template in default_templates:
            self.alert_templates[template.id] = template
    
    def add_alert_channel(self, user_id: str, channel_type: str, config: Dict) -> str:
        """Ajoute un canal d'alerte pour un utilisateur"""
        channel_id = str(uuid.uuid4())
        channel = AlertChannel(
            id=channel_id,
            user_id=user_id,
            channel_type=channel_type,
            config=config
        )
        
        if user_id not in self.alert_channels:
            self.alert_channels[user_id] = []
        
        self.alert_channels[user_id].append(channel)
        logger.info(f"Canal d'alerte ajouté pour l'utilisateur {user_id}: {channel_type}")
        
        return channel_id
    
    def remove_alert_channel(self, user_id: str, channel_id: str) -> bool:
        """Supprime un canal d'alerte"""
        if user_id in self.alert_channels:
            self.alert_channels[user_id] = [
                ch for ch in self.alert_channels[user_id] 
                if ch.id != channel_id
            ]
            logger.info(f"Canal d'alerte supprimé: {channel_id}")
            return True
        return False
    
    def send_investment_alert(self, alert: InvestmentAlert, user_id: str) -> bool:
        """Envoie une alerte d'investissement à un utilisateur"""
        if user_id not in self.alert_channels:
            logger.warning(f"Aucun canal d'alerte configuré pour l'utilisateur {user_id}")
            return False
        
        success_count = 0
        total_channels = len(self.alert_channels[user_id])
        
        for channel in self.alert_channels[user_id]:
            if not channel.is_active:
                continue
                
            try:
                if channel.channel_type == "email":
                    success = self._send_email_alert(alert, channel)
                elif channel.channel_type == "webhook":
                    success = self._send_webhook_alert(alert, channel)
                elif channel.channel_type == "telegram":
                    success = self._send_telegram_alert(alert, channel)
                elif channel.channel_type == "discord":
                    success = self._send_discord_alert(alert, channel)
                else:
                    logger.warning(f"Type de canal non supporté: {channel.channel_type}")
                    continue
                
                if success:
                    success_count += 1
                    
            except Exception as e:
                logger.error(f"Erreur lors de l'envoi de l'alerte via {channel.channel_type}: {e}")
        
        success_rate = success_count / total_channels if total_channels > 0 else 0
        logger.info(f"Alerte envoyée à {user_id}: {success_count}/{total_channels} canaux réussis")
        
        return success_rate > 0
    
    def _send_email_alert(self, alert: InvestmentAlert, channel: AlertChannel) -> bool:
        """Envoie une alerte par email"""
        try:
            # Récupérer le template approprié
            template_id = f"{alert.alert_type}_alert"
            template = self.alert_templates.get(template_id, self.alert_templates["buy_alert"])
            
            # Préparer le contenu
            subject = template.subject.format(
                crypto_symbol=alert.crypto_symbol,
                confidence=int(alert.confidence_score * 100),
                priority=alert.priority,
                reasoning=alert.reasoning
            )
            
            body = template.body_template.format(
                crypto_symbol=alert.crypto_symbol,
                confidence=int(alert.confidence_score * 100),
                priority=alert.priority,
                reasoning=alert.reasoning,
                news_title="News crypto",  # À récupérer depuis la news
                timestamp=alert.created_at.strftime("%Y-%m-%d %H:%M:%S")
            )
            
            # Créer le message
            msg = MIMEMultipart()
            msg['From'] = self.smtp_config['from_email']
            msg['To'] = channel.config.get('email')
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # Envoyer l'email
            with smtplib.SMTP(self.smtp_config['smtp_server'], self.smtp_config['smtp_port']) as server:
                server.starttls()
                if self.smtp_config['smtp_username'] and self.smtp_config['smtp_password']:
                    server.login(self.smtp_config['smtp_username'], self.smtp_config['smtp_password'])
                server.send_message(msg)
            
            logger.info(f"Email d'alerte envoyé à {channel.config.get('email')}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de l'email: {e}")
            return False
    
    def _send_webhook_alert(self, alert: InvestmentAlert, channel: AlertChannel) -> bool:
        """Envoie une alerte via webhook"""
        try:
            webhook_url = channel.config.get('webhook_url')
            if not webhook_url:
                return False
            
            payload = {
                "text": f"🚨 Alerte {alert.alert_type.upper()} pour {alert.crypto_symbol}",
                "attachments": [{
                    "color": self._get_alert_color(alert.alert_type),
                    "fields": [
                        {"title": "Confiance", "value": f"{int(alert.confidence_score * 100)}%", "short": True},
                        {"title": "Priorité", "value": alert.priority, "short": True},
                        {"title": "Raisonnement", "value": alert.reasoning, "short": False}
                    ],
                    "footer": f"Analyse du {alert.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
                }]
            }
            
            response = requests.post(webhook_url, json=payload, timeout=10)
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi du webhook: {e}")
            return False
    
    def _send_telegram_alert(self, alert: InvestmentAlert, channel: AlertChannel) -> bool:
        """Envoie une alerte via Telegram"""
        try:
            bot_token = channel.config.get('bot_token')
            chat_id = channel.config.get('chat_id')
            
            if not bot_token or not chat_id:
                return False
            
            message = f"""
🚨 *ALERTE {alert.alert_type.upper()}*
Cryptomonnaie: `{alert.crypto_symbol}`
Confiance: {int(alert.confidence_score * 100)}%
Priorité: {alert.priority}

📝 *Raisonnement:*
{alert.reasoning}

⏰ {alert.created_at.strftime('%Y-%m-%d %H:%M:%S')}
            """
            
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "Markdown"
            }
            
            response = requests.post(url, json=payload, timeout=10)
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de l'alerte Telegram: {e}")
            return False
    
    def _send_discord_alert(self, alert: InvestmentAlert, channel: AlertChannel) -> bool:
        """Envoie une alerte via Discord"""
        try:
            webhook_url = channel.config.get('webhook_url')
            if not webhook_url:
                return False
            
            embed = {
                "title": f"🚨 Alerte {alert.alert_type.upper()} - {alert.crypto_symbol}",
                "color": self._get_alert_color(alert.alert_type),
                "fields": [
                    {"name": "Confiance", "value": f"{int(alert.confidence_score * 100)}%", "inline": True},
                    {"name": "Priorité", "value": alert.priority, "inline": True},
                    {"name": "Raisonnement", "value": alert.reasoning, "inline": False}
                ],
                "timestamp": alert.created_at.isoformat(),
                "footer": {"text": "CryptoPilot Autowallet"}
            }
            
            payload = {"embeds": [embed]}
            response = requests.post(webhook_url, json=payload, timeout=10)
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de l'alerte Discord: {e}")
            return False
    
    def _get_alert_color(self, alert_type: str) -> int:
        """Retourne la couleur appropriée pour le type d'alerte"""
        colors = {
            "buy": 0x00FF00,      # Vert
            "sell": 0xFF0000,     # Rouge
            "hold": 0xFFFF00       # Jaune
        }
        return colors.get(alert_type, 0x808080)  # Gris par défaut
    
    def send_market_update(self, user_id: str, market_data: Dict) -> bool:
        """Envoie une mise à jour du marché"""
        if user_id not in self.alert_channels:
            return False
        
        template = self.alert_templates.get("market_update")
        if not template:
            return False
        
        # Préparer le contenu
        subject = template.subject
        body = template.body_template.format(
            market_sentiment=market_data.get('sentiment', 'neutral'),
            fear_greed_index=market_data.get('fear_greed_index', 50),
            volatility=market_data.get('volatility', 'modérée'),
            alert_count=market_data.get('alert_count', 0),
            critical_count=market_data.get('critical_count', 0),
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        
        # Envoyer à tous les canaux actifs
        success = False
        for channel in self.alert_channels[user_id]:
            if channel.is_active and channel.channel_type == "email":
                try:
                    msg = MIMEMultipart()
                    msg['From'] = self.smtp_config['from_email']
                    msg['To'] = channel.config.get('email')
                    msg['Subject'] = subject
                    msg.attach(MIMEText(body, 'plain', 'utf-8'))
                    
                    with smtplib.SMTP(self.smtp_config['smtp_server'], self.smtp_config['smtp_port']) as server:
                        server.starttls()
                        if self.smtp_config['smtp_username'] and self.smtp_config['smtp_password']:
                            server.login(self.smtp_config['smtp_username'], self.smtp_config['smtp_password'])
                        server.send_message(msg)
                    
                    success = True
                    
                except Exception as e:
                    logger.error(f"Erreur lors de l'envoi de la mise à jour du marché: {e}")
        
        return success
    
    def get_user_channels(self, user_id: str) -> List[AlertChannel]:
        """Récupère les canaux d'alerte d'un utilisateur"""
        return self.alert_channels.get(user_id, [])
    
    def update_channel_config(self, user_id: str, channel_id: str, new_config: Dict) -> bool:
        """Met à jour la configuration d'un canal d'alerte"""
        if user_id in self.alert_channels:
            for channel in self.alert_channels[user_id]:
                if channel.id == channel_id:
                    channel.config.update(new_config)
                    logger.info(f"Configuration mise à jour pour le canal {channel_id}")
                    return True
        return False

# Instance singleton
alert_service = AlertService()
