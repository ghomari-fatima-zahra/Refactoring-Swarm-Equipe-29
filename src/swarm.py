import os
import json
from src.agents.auditor import AuditorAgent
from src.agents.fixer import FixerAgent
from src.agents.judge import JudgeAgent

class RefactoringSwarm:
    def __init__(self, target_dir):
        self.target_dir = target_dir
        self.auditor = AuditorAgent()
        self.fixer = FixerAgent()
        self.judge = JudgeAgent()
        self.last_test_error = ""

    def run(self):
        print(f"🔍 Starting refactoring on: {self.target_dir}")
        print("=" * 60)

        for i in range(10):
            print(f"\n🔄 [Iteration {i+1}/10]")

            # 🔎 Audit only if no recent test error
            if not self.last_test_error:
                print("  🕵️  Auditing code...")
                audit_response = self.auditor.analyze(self.target_dir)
            else:
                # Treat test failure as a debugging task
                print("  🐞 Debugging test failure...")
                audit_response = json.dumps([{
                    "file": "unknown",
                    "line": 0,
                    "issue_type": "TEST_FAILURE",
                    "description": f"Test failed with error:\n{self.last_test_error[:300]}"
                }])

            # 🛠️ Fix
            print("  🛠️  Applying fixes...")
            self.fixer.fix(self.target_dir, audit_response)
            self.last_test_error = ""  # Reset after fix

            # ✅ Validate
            print("  🧪 Running tests...")
            success, error_output = self.judge.validate_with_error(self.target_dir)
            if success:
                print("\n" + "=" * 60)
                print("🎉 SUCCESS! All tests passed. Refactoring complete.")
                return
            else:
                self.last_test_error = error_output
                print("  ❌ Tests failed. Using error to guide next fix...")

        print("\n" + "=" * 60)
        print("⚠️  MAX ITERATIONS REACHED (10/10)")
        if self.last_test_error:
            print("\nLast test error:")
            print(self.last_test_error[:500])
        print("\n📂 Check logs/experiment_data.json for full trace.")