import subprocess
import sys
import os

print(f"Running pip install with {sys.executable}")

cmd = [sys.executable, "-m", "pip", "install", "google-genai", "--force-reinstall", "--no-cache-dir"]

try:
    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)
    print("Install SUCCESS")
except subprocess.CalledProcessError as e:
    print("Install FAILED")
    print("STDOUT:", e.stdout)
    print("STDERR:", e.stderr)

# Verification
try:
    import google
    print("google path:", google.__path__)
    from google import genai
    print("genai imported successfully:", genai.__file__)
except ImportError as e:
    print("Import Verification Failed:", e)
