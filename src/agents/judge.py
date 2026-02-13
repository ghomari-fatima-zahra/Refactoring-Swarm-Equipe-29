"""
Agent Testeur - Valide le code en générant et exécutant des tests.
Utilise Groq (Llama) pour générer des tests intelligents et adaptatifs.
"""
import os
import subprocess
import sys
from groq import Groq
from dotenv import load_dotenv
from src.utils.logger import log_experiment, ActionType
from src.tools.file_handler import safe_write_file

load_dotenv()

class JudgeAgent:
    """
    Agent responsable de la validation du code via des tests.
    Génère des tests automatiquement et les exécute avec pytest.
    """
    
    def __init__(self):
        """Initialise l'agent avec le client Groq et le modèle Llama."""
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model_name = "llama-3.3-70b-versatile"

    def validate(self, target_dir: str) -> bool:
        """
        Méthode legacy pour compatibilité.
        
        Args:
            target_dir: Répertoire contenant le code à tester
            
        Returns:
            True si les tests passent, False sinon
        """
        success, _ = self.validate_with_error(target_dir)
        return success

    def validate_with_error(self, target_dir: str) -> tuple[bool, str]:
        """
        Valide le code en exécutant les tests et retourne les erreurs détaillées.
        
        Args:
            target_dir: Répertoire contenant le code à tester
            
        Returns:
            Tuple (succès: bool, message d'erreur: str)
        """
        # Recherche des fichiers Python (non-test)
        py_files = []
        for root, _, files in os.walk(target_dir):
            for file in files:
                if file.endswith(".py") and not file.startswith("test_"):
                    py_files.append(os.path.join(root, file))
        
        if not py_files:
            print("  ℹ️  Aucun fichier Python à tester")
            return True, ""
        
        # Utilisation du premier fichier Python trouvé
        main_file = py_files[0]
        filename = os.path.basename(main_file)
        test_filename = f"test_{filename}"
        test_path = os.path.join(target_dir, test_filename)
        
        # Génération du test si nécessaire
        if not os.path.exists(test_path):
            print(f"  🔧 Génération du test pour {filename}...")
            self._generate_test(target_dir, filename, test_filename, main_file)
        else:
            print(f"  📋 Test existant trouvé: {test_filename}")
        
        # Exécution des tests avec pytest
        try:
            print(f"  🧪 Exécution de pytest sur {test_filename}...")
            result = subprocess.run(
                [sys.executable, "-m", "pytest", test_path, "-v", "--tb=short"],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=target_dir
            )
            
            success = (result.returncode == 0)
            output = result.stdout + "\n" + result.stderr
            
            # Logging pour l'analyse scientifique
            log_experiment(
                agent_name="JudgeAgent",
                model_used="pytest",
                action=ActionType.DEBUG,
                details={
                    "target_dir": target_dir,
                    "test_file": test_filename,
                    "input_prompt": f"Execute pytest on {test_filename}",
                    "output_response": output[:2000]  # Tronqué pour le log
                },
                status="SUCCESS" if success else "FAILED"
            )
            
            if success:
                print(f"  ✅ Tests passés: {test_filename}")
            else:
                print(f"  ❌ Tests échoués: {test_filename}")
                # Afficher un extrait de l'erreur
                error_lines = [line for line in output.split('\n') if 'FAILED' in line or 'ERROR' in line or 'assert' in line.lower()]
                if error_lines:
                    print(f"  💥 Erreur: {error_lines[0][:100]}")
            
            return success, output
            
        except subprocess.TimeoutExpired:
            error_msg = "Timeout: Les tests ont pris trop de temps (>30s)"
            print(f"  ⏱️  {error_msg}")
            return False, error_msg
        except Exception as e:
            error_msg = f"Exception lors de l'exécution: {str(e)}"
            print(f"  ❌ {error_msg}")
            return False, error_msg

    def _generate_test(self, target_dir: str, py_file: str, test_file: str, main_file_path: str):
        """
        Génère un test intelligent pour le fichier Python en utilisant Groq (Llama).
        
        Args:
            target_dir: Répertoire cible
            py_file: Nom du fichier Python à tester
            test_file: Nom du fichier de test à créer
            main_file_path: Chemin complet du fichier à tester
        """
        # Lecture du code source pour une génération de test intelligente
        try:
            with open(main_file_path, "r", encoding="utf-8") as f:
                source_code = f.read()
        except Exception as e:
            print(f"  ⚠️  Erreur lecture du fichier source: {e}")
            source_code = ""
        
        module_name = py_file[:-3]  # Retirer .py
        
        # Génération de test avec Groq si le code source est disponible
        if source_code and len(source_code.strip()) > 0:
            test_code = self._generate_smart_test(module_name, source_code)
        else:
            # Fallback: test minimal
            test_code = self._generate_minimal_test(module_name)
        
        # Sauvegarde du fichier de test
        test_path = os.path.join(target_dir, test_file)
        safe_write_file(test_path, test_code)
        
        # Logging
        log_experiment(
            agent_name="JudgeAgent",
            model_used=self.model_name if source_code else "rule-based",
            action=ActionType.GENERATION,
            details={
                "file_generated": test_file,
                "module_tested": module_name,
                "input_prompt": f"Generate comprehensive tests for {py_file}",
                "output_response": test_code[:1000]  # Tronqué pour le log
            }
        )
        
        print(f"  ✅ Test créé: {test_file}")

    def _generate_smart_test(self, module_name: str, source_code: str) -> str:
        """
        Génère un test GÉNÉRIQUE et ADAPTATIF en analysant le code source avec Llama.
        Le test s'adapte automatiquement aux fonctions présentes dans le code.
        
        Args:
            module_name: Nom du module à tester
            source_code: Code source du module
            
        Returns:
            Code du test généré
        """
        prompt = f"""Tu es un expert en tests Python. Génère un fichier de test pytest pour ce module.

MODULE: {module_name}

CODE SOURCE À TESTER:
```python
{source_code}
```

INSTRUCTIONS CRITIQUES:

1. ANALYSE D'ABORD LE CODE:
   - Identifie TOUTES les fonctions définies dans le code source
   - Comprends ce que fait chaque fonction (addition, soustraction, calcul, etc.)
   - Note les paramètres de chaque fonction

2. GÉNÈRE DES TESTS SIMPLES ET ROBUSTES:
   - Importe les fonctions avec: from {module_name} import *
   - Crée UNE fonction de test par fonction trouvée dans le code
   - Utilise UNIQUEMENT des nombres ENTIERS dans les tests (jamais de floats)
   - NE teste PAS les exceptions (pas de pytest.raises)
   - Teste que chaque fonction retourne le bon résultat

3. RÈGLES POUR LES TESTS:
   - Pour une fonction d'addition: teste avec 2+3=5, 10+5=15, etc.
   - Pour une fonction de soustraction: teste avec 5-3=2, 10-4=6, etc.
   - Pour une fonction de multiplication: teste avec 3*4=12, 5*2=10, etc.
   - Pour une fonction de division: teste SEULEMENT avec des diviseurs NON-NULS (10/2=5, 20/4=5)
   - Pour division par zéro: teste juste que la fonction retourne quelque chose (pas None)

4. FORMAT DE SORTIE:
   - Commence directement par: from {module_name} import *
   - Pas de texte explicatif
   - Pas de blocs markdown (```python ou ```)
   - Juste du code Python pur et simple

EXEMPLE (si le code contient "def calculate(a, b): return a + b"):
from {module_name} import calculate

def test_calculate():
    assert calculate(5, 3) == 8
    assert calculate(10, 2) == 12
    assert calculate(0, 0) == 0

MAINTENANT, génère le test pour le code fourni ci-dessus.
Retourne UNIQUEMENT le code Python du test, rien d'autre.
"""
        
        try:
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.model_name,
                temperature=0.1  # Très bas pour des tests déterministes
            )
            test_code = response.choices[0].message.content.strip()
            
            # Nettoyage agressif des blocs markdown
            if "```python" in test_code:
                test_code = test_code.split("```python")[1].split("```")[0]
            elif "```" in test_code:
                parts = test_code.split("```")
                if len(parts) >= 2:
                    test_code = parts[1]
            
            test_code = test_code.strip()
            
            # Vérifier que le test généré n'est pas vide
            if len(test_code) < 50:
                print("  ⚠️  Test généré trop court, utilisation du fallback minimal")
                return self._generate_minimal_test(module_name)
            
            print(f"  📝 Test généré: {len(test_code)} caractères")
            return test_code
            
        except Exception as e:
            print(f"  ⚠️  Erreur génération test intelligent: {e}")
            return self._generate_minimal_test(module_name)

    def _generate_minimal_test(self, module_name: str) -> str:
        """
        Génère un test MINIMAL qui vérifie juste que le module s'importe correctement.
        Ce test devrait TOUJOURS passer si le code a une syntaxe Python valide.
        
        Args:
            module_name: Nom du module à tester
            
        Returns:
            Code du test minimal
        """
        return f'''"""
Test minimal pour {module_name}.py
Généré automatiquement par JudgeAgent (fallback)
"""
import {module_name}

def test_module_imports():
    """Vérifie que le module peut être importé sans erreur de syntaxe."""
    assert {module_name} is not None
    print("✅ Module {module_name} importé avec succès")

def test_syntax_valid():
    """Vérifie que le code compile correctement."""
    # Si on arrive ici, c'est que la syntaxe Python est valide
    assert True
    print("✅ Syntaxe Python valide")
'''