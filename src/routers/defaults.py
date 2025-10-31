from fastapi import APIRouter, HTTPException, status, Body
from fastapi.responses import JSONResponse

from src.services.schema_service import SchemaService

router = APIRouter(
    prefix="/defaults",
    tags=["defaults"],
)

@router.get("/", summary="Get default guitar configuration")
def get_default():
    schema = SchemaService()
    return schema.defaults


@router.post("/validate", summary="Validate object against schema")
def validate(
    payload: dict = Body(..., example=SchemaService().defaults)
):
    schema = SchemaService()
    try:
        schema.validate(payload)
        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content=None)
    except ValueError as e:
        errors = str(e).replace("Validation failed:\n- ", "").split("\n- ")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "Validation failed", "errors": errors}
        )
