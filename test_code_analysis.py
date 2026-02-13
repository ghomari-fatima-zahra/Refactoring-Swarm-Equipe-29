"""
Script d'analyse statique du code pour détecter les problèmes
sans avoir besoin d'exécuter le code.
"""
import os
import ast
import sys

def test_syntax():
    """Teste la syntaxe Python de tous les fichiers .py"""
    print("=" * 70)
    print("🔍 TEST 1: VÉRIFICATION DE LA SYNTAXE PYTHON")
    print("=" * 70)
    
    files_to_check = [
        "main.py",
        "src/swarm.py",
        "src/agents/auditor.py",
        "src/agents/fixer.py",
        "src/agents/judge.py",
        "src/tools/file_handler.py",
        "src/utils/logger.py",
        "sandbox/messy_code.py",
        "sandbox/test_messy_code.py",
    ]
    
    errors = []
    for filepath in files_to_check:
        if not os.path.exists(filepath):
            errors.append(f"❌ {filepath} - FICHIER MANQUANT")
            continue
            
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                code = f.read()
            ast.parse(code)
            print(f"✅ {filepath}")
        except SyntaxError as e:
            errors.append(f"❌ {filepath} - ERREUR DE SYNTAXE: {e}")
            print(f"❌ {filepath} - ERREUR DE SYNTAXE")
        except Exception as e:
            errors.append(f"⚠️  {filepath} - ERREUR: {e}")
            print(f"⚠️  {filepath} - ERREUR: {e}")
    
    if errors:
        print("\n" + "=" * 70)
        print("ERREURS TROUVÉES:")
        for error in errors:
            print(f"  {error}")
        return False
    else:
        print("\n✅ Tous les fichiers ont une syntaxe Python valide!")
        return True

def test_imports():
    """Teste si les imports sont corrects"""
    print("\n" + "=" * 70)
    print("🔍 TEST 2: VÉRIFICATION DES IMPORTS")
    print("=" * 70)
    
    # Test des imports internes
    try:
        sys.path.insert(0, os.getcwd())
        from src.swarm import RefactoringSwarm
        print("✅ Import de RefactoringSwarm OK")
    except ImportError as e:
        print(f"❌ Erreur d'import RefactoringSwarm: {e}")
        return False
    
    try:
        from src.agents.auditor import AuditorAgent
        print("✅ Import de AuditorAgent OK")
    except ImportError as e:
        print(f"❌ Erreur d'import AuditorAgent: {e}")
        return False
    
    try:
        from src.agents.fixer import FixerAgent
        print("✅ Import de FixerAgent OK")
    except ImportError as e:
        print(f"❌ Erreur d'import FixerAgent: {e}")
        return False
    
    try:
        from src.agents.judge import JudgeAgent
        print("✅ Import de JudgeAgent OK")
    except ImportError as e:
        print(f"❌ Erreur d'import JudgeAgent: {e}")
        return False
    
    return True

def test_code_consistency():
    """Teste la cohérence du code (noms de fonctions, etc.)"""
    print("\n" + "=" * 70)
    print("🔍 TEST 3: VÉRIFICATION DE LA COHÉRENCE DU CODE")
    print("=" * 70)
    
    # Vérifier messy_code.py
    try:
        with open("sandbox/messy_code.py", "r", encoding="utf-8") as f:
            code = f.read()
        
        # Extraire les noms de fonctions
        tree = ast.parse(code)
        functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        print(f"📝 Fonctions dans messy_code.py: {functions}")
        
        # Vérifier test_messy_code.py
        with open("sandbox/test_messy_code.py", "r", encoding="utf-8") as f:
            test_code = f.read()
        
        # Vérifier si les fonctions testées existent dans le code
        if "add" in test_code and "add" not in functions:
            print("⚠️  PROBLÈME: Le test cherche 'add' mais cette fonction n'existe pas dans messy_code.py")
            if "addition" in functions:
                print("   💡 Solution: Le code a 'addition' mais le test cherche 'add'")
                return False
        
        if "subtract" in test_code and "subtract" not in functions:
            print("⚠️  PROBLÈME: Le test cherche 'subtract' mais cette fonction n'existe pas dans messy_code.py")
            return False
        
        print("✅ Cohérence entre code et tests OK")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {e}")
        return False

def test_file_structure():
    """Vérifie que tous les fichiers nécessaires existent"""
    print("\n" + "=" * 70)
    print("🔍 TEST 4: VÉRIFICATION DE LA STRUCTURE DES FICHIERS")
    print("=" * 70)
    
    required_files = [
        "main.py",
        "src/swarm.py",
        "src/agents/auditor.py",
        "src/agents/fixer.py",
        "src/agents/judge.py",
        "src/tools/file_handler.py",
        "src/utils/logger.py",
        "prompts/auditor_prompt.txt",
        "prompts/fixer_prompt.txt",
        "requirements.txt",
    ]
    
    missing = []
    for filepath in required_files:
        if os.path.exists(filepath):
            print(f"✅ {filepath}")
        else:
            print(f"❌ {filepath} - MANQUANT")
            missing.append(filepath)
    
    if missing:
        print(f"\n⚠️  {len(missing)} fichier(s) manquant(s)")
        return False
    else:
        print("\n✅ Tous les fichiers requis sont présents")
        return True

def test_env_config():
    """Vérifie la configuration de l'environnement"""
    print("\n" + "=" * 70)
    print("🔍 TEST 5: VÉRIFICATION DE LA CONFIGURATION")
    print("=" * 70)
    
    # Vérifier .env
    if os.path.exists(".env"):
        print("✅ Fichier .env existe")
        try:
            from dotenv import load_dotenv
            load_dotenv()
            groq_key = os.getenv("GROQ_API_KEY")
            if groq_key:
                print(f"✅ GROQ_API_KEY trouvée (longueur: {len(groq_key)})")
            else:
                print("⚠️  GROQ_API_KEY non trouvée dans .env")
                print("   Le système nécessite GROQ_API_KEY pour fonctionner")
        except ImportError:
            print("⚠️  python-dotenv non installé (ne peut pas vérifier .env)")
    else:
        print("⚠️  Fichier .env manquant")
        print("   Créez un fichier .env avec: GROQ_API_KEY=votre_clé")
    
    return True

def main():
    """Fonction principale"""
    print("\n" + "=" * 70)
    print("🧪 ANALYSE STATIQUE DU CODE - PROJET SWARM")
    print("=" * 70)
    
    results = []
    
    results.append(("Syntaxe Python", test_syntax()))
    results.append(("Imports", test_imports()))
    results.append(("Cohérence du code", test_code_consistency()))
    results.append(("Structure des fichiers", test_file_structure()))
    test_env_config()  # Info seulement
    
    print("\n" + "=" * 70)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 70)
    
    for name, result in results:
        status = "✅ PASSÉ" if result else "❌ ÉCHOUÉ"
        print(f"{status} - {name}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\n🎉 Tous les tests sont passés!")
    else:
        print("\n⚠️  Certains tests ont échoué. Voir les détails ci-dessus.")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
