#!/usr/bin/env python3
"""
Système de mémoire utilisateur intelligent
Extrait et stocke automatiquement des informations importantes sur l'utilisateur
"""

import json
import re
import logging
import openai
from typing import Dict, List, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

class UserMemoryManager:
    """Gestionnaire de mémoire utilisateur intelligent"""
    
    def __init__(self, db=None):
        self.db = db
        self.UserMemory = None
        
    def set_models(self, UserMemory):
        """Configurer les modèles de base de données"""
        self.UserMemory = UserMemory
        
    def extract_important_info(self, message: str, user_id: str, openai_api_key: str = None) -> List[Dict]:
        """
        Extrait automatiquement les informations importantes d'un message utilisateur
        Utilise l'IA pour détecter et catégoriser les informations personnelles avec des types dynamiques
        """
        if not openai_api_key:
            return []
            
        try:
            client = openai.OpenAI(api_key=openai_api_key)
            
            extraction_prompt = f"""
Analyse ce message utilisateur et extrait SEULEMENT les informations personnelles importantes à retenir pour personnaliser les futures conversations.

Message: "{message}"

Tu peux créer tes propres catégories (memory_type) selon le contexte. Exemples de types possibles :
- informations_personnelles, preferences_crypto, niveau_expertise, objectifs_investissement
- style_communication, contraintes_budget, horizon_temporel, tolerance_risque
- experience_trading, projets_perso, situation_professionnelle, localisation
- ou tout autre type pertinent que tu juges utile

RÈGLES STRICTES:
1. N'extrait QUE les informations explicitement mentionnées ou fortement impliquées
2. Ignore les questions, les demandes ponctuelles, les salutations
3. Concentre-toi sur les informations durables qui aideront l'IA dans le futur
4. Crée des types de mémoire logiques et cohérents (en snake_case, en français)
5. Si aucune info importante n'est détectée, réponds avec un JSON vide: {{"extractions": []}}

Format de réponse JSON OBLIGATOIRE:
{{
  "extractions": [
    {{
      "memory_type": "type_créé_par_toi",
      "key_info": "nom_du_champ_court",
      "value_info": "description détaillée",
      "confidence_score": 0.8
    }}
  ]
}}

Exemples:
- "Je m'appelle Milo" → {{"extractions": [{{"memory_type": "identite", "key_info": "prenom", "value_info": "Milo", "confidence_score": 0.95}}]}}
- "J'aime beaucoup Ethereum" → {{"extractions": [{{"memory_type": "preferences_crypto", "key_info": "blockchain_preferee", "value_info": "Ethereum", "confidence_score": 0.9}}]}}
- "Je suis débutant en crypto" → {{"extractions": [{{"memory_type": "niveau_expertise", "key_info": "experience_crypto", "value_info": "débutant", "confidence_score": 0.85}}]}}
- "Je travaille dans la tech" → {{"extractions": [{{"memory_type": "situation_professionnelle", "key_info": "secteur_activite", "value_info": "technologie", "confidence_score": 0.9}}]}}
"""

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Tu es un expert en extraction d'informations personnelles. Tu crées des catégories intelligentes et réponds UNIQUEMENT en JSON valide."},
                    {"role": "user", "content": extraction_prompt}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Parser le JSON
            try:
                result = json.loads(result_text)
                extractions = result.get('extractions', [])
                
                # Valider et nettoyer les extractions
                valid_extractions = []
                for ext in extractions:
                    if all(key in ext for key in ['memory_type', 'key_info', 'value_info']):
                        # Nettoyer et valider les données
                        cleaned_ext = {
                            'memory_type': str(ext['memory_type']).strip().lower().replace(' ', '_')[:50],  # Format snake_case
                            'key_info': str(ext['key_info']).strip()[:200],  # Limiter la longueur
                            'value_info': str(ext['value_info']).strip(),
                            'confidence_score': float(ext.get('confidence_score', 0.8))
                        }
                        
                        # S'assurer que le score de confiance est dans la bonne fourchette
                        cleaned_ext['confidence_score'] = max(0.0, min(1.0, cleaned_ext['confidence_score']))
                        
                        # Valider que le type de mémoire n'est pas vide
                        if cleaned_ext['memory_type'] and cleaned_ext['key_info'] and cleaned_ext['value_info']:
                            valid_extractions.append(cleaned_ext)
                
                return valid_extractions
                
            except json.JSONDecodeError as e:
                logger.warning(f"Erreur de parsing JSON dans l'extraction de mémoire: {e}")
                logger.warning(f"Réponse reçue: {result_text}")
                return []
                
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction d'informations: {e}")
            return []
    
    def store_memory_info(self, user_id: str, memory_type: str, key_info: str, value_info: str, 
                         confidence_score: float = 1.0, source_message_id: str = None) -> bool:
        """Stocke une information dans la mémoire utilisateur"""
        if not self.db or not self.UserMemory:
            return False
            
        try:
            # Chercher si une info avec cette clé existe déjà
            existing_memory = self.UserMemory.query.filter_by(
                user_id=user_id, 
                key_info=key_info,
                is_active=True
            ).first()
            
            if existing_memory:
                # Mettre à jour si le nouveau score de confiance est meilleur
                if confidence_score >= existing_memory.confidence_score:
                    existing_memory.value_info = value_info
                    existing_memory.confidence_score = confidence_score
                    existing_memory.memory_type = memory_type
                    existing_memory.source_message_id = source_message_id
                    existing_memory.updated_at = datetime.utcnow()
                    self.db.session.commit()
                    return True
                else:
                    # Garder l'ancienne info mais log l'événement
                    logger.info(f"Info existante gardée pour {key_info} (score: {existing_memory.confidence_score} vs {confidence_score})")
                    return True
            else:
                # Créer nouvelle entrée
                new_memory = self.UserMemory(
                    user_id=user_id,
                    memory_type=memory_type,
                    key_info=key_info,
                    value_info=value_info,
                    confidence_score=confidence_score,
                    source_message_id=source_message_id
                )
                
                self.db.session.add(new_memory)
                self.db.session.commit()
                return True
                
        except Exception as e:
            logger.error(f"Erreur lors du stockage de mémoire: {e}")
            if self.db:
                self.db.session.rollback()
            return False
    
    def get_user_memory_summary(self, user_id: str) -> str:
        """Génère un résumé dynamique de la mémoire utilisateur pour l'intégrer dans le prompt système"""
        if not self.db or not self.UserMemory:
            return ""
            
        try:
            memories = self.UserMemory.query.filter_by(
                user_id=user_id,
                is_active=True
            ).order_by(self.UserMemory.memory_type, self.UserMemory.confidence_score.desc()).all()
            
            if not memories:
                return ""
            
            # Organiser dynamiquement par type de mémoire
            memory_by_type = {}
            
            for memory in memories:
                memory_type = memory.memory_type
                if memory_type not in memory_by_type:
                    memory_by_type[memory_type] = []
                memory_by_type[memory_type].append(memory)
            
            # Construire le résumé dynamique
            summary_parts = []
            
            for memory_type, memories_list in memory_by_type.items():
                # Créer un label lisible pour le type
                type_label = memory_type.replace('_', ' ').title()
                
                # Joindre toutes les informations de ce type
                type_info = ", ".join([f"{m.key_info}: {m.value_info}" for m in memories_list])
                summary_parts.append(f"{type_label}: {type_info}")
            
            if summary_parts:
                return "MÉMOIRE UTILISATEUR: " + ". ".join(summary_parts) + "."
            
            return ""
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération du résumé de mémoire: {e}")
            return ""
    
    def process_user_message(self, user_id: str, message: str, openai_api_key: str = None, 
                           message_id: str = None) -> int:
        """
        Traite un message utilisateur pour extraire et stocker automatiquement les informations importantes
        Retourne le nombre d'informations extraites et stockées
        """
        extractions = self.extract_important_info(message, user_id, openai_api_key)
        stored_count = 0
        
        for extraction in extractions:
            success = self.store_memory_info(
                user_id=user_id,
                memory_type=extraction['memory_type'],
                key_info=extraction['key_info'],
                value_info=extraction['value_info'],
                confidence_score=extraction['confidence_score'],
                source_message_id=message_id
            )
            
            if success:
                stored_count += 1
                logger.info(f"Info stockée pour {user_id}: {extraction['key_info']} = {extraction['value_info']}")
        
        return stored_count
    
    def get_user_memories(self, user_id: str) -> List[Dict]:
        """Récupère toutes les mémoires actives d'un utilisateur"""
        if not self.db or not self.UserMemory:
            return []
            
        try:
            memories = self.UserMemory.query.filter_by(
                user_id=user_id,
                is_active=True
            ).order_by(self.UserMemory.updated_at.desc()).all()
            
            return [
                {
                    'id': memory.id,
                    'memory_type': memory.memory_type,
                    'key_info': memory.key_info,
                    'value_info': memory.value_info,
                    'confidence_score': memory.confidence_score,
                    'created_at': memory.created_at.isoformat(),
                    'updated_at': memory.updated_at.isoformat()
                }
                for memory in memories
            ]
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des mémoires: {e}")
            return []
    
    def delete_memory(self, user_id: str, memory_id: str) -> bool:
        """Supprime une mémoire spécifique (la marque comme inactive)"""
        if not self.db or not self.UserMemory:
            return False
            
        try:
            memory = self.UserMemory.query.filter_by(
                id=memory_id,
                user_id=user_id
            ).first()
            
            if memory:
                memory.is_active = False
                memory.updated_at = datetime.utcnow()
                self.db.session.commit()
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Erreur lors de la suppression de mémoire: {e}")
            if self.db:
                self.db.session.rollback()
            return False

# Instance globale
user_memory_manager = UserMemoryManager() 