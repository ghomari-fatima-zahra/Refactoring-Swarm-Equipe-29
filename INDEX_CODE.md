#  INDEX COMPLET DU CODE - PROJET SWARM

## FICHIERS PRINCIPAUX À OUVRIR

### 1. Point d'entrée
- **`main.py`** - Point d'entrée principal du système

### 2. Orchestrateur
- **`src/swarm.py`** - Classe RefactoringSwarm qui coordonne les agents

### 3. Agents (dans `src/agents/`)
- **`src/agents/auditor.py`** - Agent qui analyse le code
- **`src/agents/fixer.py`** - Agent qui corrige le code
- **`src/agents/judge.py`** - Agent qui valide avec des tests

### 4. Outils (dans `src/tools/`)
- **`src/tools/file_handler.py`** - Gestion sécurisée des fichiers

### 5. Utilitaires (dans `src/utils/`)
- **`src/utils/logger.py`** - Système de logging

### 6. Prompts (dans `prompts/`)
- **`prompts/auditor_prompt.txt`** - Prompt pour l'auditeur
- **`prompts/fixer_prompt.txt`** - Prompt pour le correcteur

### 7. Configuration
- **`requirements.txt`** - Dépendances Python
- **`setup.py`** - Configuration setuptools
- **`check_setup.py`** - Script de vérification de l'environnement

### 8. Code de test (dans `sandbox/`)
- **`sandbox/messy_code.py`** - Code à corriger  ici vous poser votre code de test 
- **`sandbox/test_messy_code.py`** - Tests générés

### 9. Tests unitaires (dans `tests/`)
- **`tests/test_fixer_agent.py`** - Tests pour FixerAgent

### 10. Scripts (dans `src/scripts/`)
- **`src/scripts/validate_logs.py`** - Validation des logs

### 11. Logs
- **`logs/experiment_data.json`** - Historique des exécutions

---

##  STRUCTURE COMPLÈTE DU PROJET

```
swarm/
├── main.py                    ← POINT D'ENTRÉE
├── requirements.txt
├── setup.py
├── check_setup.py
├── README.md
│
├── src/
│   ├── __init__.py
│   ├── swarm.py              ← ORCHESTRATEUR PRINCIPAL
│   │
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── auditor.py        ← AGENT AUDITEUR
│   │   ├── fixer.py          ← AGENT CORRECTEUR
│   │   └── judge.py          ← AGENT JUGE
│   │
│   ├── tools/
│   │   ├── __init__.py
│   │   └── file_handler.py   ← GESTION FICHIERS
│   │
│   ├── utils/
│   │   └── logger.py         ← SYSTÈME DE LOGGING
│   │
│   └── scripts/
│       └── validate_logs.py  ← VALIDATION LOGS
│
├── prompts/
│   ├── auditor_prompt.txt    ← PROMPT AUDITEUR
│   └── fixer_prompt.txt      ← PROMPT CORRECTEUR
│
├── sandbox/
│   ├── messy_code.py         ← CODE À CORRIGER
│   └── test_messy_code.py    ← TESTS GÉNÉRÉS
│
├── tests/
│   └── test_fixer_agent.py   ← TESTS UNITAIRES
│
└── logs/
    └── experiment_data.json   ← LOGS D'EXPÉRIMENTATION
```

---

##  COMMENT OUVRIR LES FICHIERS DANS VOTRE IDE

1. **Dans l'explorateur de fichiers** (panneau gauche) :
   - Cliquez sur le dossier `swarm`
   - Naviguez dans les dossiers `src/`, `prompts/`, `sandbox/`, etc.
   - Double-cliquez sur un fichier `.py` pour l'ouvrir

2. **Raccourci clavier** :
   - `Ctrl + P` (ou `Cmd + P` sur Mac) pour rechercher un fichier
   - Tapez le nom du fichier (ex: "swarm.py", "auditor.py")

3. **Ouvrir directement** :
   - `Ctrl + O` pour ouvrir un fichier
   - Naviguez jusqu'au fichier souhaité

---

## 📝 FICHIERS À LIRE EN PRIORITÉ

1. **`main.py`** - Comprendre comment le système démarre
2. **`src/swarm.py`** - Comprendre le flux principal
3. **`src/agents/auditor.py`** - Voir comment l'analyse fonctionne
4. **`src/agents/fixer.py`** - Voir comment les corrections sont appliquées
5. **`src/agents/judge.py`** - Voir comment les tests sont générés/exécutés

---

##  COMMENT TESTER LE CODE

### 1. Vérifier l'environnement
```bash
python check_setup.py
```
(Vérifie Python 3.10/3.11, .env avec GROQ_API_KEY, packages.)

### 2. Tests du sandbox (code à corriger)
```bash
cd sandbox
python -m pytest test_messy_code.py -v
```
Ou depuis la racine :
```bash
python -m pytest sandbox/test_messy_code.py -v
```

### 3. Analyse statique (sans exécuter le swarm)
```bash
python test_code_analysis.py
```
(Vérifie la syntaxe, les imports, la cohérence code/tests.)

### 4. Lancer le système complet
```bash
python main.py --target_dir sandbox
```

---

##  ÉTAT ACTUEL

- **sandbox/messy_code.py** contient `add` et `subtract` → cohérent avec **test_messy_code.py**.
- Si les tests pytest passent, le swarm peut terminer sans boucler.
