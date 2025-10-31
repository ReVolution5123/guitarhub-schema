import os
from fastapi import HTTPException
from fastapi.responses import StreamingResponse

class FileService:
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    DATA_DIR = os.path.join(BASE_DIR, "src", "data")
    ALLOWED_FILES = {"electric_guitar"}  # whitelist
    CHUNK_SIZE = 1024 * 1024  # 1 MB

    def __init__(self, filename: str):
        if filename not in self.ALLOWED_FILES:
            raise HTTPException(status_code=400, detail=f"File '{filename}' not allowed")

        self.file_path = os.path.join(self.DATA_DIR, f"{filename}.glb")

        if not os.path.exists(self.file_path):
            raise HTTPException(status_code=404, detail=f"File '{filename}.glb' not found")

        self.file_size = os.path.getsize(self.file_path)

    def stream_file(self) -> StreamingResponse:
        def iterfile():
            with open(self.file_path, "rb") as f:
                while chunk := f.read(self.CHUNK_SIZE):
                    yield chunk
        headers = {
            "Content-Type": "application/octet-stream",
            "Content-Length": str(self.file_size),
            "Accept-Ranges": "none",
        }

        return StreamingResponse(iterfile(), headers=headers)
