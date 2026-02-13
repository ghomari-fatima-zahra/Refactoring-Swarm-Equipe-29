#!/usr/bin/env python
"""
Script rapide pour vérifier si le code fonctionne.
Lancez: python run_tests_locally.py
"""
import sys
import os

# Se placer à la racine du projet
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.getcwd())

def test_messy_code():
    """Teste que messy_code.py a les bonnes fonctions et que les tests passent."""
    print("=" * 60)
    print("Test 1: Import et logique de messy_code")
    print("=" * 60)
    try:
        os.chdir("sandbox")
        import messy_code
        assert hasattr(messy_code, "add"), "Fonction 'add' manquante"
        assert hasattr(messy_code, "subtract"), "Fonction 'subtract' manquante"
        assert messy_code.add(2, 3) == 5
        assert messy_code.add(10, 5) == 15
        assert messy_code.subtract(5, 3) == 2
        assert messy_code.subtract(10, 4) == 6
        print("OK - add et subtract fonctionnent correctement.")
        os.chdir("..")
        return True
    except Exception as e:
        print(f"ERREUR: {e}")
        os.chdir("..")
        return False

def test_imports_swarm():
    """Teste que les modules du projet s'importent."""
    print("\n" + "=" * 60)
    print("Test 2: Imports du projet (swarm, agents)")
    print("=" * 60)
    try:
        from src.swarm import RefactoringSwarm
        from src.agents.auditor import AuditorAgent
        from src.agents.fixer import FixerAgent
        from src.agents.judge import JudgeAgent
        print("OK - Tous les imports fonctionnent.")
        return True
    except ImportError as e:
        print(f"ERREUR import: {e}")
        return False

def test_pytest_available():
    """Vérifie si pytest est disponible et lance les tests du sandbox."""
    print("\n" + "=" * 60)
    print("Test 3: Pytest sur sandbox/test_messy_code.py")
    print("=" * 60)
    try:
        import subprocess
        r = subprocess.run(
            [sys.executable, "-m", "pytest", "sandbox/test_messy_code.py", "-v", "--tb=short"],
            capture_output=True,
            text=True,
            timeout=15,
            cwd=os.getcwd(),
        )
        if r.returncode == 0:
            print("OK - Tous les tests pytest sont passés.")
            if r.stdout:
                for line in r.stdout.split("\n")[-6:]:
                    if line.strip():
                        print(f"  {line}")
            return True
        else:
            print("ERREUR - Les tests pytest ont échoué:")
            print(r.stdout or r.stderr or "pas de sortie")
            return False
    except FileNotFoundError:
        print("pytest non trouvé. Installez avec: pip install pytest")
        return False
    except Exception as e:
        print(f"ERREUR: {e}")
        return False

def main():
    print("\nVerification du projet swarm...\n")
    r1 = test_messy_code()
    r2 = test_imports_swarm()
    r3 = test_pytest_available()
    print("\n" + "=" * 60)
    if r1 and r2 and r3:
        print("RESULTAT: Tout fonctionne.")
        return 0
    else:
        print("RESULTAT: Au moins un test a échoué.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
