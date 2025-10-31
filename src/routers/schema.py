from functools import lru_cache

from fastapi import APIRouter

from src.services.schema_service import SchemaService

router = APIRouter(
    prefix="/schema",
    tags=["schema"],
)

@router.get("/", summary="Get default schema")
def get_schema():
    return _get_cached_schema()

# Utils
@lru_cache()
def _get_cached_schema():
    schema = SchemaService()
    return schema.data

