import sys
import os
from dotenv import load_dotenv

def check_python():
    v = sys.version_info
    if not (v.major == 3 and v.minor in (10, 11)):
        print("❌ Python 3.10 or 3.11 required")
        return False
    print("✅ Python version OK")
    return True

def check_env():
    if not os.path.exists(".env"):
        print("❌ Copy .env.example to .env and add your GROQ_API_KEY")
        return False
    load_dotenv()
    if not os.getenv("GROQ_API_KEY"):
        print("❌ GROQ_API_KEY missing in .env")
        return False
    print("✅ .env OK")
    return True

def check_dirs():
    for d in ["src", "prompts", "sandbox", "logs"]:
        os.makedirs(d, exist_ok=True)
    print("✅ Directories OK")
    return True

if __name__ == "__main__":
    if all([check_python(), check_env(), check_dirs()]):
        print("\n🚀 Ready to run!")
    else:
        sys.exit(1)