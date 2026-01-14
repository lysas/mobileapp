import sys
import os
from google import genai
try:
    from google.genai import errors as genai_errors
    print("Successfully imported google.genai.errors")
    print("ClientError:", genai_errors.ClientError)
    print("ClientError bases:", genai_errors.ClientError.__bases__)
    print("APIError bases:", genai_errors.APIError.__bases__)
except ImportError as e:
    print("Failed to import google.genai.errors:", e)
except Exception as e:
    print("Error:", e)
