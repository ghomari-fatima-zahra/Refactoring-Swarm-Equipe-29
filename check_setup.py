"""
Script de vérification de l'environnement de développement.
Vérifie que tous les prérequis sont installés et configurés correctement.
"""
import sys
import os
from dotenv import load_dotenv

def check_python():
    """Vérifie que la version de Python est compatible (3.10 ou 3.11)."""
    v = sys.version_info
    if not (v.major == 3 and v.minor in (10, 11)):
        print("❌ Python 3.10 ou 3.11 requis")
        print(f"   Version actuelle: {v.major}.{v.minor}.{v.micro}")
        return False
    print(f"✅ Version Python OK ({v.major}.{v.minor}.{v.micro})")
    return True

def check_env():
    """Vérifie que le fichier .env existe et contient la clé API Google."""
    if not os.path.exists(".env"):
        print("❌ Fichier .env manquant")
        print("   Action: Créez un fichier .env et ajoutez votre GOOGLE_API_KEY")
        print("   Exemple: GOOGLE_API_KEY=AIzaSy...")
        return False
    
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        print("❌ GOOGLE_API_KEY manquante dans .env")
        print("   Action: Ajoutez votre clé API Google dans le fichier .env")
        print("   Obtenez une clé gratuite sur: https://aistudio.google.com/app/apikey")
        return False
    
    if len(api_key) < 20:
        print("❌ GOOGLE_API_KEY semble invalide (trop courte)")
        return False
    
    print("✅ Fichier .env OK")
    print(f"   Clé API: {api_key[:10]}...{api_key[-5:]}")
    return True

def check_dirs():
    """Crée les répertoires nécessaires s'ils n'existent pas."""
    required_dirs = ["src", "prompts", "sandbox", "logs"]
    
    for d in required_dirs:
        os.makedirs(d, exist_ok=True)
    
    print("✅ Structure de répertoires OK")
    return True

def check_packages():
    """Vérifie que les packages Python nécessaires sont installés."""
    required_packages = [
        ("google.generativeai", "google-generativeai"),
        ("dotenv", "python-dotenv"),
        ("pytest", "pytest"),
    ]
    
    missing = []
    for module_name, package_name in required_packages:
        try:
            __import__(module_name)
        except ImportError:
            missing.append(package_name)
    
    if missing:
        print(f"❌ Packages manquants: {', '.join(missing)}")
        print(f"   Action: pip install {' '.join(missing)}")
        return False
    
    print("✅ Packages Python OK")
    return True

def main():
    """Fonction principale qui exécute toutes les vérifications."""
    print("🔍 Vérification de l'environnement de développement...")
    print("=" * 60)
    
    checks = [
        check_python(),
        check_packages(),
        check_env(),
        check_dirs()
    ]
    
    print("=" * 60)
    
    if all(checks):
        print("\n🚀 Environnement prêt! Vous pouvez lancer le système avec:")
        print("   python main.py --target_dir ./sandbox")
        return 0
    else:
        print("\n⚠️  Certaines vérifications ont échoué")
        print("   Corrigez les erreurs ci-dessus avant de continuer")
        return 1

if __name__ == "__main__":
    sys.exit(main())