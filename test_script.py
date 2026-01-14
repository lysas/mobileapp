from app.utils.ocr import process_answer_ocr
import os

# Path of the uploaded sheet
file_path = "uploaded_sheets\\Black and Gold Illustrative Happy New Year Instagram Story.png"

# Output directories
output_json = "output/json"
output_imgs = "output/images"

# Example user id
user_id = 101

# Run OCR / marks processing
result = process_answer_ocr(file_path, output_json, output_imgs, user_id)
print("Result:", result)
