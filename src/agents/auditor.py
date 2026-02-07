import os
import json
from string import Template
from groq import Groq
from dotenv import load_dotenv
from src.utils.logger import log_experiment, ActionType

load_dotenv()

with open("prompts/auditor_prompt.txt", "r", encoding="utf-8") as f:
    AUDITOR_PROMPT = Template(f.read())

class AuditorAgent:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "llama-3.3-70b-versatile"

    def analyze(self, target_dir):
        code_snippets = []
        for root, _, files in os.walk(target_dir):
            for file in files:
                if file.endswith(".py"):
                    path = os.path.join(root, file)
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()
                        if content.strip():
                            code_snippets.append(f"# FILE: {file}\n{content}")
        
        if not code_snippets:
            return "[]"

        full_code = "\n\n".join(code_snippets)
        prompt = AUDITOR_PROMPT.substitute(code=full_code)

        response = self.client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=self.model,
            temperature=0.1
        ).choices[0].message.content

        # Clean JSON
        cleaned = response.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        try:
            json.loads(cleaned)
        except:
            cleaned = "[]"

        log_experiment(
            agent_name="AuditorAgent",
            model_used=self.model,
            action=ActionType.ANALYSIS,
            details={"target_dir": target_dir, "input_prompt": prompt, "output_response": cleaned}
        )
        return cleaned