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

        # Récupérer les mémoires existantes pour éviter les doublons
        existing_memories = self.get_user_memories(user_id)
        existing_info = ""
        if existing_memories:
            existing_info = "\n\nINFORMATIONS DÉJÀ MÉMORISÉES (ne pas redupliquer):\n"
            for memory in existing_memories:
                existing_info += f"- {memory['memory_type']}: {memory['key_info']} = {memory['value_info']}\n"

        try:
            client = openai.OpenAI(api_key=openai_api_key)

            extraction_prompt = f"""
Analyse ce message utilisateur et extrait les informations importantes à retenir pour personnaliser les futures conversations.

Message: "{message}"{existing_info}
1. INFORMATIONS SUR L'UTILISATEUR (priorité haute):
   - Utilisez les indicateurs : "Mon...", "Je...", "Ma...", "J'ai...", "Je suis..."
   - Types suggérés : identite, preferences_crypto, portefeuille, experience_trading, etc.

2. INFORMATIONS SUR D'AUTRES PERSONNES (contacts/relations):
   - Utilisez les indicateurs : "L'adresse de [nom]", "[nom] utilise...", "Mon ami [nom]..."
   - Format des clés : "[type]_[nom]" (ex: "wallet_lucas", "plateforme_marie", "profession_paul")
   - Type de mémoire : "contacts" ou "relations"

RÈGLES CRITIQUES:
1. TOUJOURS extraire les informations sur l'utilisateur en priorité
2. Extraire aussi les informations utiles sur d'autres personnes nommées
3. IGNORE les détails de transactions ponctuelles (montants, hash, etc.)
4. IGNORE les questions générales et conversations sans info durable
5. NE REDUPLIQUE PAS les informations déjà mémorisées
6. Utilise des noms de clés cohérents et standards

EXEMPLES D'INFORMATIONS À EXTRAIRE:

SUR L'UTILISATEUR:
✅ "Mon portefeuille principal est 0x123..." → {{"memory_type": "portefeuille", "key_info": "adresse_wallet", "value_info": "0x123...", "confidence_score": 0.95}}
✅ "Je préfère Ethereum" → {{"memory_type": "preferences_crypto", "key_info": "blockchain_preferee", "value_info": "Ethereum", "confidence_score": 0.9}}
✅ "Je suis développeur" → {{"memory_type": "situation_professionnelle", "key_info": "profession", "value_info": "développeur", "confidence_score": 0.9}}

SUR D'AUTRES PERSONNES:
✅ "L'adresse MetaMask de Lucas est 0x456..." → {{"memory_type": "contacts", "key_info": "wallet_lucas", "value_info": "0x456...", "confidence_score": 0.9}}
✅ "Marie utilise Binance" → {{"memory_type": "contacts", "key_info": "plateforme_marie", "value_info": "Binance", "confidence_score": 0.8}}
✅ "Paul travaille chez Uniswap" → {{"memory_type": "relations", "key_info": "profession_paul", "value_info": "travaille chez Uniswap", "confidence_score": 0.8}}
✅ "Mon collègue Thomas préfère Bitcoin" → {{"memory_type": "relations", "key_info": "preference_thomas", "value_info": "Bitcoin", "confidence_score": 0.8}}

EXEMPLES D'INFORMATIONS À IGNORER:
❌ "Envoie 1 ETH à 0x789..." → détail de transaction ponctuelle
❌ "Transaction hash: 0xabc..." → détail technique ponctuel
❌ "Combien vaut Bitcoin ?" → simple question
❌ "La fee était de 50 gwei" → détail technique temporaire

INSTRUCTIONS POUR LES NOMS:
- Si le nom est mentionné clairement, utilisez-le : "wallet_lucas", "plateforme_marie"
- Si c'est un rôle/relation : "wallet_collegue", "preference_ami", "adresse_frere"
- Toujours en minuscules et snake_case

Format JSON OBLIGATOIRE:
{{
  "extractions": [
    {{
      "memory_type": "type_créé_par_toi",
      "key_info": "nom_coherent_et_unique",
      "value_info": "description détaillée",
      "confidence_score": 0.8
    }}
  ]
}}

Si aucune information importante et nouvelle n'est détectée, réponds: {{"extractions": []}}
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

    def _is_duplicate_info(self, user_id: str, memory_type: str, key_info: str, value_info: str) -> bool:
        """Vérifie si une information similaire existe déjà pour éviter les doublons"""
        if not self.db or not self.UserMemory:
            return False

        try:
            # Groupes de clés similaires étendus pour inclure les contacts
            similar_key_groups = [
                ['wallet', 'adresse_wallet', 'address_wallet', 'portefeuille_address'],
                ['nom', 'prenom', 'name', 'username'],
                ['age', 'âge'],
                ['profession', 'job', 'travail', 'metier'],
                ['experience', 'exp', 'niveau'],
                ['plateforme', 'exchange', 'platform'],
                ['preference', 'preferee', 'favori', 'favorite']
            ]

            # Normaliser la clé actuelle
            normalized_key = key_info.lower().strip()

            # Chercher des informations existantes avec des clés similaires
            existing_memories = self.UserMemory.query.filter_by(
                user_id=user_id,
                memory_type=memory_type,
                is_active=True
            ).all()

            for memory in existing_memories:
                existing_key = memory.key_info.lower().strip()
                existing_value = memory.value_info.lower().strip()
                current_value = value_info.lower().strip()

                # Vérifier si c'est exactement la même clé
                if existing_key == normalized_key:
                    return True

                # Pour les contacts/relations, vérifier les clés avec noms de personnes
                if memory_type in ['contacts', 'relations']:
                    # Extraire le nom de la personne de la clé (ex: wallet_lucas -> lucas)
                    existing_person = existing_key.split('_')[-1] if '_' in existing_key else existing_key
                    current_person = normalized_key.split('_')[-1] if '_' in normalized_key else normalized_key

                    # Si c'est la même personne, vérifier le type d'info
                    if existing_person == current_person:
                        existing_info_type = existing_key.split('_')[0] if '_' in existing_key else existing_key
                        current_info_type = normalized_key.split('_')[0] if '_' in normalized_key else normalized_key

                        # Vérifier si c'est le même type d'information pour la même personne
                        for group in similar_key_groups:
                            if existing_info_type in group and current_info_type in group:
                                return True

                # Vérifier les groupes de clés similaires pour les autres types
                else:
                    for group in similar_key_groups:
                        if normalized_key in group and existing_key in group:
                            # Même type d'info, vérifier si la valeur est similaire
                            if existing_value == current_value or abs(len(existing_value) - len(current_value)) <= 3:
                                return True

            return False

        except Exception as e:
            logger.error(f"Erreur lors de la vérification des doublons: {e}")
            return False

    def store_memory_info(self, user_id: str, memory_type: str, key_info: str, value_info: str,
                         confidence_score: float = 1.0, source_message_id: str = None) -> bool:
        """Stocke une information dans la mémoire utilisateur avec détection de doublons améliorée"""
        if not self.db or not self.UserMemory:
            return False

        try:
            # Vérifier les doublons avant de stocker
            if self._is_duplicate_info(user_id, memory_type, key_info, value_info):
                logger.info(f"Information dupliquée ignorée pour {user_id}: {key_info} = {value_info}")
                return False

            # Chercher si une info avec cette clé exacte existe déjà
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