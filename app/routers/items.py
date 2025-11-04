from fastapi import APIRouter, Form, UploadFile, HTTPException, responses, File
from app.core.logging_config import setup_logging, get_request_logger
from pydantic import BaseModel
from typing import Optional, Type, Dict, Any
from app.utils import make_json_response
import os, uuid, json


logger = setup_logging()
router = APIRouter()


async def handle_request(
    request_cls: Type[BaseModel],
    payload: Dict[str, Any],
    *,
    file: Optional[UploadFile] = None,
    return_file: bool = False
):
    """요청 파라미터 검증 + 로깅 + 서비스 실행 + 응답 처리"""
    operation_id = uuid.uuid4().hex
    req_logger = get_request_logger(
        operation_id,
        payload.get("user_id"),
        payload.get("affiliation"),
        request_cls.__name__,
    )

    # ----------------------------------------------------------------------
    # 1️⃣ Pydantic Payload 검증
    # ----------------------------------------------------------------------
    try:
        param = request_cls(**payload)
    except Exception as e:
        raise HTTPException(
            status_code=422,
            detail=make_json_response(
                422, "A001", "Payload validation failed", e.errors()
            ),
        )

    from app.operate.operate_service import operate_run
    req_logger.info("REQUEST_RECEIVED")

    # ----------------------------------------------------------------------
    # 2️⃣ 비즈니스 로직 실행
    # ----------------------------------------------------------------------
    try:
        result = await operate_run(param, payload, **({"file": file} if file else {}))
    except HTTPException as e:
        req_logger.error(
            f"REQUEST_FAILED status={e.status_code} code={e.detail.get('error_code', '-')}"
        )
        detail = e.detail if isinstance(e.detail, dict) else {"message": str(e.detail)}
        detail["operation_id"] = operation_id
        raise HTTPException(
            status_code=e.status_code,
            detail=detail,
            headers={"X-Operation-Id": operation_id},
        )

    except Exception as e:
        req_logger.exception(f"REQUEST_FAILED status=500")
        raise HTTPException(
            status_code=500,
            detail=make_json_response(500, "A004", "Unexpected internal error", str(e)),
            headers={"X-Operation-Id": operation_id},
        )


    # ----------------------------------------------------------------------
    # 3️⃣ 결과 반환
    # ----------------------------------------------------------------------
    try:
        if return_file:
            file_path = result.get("result") if result else None
            if file_path and os.path.exists(file_path):
                req_logger.info("REQUEST_COMPLETED (return_file=True)")
                return responses.FileResponse(
                    path=file_path,
                    filename=os.path.basename(file_path),
                    headers={"X-Operation-Id": operation_id},
                )

            req_logger.warning("REQUEST_NO_CONTENT (return_file=True)")
            raise HTTPException(
                status_code=204,
                detail=make_json_response(
                    204,
                    "A003",
                    "File result not available",
                    f"operation_id={operation_id}",
                ),
                headers={"X-Operation-Id": operation_id},
            )

        req_logger.info("REQUEST_COMPLETED")
        return responses.JSONResponse(
            status_code=200,
            content={"detail": {**result, "operation_id": operation_id}},
            headers={"X-Operation-Id": operation_id},
        )

    except HTTPException:
        raise  # 이미 처리된 예외는 그대로 전달
    except Exception as e:
        req_logger.exception("REQUEST_FAILED while building response")
        raise HTTPException(
            status_code=500,
            detail=make_json_response(
                500, "A004", "Failed to build response", str(e)
            ),
            headers={"X-Operation-Id": operation_id},
        )


# ----------------------------------------------------------------------
# ✅ 예시 라우터
# ----------------------------------------------------------------------
@router.post("/~test")
async def run_test(
    user_id: str = Form(...),
    affiliation: Optional[str] = Form(None)
):
    payload = {"user_id": user_id, "affiliation": affiliation}
    from app.models.test_model import _testRequest
    return await handle_request(_testRequest, payload)


@router.post("/~file")
async def run_test(
    user_id: str = Form(...),
    affiliation: Optional[str] = Form(None),
    file: UploadFile = File(...)
):
    payload = {"user_id": user_id, "affiliation": affiliation}
    from app.models.test_model import _testRequest
    return await handle_request(_testRequest, payload, file=file)