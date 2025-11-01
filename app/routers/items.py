from fastapi import APIRouter, Form, UploadFile, HTTPException, responses, File
from app.core.logging_config import setup_logging, get_request_logger
from pydantic import BaseModel
from typing import Optional, Type, Dict, Any, Annotated
from app.utils import *
import os, uuid, re, json

logger = setup_logging()
router = APIRouter()

async def handle_request(
    request_cls: Type[BaseModel],
    payload: Dict[str, Any], *,
    file: Optional[UploadFile] = None,
    return_file: bool = False
):
    try:
        param = request_cls(**payload)
    except Exception as e:
        raise HTTPException(
            status_code=422, 
            detail={
                "error_code" : "A001",
                "message" : "Payload validation failed",
                "errors" : e.errors()
            })
    from app.operate.operate_service import operate_run
    operation_id = uuid.uuid4().hex 
    req_logger = get_request_logger(operation_id, payload.get("user_id"), payload.get("affiliation"), request_cls.__name__)
    req_logger.info("REQUEST_RECEIVED")

    try:
        result = await operate_run(param, payload, **({'file': file} if file is not None else {}))

    except HTTPException as e: 
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail={
                "error_code" : "A002",
                "message" : "undefined error",
                "errors" : e
            })
    try:
        if return_file:
            file_path = result.get('result') if result else None
            if file_path:
                return responses.FileResponse(
                    path=file_path,
                    filename=os.path.basename(file_path),
                    headers={"X-Operation-Id": operation_id},
                )
            else:
                req_logger.info("REQUEST_NO_CONTENT return_file=true")
                raise HTTPException(
                    status_code=204, 
                    detail={"message": "File result not available.", "operation_id": operation_id},
                    headers={"X-Operation-Id": operation_id},
                )
            
        req_logger.info("REQUEST_COMPLETED")
        return responses.JSONResponse(
            status_code=200,
            content={"detail": {**result, "operation_id": operation_id}},
            headers={"X-Operation-Id": operation_id},
        )
    
    except HTTPException as e:
        req_logger.exception(f"REQUEST_FAILED status={e.status_code}")
        detail = e.detail if isinstance(e.detail, dict) else {"message": str(e.detail)}
        detail["operation_id"] = operation_id
        raise HTTPException(
            status_code=e.status_code,
            detail=detail,
            headers={"X-Operation-Id": operation_id},
        )

    except Exception as e:
        req_logger.exception(f"REQUEST_FAILED status={e.status_code}")
        raise HTTPException(
            status_code=500,
            detail={"message": str(e), "operation_id": operation_id},
            headers={"X-Operation-Id": operation_id},
        )

@router.post("/~test")
async def run_test(
    user_id: str = Form(...),
    affiliation: Optional[str] = Form(None)
):
    payload = {
        'user_id' : user_id, 
        'affiliation': affiliation
    }
    from app.models.test_model import _testRequest
    return await handle_request(_testRequest, payload)

