from fastapi import FastAPI
from src.routers import schema, defaults

app = FastAPI(title="GuitarHub schema & models API")
app.include_router(schema.router)
app.include_router(defaults.router)

