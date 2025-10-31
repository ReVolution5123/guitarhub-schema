from fastapi import FastAPI
from src.routers import schemas, defaults, files

app = FastAPI(title="GuitarHub schema & models API")

routers = [ defaults.router, files.router, schemas.router, ]
for router in routers:
    app.include_router(router)


