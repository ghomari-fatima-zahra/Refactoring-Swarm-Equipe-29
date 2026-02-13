"""
Module de logging pour l'expérimentation scientifique.
Enregistre toutes les interactions avec les LLM selon le protocole requis.
"""
import json
import os
from datetime import datetime
from enum import Enum
from pathlib import Path

class ActionType(Enum):
    """Types d'actions standardisés pour le logging."""
    ANALYSIS = "CODE_ANALYSIS"
    GENERATION = "GENERATION"
    DEBUG = "DEBUG"
    FIX = "FIX"

def log_experiment(agent_name: str, model_used: str, action: ActionType, 
                   details: dict, status: str = "SUCCESS"):
    """
    Enregistre une interaction avec le LLM dans le fichier de logs.
    
    Args:
        agent_name: Nom de l'agent (ex: "AuditorAgent")
        model_used: Modèle utilisé (ex: "gemini-2.0-flash-exp")
        action: Type d'action (utiliser ActionType enum)
        details: Dictionnaire contenant au minimum input_prompt et output_response
        status: Statut de l'opération (SUCCESS/FAILED)
    """
    # Vérification des champs obligatoires pour les actions de prompt
    if action in [ActionType.ANALYSIS, ActionType.FIX, ActionType.DEBUG]:
        if "input_prompt" not in details or "output_response" not in details:
            raise ValueError(
                f"Les actions {action.value} nécessitent 'input_prompt' et 'output_response' dans details"
            )
    
    # Création du dossier logs s'il n'existe pas
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / "experiment_data.json"
    
    # Structure de l'entrée de log
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "agent": agent_name,
        "model": model_used,
        "action": action.value,
        "status": status,
        "details": details
    }
    
    # Lecture des logs existants
    existing_logs = []
    if log_file.exists():
        try:
            with open(log_file, "r", encoding="utf-8") as f:
                existing_logs = json.load(f)
        except json.JSONDecodeError:
            existing_logs = []
    
    # Ajout de la nouvelle entrée
    existing_logs.append(log_entry)
    
    # Sauvegarde
    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(existing_logs, f, indent=2, ensure_ascii=False)