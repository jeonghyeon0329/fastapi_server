""" app 선언부 """
from app.middleware.middleware import ip_access
from app.routers import items
from settings import settings
import multiprocessing

""" library 선언부 """
from fastapi import FastAPI
import subprocess
import sys
import os

app = FastAPI()
app.middleware("http")(ip_access)
app.include_router(items.router, prefix="/items", tags=["items"])

if __name__ == "__main__":
    
    host = settings.host
    port = settings.port
    env  = getattr(settings, "app_env", "local")
    
    if env == "local":
        print(
            f"\n{'='*60}\n"
            f" Environment : {env}\n"
            f" Mode        : Uvicorn (reload)\n"
            f" Address     : http://{host}:{port}\n"
            f"{'='*60}\n"
        )
        subprocess.run([
            sys.executable, "-m", "uvicorn", "main:app",
            "--reload", "--host", host, "--port", str(port),
            "--log-level", "debug"
        ])

    else:
        workers = min(multiprocessing.cpu_count() * 2 + 1, 8)
        log_level = "warning"

        if os.name == "nt":
            print("Mode        : Uvicorn (Windows)")
            subprocess.run([
                sys.executable, "-m", "uvicorn", "main:app",
                "--host", host, "--port", str(port),
                "--workers", str(workers),
                "--log-level", log_level
            ])
        else: 
            print("Mode        : Gunicorn + UvicornWorker (Linux)")
            subprocess.run([
                "gunicorn", "main:app",
                "-k", "uvicorn.workers.UvicornWorker",
                "-w", str(workers),
                "-b", f"{host}:{port}",
                "--log-level", log_level,
                "--access-logfile", "-"  # 표준출력
            ])