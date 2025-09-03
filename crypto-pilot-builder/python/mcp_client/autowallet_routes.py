#!/usr/bin/env python3
"""
Routes API pour l'autowallet
"""

import logging
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import sys
import os

# Ajouter le répertoire parent au path Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services import (
    autowallet_service, 
    alert_service, 
    news_service, 
    ai_analyzer
)

logger = logging.getLogger(__name__)

def create_autowallet_routes(app):
    """Crée les routes pour l'autowallet"""
    
    @app.route('/api/autowallet/config', methods=['POST'])
    @jwt_required()
    def create_autowallet():
        """Crée une nouvelle configuration d'autowallet"""
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            
            if not data:
                return jsonify({"error": "Données manquantes"}), 400
            
            # Validation des données
            required_fields = ['is_active', 'analysis_interval', 'max_investment_per_trade']
            for field in required_fields:
                if field not in data:
                    return jsonify({"error": f"Champ requis manquant: {field}"}), 400
            
            # Créer l'autowallet
            autowallet_id = autowallet_service.create_autowallet(user_id, data)
            
            return jsonify({
                "success": True,
                "autowallet_id": autowallet_id,
                "message": "Autowallet créé avec succès"
            }), 201
            
        except Exception as e:
            logger.error(f"Erreur lors de la création de l'autowallet: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/autowallet/config', methods=['GET'])
    @jwt_required()
    def get_autowallet_config():
        """Récupère la configuration de l'autowallet d'un utilisateur"""
        try:
            user_id = get_jwt_identity()
            status = autowallet_service.get_autowallet_status(user_id)
            
            if "error" in status:
                return jsonify(status), 404
            
            return jsonify(status), 200
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de la config: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/autowallet/config', methods=['PUT'])
    @jwt_required()
    def update_autowallet_config():
        """Met à jour la configuration de l'autowallet"""
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            
            if not data:
                return jsonify({"error": "Données manquantes"}), 400
            
            # Mettre à jour la configuration
            success = autowallet_service.update_autowallet_config(user_id, data)
            
            if not success:
                return jsonify({"error": "Autowallet non trouvé"}), 404
            
            return jsonify({
                "success": True,
                "message": "Configuration mise à jour avec succès"
            }), 200
            
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/autowallet/start', methods=['POST'])
    @jwt_required()
    def start_autowallet():
        """Démarre le monitoring automatique"""
        try:
            user_id = get_jwt_identity()
            success = autowallet_service.start_monitoring(user_id)
            
            if not success:
                return jsonify({"error": "Impossible de démarrer le monitoring"}), 400
            
            return jsonify({
                "success": True,
                "message": "Monitoring démarré avec succès"
            }), 200
            
        except Exception as e:
            logger.error(f"Erreur lors du démarrage: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/autowallet/stop', methods=['POST'])
    @jwt_required()
    def stop_autowallet():
        """Arrête le monitoring automatique"""
        try:
            user_id = get_jwt_identity()
            success = autowallet_service.stop_monitoring(user_id)
            
            if not success:
                return jsonify({"error": "Impossible d'arrêter le monitoring"}), 400
            
            return jsonify({
                "success": True,
                "message": "Monitoring arrêté avec succès"
            }), 200
            
        except Exception as e:
            logger.error(f"Erreur lors de l'arrêt: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/autowallet/trades', methods=['GET'])
    @jwt_required()
    def get_trade_history():
        """Récupère l'historique des trades"""
        try:
            user_id = get_jwt_identity()
            limit = request.args.get('limit', 50, type=int)
            
            trades = autowallet_service.get_trade_history(user_id, limit)
            
            return jsonify({
                "success": True,
                "trades": trades,
                "count": len(trades)
            }), 200
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des trades: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/autowallet/news', methods=['GET'])
    @jwt_required()
    def get_crypto_news():
        """Récupère les dernières news crypto"""
        try:
            hours = request.args.get('hours', 24, type=int)
            news_items = news_service.get_recent_news(hours)
            
            # Convertir en format JSON
            news_data = []
            for news in news_items:
                news_data.append({
                    "id": news.id,
                    "title": news.title,
                    "content": news.content,
                    "source": news.source,
                    "published_at": news.published_at.isoformat(),
                    "url": news.url,
                    "sentiment_score": news.sentiment_score,
                    "relevance_score": news.relevance_score,
                    "crypto_mentions": news.crypto_mentions,
                    "impact_level": news.impact_level
                })
            
            return jsonify({
                "success": True,
                "news": news_data,
                "count": len(news_data)
            }), 200
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des news: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/autowallet/alerts', methods=['GET'])
    @jwt_required()
    def get_user_alerts():
        """Récupère les alertes d'un utilisateur"""
        try:
            user_id = get_jwt_identity()
            limit = request.args.get('limit', 20, type=int)
            
            # Récupérer les alertes depuis le service
            alerts = autowallet_service.get_user_alerts(user_id, limit)
            
            return jsonify({
                "success": True,
                "alerts": alerts,
                "count": len(alerts)
            }), 200
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des alertes: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route('/api/autowallet/analyze', methods=['POST'])
    @jwt_required()
    def analyze_news_manual():
        """Analyse manuelle des news pour générer des alertes"""
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            
            if not data or 'news_ids' not in data:
                return jsonify({"error": "IDs des news requis"}), 400
            
            # Récupérer les news spécifiées
            all_news = news_service.get_recent_news(hours=168)  # 1 semaine
            selected_news = [
                news for news in all_news 
                if news.id in data['news_ids']
            ]
            
            if not selected_news:
                return jsonify({"error": "Aucune news trouvée"}), 404
            
            # Obtenir le contexte de marché
            market_context = ai_analyzer.get_market_context()
            
            # Analyser les news
            alerts = ai_analyzer.analyze_news_for_investment(selected_news, market_context)
            
            # Convertir en format JSON
            alerts_data = []
            for alert in alerts:
                alerts_data.append({
                    "id": alert.id,
                    "news_id": alert.news_id,
                    "crypto_symbol": alert.crypto_symbol,
                    "alert_type": alert.alert_type,
                    "confidence_score": alert.confidence_score,
                    "reasoning": alert.reasoning,
                    "created_at": alert.created_at.isoformat(),
                    "priority": alert.priority
                })
            
            return jsonify({
                "success": True,
                "alerts": alerts_data,
                "count": len(alerts_data)
            }), 200
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse manuelle: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/autowallet/alerts/channels', methods=['POST'])
    @jwt_required()
    def add_alert_channel():
        """Ajoute un canal d'alerte"""
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            
            if not data or 'channel_type' not in data or 'config' not in data:
                return jsonify({"error": "Type de canal et configuration requis"}), 400
            
            channel_id = alert_service.add_alert_channel(
                user_id, 
                data['channel_type'], 
                data['config']
            )
            
            return jsonify({
                "success": True,
                "channel_id": channel_id,
                "message": "Canal d'alerte ajouté avec succès"
            }), 201
            
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout du canal: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/autowallet/alerts/channels', methods=['GET'])
    @jwt_required()
    def get_alert_channels():
        """Récupère les canaux d'alerte d'un utilisateur"""
        try:
            user_id = get_jwt_identity()
            channels = alert_service.get_user_channels(user_id)
            
            channels_data = []
            for channel in channels:
                channels_data.append({
                    "id": channel.id,
                    "channel_type": channel.channel_type,
                    "config": channel.config,
                    "is_active": channel.is_active,
                    "created_at": channel.created_at.isoformat()
                })
            
            return jsonify({
                "success": True,
                "channels": channels_data,
                "count": len(channels_data)
            }), 200
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des canaux: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/autowallet/alerts/channels/<channel_id>', methods=['DELETE'])
    @jwt_required()
    def remove_alert_channel(channel_id):
        """Supprime un canal d'alerte"""
        try:
            user_id = get_jwt_identity()
            success = alert_service.remove_alert_channel(user_id, channel_id)
            
            if not success:
                return jsonify({"error": "Canal non trouvé"}), 404
            
            return jsonify({
                "success": True,
                "message": "Canal d'alerte supprimé avec succès"
            }), 200
            
        except Exception as e:
            logger.error(f"Erreur lors de la suppression: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/autowallet/alerts/channels/<channel_id>', methods=['PUT'])
    @jwt_required()
    def update_alert_channel(channel_id):
        """Met à jour la configuration d'un canal d'alerte"""
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            
            if not data:
                return jsonify({"error": "Données manquantes"}), 400
            
            success = alert_service.update_channel_config(user_id, channel_id, data)
            
            if not success:
                return jsonify({"error": "Canal non trouvé"}), 404
            
            return jsonify({
                "success": True,
                "message": "Configuration mise à jour avec succès"
            }), 200
            
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/autowallet/test-alert', methods=['POST'])
    @jwt_required()
    def test_alert():
        """Envoie une alerte de test"""
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            
            if not data or 'channel_type' not in data:
                return jsonify({"error": "Type de canal requis"}), 400
            
            # Créer une alerte de test
            from services import InvestmentAlert
            test_alert = InvestmentAlert(
                id="test",
                news_id="test",
                crypto_symbol="BTC",
                alert_type="buy",
                confidence_score=0.85,
                reasoning="Ceci est un test de l'alerte d'investissement",
                created_at=datetime.now(),
                priority="high"
            )
            
            # Envoyer l'alerte de test
            success = alert_service.send_investment_alert(test_alert, user_id)
            
            if success:
                return jsonify({
                    "success": True,
                    "message": "Alerte de test envoyée avec succès"
                }), 200
            else:
                return jsonify({
                    "error": "Échec de l'envoi de l'alerte de test"
                }), 500
                
        except Exception as e:
            logger.error(f"Erreur lors du test d'alerte: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/autowallet/deactivate', methods=['POST'])
    @jwt_required()
    def deactivate_autowallet():
        """Désactive l'autowallet d'un utilisateur"""
        try:
            user_id = get_jwt_identity()
            success = autowallet_service.deactivate_autowallet(user_id)
            
            if not success:
                return jsonify({"error": "Autowallet non trouvé"}), 404
            
            return jsonify({
                "success": True,
                "message": "Autowallet désactivé avec succès"
            }), 200
            
        except Exception as e:
            logger.error(f"Erreur lors de la désactivation: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/autowallet/delete', methods=['DELETE'])
    @jwt_required()
    def delete_autowallet():
        """Supprime complètement l'autowallet d'un utilisateur"""
        try:
            user_id = get_jwt_identity()
            success = autowallet_service.delete_autowallet(user_id)
            
            if not success:
                return jsonify({"error": "Autowallet non trouvé"}), 404
            
            return jsonify({
                "success": True,
                "message": "Autowallet supprimé avec succès"
            }), 200
            
        except Exception as e:
            logger.error(f"Erreur lors de la suppression: {e}")
            return jsonify({"error": str(e)}), 500
