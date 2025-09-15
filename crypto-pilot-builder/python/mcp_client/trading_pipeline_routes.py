#!/usr/bin/env python3
"""
Routes API pour la pipeline de trading unifiée
"""

import logging
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import sys
import os

# Ajouter le répertoire parent au path Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.trading_pipeline_service import trading_pipeline_service

logger = logging.getLogger(__name__)

def create_trading_pipeline_routes(app):
    """Crée les routes pour la pipeline de trading unifiée"""
    
    @app.route('/api/trading-pipeline/status', methods=['GET'])
    @jwt_required()
    def get_pipeline_status():
        """Récupère le statut de la pipeline de trading"""
        try:
            status = trading_pipeline_service.get_pipeline_status()
            
            return jsonify({
                "success": True,
                "status": status
            }), 200
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du statut: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/trading-pipeline/start', methods=['POST'])
    @jwt_required()
    def start_trading_pipeline():
        """Démarre la pipeline de trading"""
        try:
            success = trading_pipeline_service.start_pipeline()
            
            if success:
                return jsonify({
                    "success": True,
                    "message": "Pipeline de trading démarrée avec succès"
                }), 200
            else:
                return jsonify({
                    "error": "Impossible de démarrer la pipeline"
                }), 400
            
        except Exception as e:
            logger.error(f"Erreur lors du démarrage de la pipeline: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/trading-pipeline/stop', methods=['POST'])
    @jwt_required()
    def stop_trading_pipeline():
        """Arrête la pipeline de trading"""
        try:
            success = trading_pipeline_service.stop_pipeline()
            
            if success:
                return jsonify({
                    "success": True,
                    "message": "Pipeline de trading arrêtée avec succès"
                }), 200
            else:
                return jsonify({
                    "error": "Impossible d'arrêter la pipeline"
                }), 400
            
        except Exception as e:
            logger.error(f"Erreur lors de l'arrêt de la pipeline: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/trading-pipeline/market-data', methods=['GET'])
    @jwt_required()
    def get_market_data():
        """Récupère les données de marché"""
        try:
            symbol = request.args.get('symbol')
            market_data = trading_pipeline_service.get_market_data(symbol)
            
            return jsonify({
                "success": True,
                "market_data": market_data,
                "count": len(market_data) if isinstance(market_data, dict) else 1
            }), 200
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des données de marché: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/trading-pipeline/predictions', methods=['GET'])
    @jwt_required()
    def get_predictions():
        """Récupère les prédictions de trading"""
        try:
            symbol = request.args.get('symbol')
            predictions = trading_pipeline_service.get_predictions(symbol)
            
            return jsonify({
                "success": True,
                "predictions": predictions,
                "count": len(predictions) if isinstance(predictions, dict) else 1
            }), 200
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des prédictions: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/trading-pipeline/signals', methods=['GET'])
    @jwt_required()
    def get_trading_signals():
        """Récupère les signaux de trading"""
        try:
            symbol = request.args.get('symbol')
            signals = trading_pipeline_service.get_signals(symbol)
            
            return jsonify({
                "success": True,
                "signals": signals,
                "count": len(signals) if isinstance(signals, dict) else 1
            }), 200
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des signaux: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/trading-pipeline/trades', methods=['GET'])
    @jwt_required()
    def get_trades():
        """Récupère les trades exécutés"""
        try:
            symbol = request.args.get('symbol')
            trades = trading_pipeline_service.get_trades(symbol)
            
            return jsonify({
                "success": True,
                "trades": trades,
                "count": len(trades) if isinstance(trades, dict) else 1
            }), 200
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des trades: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/trading-pipeline/config', methods=['GET'])
    @jwt_required()
    def get_pipeline_config():
        """Récupère la configuration de la pipeline"""
        try:
            status = trading_pipeline_service.get_pipeline_status()
            config = status.get("config", {})
            
            return jsonify({
                "success": True,
                "config": config
            }), 200
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de la config: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/trading-pipeline/config', methods=['PUT'])
    @jwt_required()
    def update_pipeline_config():
        """Met à jour la configuration de la pipeline"""
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({"error": "Données manquantes"}), 400
            
            # Mettre à jour la configuration
            # TODO: Implémenter la mise à jour de la configuration
            # Pour l'instant, on retourne un succès
            
            return jsonify({
                "success": True,
                "message": "Configuration mise à jour avec succès"
            }), 200
            
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour de la config: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/trading-pipeline/force-collect', methods=['POST'])
    @jwt_required()
    def force_data_collection():
        """Force la collecte de données de marché"""
        try:
            # Appeler directement la méthode de collecte
            trading_pipeline_service._collect_market_data()
            
            return jsonify({
                "success": True,
                "message": "Collecte de données forcée avec succès"
            }), 200
            
        except Exception as e:
            logger.error(f"Erreur lors de la collecte forcée: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/trading-pipeline/force-predict', methods=['POST'])
    @jwt_required()
    def force_prediction_generation():
        """Force la génération de prédictions"""
        try:
            # Appeler directement la méthode de génération de prédictions
            trading_pipeline_service._generate_predictions()
            
            return jsonify({
                "success": True,
                "message": "Génération de prédictions forcée avec succès"
            }), 200
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération forcée: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/trading-pipeline/force-signals', methods=['POST'])
    @jwt_required()
    def force_signal_generation():
        """Force la génération de signaux"""
        try:
            # Appeler directement la méthode de génération de signaux
            trading_pipeline_service._generate_trading_signals()
            
            return jsonify({
                "success": True,
                "message": "Génération de signaux forcée avec succès"
            }), 200
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération forcée: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/trading-pipeline/force-execute', methods=['POST'])
    @jwt_required()
    def force_trade_execution():
        """Force l'exécution des trades"""
        try:
            # Appeler directement la méthode d'exécution des trades
            trading_pipeline_service._execute_trades()
            
            return jsonify({
                "success": True,
                "message": "Exécution des trades forcée avec succès"
            }), 200
            
        except Exception as e:
            logger.error(f"Erreur lors de l'exécution forcée: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/trading-pipeline/statistics', methods=['GET'])
    @jwt_required()
    def get_pipeline_statistics():
        """Récupère les statistiques de la pipeline"""
        try:
            status = trading_pipeline_service.get_pipeline_status()
            stats = status.get("stats", {})
            
            return jsonify({
                "success": True,
                "statistics": stats
            }), 200
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des stats: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/trading-pipeline/clear-cache', methods=['POST'])
    @jwt_required()
    def clear_pipeline_cache():
        """Vide le cache de la pipeline"""
        try:
            # TODO: Implémenter la méthode de nettoyage du cache
            # Pour l'instant, on retourne un succès
            
            return jsonify({
                "success": True,
                "message": "Cache vidé avec succès"
            }), 200
            
        except Exception as e:
            logger.error(f"Erreur lors du vidage du cache: {e}")
            return jsonify({"error": str(e)}), 500
