import sys
import traceback

print("Attempting to import app.main...")
try:
    from app.main import app
    print("Successfully imported app.main")
except Exception:
    print("Failed to import app.main")
    traceback.print_exc()
