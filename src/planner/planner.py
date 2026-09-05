from pydantic import BaseModel, Field
from typing import List, Optional


class CreativeBrief(BaseModel):
    title: str
    use_case: str
    script: str
    duration: int = Field(gt=0, le=60)
    aspect_ratio: str
    style: Optional[str] = None
    constraints: List[str] = []


def validate_brief(data: dict) -> CreativeBrief:
    return CreativeBrief(**data)