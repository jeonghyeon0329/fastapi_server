from fastapi import Request, responses

ALLOWED_IPS = {'127.0.0.1','localhost'}
ALLOWED_PREFIXES = ["/items"]

""" 접근 허용 ip, api endpoint 검사"""
async def ip_access(request: Request, call_next):
    try:
        client_ip = request.client.host
        path = request.url.path
        if client_ip not in ALLOWED_IPS:
            return responses.JSONResponse(
                status_code=403, content={"detail": f"Access denied for IP {client_ip}"}
            )
  
        first_segment = "/" + path.lstrip("/").split("/")[0]
        
        if first_segment not in ALLOWED_PREFIXES:    
            return responses.JSONResponse(
                status_code=404,
                content={"detail": f"Invalid API path_: {path}"}
            )
        return await call_next(request)
    
    except:
        return responses.JSONResponse(
            status_code=400, 
            content={"detail": f"Bad Request"}
            )