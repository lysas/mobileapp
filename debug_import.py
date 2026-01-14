import sys
import os

print("Python Executable:", sys.executable)
print("CWD:", os.getcwd())
print("sys.path:", sys.path)

try:
    import google
    print("Found 'google' package at:", google.__path__)
    print("google file:", google.__file__)
except ImportError as e:
    print("Could not import 'google':", e)
except Exception as e:
    print("Error importing 'google':", e)

try:
    from google import genai
    print("SUCCESS: Imported genai at:", genai.__file__)
except ImportError as e:
    print("FAILURE: Could not import 'genai' from 'google':", e)
    # Check what IS in google
    if 'google' in sys.modules:
        import google
        print("Contents of google package:", dir(google))
