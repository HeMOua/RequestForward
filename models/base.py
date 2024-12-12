from pydantic import BaseModel, Field
from typing import List, Optional


class Backend(BaseModel):
    url: str
    alias: Optional[str] = None


class Group(BaseModel):
    path: str
    alias: Optional[str] = None
    current_backend: Optional[str] = None
    backends: List[Backend] = None


class Proxy(BaseModel):
    port: int = Field(..., ge=1, le=65535)
    groups: List[Group] = None