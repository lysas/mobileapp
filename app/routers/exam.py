from fastapi import APIRouter, UploadFile, File
from pathlib import Path
import shutil

# Initialize router
router = APIRouter()

# Directory to store uploaded answer sheets
UPLOAD_DIR = Path("uploaded_sheets")
UPLOAD_DIR.mkdir(exist_ok=True)  # Create if not exists

@router.post("/upload-sheet")
async def upload_sheet(file: UploadFile = File(...)):
    """
    Endpoint to upload student answer sheet images.
    Currently saves files to the server. OCR integration comes later.
    """
    try:
        # Full path to save uploaded file
        file_path = UPLOAD_DIR / file.filename

        # Save uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return {
            "filename": file.filename,
            "message": "Upload successful",
            "path": str(file_path)
        }

    except Exception as e:
        return {
            "filename": file.filename if 'file' in locals() else "unknown",
            "message": f"Upload failed: {str(e)}"
        }
