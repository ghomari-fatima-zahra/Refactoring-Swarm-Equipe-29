import os

def safe_write_file(filepath: str, content: str):
    abs_path = os.path.abspath(filepath)
    sandbox_root = os.path.abspath("sandbox")
    if not abs_path.startswith(sandbox_root + os.sep):
        raise PermissionError("Write access denied outside sandbox")
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    with open(abs_path, "w", encoding="utf-8") as f:
        f.write(content)