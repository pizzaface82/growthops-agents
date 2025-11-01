from src.digest import run_digest

if __name__ == "__main__":
    result = run_digest()
    print("=== SUMMARY ===")
    print(result["summary"])
import sys, pathlib
# Ensure this folder is on sys.path when running "python main.py"
sys.path.append(str(pathlib.Path(__file__).parent.resolve()))

from src.digest import run_digest

if __name__ == "__main__":
    result = run_digest()
    print("=== SUMMARY ===")
    print(result["summary"])
