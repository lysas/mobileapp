import sys
print(f"Python: {sys.executable}")
try:
    import fastapi
    print("FastAPI: OK")
    import uvicorn
    print("Uvicorn: OK")
    import google.genai
    print("Google GenAI: OK")
    import openai
    print("OpenAI: OK")
    import dotenv
    print("DotEnv: OK")
    
    from app.main import app
    print("App Import: OK")
    
except ImportError as e:
    print(f"MISSING DEPENDENCY: {e}")
except Exception as e:
    print(f"STARTUP ERROR: {e}")
