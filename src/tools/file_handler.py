"""
Module de gestion sécurisée des fichiers.
Empêche l'écriture en dehors du sandbox pour des raisons de sécurité.
"""
import os

def safe_write_file(filepath: str, content: str):
    """
    Écrit un fichier de manière sécurisée dans le sandbox uniquement.
    
    Args:
        filepath: Chemin du fichier à écrire
        content: Contenu à écrire
        
    Raises:
        PermissionError: Si le chemin est en dehors du sandbox
    """
    abs_path = os.path.abspath(filepath)
    sandbox_root = os.path.abspath("sandbox")
    
    # Vérification de sécurité : le fichier doit être dans le sandbox
    if not abs_path.startswith(sandbox_root + os.sep):
        raise PermissionError(f"Accès refusé : écriture interdite en dehors du sandbox ({abs_path})")
    
    # Création du répertoire parent si nécessaire
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    
    # Écriture du fichier
    with open(abs_path, "w", encoding="utf-8") as f:
        f.write(content)

def safe_read_file(filepath: str) -> str:
    """
    Lit un fichier de manière sécurisée.
    
    Args:
        filepath: Chemin du fichier à lire
        
    Returns:
        Contenu du fichier
    """
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()