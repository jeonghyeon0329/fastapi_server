from fastapi import APIRouter, Form, UploadFile, HTTPException, responses
from pydantic import BaseModel
from typing import Optional, Type
import os
router = APIRouter()

async def handle_request(
    request_cls: Type[BaseModel],
    user_id: str,
    affiliation: Optional[str],
    file: Optional[UploadFile] = None,
    parameter: Optional[str] = None,
    return_file: bool = False
):
    from app.operate.operate_service import operate_run
    try:
        param = request_cls(
            user_id=user_id,
            affiliation=affiliation,
            filename=file.filename if file else ""
        )
        result = await operate_run(param, file, parameter)
        if return_file:
            file_path = result.get('result') if result else None
            if file_path:
                return responses.FileResponse(
                    path=file_path,
                    filename=os.path.basename(file_path),
                )
            else:
                raise HTTPException(status_code=204, detail="File result not available.")
        return responses.JSONResponse(status_code=200, content={"detail": result})

    except Exception as e:
        raise HTTPException(status_code=e.status_code, detail=f"{str(e.message)}")

@router.post("/~test")
async def run_ocr(
    user_id: str = Form(...),
    affiliation: Optional[str] = Form(None)
):
    from app.models.test_model import testRequest
    return await handle_request(testRequest, user_id, affiliation)