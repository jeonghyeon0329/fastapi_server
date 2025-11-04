from fastapi import Request, Response
from typing import Callable
from app.utils import *

# 허용된 IP 및 URL prefix 설정
ALLOWED_IPS = {"127.0.0.1", "localhost", "testclient"}
ALLOWED_PREFIXES = {"/items"}


async def ip_access(request: Request, call_next: Callable[[Request], Response]) -> Response:
    """IP 및 경로 접근 제어 미들웨어"""

    client_ip = request.client.host
    path = request.url.path

    if client_ip not in ALLOWED_IPS:
        return make_json_response(
            403, "C001", f"Access denied for IP: {client_ip}"
        )

    first_segment = "/" + path.lstrip("/").split("/", 1)[0]
    if first_segment not in ALLOWED_PREFIXES:
        return make_json_response(
            404, "C002", f"Invalid API path: {path}"
        )

    return await call_next(request)


