from app.utils.ocr import process_answer_ocr
import os

# Use the existing file in uploaded_sheets
# The filename is long, so we'll use the one we found
filename = "Copy of Copy of Blue And Green Modern Happy New Year Poster.png"
file_path = os.path.join("uploaded_sheets", filename)

output_json = "output/json"
output_imgs = "output/images"
user_id = 101

if not os.path.exists(file_path):
    print(f"Error: File not found at {file_path}")
    # Fallback to listing directory to debug
    print(f"Contents of uploaded_sheets: {os.listdir('uploaded_sheets')}")
else:
    print(f"Processing {file_path}...")
    result = process_answer_ocr(file_path, output_json, output_imgs, user_id)
    print("Result:", result)
