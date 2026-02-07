import os
import subprocess
import sys
from groq import Groq
from dotenv import load_dotenv
from src.utils.logger import log_experiment, ActionType
from src.tools.file_handler import safe_write_file

load_dotenv()

class JudgeAgent:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        # ✅ Use a supported model per Groq's deprecation policy
        self.model = "llama-3.1-8b-instant"  # Still valid as of Feb 2026

    def validate(self, target_dir):
        """Legacy-compatible wrapper."""
        success, _ = self.validate_with_error(target_dir)
        return success

    def validate_with_error(self, target_dir):
        """
        Runs pytest on the first test file and returns (success: bool, error_output: str).
        Ensures a test exists before running.
        """
        # List non-test Python files
        py_files = [
            f for f in os.listdir(target_dir)
            if f.endswith(".py") and not f.startswith("test_")
        ]
        
        if not py_files:
            print("⚠️ No Python files to refactor.")
            return True, ""

        main_file = py_files[0]
        test_file = f"test_{main_file}"
        test_path = os.path.join(target_dir, test_file)

        # Always ensure a test exists
        if not os.path.exists(test_path):
            print(f"🔧 Generating minimal test for {main_file}...")
            self._generate_minimal_test(target_dir, main_file, test_file)

        # Run pytest on the specific test file
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", test_path, "-v", "--tb=short"],
                capture_output=True,
                text=True,
                timeout=20,
                cwd=target_dir
            )

            success = (result.returncode == 0)
            output = result.stdout + result.stderr

            log_experiment(
                agent_name="JudgeAgent",
                model_used="pytest",
                action=ActionType.DEBUG,
                details={
                    "target_dir": target_dir,
                    "input_prompt": f"Run pytest on {test_file}",
                    "output_response": output
                },
                status="SUCCESS" if success else "FAILED"
            )
            return success, output

        except Exception as e:
            error_str = str(e)
            log_experiment(
                agent_name="JudgeAgent",
                model_used="pytest",
                action=ActionType.DEBUG,
                details={
                    "target_dir": target_dir,
                    "input_prompt": f"Run pytest on {test_file}",
                    "output_response": error_str
                },
                status="ERROR"
            )
            return False, error_str

    def  _generate_minimal_test(self, target_dir, py_file, test_file):
        #    def _generate_minimal_test(self, target_dir, py_file, test_file):
        # Use only safe characters
        module_name = py_file[:-3]  # e.g., "messy_code"
        
        # Read source to get first function
        py_path = os.path.join(target_dir, py_file)
        func_name = "unknown"
        try:
            with open(py_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip().startswith("def "):
                        func_name = line.split("def ")[1].split("(")[0].strip()
                        if func_name.replace("_", "").replace(" ", "").isalnum():
                            break
        except:
            pass

        # Build test with ONLY spaces and \n (no tabs, no fancy quotes)
        lines = [
            "import sys",
            "import os",
            "sys.path.insert(0, os.path.dirname(__file__))",
            "",
            "try:",
            f"    from {module_name} import {func_name}",
            "except Exception as e:",
            "    def test_import_failed():",
            "        assert False, f'Import failed: {str(e)}'",
            "else:",
            f"    def test_{func_name}():",
            "        try:",
            f"            result = {func_name}(1, 2)",
            "            assert result is not None",
            "        except Exception as e:",
            "            assert False, f'Function failed: {str(e)}'",
        ]
        test_code = "\n".join(lines) + "\n"

        test_path = os.path.join(target_dir, test_file)
        # Write with explicit UTF-8, no BOM
        with open(test_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(test_code)

        log_experiment(
            agent_name="JudgeAgent",
            model_used="rule-based",
            action=ActionType.GENERATION,
            details={
                "file_generated": test_file,
                "input_prompt": f"Generate ASCII-safe test for {py_file}",
                "output_response": test_code
            }
        )
        print(f"✅ Created ASCII-safe test: {test_file}")