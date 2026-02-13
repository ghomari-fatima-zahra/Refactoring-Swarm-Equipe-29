"""
RefactoringSwarm - Orchestrateur du système multi-agents.
Gère le cycle d'analyse, correction et validation du code.
"""
import os
import json
from src.agents.auditor import AuditorAgent
from src.agents.fixer import FixerAgent
from src.agents.judge import JudgeAgent

class RefactoringSwarm:
    """
    Orchestrateur principal du système de refactoring automatique.
    Coordonne les 3 agents (Auditor, Fixer, Judge) dans une boucle de feedback.
    """
    
    def __init__(self, target_dir: str):
        """
        Initialise le swarm avec le répertoire cible.
        
        Args:
            target_dir: Répertoire contenant le code à refactorer
        """
        self.target_dir = target_dir
        self.auditor = AuditorAgent()
        self.fixer = FixerAgent()
        self.judge = JudgeAgent()
        self.last_test_error = ""
        self.max_iterations = 10

    def run(self):
        """
        Lance le processus de refactoring complet.
        Boucle sur analyse → correction → tests jusqu'à succès ou max itérations.
        """
        print(f"🚀 Démarrage du refactoring sur: {self.target_dir}")
        print("=" * 70)
        
        # Vérification initiale - teste si le code actuel fonctionne
        print("\n🔍 VÉRIFICATION INITIALE")
        print("-" * 70)
        initial_success, initial_error = self.judge.validate_with_error(self.target_dir)
        
        if initial_success:
            print("\n  ✅ Le code fonctionne déjà parfaitement !")
            print("  ℹ️  Aucune correction nécessaire")
            print("\n" + "=" * 70)
            print("🎉 SUCCÈS! Le code est déjà correct.")
            print("=" * 70)
            return
        else:
            print("\n  ℹ️  Code nécessite des corrections")
            self.last_test_error = initial_error
        
        # Boucle de refactoring
        for iteration in range(1, self.max_iterations + 1):
            print(f"\n{'='*70}")
            print(f"🔄 ITÉRATION {iteration}/{self.max_iterations}")
            print(f"{'='*70}")
            
            # Phase 1: Audit du code
            print("\n📊 PHASE 1: AUDIT DU CODE")
            print("-" * 70)
            
            if not self.last_test_error:
                # Audit normal - analyse statique du code
                print("  🔍 Analyse statique du code...")
                audit_response = self.auditor.analyze(self.target_dir)
            else:
                # Audit basé sur l'erreur de test
                print("  🐞 Analyse basée sur l'erreur de test précédente")
                print(f"  📋 Erreur à corriger:")
                print(f"  {self.last_test_error[:300]}...")
                
                # Créer un "audit" basé sur l'erreur
                audit_response = json.dumps([{
                    "file": "messy_code.py",
                    "line": 0,
                    "issue_type": "TEST_FAILURE",
                    "description": f"Tests échoués. Erreur:\n{self.last_test_error[:500]}"
                }])
            
            # Phase 2: Correction
            print("\n🛠️  PHASE 2: CORRECTION DU CODE")
            print("-" * 70)
            
            try:
                issues = json.loads(audit_response)
                if issues:
                    print(f"  🛠️  {len(issues)} problème(s) identifié(s)")
                    self.fixer.fix(self.target_dir, audit_response)
                else:
                    print("  ℹ️  Aucun problème détecté par l'audit")
            except json.JSONDecodeError:
                print("  ⚠️  Erreur de parsing de l'audit, passage à la validation...")
            
            # Réinitialiser l'erreur de test après la correction
            self.last_test_error = ""
            
            # Phase 3: Validation par tests
            print("\n✅ PHASE 3: VALIDATION PAR TESTS")
            print("-" * 70)
            
            success, error_output = self.judge.validate_with_error(self.target_dir)
            
            if success:
                print("\n" + "=" * 70)
                print("🎉 SUCCÈS! Tous les tests sont passés!")
                print("=" * 70)
                print(f"\n✨ Refactoring terminé avec succès en {iteration} itération(s)")
                print(f"📂 Code corrigé disponible dans: {self.target_dir}")
                print(f"📊 Logs disponibles dans: logs/experiment_data.json")
                return
            else:
                # Tests échoués
                self.last_test_error = error_output
                print(f"\n  ⚠️  Tests échoués, préparation de l'itération suivante...")
                
                # Afficher un extrait de l'erreur
                error_lines = [line for line in error_output.split('\n') 
                             if line.strip() and ('FAILED' in line or 'ERROR' in line or 'SyntaxError' in line)]
                if error_lines:
                    print(f"  💥 Erreur: {error_lines[0][:150]}")
        
        # Échec après max_iterations
        print("\n" + "=" * 70)
        print(f"⚠️  LIMITE D'ITÉRATIONS ATTEINTE ({self.max_iterations}/{self.max_iterations})")