"""
File Tools - Helper functions for file operations and code analysis
"""
import os
import subprocess
import json
from pathlib import Path
from typing import List, Dict, Optional


def read_file(file_path: str) -> Optional[str]:
    """
    Read and return the content of a file
    
    Args:
        file_path: Path to the file to read
        
    Returns:
        File content as string, or None if error
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except Exception as e:
        print(f"❌ Error reading file {file_path}: {e}")
        return None


def write_file(file_path: str, content: str) -> bool:
    """
    Write content to a file
    
    Args:
        file_path: Path to the file to write
        content: Content to write
        
    Returns:
        True if successful, False otherwise
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ File written successfully: {file_path}")
        return True
    except Exception as e:
        print(f"❌ Error writing file {file_path}: {e}")
        return False


def list_python_files(directory: str) -> List[str]:
    """
    List all Python files in a directory (recursively)
    
    Args:
        directory: Path to the directory to scan
        
    Returns:
        List of Python file paths
    """
    python_files = []
    try:
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.py'):
                    full_path = os.path.join(root, file)
                    python_files.append(full_path)
        print(f"📂 Found {len(python_files)} Python files in {directory}")
        return python_files
    except Exception as e:
        print(f"❌ Error listing files in {directory}: {e}")
        return []


def run_pylint(file_path: str) -> Dict:
    """
    Run pylint analysis on a Python file
    
    Args:
        file_path: Path to the Python file to analyze
        
    Returns:
        Dictionary with pylint results (score, issues)
    """
    try:
        # Run pylint with JSON output
        result = subprocess.run(
            ['pylint', file_path, '--output-format=json'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Parse JSON output
        if result.stdout:
            issues = json.loads(result.stdout)
        else:
            issues = []
        
        # Get the score from stderr (pylint puts score there)
        score_line = [line for line in result.stderr.split('\n') if 'rated at' in line.lower()]
        score = 0.0
        if score_line:
            # Extract score from line like "Your code has been rated at 7.50/10"
            try:
                score = float(score_line[0].split('rated at')[1].split('/')[0].strip())
            except:
                score = 0.0
        
        return {
            "score": score,
            "issues": issues,
            "total_issues": len(issues)
        }
    
    except subprocess.TimeoutExpired:
        print(f"⏱️ Pylint timeout for {file_path}")
        return {"score": 0.0, "issues": [], "total_issues": 0, "error": "timeout"}
    except json.JSONDecodeError:
        print(f"⚠️ Could not parse pylint output for {file_path}")
        return {"score": 0.0, "issues": [], "total_issues": 0, "error": "parse_error"}
    except Exception as e:
        print(f"❌ Error running pylint on {file_path}: {e}")
        return {"score": 0.0, "issues": [], "total_issues": 0, "error": str(e)}


def run_pytest(file_path: str) -> Dict:
    """
    Run pytest on a Python test file
    
    Args:
        file_path: Path to the test file
        
    Returns:
        Dictionary with test results (passed, failed, output)
    """
    try:
        # Run pytest with verbose output
        result = subprocess.run(
            ['pytest', file_path, '-v', '--tb=short'],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        # Parse output
        output = result.stdout + result.stderr
        
        # Check if tests passed
        passed = result.returncode == 0
        
        # Count passed/failed tests
        passed_count = output.count(' PASSED')
        failed_count = output.count(' FAILED')
        
        return {
            "passed": passed,
            "passed_count": passed_count,
            "failed_count": failed_count,
            "output": output,
            "return_code": result.returncode
        }
    
    except subprocess.TimeoutExpired:
        print(f"⏱️ Pytest timeout for {file_path}")
        return {
            "passed": False,
            "passed_count": 0,
            "failed_count": 0,
            "output": "Test execution timeout",
            "error": "timeout"
        }
    except Exception as e:
        print(f"❌ Error running pytest on {file_path}: {e}")
        return {
            "passed": False,
            "passed_count": 0,
            "failed_count": 0,
            "output": str(e),
            "error": str(e)
        }


def get_file_info(file_path: str) -> Dict:
    """
    Get basic information about a file
    
    Args:
        file_path: Path to the file
        
    Returns:
        Dictionary with file info (size, lines, name)
    """
    try:
        path = Path(file_path)
        content = read_file(file_path)
        
        if content is None:
            return {"error": "Could not read file"}
        
        return {
            "name": path.name,
            "path": str(path.absolute()),
            "size_bytes": path.stat().st_size,
            "line_count": len(content.split('\n')),
            "exists": path.exists()
        }
    except Exception as e:
        print(f"❌ Error getting file info for {file_path}: {e}")
        return {"error": str(e)}


# Test the tools if run directly
if __name__ == "__main__":
    print("🧪 Testing file tools...")
    
    # Test list files
    files = list_python_files("./src")
    print(f"Found {len(files)} Python files")
    
    # Test read file
    if files:
        content = read_file(files[0])
        if content:
            print(f"✅ Successfully read {files[0]}")