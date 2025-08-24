""" app 선언부 """
from app.middleware.middleware import ip_access
from app.routers import items
from settings import settings 

""" library 선언부 """
from fastapi import FastAPI
import uvicorn

app = FastAPI()
app.middleware("http")(ip_access)
app.include_router(items.router, prefix="/items", tags=["items"])

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.reload,
        reload_dirs=["app", "."],
        log_level="debug" if settings.DEBUG else "info",
    )
