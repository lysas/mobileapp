import os
import urllib.request
import json
import sys
from PIL import Image, ImageDraw, ImageFont

# 1. CONSTANTS
BASE_URL = "http://127.0.0.1:8000"
TEST_IMG_PATH = "temp_mcq_test.png"

# 2. GENERATE IMAGE
def create_test_image():
    print("Creating synthetic test image...")
    img = Image.new('RGB', (400, 400), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except IOError:
        font = ImageFont.load_default()

    text_content = "STUDENT ANSWER SHEET\n--------------------\n1. A\n2. B\n3. C"
    d.text((50, 50), text_content, fill=(0, 0, 0), font=font)
    img.save(TEST_IMG_PATH)
    print(f"Image saved to {TEST_IMG_PATH}")

# 3. TEST API
def test_api():
    print("\n--- Testing MCQ API ---")
    answer_key = "1:A, 2:B, 3:C"
    boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
    
    # Read file
    with open(TEST_IMG_PATH, "rb") as f:
        file_bytes = f.read()

    # Construct Multipart Body manually (urllib is low-level)
    body = []
    body.append(f"--{boundary}".encode())
    body.append('Content-Disposition: form-data; name="file"; filename="test.png"'.encode())
    body.append('Content-Type: image/png'.encode())
    body.append(b'')
    body.append(file_bytes)
    
    body.append(f"--{boundary}".encode())
    body.append('Content-Disposition: form-data; name="answer_key"'.encode())
    body.append(b'')
    body.append(answer_key.encode())
    body.append(f"--{boundary}--".encode())
    body.append(b'')
    
    payload = b"\r\n".join(body)
    
    req = urllib.request.Request(f"{BASE_URL}/mcq/evaluate", data=payload)
    req.add_header('Content-Type', f'multipart/form-data; boundary={boundary}')
    
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            print("\nRESPONSE JSON:")
            print(result)
            
            with open("test_result.txt", "w") as f:
                if result.get("score") == 3:
                    msg = "SUCCESS: Perfect score received."
                    print(f"\n✅ {msg}")
                    f.write(msg)
                else:
                    msg = f"FAILURE: Check score. Got {result.get('score')}"
                    print(f"\n❌ {msg}")
                    f.write(msg)
                    sys.exit(1)
                
    except urllib.error.URLError as e:
        msg = f"CONNECTION ERROR: {e}. Is uvicorn running?"
        print(f"\n❌ {msg}")
        with open("test_result.txt", "w") as f:
            f.write(msg)
        sys.exit(1)


# 4. EXPLAIN FORMATS
def explain_formats():
    print("\n\n=== ANSWER KEY FORMATS ===")
    print("The 'answer_key' string supports flexible formatting.")
    print("Core pattern: [Question Number] [Separator] [Answer Option (A-D)]")
    print("\nExamples of VALID inputs:")
    print("  \"1 A 2 B 3 C\"           (Spaces)")
    print("  \"1:A, 2:B, 3:C\"         (Colons & Commas)")
    print("  \"1-A, 2-B, 3-C\"         (Dashes)")
    print("  \"1) A  2) B  3) C\"      (Parentheses)")
    print("\nAlso supports converting Roman Numeral answers:")
    print("  \"1. i\"   -> Interpreted as 1 A")
    print("  \"2. ii\"  -> Interpreted as 2 B")

if __name__ == "__main__":
    create_test_image()
    test_api()
    explain_formats()
    
    # Cleanup
    if os.path.exists(TEST_IMG_PATH):
        try:
            os.remove(TEST_IMG_PATH)
            pass
        except:
            pass
