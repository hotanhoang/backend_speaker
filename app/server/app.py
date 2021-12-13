from fastapi import FastAPI

from routers import user, items,recognition

app = FastAPI()
app.include_router(user.router, prefix="/api")
# app.include_router(items.router, prefix="/api")
# app.include_router(recognition.router, prefix="/api")
