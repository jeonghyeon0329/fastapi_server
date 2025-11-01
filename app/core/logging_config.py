from logging import LoggerAdapter
import logging.handlers
from app.utils import *
import logging, sys

class ContextFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        for k in ("operation_id", "user_id", "affiliation", "action"):
            if not hasattr(record, k):
                setattr(record, k, "-")
        return True

def setup_logging() -> logging.Logger:
    logger = logging.getLogger("fastapi_server")
    logger.setLevel(logging.INFO)

    fmt = "[%(asctime)s] [%(levelname)s] [%(name)s] [op=%(operation_id)s] [user=%(user_id)s] [aff=%(affiliation)s] [act=%(action)s] %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"

    ## terminal 출력
    formatter = logging.Formatter(fmt, datefmt)
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(formatter)
    
    ## file 출력
    os.makedirs("logs", exist_ok=True)
    fh = logging.handlers.RotatingFileHandler(
        "logs/server.log", maxBytes=5_000_000, backupCount=5, encoding="utf-8"
    )
    fh.setFormatter(formatter)

    if not logger.handlers:
        # if os.getenv("ENV") == "dev":
            # logger.addHandler(sh)
        logger.addHandler(fh)
        logger.addFilter(ContextFilter())

    return logger

def get_request_logger(
    operation_id: str,
    user_id: str,
    affiliation: str,
    action: str
) -> LoggerAdapter:
    base = logging.getLogger("fastapi_server")
    extra = {
        "operation_id": operation_id,
        "user_id" : user_id,
        "affiliation" : affiliation,
        "action": action or "-",
    }
    return LoggerAdapter(base, extra)