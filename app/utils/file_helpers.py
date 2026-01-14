from pathlib import Path

def save_uploaded_file(upload_dir: Path, upload_file) -> Path:
    upload_dir.mkdir(exist_ok=True)
    file_path = upload_dir / upload_file.filename
    with open(file_path, "wb") as buffer:
        buffer.write(upload_file.file.read())
    return file_path
