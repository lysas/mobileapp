import subprocess
import time
import sys
import os
import signal

def is_port_open(host, port):
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1)
    try:
        s.connect((host, port))
        s.close()
        return True
    except:
        return False

def main():
    print("========================================")
    print("      AUTOMATED SYSTEM TEST RUNNER      ")
    print("========================================")
    
    # KIll any existing python processes for uvicorn roughly (optional, disabled for safety, rely on port check)
    
    print("\n[1/3] Starting Backend Server (Uvicorn)...")
    # Start uvicorn as a subprocess. Using sys.executable ensures we use the same venv.
    # We redirect output to avoid clutter, unless debugging is needed.
    server_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
        cwd=os.getcwd(),
        # stdout=subprocess.DEVNULL, 
        # stderr=subprocess.PIPE,  # Capture stderr for errors
        creationflags=subprocess.CREATE_NEW_CONSOLE # Try to give it its own window/process group on Windows
    )

    print(f"      Server process started with PID: {server_process.pid}")
    print("      Waiting for Localhost:8000 to allow connections...")

    # Wait up to 20 seconds for port to open
    server_ready = False
    for i in range(20):
        if is_port_open("127.0.0.1", 8000):
            server_ready = True
            break
        time.sleep(1)
        print(".", end="", flush=True)
    print()

    if not server_ready:
        print("\n❌ CRITICAL: Server failed to bind to port 8000 in time.")
        print("   Possible causes: Port in use, missing dependencies, or syntax error in app.")
        print("   Attempting to kill process...")
        server_process.kill()
        return

    print("\n✅ CONNECTION ESTABLISHED! Server is running.")

    print("\n[2/3] Running Validation Script (test_robust.py)...")
    print("----------------------------------------")
    try:
        # Run test_robust.py
        result = subprocess.run([sys.executable, "test_robust.py"], check=False)
        
        if result.returncode == 0:
            print("----------------------------------------")
            print("\n✅ ALL TESTS PASSED.")
            print("   The system is FULLY FUNCTIONAL.")
        else:
            print("\n❌ TESTS FAILED.")
    except Exception as e:
        print(f"\n❌ Execution Error: {e}")
    finally:
        print("\n[3/3] Shutting down Server...")
        try:
            # kill the server
            server_process.terminate()
            # server_process.kill() # Force kill if necessary
        except:
            pass
        print("      Done.")

if __name__ == "__main__":
    main()
