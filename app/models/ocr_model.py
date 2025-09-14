
from pydantic import BaseModel, field_validator
from typing import Optional, Dict
import json

class ocrRequest(BaseModel):
    user_id : str
    affiliation : str
    version : str
    requestId : str
    timestamp : str
    model: Optional[Dict[str, str]] = {
        "ocr_layout": "ocrlyt",
        "ocr_tsr": "ocrtsr",
        "ocr_text": "ocrtext",
        "ocr_xlsx": "ocrxlsx",
        "ocrcleaning": "ocrcln",
    }
    
    @field_validator("model", mode="before")
    @classmethod
    def parse_model(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                raise ValueError("model must be valid JSON string")
        return v