import json
import os
from string import Template
from groq import Groq
from dotenv import load_dotenv
from src.utils.logger import log_experiment, ActionType
from src.tools.file_handler import safe_write_file

load_dotenv()

with open("prompts/fixer_prompt.txt", "r", encoding="utf-8") as f:
    FIXER_PROMPT = Template(f.read())

class FixerAgent:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "llama-3.3-70b-versatile"

    def fix(self, target_dir, audit_response):
        try:
            issues = json.loads(audit_response)
        except:
            return

        for issue in issues[:2]:
            filename = issue.get("file")
            if not filename or not filename.endswith(".py"):
                continue

            filepath = os.path.join(target_dir, filename)
            if not os.path.exists(filepath):
                continue

            with open(filepath, "r", encoding="utf-8") as f:
                original_code = f.read()

            prompt = FIXER_PROMPT.substitute(
                issue_description=issue.get("description", "Improve code quality"),
                original_code=original_code
            )

            fixed_code = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.model,
                temperature=0.0
            ).choices[0].message.content

            if fixed_code.startswith("```python"):
                fixed_code = fixed_code[9:]
            if fixed_code.endswith("```"):
                fixed_code = fixed_code[:-3]

            log_experiment(
                agent_name="FixerAgent",
                model_used=self.model,
                action=ActionType.FIX,
                details={"file": filename, "input_prompt": prompt, "output_response": fixed_code}
            )

            safe_write_file(filepath, fixed_code.strip())