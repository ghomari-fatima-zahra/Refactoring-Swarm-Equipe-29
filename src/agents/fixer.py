"""
Agent Correcteur - Corrige les problèmes détectés dans le code.
Utilise Groq (Llama) pour appliquer des corrections intelligentes.
Applique des corrections MINIMALES et préserve les noms de fonctions.
"""
import json
import os
import ast
import re
from string import Template
from groq import Groq
from dotenv import load_dotenv
from src.utils.logger import log_experiment, ActionType
from src.tools.file_handler import safe_write_file

load_dotenv()

# Chargement du prompt système
with open("prompts/fixer_prompt.txt", "r", encoding="utf-8") as f:
    FIXER_PROMPT = Template(f.read())


def _extract_expected_names_from_issues(issues: list, target_dir: str, filename: str) -> str:
    """
    Extrait les noms de fonctions/variables attendus par le test (ex: add, subtract)
    à partir des erreurs "cannot import name 'X'" ou en lisant le fichier de test.
    """
    expected = set()
    module_name = filename[:-3] if filename.endswith(".py") else filename  # ex: messy_code
    test_filename = f"test_{filename}"
    test_path = os.path.join(target_dir, test_filename)

    # 1) Parser les erreurs "cannot import name 'xxx'"
    for issue in issues:
        desc = (issue.get("description") or "") + (issue.get("issue_type") or "")
        for match in re.finditer(r"cannot import name ['\"]([a-zA-Z_][a-zA-Z0-9_]*)['\"]", desc):
            expected.add(match.group(1))
        for match in re.finditer(r"ImportError[^:]*['\"]([a-zA-Z_][a-zA-Z0-9_]*)['\"]", desc):
            expected.add(match.group(1))

    # 2) Lire le fichier de test pour "from module import x, y, z"
    if os.path.exists(test_path):
        try:
            with open(test_path, "r", encoding="utf-8") as f:
                test_content = f.read()
            # from messy_code import add, subtract
            pattern = rf"from\s+{re.escape(module_name)}\s+import\s+(.+?)(?:\n|$)"
            m = re.search(pattern, test_content)
            if m:
                imports = m.group(1).strip()
                for part in re.split(r"\s*,\s*", imports):
                    part = part.strip().split()[0] if part.strip() else ""
                    if part and part.isidentifier():
                        expected.add(part)
        except Exception:
            pass

    if not expected:
        return ""

    names_list = ", ".join(sorted(expected))
    return (
        f"\n\nIMPORTANT - Le fichier de test attend ces noms exacts (ne PAS les renommer, ex: pas 'addition' à la place de 'add'): {names_list}\n"
    )

class FixerAgent:
    """
    Agent responsable de la correction du code.
    Applique des modifications pour résoudre les problèmes identifiés.
    """
    
    def __init__(self):
        """Initialise l'agent avec le client Groq et le modèle Llama."""
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model_name = "llama-3.3-70b-versatile"

    def fix(self, target_dir: str, audit_response: str):
        """
        Corrige les problèmes détectés dans les fichiers.
        
        Args:
            target_dir: Répertoire contenant le code à corriger
            audit_response: JSON string contenant la liste des problèmes
        """
        try:
            issues = json.loads(audit_response)
            if not issues:
                print("  ℹ️  Aucun problème à corriger")
                return
        except json.JSONDecodeError as e:
            print(f"  ❌ Impossible de parser la réponse de l'auditeur: {e}")
            return
        
        print(f"  🛠️  {len(issues)} problème(s) identifié(s)")
        
        # Regrouper les problèmes par fichier pour une correction plus efficace
        issues_by_file = {}
        for issue in issues:
            filename = issue.get("file", "unknown")
            if filename not in issues_by_file:
                issues_by_file[filename] = []
            issues_by_file[filename].append(issue)
        
        # Corriger chaque fichier
        for filename, file_issues in issues_by_file.items():
            if not filename.endswith(".py"):
                continue
            
            filepath = os.path.join(target_dir, filename)
            if not os.path.exists(filepath):
                print(f"  ⚠️  Fichier non trouvé: {filename}")
                continue
            
            # Limiter à 5 problèmes par fichier et par itération pour éviter de tout casser
            issues_to_fix = file_issues[:5]
            print(f"\n  📝 Correction de {filename} ({len(issues_to_fix)} problèmes)...")
            
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    original_code = f.read()
            except Exception as e:
                print(f"  ❌ Erreur lecture {filename}: {e}")
                continue
            
            # Préparer la description des problèmes pour le LLM
            issues_description = "\n".join([
                f"- Ligne {issue.get('line', '?')}: {issue.get('issue_type', 'Unknown')} - {issue.get('description', '')}"
                for issue in issues_to_fix
            ])

            # Noms attendus par le test (ex: add, subtract) pour ne pas les renommer
            expected_names_section = _extract_expected_names_from_issues(
                issues_to_fix, target_dir, filename
            )

            # Générer le prompt de correction
            prompt = FIXER_PROMPT.substitute(
                issue_description=issues_description,
                original_code=original_code,
                expected_names_section=expected_names_section
            )
            
            try:
                # Appel à l'API Groq pour obtenir le code corrigé
                print(f"  🤖 Génération du code corrigé avec Llama...")
                response = self.client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model=self.model_name,
                    temperature=0.0  # Température 0 pour des corrections déterministes
                )
                fixed_code = response.choices[0].message.content
                
                # Nettoyage de la réponse
                fixed_code = self._clean_code_response(fixed_code)
                
                # Validation de la syntaxe Python avant d'écrire
                syntax_valid = self._validate_python_syntax(fixed_code)
                
                if syntax_valid:
                    # Sauvegarde du fichier corrigé
                    safe_write_file(filepath, fixed_code)
                    print(f"  ✅ {filename} corrigé avec succès")
                else:
                    print(f"  ❌ Code corrigé invalide, conservation de l'original")
                
                # Logging pour l'analyse scientifique
                log_experiment(
                    agent_name="FixerAgent",
                    model_used=self.model_name,
                    action=ActionType.FIX,
                    details={
                        "file": filename,
                        "issues_count": len(issues_to_fix),
                        "issues": issues_to_fix,
                        "input_prompt": prompt[:1000],  # Tronqué pour le log
                        "output_response": fixed_code[:1000],  # Tronqué pour le log
                        "syntax_valid": syntax_valid
                    },
                    status="SUCCESS" if syntax_valid else "FAILED"
                )
                
            except Exception as e:
                print(f"  ❌ Erreur lors de la correction de {filename}: {e}")
                log_experiment(
                    agent_name="FixerAgent",
                    model_used=self.model_name,
                    action=ActionType.FIX,
                    details={
                        "file": filename,
                        "issues_count": len(issues_to_fix),
                        "input_prompt": prompt[:1000],
                        "output_response": f"ERROR: {str(e)}",
                        "syntax_valid": False
                    },
                    status="FAILED"
                )

    def _clean_code_response(self, response: str) -> str:
        """
        Nettoie la réponse du LLM pour extraire uniquement le code Python.
        Llama a tendance à entourer le code de blocs markdown.
        
        Args:
            response: Réponse brute du modèle
            
        Returns:
            Code Python nettoyé
        """
        cleaned = response.strip()
        
        # Suppression des blocs de code markdown
        if "```python" in cleaned:
            cleaned = cleaned.split("```python")[1].split("```")[0]
        elif "```" in cleaned:
            parts = cleaned.split("```")
            if len(parts) >= 2:
                cleaned = parts[1]
        
        return cleaned.strip()

    def _validate_python_syntax(self, code: str) -> bool:
        """
        Valide la syntaxe Python du code avec ast.parse().
        Cela nous garantit que nous n'écrivons jamais du code syntaxiquement incorrect.
        
        Args:
            code: Code Python à valider
            
        Returns:
            True si la syntaxe est valide, False sinon
        """
        try:
            ast.parse(code)
            return True
        except SyntaxError as e:
            print(f"  ⚠️  Erreur de syntaxe détectée: {e}")
            return False