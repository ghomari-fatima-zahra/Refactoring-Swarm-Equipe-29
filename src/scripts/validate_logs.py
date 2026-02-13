"""
Script de validation des logs d'expérimentation.
Vérifie que le fichier experiment_data.json respecte le protocole de logging requis.
"""
import json
from pathlib import Path

# Actions qui nécessitent les champs input_prompt et output_response
REQUIRED_DETAIL_KEYS = {"input_prompt", "output_response"}
PROMPT_ACTIONS = {"CODE_ANALYSIS", "FIX", "DEBUG"}

def main():
    """Valide le contenu du fichier de logs."""
    log_path = Path("logs/experiment_data.json")
    
    if not log_path.exists():
        print("✅ OK: Aucun fichier de logs généré (projet pas encore exécuté)")
        return
    
    try:
        data = json.loads(log_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"❌ ERREUR: Fichier de logs invalide (JSON mal formé)")
        print(f"   Détail: {e}")
        return
    
    if not isinstance(data, list):
        print("❌ ERREUR: Le fichier de logs doit être un tableau JSON")
        return
    
    print(f"📊 Validation de {len(data)} entrée(s) de log...")
    
    errors = []
    for i, entry in enumerate(data):
        if not isinstance(entry, dict):
            errors.append(f"Entrée [{i}]: doit être un objet JSON")
            continue
        
        # Vérification des champs obligatoires
        required_fields = {"timestamp", "agent", "model", "action", "status", "details"}
        missing = required_fields - entry.keys()
        if missing:
            errors.append(f"Entrée [{i}]: champs manquants: {missing}")
            continue
        
        action = entry.get("action")
        details = entry.get("details")
        
        # Validation spécifique pour les actions de prompt
        if action in PROMPT_ACTIONS:
            if not isinstance(details, dict):
                errors.append(f"Entrée [{i}]: 'details' doit être un objet pour l'action {action}")
                continue
            
            missing_details = REQUIRED_DETAIL_KEYS - details.keys()
            if missing_details:
                errors.append(
                    f"Entrée [{i}]: l'action {action} nécessite les champs: {missing_details}"
                )
    
    if errors:
        print(f"\n❌ {len(errors)} erreur(s) trouvée(s):")
        for error in errors:
            print(f"   • {error}")
        return
    
    print(f"✅ OK: Tous les logs sont conformes au protocole")
    print(f"   {len(data)} entrée(s) validée(s)")

if __name__ == "__main__":
    main()