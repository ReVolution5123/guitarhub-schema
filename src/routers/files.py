from fastapi import APIRouter
from src.services.file_service import FileService

router = APIRouter(prefix="/files", tags=["files"])

@router.get("/electric-guitar")
def get_electric_guitar():
    service = FileService("electric_guitar")
    return service.stream_file()
