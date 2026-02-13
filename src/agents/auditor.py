"""
Agent Auditeur - Analyse le code pour détecter les problèmes.
Utilise Groq (Llama) pour une analyse intelligente du code Python.
"""
import os
import json
import re
from string import Template
from groq import Groq
from dotenv import load_dotenv
from src.utils.logger import log_experiment, ActionType

load_dotenv()

# Chargement du prompt système
with open("prompts/auditor_prompt.txt", "r", encoding="utf-8") as f:
    AUDITOR_PROMPT_TEXT = f.read()

class AuditorAgent:
    """
    Agent responsable de l'analyse du code.
    Détecte les erreurs de syntaxe, les mauvaises pratiques et les bugs potentiels.
    """
    
    def __init__(self):
        """Initialise l'agent avec le client Groq et le modèle Llama."""
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model_name = "llama-3.3-70b-versatile"

    def analyze(self, target_dir: str) -> str:
        """
        Analyse tous les fichiers Python dans le répertoire cible.
        
        Args:
            target_dir: Répertoire contenant le code à analyser
            
        Returns:
            JSON string contenant la liste des problèmes détectés
        """
        print(f"  📂 Collecte des fichiers Python dans {target_dir}...")
        
        # Collecte de tous les fichiers Python non-test
        code_snippets = []
        for root, _, files in os.walk(target_dir):
            for file in files:
                if file.endswith(".py") and not file.startswith("test_"):
                    path = os.path.join(root, file)
                    try:
                        with open(path, "r", encoding="utf-8") as f:
                            content = f.read()
                            if content.strip():
                                code_snippets.append(f"# FILE: {file}\n{content}")
                    except Exception as e:
                        print(f"  ⚠️  Erreur lecture {file}: {e}")
        
        if not code_snippets:
            print("  ℹ️  Aucun fichier Python trouvé")
            return "[]"
        
        print(f"  📄 {len(code_snippets)} fichier(s) à analyser")
        
        # Préparation du prompt avec tout le code
        full_code = "\n\n".join(code_snippets)
        
        # Remplacement du placeholder {code} dans le prompt
        prompt = AUDITOR_PROMPT_TEXT.replace("{code}", full_code)
        
        try:
            # Appel à l'API Groq avec le modèle Llama
            print("  🤖 Envoi de la requête à Groq (Llama)...")
            print(f"  📝 Extrait du code envoyé (50 premiers caractères): {full_code[:50]}...")
            
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.model_name,
                temperature=0.1  # Basse température pour plus de cohérence
            )
            raw_response = response.choices[0].message.content
            
            print(f"  📥 Réponse brute de Groq (100 premiers caractères): {raw_response[:100]}...")
            
            # Nettoyage de la réponse
            cleaned = self._clean_json_response(raw_response)
            
            # Validation du JSON
            try:
                issues = json.loads(cleaned)
                if not isinstance(issues, list):
                    print("  ⚠️  Réponse non-liste, utilisation de []")
                    cleaned = "[]"
                else:
                    print(f"  ✅ {len(issues)} problème(s) détecté(s)")
                    # Afficher les premiers problèmes détectés
                    if len(issues) > 0:
                        print(f"  🔍 Premier problème: {issues[0]}")
            except json.JSONDecodeError as e:
                print(f"  ⚠️  JSON invalide de l'auditeur: {e}")
                print(f"  📝 Réponse nettoyée (200 premiers caractères): {cleaned[:200]}...")
                cleaned = "[]"
            
            # Logging pour l'analyse scientifique
            log_experiment(
                agent_name="AuditorAgent",
                model_used=self.model_name,
                action=ActionType.ANALYSIS,
                details={
                    "target_dir": target_dir,
                    "input_prompt": prompt[:1000],  # Tronqué pour le log
                    "output_response": cleaned,
                    "files_analyzed": len(code_snippets),
                    "raw_response_preview": raw_response[:500]
                }
            )
            
            return cleaned
            
        except Exception as e:
            print(f"  ❌ Erreur lors de l'analyse: {e}")
            log_experiment(
                agent_name="AuditorAgent",
                model_used=self.model_name,
                action=ActionType.ANALYSIS,
                details={
                    "target_dir": target_dir,
                    "input_prompt": prompt[:1000] if 'prompt' in locals() else "ERROR: prompt not created",
                    "output_response": f"ERROR: {str(e)}",
                    "files_analyzed": len(code_snippets)
                },
                status="FAILED"
            )
            return "[]"

    def _clean_json_response(self, response: str) -> str:
        """
        Nettoie la réponse du LLM pour extraire uniquement le JSON valide.
        Les modèles Llama ont tendance à entourer le JSON de blocs markdown.
        
        Args:
            response: Réponse brute du modèle
            
        Returns:
            JSON nettoyé sous forme de string
        """
        cleaned = response.strip()
        
        # Suppression des blocs de code markdown que Llama ajoute souvent
        if "```json" in cleaned:
            cleaned = cleaned.split("```json")[1].split("```")[0]
        elif "```" in cleaned:
            parts = cleaned.split("```")
            if len(parts) >= 3:
                cleaned = parts[1]
        
        cleaned = cleaned.strip()
        
        # Si la réponse contient du texte avant/après le JSON, extraire le JSON
        json_match = re.search(r'\[.*\]', cleaned, re.DOTALL)
        if json_match:
            cleaned = json_match.group(0)
        
        return cleaned