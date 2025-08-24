
from pydantic import BaseModel, field_validator
from typing import Optional, Dict
import json

class testRequest(BaseModel):
    user_id: str
    affiliation: Optional[str] = None
    filename: str
    model: Optional[Dict[str, str]] = {
        "test": "test",
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