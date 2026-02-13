"""
Point d'entrée principal du système Refactoring Swarm.
Ce fichier DOIT s'appeler main.py selon les spécifications du TP.
"""
import argparse
import os
import sys
from src.swarm import RefactoringSwarm

def main():
    """
    Fonction principale qui lance le système de refactoring.
    Accepte un argument --target_dir pour spécifier le dossier à analyser.
    """
    # Configuration du parser d'arguments
    parser = argparse.ArgumentParser(
        description="Refactoring Swarm - Système de correction automatique de code Python"
    )
    parser.add_argument(
        "--target_dir",
        type=str,
        default="sandbox",
        help="Répertoire contenant le code à analyser et corriger (par défaut: sandbox)"
    )
    
    args = parser.parse_args()
    
    # Vérification que le répertoire existe
    abs_target = os.path.abspath(args.target_dir)
    if not os.path.isdir(abs_target):
        print(f"❌ Erreur: Le répertoire '{abs_target}' n'existe pas")
        sys.exit(1)
    
    # Vérification qu'il y a au moins un fichier Python dans le répertoire
    py_files = []
    for root, _, files in os.walk(abs_target):
        py_files.extend([f for f in files if f.endswith('.py')])
    
    if not py_files:
        print(f"⚠️  Avertissement: Aucun fichier Python trouvé dans {abs_target}")
        print("Le système va quand même s'exécuter, mais il n'y aura rien à corriger.")
    
    # Lancement du swarm
    try:
        swarm = RefactoringSwarm(abs_target)
        swarm.run()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interruption par l'utilisateur (Ctrl+C)")
        print("📊 Les logs partiels sont disponibles dans logs/experiment_data.json")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erreur critique: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()