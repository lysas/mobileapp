import subprocess
import time
import urllib.request
import json
import socket
import os

def is_port_open(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

print("1. Checking Port 8000...")
if not is_port_open(8000):
    print("   Port 8000 is CLOSED. Starting Uvicorn...")
    # Start Uvicorn
    proc = subprocess.Popen(
        ["python", "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    print(f"   Uvicorn started with PID {proc.pid}. Waiting 5s...")
    time.sleep(5)
else:
    print("   Port 8000 is OPEN.")

print("2. Running Test Request...")
try:
    # Minimal Test Payload
    boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
    body = (
        f"--{boundary}\r\n"
        'Content-Disposition: form-data; name="answer_key"\r\n\r\n'
        "1:A\r\n"
        f"--{boundary}\r\n"
        'Content-Disposition: form-data; name="file"; filename="test.txt"\r\n'
        'Content-Type: text/plain\r\n\r\n'
        "dummy content\r\n"
        f"--{boundary}--\r\n"
    ).encode('utf-8')
    
    req = urllib.request.Request("http://127.0.0.1:8000/mcq/evaluate", data=body)
    req.add_header('Content-Type', f'multipart/form-data; boundary={boundary}')
    
    with urllib.request.urlopen(req) as res:
        print(f"   Response Code: {res.getcode()}")
        data = json.load(res)
        print(f"   Response Body: {data}")
        # We expect a failure or success, but getting ANY json means the API is UP.
        print("✅ SYSTEMS CHECK PASSED: API is responsive.")
        
except Exception as e:
    print(f"❌ API REQUEST FAILED: {e}")
    # Run robust test if possible
    
print("3. Attempting Robust Test...")
try:
    subprocess.run(["python", "test_robust.py"], check=True)
except Exception as e:
    print(f"   Robust test script failed: {e}")
